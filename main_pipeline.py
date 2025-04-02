# main_pipeline.py

from scripts.parse_all_results import parse_all_results
from scripts.extract_result_text import extract_result_text
from scripts.sanitize import sanitize_texts
from scripts.summarize import summarize_texts
from scripts.build_vector_db import build_vector_db
from scripts.parse_romanian_results import parse_all_results_ro
from scripts.extract_pdf import extract_pdf
from scripts.clean_pdfs import clean_pdfs

from config import RAW_DIR, PROCESSED_DOCUMENTS, DEFAULT_TARGET_YEAR

from pathlib import Path


# Load raw .txt files from disk
def load_raw_texts(raw_dir: Path) -> dict[str, str]:
    data = {}
    for file in raw_dir.rglob("*.txt"):
        relative_path = file.relative_to(raw_dir)
        with open(file, "r", encoding="utf-8") as f:
            data[str(relative_path)] = f.read()
    return data


# Save final summarized output to disk (flat structure)
def save_summaries(summaries: dict[str, str], output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    for relative_path, summary in summaries.items():
        output_path = output_dir / Path(relative_path).name
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(summary)


def main():
    print("🔍 Parsing metadata from EUR-Lex...")
    parse_all_results(target_year=DEFAULT_TARGET_YEAR)
    parse_all_results_ro(target_year=DEFAULT_TARGET_YEAR)

    print("🌐 Downloading full regulation text from links...")
    extract_result_text()
    extract_pdf()
    clean_pdfs()

    print("📂 Loading raw files from disk...")
    raw_data = load_raw_texts(RAW_DIR)

    print("🧼 Sanitizing text...")
    sanitized = sanitize_texts(raw_data)

    print("🧠 Summarizing content...")
    summarized = summarize_texts(sanitized)

    print("💾 Saving summaries to disk...")
    save_summaries(summarized, PROCESSED_DOCUMENTS)

    print("📚 Building vector database...")
    build_vector_db()

    print("✅ All processing complete.")


if __name__ == "__main__":
    main()
