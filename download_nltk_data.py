#!/usr/bin/env python
"""
Script to download required NLTK data for AIEmbedder.
"""

import nltk
import os
from pathlib import Path

def download_nltk_data():
    """Download required NLTK data packages."""
    print("Downloading NLTK data packages...")
    
    # Create data directory
    user_nltk_dir = Path.home() / "nltk_data"
    if not user_nltk_dir.exists():
        user_nltk_dir.mkdir(parents=True, exist_ok=True)
        print(f"Created NLTK data directory: {user_nltk_dir}")
    
    # Download required data
    required_packages = [
        'punkt',            # For sentence tokenization
        'stopwords',        # For removing common words
        'wordnet',          # For lemmatization
        'averaged_perceptron_tagger'  # For POS tagging
    ]
    
    for package in required_packages:
        print(f"Downloading {package}...")
        try:
            nltk.download(package)
            print(f"Successfully downloaded {package}")
        except Exception as e:
            print(f"Error downloading {package}: {e}")
    
    # Verify downloads
    print("\nVerifying downloads:")
    verification_paths = {
        'punkt': 'tokenizers/punkt',
        'stopwords': 'corpora/stopwords',
        'wordnet': 'corpora/wordnet',
        'averaged_perceptron_tagger': 'taggers/averaged_perceptron_tagger'
    }
    
    for package, path in verification_paths.items():
        try:
            nltk.data.find(path)
            print(f"{package}: ✓")
        except LookupError:
            print(f"{package}: ✗ (Not found)")
    
    # Display NLTK data paths
    print("\nNLTK data paths:")
    for path in nltk.data.path:
        print(f"- {path}")

if __name__ == "__main__":
    download_nltk_data()
    print("\nDone downloading NLTK data.") 