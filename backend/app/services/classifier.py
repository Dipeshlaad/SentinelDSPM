import re


EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
)

PHONE_PATTERN = re.compile(
    r"(?<!\d)(?:\+91[-\s]?)?[6-9]\d{9}(?!\d)"
)

AADHAAR_PATTERN = re.compile(
    r"(?<!\d)\d{4}[-\s]\d{4}[-\s]\d{4}(?!\d)"
)

PAN_PATTERN = re.compile(
    r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"
)

CREDIT_CARD_PATTERN = re.compile(
    r"(?<!\d)(?:\d{4}[-\s]?){3}\d{4}(?!\d)"
)

AWS_ACCESS_KEY_PATTERN = re.compile(
    r"\bAKIA[0-9A-Z]{16}\b"
)


PATTERNS = {
    "email": EMAIL_PATTERN,
    "phone": PHONE_PATTERN,
    "aadhaar": AADHAAR_PATTERN,
    "pan": PAN_PATTERN,
    "credit_card": CREDIT_CARD_PATTERN,
    "aws_access_key": AWS_ACCESS_KEY_PATTERN,
}


def _overlaps(start, end, ranges):
    for existing_start, existing_end in ranges:
        if start < existing_end and end > existing_start:
            return True

    return False


def detect_sensitive_data(text: str):
    findings = []
    occupied_ranges = []

    # Detect credit cards first.
    # This prevents the Aadhaar detector from matching
    # a 12-digit portion of a 16-digit card number.
    priority_order = [
        "credit_card",
        "email",
        "phone",
        "aadhaar",
        "pan",
        "aws_access_key",
    ]

    for data_type in priority_order:
        pattern = PATTERNS[data_type]

        matches = []

        for match in pattern.finditer(text):
            start = match.start()
            end = match.end()

            if _overlaps(start, end, occupied_ranges):
                continue

            matches.append(match.group())
            occupied_ranges.append((start, end))

        if matches:
            findings.append(
                {
                    "type": data_type,
                    "count": len(matches),
                    "matches": matches
                }
            )

    return findings


def detect_emails(text: str):
    matches = EMAIL_PATTERN.findall(text)

    return {
        "type": "email",
        "count": len(matches),
        "matches": matches
    }

