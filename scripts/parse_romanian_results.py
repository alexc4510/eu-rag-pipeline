from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import json
from urllib.parse import urljoin
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import BASE_URL_RO, METADATA_JSON_RO, DEFAULT_TARGET_YEAR

# Limit to one page per category
MAX_PAGE_PER_CATEGORY = 1

# Ensure download directory exists
os.makedirs(os.path.dirname(METADATA_JSON_RO), exist_ok=True)


def build_query_url(target_year: int, page: int) -> str:
    return f"{BASE_URL_RO}&DD_YEAR={target_year}&page={page}"


def parse_all_results_ro(target_year=DEFAULT_TARGET_YEAR):
    """
    Scrapes EUR-Lex for a given year, saving results to METADATA_JSON_RO,
    merging new entries with existing ones, and sorting by descending date.
    This version only scrapes one page per category.
    """

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )

    driver.set_page_load_timeout(253)
    results_data = []

    # Only load the first page
    page = 1
    print(f"\n[+] Processing page {page}...")
    driver.get(build_query_url(target_year, page))
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, "html.parser")

    try:
        # Extract total results info for logging (optional)
        results_info = soup.select_one("div.ResultsToolsWrapper strong:last-child")
        total_results = int(results_info.text.strip()) if results_info else 0
        print(f"[i] Total results: {total_results}. Scraping only page 1.")

        wrapper = soup.body.find("div", class_="Wrapper clearfix")
        next_div = wrapper.find("div", recursive=False)
        all_left_pads = next_div.find_all("div", class_="left-right-padding")
        left_padding = all_left_pads[1]
        main_content = left_padding.find("div", id="MainContent")
        offcanvas = main_content.find(
            "div", class_=lambda x: x and "row" in x and "row-offcanvas" in x
        )
        col_md_9 = offcanvas.find("div", class_="col-md-9")
        eurlex_content = col_md_9.find(
            "div", class_="EurlexContent RelocateFilteringWidget"
        )

        inner_divs = eurlex_content.find_all("div", recursive=False)
        search_results = [
            div for div in inner_divs if "SearchResult" in div.get("class", [])
        ]

        for i, div in enumerate(search_results):
            h2 = div.find("h2")
            if not h2:
                continue
            a_tag = h2.find("a")
            if not a_tag:
                continue

            title = a_tag.text.strip()
            raw_href = a_tag.get("href")
            full_link = urljoin(BASE_URL_RO, raw_href)

            date_str = None
            celex = None
            try:
                collapse_panel = div.find("div", class_="CollapsePanel-sm")
                result_data = collapse_panel.find(
                    "div",
                    class_=lambda x: x and "SearchResultData" in x and "collapse" in x,
                )
                row_div = result_data.find("div", class_="row")
                col_sm_6_list = row_div.find_all("div", class_="col-sm-6")

                if len(col_sm_6_list) >= 2:
                    dl1 = col_sm_6_list[0].find("dl")
                    dl2 = col_sm_6_list[1].find("dl")

                    if dl1:
                        dt_tags = dl1.find_all("dt")
                        dd_tags = dl1.find_all("dd")
                        for dt, dd in zip(dt_tags, dd_tags):
                            if "CELEX number" in dt.text:
                                celex = dd.text.strip()

                    if dl2:
                        dd_tags = dl2.find_all("dd")
                        if len(dd_tags) >= 2:
                            raw_text = dd_tags[1].text.strip()
                            date_str = raw_text.split(";")[0].strip()
            except Exception as e:
                print(
                    f"[!] Failed to extract CELEX or date for page {page}, item {i + 1}: {e}"
                )
                continue

            if celex is None:
                continue

            entry = {
                "celex": celex,
                "title": title,
                "link": full_link,
                "date": date_str,
                "page": page,
            }
            results_data.append(entry)

    except Exception as e:
        print("❌ General error:", e)

    driver.quit()

    # Merge with existing JSON
    existing_data = []
    try:
        with open(METADATA_JSON_RO, "r", encoding="utf-8") as f:
            existing_data = json.load(f)
    except FileNotFoundError:
        existing_data = []

    existing_celex_ids = {item["celex"] for item in existing_data}
    results_data = [
        entry for entry in results_data if entry["celex"] not in existing_celex_ids
    ]

    existing_dict = {item["celex"]: item for item in existing_data}
    added_or_updated = 0

    for new in results_data:
        celex = new["celex"]
        existing_dict[celex] = new
        added_or_updated += 1

    with open(METADATA_JSON_RO, "w", encoding="utf-8") as f:
        json.dump(list(existing_dict.values()), f, ensure_ascii=False, indent=2)

    print(f"\n✅ Added or updated {added_or_updated} entries. Now sorting...")

    def parse_date(d):
        try:
            return datetime.strptime(d, "%d/%m/%Y")
        except:
            return datetime.min

    with open(METADATA_JSON_RO, "r", encoding="utf-8") as f:
        final_data = json.load(f)

    final_data.sort(key=lambda x: parse_date(x["date"]), reverse=True)

    with open(METADATA_JSON_RO, "w", encoding="utf-8") as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)

    print(f"✅ JSON file sorted by descending date. Total entries: {len(final_data)}")


if __name__ == "__main__":
    parse_all_results_ro()
    print(f"\n🕰 Finished at {datetime.now()}")
