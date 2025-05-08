"""
Logging configuration for AIEmbedder.
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

class Logger:
    """Logger for AIEmbedder."""
    
    def __init__(self, log_dir: Optional[str] = None):
        """Initialize logger.
        
        Args:
            log_dir: Directory for log files. If None, uses default location.
        """
        self.log_dir = log_dir or str(Path.home() / ".aiembedder" / "logs")
        self._ensure_log_dir()
        self._setup_logger()
    
    def _ensure_log_dir(self) -> None:
        """Ensure log directory exists."""
        os.makedirs(self.log_dir, exist_ok=True)
    
    def _setup_logger(self) -> None:
        """Set up logging configuration."""
        # Create logger
        self.logger = logging.getLogger("aiembedder")
        self.logger.setLevel(logging.DEBUG)
        
        # Create handlers
        console_handler = logging.StreamHandler()
        file_handler = logging.FileHandler(
            os.path.join(self.log_dir, f"aiembedder_{datetime.now().strftime('%Y%m%d')}.log")
        )
        
        # Create formatters
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Set formatters
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        
        # Add handlers
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
    
    def debug(self, message: str) -> None:
        """Log debug message.
        
        Args:
            message: Debug message
        """
        self.logger.debug(message)
    
    def info(self, message: str) -> None:
        """Log info message.
        
        Args:
            message: Info message
        """
        self.logger.info(message)
    
    def warning(self, message: str) -> None:
        """Log warning message.
        
        Args:
            message: Warning message
        """
        self.logger.warning(message)
    
    def error(self, message: str) -> None:
        """Log error message.
        
        Args:
            message: Error message
        """
        self.logger.error(message)
    
    def critical(self, message: str) -> None:
        """Log critical message.
        
        Args:
            message: Critical message
        """
        self.logger.critical(message)
    
    def set_level(self, level: str) -> None:
        """Set logging level.
        
        Args:
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        self.logger.setLevel(level_map.get(level.upper(), logging.INFO)) 