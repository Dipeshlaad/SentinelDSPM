from fastapi import APIRouter, Depends, HTTPException

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.database import SessionLocal

from app.models.scan import Scan
from app.models.datasource import Datasource
from app.models.aws_cloud_account import AWSCloudAccount
from app.models.scan_detection import ScanDetection
from app.models.scan_asset import ScanAsset
from app.models.alert import Alert

from app.schemas.scan import (
    ScanCreate,
    ScanResponse,
    ScanChangeResponse,
    ScanSummaryResponse
)

from app.core.permissions import require_permission

from app.services.scanner import run_aws_scan
from app.services.scan_history import get_previous_successful_scan
from app.services.change_engine import compare_scan_changes
from app.services.alert_service import evaluate_scan_alerts
from app.services.audit_service import create_audit_log


router = APIRouter(
    prefix="/api/v1/scans",
    tags=["Scans"]
)


def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


def build_scan_summary(
    db,
    scan_id: int,
    changes: list,
):

    current_scan_assets = (
        db.query(ScanAsset)
        .filter(
            ScanAsset.scan_id == scan_id
        )
        .all()
    )

    total_assets = len(current_scan_assets)

    current_detections = (
        db.query(ScanDetection)
        .filter(
            ScanDetection.scan_id == scan_id
        )
        .all()
    )

    assets_with_findings = len({
        detection.asset_id
        for detection in current_detections
        if detection.policy_status == "active"
        and detection.count > 0
    })

    total_detections = sum(
        detection.count
        for detection in current_detections
    )

    detection_changes = [
        change
        for change in changes
        if change["change_type"] == "detection"
    ]

    resolved_findings = sum(
        1
        for change in detection_changes
        if change["status"] == "RESOLVED"
    )

    increased_findings = sum(
        1
        for change in detection_changes
        if change["status"] == "INCREASED"
    )

    decreased_findings = sum(
        1
        for change in detection_changes
        if change["status"] == "DECREASED"
    )

    unchanged_findings = sum(
        1
        for change in detection_changes
        if change["status"] == "UNCHANGED"
    )

    alerts_created = (
        db.query(Alert)
        .filter(
            Alert.scan_id == scan_id
        )
        .count()
    )

    return ScanSummaryResponse(
        total_assets=total_assets,
        assets_with_findings=assets_with_findings,
        total_detections=total_detections,
        resolved_findings=resolved_findings,
        increased_findings=increased_findings,
        decreased_findings=decreased_findings,
        unchanged_findings=unchanged_findings,
        alerts_created=alerts_created,
    )


@router.post(
    "/",
    response_model=ScanResponse
)
def create_scan(
    scan_data: ScanCreate,
    current_user=Depends(
        require_permission("scan:create")
    ),
    db: Session = Depends(get_db)
):

    query = (
        db.query(Datasource)
        .filter(
            Datasource.id == scan_data.datasource_id
        )
    )

    if current_user["tenant_id"] is not None:
        query = query.filter(
            Datasource.tenant_id
            == current_user["tenant_id"]
        )

    datasource = query.first()

    if datasource is None:
        raise HTTPException(
            status_code=404,
            detail="Datasource not found"
        )

    aws_cloud_account = None

    if datasource.type == "AWS":

        if datasource.aws_cloud_account_id is None:
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
                == datasource.aws_cloud_account_id,
                AWSCloudAccount.tenant_id
                == datasource.tenant_id
            )
            .first()
        )

        if aws_cloud_account is None:
            raise HTTPException(
                status_code=400,
                detail=(
                    "AWS cloud account not found "
                    "for this datasource"
                )
            )

        if aws_cloud_account.status != "verified":
            raise HTTPException(
                status_code=400,
                detail=(
                    "AWS cloud account must be verified "
                    "before creating a scan"
                )
            )

    else:

        raise HTTPException(
            status_code=400,
            detail="Only AWS datasources are supported for scanning"
        )

    new_scan = Scan(
        name=scan_data.name,
        datasource_id=scan_data.datasource_id,
        status="pending"
    )

    db.add(new_scan)
    db.flush()

    create_audit_log(
        db=db,
        user_id=current_user["user_id"],
        tenant_id=current_user["tenant_id"],
        action="SCAN_CREATED",
        resource_type="scan",
        resource_id=new_scan.id,
        details=f"Scan {new_scan.name} was created",
    )

    db.commit()
    db.refresh(new_scan)

    try:

        new_scan.status = "running"

        new_scan.started_at = datetime.now(
            timezone.utc
        )

        create_audit_log(
            db=db,
            user_id=current_user["user_id"],
            tenant_id=current_user["tenant_id"],
            action="SCAN_STARTED",
            resource_type="scan",
            resource_id=new_scan.id,
            details=f"Scan {new_scan.name} was started",
        )

        db.commit()
        db.refresh(new_scan)

        run_aws_scan(
            account_id=aws_cloud_account.account_id,
            role_name=aws_cloud_account.role_name,
            external_id=aws_cloud_account.external_id,
            region=aws_cloud_account.region,
            datasource_id=datasource.id,
            scan_id=new_scan.id
        )

        previous_scan = get_previous_successful_scan(
            db=db,
            current_scan=new_scan
        )

        previous_scan_id = None

        if previous_scan is not None:
            previous_scan_id = previous_scan.id

        changes = compare_scan_changes(
            db=db,
            previous_scan_id=previous_scan_id,
            current_scan_id=new_scan.id
        )

        created_alerts = evaluate_scan_alerts(
            db=db,
            scan_id=new_scan.id
        )

        for alert in created_alerts:

            create_audit_log(
                db=db,
                user_id=current_user["user_id"],
                tenant_id=current_user["tenant_id"],
                action="ALERT_CREATED",
                resource_type="alert",
                resource_id=alert.id,
                details=f"Alert {alert.title} was created",
            )

        new_scan.status = "completed"

        new_scan.completed_at = datetime.now(
            timezone.utc
        )

        create_audit_log(
            db=db,
            user_id=current_user["user_id"],
            tenant_id=current_user["tenant_id"],
            action="SCAN_COMPLETED",
            resource_type="scan",
            resource_id=new_scan.id,
            details=f"Scan {new_scan.name} was completed",
        )

        db.commit()
        db.refresh(new_scan)

    except Exception:

        new_scan.status = "failed"

        new_scan.completed_at = datetime.now(
            timezone.utc
        )

        create_audit_log(
            db=db,
            user_id=current_user["user_id"],
            tenant_id=current_user["tenant_id"],
            action="SCAN_FAILED",
            resource_type="scan",
            resource_id=new_scan.id,
            details=f"Scan {new_scan.name} failed",
        )

        db.commit()
        db.refresh(new_scan)

        raise HTTPException(
            status_code=500,
            detail="Scan failed"
        )

    response = ScanResponse.model_validate(
        new_scan
    )

    response.changes = [
        ScanChangeResponse(**change)
        for change in changes
    ]

    response.summary = build_scan_summary(
        db=db,
        scan_id=new_scan.id,
        changes=changes
    )

    return response


@router.get(
    "/",
    response_model=list[ScanResponse]
)
def get_scans(
    current_user=Depends(
        require_permission("scan:read")
    ),
    db: Session = Depends(get_db)
):

    query = (
        db.query(Scan)
        .join(
            Datasource,
            Scan.datasource_id == Datasource.id
        )
    )

    if current_user["tenant_id"] is not None:
        query = query.filter(
            Datasource.tenant_id
            == current_user["tenant_id"]
        )

    return query.all()


@router.get(
    "/{scan_id}",
    response_model=ScanResponse
)
def get_scan(
    scan_id: int,
    current_user=Depends(
        require_permission("scan:read")
    ),
    db: Session = Depends(get_db)
):

    query = (
        db.query(Scan)
        .join(
            Datasource,
            Scan.datasource_id == Datasource.id
        )
        .filter(
            Scan.id == scan_id
        )
    )

    if current_user["tenant_id"] is not None:
        query = query.filter(
            Datasource.tenant_id
            == current_user["tenant_id"]
        )

    scan = query.first()

    if scan is None:
        raise HTTPException(
            status_code=404,
            detail="Scan not found"
        )

    return scan


@router.post(
    "/{scan_id}/cancel",
    response_model=ScanResponse
)
def cancel_scan(
    scan_id: int,
    current_user=Depends(
        require_permission("scan:cancel")
    ),
    db: Session = Depends(get_db)
):

    query = (
        db.query(Scan)
        .join(
            Datasource,
            Scan.datasource_id == Datasource.id
        )
        .filter(
            Scan.id == scan_id
        )
    )

    if current_user["tenant_id"] is not None:
        query = query.filter(
            Datasource.tenant_id
            == current_user["tenant_id"]
        )

    scan = query.first()

    if scan is None:
        raise HTTPException(
            status_code=404,
            detail="Scan not found"
        )

    if scan.status not in [
        "pending",
        "running"
    ]:
        raise HTTPException(
            status_code=400,
            detail="Scan cannot be cancelled"
        )

    scan.status = "cancelled"

    create_audit_log(
        db=db,
        user_id=current_user["user_id"],
        tenant_id=current_user["tenant_id"],
        action="SCAN_CANCELLED",
        resource_type="scan",
        resource_id=scan.id,
        details=f"Scan {scan.name} was cancelled",
    )

    db.commit()
    db.refresh(scan)

    return scan


# DELETE SCAN
@router.delete("/{scan_id}")
def delete_scan(
    scan_id: int,
    current_user=Depends(
        require_permission("datasource:delete")
    ),
    db: Session = Depends(get_db)
):

    query = (
        db.query(Scan)
        .join(
            Datasource,
            Scan.datasource_id == Datasource.id
        )
        .filter(Scan.id == scan_id)
    )

    if current_user["tenant_id"] is not None:
        query = query.filter(
            Datasource.tenant_id == current_user["tenant_id"]
        )

    scan = query.first()

    if scan is None:
        raise HTTPException(
            status_code=404,
            detail="Scan not found"
        )

    if scan.status in ["pending", "running"]:
        raise HTTPException(
            status_code=400,
            detail="Cancel the scan before deleting it"
        )

    scan_name = scan.name

    # Alerts raised by this scan go with it;
    # alerts merely resolved by it are kept.
    db.query(Alert).filter(
        Alert.scan_id == scan_id
    ).delete(synchronize_session=False)

    db.query(Alert).filter(
        Alert.resolved_by_scan_id == scan_id
    ).update(
        {Alert.resolved_by_scan_id: None},
        synchronize_session=False
    )

    db.query(ScanDetection).filter(
        ScanDetection.scan_id == scan_id
    ).delete(synchronize_session=False)

    db.query(ScanAsset).filter(
        ScanAsset.scan_id == scan_id
    ).delete(synchronize_session=False)

    db.delete(scan)

    create_audit_log(
        db=db,
        user_id=current_user["user_id"],
        tenant_id=current_user["tenant_id"],
        action="SCAN_DELETED",
        resource_type="scan",
        resource_id=scan_id,
        details=f"Scan {scan_name} was deleted",
    )

    db.commit()

    return {
        "message": "Scan deleted successfully"
    }
