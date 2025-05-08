"""
Search dialog for querying the vector database.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict, Any, List

from aiembedder.utils.config import Config
from aiembedder.utils.logging import Logger
from aiembedder.vector.database import VectorDatabase

class SearchDialog:
    """Search dialog for querying the vector database."""
    
    def __init__(
        self,
        parent: tk.Tk,
        config: Config,
        logger: Optional[Logger] = None
    ):
        """Initialize search dialog.
        
        Args:
            parent: Parent window
            config: Configuration instance
            logger: Logger instance
        """
        self.parent = parent
        self.config = config
        self.logger = logger
        self.result = False
        
        self.create_dialog()
    
    def create_dialog(self):
        """Create search dialog."""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Search Vector Database")
        self.dialog.geometry("700x500")
        self.dialog.minsize(600, 400)
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
        self.setup_layout()
        
        # Make dialog modal
        self.dialog.protocol("WM_DELETE_WINDOW", self.on_close)
        self.dialog.wait_window()
    
    def create_widgets(self):
        """Create dialog widgets."""
        # Main frame
        self.main_frame = ttk.Frame(self.dialog, padding="10")
        
        # Search frame
        self.search_frame = ttk.Frame(self.main_frame)
        
        # Search input
        self.search_label = ttk.Label(self.search_frame, text="Search query:")
        self.search_entry = ttk.Entry(self.search_frame, width=50)
        self.search_entry.bind("<Return>", self.on_search)
        
        # Search button
        self.search_button = ttk.Button(self.search_frame, text="Search", command=self.on_search)
        
        # Options frame
        self.options_frame = ttk.Frame(self.main_frame)
        
        # Results limit
        self.limit_label = ttk.Label(self.options_frame, text="Results limit:")
        self.limit_var = tk.IntVar(value=self.config.get("database.default_limit", 5))
        self.limit_spinner = ttk.Spinbox(self.options_frame, from_=1, to=20, increment=1, textvariable=self.limit_var, width=5)
        
        # File filter
        self.filter_var = tk.BooleanVar(value=False)
        self.filter_check = ttk.Checkbutton(self.options_frame, text="Filter by file type:", variable=self.filter_var)
        self.filter_combo_var = tk.StringVar(value="All")
        self.filter_combo = ttk.Combobox(self.options_frame, textvariable=self.filter_combo_var, state="readonly", width=15)
        self.filter_combo["values"] = ("All", "Text", "HTML", "PDF", "Word")
        
        # Results frame
        self.results_frame = ttk.LabelFrame(self.main_frame, text="Results", padding="10")
        
        # Results treeview
        self.results_tree = ttk.Treeview(self.results_frame, columns=("score", "source"), show="headings")
        self.results_tree.heading("score", text="Score")
        self.results_tree.heading("source", text="Source")
        self.results_tree.column("score", width=80, anchor="center")
        self.results_tree.column("source", width=150)
        
        # Add vertical scrollbar
        self.results_scrollbar = ttk.Scrollbar(self.results_frame, orient="vertical", command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=self.results_scrollbar.set)
        
        # Add selection handler
        self.results_tree.bind("<<TreeviewSelect>>", self.on_result_selected)
        
        # Content frame
        self.content_frame = ttk.LabelFrame(self.main_frame, text="Content", padding="10")
        
        # Content text
        self.content_text = tk.Text(self.content_frame, wrap=tk.WORD, width=80, height=10)
        self.content_text.config(state=tk.DISABLED)
        
        # Add vertical scrollbar
        self.content_scrollbar = ttk.Scrollbar(self.content_frame, orient="vertical", command=self.content_text.yview)
        self.content_text.configure(yscrollcommand=self.content_scrollbar.set)
        
        # Status bar
        self.status_bar = ttk.Label(self.main_frame, text="Ready")
        
        # Close button
        self.close_button = ttk.Button(self.main_frame, text="Close", command=self.on_close)
    
    def setup_layout(self):
        """Set up widget layout."""
        # Main frame
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Search frame
        self.search_frame.pack(fill=tk.X, pady=(0, 5))
        self.search_label.pack(side=tk.LEFT, padx=(0, 5))
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.search_button.pack(side=tk.RIGHT)
        
        # Options frame
        self.options_frame.pack(fill=tk.X, pady=(0, 10))
        self.limit_label.pack(side=tk.LEFT, padx=(0, 5))
        self.limit_spinner.pack(side=tk.LEFT, padx=(0, 20))
        self.filter_check.pack(side=tk.LEFT, padx=(0, 5))
        self.filter_combo.pack(side=tk.LEFT)
        
        # Results frame
        self.results_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Content frame
        self.content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.content_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.content_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Status and close button
        self.status_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.close_button.pack(side=tk.RIGHT)
    
    def on_search(self, event=None):
        """Handle search button click."""
        query = self.search_entry.get().strip()
        if not query:
            messagebox.showwarning("Empty Query", "Please enter a search query.")
            return
        
        try:
            self.status_bar.config(text="Searching...")
            self.search_button.config(state="disabled")
            self.dialog.update_idletasks()
            
            # Clear previous results
            self.results_tree.delete(*self.results_tree.get_children())
            self.clear_content()
            
            # Get search parameters
            limit = self.limit_var.get()
            
            # Get file filter
            where_filter = None
            if self.filter_var.get():
                file_type = self.filter_combo_var.get()
                if file_type != "All":
                    extensions = {
                        "Text": ".txt",
                        "HTML": [".html", ".htm"],
                        "PDF": ".pdf",
                        "Word": [".doc", ".docx"]
                    }
                    ext = extensions.get(file_type)
                    if ext:
                        if isinstance(ext, list):
                            # For multiple extensions, we need a complex filter
                            # This is a simplification - in real implementation would use proper metadata filter
                            where_filter = {"file_name": {"$contains": ext[0]}}
                        else:
                            where_filter = {"file_name": {"$contains": ext}}
            
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
            
            # Search database
            results = db.search(query, n_results=limit, where=where_filter)
            
            # Display results
            for i, result in enumerate(results):
                score = result["score"]
                source = result["metadata"].get("source", "Unknown")
                text = result["text"]
                
                # Add to treeview
                item_id = self.results_tree.insert("", "end", 
                                                values=(f"{score:.3f}", source),
                                                text=text)
                
                # Select first item
                if i == 0:
                    self.results_tree.selection_set(item_id)
                    self.display_content(text)
            
            # Update status
            result_count = len(results)
            self.status_bar.config(text=f"Found {result_count} result{'s' if result_count != 1 else ''}")
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error searching: {str(e)}")
            messagebox.showerror("Search Error", f"An error occurred while searching: {str(e)}")
            self.status_bar.config(text="Search error")
            
        finally:
            self.search_button.config(state="normal")
    
    def on_result_selected(self, event):
        """Handle result selection."""
        selected_items = self.results_tree.selection()
        if selected_items:
            item = selected_items[0]
            text = self.results_tree.item(item, "text")
            self.display_content(text)
    
    def display_content(self, text: str):
        """Display content text.
        
        Args:
            text: Text to display
        """
        self.content_text.config(state=tk.NORMAL)
        self.content_text.delete(1.0, tk.END)
        self.content_text.insert(tk.END, text)
        self.content_text.config(state=tk.DISABLED)
    
    def clear_content(self):
        """Clear content display."""
        self.content_text.config(state=tk.NORMAL)
        self.content_text.delete(1.0, tk.END)
        self.content_text.config(state=tk.DISABLED)
    
    def on_close(self):
        """Handle close button click."""
        self.dialog.destroy() 