import pandas as pd
import numpy as np
import pickle
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

def main():
    print("⏳ Loading processed data...")
    # 1. Load your clean data (We need the dataframe you used in vectorize_data.py)
    # Since you haven't shared how you load 'train', 'val', 'test', we will recreate
    # the vectorizer and model on the FULL dataset for the best possible demo.
    
    # Path to your data (Adjust if your CSV is named differently)
    # Using the same path logic as your vectorize_data.py
    try:
        df = pd.read_csv('data/raw/post_ids.csv') # Just checking if we have IDs
        # Ideally, we load the text. Let's assume you have a 'processed.csv' or similar.
        # If not, we will rely on features_tfidf.pkl which you confirmed you HAVE.
    except:
        pass

    # --- THE SHORTCUT ---
    # Since you already ran vectorize_data.py, you have 'data/processed/features_tfidf.pkl'
    # This file contains X (features) and y (labels). We can just load it and train!
    
    features_path = 'data/processed/features_tfidf.pkl'
    if not os.path.exists(features_path):
        print(f"❌ Error: {features_path} not found. Run 'src/vectorize_data.py' first.")
        return

    print(f"📂 Loading features from {features_path}...")
    with open(features_path, 'rb') as f:
        data = pickle.load(f)
    
    X = data['X']
    y = data['y']
    
    # 2. Train the Model (Your exact parameters)
    print("🧠 Training Logistic Regression...")
    model = LogisticRegression(
        max_iter=1000,
        class_weight='balanced',
        random_state=42
    )
    model.fit(X, y)
    print("✅ Model trained successfully.")

    # 3. Save the Model (Crucial Step for App)
    output_dir = 'models'
    os.makedirs(output_dir, exist_ok=True)
    
    model_path = os.path.join(output_dir, 'lr_model.pkl')
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    
    print(f"💾 Saved model to: {model_path}")
    print("---")
    print("👉 Now you can run 'streamlit run src/app/app.py'")

if __name__ == "__main__":
    main()
