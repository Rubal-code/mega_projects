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

    # ---------------- TECH / ENGINEERING ----------------
    "python", "java", "c++", "c", "sql", "nosql", "mongodb",
    "machine learning", "deep learning", "data science",
    "nlp", "computer vision", "tensorflow", "pytorch",
    "html", "css", "javascript", "typescript",
    "react", "angular", "vue",
    "node.js", "express", "fastapi", "django", "flask",
    "spring", "spring boot",
    "git", "github", "docker", "kubernetes",
    "aws", "azure", "gcp",
    "linux", "unix", "rest api", "microservices",

    # ---------------- DATA / ANALYTICS ----------------
    "power bi", "tableau", "excel", "advanced excel",
    "data analysis", "data analytics", "statistics",
    "business intelligence", "etl", "data warehousing",
    "big data", "hadoop", "spark",

    # ---------------- MARKETING ----------------
    "digital marketing", "seo", "sem", "smm",
    "content marketing", "email marketing",
    "google analytics", "google ads", "facebook ads",
    "branding", "market research",
    "lead generation", "campaign management",
    "copywriting", "marketing strategy",

    # ---------------- SALES ----------------
    "sales", "inside sales", "b2b sales", "b2c sales",
    "crm", "salesforce", "hubspot",
    "cold calling", "negotiation",
    "account management", "pipeline management",
    "customer acquisition",

    # ---------------- FINANCE ----------------
    "financial analysis", "financial modeling",
    "accounting", "bookkeeping",
    "budgeting", "forecasting",
    "taxation", "gst", "income tax",
    "investment analysis", "equity research",
    "risk management", "corporate finance",
    "balance sheet", "profit and loss", "cash flow",
    "auditing",

    # ---------------- HR ----------------
    "human resources", "recruitment",
    "talent acquisition", "hr analytics",
    "payroll", "performance management",
    "employee engagement",
    "training and development",
    "onboarding", "labor law",

    # ---------------- OPERATIONS / MANAGEMENT ----------------
    "operations management", "supply chain",
    "logistics", "inventory management",
    "process improvement", "six sigma",
    "lean management", "project management",
    "agile", "scrum",
    "stakeholder management",

    # ---------------- DESIGN / CREATIVE ----------------
    "ui design", "ux design", "figma",
    "adobe photoshop", "illustrator",
    "indesign", "canva",
    "wireframing", "prototyping",

    # ---------------- SOFT SKILLS ----------------
    "communication", "presentation",
    "problem solving", "critical thinking",
    "leadership", "teamwork",
    "time management", "decision making",
    "adaptability", "creativity"
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
