#!/usr/bin/env python
"""
Debug script to check and fix configuration values.
"""

from pathlib import Path
import json
import os

def check_and_fix_config():
    """Check and fix configuration values."""
    # Get default config path
    config_path = str(Path.home() / ".aiembedder" / "config.json")
    print(f"Checking config at: {config_path}")
    
    # Check if config file exists
    if not os.path.exists(config_path):
        print(f"Config file does not exist at {config_path}")
        return
    
    # Read config
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            print("\nCurrent configuration:")
            print(json.dumps(config, indent=4))
            
        # Check for flat keys (legacy format)
        flat_keys = [k for k in config.keys() if "." in k]
        if flat_keys:
            print(f"\nFound legacy flat keys: {flat_keys}")
            print("Fixing configuration format...")
            
            # Move flat keys to their proper sections
            for key in flat_keys:
                if "." in key:
                    section, subkey = key.split(".", 1)
                    if section not in config:
                        config[section] = {}
                    config[section][subkey] = config[key]
                    # Remove the flat key
                    del config[key]
        
        # Ensure processing section exists
        if "processing" not in config:
            config["processing"] = {}
            
        # Ensure chunks_directory is properly set
        if "chunks_directory" not in config["processing"]:
            config["processing"]["chunks_directory"] = "~/.aiembedder/chunks"
            print("Added missing chunks_directory setting")
            
        # Fix invalid cleaning level
        if "cleaning_level" not in config["processing"] or not config["processing"]["cleaning_level"]:
            config["processing"]["cleaning_level"] = "medium"
            print("Fixed invalid cleaning level")
            
        # Save the updated config
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
            print("\nUpdated configuration saved to disk.")
            
        # Display the final config
        print("\nFinal configuration:")
        print(json.dumps(config, indent=4))
        
        # Check chunks directory
        chunks_dir = config.get("processing", {}).get("chunks_directory", "Not set")
        print(f"\nChunks directory from config: {chunks_dir}")
        
        # Resolve path
        if chunks_dir.startswith("~/"):
            resolved_path = Path.home() / chunks_dir[2:]
        else:
            resolved_path = Path(chunks_dir)
        
        resolved_path = resolved_path.expanduser().resolve()
        print(f"Resolved path: {resolved_path}")
        
        # Create directory if it doesn't exist
        if not resolved_path.exists():
            print(f"Creating directory: {resolved_path}")
            resolved_path.mkdir(parents=True, exist_ok=True)
        
        print(f"Path exists: {resolved_path.exists()}")
            
    except Exception as e:
        print(f"Error processing config: {e}")

if __name__ == "__main__":
    check_and_fix_config() 