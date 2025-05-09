#!/usr/bin/env python
"""
Script to download NLTK resources required by AIEmbedder.
Run this script if you encounter NLTK resource-related errors.
"""

import os
import sys
import nltk
from pathlib import Path

def download_nltk_resources():
    """Download all required NLTK resources."""
    print("Downloading NLTK resources for AIEmbedder...")
    
    # Resources needed by AIEmbedder
    resources = [
        ('punkt', 'tokenizers/punkt'),  # For sentence tokenization
        ('stopwords', 'corpora/stopwords'),  # For stopword removal
        ('wordnet', 'corpora/wordnet')  # For lemmatization
    ]
    
    # Create nltk_data directory if it doesn't exist
    nltk_data_dir = Path.home() / "nltk_data"
    os.makedirs(nltk_data_dir, exist_ok=True)
    print(f"NLTK data directory: {nltk_data_dir}")
    
    # Download each resource and verify
    for resource_name, resource_path in resources:
        print(f"\nProcessing resource: {resource_name}")
        try:
            # Check if resource exists
            try:
                nltk.data.find(resource_path)
                print(f"✓ Resource '{resource_name}' already exists")
            except LookupError:
                print(f"Downloading '{resource_name}'...")
                nltk.download(resource_name)
                print(f"✓ Successfully downloaded '{resource_name}'")
            
            # Verify download
            try:
                nltk.data.find(resource_path)
                print(f"✓ Verified '{resource_name}' is available")
            except LookupError:
                print(f"⚠ Warning: '{resource_name}' not found after download")
                print(f"  Attempted to find: {resource_path}")
        except Exception as e:
            print(f"✗ Error downloading/verifying '{resource_name}': {str(e)}")
    
    print("\nNLTK Resources Installation Summary:")
    print("----------------------------------")
    
    all_ok = True
    for resource_name, resource_path in resources:
        try:
            nltk.data.find(resource_path)
            print(f"✓ {resource_name}: Successfully installed")
        except LookupError:
            print(f"✗ {resource_name}: Not installed")
            all_ok = False
    
    if all_ok:
        print("\n✓ All required NLTK resources have been installed successfully!")
    else:
        print("\n⚠ Some NLTK resources couldn't be installed automatically.")
        print("  Please try manually installing them with the following commands:")
        for resource_name, _ in resources:
            print(f"    python -m nltk.downloader {resource_name}")
    
    print("\nNLTK data paths:")
    for path in nltk.data.path:
        print(f"- {path}")

if __name__ == "__main__":
    try:
        download_nltk_resources()
    except Exception as e:
        print(f"Error downloading NLTK resources: {str(e)}")
        sys.exit(1)
    
    print("\nDone! You can now run AIEmbedder without NLTK resource errors.") 