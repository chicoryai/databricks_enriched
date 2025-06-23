import os
import json
from databricks import sql
from dotenv import load_dotenv

# Load credentials from .env
load_dotenv()

HOST = os.getenv("DATABRICKS_HOST")
TOKEN = os.getenv("DATABRICKS_TOKEN")
HTTP_PATH = os.getenv("DATABRICKS_HTTP_PATH")

catalog = "workspace"
schema_src = "finance_schema"
schema_dest = "enriched_type_financial_schema"

# Connect to Databricks SQL
conn = sql.connect(server_hostname=HOST, http_path=HTTP_PATH, access_token=TOKEN)
cursor = conn.cursor()

# ✅ Create destination schema if it doesn't exist
cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {catalog}.{schema_dest}")
print(f"✅ Schema created or verified: {catalog}.{schema_dest}")

# Load updated types from agent output
with open("enriched_schema_datatype.json") as f:
    enriched = json.load(f)

for table in enriched["tables"]:
    table_name = table["table_name"]
    full_src = f"{catalog}.{schema_src}.{table_name}"
    full_dest = f"{catalog}.{schema_dest}.{table_name}"

    print(f"\n📦 Creating and altering: {full_dest}")

    try:
        # Drop & recreate table
        cursor.execute(f"DROP TABLE IF EXISTS {full_dest}")
        cursor.execute(f"CREATE TABLE {full_dest} AS SELECT * FROM {full_src}")
        print("✅ Table copied")

        # Alter column types
        for col in table["columns"]:
            col_name = col["column_name"]
            new_type = col["datatype"]
            try:
                cursor.execute(f"""
                    ALTER TABLE {full_dest}
                    ALTER COLUMN {col_name} TYPE {new_type}
                """)
                print(f"  ✅ {col_name} → {new_type}")
            except Exception as col_err:
                print(f"  ❌ Could not cast {col_name}: {col_err}")

    except Exception as tbl_err:
        print(f"❌ Failed to create table {table_name}: {tbl_err}")

print("\n🎉 All tables created in enriched_type_financial_schema with updated datatypes.")
