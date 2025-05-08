"""
Text chunker for AIEmbedder.
"""

import re
from typing import List, Optional

from nltk.tokenize import sent_tokenize

from aiembedder.utils.errors import ProcessingError
from aiembedder.utils.logging import Logger

class TextChunker:
    """Text chunker with configurable chunk size and overlap."""
    
    def __init__(self, logger: Optional[Logger] = None):
        """Initialize text chunker.
        
        Args:
            logger: Logger instance
        """
        self.logger = logger or Logger()
        self.logger.info("Initialized text chunker")
    
    def chunk(self, text: str, chunk_size: int = 400, chunk_overlap: int = 50) -> List[str]:
        """Split text into chunks with overlap.
        
        Args:
            text: Text to chunk
            chunk_size: Maximum chunk size in tokens
            chunk_overlap: Number of tokens to overlap between chunks
            
        Returns:
            List of text chunks
            
        Raises:
            ProcessingError: If chunking fails
        """
        try:
            self.logger.info(f"Chunking text with size {chunk_size} and overlap {chunk_overlap}")
            
            # Validate parameters
            if chunk_size <= 0:
                raise ProcessingError("Chunk size must be positive", "PROC_003")
            if chunk_overlap < 0:
                raise ProcessingError("Chunk overlap must be non-negative", "PROC_003")
            if chunk_overlap >= chunk_size:
                raise ProcessingError("Chunk overlap must be less than chunk size", "PROC_003")
            
            # Split text into sentences
            sentences = sent_tokenize(text)
            
            # Initialize chunks
            chunks = []
            current_chunk = []
            current_size = 0
            
            for sentence in sentences:
                # Get sentence tokens
                sentence_tokens = sentence.split()
                sentence_size = len(sentence_tokens)
                
                # If adding this sentence would exceed chunk size
                if current_size + sentence_size > chunk_size:
                    # If current chunk is not empty, add it to chunks
                    if current_chunk:
                        chunks.append(' '.join(current_chunk))
                    
                    # Start new chunk with overlap
                    if chunks and chunk_overlap > 0:
                        # Get last chunk's tokens
                        last_chunk_tokens = chunks[-1].split()
                        # Take last chunk_overlap tokens
                        overlap_tokens = last_chunk_tokens[-chunk_overlap:]
                        current_chunk = overlap_tokens
                        current_size = len(overlap_tokens)
                    else:
                        current_chunk = []
                        current_size = 0
                
                # Add sentence to current chunk
                current_chunk.append(sentence)
                current_size += sentence_size
            
            # Add final chunk if not empty
            if current_chunk:
                chunks.append(' '.join(current_chunk))
            
            self.logger.info(f"Created {len(chunks)} chunks")
            return chunks
            
        except Exception as e:
            self.logger.error(f"Error chunking text: {str(e)}")
            raise ProcessingError(f"Failed to chunk text: {str(e)}", "PROC_003")
    
    def get_token_count(self, text: str) -> int:
        """Get number of tokens in text.
        
        Args:
            text: Text to count tokens
            
        Returns:
            Number of tokens
        """
        return len(text.split())
    
    def get_sentence_count(self, text: str) -> int:
        """Get number of sentences in text.
        
        Args:
            text: Text to count sentences
            
        Returns:
            Number of sentences
        """
        return len(sent_tokenize(text)) 