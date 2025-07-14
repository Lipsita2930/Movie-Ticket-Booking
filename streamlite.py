import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Path to workflow output CSV
CSV_OUTPUT_PATH = "output/output_data.csv"

# 🔧 Hardcoded 12-line message
workflow_messages = [
    "Step 1: Loaded input successfully",
    "Step 2: Validated user parameters",
    "Step 3: Connected to database",
    "Step 4: Pulled required metadata",
    "Step 5: Data cleansing completed",
    "Step 6: Applied business logic",
    "Step 7: Merged with external sources",
    "Step 8: Performed aggregations",
    "Step 9: Generated summary tables",
    "Step 10: Exported final output to CSV",
    "Step 11: Logging and audit completed",
    "Step 12: Workflow executed successfully"
]

# 🧠 Dummy workflow function (replace with your logic)
def workflowmanager(user_input):
    df = pd.DataFrame({
        "Category": ["Sales", "Marketing", "Development", "Support"],
        "Amount": [50000, 30000, 80000, 20000],
        "Growth": [12, 9, 15, 7]
    })
    os.makedirs(os.path.dirname(CSV_OUTPUT_PATH), exist_ok=True)
    df.to_csv(CSV_OUTPUT_PATH, index=False)
    return "Workflow complete."

# 🖼️ Streamlit app
st.set_page_config(page_title="Workflow Runner", layout="wide")
st.title("🚀 Dynamic Workflow Runner")

user_input = st.text_input("Enter your input to run workflow:")

if st.button("Run Workflow"):
    if user_input.strip() == "":
        st.warning("⚠️ Please enter a valid input.")
    else:
        with st.spinner("Running workflow..."):
            result_message = workflowmanager(user_input)

        st.success("✅ Workflow completed!")

        # ✅ Display 12-step message (styled)
        st.subheader("🧾 Execution Steps")
        for msg in workflow_messages:
            st.markdown(f"<li style='color:#0a9396; font-weight:600;'>{msg}</li>", unsafe_allow_html=True)

        # ✅ Display CSV data and charts
        if os.path.exists(CSV_OUTPUT_PATH):
            df = pd.read_csv(CSV_OUTPUT_PATH)
            st.subheader("📄 Output Data")
            st.dataframe(df)

            numeric_cols = df.select_dtypes(include="number").columns.tolist()

            if len(numeric_cols) >= 2:
                x_axis = st.selectbox("Select X-axis", options=numeric_cols)
                y_axis = st.selectbox("Select Y-axis", options=numeric_cols, index=1)

                chart_type = st.radio("Chart Type", ["Line", "Bar", "Scatter", "Pie"])

                st.subheader("📈 Chart")

                if chart_type == "Line":
                    fig = px.line(df, x=x_axis, y=y_axis)
                elif chart_type == "Bar":
                    fig = px.bar(df, x=x_axis, y=y_axis, color=x_axis)
                elif chart_type == "Scatter":
                    fig = px.scatter(df, x=x_axis, y=y_axis)
                elif chart_type == "Pie":
                    fig = px.pie(df, names=x_axis, values=y_axis)

                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Not enough numeric columns to plot.")
        else:
            st.error("❌ Output CSV not found.")
