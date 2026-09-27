import os
from dotenv import load_dotenv

load_dotenv()

# for scraper
BASE_URL = "https://companyhouse.id/"
MAX_PAGES = int(os.getenv("MAX_PAGES", 20))
SEARCH_TIMEOUT = int(os.getenv("SEARCH_TIMEOUT", 30))
SECURITY_CHECK_TIMEOUT = int(os.getenv("SECURITY_CHECK_TIMEOUT", 180))
PAGINATION_TIMEOUT = int(os.getenv("PAGINATION_TIMEOUT", 45))

# for database
DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
SEARCH_TERMS_FILE = os.path.join(DATA_DIR, "search_terms.txt")