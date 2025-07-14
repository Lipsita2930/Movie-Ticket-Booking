import pandas as pd
import os

def get_summary_prompt_from_csv(tool_csv_filename):
    data_folder = "data_dic/"

    # ---------- Load Schema and Relationship Files ----------
    table_info_path = os.path.join(data_folder, "table_descriptions.csv")
    relationships_path = os.path.join(data_folder, "RELATIONSHIPS.csv")

    try:
        table_info_df = pd.read_csv(table_info_path)
        table_info_df["Table Name"] = table_info_df["Table Name"].str.strip().str.upper()
    except Exception as e:
        return f"Error reading table_descriptions.csv: {e}"

    try:
        relationships_df = pd.read_csv(relationships_path)
    except Exception as e:
        return f"Error reading RELATIONSHIPS.csv: {e}"

    # ---------- Load Tool Results Data ----------
    tool_csv_path = os.path.join(data_folder, tool_csv_filename)

    try:
        if not os.path.exists(tool_csv_path):
            return "No summary can be generated."
        tool_results_df = pd.read_csv(tool_csv_path)
        if tool_results_df.empty:
            return "No summary can be generated."
    except Exception as e:
        return f"Error reading {tool_csv_filename}: {e}"

    # Convert tool results to markdown table format
    tool_results_str = tool_results_df.to_markdown(index=False)

    # ---------- Prompt Generation ----------
    prompt = []

    prompt.append(f"""
# 📈 Insight Summary - Based Only on Tool Data

You are a dashboard analyst generating insights based solely on the **tool results** provided below.

---

### ✅ INSTRUCTIONS

- Use **only the tool data** to generate your insights.
- Ignore all other metadata, schema definitions, or relationships.
- Your output must contain **exactly 5 short, crisp, data-driven bullet points**.
- The tone should be **executive-friendly** and **focused on the data values**.
- If no meaningful insights can be derived, simply return:  
  **"No summary can be generated."**

---

## 📥 TOOL DATA

{tool_results_str}


---

## 🧠 OUTPUT FORMAT (EXAMPLE ONLY — DO NOT USE THESE VALUES)

_The following is a training/example section to show the expected style. It is not part of your actual analysis._

**Example:**

- The number of new policies in Jan 2025 was **6,203**, indicating a strong start.
- Renewal counts reached **14,420**, reflecting solid customer retention.
- Cancellations were low at **439**, under 2.5% of total active policies.
- The total premium collected crossed **$313 million**, with renewals contributing over **$209 million**.
- March 2025 marked the highest spike in premium growth across all months.

---

## ✅ FINAL SUMMARY (YOUR TASK)

Please provide **exactly 5 bullet points** summarizing insights from the provided tool data.
""")

    return "\n".join(prompt)

