"""
Processor factory for AIEmbedder.
"""

from pathlib import Path
from typing import Dict, Optional, Type

from aiembedder.processors.base_processor import BaseProcessor
from aiembedder.processors.html_processor import HTMLProcessor
from aiembedder.processors.doc_processor import DocProcessor
from aiembedder.processors.pdf_processor import PDFProcessor
from aiembedder.processors.text_processor import TextProcessor
from aiembedder.utils.errors import ProcessingError
from aiembedder.utils.logging import Logger

class ProcessorFactory:
    """Factory for creating document processors."""
    
    # File extension to processor mapping
    PROCESSORS: Dict[str, Type[BaseProcessor]] = {
        '.html': HTMLProcessor,
        '.htm': HTMLProcessor,
        '.doc': DocProcessor,
        '.docx': DocProcessor,
        '.pdf': PDFProcessor,
        '.txt': TextProcessor,
        '.text': TextProcessor,
    }
    
    def __init__(self, logger: Optional[Logger] = None):
        """Initialize processor factory.
        
        Args:
            logger: Logger instance
        """
        self.logger = logger or Logger()
        self.logger.info("Initialized processor factory")
    
    def get_processor(self, file_path: str) -> BaseProcessor:
        """Get appropriate processor for file.
        
        Args:
            file_path: Path to document file
            
        Returns:
            Document processor instance
            
        Raises:
            ProcessingError: If no processor is available for file type
        """
        extension = Path(file_path).suffix.lower()
        
        if extension not in self.PROCESSORS:
            raise ProcessingError(
                f"No processor available for file type: {extension}",
                "PROC_001"
            )
        
        processor_class = self.PROCESSORS[extension]
        return processor_class(self.logger)
    
    def get_supported_extensions(self) -> list[str]:
        """Get list of supported file extensions.
        
        Returns:
            List of supported file extensions
        """
        return list(self.PROCESSORS.keys())
    
    def is_supported(self, file_path: str) -> bool:
        """Check if file type is supported.
        
        Args:
            file_path: Path to document file
            
        Returns:
            True if file type is supported
        """
        extension = Path(file_path).suffix.lower()
        return extension in self.PROCESSORS 