from datetime import datetime, timezone

from app.models.finding import Finding
from app.services.policy_engine import evaluate_policy


def save_findings(db, asset_id: int, findings: list):
    saved_findings = []

    for finding_data in findings:
        data_type = finding_data["type"]
        count = finding_data["count"]

        policy_result = evaluate_policy(
            db,
            data_type
        )

        # Unsupported data type:
        # do not create a finding.
        if policy_result["status"] == "unsupported":
            continue

        # Policy exists but is disabled:
        # do not create or update an active finding.
        if policy_result["status"] == "disabled":
            continue

        policy = policy_result["policy"]

        existing_finding = (
            db.query(Finding)
            .filter(
                Finding.asset_id == asset_id,
                Finding.data_type == data_type
            )
            .first()
        )

        severity = policy.severity

        if existing_finding:
            existing_finding.count = count
            existing_finding.severity = severity
            existing_finding.last_seen_at = datetime.now(
                timezone.utc
            )

            saved_findings.append(
                existing_finding
            )

        else:
            finding = Finding(
                asset_id=asset_id,
                data_type=data_type,
                count=count,
                severity=severity
            )

            db.add(finding)
            saved_findings.append(finding)

    db.commit()

    for finding in saved_findings:
        db.refresh(finding)

    return saved_findings