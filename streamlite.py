import streamlit as st
import pandas as pd
import plotly.express as px
import time
import os

CSV_PATH = "data.csv"  # Path to your dynamic CSV file

# Title
st.title("📊 Dynamic CSV Dashboard")

# Auto-refresh every X seconds
REFRESH_INTERVAL = 10  # in seconds
st.caption(f"Refreshing every {REFRESH_INTERVAL} seconds")

# Load CSV
@st.cache_data(ttl=REFRESH_INTERVAL)
def load_data():
    if os.path.exists(CSV_PATH):
        return pd.read_csv(CSV_PATH)
    else:
        st.warning("CSV file not found.")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    st.write("### Preview of Data")
    st.dataframe(df)

    # Let user pick X and Y axes
    numeric_columns = df.select_dtypes(include='number').columns.tolist()
    if numeric_columns:
        x_axis = st.selectbox("Select X-axis:", options=numeric_columns)
        y_axis = st.selectbox("Select Y-axis:", options=numeric_columns, index=1 if len(numeric_columns) > 1 else 0)

        chart_type = st.selectbox("Select chart type:", ["Line", "Bar", "Scatter"])

        # Plot using Plotly
        if chart_type == "Line":
            fig = px.line(df, x=x_axis, y=y_axis)
        elif chart_type == "Bar":
            fig = px.bar(df, x=x_axis, y=y_axis)
        elif chart_type == "Scatter":
            fig = px.scatter(df, x=x_axis, y=y_axis)

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No numeric columns found in the CSV.")
else:
    st.error("No data to display.")

