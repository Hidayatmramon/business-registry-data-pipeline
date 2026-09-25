import json

from scraper import CompanyHouseScraper
from parser import parse_company_page
from database import create_table, insert_company

def main():
    create_table()

    scraper = CompanyHouseScraper()

    companies = []

    try:
        urls = scraper.search_company("Indodax")
        for url in urls:
            try:
                scraper.open(url)
                html = scraper.get_page_source()
                company = parse_company_page(
                    html,
                    url
                )
                companies.append(company)

                insert_company(company)

                print(
                    f"[+] Successfully scraped and stored data for {company['company_name']}"
                )

            except Exception as e:
                print(f"[!] Error processing {url}: {e}")

        with open(
            "output/companies.json",
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                companies,
                file,
                indent=4,
                ensure_ascii=False
            )

    finally:
        scraper.close()


if __name__ == "__main__":
    main()