import pandas as pd
import sqlite3
import os

# -----------------------
# PATH CONFIGURATION
# -----------------------
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
RAW_PATH = os.path.join(BASE_DIR, "data", "raw")
CLEAN_PATH = os.path.join(BASE_DIR, "data", "cleaned")
DB_PATH = os.path.join(BASE_DIR, "amazon_india.db")

os.makedirs(CLEAN_PATH, exist_ok=True)

# -----------------------
# DATABASE CONNECTION
# -----------------------
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("✅ Connected to database:", DB_PATH)

# -----------------------
# LOAD & MERGE YEARLY FILES
# -----------------------
all_years = []

for year in range(2015, 2026):
    file_path = os.path.join(RAW_PATH, f"amazon_india_{year}.csv")

    if os.path.exists(file_path):
        print(f"📂 Loading {file_path}")
        df_year = pd.read_csv(file_path)
        df_year["order_year"] = year
        all_years.append(df_year)
    else:
        print(f"⚠ Missing file: amazon_india_{year}.csv")

if not all_years:
    raise FileNotFoundError("❌ No yearly files found in data/raw/")

transactions = pd.concat(all_years, ignore_index=True)
print(f"✅ Total transactions loaded: {len(transactions):,}")

# -----------------------
# BASIC CLEANING (SAFE)
# -----------------------
transactions.columns = transactions.columns.str.lower().str.strip()

# Ensure required columns exist
required_cols = [
    "transaction_id",
    "customer_id",
    "product_id",
    "order_date",
    "final_amount_inr",
    "customer_city",
    "customer_state",
    "payment_method",
    "delivery_days",
    "is_prime_member"
]

for col in required_cols:
    if col not in transactions.columns:
        transactions[col] = None

# Convert dates
transactions["order_date"] = pd.to_datetime(
    transactions["order_date"], errors="coerce"
)

# Convert numerics
transactions["final_amount_inr"] = pd.to_numeric(
    transactions["final_amount_inr"], errors="coerce"
)

transactions["delivery_days"] = pd.to_numeric(
    transactions["delivery_days"], errors="coerce"
)

# Boolean cleanup
transactions["is_prime_member"] = transactions["is_prime_member"].astype(str).str.lower().isin(
    ["true", "1", "yes", "y"]
)

# -----------------------
# SAVE CLEANED TRANSACTIONS
# -----------------------
transactions.to_csv(
    os.path.join(CLEAN_PATH, "transactions_cleaned.csv"), index=False
)

print("✅ transactions_cleaned.csv created")

# -----------------------
# LOAD PRODUCTS (OPTIONAL)
# -----------------------
products_path = os.path.join(RAW_PATH, "amazon_india_products_catalog.csv")

if os.path.exists(products_path):
    products = pd.read_csv(products_path)
    products.columns = products.columns.str.lower().str.strip()

    products.to_csv(
        os.path.join(CLEAN_PATH, "products_cleaned.csv"), index=False
    )

    products.to_sql("products", conn, if_exists="replace", index=False)
    print("✅ Products table created")
else:
    print("⚠ products catalog not found – skipping products table")

# -----------------------
# CREATE CUSTOMERS TABLE
# -----------------------
customers = transactions[[
    "customer_id",
    "customer_city",
    "customer_state",
    "is_prime_member"
]].drop_duplicates()

customers.to_sql("customers", conn, if_exists="replace", index=False)

print("✅ Customers table created with columns:", customers.columns.tolist())

# -----------------------
# CREATE TIME DIMENSION
# -----------------------
time_dim = transactions[["order_date"]].dropna().drop_duplicates()
time_dim["date"] = time_dim["order_date"]
time_dim["year"] = time_dim["date"].dt.year
time_dim["month"] = time_dim["date"].dt.month
time_dim["quarter"] = time_dim["date"].dt.to_period("Q").astype(str)
time_dim["day"] = time_dim["date"].dt.day

time_dim = time_dim.drop(columns=["order_date"])

time_dim.to_sql("time_dimension", conn, if_exists="replace", index=False)

print("✅ Time dimension table created")

# -----------------------
# CREATE TRANSACTIONS TABLE
# -----------------------
transactions.to_sql("transactions", conn, if_exists="replace", index=False)

print("✅ Transactions table created")

# -----------------------
# INDEXING FOR PERFORMANCE
# -----------------------
cursor.execute("CREATE INDEX IF NOT EXISTS idx_txn_date ON transactions(order_date)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_txn_customer ON transactions(customer_id)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_txn_product ON transactions(product_id)")

conn.commit()
conn.close()

print("\n🎉 DATABASE BUILD COMPLETE")
print("📦 Database file:", DB_PATH)