from bs4 import BeautifulSoup

FIELD_MAPPING = {
    "Company Name": "company_name",
    "Legal Entity Type": "legal_entity_type",
    "Business Number": "business_number",
    "SK Number": "sk_number",
    "Country": "country",
}

def parse_company_page(html, url):
    soup = BeautifulSoup(html, "html.parser")
    table = soup.select_one("table.cp-table")
    if not table:
        raise ValueError("Company data table was not found")

    company = {
        "url": url,
        "company_name": None,
        "legal_entity_type": None,
        "business_number": None,
        "sk_number": None,
        "country": None,
    }

    rows = table.select("tr")
    for row in rows:
        cells = row.find_all(["th", "td"])
        if len(cells) != 2:
            continue

        field_name = cells[0].get_text(strip=True)
        field_value = cells[1].get_text(" ", strip=True)

        mapped_field = FIELD_MAPPING.get(field_name)
        if mapped_field:
            company[mapped_field] = field_value or None
            
    return company