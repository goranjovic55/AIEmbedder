"""
Progress panel for displaying task progress.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Dict, List, Any
import time
from datetime import datetime

from aiembedder.utils.progress import ProgressTracker, ProgressState

class ProgressPanel:
    """Progress panel for displaying task progress."""
    
    def __init__(
        self,
        parent: ttk.Frame,
        progress_tracker: ProgressTracker
    ):
        """Initialize progress panel.
        
        Args:
            parent: Parent frame
            progress_tracker: Progress tracker instance
        """
        self.parent = parent
        self.progress_tracker = progress_tracker
        self.progress_bars: Dict[str, ttk.Progressbar] = {}
        self.status_labels: Dict[str, ttk.Label] = {}
        
        self.create_widgets()
        self.setup_layout()
        self.setup_callbacks()
        self.update_tasks()
    
    def create_widgets(self):
        """Create panel widgets."""
        # Main frame
        self.main_frame = ttk.Frame(self.parent, padding="10")
        
        # Tasks frame
        self.tasks_frame = ttk.LabelFrame(self.main_frame, text="Tasks", padding="10")
        
        # No tasks label
        self.no_tasks_label = ttk.Label(self.tasks_frame, text="No tasks in progress")
        
        # Refresh button
        self.refresh_button = ttk.Button(self.main_frame, text="Refresh", command=self.update_tasks)
        
        # Summary frame
        self.summary_frame = ttk.LabelFrame(self.main_frame, text="Summary", padding="10")
        
        # Summary labels
        self.total_tasks_label = ttk.Label(self.summary_frame, text="Total tasks: 0")
        self.completed_tasks_label = ttk.Label(self.summary_frame, text="Completed tasks: 0")
        self.in_progress_tasks_label = ttk.Label(self.summary_frame, text="In progress tasks: 0")
        self.error_tasks_label = ttk.Label(self.summary_frame, text="Tasks with errors: 0")
    
    def setup_layout(self):
        """Set up panel layout."""
        # Main frame
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Tasks frame
        self.tasks_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # No tasks label
        self.no_tasks_label.pack(fill=tk.X, pady=5)
        
        # Summary frame
        self.summary_frame.pack(fill=tk.X)
        
        # Summary labels
        self.total_tasks_label.pack(anchor=tk.W, pady=(0, 2))
        self.completed_tasks_label.pack(anchor=tk.W, pady=(0, 2))
        self.in_progress_tasks_label.pack(anchor=tk.W, pady=(0, 2))
        self.error_tasks_label.pack(anchor=tk.W)
        
        # Refresh button
        self.refresh_button.pack(anchor=tk.E, pady=(10, 0))
    
    def setup_callbacks(self):
        """Set up callbacks for progress updates."""
        self.progress_tracker.register_global_callback(self.on_progress_update)
    
    def on_progress_update(self, task_id: str, state: ProgressState):
        """Handle progress update.
        
        Args:
            task_id: Task ID
            state: Task state
        """
        # Schedule UI update in main thread
        self.parent.after(0, self.update_tasks)
    
    def update_tasks(self):
        """Update task displays."""
        tasks = self.progress_tracker.get_all_tasks()
        
        # Update summary
        total_tasks = len(tasks)
        completed_tasks = sum(1 for state in tasks.values() if state.is_complete)
        in_progress_tasks = sum(1 for state in tasks.values() if not state.is_complete)
        error_tasks = sum(1 for state in tasks.values() if state.errors)
        
        self.total_tasks_label.config(text=f"Total tasks: {total_tasks}")
        self.completed_tasks_label.config(text=f"Completed tasks: {completed_tasks}")
        self.in_progress_tasks_label.config(text=f"In progress tasks: {in_progress_tasks}")
        self.error_tasks_label.config(text=f"Tasks with errors: {error_tasks}")
        
        # Clear existing progress bars
        for widget in self.tasks_frame.winfo_children():
            if widget != self.no_tasks_label:
                widget.destroy()
        
        self.progress_bars = {}
        self.status_labels = {}
        
        # Show/hide no tasks label
        if not tasks:
            self.no_tasks_label.pack(fill=tk.X, pady=5)
        else:
            self.no_tasks_label.pack_forget()
            
            # Create progress bars for each task
            for i, (task_id, state) in enumerate(tasks.items()):
                self.create_task_progress(task_id, state, i)
    
    def create_task_progress(self, task_id: str, state: ProgressState, index: int):
        """Create progress display for a task.
        
        Args:
            task_id: Task ID
            state: Task state
            index: Task index
        """
        # Task frame
        task_frame = ttk.Frame(self.tasks_frame)
        task_frame.pack(fill=tk.X, pady=(5 if index > 0 else 0, 0))
        
        # Task header
        header_frame = ttk.Frame(task_frame)
        header_frame.pack(fill=tk.X)
        
        # Task name
        task_name = task_id.replace("_", " ").title()
        task_name_label = ttk.Label(header_frame, text=task_name)
        task_name_label.pack(side=tk.LEFT)
        
        # Task status
        status_text = self.format_task_status(state)
        status_label = ttk.Label(header_frame, text=status_text)
        status_label.pack(side=tk.RIGHT)
        self.status_labels[task_id] = status_label
        
        # Progress bar
        progress_var = tk.DoubleVar(value=state.percentage)
        progress_bar = ttk.Progressbar(
            task_frame,
            variable=progress_var,
            maximum=100,
            mode="determinate"
        )
        progress_bar.pack(fill=tk.X, pady=(2, 0))
        self.progress_bars[task_id] = progress_bar
        
        # Error display if any
        if state.errors:
            error_frame = ttk.Frame(task_frame)
            error_frame.pack(fill=tk.X, pady=(2, 0))
            
            error_label = ttk.Label(
                error_frame,
                text="Errors:",
                foreground="red"
            )
            error_label.pack(anchor=tk.W)
            
            error_text = tk.Text(
                error_frame,
                height=3,
                width=40,
                wrap=tk.WORD,
                background="#f0f0f0",
                relief=tk.FLAT
            )
            error_text.pack(fill=tk.X)
            error_text.insert(tk.END, "\n".join(state.errors))
            error_text.config(state=tk.DISABLED)
    
    def format_task_status(self, state: ProgressState) -> str:
        """Format task status for display.
        
        Args:
            state: Task state
            
        Returns:
            Formatted status string
        """
        if state.is_complete:
            elapsed = self.format_time_delta(state.elapsed_time)
            return f"Completed in {elapsed}"
        else:
            return f"{state.status} - {state.percentage:.1f}%"
    
    def format_time_delta(self, seconds: float) -> str:
        """Format time delta for display.
        
        Args:
            seconds: Time in seconds
            
        Returns:
            Formatted time string
        """
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = seconds // 60
            sec = seconds % 60
            return f"{int(minutes)}m {int(sec)}s"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{int(hours)}h {int(minutes)}m" 