from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from exceptions import SecurityChallengeError, SearchResultsNotFoundError
import random, time, os
from config import BASE_URL, MAX_PAGES, SEARCH_TIMEOUT, SECURITY_CHECK_TIMEOUT, PAGINATION_TIMEOUT, OUTPUT_DIR

import logging
logger = logging.getLogger(__name__)


class CompanyHouseScraper:

    BASE_URL = BASE_URL

    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument("--disable-blink-features=AutomationControlled")

        self.driver = webdriver.Chrome(options=options)
        self.driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"}
        )

        self.wait = WebDriverWait(
            self.driver,
            SEARCH_TIMEOUT
        )

    def open(self, url):
        logger.info(f"Opening: {url}")
        self.driver.get(url)
        print(f"[+] Page loaded: {self.driver.current_url}")


    def is_security_challenge(self):
        """
        Detect an active Cloudflare challenge via DOM selectors rather
        than free-text matching on page_source. Free-text matching
        (e.g. checking for the word "cloudflare") produced false
        positives, since normal pages often reference Cloudflare in
        footers/CDN scripts even when no challenge is active.
        """
        title = self.driver.title.lower()

        challange_titles = [
            "just a moment",
            "attention required",
        ]

        if any(t in title for t in challange_titles):
            return True
        
        challange_selectors = [
            "#cf-challenge-running",
            "iframe[src*='challenges.cloudflare.com']",
            "#challenge-form",
        ]

        for selector in challange_selectors:
            if self.driver.find_elements(By.CSS_SELECTOR, selector):
                return True
        return False

    def wait_for_security_check(self, timeout=SECURITY_CHECK_TIMEOUT):
        """
        If Cloudflare presents a challenge, wait for the user to
        complete it manually in the open browser window.

        This scraper does not attempt to bypass CAPTCHA verification.
        """

        if not self.is_security_challenge():
            return True
        print()
        print("=" * 60)
        print("[!] SECURITY VERIFICATION DETECTED")
        print("=" * 60)
        print("[!] Please complete the Cloudflare verification")
        print("[!] in the open Chrome browser window.")
        print("[!] The scraper will resume once the page is normal.")
        print(f"[!] Timeout: {timeout} seconds")
        print("=" * 60)
        print()

        try:
            WebDriverWait(
                self.driver,
                timeout
            ).until(
                lambda driver: (
                    not self.is_security_challenge()
                    and len(
                        driver.find_elements(
                            By.ID,
                            "homepage-company-search"
                        )
                    ) > 0
                )
            )

            print("[+] Security verification completed.")
            print("[+] Homepage is ready to use.")
            return True

        except TimeoutException:
            logger.warning("Security verification timeout.")

            self.save_debug_page(os.path.join(OUTPUT_DIR, "debug_cloudflare_timeout.html"))
            return False


    def search_company(self, search_term, max_pages=MAX_PAGES):
        print()
        print(f"[*] Searching company: {search_term}")
        self.open(self.BASE_URL)

        if not self.wait_for_security_check():
            raise SecurityChallengeError(
                "Security verification was not completed."
            )
        print("[*] Waiting for search input...")

        search_box = self.wait.until(
            EC.visibility_of_element_located(
                (By.ID, "homepage-company-search")
            )
        )

        search_box.click()
        search_box.clear()
        search_box.send_keys(search_term)
        print(f"[+] Search term entered: {search_term}")

        search_button = self.wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, ".revamp-search__submit")
            )
        )

        search_button.click()
        print("[*] Waiting for search results...")
        self.wait_for_search_results()
        

        urls = []
        page_count = 0

        while True:
            page_count += 1
            results = self.driver.find_elements(
                By.CSS_SELECTOR,
                "#search-results a.revamp-search__result-link"
            )

            print(
                f"[+] Found {len(results)} companies on current page."
                f"(page {page_count}/{max_pages})"
            )

            for result in results:
                url = result.get_attribute("href")

                if url and url not in urls:
                    urls.append(url)
            if page_count >= max_pages:
                print(f"[*] Reached max_pages limit ({max_pages}), stopping.")
                break

            # Look for the "Next" button
            next_buttons = self.driver.find_elements(
                By.CSS_SELECTOR,
                "button[dusk='nextPage.after']"
            )

            if not next_buttons:
                print("[*] No more pages.")
                break

            next_button = next_buttons[0]

            # If disabled, this is the last page
            if not next_button.is_enabled():
                print("[*] Reached last page.")
                break

            # Store the current page's result URLs for comparison.
            # Comparing the full list (not just the first URL) avoids
            # false positives from partial DOM updates during pagination.
            old_urls = [r.get_attribute("href") for r in results] if results else []
            print("[*] Moving to next page...")

            self.driver.execute_script(
                """
                arguments[0].scrollIntoView({
                    block: 'center'
                });
                """,
                next_button
            )

            self.driver.execute_script(
                "arguments[0].click();",
                next_button
            )
            time.sleep(random.uniform(1.5, 3.0))

            # Wait until the page content actually changes
            try:
                WebDriverWait(
                    self.driver,
                    PAGINATION_TIMEOUT
                ).until(
                    lambda driver: self.page_changed(
                        old_urls
                    )
                )

            except TimeoutException:
                print(
                    "[!] Pagination timeout."
                )
                self.save_debug_page(os.path.join(OUTPUT_DIR, f"debug_pagination_page{page_count}.html"))
                break

        print(
            f"[+] Total company URLs collected: {len(urls)}"
        )

        return urls


    def wait_for_search_results(self):
        try:
            self.wait.until(
                lambda driver: len(
                    driver.find_elements(
                        By.CSS_SELECTOR,
                        "#search-results "
                        "a.revamp-search__result-link"
                    )
                ) > 0
            )

        except TimeoutException:

            print("[!] Search results not found.")
            print(
                f"[DEBUG] Current URL: "
                f"{self.driver.current_url}"
            )

            print(
                f"[DEBUG] Page title: "
                f"{self.driver.title}"
            )

            self.save_debug_page(os.path.join(OUTPUT_DIR, "debug_search.html"))
            raise SearchResultsNotFoundError(
                "Search results were not found."
            )


    def page_changed(self, old_urls):
        """
        Detect whether pagination has moved to a new page by comparing
        the full set of result URLs, not just the first one.

        Comparing only the first URL caused false positives on this
        site (partial DOM updates could change the first result while
        leaving others stale), leading to missed or duplicated entries
        during pagination.
        """
        results = self.driver.find_elements(
            By.CSS_SELECTOR,
            "#search-results a.revamp-search__result-link"
        )

        if not results:
            return False
        current_urls = [r.get_attribute("href") for r in results]
        return current_urls != old_urls


    def get_page_source(self):
        return self.driver.page_source


    def save_debug_page(self, filename):
        try:
            with open(
                filename,
                "w",
                encoding="utf-8"
            ) as file:
                file.write(
                    self.driver.page_source
                )

            print(
                f"[DEBUG] Saved page to {filename}"
            )

        except Exception as error:
            print(
                f"[DEBUG] Failed to save debug page: {error}"
            )

    def close(self):
        print("[*] Closing browser...")
        self.driver.quit()