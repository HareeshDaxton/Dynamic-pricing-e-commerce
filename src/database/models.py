from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Index, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
 
Base = declarative_base()
 
class Product(Base):
    __tablename__ = "products"
    
    product_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    product_name = Column(String(255), nullable=False)
    sku = Column(String(100), unique=True, nullable=False)
    category = Column(String(100))
    cost_price = Column(Float, nullable=False)
    current_price = Column(Float, nullable=False)
    platform = Column(String(50), nullable=False)  # 'amazon', 'flipkart'
    product_url = Column(Text, nullable=False)
    inventory_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_user_active', 'user_id', 'is_active'),
    )
 
class CompetitorProduct(Base):
    __tablename__ = "competitor_products"
    
    competitor_id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.product_id'), nullable=False)
    competitor_name = Column(String(255))
    competitor_url = Column(Text, nullable=False)
    platform = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
 
class PriceHistory(Base):
    __tablename__ = "price_history"
    
    history_id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.product_id'))
    competitor_id = Column(Integer, ForeignKey('competitor_products.competitor_id'))
    price = Column(Float, nullable=False)
    is_own_product = Column(Boolean, default=False)
    scraped_at = Column(DateTime, server_default=func.now())
    
    __table_args__ = (
        Index('idx_product_time', 'product_id', 'scraped_at'),
        Index('idx_competitor_time', 'competitor_id', 'scraped_at'),
    )
 
class SalesData(Base):
    __tablename__ = "sales_data"
    
    sale_id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.product_id'), nullable=False)
    quantity_sold = Column(Integer, nullable=False)
    price_at_sale = Column(Float, nullable=False)
    revenue = Column(Float, nullable=False)
    sale_date = Column(DateTime, nullable=False)
    hour_of_day = Column(Integer)  # 0-23
    day_of_week = Column(Integer)  # 1-7
    
    __table_args__ = (
        Index('idx_product_date', 'product_id', 'sale_date'),
    )
 
class PricePrediction(Base):
    __tablename__ = "price_predictions"
    
    prediction_id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.product_id'), nullable=False)
    recommended_price = Column(Float, nullable=False)
    confidence_score = Column(Float)
    predicted_revenue = Column(Float)
    predicted_demand = Column(Integer)
    model_version = Column(String(50))
    features_used = Column(JSON)
    created_at = Column(DateTime, server_default=func.now())
    
    __table_args__ = (
        Index('idx_product_recent', 'product_id', 'created_at'),
    )