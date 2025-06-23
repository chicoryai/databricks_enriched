import json
import re

# Load the markdown file that contains a JSON blob with 'response'
with open("enriched_output_transform.md", "r") as f:
    raw = json.load(f)

# Grab the embedded markdown content
md_content = raw.get("response", "")

# Extract SQL
sql_match = re.search(r"```sql\n(.*?)```", md_content, re.DOTALL)
sql_code = sql_match.group(1).strip() if sql_match else ""

# Extract JSON
json_match = re.search(r"```json\n(.*?)```", md_content, re.DOTALL)
json_code = json_match.group(1).strip() if json_match else ""

# Save results
if sql_code:
    with open("sql_query_logic.sql", "w") as f:
        f.write(sql_code)
    print("✅ Saved SQL")

if json_code:
    with open("sql_query_logic_output.json", "w") as f:
        f.write(json_code)
    print("✅ Saved JSON")

if not sql_code and not json_code:
    print("⚠️ No blocks found inside extracted markdown.")
