"""
Progress tracking for AIEmbedder.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Dict, List, Optional

@dataclass
class ProgressState:
    """Progress state for a task."""
    total: int
    current: int
    status: str
    start_time: datetime
    end_time: Optional[datetime] = None
    errors: List[str] = None
    
    def __post_init__(self):
        """Initialize errors list if None."""
        if self.errors is None:
            self.errors = []
    
    @property
    def percentage(self) -> float:
        """Get progress percentage.
        
        Returns:
            Progress percentage
        """
        return (self.current / self.total) * 100 if self.total > 0 else 0
    
    @property
    def elapsed_time(self) -> float:
        """Get elapsed time in seconds.
        
        Returns:
            Elapsed time in seconds
        """
        end = self.end_time or datetime.now()
        return (end - self.start_time).total_seconds()
    
    @property
    def is_complete(self) -> bool:
        """Check if task is complete.
        
        Returns:
            True if task is complete
        """
        return self.current >= self.total

class ProgressTracker:
    """Progress tracker for AIEmbedder."""
    
    def __init__(self):
        """Initialize progress tracker."""
        self.tasks: Dict[str, ProgressState] = {}
        self.callbacks: Dict[str, List[Callable[[str, ProgressState], None]]] = {}
        self.global_callbacks: List[Callable[[str, ProgressState], None]] = []
    
    def start_task(self, task_id: str, total: int, status: str = "Starting...") -> None:
        """Start a new task.
        
        Args:
            task_id: Task identifier
            total: Total number of items
            status: Initial status message
        """
        self.tasks[task_id] = ProgressState(
            total=total,
            current=0,
            status=status,
            start_time=datetime.now()
        )
        self._notify_callbacks(task_id)
    
    def update_task(self, task_id: str, current: int = None, status: str = None) -> None:
        """Update task progress.
        
        Args:
            task_id: Task identifier
            current: Current progress
            status: Status message
        """
        if task_id in self.tasks:
            if current is not None:
                self.tasks[task_id].current = current
            if status is not None:
                self.tasks[task_id].status = status
            self._notify_callbacks(task_id)
    
    def set_total(self, task_id: str, total: int) -> None:
        """Update the total value for an existing task.
        
        Args:
            task_id: Task identifier
            total: New total value
        """
        if task_id in self.tasks:
            self.tasks[task_id].total = total
            self._notify_callbacks(task_id)
    
    def complete_task(self, task_id: str, status: str = "Complete") -> None:
        """Complete a task.
        
        Args:
            task_id: Task identifier
            status: Completion status message
        """
        if task_id in self.tasks:
            self.tasks[task_id].current = self.tasks[task_id].total
            self.tasks[task_id].status = status
            self.tasks[task_id].end_time = datetime.now()
            self._notify_callbacks(task_id)
    
    def add_error(self, task_id: str, error: str) -> None:
        """Add error to task.
        
        Args:
            task_id: Task identifier
            error: Error message
        """
        if task_id in self.tasks:
            self.tasks[task_id].errors.append(error)
            self._notify_callbacks(task_id)
    
    def get_task(self, task_id: str) -> Optional[ProgressState]:
        """Get task state.
        
        Args:
            task_id: Task identifier
            
        Returns:
            Task state if found
        """
        return self.tasks.get(task_id)
    
    def get_all_tasks(self) -> Dict[str, ProgressState]:
        """Get all task states.
        
        Returns:
            Dict of task IDs to task states
        """
        return self.tasks
    
    def register_callback(self, task_id: str, callback: Callable[[str, ProgressState], None]) -> None:
        """Register callback for specific task updates.
        
        Args:
            task_id: Task identifier
            callback: Callback function
        """
        if task_id not in self.callbacks:
            self.callbacks[task_id] = []
        self.callbacks[task_id].append(callback)
    
    def register_global_callback(self, callback: Callable[[str, ProgressState], None]) -> None:
        """Register callback for all task updates.
        
        Args:
            callback: Callback function
        """
        self.global_callbacks.append(callback)
    
    def _notify_callbacks(self, task_id: str) -> None:
        """Notify callbacks of task update.
        
        Args:
            task_id: Task identifier
        """
        state = self.tasks[task_id]
        
        # Notify task-specific callbacks
        if task_id in self.callbacks:
            for callback in self.callbacks[task_id]:
                callback(task_id, state)
        
        # Notify global callbacks
        for callback in self.global_callbacks:
            callback(task_id, state) 