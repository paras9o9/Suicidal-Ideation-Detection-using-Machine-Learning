import streamlit as st
import pickle
import os
import re
import nltk
from nltk.corpus import stopwords
from lime.lime_text import LimeTextExplainer
import streamlit.components.v1 as components

# --- 1. Setup & Preprocessing (From your vectorize_data.py) ---
# We need to download stopwords for the live app
@st.cache_resource
def download_nltk_data():
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords')

download_nltk_data()

def preprocess_text(text):
    """
    Exact replica of your training preprocessing.
    Crucial for consistent predictions!
    """
    if not isinstance(text, str):
        return ""

    # 1. Lowercasing
    text = text.lower()

    # 2. URL Removal
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)

    # 3. User/Reddit Cleanup
    text = re.sub(r'u/\S+', 'USER', text)
    text = re.sub(r'r/\S+', 'SUBREDDIT', text)

    # 4. Remove special characters/numbers
    text = re.sub(r'[^a-zA-Z\s]', '', text)

    # 5. Stopword Handling with Negation Preservation
    stop_words = set(stopwords.words('english'))
    negations = {'no', 'not', 'nor', 'neither', 'never', "don't", "won't", "can't", "cannot"}
    final_stop_words = stop_words - negations

    words = text.split()
    filtered_words = [w for w in words if w not in final_stop_words]

    return " ".join(filtered_words)

# --- 2. Page Config ---
st.set_page_config(page_title="Suicidal Ideation Detector", page_icon="🧠", layout="centered")

st.markdown("""
<style>
.stTextArea textarea {font-size: 16px;}
.stButton button {width: 100%;}
</style>
""", unsafe_allow_html=True)

st.title("🧠 Mental Health Text Analysis")
st.caption("Research Model v1.0 • NLP with Negation Handling")

# --- 3. Load Assets ---
@st.cache_resource
def load_assets():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Paths based on your structure
    # NOTE: You named it 'tfidf_vectorizer.pkl' in your script, but 'lr_model.pkl' usually
    model_path = os.path.join(base_dir, 'Suicidal-Ideation-Detection-using-Machine-Learning/models', 'lr_model.pkl')
    
    vec_path = os.path.join(base_dir, 'Suicidal-Ideation-Detection-using-Machine-Learning/models', 'tfidf_vectorizer.pkl') 
    
    if not os.path.exists(model_path) or not os.path.exists(vec_path):
        return None, None
        
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    with open(vec_path, 'rb') as f:
        vectorizer = pickle.load(f)
    return model, vectorizer

model, vectorizer = load_assets()

if model is None:
    st.error("⚠️ System Error: Model files not found.")
    st.warning("Did you run `vectorize_data.py` and save the files to `models/`?")
    st.stop()

def explain_prediction(text, model, vectorizer):
    """
    Generates a LIME explanation for the given text.
    """
    # 1. Create a "Probe" function
    # LIME needs a function that takes raw text and outputs probabilities
    def predict_proba_func(texts):
        # Transform using your vectorizer
        vectors = vectorizer.transform(texts)
        # Get probabilities from your model
        return model.predict_proba(vectors)

    # 2. Initialize LIME Explainer
    explainer = LimeTextExplainer(class_names=model.classes_)

    # 3. Generate Explanation
    # num_features=6 means "Show me the top 6 most important words"
    exp = explainer.explain_instance(
        text, 
        predict_proba_func, 
        num_features=6, 
        top_labels=1
    )
    return exp

# --- 4. User Interface ---
st.subheader("Analyze Post")
user_input = st.text_area("Enter text:", height=150, placeholder="e.g., I feel trapped and see no way out...")

# Initialize session state to keep results visible
if 'analyzed' not in st.session_state:
    st.session_state.analyzed = False

if st.button("Analyze Risk", type="primary"):
    if user_input.strip():
        st.session_state.analyzed = True
    else:
        st.info("Please enter some text.")

# Only show results if analysis has happened
if st.session_state.analyzed and user_input:
    
    # A. Preprocess
    clean_text = preprocess_text(user_input)
    
    # B. Vectorize
    vec_text = vectorizer.transform([clean_text])
    
    # C. Predict
    probs = model.predict_proba(vec_text)[0]
    classes = model.classes_
    si_index = list(classes).index('SI')
    risk_score = probs[si_index]
    prediction = model.predict(vec_text)[0]

    # D. Display Results
    st.markdown("---")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.metric("Suicidal Risk Score", f"{risk_score:.1%}")
        st.caption(f"Predicted Category: **{prediction}**")
    
    with col2:
        if risk_score > 0.5:
            st.error("🚨 **High Risk Detected (SI)**")
            st.write("The model identified patterns consistent with Suicidal Ideation.")
        elif prediction == 'MH':
            st.warning("⚠️ **Mental Health Concern**")
            st.write("Detected signs of mental health distress, but not immediate SI.")
        elif prediction == 'HUMOR':
            st.info("🎭 **Dark Humor Detected**")
            st.write("Classified as sarcasm or dark humor.")
        else:
            st.success("✅ **Neutral / Low Risk**")
            st.write("Content appears safe.")

    # E. Explainability (Now sits at the same level, not nested)
    st.markdown("---")
    st.subheader("🔍 Why did the AI make this decision?")
    
    # This button now works because it's not hidden inside the first button's block
    if st.button("Generate Explanation (LIME)"):
        with st.spinner("Calculating word importance..."):
            exp = explain_prediction(user_input, model, vectorizer)
            st.write("The words highlighted below contributed most to the prediction:")
            components.html(exp.as_html(), height=400, scrolling=True)
            st.info("🟩 Green = Supports Prediction | 🟥 Red = Opposes Prediction")

    else:
        st.info("Please enter some text.")
