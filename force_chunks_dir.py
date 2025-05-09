#!/usr/bin/env python
"""
Script to force the chunks directory setting in the config.
"""

from pathlib import Path
import json
import os
import sys

def force_chunks_dir():
    """Force the chunks directory setting in the config."""
    # Get default config path
    config_path = str(Path.home() / ".aiembedder" / "config.json")
    print(f"Updating config at: {config_path}")
    
    # Set custom chunks directory path
    custom_dir = "D:\\_APP\\AIEmbedder\\output\\custom_chunks"
    print(f"Setting chunks directory to: {custom_dir}")
    
    # Create the directory if it doesn't exist
    os.makedirs(custom_dir, exist_ok=True)
    print(f"Created directory: {custom_dir}")
    
    try:
        # Load existing config
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
        else:
            config = {}
            
        # Ensure processing section exists
        if "processing" not in config:
            config["processing"] = {}
            
        # Set chunks_directory directly
        config["processing"]["chunks_directory"] = custom_dir
        
        # Save back to config file
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
            
        print("Successfully updated config file.")
        print("\nUpdated config:")
        with open(config_path, 'r') as f:
            print(json.dumps(json.load(f), indent=4))
    
    except Exception as e:
        print(f"Error updating config: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(force_chunks_dir()) 