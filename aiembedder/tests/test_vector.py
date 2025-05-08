"""
Tests for vector components.
"""

import pytest
import tempfile
from pathlib import Path

from aiembedder.vector.generator import VectorGenerator
from aiembedder.vector.database import VectorDatabase
from aiembedder.utils.errors import ProcessingError

def test_vector_generator():
    """Test vector generator."""
    # Test initialization
    generator = VectorGenerator(use_gpu=False)  # Use CPU for testing
    assert generator.get_embedding_dimension() > 0
    
    # Test model info
    model_info = generator.get_model_info()
    assert "model_name" in model_info
    assert "embedding_dim" in model_info
    assert "device" in model_info
    
    # Test embedding generation
    chunks = [
        {"text": "This is a test sentence."},
        {"text": "This is another test sentence."},
    ]
    chunks_with_embeddings = generator.generate_embeddings(chunks)
    
    assert len(chunks_with_embeddings) == len(chunks)
    assert all("embedding" in chunk for chunk in chunks_with_embeddings)
    assert all("embedding_model" in chunk for chunk in chunks_with_embeddings)
    assert all("embedding_dim" in chunk for chunk in chunks_with_embeddings)
    
    # Test empty input
    assert generator.generate_embeddings([]) == []

def test_vector_database():
    """Test vector database."""
    # Create temporary directory for database
    with tempfile.TemporaryDirectory() as temp_dir:
        # Test initialization
        db = VectorDatabase(
            collection_name="test_collection",
            persist_directory=temp_dir,
            use_gpu=False
        )
        
        # Test collection stats
        stats = db.get_collection_stats()
        assert stats["collection_name"] == "test_collection"
        assert stats["total_chunks"] == 0
        
        # Test adding chunks
        chunks = [
            {
                "text": "This is a test sentence.",
                "embedding": [0.1, 0.2, 0.3],
                "metadata": {"source": "test"}
            },
            {
                "text": "This is another test sentence.",
                "embedding": [0.4, 0.5, 0.6],
                "metadata": {"source": "test"}
            }
        ]
        chunk_ids = db.add_chunks(chunks)
        assert len(chunk_ids) == len(chunks)
        
        # Test collection stats after adding
        stats = db.get_collection_stats()
        assert stats["total_chunks"] == len(chunks)
        
        # Test search
        results = db.search("test sentence", n_results=2)
        assert len(results) > 0
        assert all("id" in result for result in results)
        assert all("text" in result for result in results)
        assert all("metadata" in result for result in results)
        assert all("score" in result for result in results)
        
        # Test search with metadata filter
        results = db.search(
            "test sentence",
            n_results=2,
            where={"source": "test"}
        )
        assert len(results) > 0
        assert all(result["metadata"]["source"] == "test" for result in results)
        
        # Test delete chunks
        db.delete_chunks(where={"source": "test"})
        stats = db.get_collection_stats()
        assert stats["total_chunks"] == 0
        
        # Test reset collection
        db.add_chunks(chunks)
        db.reset_collection()
        stats = db.get_collection_stats()
        assert stats["total_chunks"] == 0

def test_vector_pipeline():
    """Test vector pipeline (generator + database)."""
    # Create temporary directory for database
    with tempfile.TemporaryDirectory() as temp_dir:
        # Initialize components
        generator = VectorGenerator(use_gpu=False)
        db = VectorDatabase(
            collection_name="test_collection",
            persist_directory=temp_dir,
            use_gpu=False
        )
        
        # Test full pipeline
        chunks = [
            {"text": "This is a test sentence."},
            {"text": "This is another test sentence."},
        ]
        
        # Generate embeddings
        chunks_with_embeddings = generator.generate_embeddings(chunks)
        assert len(chunks_with_embeddings) == len(chunks)
        assert all("embedding" in chunk for chunk in chunks_with_embeddings)
        
        # Add to database
        chunk_ids = db.add_chunks(chunks_with_embeddings)
        assert len(chunk_ids) == len(chunks)
        
        # Search
        results = db.search("test sentence", n_results=2)
        assert len(results) > 0
        assert all("score" in result for result in results)
        
        # Clean up
        db.reset_collection() 