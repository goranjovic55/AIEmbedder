"""
Deduplicator for AIEmbedder.
"""

from typing import List, Optional, Set, Tuple
import numpy as np
import torch
from sentence_transformers import SentenceTransformer

from aiembedder.utils.errors import ProcessingError
from aiembedder.utils.logging import Logger

class Deduplicator:
    """Deduplicator for text chunks with GPU support."""
    
    def __init__(self, logger: Optional[Logger] = None, use_gpu: bool = True):
        """Initialize deduplicator.
        
        Args:
            logger: Logger instance
            use_gpu: Whether to use GPU for embeddings
        """
        self.logger = logger or Logger()
        self.logger.info("Initialized deduplicator")
        
        # Check GPU availability
        self.device = "cuda" if use_gpu and torch.cuda.is_available() else "cpu"
        self.logger.info(f"Using device: {self.device}")
        
        # Initialize sentence transformer
        try:
            self.model = SentenceTransformer('all-MiniLM-L6-v2', device=self.device)
        except Exception as e:
            self.logger.error(f"Failed to load sentence transformer: {str(e)}")
            raise ProcessingError("Failed to initialize deduplicator", "PROC_004")
    
    def deduplicate(self, chunks: List[str], threshold: float = 0.95) -> List[str]:
        """Remove duplicate chunks based on similarity.
        
        Args:
            chunks: List of text chunks
            threshold: Similarity threshold (0-1)
            
        Returns:
            List of unique chunks
            
        Raises:
            ProcessingError: If deduplication fails
        """
        try:
            self.logger.info(f"Deduplicating {len(chunks)} chunks with threshold {threshold}")
            
            if not chunks:
                return []
            
            # Validate threshold
            if not 0 <= threshold <= 1:
                raise ProcessingError("Threshold must be between 0 and 1", "PROC_004")
            
            # Generate embeddings
            embeddings = self.model.encode(chunks, show_progress_bar=True)
            
            # Convert to tensor
            embeddings = torch.tensor(embeddings, device=self.device)
            
            # Calculate similarity matrix
            similarity_matrix = torch.mm(embeddings, embeddings.t())
            
            # Get unique chunks
            unique_chunks = []
            seen_indices: Set[int] = set()
            
            for i in range(len(chunks)):
                if i in seen_indices:
                    continue
                
                # Add current chunk
                unique_chunks.append(chunks[i])
                
                # Find similar chunks
                similar_indices = torch.where(similarity_matrix[i] > threshold)[0]
                seen_indices.update(similar_indices.tolist())
            
            self.logger.info(f"Removed {len(chunks) - len(unique_chunks)} duplicate chunks")
            return unique_chunks
            
        except Exception as e:
            self.logger.error(f"Error deduplicating chunks: {str(e)}")
            raise ProcessingError(f"Failed to deduplicate chunks: {str(e)}", "PROC_004")
    
    def get_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0-1)
        """
        try:
            # Generate embeddings
            embeddings = self.model.encode([text1, text2])
            
            # Calculate cosine similarity
            similarity = np.dot(embeddings[0], embeddings[1]) / (
                np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
            )
            
            return float(similarity)
            
        except Exception as e:
            self.logger.error(f"Error calculating similarity: {str(e)}")
            raise ProcessingError(f"Failed to calculate similarity: {str(e)}", "PROC_004")
    
    def find_duplicates(self, chunks: List[str], threshold: float = 0.95) -> List[Tuple[int, int]]:
        """Find duplicate chunks based on similarity.
        
        Args:
            chunks: List of text chunks
            threshold: Similarity threshold (0-1)
            
        Returns:
            List of (index1, index2) pairs for duplicate chunks
        """
        try:
            self.logger.info(f"Finding duplicates in {len(chunks)} chunks")
            
            if not chunks:
                return []
            
            # Generate embeddings
            embeddings = self.model.encode(chunks, show_progress_bar=True)
            
            # Convert to tensor
            embeddings = torch.tensor(embeddings, device=self.device)
            
            # Calculate similarity matrix
            similarity_matrix = torch.mm(embeddings, embeddings.t())
            
            # Find duplicates
            duplicates = []
            for i in range(len(chunks)):
                for j in range(i + 1, len(chunks)):
                    if similarity_matrix[i, j] > threshold:
                        duplicates.append((i, j))
            
            self.logger.info(f"Found {len(duplicates)} duplicate pairs")
            return duplicates
            
        except Exception as e:
            self.logger.error(f"Error finding duplicates: {str(e)}")
            raise ProcessingError(f"Failed to find duplicates: {str(e)}", "PROC_004") 