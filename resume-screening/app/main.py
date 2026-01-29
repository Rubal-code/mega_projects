from fastapi import FastAPI
import pickle
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.metrics.pairwise import cosine_similarity
import os

app=FastAPI()

# load models
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

model = pickle.load(open(os.path.join(BASE_DIR, "model", "resume_model.pkl"), "rb"))
tfidf = pickle.load(open(os.path.join(BASE_DIR, "model", "tfidf.pkl"), "rb"))

# Text cleaning function (SAME as training)
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words("english"))

def clean_text(text):
    text = re.sub(r"http\S+", " ", text)
    text = re.sub(r"[^a-zA-Z]", " ", text)
    text = text.lower()
    words = text.split()
    words = [lemmatizer.lemmatize(w) for w in words if w not in stop_words]
    return " ".join(words)

@app.get("/")
def home():
    return {"message": "Resume Analyzer API is running"}