from typing import List, Dict
from datetime import datetime
from loguru import logger
from src.scraping.scraper_manager import ScraperManager
from src.database.crud import PriceHistoryCRUD, ProductCRUD
from src.database.connection import get_db
from src.database.models import Product, CompetitorProduct

 
class DataPipeline:
    """
    End-to-end data pipeline:
    Scraping -> Validation -> Database -> Cache
    """
    
    def __init__(self):
        self.scraper_manager = ScraperManager(max_workers=3)
    
    def run_scraping_job(self, user_id: int = None):
        """
        Main scraping job:
        1. Get all active products (and their competitors) from DB
        2. Scrape current prices
        3. Validate data
        4. Save to database
        5. Update cache
        """
        logger.info("Starting scraping job")
        
        with get_db() as db:
            # Get products to scrape
            if user_id:
                products = ProductCRUD.get_user_products(db, user_id, active_only=True)
            else:
                # Scrape all active products
                products = db.query(Product).filter(Product.is_active == True).all()
            
            if not products:
                logger.warning("No products to scrape")
                return
            
            logger.info(f"Found {len(products)} products to scrape")
            
            # Prepare scraping tasks
            scraping_tasks = []
            
            for product in products:
                # Add own product URL
                scraping_tasks.append((
                    product.product_url,
                    product.platform,
                    product.product_id,
                    None,  # Not a competitor
                    True   # Is own product
                ))
                
                # Add competitor URLs
                competitors = db.query(CompetitorProduct).filter(
                    CompetitorProduct.product_id == product.product_id,
                    CompetitorProduct.is_active == True
                ).all()
                
                for comp in competitors:
                    scraping_tasks.append((
                        comp.competitor_url,
                        comp.platform,
                        product.product_id,
                        comp.competitor_id,
                        False  # Not own product
                    ))
            
            logger.info(f"Total URLs to scrape: {len(scraping_tasks)}")
            
            # Scrape all URLs
            urls_and_platforms = [(url, platform) for url, platform, _, _, _ in scraping_tasks]
            scraped_results = self.scraper_manager.scrape_multiple(urls_and_platforms)
            
            # Process and save results
            price_records = []
            
            for (url, platform, product_id, competitor_id, is_own), result in zip(scraping_tasks, scraped_results):
                if result.get("status") == "success":
                    price_records.append({
                        "product_id": product_id,
                        "competitor_id": competitor_id,
                        "price": result["price"],
                        "is_own_product": is_own,
                        "scraped_at": result["timestamp"]
                    })
            
            # Bulk insert price records
            if price_records:
                inserted_count = PriceHistoryCRUD.add_bulk_prices(db, price_records)
                logger.info(f"Saved {inserted_count} price records")
            
            logger.info("Scraping job complete")
    
    def validate_scraped_data(self, data: Dict) -> bool:
        """Validate scraped data before saving"""
        required_fields = ["price", "url", "platform"]
        
        # Check required fields
        for field in required_fields:
            if field not in data or data[field] is None:
                logger.warning(f"Missing required field: {field}")
                return False
        
        # Validate price is reasonable
        price = data.get("price", 0)
        if price <= 0 or price > 1000000:  # Sanity check
            logger.warning(f"Suspicious price value: {price}")
            return False
        
        return True



"""
main automation pipeline of your project. It connects everything together.
    
Database
   ↓
Get product URLs
   ↓
ScraperManager
   ↓
Amazon/Flipkart scraping
   ↓
Validate data
   ↓
Save price history
   ↓
Database
    
"""