"""
Vector generator for AIEmbedder.
"""

from typing import List, Dict, Any, Optional
import torch
from sentence_transformers import SentenceTransformer

from aiembedder.utils.errors import ProcessingError
from aiembedder.utils.logging import Logger

class VectorGenerator:
    """Vector generator for text chunks with GPU support."""
    
    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        use_gpu: bool = True,
        logger: Optional[Logger] = None
    ):
        """Initialize vector generator.
        
        Args:
            model_name: Name of the sentence transformer model
            use_gpu: Whether to use GPU for embeddings
            logger: Logger instance
        """
        self.logger = logger or Logger()
        self.logger.info("Initializing vector generator")
        
        # Check GPU availability
        self.device = "cuda" if use_gpu and torch.cuda.is_available() else "cpu"
        self.logger.info(f"Using device: {self.device}")
        
        # Initialize sentence transformer
        try:
            self.model = SentenceTransformer(model_name, device=self.device)
            self.model_name = model_name
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
            self.logger.info(f"Loaded model {model_name} with dimension {self.embedding_dim}")
        except Exception as e:
            self.logger.error(f"Failed to load sentence transformer: {str(e)}")
            raise ProcessingError("Failed to initialize vector generator", "VECT_001")
    
    def generate_embeddings(
        self,
        chunks: List[Dict[str, Any]],
        batch_size: int = 32
    ) -> List[Dict[str, Any]]:
        """Generate embeddings for text chunks.
        
        Args:
            chunks: List of text chunks with metadata
            batch_size: Batch size for generating embeddings
            
        Returns:
            List of chunks with embeddings
            
        Raises:
            ProcessingError: If embedding generation fails
        """
        try:
            self.logger.info(f"Generating embeddings for {len(chunks)} chunks")
            
            if not chunks:
                return []
            
            # Extract texts
            texts = [chunk["text"] for chunk in chunks]
            
            # Generate embeddings in batches
            embeddings = []
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                batch_embeddings = self.model.encode(
                    batch_texts,
                    show_progress_bar=True,
                    convert_to_tensor=True
                )
                embeddings.extend(batch_embeddings)
            
            # Add embeddings to chunks
            for chunk, embedding in zip(chunks, embeddings):
                chunk["embedding"] = embedding.cpu().numpy()
                chunk["embedding_model"] = self.model_name
                chunk["embedding_dim"] = self.embedding_dim
            
            self.logger.info("Successfully generated embeddings")
            return chunks
            
        except Exception as e:
            self.logger.error(f"Error generating embeddings: {str(e)}")
            raise ProcessingError(f"Failed to generate embeddings: {str(e)}", "VECT_001")
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of generated embeddings.
        
        Returns:
            Embedding dimension
        """
        return self.embedding_dim
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the embedding model.
        
        Returns:
            Dictionary with model information
        """
        return {
            "model_name": self.model_name,
            "embedding_dim": self.embedding_dim,
            "device": self.device,
        } 