import json
import os
from scraper import CompanyHouseScraper
from parser import parse_company_page
from database import create_table, insert_company
from config import OUTPUT_DIR, SEARCH_TERMS_FILE

from logger_config import setup_logging
setup_logging()

import logging
logger = logging.getLogger(__name__)

def load_search_terms(filepath=None):
    if filepath is None:
        filepath = SEARCH_TERMS_FILE

    with open(filepath, "r", encoding="utf-8") as file:
        terms = [
            line.strip()
            for line in file
            if line.strip()
        ]
    return terms

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    create_table()
    scraper = CompanyHouseScraper()
    all_companies = []

    try:
        search_terms = load_search_terms()
        print(f"[*] Loaded {len(search_terms)} search terms: {search_terms}")

        for term in search_terms:
            try:
                urls = scraper.search_company(term)
                for url in urls:
                    try:
                        scraper.open(url)
                        html = scraper.get_page_source()
                        company = parse_company_page(html, url)
                        all_companies.append(company)
                        insert_company(company)
                        print(
                            f"[+] Successfully scraped and stored data "
                            f"for {company['company_name']}"
                        )

                    except Exception as error:
                        print(f"[!] Error processing {url}: {error}")

            except Exception as error:
                print(f"[!] Error searching '{term}': {error}")

        output_path = os.path.join(OUTPUT_DIR, "companies.json")
        seen_urls = set()
        unique_companies = []

        for company in all_companies:
            if company["url"] not in seen_urls:
                seen_urls.add(company['url'])
                unique_companies.append(company)

        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(unique_companies, file, indent=4, ensure_ascii=False)

    finally:
        scraper.close()


if __name__ == "__main__":
    main()