from datetime import datetime, timezone

from app.database import SessionLocal

from app.models.asset import Asset
from app.models.scan_asset import ScanAsset
from app.models.scan_detection import ScanDetection

from app.services.classifier import detect_sensitive_data
from app.services.finding_service import save_findings
from app.services.policy_engine import evaluate_policy

from app.services.aws_discovery_service import (
    get_customer_s3_client,
    discover_s3_buckets,
    discover_s3_objects,
    read_s3_object_bytes,
    normalize_s3_objects,
)

from app.services.aws_content_reader import (
    is_supported_object_type,
    read_s3_object_content,
)


MAX_SCAN_OBJECT_SIZE_BYTES = 20 * 1024 * 1024


def run_aws_scan(
    account_id: str,
    role_name: str,
    external_id: str,
    region: str,
    datasource_id: int,
    scan_id: int
):

    s3 = get_customer_s3_client(
        account_id=account_id,
        role_name=role_name,
        external_id=external_id,
        region=region,
    )

    buckets = discover_s3_buckets(
        account_id=account_id,
        role_name=role_name,
        external_id=external_id,
        region=region,
    )

    db = SessionLocal()

    classifications = []

    try:

        for bucket in buckets:

            bucket_name = bucket["Name"]

            objects = discover_s3_objects(
                s3_client=s3,
                bucket_name=bucket_name
            )

            normalized_objects = normalize_s3_objects(
                objects=objects,
                bucket_name=bucket_name
            )

            for object_data in normalized_objects:

                asset_path = object_data["path"]

                existing_asset = (
                    db.query(Asset)
                    .filter(
                        Asset.datasource_id == datasource_id,
                        Asset.path == asset_path
                    )
                    .first()
                )

                if existing_asset:

                    existing_asset.name = object_data["name"]
                    existing_asset.type = object_data["type"]
                    existing_asset.size = object_data["size"]
                    existing_asset.last_scanned_at = datetime.now(
                        timezone.utc
                    )

                    asset = existing_asset

                else:

                    asset = Asset(
                        name=object_data["name"],
                        type=object_data["type"],
                        path=asset_path,
                        size=object_data["size"],
                        datasource_id=datasource_id,
                        last_scanned_at=datetime.now(
                            timezone.utc
                        )
                    )

                    db.add(asset)
                    db.flush()

                scan_asset = ScanAsset(
                    scan_id=scan_id,
                    asset_id=asset.id
                )

                db.add(scan_asset)

                object_key = asset_path.split(
                    f"s3://{bucket_name}/",
                    1
                )[1]

                if object_data["size"] > MAX_SCAN_OBJECT_SIZE_BYTES:

                    classifications.append(
                        {
                            "asset_id": asset.id,
                            "asset_name": asset.name,
                            "classified": False,
                            "findings": []
                        }
                    )

                    continue

                if not is_supported_object_type(object_key):

                    classifications.append(
                        {
                            "asset_id": asset.id,
                            "asset_name": asset.name,
                            "classified": False,
                            "findings": []
                        }
                    )

                    continue

                try:

                    content_bytes = read_s3_object_bytes(
                        s3_client=s3,
                        bucket_name=bucket_name,
                        object_key=object_key
                    )

                    content = read_s3_object_content(
                        content=content_bytes,
                        object_key=object_key
                    )

                except Exception:

                    classifications.append(
                        {
                            "asset_id": asset.id,
                            "asset_name": asset.name,
                            "classified": False,
                            "findings": []
                        }
                    )

                    continue

                if content is None:

                    classifications.append(
                        {
                            "asset_id": asset.id,
                            "asset_name": asset.name,
                            "classified": False,
                            "findings": []
                        }
                    )

                    continue

                findings = detect_sensitive_data(
                    content
                )

                # Record every detected data type for this scan.
                # This includes detections whose policies are disabled.
                for finding_data in findings:

                    data_type = finding_data["type"]
                    count = finding_data["count"]

                    policy_result = evaluate_policy(
                        db,
                        data_type
                    )

                    scan_detection = ScanDetection(
                        scan_id=scan_id,
                        asset_id=asset.id,
                        data_type=data_type,
                        count=count,
                        policy_status=policy_result["status"]
                    )

                    db.add(scan_detection)

                db.commit()

                # save_findings() applies the Policy Engine again.
                # Disabled or unsupported policies therefore do not
                # create active Findings.
                saved_findings = save_findings(
                    db=db,
                    asset_id=asset.id,
                    findings=findings
                )

                classifications.append(
                    {
                        "asset_id": asset.id,
                        "asset_name": asset.name,
                        "classified": True,
                        "findings": [
                            {
                                "id": finding.id,
                                "type": finding.data_type,
                                "count": finding.count,
                                "severity": finding.severity
                            }
                            for finding in saved_findings
                        ]
                    }
                )

        db.commit()

        return classifications

    finally:
        db.close()