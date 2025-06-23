import json
import os

# Load your local service account JSON
with open("emakia-key.json") as f:
    data = json.load(f)

# Format as TOML content with clean private_key
toml_lines = ["[bq.creds]"]
for k, v in data.items():
    if k == "private_key":
        v_clean = v.replace("\\n", "\n") if "\\n" in v else v
        toml_lines.append(f'{k} = """{v_clean}"""')
    else:
        toml_lines.append(f'{k} = "{v}"')

# Ensure target folder exists
os.makedirs(".streamlit", exist_ok=True)

# Write to secrets.toml
with open(".streamlit/secrets.toml", "w") as f:
    f.write("\n".join(toml_lines))

print("✅ secrets.toml written to .streamlit/")
