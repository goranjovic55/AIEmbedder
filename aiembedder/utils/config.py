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
                "dedup_threshold": 0.95,
                "use_gpu": True
            },
            "database": {
                "collection_name": "localdocs_collection",
                "persist_directory": "output/vector_db",
                "embedding_model": "all-MiniLM-L6-v2"
            },
            "gui": {
                "window_title": "AIEmbedder",
                "window_size": "800x600",
                "theme": "default",
                "log_level": "INFO"
            }
        }
    
    def load(self) -> None:
        """Load configuration from file."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    loaded_config = json.load(f)
                    self.config.update(loaded_config)
        except Exception as e:
            print(f"Error loading configuration: {e}")
    
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
        return self.config.get(section, {}).get(key, default)
    
    def set(self, section: str, key: str, value: Any) -> None:
        """Set configuration value.
        
        Args:
            section: Configuration section
            key: Configuration key
            value: Configuration value
        """
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        self.save()
    
    def update(self, config: Dict[str, Any]) -> None:
        """Update configuration with new values.
        
        Args:
            config: New configuration values
        """
        self.config.update(config)
        self.save() 