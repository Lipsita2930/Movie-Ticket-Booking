import pandas as pd
from langchain.tools import tool
from src.utils import create_snowflake_connection  # Make sure this is implemented

@tool
def query_snowflake(query: str) -> str:
    """Execute the Snowflake query and return the result as a formatted string."""
    print("---------------------Query to be executed-------------------------")
    conn = create_snowflake_connection()
    print(query)
    cursor = conn.cursor()
    csv_file_path = 'output/query_results.csv'

    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        print(rows)
        columns = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(rows, columns=columns)
        df.to_csv(csv_file_path, index=False)

        res = [", ".join(columns)]
        for row in rows:
            res.append(", ".join(str(val) for val in row))
        return "\n".join(res)

    except Exception as e:
        print('❌ Something went wrong:', e)
        return f"error: {str(e)}"

    finally:
        cursor.close()
        conn.close()
