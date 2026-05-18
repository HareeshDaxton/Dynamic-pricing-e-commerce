from typing import List, Dict
from .amazon_scraper import AmazonScraper
from .flipkart_scraper import FlipkartScraper
from loguru import logger
import concurrent.futures
from datetime import datetime
 
class ScraperManager:
    """
    Manages multiple scrapers and orchestrates scraping tasks
    """
    
    def __init__(self, max_workers: int = 3):
        self.max_workers = max_workers
        self.scrapers = {
            'amazon': AmazonScraper,
            'flipkart': FlipkartScraper,
        }
    
    def scrape_url(self, url: str, platform: str) -> Dict:
        """
        Scrape a single URL
        
        Args:
            url: Product URL
            platform: 'amazon' or 'flipkart'
        
        Returns:
            Dict with scraped data
        """
        ScraperClass = self.scrapers.get(platform.lower())
        
        if not ScraperClass:
            logger.error(f"Unknown platform: {platform}")
            return {"status": "failed", "error": f"Unknown platform: {platform}"}
        
        try:
            with ScraperClass(headless=True) as scraper:
                return scraper.scrape_product(url)
        except Exception as e:
            logger.error(f"Error in scraper manager for {url}: {e}")
            return {"status": "failed", "error": str(e)}
    
    def scrape_multiple(self, urls_and_platforms: List[tuple]) -> List[Dict]:
        """
        Scrape multiple URLs concurrently
        
        Args:
            urls_and_platforms: List of (url, platform) tuples
            
        Returns:
            List of scraped results
        """
        results = []
        
        logger.info(f"Starting batch scrape of {len(urls_and_platforms)} products")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_url = {
                executor.submit(self.scrape_url, url, platform): (url, platform)
                for url, platform in urls_and_platforms
            }
            
            # Collect results
            for future in concurrent.futures.as_completed(future_to_url):
                url, platform = future_to_url[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"Exception for {url}: {e}")
                    results.append({
                        "url": url,
                        "platform": platform,
                        "status": "failed",
                        "error": str(e)
                    })
        
        successful = sum(1 for r in results if r.get("status") == "success")
        logger.info(f"Batch scraping complete: {successful}/{len(results)} successful")
        
        return results
 
 
# Usage example
if __name__ == "__main__":
    manager = ScraperManager(max_workers=3)
    
    urls = [
        ("https://www.amazon.in/dp/B09X3EXAMPLE1", "amazon"),
        ("https://www.flipkart.com/product/example2", "flipkart"),
        ("https://www.amazon.in/dp/B09X3EXAMPLE3", "amazon"),
    ]
    
    results = manager.scrape_multiple(urls)
    for result in results:
        print(result)
        
    
    
""" 
SCRAPER MANAGER (ORCHESTRATION) 


User gives URLs
        ↓
ScraperManager
        ↓
Identify platform
        ↓
Select AmazonScraper / FlipkartScraper
        ↓
Run scraping
        ↓
Collect results
        ↓
Return final list


"""                                                                                                                    