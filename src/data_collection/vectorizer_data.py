import pandas as pd
import numpy as np
import re
import pickle
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
import os # Import the os module for directory operations

# Ensure NLTK resources are available
nltk.download('stopwords')

def preprocess_text(text):
    """
    Implements the cleaning logic from your README:
    - Lowercasing
    - URL removal
    - Preserving negations (clinical priority)
    """
    if not isinstance(text, str):
        return ""

    # 1. Lowercasing
    text = text.lower()

    # 2. URL Removal
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)

    # 3. User Mention/Reddit Cleanup (Basic)
    text = re.sub(r'u/\S+', 'USER', text)
    text = re.sub(r'r/\S+', 'SUBREDDIT', text)

    # 4. Remove special characters/numbers (keep words only)
    text = re.sub(r'[^a-zA-Z\s]', '', text)

    # 5. Stopword Handling with Negation Preservation
    # Standard English stopwords
    stop_words = set(stopwords.words('english'))
    # List of negations to KEEP (Critical for SI detection: "I do NOT want to live")
    negations = {'no', 'not', 'nor', 'neither', 'never', "don't", "won't", "can't", "cannot"}

    # Final stopword list = Standard - Negations
    final_stop_words = stop_words - negations

    words = text.split()
    filtered_words = [w for w in words if w not in final_stop_words]

    return " ".join(filtered_words)

def main():
    print("⏳ Loading Dataset...")
    # REPLACE THIS with the path to your actual raw CSV
    # Your dataset likely has columns like 'title' and 'body' or 'combined_text'
    df = pd.read_csv('/content/SID_DATA_WITH_SPLITS.csv')

    # Basic check: Ensure we have the text column
    # If your column is named 'text' or 'selftext', change 'combined_text' below
    if 'combined_text' not in df.columns:
        print("⚠️ 'combined_text' column not found. Creating it from Title + Body...")
        df['combined_text'] = df['title'].fillna('') + " " + df['body'].fillna('')

    print("🧹 Preprocessing Text (Preserving Negations)...")
    df['clean_text'] = df['combined_text'].apply(preprocess_text)

    # Create directories if they don't exist
    os.makedirs('data/raw', exist_ok=True)
    os.makedirs('data/processed', exist_ok=True)
    os.makedirs('models', exist_ok=True)

    # --- 1. Generate post_ids.csv (Safe to Share) ---
    print("📝 Generating ID List...")
    # Assuming you have an 'id' or 'post_id' column. If not, create a dummy index.
    if 'id' in df.columns:
        id_df = df[['id', 'prelim_label']]
    else:
        id_df = df[['prelim_label']].reset_index() # Use row index if no ID
        id_df.rename(columns={'index': 'id'}, inplace=True)

    id_df.to_csv('data/raw/post_ids.csv', index=False)
    print("✅ Saved 'data/raw/post_ids.csv'")

    # --- 2. TF-IDF Vectorization ---
    print("🧮 Vectorizing Data (TF-IDF)...")
    # Config from your report: 5000 features, unigrams + bigrams
    vectorizer = TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 2),
        sublinear_tf=True  # Usually improves performance on text
    )

    X = vectorizer.fit_transform(df['clean_text'])
    y = df['prelim_label'].values

    # --- 3. Save Features (Safe to Share) ---
    print("💾 Saving Vectorized Features...")
    output_path = 'data/processed/features_tfidf.pkl'

    with open(output_path, 'wb') as f:
        pickle.dump({
            'X': X,
            'y': y,
            'feature_names': vectorizer.get_feature_names_out(),
            'vocab': vectorizer.vocabulary_
        }, f)

    # Also save the vectorizer itself so you can use it on NEW data (demo)
    with open('models/tfidf_vectorizer.pkl', 'wb') as f:
        pickle.dump(vectorizer, f)

    print(f"✅ Saved features to '{output_path}'")
    print(f"   Matrix Shape: {X.shape}")
    print("🎉 Done! You can now safely upload 'post_ids.csv' and 'features_tfidf.pkl'.")

if __name__ == "__main__":
    main()
