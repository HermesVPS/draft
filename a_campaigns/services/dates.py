"""Date-review detection, ported from ``campaign.mjs`` ``findNumberedDates``."""

import re

_DATE_PATTERNS = [
    re.compile(
        r"\b\d{1,2}\s+(?:January|February|March|April|May|June|July|August|"
        r"September|October|November|December)\s+\d{4}\b",
        re.IGNORECASE,
    ),
    re.compile(r"\b\d{1,2}/\d{1,2}/\d{4}\b"),
    re.compile(r"\b\d{4}-\d{2}-\d{2}\b"),
]


def find_numbered_dates(text):
    """Return the unique exact numbered calendar dates found in text.

    Flags only exact dates ("22 October 2026", "22/10/2026", "2026-10-22");
    ignores general wording ("October allocation", "Mid-November", etc.).
    """
    value = str(text)
    findings = []
    for pattern in _DATE_PATTERNS:
        findings.extend(m.group(0) for m in pattern.finditer(value))
    return list(dict.fromkeys(findings))
