"""
Tests for text processing components.
"""

import pytest

from aiembedder.processing.text_cleaner import TextCleaner
from aiembedder.processing.text_chunker import TextChunker
from aiembedder.processing.deduplicator import Deduplicator
from aiembedder.utils.errors import ProcessingError

# Test Text Cleaner
def test_text_cleaner():
    """Test text cleaner."""
    cleaner = TextCleaner()
    
    # Test basic cleaning
    text = "Hello, World!  This is a test."
    cleaned = cleaner.clean(text, "light")
    assert cleaned == "hello world this is a test"
    
    # Test medium cleaning
    text = "Hello123, World! This is a test."
    cleaned = cleaner.clean(text, "medium")
    assert "123" not in cleaned
    assert len(cleaned.split()) == 5
    
    # Test aggressive cleaning
    text = "The quick brown fox jumps over the lazy dog."
    cleaned = cleaner.clean(text, "aggressive")
    assert "the" not in cleaned  # Stopword removed
    assert len(cleaned.split()) < 9  # Some words removed
    
    # Test invalid cleaning level
    with pytest.raises(ProcessingError):
        cleaner.clean(text, "invalid")
    
    # Test cleaning levels
    assert "light" in cleaner.get_cleaning_levels()
    assert "medium" in cleaner.get_cleaning_levels()
    assert "aggressive" in cleaner.get_cleaning_levels()

# Test Text Chunker
def test_text_chunker():
    """Test text chunker."""
    chunker = TextChunker()
    
    # Test basic chunking
    text = "This is sentence one. This is sentence two. This is sentence three."
    chunks = chunker.chunk(text, chunk_size=10, chunk_overlap=2)
    assert len(chunks) > 1
    assert all(len(chunk.split()) <= 10 for chunk in chunks)
    
    # Test chunk overlap
    text = "This is a longer text that should be split into multiple chunks with overlap."
    chunks = chunker.chunk(text, chunk_size=5, chunk_overlap=2)
    assert len(chunks) > 1
    
    # Test invalid parameters
    with pytest.raises(ProcessingError):
        chunker.chunk(text, chunk_size=0)
    with pytest.raises(ProcessingError):
        chunker.chunk(text, chunk_size=5, chunk_overlap=6)
    
    # Test token counting
    text = "This is a test sentence."
    assert chunker.get_token_count(text) == 5
    
    # Test sentence counting
    text = "This is sentence one. This is sentence two."
    assert chunker.get_sentence_count(text) == 2

# Test Deduplicator
def test_deduplicator():
    """Test deduplicator."""
    deduplicator = Deduplicator(use_gpu=False)  # Use CPU for testing
    
    # Test basic deduplication
    chunks = [
        "This is a test sentence.",
        "This is a test sentence.",  # Duplicate
        "This is a different sentence.",
        "This is a test sentence.",  # Duplicate
    ]
    unique_chunks = deduplicator.deduplicate(chunks, threshold=0.95)
    assert len(unique_chunks) < len(chunks)
    
    # Test similarity calculation
    text1 = "This is a test sentence."
    text2 = "This is a test sentence."
    text3 = "This is a completely different sentence."
    
    similarity1 = deduplicator.get_similarity(text1, text2)
    similarity2 = deduplicator.get_similarity(text1, text3)
    
    assert similarity1 > 0.9  # Very similar
    assert similarity2 < 0.5  # Not similar
    
    # Test duplicate finding
    chunks = [
        "This is a test sentence.",
        "This is a test sentence.",  # Duplicate
        "This is a different sentence.",
        "This is a test sentence.",  # Duplicate
    ]
    duplicates = deduplicator.find_duplicates(chunks, threshold=0.95)
    assert len(duplicates) > 0
    
    # Test invalid threshold
    with pytest.raises(ProcessingError):
        deduplicator.deduplicate(chunks, threshold=1.5)
    
    # Test empty input
    assert deduplicator.deduplicate([]) == []
    assert deduplicator.find_duplicates([]) == [] 