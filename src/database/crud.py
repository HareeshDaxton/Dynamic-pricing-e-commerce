from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from .models import (
    Product, CompetitorProduct, PriceHistory, 
    SalesData, PricePrediction
)
from loguru import logger
 
class ProductCRUD:
    """CRUD operations for products"""
    
    @staticmethod
    def create_product(db: Session, product_data: Dict) -> Product:
        """Create a new product"""
        product = Product(**product_data)
        db.add(product)
        db.commit()
        db.refresh(product)
        logger.info(f"Created product: {product.product_name} (ID: {product.product_id})")
        return product
    
    @staticmethod
    def get_product(db: Session, product_id: int) -> Optional[Product]:
        """Get product by ID"""
        return db.query(Product).filter(Product.product_id == product_id).first()
    
    @staticmethod
    def get_user_products(db: Session, user_id: int, active_only: bool = True) -> List[Product]:
        """Get all products for a user"""
        query = db.query(Product).filter(Product.user_id == user_id)
        if active_only:
            query = query.filter(Product.is_active == True)
        return query.all()
    
    @staticmethod
    def update_product_price(db: Session, product_id: int, new_price: float) -> Product:
        """Update product's current price"""
        product = db.query(Product).filter(Product.product_id == product_id).first()
        if product:
            product.current_price = new_price
            product.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(product)
        return product
 
 
class PriceHistoryCRUD:
    """CRUD operations for price history"""
    
    @staticmethod
    def add_price_record(db: Session, price_data: Dict) -> PriceHistory:
        """Add a price history record"""
        price_record = PriceHistory(**price_data)
        db.add(price_record)
        db.commit()
        db.refresh(price_record)
        return price_record
    
    @staticmethod
    def add_bulk_prices(db: Session, price_records: List[Dict]) -> int:
        """Bulk insert price records (more efficient)"""
        try:
            db.bulk_insert_mappings(PriceHistory, price_records)
            db.commit()
            logger.info(f"Inserted {len(price_records)} price records")
            return len(price_records)
        except Exception as e:
            db.rollback()
            logger.error(f"Error in bulk insert: {e}")
            return 0
    
    @staticmethod
    def get_price_history(
        db: Session,
        product_id: int,
        days: int = 30,
        include_competitors: bool = True
    ) -> List[PriceHistory]:
        """Get price history for product"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        query = db.query(PriceHistory).filter(
            PriceHistory.product_id == product_id,
            PriceHistory.scraped_at >= start_date
        )
        
        if not include_competitors:
            query = query.filter(PriceHistory.is_own_product == True)
        
        return query.order_by(PriceHistory.scraped_at).all()
    
    @staticmethod
    def get_competitor_prices(
        db: Session,
        product_id: int,
        latest_only: bool = True
    ) -> List[Dict]:
        """Get current competitor prices for a product"""
        
        if latest_only:
            # Get most recent price for each competitor
            from sqlalchemy import func
            
            subquery = db.query(
                PriceHistory.competitor_id,
                func.max(PriceHistory.scraped_at).label('max_time')
            ).filter(
                PriceHistory.product_id == product_id,
                PriceHistory.is_own_product == False
            ).group_by(PriceHistory.competitor_id).subquery()
            
            results = db.query(
                CompetitorProduct.competitor_name,
                PriceHistory.price,
                PriceHistory.scraped_at
            ).join(
                PriceHistory,
                PriceHistory.competitor_id == CompetitorProduct.competitor_id
            ).join(
                subquery,
                and_(
                    PriceHistory.competitor_id == subquery.c.competitor_id,
                    PriceHistory.scraped_at == subquery.c.max_time
                )
            ).all()
            
            return [
                {
                    "competitor": r.competitor_name,
                    "price": r.price,
                    "as_of": r.scraped_at
                }
                for r in results
            ]
        
        return []
 
 
class PredictionCRUD:
    """CRUD operations for price predictions"""
    
    @staticmethod
    def save_prediction(db: Session, prediction_data: Dict) -> PricePrediction:
        """Save a price prediction"""
        prediction = PricePrediction(**prediction_data)
        db.add(prediction)
        db.commit()
        db.refresh(prediction)
        logger.info(f"Saved prediction for product {prediction.product_id}")
        return prediction
    
    @staticmethod
    def get_latest_prediction(db: Session, product_id: int) -> Optional[PricePrediction]:
        """Get most recent prediction for product"""
        return db.query(PricePrediction).filter(
            PricePrediction.product_id == product_id
        ).order_by(desc(PricePrediction.created_at)).first()
    
    @staticmethod
    def get_prediction_accuracy(db: Session, days: int = 7) -> Dict:
        """Calculate prediction accuracy metrics"""
        # This would compare predictions vs actual outcomes
        # Implement based on your evaluation strategy
        pass