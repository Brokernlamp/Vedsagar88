import streamlit as st
import requests
import pandas as pd

NOCODB_BASE_URL = "https://app.nocodb.com"
NOCODB_API_TOKEN = "bf3teMimRCaM9KV3pdaBgWo666jJQLeAI2s5kxlu"
NOCODB_PROJECT_NAME = "pxf5yahsh743r6d"

headers = {"xc-token": NOCODB_API_TOKEN}

url = f"{NOCODB_BASE_URL}/api/v1/db/data/v1/{NOCODB_PROJECT_NAME}/students"

response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    st.write("✅ Raw API Response:")
