from app.models.scan_detection import ScanDetection
from app.models.asset import Asset


def compare_scan_detections(
    db,
    previous_scan_id: int | None,
    current_scan_id: int
):
    """
    Compare detections from the previous successful scan
    with detections from the current scan.

    The first scan has no previous scan, so every current
    detection is treated as an initial state with change 0.
    """

    current_detections = (
        db.query(ScanDetection)
        .filter(
            ScanDetection.scan_id == current_scan_id
        )
        .all()
    )

    # First successful scan.
    if previous_scan_id is None:
        return [
            {
                "asset_id": detection.asset_id,
                "data_type": detection.data_type,
                "previous_count": 0,
                "current_count": detection.count,
                "change": 0,
                "status": "INITIAL"
            }
            for detection in current_detections
        ]

    previous_detections = (
        db.query(ScanDetection)
        .filter(
            ScanDetection.scan_id == previous_scan_id
        )
        .all()
    )

    previous_map = {
        (
            detection.asset_id,
            detection.data_type
        ): detection.count
        for detection in previous_detections
    }

    current_map = {
        (
            detection.asset_id,
            detection.data_type
        ): detection.count
        for detection in current_detections
    }

    changes = []

    all_keys = set(previous_map) | set(current_map)

    for asset_id, data_type in sorted(all_keys):

        previous_count = previous_map.get(
            (asset_id, data_type),
            0
        )

        current_count = current_map.get(
            (asset_id, data_type),
            0
        )

        change = (
            current_count
            - previous_count
        )

        if previous_count == 0 and current_count > 0:
            status = "NEW_FINDING"

        elif previous_count > 0 and current_count == 0:
            status = "RESOLVED"

        elif current_count > previous_count:
            status = "INCREASED"

        elif current_count < previous_count:
            status = "DECREASED"

        else:
            status = "UNCHANGED"

        changes.append(
            {
                "asset_id": asset_id,
                "data_type": data_type,
                "previous_count": previous_count,
                "current_count": current_count,
                "change": change,
                "status": status
            }
        )

    return changes


def compare_scan_assets(
    db,
    previous_scan_id: int | None,
    current_scan_id: int
):
    """
    Compare assets discovered in the previous successful scan
    with assets discovered in the current scan.
    """

    from app.models.scan_asset import ScanAsset

    current_scan_assets = (
        db.query(ScanAsset)
        .filter(
            ScanAsset.scan_id == current_scan_id
        )
        .all()
    )

    current_asset_ids = {
        scan_asset.asset_id
        for scan_asset in current_scan_assets
    }

    previous_asset_ids = set()

    if previous_scan_id is not None:

        previous_scan_assets = (
            db.query(ScanAsset)
            .filter(
                ScanAsset.scan_id == previous_scan_id
            )
            .all()
        )

        previous_asset_ids = {
            scan_asset.asset_id
            for scan_asset in previous_scan_assets
        }

    all_asset_ids = (
        previous_asset_ids
        | current_asset_ids
    )

    changes = []

    for asset_id in sorted(all_asset_ids):

        asset = (
            db.query(Asset)
            .filter(
                Asset.id == asset_id
            )
            .first()
        )

        if asset is None:
            continue

        if previous_scan_id is None:
            status = "NEW_ASSET"

        elif (
            asset_id not in previous_asset_ids
            and asset_id in current_asset_ids
        ):
            status = "NEW_ASSET"

        elif (
            asset_id in previous_asset_ids
            and asset_id not in current_asset_ids
        ):
            status = "REMOVED_ASSET"

        else:
            status = "UNCHANGED"

        changes.append(
            {
                "asset_id": asset.id,
                "asset_name": asset.name,
                "asset_path": asset.path,
                "status": status
            }
        )

    return changes


def compare_scan_changes(
    db,
    previous_scan_id: int | None,
    current_scan_id: int
):
    """
    Return all asset-level and sensitive-data changes
    between the previous successful scan and the current scan.

    Asset changes and detection changes are combined into
    one unified change list.

    If an asset was completely removed, its detection-level
    RESOLVED events are suppressed because the REMOVED_ASSET
    event already represents the change.
    """

    asset_changes = compare_scan_assets(
        db=db,
        previous_scan_id=previous_scan_id,
        current_scan_id=current_scan_id
    )

    detection_changes = compare_scan_detections(
        db=db,
        previous_scan_id=previous_scan_id,
        current_scan_id=current_scan_id
    )

    # Assets that disappeared completely between scans.
    removed_asset_ids = {
        change["asset_id"]
        for change in asset_changes
        if change["status"] == "REMOVED_ASSET"
    }

    changes = []

    # ---------------------------------------------------------
    # Asset-level changes
    # ---------------------------------------------------------

    for change in asset_changes:

        changes.append(
            {
                "change_type": "asset",
                "asset_id": change["asset_id"],
                "asset_name": change["asset_name"],
                "asset_path": change["asset_path"],
                "data_type": None,
                "previous_count": None,
                "current_count": None,
                "change": None,
                "status": change["status"]
            }
        )

    # ---------------------------------------------------------
    # Sensitive-data changes
    # ---------------------------------------------------------

    for change in detection_changes:

        # If the entire asset was removed, do not also report
        # its individual detections as RESOLVED.
        if change["asset_id"] in removed_asset_ids:
            continue

        asset = (
            db.query(Asset)
            .filter(
                Asset.id == change["asset_id"]
            )
            .first()
        )

        if asset is None:
            continue

        changes.append(
            {
                "change_type": "detection",
                "asset_id": asset.id,
                "asset_name": asset.name,
                "asset_path": asset.path,
                "data_type": change["data_type"],
                "previous_count": change["previous_count"],
                "current_count": change["current_count"],
                "change": change["change"],
                "status": change["status"]
            }
        )

    return changes