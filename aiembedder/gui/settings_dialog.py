"""
Settings dialog for AIEmbedder GUI.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Optional, Dict, Any
from pathlib import Path

from aiembedder.utils.config import Config

class SettingsDialog:
    """Settings dialog for configuring application settings."""
    
    def __init__(
        self,
        parent: tk.Tk,
        config: Config
    ):
        """Initialize settings dialog.
        
        Args:
            parent: Parent window
            config: Configuration instance
        """
        self.parent = parent
        self.config = config
        self.result = False
        
        self.create_dialog()
    
    def create_dialog(self):
        """Create settings dialog."""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Settings")
        self.dialog.geometry("500x400")
        self.dialog.minsize(400, 300)
        self.dialog.resizable(True, True)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.parent.winfo_width() - width) // 2 + self.parent.winfo_x()
        y = (self.parent.winfo_height() - height) // 2 + self.parent.winfo_y()
        self.dialog.geometry(f"+{x}+{y}")
        
        self.create_widgets()
        self.load_settings()
        
        # Make dialog modal
        self.dialog.protocol("WM_DELETE_WINDOW", self.on_cancel)
        self.dialog.wait_window()
    
    def create_widgets(self):
        """Create dialog widgets."""
        # Main frame
        self.main_frame = ttk.Frame(self.dialog, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Notebook for different settings sections
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Processing settings tab
        self.processing_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.processing_frame, text="Processing")
        
        # Database settings tab
        self.database_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.database_frame, text="Database")
        
        # GUI settings tab
        self.gui_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.gui_frame, text="Interface")
        
        # Advanced settings tab
        self.advanced_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.advanced_frame, text="Advanced")
        
        # Processing settings
        self.create_processing_settings()
        
        # Database settings
        self.create_database_settings()
        
        # GUI settings
        self.create_gui_settings()
        
        # Advanced settings
        self.create_advanced_settings()
        
        # Button frame
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(fill=tk.X)
        
        self.save_button = ttk.Button(self.button_frame, text="Save", command=self.on_save)
        self.save_button.pack(side=tk.RIGHT)
        
        self.cancel_button = ttk.Button(self.button_frame, text="Cancel", command=self.on_cancel)
        self.cancel_button.pack(side=tk.RIGHT, padx=5)
    
    def create_processing_settings(self):
        """Create processing settings tab."""
        # Default cleaning level
        self.clean_frame = ttk.Frame(self.processing_frame)
        self.clean_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.clean_label = ttk.Label(self.clean_frame, text="Default cleaning level:")
        self.clean_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.clean_var = tk.StringVar(value="medium")
        self.clean_combo = ttk.Combobox(self.clean_frame, textvariable=self.clean_var)
        self.clean_combo["values"] = ("light", "medium", "aggressive")
        self.clean_combo.state(["readonly"])
        self.clean_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Default chunk size
        self.chunk_frame = ttk.Frame(self.processing_frame)
        self.chunk_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.chunk_label = ttk.Label(self.chunk_frame, text="Default chunk size:")
        self.chunk_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.chunk_var = tk.IntVar(value=400)
        self.chunk_entry = ttk.Spinbox(self.chunk_frame, from_=50, to=1000, increment=50, textvariable=self.chunk_var)
        self.chunk_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Default chunk overlap
        self.overlap_frame = ttk.Frame(self.processing_frame)
        self.overlap_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.overlap_label = ttk.Label(self.overlap_frame, text="Default chunk overlap:")
        self.overlap_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.overlap_var = tk.IntVar(value=50)
        self.overlap_entry = ttk.Spinbox(self.overlap_frame, from_=0, to=500, increment=10, textvariable=self.overlap_var)
        self.overlap_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Default similarity threshold
        self.similarity_frame = ttk.Frame(self.processing_frame)
        self.similarity_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.similarity_label = ttk.Label(self.similarity_frame, text="Default similarity threshold:")
        self.similarity_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.similarity_var = tk.DoubleVar(value=0.95)
        self.similarity_entry = ttk.Spinbox(self.similarity_frame, from_=0.5, to=1.0, increment=0.01, textvariable=self.similarity_var)
        self.similarity_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Chunks directory
        self.chunks_dir_frame = ttk.Frame(self.processing_frame)
        self.chunks_dir_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.chunks_dir_label = ttk.Label(self.chunks_dir_frame, text="Chunks directory:")
        self.chunks_dir_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.chunks_dir_var = tk.StringVar(value="~/.aiembedder/chunks")
        self.chunks_dir_entry = ttk.Entry(self.chunks_dir_frame, textvariable=self.chunks_dir_var)
        self.chunks_dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.chunks_dir_button = ttk.Button(self.chunks_dir_frame, text="Browse", command=self.browse_chunks_dir)
        self.chunks_dir_button.pack(side=tk.LEFT, padx=(5, 0))
        
        # Use GPU
        self.gpu_frame = ttk.Frame(self.processing_frame)
        self.gpu_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.gpu_var = tk.BooleanVar(value=True)
        self.gpu_check = ttk.Checkbutton(self.gpu_frame, text="Use GPU for processing (if available)", variable=self.gpu_var)
        self.gpu_check.pack(anchor=tk.W)
        
        # GPT4All optimization
        self.gpt4all_frame = ttk.Frame(self.processing_frame)
        self.gpt4all_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.gpt4all_optimize_var = tk.BooleanVar(value=True)
        self.gpt4all_check = ttk.Checkbutton(
            self.gpt4all_frame, 
            text="Optimize chunks for GPT4All embeddings", 
            variable=self.gpt4all_optimize_var
        )
        self.gpt4all_check.pack(anchor=tk.W)
        
        # GPT4All info 
        self.gpt4all_info_frame = ttk.Frame(self.processing_frame)
        self.gpt4all_info_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.gpt4all_info = ttk.Label(
            self.gpt4all_info_frame, 
            text="This will enhance chunks with additional context and normalize text to improve GPT4All embedding precision.",
            wraplength=400,
            justify=tk.LEFT
        )
        self.gpt4all_info.pack(anchor=tk.W, padx=(20, 0))
    
    def create_database_settings(self):
        """Create database settings tab."""
        # Collection name
        self.collection_frame = ttk.Frame(self.database_frame)
        self.collection_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.collection_label = ttk.Label(self.collection_frame, text="Collection name:")
        self.collection_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.collection_var = tk.StringVar(value="aiembedder")
        self.collection_entry = ttk.Entry(self.collection_frame, textvariable=self.collection_var)
        self.collection_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Database directory
        self.db_dir_frame = ttk.Frame(self.database_frame)
        self.db_dir_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.db_dir_label = ttk.Label(self.db_dir_frame, text="Database directory:")
        self.db_dir_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.db_dir_var = tk.StringVar(value="~/.aiembedder/db")
        self.db_dir_entry = ttk.Entry(self.db_dir_frame, textvariable=self.db_dir_var)
        self.db_dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.db_dir_button = ttk.Button(self.db_dir_frame, text="Browse", command=self.browse_db_dir)
        self.db_dir_button.pack(side=tk.LEFT, padx=(5, 0))
        
        # Search results limit
        self.limit_frame = ttk.Frame(self.database_frame)
        self.limit_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.limit_label = ttk.Label(self.limit_frame, text="Default search results limit:")
        self.limit_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.limit_var = tk.IntVar(value=5)
        self.limit_entry = ttk.Spinbox(self.limit_frame, from_=1, to=100, increment=1, textvariable=self.limit_var)
        self.limit_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def create_gui_settings(self):
        """Create GUI settings tab."""
        # Window title
        self.title_frame = ttk.Frame(self.gui_frame)
        self.title_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.title_label = ttk.Label(self.title_frame, text="Window title:")
        self.title_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.title_var = tk.StringVar(value="AIEmbedder")
        self.title_entry = ttk.Entry(self.title_frame, textvariable=self.title_var)
        self.title_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Theme
        self.theme_frame = ttk.Frame(self.gui_frame)
        self.theme_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.theme_label = ttk.Label(self.theme_frame, text="Theme:")
        self.theme_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.theme_var = tk.StringVar(value="default")
        self.theme_combo = ttk.Combobox(self.theme_frame, textvariable=self.theme_var)
        self.theme_combo["values"] = ("default", "light", "dark")
        self.theme_combo.state(["readonly"])
        self.theme_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Log level
        self.log_level_frame = ttk.Frame(self.gui_frame)
        self.log_level_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.log_level_label = ttk.Label(self.log_level_frame, text="Log level:")
        self.log_level_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.log_level_var = tk.StringVar(value="INFO")
        self.log_level_combo = ttk.Combobox(self.log_level_frame, textvariable=self.log_level_var)
        self.log_level_combo["values"] = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
        self.log_level_combo.state(["readonly"])
        self.log_level_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def create_advanced_settings(self):
        """Create advanced settings tab."""
        # Log directory
        self.log_dir_frame = ttk.Frame(self.advanced_frame)
        self.log_dir_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.log_dir_label = ttk.Label(self.log_dir_frame, text="Log directory:")
        self.log_dir_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.log_dir_var = tk.StringVar(value="~/.aiembedder/logs")
        self.log_dir_entry = ttk.Entry(self.log_dir_frame, textvariable=self.log_dir_var)
        self.log_dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.log_dir_button = ttk.Button(self.log_dir_frame, text="Browse", command=self.browse_log_dir)
        self.log_dir_button.pack(side=tk.LEFT, padx=(5, 0))
        
        # Model name
        self.model_frame = ttk.Frame(self.advanced_frame)
        self.model_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.model_label = ttk.Label(self.model_frame, text="Embedding model:")
        self.model_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.model_var = tk.StringVar(value="all-MiniLM-L6-v2")
        self.model_entry = ttk.Entry(self.model_frame, textvariable=self.model_var)
        self.model_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def load_settings(self):
        """Load settings from configuration."""
        # Processing settings
        self.clean_var.set(self.config.get("processing", "cleaning_level", "medium"))
        self.chunk_var.set(self.config.get("processing", "chunk_size", 400))
        self.overlap_var.set(self.config.get("processing", "chunk_overlap", 50))
        self.similarity_var.set(self.config.get("processing", "dedup_threshold", 0.95))
        self.chunks_dir_var.set(self.config.get("processing", "chunks_directory", "~/.aiembedder/chunks"))
        self.gpu_var.set(self.config.get("processing", "use_gpu", True))
        self.gpt4all_optimize_var.set(self.config.get("processing", "optimize_for_gpt4all", True))
        
        # Database settings
        self.collection_var.set(self.config.get("database", "collection_name", "aiembedder"))
        self.db_dir_var.set(self.config.get("database", "persist_directory", "~/.aiembedder/db"))
        self.limit_var.set(self.config.get("database", "search_limit", 5))
        
        # GUI settings
        self.title_var.set(self.config.get("gui", "window_title", "AIEmbedder"))
        self.theme_var.set(self.config.get("gui", "theme", "default"))
        self.log_level_var.set(self.config.get("gui", "log_level", "INFO"))
        
        # Advanced settings
        self.log_dir_var.set(self.config.get("gui", "log_directory", "~/.aiembedder/logs"))
        self.model_var.set(self.config.get("database", "embedding_model", "all-MiniLM-L6-v2"))
    
    def save_settings(self):
        """Save settings to configuration."""
        # Processing settings
        self.config.set("processing", "cleaning_level", self.clean_var.get())
        self.config.set("processing", "chunk_size", self.chunk_var.get())
        self.config.set("processing", "chunk_overlap", self.overlap_var.get())
        self.config.set("processing", "dedup_threshold", self.similarity_var.get())
        
        # Explicitly ensure chunks directory is set correctly
        chunks_dir = self.chunks_dir_var.get()
        if not chunks_dir:
            chunks_dir = "~/.aiembedder/chunks"  # Default if empty
        self.config.set("processing", "chunks_directory", chunks_dir)
        
        self.config.set("processing", "use_gpu", self.gpu_var.get())
        self.config.set("processing", "optimize_for_gpt4all", self.gpt4all_optimize_var.get())
        
        # Database settings
        self.config.set("database", "collection_name", self.collection_var.get())
        self.config.set("database", "persist_directory", self.db_dir_var.get())
        self.config.set("database", "search_limit", self.limit_var.get())
        
        # GUI settings
        self.config.set("gui", "window_title", self.title_var.get())
        self.config.set("gui", "theme", self.theme_var.get())
        self.config.set("gui", "log_level", self.log_level_var.get())
        
        # Advanced settings
        self.config.set("gui", "log_directory", self.log_dir_var.get())
        self.config.set("database", "embedding_model", self.model_var.get())
        
        # Save configuration to file
        self.config.save()
    
    def browse_db_dir(self):
        """Browse for database directory."""
        directory = filedialog.askdirectory(
            title="Select Database Directory",
            initialdir=self.db_dir_var.get().replace("~", str(Path.home()))
        )
        
        if directory:
            self.db_dir_var.set(directory)
    
    def browse_log_dir(self):
        """Browse for log directory."""
        directory = filedialog.askdirectory(
            title="Select Log Directory",
            initialdir=self.log_dir_var.get().replace("~", str(Path.home()))
        )
        
        if directory:
            self.log_dir_var.set(directory)
    
    def browse_chunks_dir(self):
        """Browse for chunks directory."""
        directory = filedialog.askdirectory(
            title="Select Chunks Directory",
            initialdir=self.chunks_dir_var.get().replace("~", str(Path.home()))
        )
        
        if directory:
            self.chunks_dir_var.set(directory)
    
    def on_save(self):
        """Handle save button click."""
        try:
            # Validate settings
            chunk_size = self.chunk_var.get()
            chunk_overlap = self.overlap_var.get()
            
            if chunk_overlap >= chunk_size:
                messagebox.showerror("Invalid Settings", "Chunk overlap must be less than chunk size.")
                return
            
            # Save settings
            self.save_settings()
            
            # Set result and close dialog
            self.result = True
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")
    
    def on_cancel(self):
        """Handle cancel button click."""
        self.result = False
        self.dialog.destroy() 