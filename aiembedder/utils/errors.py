"""
Error handling for AIEmbedder.
"""

from typing import Dict, Optional

class AIEmbedderError(Exception):
    """Base exception for AIEmbedder."""
    
    def __init__(self, message: str, error_code: Optional[str] = None):
        """Initialize error.
        
        Args:
            message: Error message
            error_code: Error code
        """
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class FileAccessError(AIEmbedderError):
    """Error accessing files."""
    pass

class ProcessingError(AIEmbedderError):
    """Error during processing."""
    pass

class DatabaseError(AIEmbedderError):
    """Error with database operations."""
    pass

class ConfigurationError(AIEmbedderError):
    """Error with configuration."""
    pass

class ValidationError(AIEmbedderError):
    """Error with validation."""
    pass

ERROR_CODES: Dict[str, str] = {
    # File Access Errors
    "FILE_001": "File not found",
    "FILE_002": "Permission denied",
    "FILE_003": "Invalid file format",
    "FILE_004": "File is empty",
    
    # Processing Errors
    "PROC_001": "Text extraction failed",
    "PROC_002": "Text cleaning failed",
    "PROC_003": "Chunking failed",
    "PROC_004": "Deduplication failed",
    
    # Database Errors
    "DB_001": "Database connection failed",
    "DB_002": "Collection creation failed",
    "DB_003": "Vector storage failed",
    "DB_004": "Metadata storage failed",
    
    # Configuration Errors
    "CONF_001": "Invalid configuration",
    "CONF_002": "Missing required setting",
    "CONF_003": "Invalid setting value",
    
    # Validation Errors
    "VAL_001": "Invalid input",
    "VAL_002": "Missing required field",
    "VAL_003": "Invalid field value"
}

def get_error_message(error_code: str) -> str:
    """Get error message for error code.
    
    Args:
        error_code: Error code
        
    Returns:
        Error message
    """
    return ERROR_CODES.get(error_code, "Unknown error")

def raise_error(error_code: str, message: Optional[str] = None) -> None:
    """Raise error with code and message.
    
    Args:
        error_code: Error code
        message: Error message (optional)
    """
    error_message = message or get_error_message(error_code)
    
    if error_code.startswith("FILE"):
        raise FileAccessError(error_message, error_code)
    elif error_code.startswith("PROC"):
        raise ProcessingError(error_message, error_code)
    elif error_code.startswith("DB"):
        raise DatabaseError(error_message, error_code)
    elif error_code.startswith("CONF"):
        raise ConfigurationError(error_message, error_code)
    elif error_code.startswith("VAL"):
        raise ValidationError(error_message, error_code)
    else:
        raise AIEmbedderError(error_message, error_code) 