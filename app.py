# app.py
import streamlit as st
import requests

st.title(" MCP Server Client")

context = st.text_area("Context", height=200)
prompt = st.text_input("Prompt")

if st.button("Submit"):
    response = requests.post(
        "http://localhost:8000/mcp",
        json={"context": context, "prompt": prompt}
    )
    if response.status_code == 200:
        st.success("Response:")
        st.write(response.json()["result"])
    else:
        st.error("Error: " + response.text)
