import re
from pathlib import Path
from config import SUMMARY_DIR


def sanitize_texts(
    categorized_data: dict[str, dict[str, str]],
) -> dict[str, dict[str, str]]:
    sanitized = {}
    for category, files in categorized_data.items():
        sanitized[category] = {}
        for relative_path, content in files.items():
            celex_filename = Path(relative_path).name

            # ✅ Skip if already summarized (sanitized step is unnecessary)
            already_summarized = any(
                (subdir / celex_filename).exists()
                for subdir in SUMMARY_DIR.iterdir()
                if subdir.is_dir()
            )
            if already_summarized:
                print(
                    f"⏭️ Skipping sanitization for {celex_filename} (already summarized)"
                )
                continue

            cleaned = re.sub(r"\s+", " ", content).strip()
            sanitized[category][relative_path] = cleaned
    return sanitized
