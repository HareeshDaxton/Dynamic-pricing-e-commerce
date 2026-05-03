Products table (your client's products)
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    sku VARCHAR(100) UNIQUE NOT NULL,
    category VARCHAR(100),
    cost_price DECIMAL(10, 2) NOT NULL,
    current_price DECIMAL(10, 2) NOT NULL,
    platform VARCHAR(50) NOT NULL, -- 'amazon', 'flipkart', 'shopify'
    product_url TEXT NOT NULL,
    inventory_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
 
-- Competitor products table
CREATE TABLE competitor_products (
    competitor_id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(product_id),
    competitor_name VARCHAR(255),
    competitor_url TEXT NOT NULL,
    platform VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
 
-- Price history (time-series data)
CREATE TABLE price_history (
    history_id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(product_id),
    competitor_id INTEGER REFERENCES competitor_products(competitor_id),
    price DECIMAL(10, 2) NOT NULL,
    is_own_product BOOLEAN DEFAULT FALSE, -- true if your product, false if competitor
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_product_time (product_id, scraped_at),
    INDEX idx_competitor_time (competitor_id, scraped_at)
);
 
-- Sales data (if available from client)
CREATE TABLE sales_data (
    sale_id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(product_id),
    quantity_sold INTEGER NOT NULL,
    price_at_sale DECIMAL(10, 2) NOT NULL,
    revenue DECIMAL(10, 2) NOT NULL,
    sale_date DATE NOT NULL,
    hour_of_day INTEGER, -- 0-23
    day_of_week INTEGER, -- 1-7
    
    INDEX idx_product_date (product_id, sale_date)
);
 
-- ML Predictions table
CREATE TABLE price_predictions (
    prediction_id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(product_id),
    recommended_price DECIMAL(10, 2) NOT NULL,
    confidence_score DECIMAL(5, 4), -- 0-1
    predicted_revenue DECIMAL(10, 2),
    predicted_demand INTEGER,
    model_version VARCHAR(50),
    features_used JSONB, -- store feature values
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_product_recent (product_id, created_at DESC)
);
 
-- User alerts
CREATE TABLE alerts (
    alert_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    product_id INTEGER REFERENCES products(product_id),
    alert_type VARCHAR(50), -- 'price_drop', 'competitor_undercut', 'low_inventory'
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    severity VARCHAR(20), -- 'low', 'medium', 'high'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
 
-- Model performance tracking
CREATE TABLE model_metrics (
    metric_id SERIAL PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    metric_type VARCHAR(50), -- 'mae', 'rmse', 'r2', 'accuracy'
    metric_value DECIMAL(10, 6),
    dataset_type VARCHAR(20), -- 'train', 'validation', 'test'
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);