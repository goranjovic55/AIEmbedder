"""
HTML document processor for AIEmbedder.
"""

from typing import Optional
import os

from bs4 import BeautifulSoup

from aiembedder.processors.base_processor import BaseProcessor
from aiembedder.utils.errors import ProcessingError
from aiembedder.utils.logging import Logger

class HTMLProcessor(BaseProcessor):
    """Processor for HTML documents."""
    
    def __init__(self, logger: Optional[Logger] = None):
        """Initialize HTML processor.
        
        Args:
            logger: Logger instance
        """
        super().__init__(logger)
        self.logger.info("Initialized HTML processor")
    
    def process(self, file_path: str) -> str:
        """Process HTML document and return text content.
        
        Args:
            file_path: Path to HTML file
            
        Returns:
            Extracted text content
            
        Raises:
            ProcessingError: If processing fails
        """
        try:
            # Validate file
            if not os.path.isfile(file_path):
                raise ProcessingError(f"File not found: {file_path}")
            
            if not file_path.lower().endswith(('.html', '.htm')):
                self.logger.warning(f"File {file_path} may not be an HTML file")
            
            # Read HTML file
            with open(file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Parse HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(['script', 'style', 'header', 'footer', 'nav']):
                script.extract()
            
            # Extract text
            text = soup.get_text(separator=' ', strip=True)
            
            # Clean up whitespace
            lines = [line.strip() for line in text.splitlines()]
            chunks = [phrase.strip() for line in lines for phrase in line.split("  ")]
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            # Log success
            self.logger.info(f"Successfully processed HTML file: {file_path}")
            self.logger.info(f"Extracted {len(text)} characters")
            
            return text
            
        except ProcessingError as e:
            # Re-raise processing errors
            raise e
        except Exception as e:
            # Convert other exceptions to ProcessingError
            error_msg = f"Error processing HTML file {file_path}: {str(e)}"
            self.logger.error(error_msg)
            raise ProcessingError(error_msg) 