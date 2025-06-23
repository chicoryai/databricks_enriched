import os
import json
import re
from databricks import sql
from dotenv import load_dotenv

# Load .env credentials
load_dotenv()

HOST = os.getenv("DATABRICKS_HOST")
TOKEN = os.getenv("DATABRICKS_TOKEN")
HTTP_PATH = os.getenv("DATABRICKS_HTTP_PATH")

catalog = "workspace"
schema_src = "finance_schema"
schema_dest = "enriched_fk_financial_schema"

# Connect to Databricks
conn = sql.connect(server_hostname=HOST, http_path=HTTP_PATH, access_token=TOKEN)
cursor = conn.cursor()

# ✅ Create the new schema if it doesn't exist
cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {catalog}.{schema_dest}")
print(f"✅ Created or verified schema: {catalog}.{schema_dest}")

# Load your enriched FK data
with open("enriched_schema_raw_source.json") as f:
    enriched = json.load(f)

for table in enriched:
    table_name = table["table_name"]
    full_table_src = f"{catalog}.{schema_src}.{table_name}"
    full_table_dest = f"{catalog}.{schema_dest}.{table_name}"

    print(f"\n📦 Creating table and setting description for: {full_table_dest}")

    try:
        # Drop if already exists to overwrite
        cursor.execute(f"DROP TABLE IF EXISTS {full_table_dest}")
        print(f"🗑️  Dropped existing table: {full_table_dest}")

        # Copy table structure and data from source
        cursor.execute(f"CREATE TABLE {full_table_dest} AS SELECT * FROM {full_table_src}")
        print(f"✅ Table created: {full_table_dest}")

        # Clean and set description
        raw_description = table.get("business_process_overview", "")
        cleaned_description = re.sub(r'\[.*?\]', '', raw_description).replace("'", "''").strip()

        # Set UI-visible description
        cursor.execute(f"""
            COMMENT ON TABLE {full_table_dest} IS '{cleaned_description}'
        """)

        # Also set as a TBLPROPERTY
        cursor.execute(f"""
            ALTER TABLE {full_table_dest}
            SET TBLPROPERTIES ('description' = '{cleaned_description}')
        """)

        print("✅ Description added (UI + TBLPROPERTY)")

    except Exception as e:
        print(f"❌ Failed for {table_name}: {e}")

print("\n🎉 All enriched FK tables created and documented in Databricks.")
