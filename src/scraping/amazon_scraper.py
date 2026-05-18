from typing import Dict, Optional
from selenium.webdriver.common.by import By
from .base_scraper import BaseScraper
from loguru import logger
import re
from datetime import datetime
 
class AmazonScraper(BaseScraper):
    """
    Scraper for Amazon.in
    
    Note: Amazon's HTML structure changes frequently. 
    This implementation uses multiple selectors as fallback.
    """
    
    DOMAIN = "https://www.amazon.in"
    
    # Multiple selectors for price (Amazon uses different ones)
    PRICE_SELECTORS = [
        "span.a-price-whole",
        "span.a-price span.a-offscreen",
        "span#priceblock_ourprice",
        "span#priceblock_dealprice",
        "span.a-color-price",
    ]
    
    TITLE_SELECTORS = [
        "span#productTitle",
        "h1.a-size-large",
    ]
    
    def scrape_product(self, url: str) -> Dict:
        """
        Scrape product details from Amazon
        
        Args:
            url: Amazon product URL
            
        Returns:
            Dict containing: name, price, url, platform, timestamp, status
        """
        result = {
            "name": None,
            "price": None,
            "url": url,
            "platform": "amazon",
            "timestamp": datetime.utcnow(),
            "status": "failed",
            "error": None
        }
        
        try:
            # Navigate to product page
            logger.info(f"Scraping Amazon: {url}")
            self.driver.get(url)
            
            # Human-like delay
            self.human_delay(2, 4)
            
            # Extract product name
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
    
    def _extract_title(self) -> Optional[str]:
        """Extract product title using multiple selectors"""
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
        """Extract product price using multiple selectors"""
        for selector in self.PRICE_SELECTORS:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                price_text = self.safe_get_text(element)
                
                if price_text:
                    # Clean price text: "₹1,499.00" -> 1499.00
                    price = self._clean_price(price_text)
                    if price:
                        return price
            except:
                continue
        
        # Fallback: try to find any element with price pattern
        try:
            body_text = self.driver.find_element(By.TAG_NAME, "body").text
            price_match = re.search(r'₹\s*([0-9,]+\.?[0-9]*)', body_text)
            if price_match:
                return self._clean_price(price_match.group(1))
        except:
            pass
        
        return None
    
    @staticmethod
    def _clean_price(price_text: str) -> Optional[float]:
        """
        Clean price text and convert to float
        
        Examples:
            "₹1,499.00" -> 1499.0
            "1,499" -> 1499.0
            "₹ 1499" -> 1499.0
        """
        try:
            # Remove currency symbols, commas, spaces
            cleaned = re.sub(r'[₹,\s]', '', price_text)
            # Convert to float
            return float(cleaned)
        except (ValueError, AttributeError):
            return None
 
 
# Usage example
if __name__ == "__main__":
    url = "https://www.amazon.in/dp/B09X3EXAMPLE"  # Replace with real URL
    
    with AmazonScraper(headless=True) as scraper:
        result = scraper.scrape_product(url)
        print(result)


"""        
workflow:

URL
 ↓
Open Amazon page
 ↓
Wait like a human
 ↓
Find product title
 ↓
Find product price
 ↓
Clean price text
 ↓
Return result dictionary

"""
