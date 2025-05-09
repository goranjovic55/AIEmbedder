"""
Text chunker for AIEmbedder.
"""

import re
from typing import List, Optional
import nltk

# Try to use NLTK but provide fallback
try:
    from nltk.tokenize import sent_tokenize
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False

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
        
        # Store NLTK availability as an instance attribute
        self.nltk_available = NLTK_AVAILABLE
        
        # Ensure NLTK resources are available if NLTK is installed
        if self.nltk_available:
            try:
                try:
                    nltk.data.find('tokenizers/punkt')
                except LookupError:
                    self.logger.info("Downloading NLTK punkt data...")
                    nltk.download('punkt')
            except Exception as e:
                self.logger.error(f"Error initializing NLTK resources: {e}")
                self.logger.warning("NLTK punkt resource not available, using fallback tokenizer")
                # Set NLTK_AVAILABLE to False to force fallback
                self.nltk_available = False
    
    def _fallback_sent_tokenize(self, text: str) -> List[str]:
        """Fallback sentence tokenizer using regex.
        
        Args:
            text: Text to tokenize
            
        Returns:
            List of sentences
        """
        # Simple regex for sentence boundary detection
        # This is not as good as NLTK's tokenizer but serves as a fallback
        self.logger.info("Using fallback sentence tokenizer")
        sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _get_sentences(self, text: str) -> List[str]:
        """Get sentences from text using NLTK if available, otherwise fallback.
        
        Args:
            text: Text to tokenize
            
        Returns:
            List of sentences
        """
        try:
            if self.nltk_available:
                try:
                    return sent_tokenize(text)
                except Exception as e:
                    self.logger.warning(f"Error using NLTK sent_tokenize: {str(e)}")
                    self.logger.info("Falling back to regex tokenizer")
                    return self._fallback_sent_tokenize(text)
            else:
                return self._fallback_sent_tokenize(text)
        except Exception as e:
            self.logger.warning(f"Error in sentence tokenization: {str(e)}")
            return self._fallback_sent_tokenize(text)
    
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
            
            # Get token count to ensure we're creating multiple chunks for large docs
            total_tokens = len(text.split())
            self.logger.info(f"Total tokens in text: {total_tokens}")
            
            # If this is a small text that fits in one chunk, just return it
            if total_tokens <= chunk_size:
                self.logger.info(f"Text fits in a single chunk ({total_tokens} tokens)")
                return [text]
            
            # Split text into sentences using safe method
            sentences = self._get_sentences(text)
            self.logger.info(f"Split text into {len(sentences)} sentences")
            
            # Initialize chunks
            chunks = []
            current_chunk = []
            current_size = 0
            
            for sentence in sentences:
                # Get sentence tokens
                sentence_tokens = sentence.split()
                sentence_size = len(sentence_tokens)
                
                # Handle excessively long sentences (longer than chunk_size)
                if sentence_size > chunk_size:
                    self.logger.warning(f"Found sentence longer than chunk_size: {sentence_size} tokens")
                    # If we have a current chunk, add it first
                    if current_chunk:
                        chunks.append(' '.join(current_chunk))
                        current_chunk = []
                        current_size = 0
                    
                    # Add sentence as separate chunks (forced split)
                    for i in range(0, sentence_size, chunk_size - chunk_overlap):
                        end_idx = min(i + chunk_size, sentence_size)
                        chunk_text = ' '.join(sentence_tokens[i:end_idx])
                        chunks.append(chunk_text)
                        
                        # If this is the last piece and it's smaller than overlap, stop
                        if end_idx == sentence_size:
                            break
                    
                    continue
                
                # If adding this sentence would exceed chunk size, finish current chunk
                if current_chunk and (current_size + sentence_size > chunk_size):
                    chunks.append(' '.join(current_chunk))
                    
                    # Start new chunk with overlap from previous chunk
                    if chunk_overlap > 0:
                        # Get last chunk tokens
                        last_chunk_tokens = ' '.join(current_chunk).split()
                        # Take tokens for overlap, but no more than what we have
                        overlap_count = min(chunk_overlap, len(last_chunk_tokens))
                        overlap_tokens = last_chunk_tokens[-overlap_count:] if overlap_count > 0 else []
                        
                        # Start new chunk with overlap
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
            
            # Verify chunks were actually created
            if len(chunks) <= 1 and total_tokens > chunk_size:
                self.logger.warning(f"Chunking algorithm created only {len(chunks)} chunk(s) for {total_tokens} tokens with chunk_size={chunk_size}. This may indicate a problem.")
            
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
        return len(self._get_sentences(text)) 