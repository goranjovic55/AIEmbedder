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
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('punkt')
            nltk.download('stopwords')
        
        # Initialize stopwords
        self.stopwords = set(stopwords.words('english'))
    
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
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters
        text = re.sub(r'[^\w\s]', ' ', text)
        
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
        
        # Remove numbers
        text = re.sub(r'\d+', '', text)
        
        # Remove short words (1-2 characters)
        text = ' '.join(word for word in text.split() if len(word) > 2)
        
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
        
        # Remove stopwords
        words = word_tokenize(text)
        text = ' '.join(word for word in words if word not in self.stopwords)
        
        # Remove very short words (1-3 characters)
        text = ' '.join(word for word in text.split() if len(word) > 3)
        
        return text.strip()
    
    def get_cleaning_levels(self) -> List[str]:
        """Get available cleaning levels.
        
        Returns:
            List of cleaning levels
        """
        return ["light", "medium", "aggressive"] 