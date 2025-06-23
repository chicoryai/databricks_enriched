from dotenv import load_dotenv
load_dotenv()

from databricks import sql
import json
import os

HOST = os.getenv("DATABRICKS_HOST")
TOKEN = os.getenv("DATABRICKS_TOKEN")
HTTP_PATH = os.getenv("DATABRICKS_HTTP_PATH")

catalog = "workspace"
schema = "finance_schema"

conn = sql.connect(server_hostname=HOST, http_path=HTTP_PATH, access_token=TOKEN)
cursor = conn.cursor()

cursor.execute(f"SHOW TABLES IN {catalog}.{schema}")
tables = [row.tableName for row in cursor.fetchall()]

schema_result = {"tables": []}

for table in tables:
    cursor.execute(f"DESCRIBE TABLE {catalog}.{schema}.{table}")
    cols = cursor.fetchall()

    columns = []
    for col in cols:
        if col.col_name and not col.col_name.startswith("#"):
            columns.append({"column_name": col.col_name, "column_type": col.data_type})

    schema_result["tables"].append({
        "table_name": table,
        "columns": columns
    })

with open("financial_schema.json", "w") as f:
    json.dump(schema_result, f, indent=2)

print("✅ Saved to financial_schema.json")
