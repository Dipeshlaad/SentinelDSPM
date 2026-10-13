from pathlib import Path


SUPPORTED_TEXT_TYPES = {
    ".txt",
    ".csv",
}


def read_file_content(file_path: str):
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"File does not exist: {file_path}"
        )

    if not path.is_file():
        raise ValueError(
            f"Path is not a file: {file_path}"
        )

    if path.suffix.lower() not in SUPPORTED_TEXT_TYPES:
        return None

    encodings = [
        "utf-8",
        "utf-16",
    ]

    for encoding in encodings:
        try:
            return path.read_text(
                encoding=encoding
            )

        except UnicodeDecodeError:
            continue

    return None