import streamlit as st
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sklearn.linear_model import LinearRegression

st.set_page_config(layout="wide")

# 1️⃣ Cache DB engine
@st.cache_resource
def get_engine():
    return create_engine("sqlite:///amazon_india.db")

engine = get_engine()

# 2️⃣ Load YEARLY revenue using SQL (tiny dataset)
@st.cache_data(ttl=600)
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

yearly = load_yearly_revenue()

# 3️⃣ Train model (cached)
@st.cache_resource
def train_model(data):
    X = data[["order_year"]]
    y = data["revenue"]
    model = LinearRegression()
    model.fit(X, y)
    return model

model = train_model(yearly)

# 4️⃣ Forecast
future_years = np.array([[2026], [2027]])
predictions = model.predict(future_years)

forecast_df = pd.DataFrame({
    "Year": [2026, 2027],
    "Predicted Revenue (INR)": predictions.astype(int)
})

# 5️⃣ UI
st.header("🔮 Predictive Analytics")

c1, c2 = st.columns(2)

c1.metric("Forecast 2026", f"₹{forecast_df.iloc[0,1]:,}")
c2.metric("Forecast 2027", f"₹{forecast_df.iloc[1,1]:,}")

st.subheader("📈 Historical + Forecast Trend")

plot_df = pd.concat([
    yearly.rename(columns={"revenue": "value"}).assign(type="Actual"),
    forecast_df.rename(columns={"Predicted Revenue (INR)": "value"}).assign(type="Forecast")
])

st.line_chart(plot_df.set_index("order_year" if "order_year" in plot_df else "Year")["value"])