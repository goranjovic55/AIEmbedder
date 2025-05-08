"""
Log panel for displaying application logs.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Optional, Dict, List, Any, Callable
import logging
import queue
import time

from aiembedder.utils.logging import Logger

class LogHandler(logging.Handler):
    """Custom log handler for GUI log panel."""
    
    def __init__(self, callback: Callable[[str], None]):
        """Initialize log handler.
        
        Args:
            callback: Callback function for new log entries
        """
        super().__init__()
        self.callback = callback
    
    def emit(self, record):
        """Emit a log record.
        
        Args:
            record: Log record
        """
        log_entry = self.format(record)
        self.callback(log_entry)

class LogPanel:
    """Log panel for displaying application logs."""
    
    def __init__(
        self,
        parent: ttk.Frame,
        logger: Logger
    ):
        """Initialize log panel.
        
        Args:
            parent: Parent frame
            logger: Logger instance
        """
        self.parent = parent
        self.logger = logger
        self.log_queue = queue.Queue()
        self.level_var = tk.StringVar(value="INFO")
        self.should_auto_scroll = tk.BooleanVar(value=True)
        
        self.create_widgets()
        self.setup_layout()
        self.setup_handler()
        
        # Start periodic log update
        self.update_logs()
    
    def create_widgets(self):
        """Create panel widgets."""
        # Main frame
        self.main_frame = ttk.Frame(self.parent, padding="10")
        
        # Log options frame
        self.options_frame = ttk.Frame(self.main_frame)
        
        # Log level filter
        self.level_label = ttk.Label(self.options_frame, text="Log level:")
        self.level_combo = ttk.Combobox(self.options_frame, textvariable=self.level_var)
        self.level_combo["values"] = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
        self.level_combo.state(["readonly"])
        self.level_combo.bind("<<ComboboxSelected>>", self.on_level_change)
        
        # Auto-scroll option
        self.auto_scroll_check = ttk.Checkbutton(
            self.options_frame,
            text="Auto-scroll",
            variable=self.should_auto_scroll
        )
        
        # Clear logs button
        self.clear_button = ttk.Button(self.options_frame, text="Clear Logs", command=self.clear_logs)
        
        # Log display
        self.log_text = scrolledtext.ScrolledText(
            self.main_frame,
            wrap=tk.WORD,
            width=80,
            height=20,
            background="#f5f5f5",
            font=("Courier", 9)
        )
        self.log_text.config(state=tk.DISABLED)
        
        # Status bar
        self.status_bar = ttk.Label(self.main_frame, text="0 log entries")
    
    def setup_layout(self):
        """Set up panel layout."""
        # Main frame
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Log options frame
        self.options_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Log level filter
        self.level_label.pack(side=tk.LEFT, padx=(0, 5))
        self.level_combo.pack(side=tk.LEFT, padx=(0, 10))
        
        # Auto-scroll option
        self.auto_scroll_check.pack(side=tk.LEFT, padx=(0, 10))
        
        # Clear logs button
        self.clear_button.pack(side=tk.RIGHT)
        
        # Log display
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        # Status bar
        self.status_bar.pack(side=tk.LEFT)
    
    def setup_handler(self):
        """Set up log handler."""
        # Create custom log handler
        self.handler = LogHandler(self.on_log_entry)
        self.handler.setLevel(logging.DEBUG)
        
        # Format log entries
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        self.handler.setFormatter(formatter)
        
        # Add handler to logger
        root_logger = logging.getLogger()
        root_logger.addHandler(self.handler)
    
    def on_log_entry(self, log_entry: str):
        """Handle new log entry.
        
        Args:
            log_entry: Log entry text
        """
        # Add log entry to queue
        self.log_queue.put(log_entry)
    
    def update_logs(self):
        """Update log display from queue."""
        # Process all available log entries
        while not self.log_queue.empty():
            try:
                log_entry = self.log_queue.get_nowait()
                self.add_log_entry(log_entry)
            except queue.Empty:
                break
        
        # Schedule next update
        self.parent.after(100, self.update_logs)
    
    def add_log_entry(self, log_entry: str):
        """Add log entry to display.
        
        Args:
            log_entry: Log entry text
        """
        # Check if entry matches current filter
        current_level = self.level_var.get()
        if current_level in log_entry:
            # Enable text widget
            self.log_text.config(state=tk.NORMAL)
            
            # Add entry with appropriate tag
            tag = self.get_tag_for_entry(log_entry)
            self.log_text.insert(tk.END, log_entry + "\n", tag)
            
            # Auto-scroll if enabled
            if self.should_auto_scroll.get():
                self.log_text.see(tk.END)
            
            # Disable text widget
            self.log_text.config(state=tk.DISABLED)
        
        # Update status bar
        self.update_status()
    
    def get_tag_for_entry(self, log_entry: str) -> str:
        """Get the appropriate tag for a log entry.
        
        Args:
            log_entry: Log entry text
            
        Returns:
            Tag name
        """
        if "DEBUG" in log_entry:
            return "debug"
        elif "INFO" in log_entry:
            return "info"
        elif "WARNING" in log_entry:
            return "warning"
        elif "ERROR" in log_entry:
            return "error"
        elif "CRITICAL" in log_entry:
            return "critical"
        else:
            return "default"
    
    def on_level_change(self, event):
        """Handle log level change.
        
        Args:
            event: Combobox event
        """
        self.clear_logs()
    
    def clear_logs(self):
        """Clear log display."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        
        # Update status bar
        self.update_status()
    
    def update_status(self):
        """Update status bar."""
        # Count log entries
        log_content = self.log_text.get(1.0, tk.END)
        entry_count = log_content.count("\n") - 1  # Subtract empty line at end
        
        # Update status text
        self.status_bar.config(text=f"{entry_count} log {'entry' if entry_count == 1 else 'entries'}")
    
    def set_colors(self):
        """Set colors for log levels."""
        self.log_text.tag_configure("debug", foreground="gray")
        self.log_text.tag_configure("info", foreground="black")
        self.log_text.tag_configure("warning", foreground="orange")
        self.log_text.tag_configure("error", foreground="red")
        self.log_text.tag_configure("critical", foreground="red", background="yellow")
        self.log_text.tag_configure("default", foreground="black") 