import re
from difflib import SequenceMatcher


def normalize_text(text: str) -> str:
    normalized = re.sub(r"\s+", " ", text.strip().lower())
    return re.sub(r"[^\w\s]", "", normalized)


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, normalize_text(a), normalize_text(b)).ratio()
