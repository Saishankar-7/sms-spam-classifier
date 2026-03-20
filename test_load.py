import pickle
import numpy as np
import scipy.sparse
import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
import string

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

# Load
with open('model.pkl', 'rb') as f:
    model = pickle.load(f)
with open('vectorizer.pkl', 'rb') as f:
    vectorizer = pickle.load(f)

def scale_length(length):
    # Based on notebook EDA: min=2, max=910
    min_len = 2
    max_len = 910
    return (length - min_len) / (max_len - min_len)

test_messages = [
    "Hey, are we still meeting for lunch today at 1pm?",
    "CONGRATULATIONS! You have a chance to win 1000 cash. Call 09058094455 now to claim your prize.",
    "Free entry in 2 a wkly comp to win FA Cup final tkt 21st May 2005. Text FA to 87121 to receive entry question(std txt rate)T&C's apply 08452810075over18's"
]

print(f"Model expects {model.n_features_in_} features.")

for msg in test_messages:
    clean_msg = msg.replace('\n', ' ').replace('\r', ' ')
    transformed = transform_text(clean_msg)
    vector = vectorizer.transform([transformed]).toarray()
    
    raw_len = len(clean_msg)
    scaled_len = scale_length(raw_len)
    
    final_features = np.hstack((vector, np.array([[scaled_len]])))
    
    pred = model.predict(final_features)
    res = "Spam" if pred[0] == 1 else "Ham"
    print(f"MSG: {clean_msg[:50]}...")
    print(f"LEN: {raw_len} -> SCALED: {scaled_len:.4f}")
    print(f"PRED: {res}")
    print("-" * 10)
