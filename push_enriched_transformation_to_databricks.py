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
schema_src = "enriched_customer360_schema"
schema_dest = "enriched_customer360_schema_enhanced"

# Connect to Databricks
conn = sql.connect(server_hostname=HOST, http_path=HTTP_PATH, access_token=TOKEN)
cursor = conn.cursor()

# ✅ Create the new schema if it doesn't exist
cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {catalog}.{schema_dest}")
print(f"✅ Created or verified schema: {catalog}.{schema_dest}")

# Load your high_risk_customers schema
with open("sql_query_logic_output.json") as f:
    schema_data = json.load(f)

table_name = schema_data["table_name"]
full_table_src = f"{catalog}.{schema_src}.customer_flags_30d"  # Your source table
full_table_dest = f"{catalog}.{schema_dest}.{table_name}"     # high_risk_customers

print(f"\n📦 Creating table and setting enhanced descriptions for: {full_table_dest}")

try:
    # Drop if already exists to overwrite
    cursor.execute(f"DROP TABLE IF EXISTS {full_table_dest}")
    print(f"🗑️  Dropped existing table: {full_table_dest}")

    # Copy table structure and data from source
    cursor.execute(f"CREATE TABLE {full_table_dest} AS SELECT * FROM {full_table_src}")
    print(f"✅ Table created: {full_table_dest}")

    # Clean and set table description
    raw_description = schema_data.get("business_process_overview", "")
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

    print("✅ Table description added (UI + TBLPROPERTY)")

    # Update column comments with derivation logic + enhanced descriptions
    for col in schema_data["columns"]:
        col_name = col["column_name"]
        derivation_logic = col.get("derivation_logic", "")
        enhanced_desc = col.get("enhanced_column_description", "")
        
        # Combine derivation logic and enhanced description
        combined_comment = f"{derivation_logic} | {enhanced_desc}"
        
        # Clean and escape the combined comment
        cleaned_comment = combined_comment.replace("'", "''").strip()
        
        cursor.execute(f"""
            ALTER TABLE {full_table_dest}
            ALTER COLUMN {col_name} COMMENT '{cleaned_comment}'
        """)
        
        print(f" ✏️ Updated column: {col_name}")

    print("✅ All derivation logic + enhanced column descriptions applied")

except Exception as e:
    print(f"❌ Failed for {table_name}: {e}")

# Close connection
cursor.close()
conn.close()

print(f"\n🎉 Enhanced high_risk_customers table created with enhanced descriptions!")
print(f"📊 Query your table: SELECT * FROM {full_table_dest}")
print(f"🔍 View descriptions: DESCRIBE TABLE EXTENDED {full_table_dest}")