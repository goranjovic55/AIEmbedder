"""
Text document processor for AIEmbedder.
"""

from typing import Optional

from aiembedder.processors.base_processor import BaseProcessor
from aiembedder.utils.errors import ProcessingError
from aiembedder.utils.logging import Logger

class TextProcessor(BaseProcessor):
    """Processor for plain text documents."""
    
    def __init__(self, logger: Optional[Logger] = None):
        """Initialize text processor.
        
        Args:
            logger: Logger instance
        """
        super().__init__(logger)
        self.logger.info("Initialized text processor")
    
    def process(self, file_path: str) -> str:
        """Process text document and return content.
        
        Args:
            file_path: Path to text file
            
        Returns:
            File content
            
        Raises:
            FileAccessError: If file cannot be accessed
            ProcessingError: If processing fails
        """
        try:
            self.validate_file(file_path)
            self.logger.info(f"Processing text file: {file_path}")
            
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'cp1252']
            text = None
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as file:
                        text = file.read()
                    break
                except UnicodeDecodeError:
                    continue
            
            if text is None:
                raise ProcessingError("Failed to decode text file", "PROC_001")
            
            if not text.strip():
                raise ProcessingError("File is empty", "FILE_004")
            
            self.logger.info(f"Successfully processed text file: {file_path}")
            return text
            
        except ProcessingError:
            raise
        except Exception as e:
            self.log_error(e, file_path)
            raise ProcessingError(f"Failed to process text file: {str(e)}", "PROC_001") 