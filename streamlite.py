import streamlit as st
import pandas as pd
import plotly.express as px
import time
import os
from src.workflow_manager import WorkflowManager
import uuid
from src.snowflake_connection import create_snowflake_connection
from config.config import Config
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from data_dic.table_name import TableManager
from pyspark.sql import SparkSession
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Dashboard Runner", layout="wide")

CSV_PATH = "data_dic/sample/CAT_INFORCE_sample.csv" 

# ✅ Run workflow only once
if "workflow_ran" not in st.session_state:
    st.session_state.workflow_ran = False
    st.session_state.result_message = []

def call_workFlowManager(user_input):
    workflow_manager = WorkflowManager()
    final_state = workflow_manager.run(input_message=user_input, thread_id=str(uuid.uuid4()))
    return final_state


st.title("Dynamic Dashboard")

user_input = st.text_input("Enter your query.")

if st.button("Run Workflow"):
    if user_input.strip() == "":
        st.warning("⚠️ Please enter something.")
    else:
        with st.spinner("Running your workflow..."):
            call_workFlowManager(user_input)
            st.session_state.workflow_ran = True
            st.session_state.result_message = [
                "New Business: There are 6,203 new business entries recorded, indicating a robust influx of new clients or policies.",
                "Renewal: The renewal count stands at 14,420, showcasing a strong retention rate of existing customers.",
                "Total Inforce: The total number of inforce policies is 20,623, which combines both new and renewed policies, reflecting the overall active customer base.",
                "Cancelled Policies: There have been 439 cancellations, which suggests a relatively low churn rate compared to the total inforce policies.",
                "Financial Overview: The total premium collected from new business amounts to $104,537,613, while the total premium from renewals is $209,455,097. This indicates that renewals contribute significantly more to the overall premium income.",
                "Total Premium: The overall total premium across all policies is $313,992,710, which is a critical indicator of the business's financial health.",
                "Summary By Time Period: The graphical representation shows the distribution of inforce count and annual premium over the months. Notably, January 2025 shows a significant amount of inforce policies and premiums, suggesting a strong start to the year.",
                "Segment Summary: The segment summary indicates that the annual premium for most policies is below $300,000, which could imply a focus on smaller policies or clients.",
                "Demographics: A large number of policyholders fall in the age range of 30-45, indicating a younger customer base.",
                "Geographical Spread: The majority of policies are concentrated in metro cities, particularly Mumbai, Delhi, and Bangalore.",
                "Channel Performance: Direct sales have the highest premium conversion rate, while broker channels handle the highest volume.",
                "Policy Types: Term insurance and ULIPs form the bulk of the policy portfolio."
            ]

# ✅ Display only after workflow ran
if st.session_state.workflow_ran:

    st.success("Workflow finished!")
    st.subheader("Log Output:")

    for msg in st.session_state.result_message:
        st.markdown(f"<li style='color:#0a9396; font-weight:600;'>{msg}</li>", unsafe_allow_html=True)

    if os.path.exists(CSV_PATH):
        st.subheader("📊 Query Result Preview:")
        df = pd.read_csv(CSV_PATH)
        st.dataframe(df)

        numeric_cols = df.select_dtypes(include='number').columns.tolist()
        if len(numeric_cols) >= 2:
            x_axis = st.selectbox("X-axis:", options=numeric_cols)
            y_axis = st.selectbox("Y-axis:", options=numeric_cols, index=1)

            chart_type = st.radio("Chart Type", ["Line", "Bar", "Scatter", "Pie"])

            if chart_type == "Line":
                fig = px.line(df, x=x_axis, y=y_axis)
            elif chart_type == "Bar":
                fig = px.bar(df, x=x_axis, y=y_axis)
            elif chart_type == "Scatter":
                fig = px.scatter(df, x=x_axis, y=y_axis)
            elif chart_type == "Pie":
                fig = px.pie(df, names=x_axis, values=y_axis)

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ Not enough numeric columns for plotting.")
    else:
        st.error(f"❌ CSV file not found at: {CSV_PATH}")
