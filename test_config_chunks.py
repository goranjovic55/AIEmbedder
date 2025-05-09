#!/usr/bin/env python
"""
Test script to verify chunks directory configuration.
"""

from pathlib import Path
import os
from aiembedder.utils.config import Config

def test_chunks_directory():
    """Test setting a custom chunks directory."""
    # Create config instance
    config = Config()
    
    # Print current chunks directory
    current_chunks_dir = config.get("processing", "chunks_directory", "~/.aiembedder/chunks")
    print(f"Current chunks directory: {current_chunks_dir}")
    
    # Set a custom chunks directory (using Windows path)
    custom_dir = "D:\\_APP\\AIEmbedder\\output\\custom_chunks"
    config.set("processing", "chunks_directory", custom_dir)
    print(f"Set custom chunks directory: {custom_dir}")
    
    # Verify it was set correctly
    new_chunks_dir = config.get("processing", "chunks_directory", "~/.aiembedder/chunks")
    print(f"Chunks directory after setting: {new_chunks_dir}")
    
    # Create the directory if it doesn't exist
    os.makedirs(custom_dir, exist_ok=True)
    print(f"Created directory: {custom_dir}")
    
    # Verify the path resolution works correctly
    if new_chunks_dir.startswith("~/"):
        resolved_path = Path.home() / new_chunks_dir[2:]
    else:
        resolved_path = Path(new_chunks_dir)
    
    resolved_path = resolved_path.expanduser().resolve()
    print(f"Resolved path: {resolved_path}")
    print(f"Path exists: {resolved_path.exists()}")
    
    # Make sure the resolved path is not the default home directory path
    default_path = Path.home() / ".aiembedder" / "chunks"
    print(f"Default path: {default_path}")
    print(f"Is using default path? {resolved_path == default_path}")
    
    # Read config file directly to verify
    print("\nDirect config file check:")
    config_path = str(Path.home() / ".aiembedder" / "config.json")
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            print(f.read())

if __name__ == "__main__":
    test_chunks_directory() 