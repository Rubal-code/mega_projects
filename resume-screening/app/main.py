from fastapi import FastAPI, UploadFile, File
import joblib
import re
import nltk
import os
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from PyPDF2 import PdfReader

# ---------------------------
# FastAPI app
# ---------------------------
app = FastAPI(title="Resume Screening API")

# ---------------------------
# Paths
# ---------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))   # app/
MODEL_DIR = os.path.join(BASE_DIR, "..", "model")       # ../model/

model_path = os.path.join(MODEL_DIR, "resume_model.pkl")
tfidf_path = os.path.join(MODEL_DIR, "tfidf.pkl")

# ---------------------------
# Load model & vectorizer
# ---------------------------
model = joblib.load(model_path)
tfidf = joblib.load(tfidf_path)

# ---------------------------
# NLTK setup (download once)
# ---------------------------
nltk.download("stopwords")
nltk.download("wordnet")

lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words("english"))

# ---------------------------
# Text cleaning
# ---------------------------
def clean_text(text: str) -> str:
    text = re.sub(r"http\S+", " ", text)
    text = re.sub(r"[^a-zA-Z]", " ", text)
    text = text.lower()
    words = text.split()
    words = [lemmatizer.lemmatize(w) for w in words if w not in stop_words]
    return " ".join(words)

# ---------------------------
# PDF text extractor
# ---------------------------
def extract_text_from_pdf(file: UploadFile) -> str:
    reader = PdfReader(file.file)
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted
    return text

# ---------------------------
# Routes
# ---------------------------
@app.get("/")
def home():
    return {"message": "Resume Analyzer API is running"}

@app.post("/predict-text")
def predict_text(text: str):
    clean = clean_text(text)
    vector = tfidf.transform([clean])
    prediction = model.predict(vector)
    return {
        "prediction": prediction.tolist()
    }

@app.post("/predict-pdf")
def predict_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        return {"error": "Only PDF files are allowed"}

    raw_text = extract_text_from_pdf(file)
    clean = clean_text(raw_text)
    vector = tfidf.transform([clean])
    prediction = model.predict(vector)

    return {
        "filename": file.filename,
        "prediction": prediction.tolist()
    }
 