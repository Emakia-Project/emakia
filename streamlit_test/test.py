import json

with open("emakia-key.json") as f:
    creds = json.load(f)

print(creds["private_key"])

print("First 60 chars of private key:")
print("First 60 chars of private key:")
st.write("🔎 First 20 chars of private key:")
st.code(repr(st.secrets["bq"]["creds"]["private_key"][:60]))
