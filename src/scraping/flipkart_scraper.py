from typing import Dict, Optional
from selenium.webdriver.common.by import By
from .base_scraper import BaseScraper
from loguru import logger
import re
from datetime import datetime
 
class FlipkartScraper(BaseScraper):
    """
    Scraper for Flipkart.com
    """
    
    DOMAIN = "https://www.flipkart.com"
    
    PRICE_SELECTORS = [
        "div._30jeq3._16Jk6d",
        "div._30jeq3",
        "div._16Jk6d",
    ]
    
    TITLE_SELECTORS = [
        "span.B_NuCI",
        "h1.yhB1nd",
    ]
    
    def scrape_product(self, url: str) -> Dict:
        """Scrape product from Flipkart"""
        result = {
            "name": None,
            "price": None,
            "url": url,
            "platform": "flipkart",
            "timestamp": datetime.utcnow(),
            "status": "failed",
            "error": None
        }
        
        try:
            logger.info(f"Scraping Flipkart: {url}")
            self.driver.get(url)
            self.human_delay(2, 4)
            
            # Close login popup if it appears
            self._close_login_popup()
            
            # Extract title
            title = self._extract_title()
            if title:
                result["name"] = title
            else:
                logger.warning(f"Could not extract title from {url}")
                result["error"] = "Title not found"
                return result
            
            # Extract price
            price = self._extract_price()
            if price:
                result["price"] = price
                result["status"] = "success"
            else:
                logger.warning(f"Could not extract price from {url}")
                result["error"] = "Price not found"
                return result
            
            logger.info(f"Successfully scraped: {title} - ₹{price}")
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            result["error"] = str(e)
        
        return result
    
    def _close_login_popup(self):
        """Close Flipkart's annoying login popup"""
        try:
            close_button = self.driver.find_element(
                By.CSS_SELECTOR, "button._2KpZ6l._2doB4z"
            )
            close_button.click()
            self.human_delay(0.5, 1)
        except:
            pass  # Popup might not appear
    
    def _extract_title(self) -> Optional[str]:
        """Extract product title"""
        for selector in self.TITLE_SELECTORS:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                title = self.safe_get_text(element)
                if title:
                    return title
            except:
                continue
        return None
    
    def _extract_price(self) -> Optional[float]:
        """Extract product price"""
        for selector in self.PRICE_SELECTORS:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                price_text = self.safe_get_text(element)
                
                if price_text:
                    price = self._clean_price(price_text)
                    if price:
                        return price
            except:
                continue
        return None
    
    @staticmethod
    def _clean_price(price_text: str) -> Optional[float]:
        """Clean Flipkart price text"""
        try:
            cleaned = re.sub(r'[₹,\s]', '', price_text)
            return float(cleaned)
        except (ValueError, AttributeError):
            return None
        

"""
workflow:

URL
 ↓
Open Flipkart page
 ↓
Wait like human
 ↓
Close login popup
 ↓
Extract title
 ↓
Extract price
 ↓
Clean price
 ↓
Return result

"""