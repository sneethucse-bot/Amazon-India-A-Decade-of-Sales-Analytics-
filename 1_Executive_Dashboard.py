import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

st.set_page_config(layout="wide")

# 1️⃣ Cache DB connection (very important)
@st.cache_resource
def get_engine():
    return create_engine("sqlite:///amazon_india.db")

engine = get_engine()

# 2️⃣ Cache aggregated queries instead of full table
@st.cache_data(ttl=300)  # refresh every 5 mins
def load_kpis():
    query = """
    SELECT
        SUM(final_amount_inr) AS total_revenue,
        COUNT(DISTINCT customer_id) AS active_customers,
        AVG(final_amount_inr) AS avg_order_value
    FROM transactions
    """
    return pd.read_sql(query, engine)

@st.cache_data(ttl=300)
def load_yearly_revenue():
    query = """
    SELECT
        order_year,
        SUM(final_amount_inr) AS revenue
    FROM transactions
    GROUP BY order_year
    ORDER BY order_year
    """
    return pd.read_sql(query, engine)

kpis = load_kpis()
yearly = load_yearly_revenue()

# 3️⃣ UI Rendering (very fast now)
st.header("📊 Executive Summary")

c1, c2, c3 = st.columns(3)

c1.metric("Total Revenue", f"₹{kpis.total_revenue.iloc[0]:,.0f}")
c2.metric("Active Customers", int(kpis.active_customers.iloc[0]))
c3.metric("Avg Order Value", f"₹{kpis.avg_order_value.iloc[0]:,.0f}")

st.line_chart(yearly.set_index("order_year"))