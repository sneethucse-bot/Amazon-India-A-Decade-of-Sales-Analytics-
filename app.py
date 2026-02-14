import streamlit as st
import sqlite3
import pandas as pd

# -----------------------
# PAGE CONFIG
# -----------------------
st.set_page_config(
    page_title="Amazon India Analytics",
    layout="wide"
)

st.title("🛒 Amazon India – E-Commerce Analytics Dashboard")
st.caption("Optimized BI Dashboard | SQL-first | Scalable")

DB_PATH = "amazon_india.db"

# -----------------------
# DATABASE CONNECTION
# -----------------------
def get_connection():
    return sqlite3.connect(DB_PATH)

# -----------------------
# LOAD FILTER VALUES
# -----------------------
@st.cache_data
def get_years():
    conn = get_connection()
    years = pd.read_sql(
        "SELECT DISTINCT order_year FROM transactions ORDER BY order_year",
        conn
    )["order_year"].tolist()
    conn.close()
    return years

years = get_years()

# -----------------------
# SIDEBAR FILTERS
# -----------------------
st.sidebar.header("🔍 Filters")

selected_years = st.sidebar.multiselect(
    "Select Year(s)",
    years,
    default=years
)

year_filter_sql = ",".join(map(str, selected_years))

# -----------------------
# KPI QUERIES (SQL AGGREGATION)
# -----------------------
@st.cache_data
def load_kpis(years_sql):
    conn = get_connection()
    query = f"""
        SELECT
            SUM(final_amount_inr) AS revenue,
            COUNT(*) AS orders,
            COUNT(DISTINCT customer_id) AS customers,
            AVG(final_amount_inr) AS aov
        FROM transactions
        WHERE order_year IN ({years_sql})
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df.iloc[0]

kpi = load_kpis(year_filter_sql)

# -----------------------
# KPI DISPLAY
# -----------------------
c1, c2, c3, c4 = st.columns(4)

c1.metric("💰 Total Revenue", f"₹{kpi.revenue:,.0f}")
c2.metric("📦 Total Orders", f"{int(kpi.orders):,}")
c3.metric("👥 Active Customers", f"{int(kpi.customers):,}")
c4.metric("🛍 Avg Order Value", f"₹{kpi.aov:,.0f}")

st.divider()

# -----------------------
# REVENUE TREND (FAST)
# -----------------------
@st.cache_data
def revenue_trend(years_sql):
    conn = get_connection()
    query = f"""
        SELECT order_year,
               SUM(final_amount_inr) AS revenue
        FROM transactions
        WHERE order_year IN ({years_sql})
        GROUP BY order_year
        ORDER BY order_year
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

st.subheader("📈 Revenue Trend (Yearly)")
rev_df = revenue_trend(year_filter_sql)
st.line_chart(rev_df, x="order_year", y="revenue")

# -----------------------
# TOP CITIES
# -----------------------
@st.cache_data
def top_cities(years_sql):
    conn = get_connection()
    query = f"""
        SELECT customer_city,
               SUM(final_amount_inr) AS revenue
        FROM transactions
        WHERE order_year IN ({years_sql})
        GROUP BY customer_city
        ORDER BY revenue DESC
        LIMIT 10
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

st.subheader("🏙 Top 10 Customer Cities")
st.bar_chart(top_cities(year_filter_sql), x="customer_city", y="revenue")

# -----------------------
# PAYMENT METHODS
# -----------------------
@st.cache_data
def payment_distribution(years_sql):
    conn = get_connection()
    query = f"""
        SELECT payment_method,
               COUNT(*) AS orders
        FROM transactions
        WHERE order_year IN ({years_sql})
        GROUP BY payment_method
        ORDER BY orders DESC
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

st.subheader("💳 Payment Method Usage")
st.bar_chart(payment_distribution(year_filter_sql), x="payment_method", y="orders")

# -----------------------
# PRIME VS NON-PRIME
# -----------------------
@st.cache_data
def prime_analysis(years_sql):
    conn = get_connection()
    query = f"""
        SELECT
            is_prime_member,
            AVG(final_amount_inr) AS avg_order_value,
            COUNT(*) AS orders
        FROM transactions
        WHERE order_year IN ({years_sql})
        GROUP BY is_prime_member
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

st.subheader("⭐ Prime vs Non-Prime Customers")
st.dataframe(prime_analysis(year_filter_sql))

# -----------------------
# SAMPLE DATA (LIMITED)
# -----------------------
@st.cache_data
def sample_data(years_sql):
    conn = get_connection()
    query = f"""
        SELECT *
        FROM transactions
        WHERE order_year IN ({years_sql})
        LIMIT 1000
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

with st.expander("📄 View Sample Transactions (1000 rows)"):
    st.dataframe(sample_data(year_filter_sql))

# -----------------------
# FOOTER
# -----------------------
st.caption("🚀 Built with Streamlit + SQLite | Optimized for Large-Scale BI")