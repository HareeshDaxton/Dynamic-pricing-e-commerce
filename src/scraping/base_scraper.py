import random
import time
from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from loguru import logger
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class BaseScraper(ABC):
    """
    Abstract base class for all scrapers.
    Implements common functionality like driver setup, waiting, etc.
    """

    # Stores initial settings., So scraper knows whether to Hide browser?, Use proxy?
    def __init__(self, headless: bool = True, use_proxy: bool = False):
        self.headless = headless
        self.use_proxy = use_proxy
        self.driver = None

    # Creates and configures Chrome browser. Without browser → cannot scrape website. Also adds anti-detection settings.
    def setup_driver(self) -> webdriver.Chrome:
        """Setup and return a configured Chrome driver"""

        options = Options()

        if self.headless:
            options.add_argument("--headless")

        # Essential options to avoid detection
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")

        # Random user agent
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
        ]
        options.add_argument(f"user-agent={random.choice(user_agents)}")

        # Proxy setup (if enabled)
        if self.use_proxy:
            proxy = self._get_proxy()
            if proxy:
                options.add_argument(f"--proxy-server={proxy}")

        driver = webdriver.Chrome(options=options)

        # Execute stealth scripts to avoid detection
        driver.execute_cdp_cmd(
            "Network.setUserAgentOverride",
            {
                "userAgent": driver.execute_script(
                    "return navigator.userAgent"
                ).replace("Headless", "")
            },
        )

        return driver

    # Gets proxy information. Avoid IP blocking
    def _get_proxy(self) -> Optional[str]:
        """Get a working proxy from pool"""
        # Implement proxy rotation logic
        # Can use services like ScraperAPI, Bright Data, etc.
        return None

    # Waits until an element appears. Pages load slowly Without waiting → element not found
    def wait_for_element(self, by: By, value: str, timeout: int = 10):
        """Wait for element to be present"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            logger.warning(f"Timeout waiting for element: {value}")
            return None

    # Adds random waiting time. Coz bots → too fast and Humans → slower (Makes scraper look natural)
    def human_delay(self, min_seconds: float = 1.0, max_seconds: float = 3.0):
        """Add random delay to mimic human behavior"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)

    # Safely gets text. If element missing → avoid crash
    def safe_get_text(self, element, default: str = "") -> str:
        """Safely extract text from element"""
        try:
            return element.text.strip() if element else default
        except Exception as e:
            logger.error(f"Error extracting text: {e}")
            return default

    # Scrapes product data. Main purpose of scraper (like -> Name, price, url, platform)
    @abstractmethod
    def scrape_product(self, url: str) -> Dict:
        """
        Scrape a single product. Must be implemented by subclass.

        Returns:
            Dict with keys: name, price, url, platform, timestamp
        """
        pass

    # Starts browser automatically. Less manual work
    def __enter__(self):
        """Context manager entry"""
        self.driver = self.setup_driver()
        return self

    # Closes browser automatically. Prevent browser staying open
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup"""
        if self.driver:
            self.driver.quit()


"""
Workflow:

Create scraper
      ↓
setup_driver()
      ↓
wait_for_element()
      ↓
safe_get_text()
      ↓
scrape_product()
      ↓
__exit__()

"""
