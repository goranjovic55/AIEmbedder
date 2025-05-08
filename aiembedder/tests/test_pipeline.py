"""
Tests for the text processing pipeline.
"""

import pytest
from pathlib import Path
import tempfile

from aiembedder.processing.pipeline import TextProcessingPipeline
from aiembedder.utils.errors import ProcessingError
from aiembedder.utils.progress import ProgressTracker

def test_pipeline_initialization():
    """Test pipeline initialization."""
    # Test default initialization
    pipeline = TextProcessingPipeline()
    assert pipeline.cleaning_level == "medium"
    assert pipeline.chunk_size == 400
    assert pipeline.chunk_overlap == 50
    assert pipeline.similarity_threshold == 0.95
    
    # Test custom initialization
    pipeline = TextProcessingPipeline(
        cleaning_level="light",
        chunk_size=200,
        chunk_overlap=20,
        similarity_threshold=0.9,
        use_gpu=False
    )
    assert pipeline.cleaning_level == "light"
    assert pipeline.chunk_size == 200
    assert pipeline.chunk_overlap == 20
    assert pipeline.similarity_threshold == 0.9
    
    # Test invalid parameters
    with pytest.raises(ProcessingError):
        TextProcessingPipeline(cleaning_level="invalid")
    with pytest.raises(ProcessingError):
        TextProcessingPipeline(chunk_size=0)
    with pytest.raises(ProcessingError):
        TextProcessingPipeline(chunk_size=100, chunk_overlap=100)
    with pytest.raises(ProcessingError):
        TextProcessingPipeline(similarity_threshold=1.5)

def test_process_text():
    """Test text processing."""
    pipeline = TextProcessingPipeline(
        cleaning_level="light",
        chunk_size=10,
        chunk_overlap=2,
        similarity_threshold=0.95
    )
    
    # Test basic text processing
    text = "This is a test sentence. This is another test sentence."
    chunks = pipeline.process_text(text)
    assert len(chunks) > 0
    assert all("text" in chunk for chunk in chunks)
    assert all("chunk_index" in chunk for chunk in chunks)
    assert all("total_chunks" in chunk for chunk in chunks)
    
    # Test with metadata
    metadata = {"source": "test", "author": "tester"}
    chunks = pipeline.process_text(text, metadata)
    assert all(chunk["source"] == "test" for chunk in chunks)
    assert all(chunk["author"] == "tester" for chunk in chunks)
    
    # Test with duplicate text
    text = "This is a test. This is a test. This is a test."
    chunks = pipeline.process_text(text)
    assert len(chunks) < 3  # Should have fewer chunks due to deduplication
    
    # Test with empty text
    chunks = pipeline.process_text("")
    assert len(chunks) == 0

def test_process_file():
    """Test file processing."""
    pipeline = TextProcessingPipeline(
        cleaning_level="light",
        chunk_size=10,
        chunk_overlap=2
    )
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write("This is a test sentence. This is another test sentence.")
        file_path = Path(f.name)
    
    try:
        # Test file processing
        chunks = pipeline.process_file(file_path)
        assert len(chunks) > 0
        assert all("file_path" in chunk for chunk in chunks)
        assert all("file_name" in chunk for chunk in chunks)
        assert all("file_size" in chunk for chunk in chunks)
        
        # Test with metadata
        metadata = {"source": "test", "author": "tester"}
        chunks = pipeline.process_file(file_path, metadata)
        assert all(chunk["source"] == "test" for chunk in chunks)
        assert all(chunk["author"] == "tester" for chunk in chunks)
        
        # Test with non-existent file
        with pytest.raises(ProcessingError):
            pipeline.process_file(Path("nonexistent.txt"))
            
    finally:
        # Clean up temporary file
        file_path.unlink()

def test_progress_tracking():
    """Test progress tracking."""
    progress_tracker = ProgressTracker()
    pipeline = TextProcessingPipeline(progress_tracker=progress_tracker)
    
    # Process text and check progress
    text = "This is a test sentence. This is another test sentence."
    chunks = pipeline.process_text(text)
    
    # Get task state
    task = progress_tracker.get_task("text_processing")
    assert task is not None
    assert task.is_complete
    assert task.current == task.total
    assert task.status == "Adding metadata"

def test_processing_stats():
    """Test processing statistics."""
    pipeline = TextProcessingPipeline(
        cleaning_level="light",
        chunk_size=200,
        chunk_overlap=20,
        similarity_threshold=0.9,
        use_gpu=False
    )
    
    stats = pipeline.get_processing_stats()
    assert stats["cleaning_level"] == "light"
    assert stats["chunk_size"] == 200
    assert stats["chunk_overlap"] == 20
    assert stats["similarity_threshold"] == 0.9
    assert stats["use_gpu"] is False
    assert "light" in stats["available_cleaning_levels"]
    assert "medium" in stats["available_cleaning_levels"]
    assert "aggressive" in stats["available_cleaning_levels"] 