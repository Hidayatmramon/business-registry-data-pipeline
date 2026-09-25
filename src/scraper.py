from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class CompanyHouseScraper:
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  # Run in headless mode (no GUI)
        options.add_argument("--no-sandbox")  # Bypass OS security model
        options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
        self.driver = webdriver.Chrome(options=options)
        self.driver.set_window_size(1280, 800)  # Set window size to avoid issues with elements not being visible
        self.wait = WebDriverWait(self.driver, 15)  # Wait up to 15 seconds for elements to be present

    def open(self, url):
        self.driver.get(url)

    def search_company(self, search_term):
        self.open("https://www.companyhouse.id/")
        search_box = self.wait.until(
            EC.presence_of_element_located(
                (By.ID, "homepage-company-search")
            )
        )

        search_box.clear()
        search_box.send_keys(search_term)
        search_box.send_keys(Keys.RETURN)

        self.wait.until(
            EC.presence_of_element_located(
                (By.ID, "search-results")
            )
        )

        results = self.driver.find_elements(
            By.CSS_SELECTOR,
            "#search-results a.revamp-search__result-link"
        )

        return [
            result.get_attribute("href")
            for result in results
        ]

    def get_page_source(self):
        return self.driver.page_source

    def close(self):
        self.driver.quit()