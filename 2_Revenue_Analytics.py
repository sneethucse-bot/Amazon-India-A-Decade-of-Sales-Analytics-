import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

st.set_page_config(layout="wide")

# 1️⃣ Cache DB engine (created once)
@st.cache_resource
def get_engine():
    return create_engine("sqlite:///amazon_india.db")

engine = get_engine()

# 2️⃣ Load year range ONCE (very small query)
@st.cache_data
def get_year_range():
    q = "SELECT MIN(order_year) AS min_year, MAX(order_year) AS max_year FROM transactions"
    return pd.read_sql(q, engine)

years = get_year_range()

# 3️⃣ Load monthly revenue BY YEAR (cached per year)
@st.cache_data(ttl=300)
def load_monthly_revenue(year):
    query = """
    SELECT
        order_month,
        SUM(final_amount_inr) AS revenue
    FROM transactions
    WHERE order_year = :year
    GROUP BY order_month
    ORDER BY order_month
    """
    return pd.read_sql(query, engine, params={"year": year})

# 4️⃣ UI
st.header("📊 Revenue Analytics")

year = st.slider(
    "Year",
    int(years.min_year.iloc[0]),
    int(years.max_year.iloc[0])
)

monthly = load_monthly_revenue(year)

st.bar_chart(monthly.set_index("order_month"))