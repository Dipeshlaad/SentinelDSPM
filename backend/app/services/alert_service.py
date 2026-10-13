from datetime import datetime, timezone

from app.models.alert import Alert
from app.models.alert_rule import AlertRule
from app.models.asset import Asset
from app.models.scan_detection import ScanDetection
from app.services.policy_engine import evaluate_policy


def evaluate_scan_alerts(db, scan_id: int):
    """
    Evaluate all active alert rules against the current scan.

    Creates new OPEN alerts when thresholds are met and
    resolves previously unresolved alerts when the condition
    is cleared by the current scan.
    """

    active_rules = (
        db.query(AlertRule)
        .filter(AlertRule.is_active.is_(True))
        .all()
    )

    detections = (
        db.query(ScanDetection)
        .filter(ScanDetection.scan_id == scan_id)
        .all()
    )

    detection_map = {
        (detection.asset_id, detection.data_type): detection
        for detection in detections
    }

    created_alerts = []

    for rule in active_rules:

        existing_assets = (
            db.query(Alert.asset_id)
            .filter(
                Alert.alert_rule_id == rule.id
            )
            .distinct()
            .all()
        )

        current_asset_ids = {
            asset_id
            for (asset_id,) in existing_assets
        }

        current_asset_ids.update(
            asset_id
            for asset_id, data_type in detection_map
            if data_type == rule.data_type
        )

        for asset_id in current_asset_ids:

            detection = detection_map.get(
                (asset_id, rule.data_type)
            )

            current_count = (
                detection.count
                if detection is not None
                else 0
            )

            asset = (
                db.query(Asset)
                .filter(Asset.id == asset_id)
                .first()
            )

            if asset is None:
                continue

            unresolved_alerts = (
                db.query(Alert)
                .filter(
                    Alert.alert_rule_id == rule.id,
                    Alert.asset_id == asset_id,
                    Alert.status.in_(
                        ["OPEN", "ACKNOWLEDGED"]
                    ),
                    Alert.resolved_at.is_(None)
                )
                .all()
            )

            if current_count >= rule.threshold:

                policy_result = evaluate_policy(
                    db,
                    rule.data_type
                )

                if policy_result["status"] != "active":
                    continue

                policy = policy_result["policy"]

                existing_alert = (
                    db.query(Alert)
                    .filter(
                        Alert.alert_rule_id == rule.id,
                        Alert.scan_id == scan_id,
                        Alert.asset_id == asset_id
                    )
                    .first()
                )

                if existing_alert is not None:
                    continue

                alert = Alert(
                    alert_rule_id=rule.id,
                    scan_id=scan_id,
                    asset_id=asset_id,
                    data_type=rule.data_type,
                    threshold=rule.threshold,
                    current_count=current_count,
                    severity=policy.severity,
                    title=f"{rule.name} triggered",
                    description=(
                        f"{asset.name} contains "
                        f"{current_count} "
                        f"{rule.data_type} detections, "
                        f"which meets or exceeds "
                        f"the configured threshold of "
                        f"{rule.threshold}."
                    ),
                    status="OPEN"
                )

                db.add(alert)
                created_alerts.append(alert)

            else:

                for alert in unresolved_alerts:
                    alert.status = "RESOLVED"
                    alert.resolved_at = datetime.now(
                        timezone.utc
                    )
                    alert.resolved_by_scan_id = scan_id

    db.commit()

    for alert in created_alerts:
        db.refresh(alert)

    return created_alerts