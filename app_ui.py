"""
app_ui.py
Simple Streamlit frontend for the Resume Evaluator.
Uploads a resume, sends it to the FastAPI backend, displays the match result.
"""

import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/evaluate-resume"

st.set_page_config(page_title="Resume Evaluator", page_icon="📄")

st.title("📄 Resume Evaluator")
st.write("Upload a resume (PDF or DOCX) to see how well it matches the job requirements.")

uploaded_file = st.file_uploader("Choose a resume file", type=["pdf", "docx"])

if uploaded_file is not None:
    if st.button("Evaluate Resume"):
        with st.spinner("Analyzing resume..."):
            try:
                files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                response = requests.post(API_URL, files=files)

                if response.status_code == 200:
                    data = response.json()
                    match_result = data["match_result"]
                    resume_data = data["resume_data"]

                    st.success("Evaluation complete!")

                    # Match percentage as a headline metric
                    st.metric("Match Percentage", f"{match_result['match_percentage']}%")

                    col1, col2 = st.columns(2)

                    with col1:
                        st.subheader("✅ Matched Skills")
                        for skill in match_result["matched_skills"]:
                            st.write(f"- {skill}")

                    with col2:
                        st.subheader("❌ Missing Skills")
                        for skill in match_result["missing_skills"]:
                            st.write(f"- {skill}")

                    st.subheader("🧠 Reasoning")
                    st.write(match_result["reasoning"])

                    with st.expander("View extracted resume data"):
                        st.json(resume_data)

                else:
                    st.error(f"Error: {response.json().get('detail', 'Unknown error')}")

            except requests.exceptions.ConnectionError:
                st.error("Could not connect to the API. Make sure the FastAPI server is running on port 8000.")