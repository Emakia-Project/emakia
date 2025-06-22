from google.cloud import bigquery
from google.oauth2 import service_account

creds = service_account.Credentials.from_service_account_file("/Users/corinnedavid/Downloads/emakia-722bcde763ae.json")
client = bigquery.Client(credentials=creds, project=creds.project_id)

# Quick test
for dataset in client.list_datasets():  
    print(f"Found dataset: {dataset.dataset_id}")
