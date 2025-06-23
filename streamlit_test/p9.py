import json

# Path to your downloaded service account key
with open("/Users/corinnedavid/Downloads/emakia-236347b5f4b3.json") as f:
    data = json.load(f)


print("[bq.creds]")

for k, v in data.items():
    if k == "private_key":
        # Ensure the private key has real line breaks for TOML
        v_clean = v.replace("\\n", "\n") if "\\n" in v else v
        print(f'{k} = """{v_clean}"""')
    else:
        print(f'{k} = "{v}"')
