from app.models.policy import Policy


def evaluate_policy(
    db,
    data_type: str
):
    policy = (
        db.query(Policy)
        .filter(
            Policy.data_type == data_type
        )
        .first()
    )

    if policy is None:
        return {
            "status": "unsupported",
            "policy": None
        }

    if not policy.is_active:
        return {
            "status": "disabled",
            "policy": policy
        }

    return {
        "status": "active",
        "policy": policy
    }