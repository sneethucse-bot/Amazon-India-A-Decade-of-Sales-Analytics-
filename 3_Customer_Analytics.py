import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

st.set_page_config(layout="wide")

# 1️⃣ Cache engine
@st.cache_resource
def get_engine():
    return create_engine("sqlite:///amazon_india.db")

engine = get_engine()

# 2️⃣ Load ONLY aggregated data (tiny result)
@st.cache_data(ttl=300)
def load_prime_revenue():
    query = """
    SELECT
        is_prime_member,
        AVG(final_amount_inr) AS avg_revenue
    FROM transactions
    GROUP BY is_prime_member
    """
    return pd.read_sql(query, engine)

prime_df = load_prime_revenue()

# 3️⃣ UI
st.header("👥 Customer Analytics")

# Optional: readable labels
prime_df["is_prime_member"] = prime_df["is_prime_member"].map(
    {0: "Non-Prime Customers", 1: "Prime Customers"}
)

st.bar_chart(prime_df.set_index("is_prime_member"))