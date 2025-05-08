"""
Tests for utility modules.
"""

import os
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from aiembedder.utils.config import Config
from aiembedder.utils.logging import Logger
from aiembedder.utils.errors import (
    AIEmbedderError,
    FileAccessError,
    ProcessingError,
    DatabaseError,
    ConfigurationError,
    ValidationError,
    get_error_message,
    raise_error
)
from aiembedder.utils.progress import ProgressState, ProgressTracker

# Test Config
def test_config_initialization():
    """Test Config initialization."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = os.path.join(temp_dir, "config.json")
        config = Config(config_path)
        
        # Test default values
        assert config.get("processing", "cleaning_level") == "medium"
        assert config.get("processing", "chunk_size") == 400
        assert config.get("database", "collection_name") == "localdocs_collection"
        
        # Test setting values
        config.set("processing", "cleaning_level", "aggressive")
        assert config.get("processing", "cleaning_level") == "aggressive"
        
        # Test updating multiple values
        config.update({
            "processing": {
                "chunk_size": 300,
                "chunk_overlap": 75
            }
        })
        assert config.get("processing", "chunk_size") == 300
        assert config.get("processing", "chunk_overlap") == 75

# Test Logger
def test_logger_initialization():
    """Test Logger initialization."""
    with tempfile.TemporaryDirectory() as temp_dir:
        logger = Logger(temp_dir)
        
        # Test logging levels
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        logger.critical("Critical message")
        
        # Test log file creation
        log_files = list(Path(temp_dir).glob("*.log"))
        assert len(log_files) > 0

# Test Error Handling
def test_error_handling():
    """Test error handling."""
    # Test error codes
    assert get_error_message("FILE_001") == "File not found"
    assert get_error_message("UNKNOWN") == "Unknown error"
    
    # Test error raising
    with pytest.raises(FileAccessError):
        raise_error("FILE_001")
    
    with pytest.raises(ProcessingError):
        raise_error("PROC_001")
    
    with pytest.raises(DatabaseError):
        raise_error("DB_001")
    
    with pytest.raises(ConfigurationError):
        raise_error("CONF_001")
    
    with pytest.raises(ValidationError):
        raise_error("VAL_001")
    
    with pytest.raises(AIEmbedderError):
        raise_error("UNKNOWN")

# Test Progress Tracking
def test_progress_tracking():
    """Test progress tracking."""
    tracker = ProgressTracker()
    
    # Test task creation
    tracker.start_task("test_task", 100, "Testing...")
    state = tracker.get_task("test_task")
    assert state is not None
    assert state.total == 100
    assert state.current == 0
    assert state.status == "Testing..."
    
    # Test progress update
    tracker.update_task("test_task", 50, "Halfway...")
    state = tracker.get_task("test_task")
    assert state.current == 50
    assert state.status == "Halfway..."
    assert state.percentage == 50.0
    
    # Test task completion
    tracker.complete_task("test_task", "Done!")
    state = tracker.get_task("test_task")
    assert state.is_complete
    assert state.status == "Done!"
    
    # Test error handling
    tracker.add_error("test_task", "Test error")
    state = tracker.get_task("test_task")
    assert "Test error" in state.errors

def test_progress_callbacks():
    """Test progress callbacks."""
    tracker = ProgressTracker()
    callback_called = False
    
    def test_callback(state: ProgressState):
        nonlocal callback_called
        callback_called = True
        assert state.total == 100
        assert state.current == 50
    
    # Register callback
    tracker.register_callback("test_task", test_callback)
    
    # Start and update task
    tracker.start_task("test_task", 100)
    tracker.update_task("test_task", 50, "Testing callback...")
    
    # Verify callback was called
    assert callback_called 