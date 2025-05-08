"""
Base document processor for AIEmbedder.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional
import os

from aiembedder.utils.errors import FileAccessError, ProcessingError
from aiembedder.utils.logging import Logger

class BaseProcessor(ABC):
    """Base class for document processors."""
    
    def __init__(self, logger: Optional[Logger] = None):
        """Initialize processor.
        
        Args:
            logger: Logger instance
        """
        self.logger = logger or Logger()
    
    @abstractmethod
    def process(self, file_path: str) -> str:
        """Process document and return text content.
        
        Args:
            file_path: Path to document file
            
        Returns:
            Extracted text content
            
        Raises:
            FileAccessError: If file cannot be accessed
            ProcessingError: If processing fails
        """
        pass
    
    def validate_file(self, file_path: str) -> None:
        """Validate file exists and is accessible.
        
        Args:
            file_path: Path to file
            
        Raises:
            FileAccessError: If file is invalid
        """
        path = Path(file_path)
        if not path.exists():
            raise FileAccessError(f"File not found: {file_path}", "FILE_001")
        if not path.is_file():
            raise FileAccessError(f"Not a file: {file_path}", "FILE_001")
        if not os.access(path, os.R_OK):
            raise FileAccessError(f"Permission denied: {file_path}", "FILE_002")
    
    def log_error(self, error: Exception, file_path: str) -> None:
        """Log processing error.
        
        Args:
            error: Error that occurred
            file_path: Path to file being processed
        """
        self.logger.error(f"Error processing {file_path}: {str(error)}") 