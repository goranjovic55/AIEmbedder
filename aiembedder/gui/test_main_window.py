"""
Test main window for AIEmbedder GUI with minimal dependencies.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sys
import os
from pathlib import Path

class MockConfig:
    """Mock configuration class."""
    
    def __init__(self):
        """Initialize mock config."""
        self.settings = {
            "gui.log_level": "INFO",
            "processing.cleaning_level": "medium",
            "processing.chunk_size": 400,
            "processing.chunk_overlap": 50,
            "processing.similarity_threshold": 0.95,
        }
    
    def get(self, path, default=None):
        """Get setting value.
        
        Args:
            path: Setting path
            default: Default value
            
        Returns:
            Setting value
        """
        parts = path.split(".")
        if len(parts) == 1:
            # Simple key
            return self.settings.get(path, default)
        else:
            # Nested key
            key = ".".join(parts)
            return self.settings.get(key, default)
    
    def update(self, settings):
        """Update settings.
        
        Args:
            settings: Settings to update
        """
        self.settings.update(settings)

class MockLogger:
    """Mock logger class."""
    
    def __init__(self):
        """Initialize mock logger."""
        self.logs = []
    
    def info(self, message):
        """Log info message.
        
        Args:
            message: Log message
        """
        print(f"INFO: {message}")
        self.logs.append(("INFO", message))
    
    def warning(self, message):
        """Log warning message.
        
        Args:
            message: Log message
        """
        print(f"WARNING: {message}")
        self.logs.append(("WARNING", message))
    
    def error(self, message):
        """Log error message.
        
        Args:
            message: Log message
        """
        print(f"ERROR: {message}")
        self.logs.append(("ERROR", message))
    
    def set_level(self, level):
        """Set log level.
        
        Args:
            level: Log level
        """
        print(f"Setting log level to {level}")

class MockProgressTracker:
    """Mock progress tracker class."""
    
    def __init__(self):
        """Initialize mock progress tracker."""
        self.tasks = {}
        self.next_id = 1
    
    def start_task(self, name, total=None, status=None):
        """Start task.
        
        Args:
            name: Task name
            total: Total steps
            status: Task status
            
        Returns:
            Task ID
        """
        task_id = self.next_id
        self.next_id += 1
        
        self.tasks[task_id] = {
            "name": name,
            "total": total,
            "current": 0,
            "status": status,
            "errors": [],
            "complete": False
        }
        
        return task_id
    
    def update_task(self, task_id, current=None, status=None):
        """Update task.
        
        Args:
            task_id: Task ID
            current: Current step
            status: Task status
        """
        if task_id not in self.tasks:
            return
        
        if current is not None:
            self.tasks[task_id]["current"] = current
        
        if status is not None:
            self.tasks[task_id]["status"] = status
    
    def complete_task(self, task_id):
        """Complete task.
        
        Args:
            task_id: Task ID
        """
        if task_id not in self.tasks:
            return
        
        self.tasks[task_id]["complete"] = True
    
    def add_error(self, task_id, error):
        """Add task error.
        
        Args:
            task_id: Task ID
            error: Error message
        """
        if task_id not in self.tasks:
            return
        
        self.tasks[task_id]["errors"].append(error)

class TestMainWindow:
    """Test main window for AIEmbedder GUI."""
    
    def __init__(
        self,
        config=None,
        logger=None,
        progress_tracker=None
    ):
        """Initialize main window.
        
        Args:
            config: Configuration instance
            logger: Logger instance
            progress_tracker: Progress tracker instance
        """
        self.config = config or MockConfig()
        self.logger = logger or MockLogger()
        self.progress_tracker = progress_tracker or MockProgressTracker()
        
        self.root = tk.Tk()
        self.root.title("AIEmbedder - Test")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)
        
        # Initialize event handling
        self.processing_thread = None
        self.stop_processing_flag = False
        
        self.setup_styles()
        self.create_menu()
        self.create_widgets()
        self.setup_layout()
        
        self.logger.info("Initialized test main window")
    
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
        
        # Help menu
        self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.help_menu.add_command(label="About", command=self.show_about)
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
        
        # Action buttons
        self.action_frame = ttk.Frame(self.main_frame)
        self.process_button = ttk.Button(self.action_frame, text="Process Files", command=self.process_files)
        self.process_button.configure(state="disabled")  # Disabled until files are selected
        
        # Output frame
        self.output_frame = ttk.LabelFrame(self.main_frame, text="Output", padding="10")
        self.output_text = tk.Text(self.output_frame, wrap=tk.WORD, width=80, height=10)
        self.output_scrollbar = ttk.Scrollbar(self.output_frame, orient="vertical", command=self.output_text.yview)
        self.output_text.configure(yscrollcommand=self.output_scrollbar.set)
    
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
        
        # Action buttons
        self.action_frame.pack(fill=tk.X, pady=(0, 10))
        self.process_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Output frame
        self.output_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.output_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    def run(self):
        """Run the main window."""
        self.root.protocol("WM_DELETE_WINDOW", self.exit_app)
        self.root.mainloop()
    
    def exit_app(self):
        """Exit the application."""
        if messagebox.askokcancel("Exit", "Are you sure you want to exit?"):
            self.logger.info("Exiting application")
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
    
    def process_files(self):
        """Process selected files (mock implementation)."""
        files = list(self.file_listbox.get(0, tk.END))
        if not files:
            messagebox.showwarning("No Files", "Please select files or directories to process.")
            return
        
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "Processing files:\n\n")
        
        for file_path in files:
            self.output_text.insert(tk.END, f"- {file_path}\n")
        
        self.output_text.insert(tk.END, "\nProcessing complete (mock implementation)")
        messagebox.showinfo("Success", "Files processed successfully (mock implementation)")
    
    def show_about(self):
        """Show about dialog."""
        messagebox.showinfo(
            "About AIEmbedder",
            "AIEmbedder is a tool for embedding documents into vector databases for semantic search.\n\n"
            "Version: 0.1.0 (Test)\n"
            "Created by: AIEmbedder Team"
        )

def main():
    """Run the application."""
    try:
        window = TestMainWindow()
        window.run()
        return 0
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main()) 