"""
Text chunker for AIEmbedder.
"""

import re
from typing import List, Optional, Dict, Any, Tuple
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
    
    # Common section patterns to detect document structure
    SECTION_PATTERNS = [
        # Chapter patterns
        r'^chapter\s+\d+[.:]\s+', 
        r'^\d+\.\s+',
        # Section patterns
        r'^\d+\.\d+\.\s+',
        r'^section\s+\d+[.:]\s+',
        # Appendix patterns
        r'^appendix\s+[a-z]\s+',
        # Heading with numbering
        r'^[IVXivx]+\.\s+',
        # Common document divisions
        r'^introduction$',
        r'^conclusion$',
        r'^references$',
        r'^bibliography$',
        # Special sections
        r'^abstract$',
        r'^summary$',
        r'^acknowledgments$',
    ]
    
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
    
    def _detect_section_boundaries(self, text: str) -> List[Tuple[int, str]]:
        """Detect section boundaries in text.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of tuples (line_index, section_heading)
        """
        boundaries = []
        lines = text.split('\n')
        
        # Compile section patterns for efficiency
        compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.SECTION_PATTERNS]
        
        # Add artificial boundary at start
        boundaries.append((0, "Start"))
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            
            # Skip empty lines
            if not line_stripped:
                continue
                
            # Check if this line matches a section pattern
            for pattern in compiled_patterns:
                if pattern.match(line_stripped):
                    boundaries.append((i, line_stripped))
                    break
            
            # Additional heuristics for detecting section headings
            # 1. Check for all caps lines that are potential headings
            if (line_stripped.isupper() and 
                len(line_stripped) > 3 and  # Not too short
                len(line_stripped) < 100 and  # Not too long
                not any(c.isdigit() for c in line_stripped)):  # No numbers
                boundaries.append((i, line_stripped))
                
            # 2. Check for lines that are likely headings
            elif (line_stripped.istitle() and  # Title case
                  len(line_stripped.split()) < 7 and  # Not too many words
                  len(line_stripped) < 60 and  # Not too long
                  not line_stripped[-1] in ".,:;?!"):  # Doesn't end with punctuation
                boundaries.append((i, line_stripped))
        
        return boundaries
    
    def chunk_with_structure(self, text: str, target_chunk_size: int = 400, 
                           chunk_overlap: int = 50, 
                           flexibility_percent: int = 30) -> List[Dict[str, Any]]:
        """Split text into chunks respecting document structure like chapters and sections.
        
        Args:
            text: Text to chunk
            target_chunk_size: Target chunk size in tokens
            chunk_overlap: Number of tokens to overlap between chunks
            flexibility_percent: How much chunks can deviate from target size (percentage)
            
        Returns:
            List of chunks with metadata
            
        Raises:
            ProcessingError: If chunking fails
        """
        try:
            self.logger.info(f"Chunking text with structure awareness, target size {target_chunk_size} and flexibility {flexibility_percent}%")
            
            # Calculate flexibility bounds
            min_size = int(target_chunk_size * (1 - flexibility_percent/100))
            max_size = int(target_chunk_size * (1 + flexibility_percent/100))
            
            self.logger.info(f"Chunk size flexibility: {min_size} to {max_size} tokens")
            
            # Validate parameters
            if target_chunk_size <= 0:
                raise ProcessingError("Chunk size must be positive", "PROC_003")
            if chunk_overlap < 0:
                raise ProcessingError("Chunk overlap must be non-negative", "PROC_003")
            if chunk_overlap >= target_chunk_size:
                raise ProcessingError("Chunk overlap must be less than chunk size", "PROC_003")
            
            # Get token count
            total_tokens = len(text.split())
            self.logger.info(f"Total tokens in text: {total_tokens}")
            
            # If this is a small text that fits in one chunk, just return it
            if total_tokens <= max_size:
                self.logger.info(f"Text fits in a single chunk ({total_tokens} tokens)")
                return [{
                    "text": text,
                    "is_first_chunk": True,
                    "is_last_chunk": True,
                    "chunk_index": 0,
                    "total_chunks": 1,
                    "token_count": total_tokens,
                    "section": "Full Document"
                }]
            
            # Get section boundaries
            lines = text.split('\n')
            section_boundaries = self._detect_section_boundaries(text)
            
            self.logger.info(f"Detected {len(section_boundaries)} section boundaries")
            
            # Convert line numbers to characters
            section_positions = []
            char_position = 0
            for line_idx, section_name in section_boundaries:
                # Convert lines to character position
                for i in range(line_idx):
                    if i < len(lines):
                        char_position += len(lines[i]) + 1  # +1 for newline
                section_positions.append((char_position, section_name))
            
            # Add EOD for convenience
            section_positions.append((len(text), "End of Document"))
            
            # Split text into sentences using safe method
            sentences = self._get_sentences(text)
            self.logger.info(f"Split text into {len(sentences)} sentences")
            
            # Get character positions of each sentence
            sentence_positions = []
            current_pos = 0
            for sent in sentences:
                start = text.find(sent, current_pos)
                if start == -1:  # Fallback if exact match fails
                    start = current_pos
                end = start + len(sent)
                sentence_positions.append((start, end, sent))
                current_pos = end
            
            # Initialize chunks
            chunks = []
            current_chunk_sentences = []
            current_size = 0
            current_section = "Start"
            next_section_idx = 1
            
            for i, (start, end, sentence) in enumerate(sentence_positions):
                # Update current section if we've passed a section boundary
                while (next_section_idx < len(section_positions) and 
                       start >= section_positions[next_section_idx][0]):
                    current_section = section_positions[next_section_idx][1]
                    next_section_idx += 1
                
                # Get sentence tokens and size
                sentence_tokens = sentence.split()
                sentence_size = len(sentence_tokens)
                
                # Handle excessively long sentences (longer than max_size)
                if sentence_size > max_size:
                    self.logger.warning(f"Found sentence longer than max_size: {sentence_size} tokens")
                    
                    # If we have a current chunk, add it first
                    if current_chunk_sentences:
                        chunk_text = ' '.join(current_chunk_sentences)
                        chunks.append({
                            "text": chunk_text,
                            "is_first_chunk": len(chunks) == 0,
                            "is_last_chunk": False,
                            "chunk_index": len(chunks),
                            "total_chunks": -1,  # Will update later
                            "token_count": current_size,
                            "section": current_section
                        })
                        current_chunk_sentences = []
                        current_size = 0
                    
                    # Add long sentence as separate chunks (forced split)
                    for j in range(0, sentence_size, max_size - chunk_overlap):
                        end_idx = min(j + max_size, sentence_size)
                        chunk_text = ' '.join(sentence_tokens[j:end_idx])
                        chunks.append({
                            "text": chunk_text,
                            "is_first_chunk": len(chunks) == 0,
                            "is_last_chunk": False,
                            "chunk_index": len(chunks),
                            "total_chunks": -1,  # Will update later
                            "token_count": end_idx - j,
                            "section": current_section
                        })
                        
                        # If this is the last piece and it's smaller than overlap, stop
                        if end_idx == sentence_size:
                            break
                    
                    continue
                
                # Check if adding this sentence would exceed target size
                new_size = current_size + sentence_size
                
                # If we're at a new section boundary
                at_section_boundary = False
                for pos, section in section_positions:
                    if start <= pos < end:
                        at_section_boundary = True
                        break
                
                # Finish current chunk if:
                # 1. Adding this sentence would exceed max_size, OR
                # 2. We're past target_size AND reached a section boundary, OR
                # 3. We're past target_size AND at a good break point (not mid-paragraph)
                good_break_point = sentence.strip().endswith(('.', '!', '?', ':', ';')) and i > 0
                should_break = (new_size > max_size or 
                               (new_size >= target_chunk_size and at_section_boundary) or
                               (new_size >= target_chunk_size and good_break_point))
                
                if current_chunk_sentences and should_break:
                    # Special exception - if current chunk is too small and we're not 
                    # at a section boundary, don't break
                    if current_size < min_size and not at_section_boundary:
                        # Continue adding to current chunk
                        pass
                    else:
                        # Finish current chunk
                        chunk_text = ' '.join(current_chunk_sentences)
                        chunks.append({
                            "text": chunk_text,
                            "is_first_chunk": len(chunks) == 0,
                            "is_last_chunk": False,
                            "chunk_index": len(chunks),
                            "total_chunks": -1,  # Will update later
                            "token_count": current_size,
                            "section": current_section
                        })
                        
                        # Start new chunk with overlap from previous chunk
                        if chunk_overlap > 0:
                            # Calculate overlap sentences
                            overlap_tokens = 0
                            overlap_sentences = []
                            for s in reversed(current_chunk_sentences):
                                s_tokens = len(s.split())
                                if overlap_tokens + s_tokens <= chunk_overlap:
                                    overlap_sentences.insert(0, s)
                                    overlap_tokens += s_tokens
                                else:
                                    break
                            
                            # Start new chunk with overlap
                            current_chunk_sentences = overlap_sentences
                            current_size = overlap_tokens
                        else:
                            current_chunk_sentences = []
                            current_size = 0
                
                # Add sentence to current chunk
                current_chunk_sentences.append(sentence)
                current_size += sentence_size
            
            # Add final chunk if not empty
            if current_chunk_sentences:
                chunk_text = ' '.join(current_chunk_sentences)
                chunks.append({
                    "text": chunk_text,
                    "is_first_chunk": len(chunks) == 0,
                    "is_last_chunk": True,
                    "chunk_index": len(chunks),
                    "total_chunks": len(chunks) + 1,  # Now we know
                    "token_count": current_size,
                    "section": current_section
                })
            
            # Update total chunks count
            total_chunks = len(chunks)
            for chunk in chunks:
                chunk["total_chunks"] = total_chunks
                # Fix last chunk flag (only the last one is True)
                chunk["is_last_chunk"] = (chunk["chunk_index"] == total_chunks - 1)
                
            # Log chunk sizes for verification
            chunk_sizes = [chunk["token_count"] for chunk in chunks]
            self.logger.info(f"Created {len(chunks)} chunks with sizes: {chunk_sizes}")
            
            # Verify chunks were actually created
            if len(chunks) <= 1 and total_tokens > max_size:
                self.logger.warning(f"Chunking algorithm created only {len(chunks)} chunk(s) for {total_tokens} tokens with target_size={target_chunk_size}. This may indicate a problem.")
            
            return chunks
            
        except Exception as e:
            self.logger.error(f"Error chunking text: {str(e)}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            raise ProcessingError(f"Failed to chunk text: {str(e)}", "PROC_003")
    
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
        # Call to the new structure-aware method with default flexibility
        try:
            structured_chunks = self.chunk_with_structure(
                text=text,
                target_chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                flexibility_percent=30  # Default flexibility
            )
            
            # Convert to simple list of strings for backward compatibility
            return [chunk["text"] for chunk in structured_chunks]
        except Exception as e:
            self.logger.error(f"Error in structure-aware chunking, falling back to basic chunking: {str(e)}")
            # Fallback to the original implementation
            return self._chunk_basic(text, chunk_size, chunk_overlap)
    
    def _chunk_basic(self, text: str, chunk_size: int = 400, chunk_overlap: int = 50) -> List[str]:
        """Original chunking method (kept for fallback).
        
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
            self.logger.info(f"Using basic chunking with size {chunk_size} and overlap {chunk_overlap}")
            
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