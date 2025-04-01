import fitz  # PyMuPDF
import re
from pathlib import Path
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import PDF_DIR, RAW_DIR


def clean_pdfs():
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    def clean_text(raw_text: str) -> str:
        raw_text = re.sub(r"MONITORUL OFICIAL.*?\n", "", raw_text)
        raw_text = re.sub(r"^\s*P A R T E A.*?\n", "", raw_text, flags=re.MULTILINE)
        raw_text = re.sub(r"^.*?ISSN.*?$", "", raw_text, flags=re.MULTILINE)
        raw_text = raw_text.replace("\x04", "…")
        raw_text = raw_text.replace("�", "")
        raw_text = re.sub(r"\n{2,}", "\n\n", raw_text)
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
        return "\n".join(lines)

    def process_pdf(pdf_path: Path, output_dir: Path):
        out_path = output_dir / f"{pdf_path.stem}.txt"
        if out_path.exists():
            print(f"⏩ Skipping {pdf_path.name} (already exists)")
            return
        doc = fitz.open(pdf_path)
        raw_text = "\n".join(page.get_text() for page in doc[1:])  # skip first page
        doc.close()
        cleaned = clean_text(raw_text)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(cleaned)
        print(f"✅ Cleaned: {pdf_path.name}")

    for pdf_file in PDF_DIR.glob("*.pdf"):
        process_pdf(pdf_file, RAW_DIR)

    print("✅ All PDFs processed successfully.")


if __name__ == "__main__":
    clean_pdfs()
