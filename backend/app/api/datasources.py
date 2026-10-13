from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import SessionLocal
from app.models.datasource import Datasource
from app.models.aws_cloud_account import AWSCloudAccount
from app.schemas.datasource import (
    DatasourceCreate,
    DatasourceResponse
)
from app.core.permissions import require_permission
from app.models.tenant import Tenant
from app.services.audit_service import create_audit_log
from sqlalchemy.exc import IntegrityError
from app.models.scan import Scan
from app.models.asset import Asset
from app.models.finding import Finding
from app.models.alert import Alert


router = APIRouter(
    prefix="/api/v1/datasources",
    tags=["Datasources"]
)


def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# GET ALL DATASOURCES
@router.get(
    "/",
    response_model=List[DatasourceResponse]
)
def get_datasources(
    current_user=Depends(
        require_permission("datasource:read")
    ),
    db: Session = Depends(get_db)
):

    query = db.query(Datasource)

    # Tenant users can only see datasources
    # belonging to their own tenant
    if current_user["tenant_id"] is not None:
        query = query.filter(
            Datasource.tenant_id == current_user["tenant_id"]
        )

    datasources = query.all()

    return datasources


# GET DATASOURCE BY ID
@router.get(
    "/{datasource_id}",
    response_model=DatasourceResponse
)
def get_datasource(
    datasource_id: int,
    current_user=Depends(
        require_permission("datasource:read")
    ),
    db: Session = Depends(get_db)
):

    query = (
        db.query(Datasource)
        .filter(Datasource.id == datasource_id)
    )

    # Tenant users can only access datasources
    # belonging to their own tenant
    if current_user["tenant_id"] is not None:
        query = query.filter(
            Datasource.tenant_id == current_user["tenant_id"]
        )

    datasource = query.first()

    if datasource is None:
        raise HTTPException(
            status_code=404,
            detail="Datasource not found"
        )

    return datasource


# CREATE DATASOURCE
@router.post(
    "/",
    response_model=DatasourceResponse
)
def create_datasource(
    datasource_data: DatasourceCreate,
    current_user=Depends(
        require_permission("datasource:create")
    ),
    db: Session = Depends(get_db)
):

    # Tenant users can only create datasources
    # for their own tenant
    if (
        current_user["tenant_id"] is not None
        and datasource_data.tenant_id != current_user["tenant_id"]
    ):
        raise HTTPException(
            status_code=400,
            detail="You can only create datasources for your own tenant"
        )

    # Check whether the tenant exists
    tenant = (
        db.query(Tenant)
        .filter(Tenant.id == datasource_data.tenant_id)
        .first()
    )

    if tenant is None:
        raise HTTPException(
            status_code=400,
            detail="Tenant does not exist"
        )

    if datasource_data.type != "AWS":
        raise HTTPException(
            status_code=400,
            detail="Only AWS datasources are supported"
        )

    aws_cloud_account = None

    if datasource_data.aws_cloud_account_id is None:
        raise HTTPException(
            status_code=400,
            detail=(
                "AWS datasource must have an AWS cloud account"
            )
        )

    aws_cloud_account = (
        db.query(AWSCloudAccount)
        .filter(
            AWSCloudAccount.id
            == datasource_data.aws_cloud_account_id,
            AWSCloudAccount.tenant_id
            == datasource_data.tenant_id
        )
        .first()
    )

    if aws_cloud_account is None:
        raise HTTPException(
            status_code=400,
            detail=(
                "AWS cloud account not found "
                "for this tenant"
            )
        )

    if aws_cloud_account.status != "verified":
        raise HTTPException(
            status_code=400,
            detail=(
                "AWS cloud account must be verified "
                "before creating an AWS datasource"
            )
        )

    new_datasource = Datasource(
        name=datasource_data.name,
        type=datasource_data.type,
        tenant_id=datasource_data.tenant_id,
        aws_cloud_account_id=(
            datasource_data.aws_cloud_account_id
        ),
        status=datasource_data.status
    )

    db.add(new_datasource)
    db.flush()

    create_audit_log(
        db=db,
        user_id=current_user["user_id"],
        tenant_id=current_user["tenant_id"],
        action="DATASOURCE_CREATED",
        resource_type="datasource",
        resource_id=new_datasource.id,
        details=f"Datasource {new_datasource.name} was created",
    )

    db.commit()
    db.refresh(new_datasource)

    return new_datasource


# UPDATE DATASOURCE
@router.put(
    "/{datasource_id}",
    response_model=DatasourceResponse
)
def update_datasource(
    datasource_id: int,
    datasource_data: DatasourceCreate,
    current_user=Depends(
        require_permission("datasource:update")
    ),
    db: Session = Depends(get_db)
):

    query = (
        db.query(Datasource)
        .filter(Datasource.id == datasource_id)
    )

    # Tenant users can only update datasources
    # belonging to their own tenant
    if current_user["tenant_id"] is not None:
        query = query.filter(
            Datasource.tenant_id == current_user["tenant_id"]
        )

    datasource = query.first()

    if datasource is None:
        raise HTTPException(
            status_code=404,
            detail="Datasource not found"
        )

    # Tenant users cannot move a datasource
    # to another tenant
    if (
        current_user["tenant_id"] is not None
        and datasource_data.tenant_id != current_user["tenant_id"]
    ):
        raise HTTPException(
            status_code=400,
            detail="You can only assign datasources to your own tenant"
        )

    if datasource_data.type != "AWS":
        raise HTTPException(
            status_code=400,
            detail="Only AWS datasources are supported"
        )

    if datasource_data.aws_cloud_account_id is None:
        raise HTTPException(
            status_code=400,
            detail=(
                "AWS datasource must have an AWS cloud account"
            )
        )

    aws_cloud_account = (
        db.query(AWSCloudAccount)
        .filter(
            AWSCloudAccount.id
            == datasource_data.aws_cloud_account_id,
            AWSCloudAccount.tenant_id
            == datasource_data.tenant_id
        )
        .first()
    )

    if aws_cloud_account is None:
        raise HTTPException(
            status_code=400,
            detail=(
                "AWS cloud account not found "
                "for this tenant"
            )
        )

    if aws_cloud_account.status != "verified":
        raise HTTPException(
            status_code=400,
            detail=(
                "AWS cloud account must be verified "
                "before assigning it to an AWS datasource"
            )
        )

    datasource.name = datasource_data.name
    datasource.type = datasource_data.type
    datasource.tenant_id = datasource_data.tenant_id
    datasource.aws_cloud_account_id = (
        datasource_data.aws_cloud_account_id
    )
    datasource.status = datasource_data.status

    create_audit_log(
        db=db,
        user_id=current_user["user_id"],
        tenant_id=current_user["tenant_id"],
        action="DATASOURCE_UPDATED",
        resource_type="datasource",
        resource_id=datasource.id,
        details=f"Datasource {datasource.name} was updated",
    )

    db.commit()
    db.refresh(datasource)

    return datasource


# DELETE DATASOURCE
@router.delete(
    "/{datasource_id}"
)
def delete_datasource(
    datasource_id: int,
    current_user=Depends(
        require_permission("datasource:delete")
    ),
    db: Session = Depends(get_db)
):

    query = (
        db.query(Datasource)
        .filter(Datasource.id == datasource_id)
    )

    # Tenant users can only delete datasources
    # belonging to their own tenant
    if current_user["tenant_id"] is not None:
        query = query.filter(
            Datasource.tenant_id == current_user["tenant_id"]
        )

    datasource = query.first()

    if datasource is None:
        raise HTTPException(
            status_code=404,
            detail="Datasource not found"
        )

    # Scans are history: the user must delete them explicitly first.
    scan_count = (
        db.query(Scan)
        .filter(Scan.datasource_id == datasource.id)
        .count()
    )

    if scan_count:
        raise HTTPException(
            status_code=409,
            detail=(
                f"Cannot delete '{datasource.name}': it still has "
                f"{scan_count} scan(s). Delete those scans first, "
                "then try again."
            ),
        )

    # With no scans left, remove the data derived from this datasource.
    asset_ids = [
        r[0]
        for r in db.query(Asset.id)
        .filter(Asset.datasource_id == datasource.id)
        .all()
    ]

    if asset_ids:
        db.query(Alert).filter(
            Alert.asset_id.in_(asset_ids)
        ).delete(synchronize_session=False)

        db.query(Finding).filter(
            Finding.asset_id.in_(asset_ids)
        ).delete(synchronize_session=False)

        db.query(Asset).filter(
            Asset.id.in_(asset_ids)
        ).delete(synchronize_session=False)

    deleted_datasource_name = datasource.name

    db.delete(datasource)

    create_audit_log(
        db=db,
        user_id=current_user["user_id"],
        tenant_id=current_user["tenant_id"],
        action="DATASOURCE_DELETED",
        resource_type="datasource",
        resource_id=datasource_id,
        details=f"Datasource {deleted_datasource_name} was deleted",
    )

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail=(
                "Cannot delete this data source because "
                "other records still depend on it."
            ),
        )

    return {
        "message": "Datasource deleted successfully"
    }
