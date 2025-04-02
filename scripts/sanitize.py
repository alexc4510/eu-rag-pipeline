import re
import unicodedata
from pathlib import Path
from config import PROCESSED_DOCUMENTS


def sanitize_text(text: str) -> str:
    # Normalize unicode characters
    text = unicodedata.normalize("NFKC", text)

    # Remove control characters (non-printable)
    text = re.sub(r"[\x00-\x1F\x7F]", "", text)

    # Remove isolated punctuation surrounded by spaces (optional)
    text = re.sub(r"\s+[^\w\s]\s+", " ", text)

    # Remove duplicated punctuation (e.g., "!!", "..", "--")
    text = re.sub(r"([!?.\-])\1{1,}", r"\1", text)

    # Collapse multiple whitespaces into one space
    text = re.sub(r"\s+", " ", text)

    # Trim leading/trailing spaces
    return text.strip()


def sanitize_texts(flat_data: dict[str, str]) -> dict[str, str]:
    sanitized = {}
    for relative_path, content in flat_data.items():
        celex_filename = Path(relative_path).name

        already_summarized = (PROCESSED_DOCUMENTS / celex_filename).exists()
        if already_summarized:
            print(f"⏭️ Skipping sanitization for {celex_filename} (already summarized)")
            continue

        cleaned = sanitize_text(content)
        sanitized[relative_path] = cleaned

    return sanitized
