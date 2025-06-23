import os
import json
import re
from databricks import sql
from dotenv import load_dotenv

# Load credentials from .env
load_dotenv()

HOST = os.getenv("DATABRICKS_HOST")
TOKEN = os.getenv("DATABRICKS_TOKEN")
HTTP_PATH = os.getenv("DATABRICKS_HTTP_PATH")

catalog = "workspace"
schema_src = "finance_schema"
schema_dest = "enriched_column_financial_schema"

# Connect to Databricks SQL
conn = sql.connect(server_hostname=HOST, http_path=HTTP_PATH, access_token=TOKEN)
cursor = conn.cursor()

# Create schema if not exists
cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {catalog}.{schema_dest}")

# Load enriched metadata
with open("enriched_schema_raw.json") as f:
    enriched = json.load(f)

for table in enriched["tables"]:
    table_name = table["table_name"]
    source_table = f"{catalog}.{schema_src}.{table_name}"
    dest_table = f"{catalog}.{schema_dest}.{table_name}"

    print(f"\n📦 Overwriting table: {dest_table}")

    try:
        # Drop existing table and recreate
        cursor.execute(f"DROP TABLE IF EXISTS {dest_table}")
        print(f"🗑️  Dropped existing table: {dest_table}")
        cursor.execute(f"CREATE TABLE {dest_table} AS SELECT * FROM {source_table}")
        print("✅ Table copied")

        # Add column comments with formatted description + sample
        for col in table["columns"]:
            col_name = col["column_name"]
            raw_desc = col.get("column_description", "")
            sample = col.get("sample_value", "")

            # Clean and replace single quotes with double quotes
            cleaned_desc = re.sub(r'\[.*?\]', '', raw_desc).strip().replace("'", '"')
            cleaned_sample = sample.strip().replace("'", '"')

            comment = f"column description: {cleaned_desc} | sample: {cleaned_sample}"

            cursor.execute(f"""
                ALTER TABLE {dest_table}
                ALTER COLUMN {col_name}
                COMMENT '{comment}'
            """)

        # Add table-level description
        if "business_process_overview" in table:
            overview = re.sub(r'\[.*?\]', '', table["business_process_overview"]).strip().replace("'", '"')
            cursor.execute(f"""
                ALTER TABLE {dest_table}
                SET TBLPROPERTIES ('description' = '{overview}')
            """)
        print("✅ Comments applied")

    except Exception as e:
        print(f"❌ Failed for {table_name}: {e}")

print("\n🎉 All enriched tables overwritten and updated in Databricks.")
