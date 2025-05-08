"""
Tests for GUI components.
"""

import pytest
import tkinter as tk
from unittest.mock import MagicMock, patch

from aiembedder.utils.config import Config
from aiembedder.utils.logging import Logger
from aiembedder.utils.progress import ProgressTracker, ProgressState
from aiembedder.gui.settings_dialog import SettingsDialog
from aiembedder.gui.progress_panel import ProgressPanel
from aiembedder.gui.log_panel import LogPanel, LogHandler

# Skip tests if no display available
pytestmark = pytest.mark.skipif("not hasattr(tk, '_default_root')", reason="No display available")

class TestLogComponents:
    """Test log components."""
    
    def test_log_handler(self):
        """Test log handler."""
        # Create mock callback
        callback = MagicMock()
        
        # Create handler with mock callback
        handler = LogHandler(callback)
        
        # Create log record
        record = MagicMock()
        record.getMessage.return_value = "Test message"
        record.levelname = "INFO"
        
        # Mock format method
        handler.format = MagicMock(return_value="Formatted log message")
        
        # Emit record
        handler.emit(record)
        
        # Verify callback was called with formatted message
        handler.format.assert_called_once_with(record)
        callback.assert_called_once_with("Formatted log message")
    
    def test_get_tag_for_entry(self, monkeypatch):
        """Test getting tag for log entry."""
        # Mock Logger and ttk.Frame
        logger = MagicMock()
        parent = MagicMock()
        
        # Create log panel
        with patch("tkinter.scrolledtext.ScrolledText", MagicMock()):
            log_panel = LogPanel(parent, logger)
        
        # Test tag for different log levels
        assert log_panel.get_tag_for_entry("2022-01-01 [DEBUG] test: message") == "debug"
        assert log_panel.get_tag_for_entry("2022-01-01 [INFO] test: message") == "info"
        assert log_panel.get_tag_for_entry("2022-01-01 [WARNING] test: message") == "warning"
        assert log_panel.get_tag_for_entry("2022-01-01 [ERROR] test: message") == "error"
        assert log_panel.get_tag_for_entry("2022-01-01 [CRITICAL] test: message") == "critical"
        assert log_panel.get_tag_for_entry("Other message") == "default"

class TestProgressComponents:
    """Test progress components."""
    
    def test_format_time_delta(self):
        """Test formatting time delta."""
        # Mock ProgressTracker and ttk.Frame
        progress_tracker = MagicMock()
        parent = MagicMock()
        
        # Create progress panel
        progress_panel = ProgressPanel(parent, progress_tracker)
        
        # Test different time formats
        assert progress_panel.format_time_delta(10.5) == "10.5s"
        assert progress_panel.format_time_delta(65) == "1m 5s"
        assert progress_panel.format_time_delta(3665) == "1h 1m"
    
    def test_format_task_status(self):
        """Test formatting task status."""
        # Mock ProgressTracker and ttk.Frame
        progress_tracker = MagicMock()
        parent = MagicMock()
        
        # Create progress panel
        progress_panel = ProgressPanel(parent, progress_tracker)
        
        # Mock format_time_delta
        progress_panel.format_time_delta = MagicMock(return_value="10.5s")
        
        # Create mock progress state for completed task
        completed_state = MagicMock()
        completed_state.is_complete = True
        completed_state.elapsed_time = 10.5
        
        # Create mock progress state for in-progress task
        in_progress_state = MagicMock()
        in_progress_state.is_complete = False
        in_progress_state.status = "Processing"
        in_progress_state.percentage = 50.0
        
        # Test formatting completed task
        assert progress_panel.format_task_status(completed_state) == "Completed in 10.5s"
        progress_panel.format_time_delta.assert_called_once_with(10.5)
        
        # Test formatting in-progress task
        assert progress_panel.format_task_status(in_progress_state) == "Processing - 50.0%"

class TestSettingsDialog:
    """Test settings dialog."""
    
    def test_config_loading(self, monkeypatch):
        """Test loading config values into settings dialog."""
        # Mock Config
        config = MagicMock()
        config.get.side_effect = lambda key, default: {
            "processing.cleaning_level": "aggressive",
            "processing.chunk_size": 200,
            "processing.chunk_overlap": 30,
            "processing.similarity_threshold": 0.9,
            "processing.use_gpu": False,
            "database.collection_name": "test_collection",
            "database.persist_directory": "/test/db",
            "database.default_limit": 10,
            "gui.window_title": "Test Title",
            "gui.theme": "dark",
            "gui.log_level": "DEBUG",
            "advanced.log_directory": "/test/logs",
            "advanced.model_name": "test-model"
        }.get(key, default)
        
        # Mock tkinter components
        with patch("tkinter.Toplevel", MagicMock()) as mock_toplevel:
            with patch("tkinter.StringVar") as mock_string_var:
                with patch("tkinter.IntVar") as mock_int_var:
                    with patch("tkinter.DoubleVar") as mock_double_var:
                        with patch("tkinter.BooleanVar") as mock_boolean_var:
                            # Mock wait_window to prevent blocking
                            mock_toplevel.return_value.wait_window = MagicMock()
                            
                            # Create settings dialog
                            dialog = SettingsDialog(MagicMock(), config)
                            
                            # Verify config.get was called with correct keys
                            config.get.assert_any_call("processing.cleaning_level", "medium")
                            config.get.assert_any_call("processing.chunk_size", 400)
                            config.get.assert_any_call("processing.chunk_overlap", 50)
                            config.get.assert_any_call("processing.similarity_threshold", 0.95)
                            config.get.assert_any_call("processing.use_gpu", True)
                            config.get.assert_any_call("database.collection_name", "aiembedder")
                            config.get.assert_any_call("database.persist_directory", "~/.aiembedder/db")
                            config.get.assert_any_call("database.default_limit", 5)
                            config.get.assert_any_call("gui.window_title", "AIEmbedder")
                            config.get.assert_any_call("gui.theme", "default")
                            config.get.assert_any_call("gui.log_level", "INFO")
                            config.get.assert_any_call("advanced.log_directory", "~/.aiembedder/logs")
                            config.get.assert_any_call("advanced.model_name", "all-MiniLM-L6-v2") 