import streamlit as st
import pandas as pd
import plotly.express as px
import os

CSV_PATH = "data.csv"  # Update this to your dynamic CSV file path

st.set_page_config(page_title="Dynamic CSV Dashboard", layout="wide")

st.title("📊 Dynamic Reporting Dashboard")

# Reload interval for the CSV
REFRESH_INTERVAL = 10  # in seconds

# Load CSV dynamically
@st.cache_data(ttl=REFRESH_INTERVAL)
def load_data():
    if os.path.exists(CSV_PATH):
        return pd.read_csv(CSV_PATH)
    else:
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.warning("⚠️ CSV file not found or is empty.")
else:
    st.subheader("🔍 Preview of the Data")
    st.dataframe(df, use_container_width=True)

    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()

    if len(numeric_cols) >= 2:
        st.subheader("📈 Select Chart Parameters")

        x_axis = st.selectbox("Select X-axis", numeric_cols)
        y_axis = st.selectbox("Select Y-axis", numeric_cols, index=1)

        chart_type = st.radio("Select Chart Type", ["Line", "Bar", "Scatter"])

        st.subheader("📊 Generated Chart")

        if chart_type == "Line":
            fig = px.line(df, x=x_axis, y=y_axis, title=f"{chart_type} Chart")
        elif chart_type == "Bar":
            fig = px.bar(df, x=x_axis, y=y_axis, title=f"{chart_type} Chart")
        elif chart_type == "Scatter":
            fig = px.scatter(df, x=x_axis, y=y_axis, title=f"{chart_type} Chart")

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Need at least two numeric columns to generate a chart.")
