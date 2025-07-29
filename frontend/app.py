import streamlit as st
import requests,os

API_URL = "http://127.0.0.1:8000"

st.title("QuantaQuill - AI Scientific Paper Generator")

# Input fields
topic = st.text_input("Enter your research topic:")
methodology = st.text_area("Optional: Provide Methodology content", height=150)
experiments = st.text_area("Optional: Provide Experiments content", height=150)

if st.button("Generate Paper"):
    if not topic.strip():
        st.error("Please enter a research topic.")
    else:
        with st.spinner("Generating your paper... This may take a few minutes."):
            response = requests.post(f"{API_URL}/generate", json={
                "topic": topic,
                "methodology": methodology if methodology.strip() else None,
                "experiments": experiments if experiments.strip() else None
            })

            if response.status_code == 200:
                st.success("✅ Paper generated successfully!")
                file_path = os.path.join("C:\\", "study", "paper made tools", "quantaquill_clone", "backend", "output", "full_paper.pdf")
                st.download_button("Download PDF", data=open(file_path, "rb"),
                   file_name="full_paper.pdf", mime="application/pdf")
            else:
                st.error("Failed to generate paper. Check backend logs.")
