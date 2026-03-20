from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pickle
import numpy as np
from scipy.sparse import hstack
import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
import string
import os
import uvicorn

# Ensure NLTK resources
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

ps = PorterStemmer()

def transform_text(text):
    text = text.lower()
    text = nltk.word_tokenize(text)
    y = []
    for i in text:
        if i.isalnum():
            y.append(i)
    text = y[:]
    y = []
    for i in text:
        if i not in stopwords.words('english') and i not in string.punctuation:
            y.append(i)
    text = y[:]
    y = []
    for i in text:
        y.append(ps.stem(i))
    return " ".join(y)

def scale_len(length):
    # Based on notebook statistics: min=2, max=910
    return (length - 2) / (910 - 2)

app = FastAPI(title="SMS Spam Classifier")

# Setup templates and static files directories
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Load models on startup
try:
    with open('model.pkl', 'rb') as f:
        model = pickle.load(f)
    with open('vectorizer.pkl', 'rb') as f:
        vectorizer = pickle.load(f)
except Exception as e:
    print(f"Error loading models: {e}")
    model = None
    vectorizer = None

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/predict")
async def predict(text: str = Form(...)):
    if model is None or vectorizer is None:
        return {"error": "Model not loaded properly"}
    
    try:
        # Preprocess text
        transformed = transform_text(text)
        
        # Vectorize
        features = vectorizer.transform([transformed]).toarray()
        
        # Scale length
        raw_len = len(text)
        scaled_len = scale_len(raw_len)
        
        # Combine features (3001 total)
        combined_features = np.hstack((features, np.array([[scaled_len]])))
        
        # Predict (0 is Ham, 1 is Spam)
        pred = model.predict(combined_features)
        result = "Spam" if pred[0] == 1 else "Ham"
        
        return {"result": result, "text": text}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
