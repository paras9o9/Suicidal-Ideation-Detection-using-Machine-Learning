import streamlit as st
import pickle
import os
import re
import nltk
from nltk.corpus import stopwords
from lime.lime_text import LimeTextExplainer
import streamlit.components.v1 as components

# --- 1. Page Config (Must be first) ---
st.set_page_config(
    page_title="Suicidal Ideation Detector",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 2. Custom Styling for Visible Text ---
st.markdown("""
<style>
/* Text area styling - visible white text on dark background */
[data-testid="stTextArea"] textarea {
    color: #E6EDF3 !important;
    background-color: #0E1117 !important;
    border: 1px solid #30363D !important;
    caret-color: #E6EDF3 !important;
    font-size: 16px;
}

/* Widget labels */
[data-testid="stWidgetLabel"] p {
    color: #E6EDF3 !important;
    font-weight: 500;
}

/* Buttons */
.stButton button {
    width: 100%;
    font-weight: 600;
}

/* Metrics */
[data-testid="stMetricValue"] {
    color: #58A6FF !important;
    font-size: 32px !important;
}

/* General text readability */
.stMarkdown, .stText {
    color: #E6EDF3;
}

/* Info boxes */
.stAlert {
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# --- 3. Setup & Preprocessing ---
@st.cache_resource
def download_nltk_data():
    """Download required NLTK data"""
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords')

download_nltk_data()

def preprocess_text(text):
    """
    Preprocessing pipeline matching training data.
    Essential for consistent predictions.
    """
    if not isinstance(text, str):
        return ""

    # Lowercasing
    text = text.lower()

    # URL removal
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)

    # Reddit-specific cleanup
    text = re.sub(r'u/\S+', 'USER', text)
    text = re.sub(r'r/\S+', 'SUBREDDIT', text)

    # Remove special characters/numbers
    text = re.sub(r'[^a-zA-Z\s]', '', text)

    # Stopword removal with negation preservation
    stop_words = set(stopwords.words('english'))
    negations = {'no', 'not', 'nor', 'neither', 'never', "don't", "won't", "can't", "cannot"}
    final_stop_words = stop_words - negations

    words = text.split()
    filtered_words = [w for w in words if w not in final_stop_words]

    return " ".join(filtered_words)

# --- 4. Load ML Assets ---
@st.cache_resource
def load_assets():
    """Load trained model and vectorizer"""
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Search for models directory
    possible_paths = [
        os.path.join(current_dir, 'models'),
        os.path.join(current_dir, '..', 'models'),
        os.path.join(current_dir, '..', '..', 'models'),
    ]

    models_dir = None
    for path in possible_paths:
        if os.path.isdir(path):
            models_dir = path
            break

    if models_dir is None:
        st.error(f"❌ Critical Error: Could not find 'models' directory.")
        st.info(f"Searched: {possible_paths}")
        return None, None

    model_path = os.path.join(models_dir, 'lr_model.pkl')
    vec_path = os.path.join(models_dir, 'tfidf_vectorizer.pkl')

    if not os.path.exists(model_path):
        st.error(f"❌ Model file missing: {model_path}")
        return None, None

    if not os.path.exists(vec_path):
        st.error(f"❌ Vectorizer file missing: {vec_path}")
        return None, None

    try:
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        with open(vec_path, 'rb') as f:
            vectorizer = pickle.load(f)
        return model, vectorizer
    except Exception as e:
        st.error(f"❌ Error loading models: {str(e)}")
        return None, None

model, vectorizer = load_assets()
if model is None or vectorizer is None:
    st.stop()

# --- 5. LIME Explainability Function ---
def explain_prediction(text, model, vectorizer):
    """Generate LIME explanation for model prediction"""
    def predict_proba_func(texts):
        vectors = vectorizer.transform(texts)
        return model.predict_proba(vectors)

    explainer = LimeTextExplainer(class_names=model.classes_)
    exp = explainer.explain_instance(
        text, 
        predict_proba_func, 
        num_features=6, 
        top_labels=1
    )
    return exp

# --- 6. UI Header ---
st.title("🧠 Mental Health Text Analysis")
st.caption("Research Model v1.0 • NLP with Negation Handling")
st.markdown("---")

# --- 7. Main Interface ---
st.subheader("Analyze Text for Risk Indicators")

user_input = st.text_area(
    "Enter text to analyze:",
    height=150,
    placeholder="e.g., I feel trapped and see no way out...",
    help="Paste social media posts, messages, or any text for mental health risk assessment"
)

# Session state for persistent results
if 'analyzed' not in st.session_state:
    st.session_state.analyzed = False
if 'last_input' not in st.session_state:
    st.session_state.last_input = ""

# Analyze button
col_btn1, col_btn2 = st.columns([3, 1])
with col_btn1:
    analyze_clicked = st.button("🔍 Analyze Risk", type="primary", use_container_width=True)
with col_btn2:
    if st.button("🔄 Clear", use_container_width=True):
        st.session_state.analyzed = False
        st.session_state.last_input = ""
        st.rerun()

if analyze_clicked:
    if user_input.strip():
        st.session_state.analyzed = True
        st.session_state.last_input = user_input
    else:
        st.warning("⚠️ Please enter some text to analyze.")

# --- 8. Results Display ---
if st.session_state.analyzed and st.session_state.last_input:

    text_to_analyze = st.session_state.last_input

    # Preprocess
    clean_text = preprocess_text(text_to_analyze)

    # Vectorize & Predict
    vec_text = vectorizer.transform([clean_text])
    probs = model.predict_proba(vec_text)[0]
    classes = model.classes_
    si_index = list(classes).index('SI')
    risk_score = probs[si_index]
    prediction = model.predict(vec_text)[0]

    # Results section
    st.markdown("---")
    st.subheader("📊 Analysis Results")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.metric("Suicidal Risk Score", f"{risk_score:.1%}")
        st.caption(f"Category: **{prediction}**")

    with col2:
        if risk_score > 0.5:
            st.error("🚨 **High Risk Detected (SI)**")
            st.write("The model identified patterns consistent with Suicidal Ideation.")
            st.write("**Action**: This requires immediate professional attention.")
        elif prediction == 'MH':
            st.warning("⚠️ **Mental Health Concern**")
            st.write("Detected signs of mental health distress, but not immediate SI.")
            st.write("**Recommendation**: Consider wellness check or counseling.")
        elif prediction == 'HUMOR':
            st.info("🎭 **Dark Humor Detected**")
            st.write("Classified as sarcasm or dark humor.")
            st.write("**Note**: Context matters - monitor if patterns persist.")
        else:
            st.success("✅ **Neutral / Low Risk**")
            st.write("Content appears safe with no significant risk indicators.")

    # Explainability section
    st.markdown("---")
    st.subheader("🔍 Model Explainability")

    with st.expander("ℹ️ What is LIME?", expanded=False):
        st.write("""
        **LIME** (Local Interpretable Model-agnostic Explanations) shows which words 
        influenced the AI's decision:
        - 🟩 **Green highlights**: Words supporting the predicted category
        - 🟥 **Red highlights**: Words opposing the prediction
        - Helps understand the "why" behind AI decisions
        """)

    if st.button("🎯 Generate Explanation (LIME)", use_container_width=True):
        with st.spinner("Calculating word importance..."):
            try:
                exp = explain_prediction(text_to_analyze, model, vectorizer)

                # Fix LIME HTML for better visibility
                lime_html = exp.as_html()
                lime_html = lime_html.replace(
                    "<head>",
                    "<head><style>body{background:#ffffff !important; color:#111111 !important; padding:15px;}</style>"
                )

                st.write("**Word Importance Visualization:**")
                components.html(lime_html, height=450, scrolling=True)

                st.success("✅ Explanation generated successfully!")
            except Exception as e:
                st.error(f"❌ Error generating explanation: {str(e)}")

# --- 9. Footer ---
st.markdown("---")
st.caption("""
⚠️ **Disclaimer**: This is a research tool. Not a substitute for professional mental health assessment. 
If you're in crisis, please contact emergency services or a crisis helpline immediately.
""")
