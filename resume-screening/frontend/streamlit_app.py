import streamlit as st
import requests
import re
from PyPDF2 import PdfReader

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(
    page_title="Resume Screening App",
    page_icon="📄",
    layout="centered"
)
# Set background image using CSS
st.markdown(
    """
    <style>
    .stApp {
        background-image: url("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcToXZ8nFvzCgge15rpA9a5Pn9eotsK8XUyOlg&s");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("📄 Resume Screening System")
st.write("Upload your resume (PDF) and see resume details before prediction.")

BACKEND_URL = "http://127.0.0.1:8000/predict-pdf"

# -----------------------------
# Helper functions
# -----------------------------
def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        if page.extract_text():
            text += page.extract_text()
    return text


def extract_email(text):
    text = text.replace("\n", " ")  # remove line breaks
    match = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    return match[0] if match else "Not found"

def extract_phone(text):
    match = re.findall(r"\b\d{10}\b", text)
    return match[0] if match else "Not found"


def extract_name(text):
    lines = text.split("\n")
    for line in lines:
        line = line.strip()
        if line and "resume" not in line.lower():
            return line[:40]  # return first 40 chars as name
    return "Not found"



def extract_skills(text):
    skills_db = [
        "python", "java", "c++", "sql", "machine learning",
        "deep learning", "data science", "html", "css",
        "javascript", "react", "fastapi", "django"
    ]
    text = text.lower()
    found = [skill for skill in skills_db if skill in text]
    return found if found else ["Not detected"]

# -----------------------------
# File upload
# -----------------------------
uploaded_file = st.file_uploader("Upload Resume PDF", type=["pdf"])

if uploaded_file:
    st.success("PDF uploaded successfully")

    resume_text = extract_text_from_pdf(uploaded_file)

    if resume_text.strip() == "":
        st.error("No text found in PDF")
    else:
        # -----------------------------
        # Resume Details Section
        # -----------------------------
        st.subheader("📋 Resume Details")

        col1, col2 = st.columns(2)
        with col1:
            st.write("**Name:**", extract_name(resume_text))
            st.write("**Email:**", extract_email(resume_text))
            st.write("**Phone:**", extract_phone(resume_text))

        with col2:
            st.write("**Pages:**", len(PdfReader(uploaded_file).pages))
            st.write("**Word Count:**", len(resume_text.split()))

        st.write("**Skills Found:**")
        st.write(", ".join(extract_skills(resume_text)))

        # -----------------------------
        # Resume Preview
        # -----------------------------
        st.subheader("📝 Resume Preview")
        st.text_area("Extracted Text", resume_text[:2000], height=250)

        # -----------------------------
        # Prediction Button
        # -----------------------------
        if st.button("Predict Category"):
            with st.spinner("Analyzing resume..."):
                files = {
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        "application/pdf"
                    )
                }
                response = requests.post(BACKEND_URL, files=files)

            if response.status_code == 200:
                result = response.json()
                st.success("Prediction Complete 🎯")

                st.subheader("🎯 Predicted Category")
                st.write(result["prediction"][0])
            else:
                st.error("Backend API error")
