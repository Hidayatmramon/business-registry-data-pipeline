# tests/test_parser.py
import sys
import os

sys.path.insert(
    0,
    os.path.join(os.path.dirname(__file__), "..", "src")
)

import pytest

from parser import parse_company_page, validate_company
from exceptions import CompanyDataNotFoundError


def make_html(rows_html):
    return f"""
    <html>
        <body>
            <table class="cp-table">
                {rows_html}
            </table>
        </body>
    </html>
    """


def test_parse_company_page_full_data():
    html = make_html("""
        <tr><th>Company Name</th><td>PT. Contoh Sejahtera</td></tr>
        <tr><th>Legal Entity Type</th><td>Limited Liability Company (PT)</td></tr>
        <tr><th>Business Number</th><td>12345</td></tr>
        <tr><th>SK Number</th><td>AHU-0001234.AH.01.02.TAHUN 2020</td></tr>
        <tr><th>Country</th><td>Indonesia</td></tr>
    """)

    result = parse_company_page(html, "https://companyhouse.id/contoh-sejahtera")

    assert result["url"] == "https://companyhouse.id/contoh-sejahtera"
    assert result["company_name"] == "PT. Contoh Sejahtera"
    assert result["legal_entity_type"] == "Limited Liability Company (PT)"
    assert result["business_number"] == "12345"
    assert result["sk_number"] == "AHU-0001234.AH.01.02.TAHUN 2020"
    assert result["country"] == "Indonesia"


def test_parse_company_page_missing_optional_fields():
    html = make_html("""
        <tr><th>Company Name</th><td>PT. Data Minimal</td></tr>
        <tr><th>Country</th><td>Indonesia</td></tr>
    """)

    result = parse_company_page(html, "https://companyhouse.id/data-minimal")

    assert result["company_name"] == "PT. Data Minimal"
    assert result["business_number"] is None
    assert result["sk_number"] is None


def test_parse_company_page_empty_cell_value():
    html = make_html("""
        <tr><th>Company Name</th><td>PT. Data Kosong</td></tr>
        <tr><th>Business Number</th><td></td></tr>
    """)

    result = parse_company_page(html, "https://companyhouse.id/data-kosong")

    assert result["business_number"] is None


def test_parse_company_page_table_not_found_raises_error():
    html = "<html><body><p>No table here</p></body></html>"

    with pytest.raises(CompanyDataNotFoundError):
        parse_company_page(html, "https://companyhouse.id/tidak-ada-tabel")


def test_parse_company_page_missing_company_name_raises_error():
    html = make_html("""
        <tr><th>Country</th><td>Indonesia</td></tr>
    """)

    with pytest.raises(CompanyDataNotFoundError):
        parse_company_page(html, "https://companyhouse.id/tanpa-nama")


def test_parse_company_page_ignores_rows_with_wrong_column_count():
    html = make_html("""
        <tr><th>Company Name</th><td>PT. Baris Aneh</td></tr>
        <tr><td>Cuma satu kolom</td></tr>
        <tr><th>Extra</th><td>Kolom</td><td>Ketiga</td></tr>
    """)

    result = parse_company_page(html, "https://companyhouse.id/baris-aneh")

    assert result["company_name"] == "PT. Baris Aneh"


def test_validate_company_raises_when_url_missing():
    company = {
        "url": None,
        "company_name": "PT. Tanpa URL",
    }

    with pytest.raises(CompanyDataNotFoundError):
        validate_company(company)