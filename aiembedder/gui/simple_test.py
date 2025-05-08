"""
Simple test window to verify Tkinter functionality.
"""

import tkinter as tk
from tkinter import ttk
import sys

def main():
    """Show a simple window."""
    try:
        # Create the root window
        root = tk.Tk()
        root.title("AIEmbedder Test")
        root.geometry("400x200")
        
        # Create a frame
        frame = ttk.Frame(root, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Add a label
        label = ttk.Label(frame, text="AIEmbedder Test Window", font=("Helvetica", 14))
        label.pack(pady=20)
        
        # Add a button
        button = ttk.Button(frame, text="Close", command=root.destroy)
        button.pack(pady=10)
        
        # Run the main loop
        root.mainloop()
        
        return 0
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main()) 