"""
PDF document processor for AIEmbedder.
"""

from typing import Optional

from PyPDF2 import PdfReader

from aiembedder.processors.base_processor import BaseProcessor
from aiembedder.utils.errors import ProcessingError
from aiembedder.utils.logging import Logger

class PDFProcessor(BaseProcessor):
    """Processor for PDF documents."""
    
    def __init__(self, logger: Optional[Logger] = None):
        """Initialize PDF processor.
        
        Args:
            logger: Logger instance
        """
        super().__init__(logger)
        self.logger.info("Initialized PDF processor")
    
    def process(self, file_path: str) -> str:
        """Process PDF document and return text content.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Extracted text content
            
        Raises:
            FileAccessError: If file cannot be accessed
            ProcessingError: If processing fails
        """
        try:
            self.validate_file(file_path)
            self.logger.info(f"Processing PDF file: {file_path}")
            
            # Open PDF file
            with open(file_path, 'rb') as file:
                # Create PDF reader
                reader = PdfReader(file)
                
                # Extract text from each page
                pages = []
                for page in reader.pages:
                    text = page.extract_text()
                    if text.strip():
                        pages.append(text.strip())
                
                # Join pages with newlines
                text = '\n'.join(pages)
            
            if not text:
                raise ProcessingError("No text content extracted", "PROC_001")
            
            self.logger.info(f"Successfully processed PDF file: {file_path}")
            return text
            
        except ProcessingError:
            raise
        except Exception as e:
            self.log_error(e, file_path)
            raise ProcessingError(f"Failed to process PDF file: {str(e)}", "PROC_001") 