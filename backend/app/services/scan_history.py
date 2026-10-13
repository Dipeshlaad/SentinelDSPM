from app.models.scan import Scan


def get_previous_successful_scan(
    db,
    current_scan: Scan
):
    """
    Return the most recent successful scan for the
    same datasource that happened before the current scan.

    The current scan itself is excluded.

    Failed, cancelled, pending, and running scans are ignored.
    """

    return (
        db.query(Scan)
        .filter(
            Scan.datasource_id == current_scan.datasource_id,
            Scan.status == "completed",
            Scan.id != current_scan.id
        )
        .order_by(
            Scan.completed_at.desc()
        )
        .first()
    )