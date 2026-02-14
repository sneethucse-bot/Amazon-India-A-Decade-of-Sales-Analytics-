import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

st.set_page_config(layout="wide")

# 1️⃣ Cache DB engine
@st.cache_resource
def get_engine():
    return create_engine("sqlite:///amazon_india.db")

engine = get_engine()

# 2️⃣ Cache aggregated join result
@st.cache_data(ttl=600)  # refresh every 10 mins
def load_category_revenue():
    query = """
    SELECT
        p.category,
        SUM(t.final_amount_inr) AS revenue
    FROM transactions t
    JOIN products p ON t.product_id = p.product_id
    GROUP BY p.category
    ORDER BY revenue DESC
    """
    return pd.read_sql(query, engine)

df = load_category_revenue()

# 3️⃣ UI
st.header("📦 Product Performance")

st.bar_chart(df.set_index("category"))