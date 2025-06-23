import json

with open("/Users/corinnedavid/Downloads/emakia-236347b5f4b3.json") as f:
    data = json.load(f)

print("[bq.creds]")
for k, v in data.items():
    if k == "private_key":
        print(f'{k} = """{v}"""')  # Triple quotes preserve real newlines
    else:
        print(f'{k} = "{v}"')
