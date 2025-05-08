"""
Simplified main window for AIEmbedder GUI testing.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys

class SimpleMainWindow:
    """Simplified main window for AIEmbedder GUI testing."""
    
    def __init__(self):
        """Initialize main window."""
        self.root = tk.Tk()
        self.root.title("AIEmbedder - Simple Test")
        self.root.geometry("600x400")
        self.root.minsize(600, 400)
        
        self.create_widgets()
        self.setup_layout()
        self.root.protocol("WM_DELETE_WINDOW", self.exit_app)
    
    def create_widgets(self):
        """Create main widgets."""
        # Main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        
        # Header
        self.header_label = ttk.Label(
            self.main_frame, 
            text="AIEmbedder - Simple Test", 
            font=("Helvetica", 16, "bold")
        )
        
        # Description
        self.description = ttk.Label(
            self.main_frame,
            text="This is a simplified test of the AIEmbedder GUI",
            wraplength=400
        )
        
        # Input frame
        self.input_frame = ttk.LabelFrame(self.main_frame, text="Input", padding="10")
        self.input_label = ttk.Label(self.input_frame, text="Enter some text:")
        self.input_entry = ttk.Entry(self.input_frame, width=40)
        
        # Buttons
        self.button_frame = ttk.Frame(self.main_frame)
        self.process_button = ttk.Button(
            self.button_frame, 
            text="Process", 
            command=self.process_action
        )
        self.clear_button = ttk.Button(
            self.button_frame, 
            text="Clear", 
            command=self.clear_action
        )
        
        # Output frame
        self.output_frame = ttk.LabelFrame(self.main_frame, text="Output", padding="10")
        self.output_text = tk.Text(self.output_frame, height=10, width=50, wrap=tk.WORD)
        self.output_text.config(state=tk.DISABLED)
    
    def setup_layout(self):
        """Set up widget layout."""
        # Main frame
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        self.header_label.pack(pady=(0, 10))
        
        # Description
        self.description.pack(pady=(0, 20))
        
        # Input frame
        self.input_frame.pack(fill=tk.X, pady=(0, 10))
        self.input_label.pack(side=tk.LEFT, padx=(0, 10))
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Buttons
        self.button_frame.pack(fill=tk.X, pady=(0, 10))
        self.process_button.pack(side=tk.LEFT, padx=(0, 10))
        self.clear_button.pack(side=tk.LEFT)
        
        # Output frame
        self.output_frame.pack(fill=tk.BOTH, expand=True)
        self.output_text.pack(fill=tk.BOTH, expand=True)
    
    def process_action(self):
        """Handle process button click."""
        input_text = self.input_entry.get().strip()
        
        if not input_text:
            messagebox.showwarning("No Input", "Please enter some text to process.")
            return
        
        # Display in output
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, f"Processed: {input_text}")
        self.output_text.config(state=tk.DISABLED)
        
        messagebox.showinfo("Success", "Text processed successfully!")
    
    def clear_action(self):
        """Handle clear button click."""
        self.input_entry.delete(0, tk.END)
        
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)
    
    def exit_app(self):
        """Exit the application."""
        if messagebox.askokcancel("Exit", "Are you sure you want to exit?"):
            self.root.destroy()
    
    def run(self):
        """Run the main window."""
        self.root.mainloop()

def main():
    """Run the application."""
    try:
        window = SimpleMainWindow()
        window.run()
        return 0
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main()) 