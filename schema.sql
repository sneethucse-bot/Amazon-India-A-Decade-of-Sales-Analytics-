CREATE TABLE IF NOT EXISTS products (
    product_id TEXT PRIMARY KEY,
    product_name TEXT,
    category TEXT,
    subcategory TEXT,
    brand TEXT,
    base_price_2015 REAL,
    is_prime_eligible BOOLEAN,
    launch_year INTEGER
);

CREATE TABLE IF NOT EXISTS customers (
    customer_id TEXT PRIMARY KEY,
    customer_city TEXT,
    customer_state TEXT,
    age_group TEXT,
    customer_spending_tier TEXT
);

CREATE TABLE IF NOT EXISTS transactions (
    transaction_id TEXT PRIMARY KEY,
    customer_id TEXT,
    product_id TEXT,
    order_date DATE,
    order_year INTEGER,
    order_month INTEGER,
    final_amount_inr REAL,
    discount_percent REAL,
    payment_method TEXT,
    delivery_days INTEGER,
    return_status TEXT,
    customer_rating REAL,
    is_prime_member BOOLEAN,
    is_festival_sale BOOLEAN,
    festival_name TEXT,
    FOREIGN KEY(customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY(product_id) REFERENCES products(product_id)
);

CREATE INDEX idx_year ON transactions(order_year);
CREATE INDEX idx_customer ON transactions(customer_id);
CREATE INDEX idx_product ON transactions(product_id);