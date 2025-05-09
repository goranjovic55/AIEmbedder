"""
Configuration management for AIEmbedder.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

class Config:
    """Configuration manager for AIEmbedder."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration manager.
        
        Args:
            config_path: Path to configuration file. If None, uses default location.
        """
        self.config_path = config_path or str(Path.home() / ".aiembedder" / "config.json")
        self.config: Dict[str, Any] = self._load_default_config()
        self._ensure_config_dir()
        self.load()
    
    def _ensure_config_dir(self) -> None:
        """Ensure configuration directory exists."""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration.
        
        Returns:
            Dict containing default configuration values.
        """
        return {
            "processing": {
                "cleaning_level": "medium",
                "chunk_size": 400,
                "chunk_overlap": 50,
                "remove_stopwords": False,
                "similarity_threshold": 0.95,
                "use_gpu": True,
                "chunks_directory": str(Path.home() / ".aiembedder" / "chunks"),
                "optimize_for_gpt4all": True,
                "respect_document_structure": True,
                "chunk_flexibility_percent": 30
            },
            "database": {
                "collection_name": "localdocs_collection",
                "directory": str(Path.home() / ".aiembedder" / "db"),
                "embedding_model": "all-MiniLM-L6-v2",
                "search_limit": 5
            },
            "gui": {
                "window_title": "AIEmbedder",
                "window_size": "800x600",
                "theme": "default"
            },
            "logging": {
                "level": "INFO",
                "directory": str(Path.home() / ".aiembedder" / "logs")
            }
        }
    
    def load(self) -> None:
        """Load configuration from file."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    loaded_config = json.load(f)
                    
                    # Fix legacy flat keys (e.g., "processing.chunk_size")
                    flat_keys = [k for k in loaded_config.keys() if "." in k]
                    for key in flat_keys:
                        if "." in key:
                            section, subkey = key.split(".", 1)
                            if section not in loaded_config:
                                loaded_config[section] = {}
                            loaded_config[section][subkey] = loaded_config[key]
                            # Remove the flat key
                            del loaded_config[key]
                    
                    # Rename legacy keys for compatibility
                    self._rename_legacy_keys(loaded_config)
                    
                    # Update the config with fixed format
                    self.config.update(loaded_config)
                    
                    # Ensure critical values exist after loading
                    # This handles cases where config file might be missing newer settings
                    if "processing" not in self.config:
                        self.config["processing"] = {}
                    
                    # Ensure chunks directory is set with valid path
                    if "chunks_directory" not in self.config["processing"] or not self._is_valid_path(self.config["processing"]["chunks_directory"]):
                        self.config["processing"]["chunks_directory"] = str(Path.home() / ".aiembedder" / "chunks")
                        self.save()  # Save to ensure it's written to file
                        
                    # Ensure cleaning level has a valid value
                    if "cleaning_level" not in self.config["processing"] or not self.config["processing"]["cleaning_level"]:
                        self.config["processing"]["cleaning_level"] = "medium"
                        self.save()
        except Exception as e:
            print(f"Error loading configuration: {e}")
            # If config is corrupt, restore defaults
            self.config = self._load_default_config()
            self.save()
    
    def _rename_legacy_keys(self, config: Dict[str, Any]) -> None:
        """Rename legacy keys for compatibility.
        
        Args:
            config: Config dictionary to update
        """
        # Database section renames
        if "database" in config:
            if "persist_directory" in config["database"]:
                config["database"]["directory"] = config["database"].pop("persist_directory")
                
        # Processing section renames
        if "processing" in config:
            if "dedup_threshold" in config["processing"]:
                config["processing"]["similarity_threshold"] = config["processing"].pop("dedup_threshold")
                
        # GUI section renames - move logging to its own section
        if "gui" in config:
            if "log_level" in config["gui"]:
                if "logging" not in config:
                    config["logging"] = {}
                config["logging"]["level"] = config["gui"].pop("log_level")
                
            if "log_directory" in config["gui"]:
                if "logging" not in config:
                    config["logging"] = {}
                config["logging"]["directory"] = config["gui"].pop("log_directory")
    
    def _is_valid_path(self, path_str: str) -> bool:
        """Check if a path string is valid.
        
        Args:
            path_str: The path string to check
            
        Returns:
            True if path is valid, False otherwise
        """
        if not path_str or not isinstance(path_str, str):
            return False
            
        # Check for obvious error patterns in path
        if path_str.startswith("Traceback") or "Error" in path_str:
            return False
            
        # Try to construct a path object
        try:
            path = Path(path_str.replace("~", str(Path.home())))
            # Check if parent directory exists or is a home directory
            return path.parent.exists() or "~" in path_str or ".aiembedder" in path_str
        except Exception:
            return False
    
    def save(self) -> None:
        """Save configuration to file."""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Error saving configuration: {e}")
    
    def get(self, section: str, key: str, default: Any = None) -> Any:
        """Get configuration value.
        
        Args:
            section: Configuration section
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        value = self.config.get(section, {}).get(key, default)
        
        # If value looks like a path and it's invalid, return default
        if key.endswith('_directory') and isinstance(value, str) and not self._is_valid_path(value):
            return default
            
        return value
    
    def set(self, section: str, key: str, value: Any) -> None:
        """Set configuration value.
        
        Args:
            section: Configuration section
            key: Configuration key
            value: Configuration value
        """
        if section not in self.config:
            self.config[section] = {}
            
        # Check if we're setting a directory path and it looks invalid
        if key.endswith('_directory') and isinstance(value, str) and not self._is_valid_path(value):
            # Use default path instead
            if key == "chunks_directory":
                value = str(Path.home() / ".aiembedder" / "chunks")
            elif key == "directory" and section == "database":
                value = str(Path.home() / ".aiembedder" / "db")
            elif key == "directory" and section == "logging":
                value = str(Path.home() / ".aiembedder" / "logs")
                
        self.config[section][key] = value
        self.save()
    
    def update(self, config: Dict[str, Any]) -> None:
        """Update configuration with new values.
        
        Args:
            config: New configuration values
        """
        self.config.update(config)
        self.save() 