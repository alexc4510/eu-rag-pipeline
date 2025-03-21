# extract_result_text.py

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import time
import json
import os
from urllib.parse import urljoin
from webdriver_manager.chrome import ChromeDriverManager
from config import RAW_DIR, METADATA_JSON


def extract_result_text():
    """
    Reads eurlex_results.json, visits each link, extracts the HTML content
    from <div id='document1'>, saves to RAW_DIR/<celex_id>.txt
    """

    # Load CELEX entries from metadata
    with open(METADATA_JSON, "r", encoding="utf-8") as f:
        entries = json.load(f)

    # Setup headless browser
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )

    os.makedirs(RAW_DIR, exist_ok=True)

    for entry in entries:
        celex_id = entry["celex"]
        output_path = RAW_DIR / f"{celex_id}.txt"

        if output_path.exists():
            print(f"⏭️ Skipping {celex_id} (already saved)")
            continue

        url = entry["link"].replace("AUTO", "EN/TXT").replace("&rid=1", "")
        print(f"🔍 Processing CELEX {celex_id} → {url}")

        driver.get(url)
        time.sleep(3)  # Let JavaScript render

        soup = BeautifulSoup(driver.page_source, "html.parser")
        document_div = soup.find("div", id="document1")
        document_content = []

        if document_div:
            for child in document_div.descendants:
                if child.name == "table":
                    table_rows = []
                    for row in child.find_all("tr"):
                        row_cells = [
                            cell.get_text(separator=" ", strip=True)
                            for cell in row.find_all("td")
                        ]
                        if row_cells:
                            table_rows.append(" ; ".join(row_cells))
                    if table_rows:
                        document_content.append("\n".join(table_rows))
                elif child.name == "p":
                    paragraph = child.get_text(separator=" ", strip=True)
                    if paragraph:
                        document_content.append(paragraph)
        else:
            document_content.append("No content found in the div with id 'document1'.")

        full_text = "\n\n".join(document_content)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(full_text)

        print(f"✅ Saved document for {celex_id}")

    driver.quit()


if __name__ == "__main__":
    extract_result_text()
