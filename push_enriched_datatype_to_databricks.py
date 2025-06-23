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
schema_dest = "enriched_datatype_financial_schema"

# Connect to Databricks SQL
conn = sql.connect(server_hostname=HOST, http_path=HTTP_PATH, access_token=TOKEN)
cursor = conn.cursor()

# Create schema if not exists
cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {catalog}.{schema_dest}")

# Load enriched metadata
with open("enriched_schema_raw_datatype.json") as f:
    enriched = json.load(f)

for table in enriched["tables"]:
    table_name = table["table_name"]
    source_table = f"{catalog}.{schema_src}.{table_name}"
    dest_table = f"{catalog}.{schema_dest}.{table_name}"

    print(f"\n📦 Overwriting table: {dest_table}")

    try:
        # Drop and recreate table
        cursor.execute(f"DROP TABLE IF EXISTS {dest_table}")
        print(f"🗑️  Dropped existing table: {dest_table}")
        cursor.execute(f"CREATE TABLE {dest_table} AS SELECT * FROM {source_table}")
        print("✅ Table copied")

        # Add column comments
        for col in table["columns"]:
            col_name = col["column_name"]
            datatype = col.get("datatype", "string")
            sample_value = col.get("sample_value", "example")
            
            # Format comment with line break
            comment = f"updated datatype: {datatype}\nsample: {sample_value}".replace("'", "")
            
            cursor.execute(f"""
                ALTER TABLE {dest_table}
                ALTER COLUMN {col_name}
                COMMENT '{comment}'
            """)
            
           

        # Add table description
        if "business_process_overview" in table:
            overview = table["business_process_overview"].replace("'", "")
            cursor.execute(f"""
                ALTER TABLE {dest_table}
                SET TBLPROPERTIES ('description' = '{overview}')
            """)
        print("✅ Comments applied")

    except Exception as e:
        print(f"❌ Failed for {table_name}: {e}")

print("\n🎉 All enriched tables overwritten and updated in Databricks.")
