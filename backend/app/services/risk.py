from app.models.finding import Finding


SEVERITY_MAP = {
    "email": "medium",
    "phone": "medium",
    "aadhaar": "high",
    "pan": "high",
    "credit_card": "critical",
    "aws_access_key": "critical",
}


SEVERITY_SCORE = {
    "critical": 10,
    "high": 7,
    "medium": 4,
    "low": 1,
}


def get_severity(data_type: str):
    return SEVERITY_MAP.get(
        data_type,
        "low"
    )


def get_severity_score(severity: str):
    return SEVERITY_SCORE.get(
        severity.lower(),
        0
    )


def calculate_finding_score(
    severity: str,
    count: int
):
    return (
        get_severity_score(severity)
        * count
    )


def calculate_asset_risk(
    db,
    asset_id: int
):
    findings = (
        db.query(Finding)
        .filter(
            Finding.asset_id == asset_id
        )
        .all()
    )

    total_score = 0

    for finding in findings:
        total_score += calculate_finding_score(
            finding.severity,
            finding.count
        )

    return total_score


def get_risk_level(score: int):
    if score == 0:
        return "none"

    if score < 30:
        return "low"

    if score < 75:
        return "medium"

    if score <= 100:
        return "high"

    return "critical"

def calculate_asset_risk_level(
    db,
    asset_id: int
):
    score = calculate_asset_risk(
        db,
        asset_id
    )

    return {
        "score": score,
        "level": get_risk_level(score)
    }