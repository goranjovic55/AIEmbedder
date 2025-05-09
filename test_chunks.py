#!/usr/bin/env python
"""
Test script to verify that chunks are created correctly in subdirectories.
"""

import os
import sys
from pathlib import Path
import re
import shutil
from datetime import datetime

def create_test_chunks():
    # Create a test directory
    chunks_dir = Path("./test_chunks_output")
    print(f"Using chunks directory: {chunks_dir}")
    
    # Ensure main chunks directory exists
    if chunks_dir.exists():
        print(f"Removing existing chunks directory: {chunks_dir}")
        shutil.rmtree(chunks_dir)
    
    print(f"Creating chunks directory: {chunks_dir}")
    chunks_dir.mkdir(parents=True, exist_ok=True)
    
    # Create test files/chunks
    test_files = [
        Path("example1.txt"), 
        Path("subdir/example2.txt"),
        Path("_TEST/example3.txt")
    ]
    
    for file_path in test_files:
        # Create a unique folder name for this file
        file_name = file_path.stem
        parent_dir = file_path.parent.name
        
        # Create a folder name with parent directory to avoid conflicts
        if parent_dir and parent_dir != ".":
            folder_name = f"{parent_dir}_{file_name}"
        else:
            folder_name = file_name
        
        # Windows-safe folder name
        folder_name = re.sub(r'[\\/*?:"<>|]', "_", folder_name)
        
        # Create chunk directory for this file
        chunk_dir = chunks_dir / folder_name
        print(f"Creating chunk subfolder: {chunk_dir}")
        chunk_dir.mkdir(parents=True, exist_ok=True)
        
        # Create sample chunks
        chunks = [f"This is chunk {i} from {file_path}" for i in range(3)]
        
        # Save each chunk as a separate file
        for i, chunk_text in enumerate(chunks):
            chunk_file = chunk_dir / f"chunk_{i:04d}.txt"
            print(f"  Saving chunk {i+1}/{len(chunks)} to {chunk_file}")
            
            with open(chunk_file, "w", encoding="utf-8") as f:
                # Add metadata as comments
                f.write(f"# Source: {file_path}\n")
                f.write(f"# Chunk: {i+1} of {len(chunks)}\n")
                f.write(f"# Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("\n")
                f.write(chunk_text)
    
    # Verify the results
    print("\nVerification:")
    for dir_path in chunks_dir.iterdir():
        if dir_path.is_dir():
            chunks = list(dir_path.glob("*.txt"))
            print(f"{dir_path.name}: {len(chunks)} chunks")
            for chunk in chunks:
                print(f"  - {chunk.name}")

if __name__ == "__main__":
    print("Starting chunk directory test...")
    create_test_chunks()
    print("Test completed successfully!") 