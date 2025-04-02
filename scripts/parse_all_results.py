from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import time
import json
from urllib.parse import urljoin
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
from config import (
    METADATA_JSON,
    BASE_URL,
    DEFAULT_TARGET_YEAR,
    build_query_url,
    CATEGORY_QUERY_PARAMS,
    MAX_ONE_PAGE,
)


def parse_all_results(target_year=DEFAULT_TARGET_YEAR):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )

    driver.set_page_load_timeout(300)
    results_data = []

    for category, query_param in CATEGORY_QUERY_PARAMS.items():
        print(f"[i] Scraping category: {category}")
        page = 1

        while True:
            print(f"    Processing page {page} for {category}")
            driver.get(build_query_url(target_year, page, category))
            time.sleep(5)
            soup = BeautifulSoup(driver.page_source, "html.parser")

            try:
                if page == 1:
                    results_info = soup.select_one(
                        "div.ResultsToolsWrapper strong:last-child"
                    )
                    total_results = (
                        int(results_info.text.strip()) if results_info else 0
                    )
                    print(f"    Total results: {total_results}.")

                search_results = soup.select(".SearchResult")

                for div in search_results:
                    a_tag = div.find("h2").find("a") if div.find("h2") else None
                    if not a_tag:
                        continue

                    title = a_tag.text.strip()
                    full_link = urljoin(BASE_URL, a_tag.get("href"))

                    celex = None
                    date_str = None

                    try:
                        collapse_panel = div.find("div", class_="CollapsePanel-sm")
                        result_data = collapse_panel.find(
                            "div", class_=lambda x: x and "SearchResultData" in x
                        )
                        row_div = result_data.find("div", class_="row")
                        col_sm_6_list = row_div.find_all("div", class_="col-sm-6")

                        if len(col_sm_6_list) >= 2:
                            dl1 = col_sm_6_list[0].find("dl")
                            dl2 = col_sm_6_list[1].find("dl")

                            if dl1:
                                for dt, dd in zip(
                                    dl1.find_all("dt"), dl1.find_all("dd")
                                ):
                                    if "CELEX number" in dt.text:
                                        celex = dd.text.strip()

                            if dl2 and len(dl2.find_all("dd")) >= 2:
                                raw_text = dl2.find_all("dd")[1].text.strip()
                                date_str = raw_text.split(";")[0].strip()
                    except Exception as e:
                        print(f"[!] Error extracting details: {e}")

                    if celex:
                        results_data.append(
                            {
                                "celex": celex,
                                "title": title,
                                "link": full_link,
                                "date": date_str,
                                "page": page,
                                "category": category,
                            }
                        )

            except Exception as e:
                print(f"❌ Error processing category '{category}': {e}")
                break

            if MAX_ONE_PAGE:
                print(f"    [i] MAX_ONE_PAGE is True. Stopping after page 1.")
                break

            next_button = soup.select_one("li.next:not(.disabled)")
            if not next_button:
                print(f"    [i] No more pages for {category}.")
                break

            page += 1

    driver.quit()

    try:
        with open(METADATA_JSON, "r", encoding="utf-8") as f:
            existing_data = json.load(f)
    except FileNotFoundError:
        existing_data = []

    existing_dict = {item["celex"]: item for item in existing_data}
    added_or_updated = 0

    for new in results_data:
        celex = new["celex"]
        if celex not in existing_dict or any(
            new[k] != existing_dict[celex].get(k)
            for k in ["title", "link", "date", "page", "category"]
        ):
            existing_dict[celex] = new
            added_or_updated += 1

    with open(METADATA_JSON, "w", encoding="utf-8") as f:
        json.dump(list(existing_dict.values()), f, ensure_ascii=False, indent=2)

    print(f"✅ Added or updated {added_or_updated} entries.")

    def parse_date(d):
        try:
            return datetime.strptime(d, "%d/%m/%Y")
        except:
            return datetime.min

    with open(METADATA_JSON, "r", encoding="utf-8") as f:
        final_data = json.load(f)

    final_data.sort(key=lambda x: parse_date(x["date"]), reverse=True)

    with open(METADATA_JSON, "w", encoding="utf-8") as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)

    print(f"✅ JSON sorted by descending date. Total entries: {len(final_data)}")


if __name__ == "__main__":
    parse_all_results()
    print(f"🕰 Finished at {datetime.now()}")
