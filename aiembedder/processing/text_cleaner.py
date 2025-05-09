"""
Text cleaner for AIEmbedder.
"""

import re
from typing import Optional, List

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

from aiembedder.utils.errors import ProcessingError
from aiembedder.utils.logging import Logger

class TextCleaner:
    """Text cleaner with configurable cleaning levels."""
    
    def __init__(self, logger: Optional[Logger] = None):
        """Initialize text cleaner.
        
        Args:
            logger: Logger instance
        """
        self.logger = logger or Logger()
        self.logger.info("Initialized text cleaner")
        
        # Download required NLTK data
        try:
            # First try to find resources
            try:
                nltk.data.find('tokenizers/punkt')
            except LookupError:
                self.logger.info("Downloading NLTK punkt data...")
                nltk.download('punkt')
            
            try:
                nltk.data.find('corpora/stopwords')
            except LookupError:
                self.logger.info("Downloading NLTK stopwords data...")
                nltk.download('stopwords')
        except Exception as e:
            self.logger.error(f"Error initializing NLTK resources: {e}")
            self.logger.info("NLTK resources may need to be downloaded manually:")
            self.logger.info("Run 'python -m nltk.downloader punkt stopwords'")
        
        # Initialize stopwords with fallback
        try:
            self.stopwords = set(stopwords.words('english'))
        except Exception as e:
            self.logger.error(f"Could not load stopwords: {e}")
            self.stopwords = set()  # Fallback to empty set
    
    def clean(self, text: str, level: str = "medium") -> str:
        """Clean text based on specified level.
        
        Args:
            text: Text to clean
            level: Cleaning level (light, medium, aggressive)
            
        Returns:
            Cleaned text
            
        Raises:
            ProcessingError: If cleaning fails
        """
        try:
            self.logger.info(f"Cleaning text with level: {level}")
            
            # Apply basic cleaning to all levels
            text = self._basic_clean(text)
            
            # Apply level-specific cleaning
            if level == "light":
                return text
            elif level == "medium":
                return self._medium_clean(text)
            elif level == "aggressive":
                return self._aggressive_clean(text)
            else:
                raise ProcessingError(f"Invalid cleaning level: {level}", "PROC_002")
            
        except Exception as e:
            self.logger.error(f"Error cleaning text: {str(e)}")
            raise ProcessingError(f"Failed to clean text: {str(e)}", "PROC_002")
    
    def _basic_clean(self, text: str) -> str:
        """Apply basic cleaning to text.
        
        Args:
            text: Text to clean
            
        Returns:
            Basic cleaned text
        """
        # Don't convert to lowercase - preserve case for better semantic meaning
        # text = text.lower()
        
        # Normalize line breaks
        text = re.sub(r'\r\n', '\n', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Preserve important punctuation for sentence detection
        # We only remove excessive punctuation rather than all special characters
        text = re.sub(r'([.!?])[.!?]+', r'\1', text)
        
        return text.strip()
    
    def _medium_clean(self, text: str) -> str:
        """Apply medium cleaning to text.
        
        Args:
            text: Text to clean
            
        Returns:
            Medium cleaned text
        """
        # Apply basic cleaning
        text = self._basic_clean(text)
        
        # Remove repeated punctuation
        text = re.sub(r'([.!?])[.!?]+', r'\1', text)
        
        # Replace multiple dashes with a single dash
        text = re.sub(r'-+', '-', text)
        
        # We don't remove numbers anymore - they're often meaningful
        # text = re.sub(r'\d+', '', text)
        
        # We don't remove short words either - they may be part of key phrases
        # text = ' '.join(word for word in text.split() if len(word) > 2)
        
        return text.strip()
    
    def _aggressive_clean(self, text: str) -> str:
        """Apply aggressive cleaning to text.
        
        Args:
            text: Text to clean
            
        Returns:
            Aggressively cleaned text
        """
        # Apply medium cleaning
        text = self._medium_clean(text)
        
        # Convert to lowercase for aggressive cleaning
        text = text.lower()
        
        # Remove stopwords with fallback in case word_tokenize fails
        try:
            words = word_tokenize(text)
            text = ' '.join(word for word in words if word not in self.stopwords)
        except Exception as e:
            self.logger.warning(f"Error using NLTK word_tokenize: {e}")
            # Fallback to simple splitting
            words = text.split()
            text = ' '.join(word for word in words if word not in self.stopwords)
        
        # Remove very short words (1-2 characters)
        text = ' '.join(word for word in text.split() if len(word) > 2)
        
        return text.strip()
    
    def get_cleaning_levels(self) -> List[str]:
        """Get available cleaning levels.
        
        Returns:
            List of cleaning levels
        """
        return ["light", "medium", "aggressive"] 