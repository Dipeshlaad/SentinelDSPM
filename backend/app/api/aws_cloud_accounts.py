import secrets
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.aws_cloud_account import AWSCloudAccount
from app.schemas.aws_cloud_account import (
    AWSCloudAccountCreate,
    AWSCloudAccountResponse
)
from app.core.permissions import require_permission
from app.services.audit_service import create_audit_log
from app.services.aws_cloudformation_service import (
    generate_aws_onboarding_template
)
from app.services.aws_connection_service import (
    verify_aws_account_connection
)
from fastapi.responses import Response


router = APIRouter(
    prefix="/api/v1/cloud-accounts/aws",
    tags=["AWS Cloud Accounts"]
)


def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


@router.post(
    "/",
    response_model=AWSCloudAccountResponse
)
def create_aws_cloud_account(
    account_data: AWSCloudAccountCreate,
    current_user=Depends(
        require_permission("datasource:create")
    ),
    db: Session = Depends(get_db)
):

    if current_user["tenant_id"] is None:
        raise HTTPException(
            status_code=400,
            detail="AWS cloud accounts must belong to a tenant"
        )

    existing_account = (
        db.query(AWSCloudAccount)
        .filter(
            AWSCloudAccount.tenant_id
            == current_user["tenant_id"],
            AWSCloudAccount.account_id
            == account_data.account_id
        )
        .first()
    )

    if existing_account is not None:
        raise HTTPException(
            status_code=400,
            detail=(
                "This AWS account is already registered "
                "for this tenant"
            )
        )

    external_id = secrets.token_urlsafe(32)

    new_account = AWSCloudAccount(
        tenant_id=current_user["tenant_id"],
        name=account_data.name,
        account_id=account_data.account_id,
        account_name=account_data.account_name,
        role_name=account_data.role_name,
        external_id=external_id,
        region=account_data.region,
        status="pending"
    )

    db.add(new_account)
    db.flush()

    create_audit_log(
        db=db,
        user_id=current_user["user_id"],
        tenant_id=current_user["tenant_id"],
        action="AWS_CLOUD_ACCOUNT_CREATED",
        resource_type="aws_cloud_account",
        resource_id=new_account.id,
        details=(
            f"AWS cloud account {new_account.name} "
            f"was created"
        ),
    )

    db.commit()
    db.refresh(new_account)

    return new_account


@router.get(
    "/{account_id}/cloudformation-template"
)
def get_cloudformation_template(
    account_id: int,
    current_user=Depends(
        require_permission("datasource:create")
    ),
    db: Session = Depends(get_db)
):

    aws_account = (
        db.query(AWSCloudAccount)
        .filter(
            AWSCloudAccount.id == account_id,
            AWSCloudAccount.tenant_id == current_user["tenant_id"]
        )
        .first()
    )

    if aws_account is None:
        raise HTTPException(
            status_code=404,
            detail="AWS cloud account not found"
        )

    template = generate_aws_onboarding_template(
        account_id=aws_account.account_id,
        account_name=aws_account.account_name,
        role_name=aws_account.role_name,
        external_id=aws_account.external_id,
        region=aws_account.region,
    )

    return {
        "account_id": aws_account.id,
        "account_name": aws_account.name,
        "template": template
    }


@router.get(
    "/{account_id}/cloudformation-template/download"
)
def download_cloudformation_template(
    account_id: int,
    current_user=Depends(
        require_permission("datasource:create")
    ),
    db: Session = Depends(get_db)
):

    aws_account = (
        db.query(AWSCloudAccount)
        .filter(
            AWSCloudAccount.id == account_id,
            AWSCloudAccount.tenant_id == current_user["tenant_id"]
        )
        .first()
    )

    if aws_account is None:
        raise HTTPException(
            status_code=404,
            detail="AWS cloud account not found"
        )

    template = generate_aws_onboarding_template(
        account_id=aws_account.account_id,
        account_name=aws_account.account_name,
        role_name=aws_account.role_name,
        external_id=aws_account.external_id,
        region=aws_account.region,
    )

    filename = (
        f"sentineldspm-aws-{aws_account.id}.yaml"
    )

    return Response(
        content=template,
        media_type="application/x-yaml",
        headers={
            "Content-Disposition": (
                f'attachment; filename="{filename}"'
            )
        }
    )


@router.post(
    "/{account_id}/verify",
    response_model=AWSCloudAccountResponse
)
def verify_aws_cloud_account(
    account_id: int,
    current_user=Depends(
        require_permission("datasource:create")
    ),
    db: Session = Depends(get_db)
):

    aws_account = (
        db.query(AWSCloudAccount)
        .filter(
            AWSCloudAccount.id == account_id,
            AWSCloudAccount.tenant_id == current_user["tenant_id"]
        )
        .first()
    )

    if aws_account is None:
        raise HTTPException(
            status_code=404,
            detail="AWS cloud account not found"
        )

    try:

        verify_aws_account_connection(
            account_id=aws_account.account_id,
            role_name=aws_account.role_name,
            external_id=aws_account.external_id,
            region=aws_account.region,
        )

    except Exception:

        raise HTTPException(
            status_code=400,
            detail="AWS account verification failed"
        )

    aws_account.status = "verified"

    aws_account.last_verified_at = datetime.now(
        timezone.utc
    )

    create_audit_log(
        db=db,
        user_id=current_user["user_id"],
        tenant_id=current_user["tenant_id"],
        action="AWS_CLOUD_ACCOUNT_VERIFIED",
        resource_type="aws_cloud_account",
        resource_id=aws_account.id,
        details=(
            f"AWS cloud account {aws_account.name} "
            f"was successfully verified"
        ),
    )

    db.commit()
    db.refresh(aws_account)

    return aws_account