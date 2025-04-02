from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from urllib.parse import urljoin
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
from pathlib import Path
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import PDF_DIR, METADATA_JSON_RO


def extract_pdf():
    # Load metadata
    with open(METADATA_JSON_RO, "r", encoding="utf-8") as f:
        entries = json.load(f)

    # Selenium options
    options = Options()
    options.add_argument("--headless")
    options.add_experimental_option(
        "prefs",
        {
            "download.default_directory": str(PDF_DIR),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True,
        },
    )

    # Initialize WebDriver
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )

    for entry in entries:
        celex_id = entry["celex"]
        pdf_filename = f"CELEX_{celex_id}_RO_TXT.pdf"
        pdf_path = Path(PDF_DIR) / pdf_filename

        # ✅ Skip if already downloaded
        if pdf_path.exists():
            print(f"⏩ Skipping {pdf_filename} (already exists)")
            continue

        page_url = entry["link"].replace("AUTO", "RO/TXT").replace("&rid=1", "")
        print(f"🔍 Processing {celex_id}: {page_url}")

        driver.get(page_url)
        time.sleep(3)

        try:
            pdf_link_element = driver.find_element(
                By.CSS_SELECTOR, "a#format_language_table_PDF_RO"
            )
            pdf_url = urljoin(page_url, pdf_link_element.get_attribute("href"))
            driver.get(pdf_url)
            print(f"⬇ Downloading PDF: {pdf_url}")
            time.sleep(3)  # Wait for download
        except Exception as e:
            print(f"❌ Could not find PDF link for {celex_id}: {e}")

    driver.quit()
    print("✅ All PDFs processed successfully.")


if __name__ == "__main__":
    extract_pdf()
