import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 🔧 Customize this path to match where your workflow writes the CSV
CSV_OUTPUT_PATH = "output/output_data.csv"

# 🧠 Your actual workflow function
def workflowmanager(user_input):
    """
    Simulate running your workflow.
    Replace this with your actual logic.
    It saves a CSV file and returns a string log/message.
    """
    # Simulated output message
    message = f"Workflow executed successfully for input: '{user_input}'"

    # Simulate writing a CSV file
    df = pd.DataFrame({
        "step": [1, 2, 3, 4],
        "value": [10, 15, 20, 18]
    })
    os.makedirs(os.path.dirname(CSV_OUTPUT_PATH), exist_ok=True)
    df.to_csv(CSV_OUTPUT_PATH, index=False)

    return message


# 🌐 Streamlit App
st.set_page_config(page_title="Workflow Runner with Output", layout="wide")

st.title("🛠️ Dynamic Workflow Runner")

# 📥 User Input
user_input = st.text_input("Enter your input (e.g., keyword or ID):")

if st.button("Run Workflow"):
    if user_input.strip() == "":
        st.warning("⚠️ Please enter something.")
    else:
        with st.spinner("Running your workflow..."):
            # Call the workflow
            result_message = workflowmanager(user_input)

        # 📝 Show log/message
        st.success("✅ Workflow finished!")
        st.subheader("📄 Log Output:")
        st.code(result_message)

        # 📊 Try loading and visualizing the generated CSV
        if os.path.exists(CSV_OUTPUT_PATH):
            st.subheader("📊 Data Output Preview:")
            df = pd.read_csv(CSV_OUTPUT_PATH)
            st.dataframe(df)

            # 🎨 Chart section
            numeric_cols = df.select_dtypes(include='number').columns.tolist()
            if len(numeric_cols) >= 2:
                x_axis = st.selectbox("X-axis:", options=numeric_cols)
                y_axis = st.selectbox("Y-axis:", options=numeric_cols, index=1)

                chart_type = st.radio("Chart Type:", ["Line", "Bar", "Scatter"])

                if chart_type == "Line":
                    fig = px.line(df, x=x_axis, y=y_axis)
                elif chart_type == "Bar":
                    fig = px.bar(df, x=x_axis, y=y_axis)
                elif chart_type == "Scatter":
                    fig = px.scatter(df, x=x_axis, y=y_axis)

                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("⚠️ Not enough numeric columns for plotting.")
        else:
            st.error(f"❌ CSV file not found at: {CSV_OUTPUT_PATH}")
