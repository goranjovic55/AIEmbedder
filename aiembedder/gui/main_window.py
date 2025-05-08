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
        
        # Input panel
        self.input_frame = ttk.LabelFrame(self.main_frame, text="Input", padding="10")
        
        # File selection
        self.file_frame = ttk.Frame(self.input_frame)
        self.file_label = ttk.Label(self.file_frame, text="Selected files/directories:")
        self.file_listbox = tk.Listbox(self.file_frame, height=5, selectmode=tk.EXTENDED)
        self.file_scrollbar = ttk.Scrollbar(self.file_frame, orient="vertical", command=self.file_listbox.yview)
        self.file_listbox.configure(yscrollcommand=self.file_scrollbar.set)
        
        self.file_buttons_frame = ttk.Frame(self.input_frame)
        self.add_file_button = ttk.Button(self.file_buttons_frame, text="Add File", command=self.open_file)
        self.add_dir_button = ttk.Button(self.file_buttons_frame, text="Add Directory", command=self.open_directory)
        self.remove_selected_button = ttk.Button(self.file_buttons_frame, text="Remove Selected", command=self.remove_selected)
        self.clear_all_button = ttk.Button(self.file_buttons_frame, text="Clear All", command=self.clear_all)
        
        # Process options
        self.options_frame = ttk.LabelFrame(self.main_frame, text="Processing Options", padding="10")
        
        self.cleaning_frame = ttk.Frame(self.options_frame)
        self.cleaning_label = ttk.Label(self.cleaning_frame, text="Cleaning level:")
        self.cleaning_var = tk.StringVar(value=self.config.get("processing.cleaning_level", "medium"))
        self.cleaning_combo = ttk.Combobox(self.cleaning_frame, textvariable=self.cleaning_var)
        self.cleaning_combo["values"] = ("light", "medium", "aggressive")
        self.cleaning_combo.state(["readonly"])
        
        self.chunk_frame = ttk.Frame(self.options_frame)
        self.chunk_label = ttk.Label(self.chunk_frame, text="Chunk size:")
        self.chunk_var = tk.IntVar(value=self.config.get("processing.chunk_size", 400))
        self.chunk_entry = ttk.Spinbox(self.chunk_frame, from_=50, to=1000, increment=50, textvariable=self.chunk_var)
        
        self.overlap_frame = ttk.Frame(self.options_frame)
        self.overlap_label = ttk.Label(self.overlap_frame, text="Overlap:")
        self.overlap_var = tk.IntVar(value=self.config.get("processing.chunk_overlap", 50))
        self.overlap_entry = ttk.Spinbox(self.overlap_frame, from_=0, to=500, increment=10, textvariable=self.overlap_var)
        
        self.similarity_frame = ttk.Frame(self.options_frame)
        self.similarity_label = ttk.Label(self.similarity_frame, text="Similarity threshold:")
        self.similarity_var = tk.DoubleVar(value=self.config.get("processing.similarity_threshold", 0.95))
        self.similarity_entry = ttk.Spinbox(self.similarity_frame, from_=0.5, to=1.0, increment=0.01, textvariable=self.similarity_var)
        
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
        
        # Input panel
        self.input_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.file_frame.pack(fill=tk.X, pady=(0, 5))
        self.file_label.pack(anchor=tk.W)
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.file_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.file_buttons_frame.pack(fill=tk.X)
        self.add_file_button.pack(side=tk.LEFT, padx=(0, 5))
        self.add_dir_button.pack(side=tk.LEFT, padx=(0, 5))
        self.remove_selected_button.pack(side=tk.LEFT, padx=(0, 5))
        self.clear_all_button.pack(side=tk.LEFT)
        
        # Process options
        self.options_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.cleaning_frame.pack(fill=tk.X, pady=(0, 5))
        self.cleaning_label.pack(side=tk.LEFT, padx=(0, 5))
        self.cleaning_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.chunk_frame.pack(fill=tk.X, pady=(0, 5))
        self.chunk_label.pack(side=tk.LEFT, padx=(0, 5))
        self.chunk_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.overlap_frame.pack(fill=tk.X, pady=(0, 5))
        self.overlap_label.pack(side=tk.LEFT, padx=(0, 5))
        self.overlap_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.similarity_frame.pack(fill=tk.X)
        self.similarity_label.pack(side=tk.LEFT, padx=(0, 5))
        self.similarity_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
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
    
    def clear_all(self):
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
            self.cleaning_var.set(self.config.get("processing.cleaning_level", "medium"))
            self.chunk_var.set(self.config.get("processing.chunk_size", 400))
            self.overlap_var.set(self.config.get("processing.chunk_overlap", 50))
            self.similarity_var.set(self.config.get("processing.similarity_threshold", 0.95))
    
    def open_search(self):
        """Open search dialog."""
        from aiembedder.gui.search_dialog import SearchDialog
        search_dialog = SearchDialog(self.root, self.config, self.logger)
    
    def reset_database(self):
        """Reset the vector database."""
        if messagebox.askyesno("Reset Database", "Are you sure you want to reset the database? This will delete all stored embeddings."):
            try:
                # Create database with configured settings
                collection_name = self.config.get("database.collection_name", "aiembedder")
                persist_directory = self.config.get("database.persist_directory", "~/.aiembedder/db")
                use_gpu = self.config.get("processing.use_gpu", True)
                
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
            
            # Update processing configuration
            self.config.update({
                "processing.cleaning_level": self.cleaning_var.get(),
                "processing.chunk_size": chunk_size,
                "processing.chunk_overlap": chunk_overlap,
                "processing.similarity_threshold": self.similarity_var.get()
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
            cleaning_level = self.config.get("processing.cleaning_level", "medium")
            chunk_size = self.config.get("processing.chunk_size", 400)
            chunk_overlap = self.config.get("processing.chunk_overlap", 50)
            similarity_threshold = self.config.get("processing.similarity_threshold", 0.95)
            use_gpu = self.config.get("processing.use_gpu", True)
            
            # Create processing components
            pipeline = TextProcessingPipeline(
                cleaning_level=cleaning_level,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                similarity_threshold=similarity_threshold,
                use_gpu=use_gpu,
                progress_tracker=self.progress_tracker
            )
            
            # Create vector components
            model_name = self.config.get("advanced.model_name", "all-MiniLM-L6-v2")
            generator = VectorGenerator(
                model_name=model_name,
                use_gpu=use_gpu,
                logger=self.logger
            )
            
            collection_name = self.config.get("database.collection_name", "aiembedder")
            persist_directory = self.config.get("database.persist_directory", "~/.aiembedder/db")
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
            self.progress_tracker.update_task(main_task_id, current=len(file_paths))
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
        self.logger.info(f"Processing file: {file_path}")
        
        # Get appropriate processor
        processor = self.processor_factory.get_processor(file_path)
        
        # Extract text
        text = processor.extract_text(file_path)
        
        # Process text
        chunks = pipeline.process_text(text, metadata={"source": str(file_path)})
        
        # Generate embeddings
        chunks_with_embeddings = generator.generate_embeddings(chunks)
        
        # Add to database
        db.add_chunks(chunks_with_embeddings)
        
        self.logger.info(f"Completed processing file: {file_path}")
    
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
        
        # Create directory task
        dir_task_id = self.progress_tracker.start_task(
            f"dir_{dir_path.name}",
            status=f"Scanning directory {dir_path.name}"
        )
        
        try:
            # Get all files
            files = []
            for ext in [".txt", ".html", ".htm", ".pdf", ".doc", ".docx"]:
                files.extend(dir_path.glob(f"**/*{ext}"))
            
            # Update task with total files
            self.progress_tracker.update_task(dir_task_id, total=len(files))
            
            # Process each file
            for i, file_path in enumerate(files):
                if self.stop_processing_flag.is_set():
                    break
                
                try:
                    self.progress_tracker.update_task(
                        dir_task_id,
                        current=i,
                        status=f"Processing {file_path.name}"
                    )
                    
                    self._process_single_file(file_path, pipeline, generator, db)
                    
                except Exception as e:
                    self.logger.error(f"Error processing {file_path}: {str(e)}")
                    self.progress_tracker.add_error(dir_task_id, f"Error processing {file_path}: {str(e)}")
            
            # Complete directory task
            self.progress_tracker.update_task(dir_task_id, current=len(files))
            self.progress_tracker.complete_task(dir_task_id)
            
        except Exception as e:
            self.logger.error(f"Error processing directory {dir_path}: {str(e)}")
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