import streamlit as st
import requests
import pandas as pd

# Load NocoDB secrets
base_url = st.secrets["NOCODB_BASE_URL"]
api_token = st.secrets["NOCODB_API_TOKEN"]
workspace_id = st.secrets["NOCODB_WORKSPACE_ID"]
base_id = st.secrets["NOCODB_BASE_ID"]

headers = {"xc-token": api_token}

# Fetch students from NocoDB
url = f"{base_url}/v1/db/data/noco/{workspace_id}/{base_id}/students"

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
            st.warning("⚠️ full_name column not found. Here are the available columns:")
            st.write(students.columns.tolist())
    else:
        st.warning("⚠️ 'list' key not found in response. Check API path or base_id.")
else:
    st.error(f"❌ API Request failed with status code {response.status_code}")
    st.error(response.text)
