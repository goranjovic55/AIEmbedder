"""
Vector database manager for AIEmbedder.
"""

from typing import List, Dict, Any, Optional, Tuple
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import numpy as np

from aiembedder.utils.errors import ProcessingError
from aiembedder.utils.logging import Logger

class VectorDatabase:
    """Vector database manager for storing and querying embeddings."""
    
    def __init__(
        self,
        collection_name: str = "aiembedder",
        persist_directory: str = "~/.aiembedder/db",
        use_gpu: bool = True,
        logger: Optional[Logger] = None
    ):
        """Initialize vector database.
        
        Args:
            collection_name: Name of the collection
            persist_directory: Directory to persist the database
            use_gpu: Whether to use GPU for operations
            logger: Logger instance
        """
        self.logger = logger or Logger()
        self.logger.info("Initializing vector database")
        
        try:
            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(
                path=persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True,
                    is_persistent=True
                )
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"description": "AIEmbedder vector collection"}
            )
            
            self.logger.info(f"Initialized collection: {collection_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize vector database: {str(e)}")
            raise ProcessingError("Failed to initialize vector database", "VECT_002")
    
    def add_chunks(
        self,
        chunks: List[Dict[str, Any]],
        batch_size: int = 100
    ) -> List[str]:
        """Add chunks to the database.
        
        Args:
            chunks: List of chunks with embeddings and metadata
            batch_size: Batch size for adding chunks
            
        Returns:
            List of chunk IDs
            
        Raises:
            ProcessingError: If adding chunks fails
        """
        try:
            self.logger.info(f"Adding {len(chunks)} chunks to database")
            
            if not chunks:
                return []
            
            # Prepare data
            ids = []
            embeddings = []
            documents = []
            metadatas = []
            
            for i, chunk in enumerate(chunks):
                chunk_id = f"chunk_{i}"
                ids.append(chunk_id)
                embeddings.append(chunk["embedding"].tolist())
                documents.append(chunk["text"])
                
                # Prepare metadata
                metadata = {k: v for k, v in chunk.items() if k not in ["text", "embedding"]}
                metadatas.append(metadata)
            
            # Add chunks in batches
            for i in range(0, len(ids), batch_size):
                batch_ids = ids[i:i + batch_size]
                batch_embeddings = embeddings[i:i + batch_size]
                batch_documents = documents[i:i + batch_size]
                batch_metadatas = metadatas[i:i + batch_size]
                
                self.collection.add(
                    ids=batch_ids,
                    embeddings=batch_embeddings,
                    documents=batch_documents,
                    metadatas=batch_metadatas
                )
            
            self.logger.info("Successfully added chunks to database")
            return ids
            
        except Exception as e:
            self.logger.error(f"Error adding chunks to database: {str(e)}")
            raise ProcessingError(f"Failed to add chunks to database: {str(e)}", "VECT_002")
    
    def search(
        self,
        query: str,
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar chunks.
        
        Args:
            query: Query text
            n_results: Number of results to return
            where: Optional metadata filter
            
        Returns:
            List of similar chunks with scores
            
        Raises:
            ProcessingError: If search fails
        """
        try:
            self.logger.info(f"Searching for: {query}")
            
            # Search database
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where
            )
            
            # Format results
            similar_chunks = []
            for i in range(len(results["ids"][0])):
                chunk = {
                    "id": results["ids"][0][i],
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "score": float(results["distances"][0][i])
                }
                similar_chunks.append(chunk)
            
            self.logger.info(f"Found {len(similar_chunks)} similar chunks")
            return similar_chunks
            
        except Exception as e:
            self.logger.error(f"Error searching database: {str(e)}")
            raise ProcessingError(f"Failed to search database: {str(e)}", "VECT_002")
    
    def delete_chunks(
        self,
        where: Optional[Dict[str, Any]] = None,
        ids: Optional[List[str]] = None
    ) -> int:
        """Delete chunks from the database.
        
        Args:
            where: Optional metadata filter
            ids: Optional list of chunk IDs
            
        Returns:
            Number of deleted chunks
            
        Raises:
            ProcessingError: If deletion fails
        """
        try:
            self.logger.info("Deleting chunks from database")
            
            # Delete chunks
            self.collection.delete(
                where=where,
                ids=ids
            )
            
            self.logger.info("Successfully deleted chunks")
            return 1  # ChromaDB doesn't return count, so we assume success
            
        except Exception as e:
            self.logger.error(f"Error deleting chunks: {str(e)}")
            raise ProcessingError(f"Failed to delete chunks: {str(e)}", "VECT_002")
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics.
        
        Returns:
            Dictionary with collection statistics
        """
        try:
            count = self.collection.count()
            return {
                "collection_name": self.collection.name,
                "total_chunks": count,
            }
        except Exception as e:
            self.logger.error(f"Error getting collection stats: {str(e)}")
            raise ProcessingError(f"Failed to get collection stats: {str(e)}", "VECT_002")
    
    def reset_collection(self) -> None:
        """Reset the collection.
        
        Raises:
            ProcessingError: If reset fails
        """
        try:
            self.logger.info("Resetting collection")
            self.collection.delete(where={})
            self.logger.info("Successfully reset collection")
        except Exception as e:
            self.logger.error(f"Error resetting collection: {str(e)}")
            raise ProcessingError(f"Failed to reset collection: {str(e)}", "VECT_002") 