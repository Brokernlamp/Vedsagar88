import streamlit as st
import requests
import pandas as pd

# Load NocoDB config (hardcoded)
NOCODB_BASE_URL = "https://app.nocodb.com"
NOCODB_API_TOKEN = "bf3teMimRCaM9KV3pdaBgWo666jJQLeAI2s5kxlu"
NOCODB_WORKSPACE_ID = "wd6chino"
NOCODB_BASE_ID = "pxf5yahsh743r6d"

headers = {"xc-token": NOCODB_API_TOKEN}

# Fetch students from NocoDB
url = f"{NOCODB_BASE_URL}/v1/db/data/noco/{NOCODB_WORKSPACE_ID}/{NOCODB_BASE_ID}/students"

response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    st.write("✅ Raw API Response:")
    st.json(data)  # This shows the exact structure

    if 'list' in data:
        students = pd.DataFrame(data['list'])
        st.write("✅ Students Table Preview:")
        st.dataframe(students)

        if 'full_name' in students.columns:
            st.success("✅ full_name column exists!")
            st.write(students['full_name'])
        else:
            st.warning("⚠️ full_name column not found. Available columns:")
            st.write(students.columns.tolist())
    else:
        st.warning("⚠️ 'list' key not found in response. Check API path or base_id.")
else:
    st.error(f"❌ API Request failed with status code {response.status_code}")
    st.error(response.text)
