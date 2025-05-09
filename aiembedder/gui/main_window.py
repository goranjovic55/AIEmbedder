"""
Main window for AIEmbedder GUI.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from pathlib import Path
from typing import Optional, List, Dict, Any, Callable
import threading
import queue
import re
from datetime import datetime

from aiembedder.utils.config import Config
from aiembedder.utils.logging import Logger
from aiembedder.utils.progress import ProgressTracker
from aiembedder.utils.errors import AIEmbedderError, ProcessingError
from aiembedder.gui.settings_dialog import SettingsDialog
from aiembedder.gui.progress_panel import ProgressPanel
from aiembedder.gui.log_panel import LogPanel
from aiembedder.processing.pipeline import TextProcessingPipeline
from aiembedder.vector.generator import VectorGenerator
from aiembedder.vector.database import VectorDatabase
from aiembedder.processors.processor_factory import ProcessorFactory

class MainWindow:
    """Main window for AIEmbedder GUI."""
    
    def __init__(
        self,
        config: Optional[Config] = None,
        logger: Optional[Logger] = None,
        progress_tracker: Optional[ProgressTracker] = None
    ):
        """Initialize main window.
        
        Args:
            config: Configuration instance
            logger: Logger instance
            progress_tracker: Progress tracker instance
        """
        self.config = config or Config()
        self.logger = logger or Logger()
        self.progress_tracker = progress_tracker or ProgressTracker()
        
        self.root = tk.Tk()
        self.root.title("AIEmbedder")
        self.root.geometry("900x650")
        self.root.minsize(800, 600)
        
        # Initialize processing components
        self.processor_factory = ProcessorFactory(logger=self.logger)
        
        # Initialize event handling
        self.processing_thread = None
        self.stop_processing_flag = threading.Event()
        self.processing_queue = queue.Queue()
        
        self.setup_styles()
        self.create_menu()
        self.create_widgets()
        self.setup_layout()
        
        # Start queue processing
        self.process_queue()
        
        self.logger.info("Initialized main window")
    
    def setup_styles(self):
        """Set up TTK styles."""
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, relief="flat", background="#ccc")
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TLabel", background="#f0f0f0", font=("Helvetica", 10))
        self.style.configure("Header.TLabel", font=("Helvetica", 12, "bold"))
        self.style.configure("TNotebook", tabposition="n")
    
    def create_menu(self):
        """Create menu bar."""
        self.menu_bar = tk.Menu(self.root)
        
        # File menu
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="Open File", command=self.open_file)
        self.file_menu.add_command(label="Open Directory", command=self.open_directory)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.exit_app)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        
        # Settings menu
        self.settings_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.settings_menu.add_command(label="Preferences", command=self.open_settings)
        self.menu_bar.add_cascade(label="Settings", menu=self.settings_menu)
        
        # Database menu
        self.database_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.database_menu.add_command(label="Search Database", command=self.open_search)
        self.database_menu.add_command(label="Reset Database", command=self.reset_database)
        self.menu_bar.add_cascade(label="Database", menu=self.database_menu)
        
        # Tools menu
        self.tools_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.tools_menu.add_command(label="Show Processing Errors", command=self.show_errors)
        self.tools_menu.add_command(label="Check Chunks Folder", command=self.check_chunks_folder)
        self.menu_bar.add_cascade(label="Tools", menu=self.tools_menu)
        
        # Help menu
        self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.help_menu.add_command(label="About", command=self.show_about)
        self.help_menu.add_command(label="Help", command=self.show_help)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)
        
        self.root.config(menu=self.menu_bar)
    
    def create_widgets(self):
        """Create main widgets."""
        # Main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        
        # Header
        self.header_label = ttk.Label(
            self.main_frame, 
            text="AIEmbedder",
            font=("Helvetica", 16, "bold")
        )
        
        # Description
        self.description = ttk.Label(
            self.main_frame,
            text="Embed documents into vector databases for semantic search.",
            wraplength=400
        )
        
        # File panel
        self.file_frame = ttk.LabelFrame(self.main_frame, text="Files", padding="10")
        
        # File listbox
        self.file_list_frame = ttk.Frame(self.file_frame)
        self.file_listbox = tk.Listbox(self.file_list_frame, selectmode=tk.EXTENDED, height=5)
        self.file_scrollbar = ttk.Scrollbar(self.file_list_frame, command=self.file_listbox.yview)
        self.file_listbox.config(yscrollcommand=self.file_scrollbar.set)
        
        # File buttons
        self.file_button_frame = ttk.Frame(self.file_frame)
        self.add_file_button = ttk.Button(self.file_button_frame, text="Add File", command=self.open_file)
        self.add_dir_button = ttk.Button(self.file_button_frame, text="Add Directory", command=self.open_directory)
        self.remove_button = ttk.Button(self.file_button_frame, text="Remove Selected", command=self.remove_selected)
        self.clear_button = ttk.Button(self.file_button_frame, text="Clear All", command=self.clear_files)
        
        # Processing options panel
        self.options_frame = ttk.LabelFrame(self.main_frame, text="Processing Options", padding="10")
        
        # Cleaning level
        self.cleaning_frame = ttk.Frame(self.options_frame)
        self.cleaning_label = ttk.Label(self.cleaning_frame, text="Cleaning level:")
        self.cleaning_var = tk.StringVar(value=self.config.get("processing", "cleaning_level", "medium"))
        self.cleaning_combo = ttk.Combobox(self.cleaning_frame, textvariable=self.cleaning_var)
        self.cleaning_combo["values"] = ("light", "medium", "aggressive")
        self.cleaning_combo.state(["readonly"])
        
        # Chunk size
        self.chunk_frame = ttk.Frame(self.options_frame)
        self.chunk_label = ttk.Label(self.chunk_frame, text="Chunk size:")
        self.chunk_var = tk.IntVar(value=self.config.get("processing", "chunk_size", 400))
        self.chunk_spinbox = ttk.Spinbox(self.chunk_frame, from_=50, to=1000, increment=50, textvariable=self.chunk_var)
        
        # Chunk overlap
        self.overlap_frame = ttk.Frame(self.options_frame)
        self.overlap_label = ttk.Label(self.overlap_frame, text="Chunk overlap:")
        self.overlap_var = tk.IntVar(value=self.config.get("processing", "chunk_overlap", 50))
        self.overlap_spinbox = ttk.Spinbox(self.overlap_frame, from_=0, to=200, increment=10, textvariable=self.overlap_var)
        
        # Similarity threshold
        self.similarity_frame = ttk.Frame(self.options_frame)
        self.similarity_label = ttk.Label(self.similarity_frame, text="Similarity threshold:")
        self.similarity_var = tk.DoubleVar(value=self.config.get("processing", "dedup_threshold", 0.95))
        self.similarity_spinbox = ttk.Spinbox(self.similarity_frame, from_=0.5, to=1.0, increment=0.01, textvariable=self.similarity_var)
        
        # Action buttons
        self.action_frame = ttk.Frame(self.main_frame)
        self.process_button = ttk.Button(self.action_frame, text="Process Files", command=self.process_files)
        self.process_button.configure(state="disabled")  # Disabled until files are selected
        self.stop_button = ttk.Button(self.action_frame, text="Stop", command=self.stop_processing)
        self.stop_button.configure(state="disabled")  # Disabled until processing starts
        
        # Notebook for progress and logs
        self.notebook = ttk.Notebook(self.main_frame)
        self.progress_frame = ttk.Frame(self.notebook)
        self.log_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.progress_frame, text="Progress")
        self.notebook.add(self.log_frame, text="Logs")
        
        # Progress panel
        self.progress_panel = ProgressPanel(self.progress_frame, self.progress_tracker)
        
        # Log panel
        self.log_panel = LogPanel(self.log_frame, self.logger)
    
    def setup_layout(self):
        """Set up widget layout."""
        # Main frame
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        self.header_label.pack(pady=(0, 10))
        self.description.pack(pady=(0, 10))
        
        # File panel
        self.file_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.file_list_frame.pack(fill=tk.X, pady=(0, 5))
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.file_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.file_button_frame.pack(fill=tk.X)
        self.add_file_button.pack(side=tk.LEFT, padx=(0, 5))
        self.add_dir_button.pack(side=tk.LEFT, padx=(0, 5))
        self.remove_button.pack(side=tk.LEFT, padx=(0, 5))
        self.clear_button.pack(side=tk.LEFT)
        
        # Processing options panel
        self.options_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.cleaning_frame.pack(fill=tk.X, pady=(0, 5))
        self.cleaning_label.pack(side=tk.LEFT, padx=(0, 5))
        self.cleaning_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.chunk_frame.pack(fill=tk.X, pady=(0, 5))
        self.chunk_label.pack(side=tk.LEFT, padx=(0, 5))
        self.chunk_spinbox.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.overlap_frame.pack(fill=tk.X, pady=(0, 5))
        self.overlap_label.pack(side=tk.LEFT, padx=(0, 5))
        self.overlap_spinbox.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.similarity_frame.pack(fill=tk.X, pady=(0, 5))
        self.similarity_label.pack(side=tk.LEFT, padx=(0, 5))
        self.similarity_spinbox.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Action buttons
        self.action_frame.pack(fill=tk.X, pady=(0, 10))
        self.process_button.pack(side=tk.LEFT, padx=(0, 5))
        self.stop_button.pack(side=tk.LEFT)
        
        # Notebook
        self.notebook.pack(fill=tk.BOTH, expand=True)
    
    def run(self):
        """Run the main window."""
        self.root.protocol("WM_DELETE_WINDOW", self.exit_app)
        self.root.mainloop()
    
    def exit_app(self):
        """Exit the application."""
        if messagebox.askokcancel("Exit", "Are you sure you want to exit?"):
            self.logger.info("Exiting application")
            # Stop any running threads
            self.stop_processing_flag.set()
            if self.processing_thread and self.processing_thread.is_alive():
                self.processing_thread.join(timeout=2.0)
            self.root.destroy()
    
    def open_file(self):
        """Open file dialog."""
        filetypes = (
            ("All files", "*.*"),
            ("Text files", "*.txt"),
            ("HTML files", "*.html"),
            ("PDF files", "*.pdf"),
            ("Word files", "*.docx"),
        )
        
        filenames = filedialog.askopenfilenames(
            title="Select Files",
            filetypes=filetypes
        )
        
        if filenames:
            for filename in filenames:
                if filename not in self.file_listbox.get(0, tk.END):
                    self.file_listbox.insert(tk.END, filename)
                    self.logger.info(f"Added file: {filename}")
            
            self.update_buttons()
    
    def open_directory(self):
        """Open directory dialog."""
        directory = filedialog.askdirectory(
            title="Select Directory"
        )
        
        if directory:
            if directory not in self.file_listbox.get(0, tk.END):
                self.file_listbox.insert(tk.END, directory)
                self.logger.info(f"Added directory: {directory}")
            
            self.update_buttons()
    
    def remove_selected(self):
        """Remove selected files."""
        selected = self.file_listbox.curselection()
        for i in reversed(selected):
            self.file_listbox.delete(i)
        
        self.update_buttons()
    
    def clear_files(self):
        """Clear all files."""
        self.file_listbox.delete(0, tk.END)
        self.update_buttons()
    
    def update_buttons(self):
        """Update button states."""
        if self.file_listbox.size() > 0:
            self.process_button.configure(state="normal")
        else:
            self.process_button.configure(state="disabled")
    
    def open_settings(self):
        """Open settings dialog."""
        settings_dialog = SettingsDialog(self.root, self.config)
        if settings_dialog.result:
            self.logger.info("Settings updated")
            # Update UI with new settings
            self.cleaning_var.set(self.config.get("processing", "cleaning_level", "medium"))
            self.chunk_var.set(self.config.get("processing", "chunk_size", 400))
            self.overlap_var.set(self.config.get("processing", "chunk_overlap", 50))
            self.similarity_var.set(self.config.get("processing", "dedup_threshold", 0.95))
            
            # Ensure chunks directory exists
            chunks_dir = Path(self.config.get("processing", "chunks_directory", "~/.aiembedder/chunks")).expanduser()
            if not chunks_dir.exists():
                try:
                    chunks_dir.mkdir(parents=True, exist_ok=True)
                    self.logger.info(f"Created chunks directory: {chunks_dir}")
                except Exception as e:
                    self.logger.error(f"Error creating chunks directory: {str(e)}")
    
    def open_search(self):
        """Open search dialog."""
        from aiembedder.gui.search_dialog import SearchDialog
        search_dialog = SearchDialog(self.root, self.config, self.logger)
    
    def reset_database(self):
        """Reset the vector database."""
        if messagebox.askyesno("Reset Database", "Are you sure you want to reset the database? This will delete all stored embeddings."):
            try:
                # Create database with configured settings
                collection_name = self.config.get("database", "collection_name", "aiembedder")
                persist_directory = self.config.get("database", "persist_directory", "~/.aiembedder/db")
                use_gpu = self.config.get("processing", "use_gpu", True)
                
                db = VectorDatabase(
                    collection_name=collection_name,
                    persist_directory=persist_directory,
                    use_gpu=use_gpu,
                    logger=self.logger
                )
                
                # Reset collection
                db.reset_collection()
                
                messagebox.showinfo("Success", "Database has been reset successfully.")
                
            except Exception as e:
                self.logger.error(f"Error resetting database: {str(e)}")
                messagebox.showerror("Error", f"Failed to reset database: {str(e)}")
    
    def show_about(self):
        """Show about dialog."""
        messagebox.showinfo(
            "About AIEmbedder",
            "AIEmbedder is a tool for embedding documents into vector databases for semantic search.\n\n"
            "Version: 0.1.0\n"
            "Created by: AIEmbedder Team"
        )
    
    def show_help(self):
        """Show help dialog."""
        messagebox.showinfo(
            "AIEmbedder Help",
            "How to use AIEmbedder:\n\n"
            "1. Add files or directories using the buttons\n"
            "2. Configure processing options\n"
            "3. Click 'Process Files' to start\n"
            "4. Monitor progress in the Progress tab\n"
            "5. View logs in the Logs tab\n\n"
            "For more help, please refer to the documentation."
        )
    
    def process_files(self):
        """Process selected files."""
        try:
            # Validate inputs
            file_paths = list(self.file_listbox.get(0, tk.END))
            if not file_paths:
                messagebox.showwarning("No Files", "Please select files or directories to process.")
                return
            
            # Check if chunk overlap is less than chunk size
            chunk_size = self.chunk_var.get()
            chunk_overlap = self.overlap_var.get()
            if chunk_overlap >= chunk_size:
                messagebox.showerror("Invalid Settings", "Chunk overlap must be less than chunk size.")
                return
            
            # Create chunks directory if it doesn't exist
            # Get chunks directory directly from config dictionary
            if "processing" in self.config.config and "chunks_directory" in self.config.config["processing"]:
                chunks_dir_path = self.config.config["processing"]["chunks_directory"]
            else:
                chunks_dir_path = "~/.aiembedder/chunks"  # Use default only if not found
                # Set it in config
                self.config.set("processing", "chunks_directory", chunks_dir_path)
                self.logger.info(f"Set chunks_directory in config: {chunks_dir_path}")

            chunks_dir = Path(chunks_dir_path).expanduser()
            self.logger.info(f"Using chunks directory from config: {chunks_dir}")
            
            if not chunks_dir.exists():
                try:
                    chunks_dir.mkdir(parents=True, exist_ok=True)
                    self.logger.info(f"Created chunks directory: {chunks_dir}")
                except Exception as e:
                    self.logger.error(f"Error creating chunks directory: {str(e)}")
                    messagebox.showerror("Directory Error", f"Failed to create chunks directory: {str(e)}")
                    return
            
            # Update processing configuration
            self.config.update({
                "processing": {
                    "cleaning_level": self.cleaning_var.get(),
                    "chunk_size": chunk_size,
                    "chunk_overlap": chunk_overlap,
                    "dedup_threshold": self.similarity_var.get()
                }
            })
            
            # Update UI state
            self.process_button.configure(state="disabled")
            self.stop_button.configure(state="normal")
            self.notebook.select(0)  # Switch to Progress tab
            
            # Reset stop flag
            self.stop_processing_flag.clear()
            
            # Log start of processing
            self.logger.info(f"Starting processing of {len(file_paths)} files/directories")
            
            # Start processing in a separate thread
            self.processing_thread = threading.Thread(
                target=self._process_files_thread,
                args=(file_paths,),
                daemon=True
            )
            self.processing_thread.start()
            
        except AIEmbedderError as e:
            self.logger.error(f"Processing error: {str(e)}")
            messagebox.showerror("Processing Error", str(e))
            
            # Update UI state
            self.process_button.configure(state="normal")
            self.stop_button.configure(state="disabled")
            
        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)}")
            messagebox.showerror("Unexpected Error", f"An unexpected error occurred: {str(e)}")
            
            # Update UI state
            self.process_button.configure(state="normal")
            self.stop_button.configure(state="disabled")
    
    def _process_files_thread(self, file_paths: List[str]):
        """Process files in a separate thread.
        
        Args:
            file_paths: List of file paths to process
        """
        try:
            # Create main task
            main_task_id = self.progress_tracker.start_task(
                "main_processing",
                total=len(file_paths),
                status="Processing files"
            )
            
            # Get processing settings
            cleaning_level = self.config.get("processing", "cleaning_level", "medium")
            chunk_size = self.config.get("processing", "chunk_size", 400)
            chunk_overlap = self.config.get("processing", "chunk_overlap", 50)
            similarity_threshold = self.config.get("processing", "dedup_threshold", 0.95)
            use_gpu = self.config.get("processing", "use_gpu", True)
            optimize_for_gpt4all = self.config.get("processing", "optimize_for_gpt4all", True)
            
            # Create processing components
            pipeline = TextProcessingPipeline(
                cleaning_level=cleaning_level,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                similarity_threshold=similarity_threshold,
                use_gpu=use_gpu,
                optimize_for_gpt4all=optimize_for_gpt4all,
                progress_tracker=self.progress_tracker
            )
            
            # Create vector components
            model_name = self.config.get("database", "embedding_model", "all-MiniLM-L6-v2")
            generator = VectorGenerator(
                model_name=model_name,
                use_gpu=use_gpu,
                logger=self.logger
            )
            
            collection_name = self.config.get("database", "collection_name", "aiembedder")
            persist_directory = self.config.get("database", "persist_directory", "~/.aiembedder/db")
            db = VectorDatabase(
                collection_name=collection_name,
                persist_directory=persist_directory,
                use_gpu=use_gpu,
                logger=self.logger
            )
            
            # Process each file
            for i, file_path in enumerate(file_paths):
                if self.stop_processing_flag.is_set():
                    self.logger.info("Processing stopped by user")
                    self.progress_tracker.update_task(main_task_id, status="Stopped by user")
                    break
                
                try:
                    # Update main task progress
                    self.progress_tracker.update_task(
                        main_task_id,
                        current=i,
                        status=f"Processing {Path(file_path).name}"
                    )
                    
                    # Process file or directory
                    path = Path(file_path)
                    if path.is_file():
                        self._process_single_file(path, pipeline, generator, db)
                    elif path.is_dir():
                        self._process_directory(path, pipeline, generator, db)
                    
                except Exception as e:
                    self.logger.error(f"Error processing {file_path}: {str(e)}")
                    self.progress_tracker.add_error(main_task_id, f"Error processing {file_path}: {str(e)}")
            
            # Complete main task
            self.progress_tracker.update_task(main_task_id, current=len(file_paths), status="Completed")
            self.progress_tracker.complete_task(main_task_id)
            
            # Add completion message to queue
            if not self.stop_processing_flag.is_set():
                self.processing_queue.put(("complete", f"Successfully processed {len(file_paths)} files/directories."))
            
        except Exception as e:
            self.logger.error(f"Processing thread error: {str(e)}")
            self.processing_queue.put(("error", str(e)))
        
        finally:
            # Update UI state (via queue)
            self.processing_queue.put(("update_ui", None))
    
    def _process_single_file(self, file_path: Path, pipeline: TextProcessingPipeline, 
                            generator: VectorGenerator, db: VectorDatabase):
        """Process a single file.
        
        Args:
            file_path: File path
            pipeline: Text processing pipeline
            generator: Vector generator
            db: Vector database
        """
        try:
            self.logger.info(f"Processing file: {file_path}")
            
            # Get appropriate processor
            self.logger.info(f"Getting processor for file type: {file_path.suffix}")
            processor = self.processor_factory.get_processor(file_path)
            self.logger.info(f"Using processor: {processor.__class__.__name__}")
            
            # Extract text
            self.logger.info(f"Extracting text from file: {file_path}")
            text = processor.process(str(file_path))  # Using process() method from BaseProcessor
            text_length = len(text)
            self.logger.info(f"Extracted {text_length} characters from file: {file_path}")
            
            if text_length == 0:
                self.logger.warning(f"No text extracted from file: {file_path}")
                return
            
            # Process text
            self.logger.info(f"Processing text through pipeline, length={text_length}")
            chunks = pipeline.process_text(text, metadata={"source": str(file_path)})
            self.logger.info(f"Created {len(chunks)} chunks from file: {file_path}")
            
            if not chunks:
                self.logger.warning(f"No chunks created from file: {file_path}")
                return
            
            # Generate embeddings
            self.logger.info(f"Generating embeddings for {len(chunks)} chunks")
            chunks_with_embeddings = generator.generate_embeddings(chunks)
            self.logger.info(f"Generated embeddings for {len(chunks_with_embeddings)} chunks")
            
            if not chunks_with_embeddings:
                self.logger.warning(f"No embeddings created for chunks from file: {file_path}")
                return
            
            # Add to database
            self.logger.info(f"Adding {len(chunks_with_embeddings)} chunks to database")
            db.add_chunks(chunks_with_embeddings)
            
            # Save chunks to disk for GPT4All localdocs
            self.logger.info(f"Saving {len(chunks)} chunks to disk")
            self._save_chunks_to_disk(file_path, chunks)
            
            self.logger.info(f"Completed processing file: {file_path}")
            
        except Exception as e:
            self.logger.error(f"Error processing file {file_path}: {str(e)}")
            import traceback
            self.logger.error(f"Stack trace:\n{traceback.format_exc()}")
            
            # Add error to task
            task_ids = list(self.progress_tracker.get_all_tasks().keys())
            if task_ids:
                self.progress_tracker.add_error(task_ids[0], f"Error processing file {file_path}: {str(e)}")
                
            # Show error dialog
            messagebox.showerror("Processing Error", f"Error processing file {file_path}:\n{str(e)}")
    
    def _save_chunks_to_disk(self, file_path: Path, chunks: List[Dict[str, Any]]):
        """Save text chunks to disk for GPT4All localdocs.
        
        Args:
            file_path: Original file path
            chunks: List of text chunks with metadata
        """
        try:
            # Get chunks directory from config
            chunks_dir_path = self.config.get("processing", "chunks_directory", "~/.aiembedder/chunks")
            self.logger.info(f"Using chunks directory from config: {chunks_dir_path}")
            
            # Create absolute path - handle various path formats correctly
            if chunks_dir_path.startswith("~/"):
                output_dir = Path.home() / chunks_dir_path[2:]
            else:
                output_dir = Path(chunks_dir_path)
                
            output_dir = output_dir.resolve()
            self.logger.info(f"Using absolute chunks directory path: {output_dir}")
            
            # Ensure main chunks directory exists
            if not output_dir.exists():
                self.logger.info(f"Creating chunks directory: {output_dir}")
                output_dir.mkdir(parents=True, exist_ok=True)
            else:
                self.logger.info(f"Chunks directory already exists: {output_dir}")
            
            # Create a unique, filesystem-safe folder name for this file
            file_name = file_path.stem
            parent_dir = file_path.parent.name
            
            # Create a folder name with parent directory to avoid conflicts
            if parent_dir and parent_dir != ".":
                folder_name = f"{parent_dir}_{file_name}"
            else:
                folder_name = file_name
            
            # Windows-safe folder name (remove invalid chars)
            folder_name = re.sub(r'[\\/*?:"<>|]', "_", folder_name)
            
            # Create full path for the folder
            chunk_dir = output_dir / folder_name
            self.logger.info(f"Creating chunk subfolder: {chunk_dir}")
            
            # Create the folder for this file's chunks
            chunk_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Created chunk subfolder successfully: {chunk_dir}")
            
            # Save each chunk as a separate file
            self.logger.info(f"Saving {len(chunks)} chunks to {chunk_dir}")
            
            # Extract document info to add as context to each chunk
            doc_info = {
                "document_name": file_path.name,
                "document_path": str(file_path),
                "document_type": file_path.suffix.lstrip('.').upper(),
                "total_chunks": len(chunks),
                "created": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Try to get file stats for additional metadata
            try:
                stats = file_path.stat()
                doc_info["size_bytes"] = stats.st_size
                doc_info["modified"] = datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            except Exception as e:
                self.logger.debug(f"Could not get file stats: {str(e)}")
            
            for i, chunk in enumerate(chunks):
                # Create chunk filename with leading zeros for proper sorting
                chunk_file = chunk_dir / f"chunk_{i:04d}.txt"
                self.logger.debug(f"Saving chunk {i+1}/{len(chunks)} to {chunk_file}")
                
                with open(chunk_file, "w", encoding="utf-8") as f:
                    # Add document context header - critical for better GPT4All embeddings
                    f.write(f"# DOCUMENT: {doc_info['document_name']}\n")
                    f.write(f"# CHUNK: {i+1} of {doc_info['total_chunks']}\n")
                    f.write(f"# TYPE: {doc_info['document_type']}\n")
                    f.write(f"# CREATED: {doc_info['created']}\n")
                    
                    # Add source path as reference
                    f.write(f"# SOURCE: {doc_info['document_path']}\n")
                    
                    # Add chunk position indicators for GPT4All context
                    position = "BEGINNING" if i == 0 else "MIDDLE" if i < len(chunks) - 1 else "END"
                    f.write(f"# POSITION: {position}\n")
                    
                    # Add any additional metadata from the chunks dictionary
                    # These come from the pipeline processing
                    if 'cleaning_level' in chunk:
                        f.write(f"# CLEANING: {chunk['cleaning_level']}\n")
                    if 'chunk_size' in chunk:
                        f.write(f"# TOKENS_PER_CHUNK: {chunk['chunk_size']}\n")
                    if 'chunk_overlap' in chunk:
                        f.write(f"# OVERLAP_TOKENS: {chunk['chunk_overlap']}\n")
                    
                    # Add a separator for better visual parsing
                    f.write("\n---\n\n")
                    
                    # Write the actual text content
                    f.write(chunk['text'])
            
            self.logger.info(f"Successfully saved {len(chunks)} chunks to {chunk_dir}")
            
        except Exception as e:
            self.logger.error(f"Error saving chunks to disk: {str(e)}")
            import traceback
            self.logger.error(f"Stack trace:\n{traceback.format_exc()}")
    
    def _process_directory(self, dir_path: Path, pipeline: TextProcessingPipeline,
                          generator: VectorGenerator, db: VectorDatabase):
        """Process a directory.
        
        Args:
            dir_path: Directory path
            pipeline: Text processing pipeline
            generator: Vector generator
            db: Vector database
        """
        self.logger.info(f"Processing directory: {dir_path}")
        
        try:
            # Create directory task
            dir_task_id = self.progress_tracker.start_task(
                f"dir_{dir_path.name}",
                total=100,  # Initialize with default value
                status=f"Scanning directory {dir_path.name}"
            )
            
            # Get all files
            files = []
            for ext in [".txt", ".html", ".htm", ".pdf", ".doc", ".docx"]:
                files.extend(dir_path.glob(f"**/*{ext}"))
            
            # Update the status with file count
            self.logger.info(f"Found {len(files)} files in directory: {dir_path}")
            self.progress_tracker.update_task(
                dir_task_id, 
                current=0,
                status=f"Found {len(files)} files to process"
            )
            
            # Process each file
            for i, file_path in enumerate(files):
                if self.stop_processing_flag.is_set():
                    break
                
                try:
                    # Calculate percentage of completion for progress
                    current_progress = int((i / len(files)) * 100) if files else 0
                    
                    self.progress_tracker.update_task(
                        dir_task_id,
                        current=current_progress,
                        status=f"Processing {file_path.name} ({i+1}/{len(files)})"
                    )
                    
                    self._process_single_file(file_path, pipeline, generator, db)
                    
                except Exception as e:
                    self.logger.error(f"Error processing {file_path}: {str(e)}")
                    self.progress_tracker.add_error(dir_task_id, f"Error processing {file_path}: {str(e)}")
            
            # Complete directory task
            self.progress_tracker.update_task(
                dir_task_id, 
                current=100,  # Set to 100% complete
                status=f"Completed processing {len(files)} files"
            )
            self.progress_tracker.complete_task(dir_task_id)
            
        except Exception as e:
            self.logger.error(f"Error processing directory {dir_path}: {str(e)}")
            import traceback
            self.logger.error(f"Stack trace:\n{traceback.format_exc()}")
            
            # Add error if task was created
            if 'dir_task_id' in locals():
                self.progress_tracker.add_error(dir_task_id, f"Error processing directory {dir_path}: {str(e)}")
            
            raise
    
    def process_queue(self):
        """Process the queue of UI updates from the processing thread."""
        try:
            while not self.processing_queue.empty():
                message_type, message = self.processing_queue.get_nowait()
                
                if message_type == "complete":
                    messagebox.showinfo("Processing Complete", message)
                elif message_type == "error":
                    messagebox.showerror("Processing Error", f"An error occurred: {message}")
                elif message_type == "update_ui":
                    # Update UI state
                    self.process_button.configure(state="normal")
                    self.stop_button.configure(state="disabled")
                
        except queue.Empty:
            pass
        
        # Schedule next queue check
        self.root.after(100, self.process_queue)
    
    def stop_processing(self):
        """Stop processing."""
        if self.processing_thread and self.processing_thread.is_alive():
            if messagebox.askyesno("Stop Processing", "Are you sure you want to stop processing?"):
                self.logger.info("Stopping processing...")
                self.stop_processing_flag.set()
                
                # Update button state (full UI update will happen when thread ends)
                self.stop_button.configure(state="disabled") 
    
    def show_errors(self):
        """Show a list of all errors from the current processing."""
        tasks = self.progress_tracker.get_all_tasks()
        
        # Collect all errors
        all_errors = []
        for task_id, state in tasks.items():
            if state.errors:
                all_errors.append(f"Task: {task_id}")
                for i, error in enumerate(state.errors, 1):
                    all_errors.append(f"  {i}. {error}")
        
        # Show errors in a dialog
        if all_errors:
            error_text = "\n".join(all_errors)
            self.show_text_dialog("Processing Errors", error_text)
        else:
            messagebox.showinfo("Processing Errors", "No errors have been reported.")
    
    def check_chunks_folder(self):
        """Check if the chunks folder is empty and show its contents."""
        # Get chunks directory directly from config dictionary
        if "processing" in self.config.config and "chunks_directory" in self.config.config["processing"]:
            chunks_dir_path = self.config.config["processing"]["chunks_directory"]
        else:
            chunks_dir_path = "~/.aiembedder/chunks"  # Use default only if not found
            # Set it in config
            self.config.set("processing", "chunks_directory", chunks_dir_path)
            self.logger.info(f"Set chunks_directory in config: {chunks_dir_path}")
        
        chunks_dir = Path(chunks_dir_path).expanduser().resolve()
        self.logger.info(f"Checking chunks directory: {chunks_dir}")
        
        if not chunks_dir.exists():
            if messagebox.askyesno("Chunks Folder", 
                                f"The chunks folder does not exist: {chunks_dir}\n\nDo you want to create it?"):
                try:
                    chunks_dir.mkdir(parents=True, exist_ok=True)
                    self.logger.info(f"Created chunks directory: {chunks_dir}")
                    messagebox.showinfo("Chunks Folder", f"Created chunks directory: {chunks_dir}")
                except Exception as e:
                    self.logger.error(f"Error creating chunks directory: {str(e)}")
                    messagebox.showerror("Error", f"Failed to create chunks directory: {str(e)}")
            return
        
        # Get all chunk directories and files
        chunk_dirs = [d for d in chunks_dir.iterdir() if d.is_dir()]
        
        if not chunk_dirs:
            result = messagebox.askyesno("Chunks Folder", 
                                       f"The chunks folder is empty: {chunks_dir}\n\nDo you want to open it?")
            if result:
                self.open_folder(chunks_dir)
            return
        
        # Count files in each directory
        dir_stats = []
        total_chunks = 0
        for dir in chunk_dirs:
            chunk_files = list(dir.glob("*.txt"))
            file_count = len(chunk_files)
            total_chunks += file_count
            dir_stats.append(f"{dir.name}: {file_count} chunks")
        
        # Show results
        result_text = f"Chunks folder: {chunks_dir}\n\n"
        result_text += f"Total chunks: {total_chunks}\n"
        result_text += f"Source documents: {len(dir_stats)}\n\n"
        result_text += "\n".join(dir_stats)
        
        self.show_chunks_dialog("Chunks Folder Contents", result_text, chunks_dir)
    
    def show_chunks_dialog(self, title, text, folder_path):
        """Show a dialog with scrollable text and folder open button.
        
        Args:
            title: Dialog title
            text: Text to display
            folder_path: Path to the folder to open
        """
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("600x400")
        dialog.minsize(400, 300)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (self.root.winfo_width() - width) // 2 + self.root.winfo_x()
        y = (self.root.winfo_height() - height) // 2 + self.root.winfo_y()
        dialog.geometry(f"+{x}+{y}")
        
        # Create text widget with scrollbar
        frame = ttk.Frame(dialog, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        text_widget = tk.Text(frame, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(frame, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Insert text
        text_widget.insert(tk.END, text)
        text_widget.configure(state=tk.DISABLED)
        
        # Add buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        open_button = ttk.Button(button_frame, text="Open Folder", 
                               command=lambda: self.open_folder(folder_path))
        open_button.pack(side=tk.LEFT)
        
        close_button = ttk.Button(button_frame, text="Close", command=dialog.destroy)
        close_button.pack(side=tk.RIGHT)
    
    def open_folder(self, folder_path):
        """Open a folder in the file explorer.
        
        Args:
            folder_path: Path to open
        """
        try:
            import os
            import platform
            
            # Use the appropriate command based on the OS
            if platform.system() == "Windows":
                os.startfile(folder_path)
            elif platform.system() == "Darwin":  # macOS
                import subprocess
                subprocess.Popen(["open", folder_path])
            else:  # Linux
                import subprocess
                subprocess.Popen(["xdg-open", folder_path])
                
            self.logger.info(f"Opened folder: {folder_path}")
        except Exception as e:
            self.logger.error(f"Error opening folder: {str(e)}")
            messagebox.showerror("Error", f"Failed to open folder: {str(e)}")
    
    def show_text_dialog(self, title, text):
        """Show a dialog with scrollable text.
        
        Args:
            title: Dialog title
            text: Text to display
        """
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("600x400")
        dialog.minsize(400, 300)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (self.root.winfo_width() - width) // 2 + self.root.winfo_x()
        y = (self.root.winfo_height() - height) // 2 + self.root.winfo_y()
        dialog.geometry(f"+{x}+{y}")
        
        # Create text widget with scrollbar
        frame = ttk.Frame(dialog, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        text_widget = tk.Text(frame, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(frame, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Insert text
        text_widget.insert(tk.END, text)
        text_widget.configure(state=tk.DISABLED)
        
        # Add close button
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        close_button = ttk.Button(button_frame, text="Close", command=dialog.destroy)
        close_button.pack(side=tk.RIGHT) 