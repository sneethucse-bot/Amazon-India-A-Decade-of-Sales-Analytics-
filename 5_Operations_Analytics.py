import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

st.set_page_config(layout="wide")

# 1️⃣ Cache DB engine
@st.cache_resource
def get_engine():
    return create_engine("sqlite:///amazon_india.db")

engine = get_engine()

# 2️⃣ Aggregate delivery days in SQL (FAST)
@st.cache_data(ttl=300)
def load_delivery_distribution():
    query = """
    SELECT
        delivery_days,
        COUNT(*) AS orders
    FROM transactions
    GROUP BY delivery_days
    ORDER BY delivery_days
    """
    return pd.read_sql(query, engine)

df = load_delivery_distribution()

# 3️⃣ UI
st.header("🚚 Operations & Logistics")

st.bar_chart(df.set_index("delivery_days"))