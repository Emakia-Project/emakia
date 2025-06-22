import json
from google.oauth2 import service_account
from google.cloud import bigquery
import streamlit as st
import os 
# Initialize BigQuery client

client = bigquery.Client()
print("✅ BigQuery client initialized.")
        
limit = 25 
offset = 50

query = f"""
        SELECT * FROM `emakia.politics2024.tweets` LIMIT 100
    """


results = client.query(query).result()