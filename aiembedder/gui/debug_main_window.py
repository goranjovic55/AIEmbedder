"""
Debug script for MainWindow initialization.
"""

import sys
import traceback
import os

# Add the parent directory to sys.path so imports work correctly
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
project_dir = os.path.dirname(parent_dir)
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

def main():
    """Debug MainWindow initialization."""
    try:
        print("=== STARTING DEBUG ===")
        
        print("Importing config...")
        from utils.config import Config
        config = Config()
        print("Config initialized!")
        
        print("Importing logger...")
        from utils.logging import Logger
        logger = Logger()
        print("Logger initialized!")
        
        print("Importing progress tracker...")
        from utils.progress import ProgressTracker
        progress_tracker = ProgressTracker()
        print("Progress tracker initialized!")
        
        # Inspect MainWindow imports first without instantiating
        print("Importing MainWindow...")
        from gui.main_window import MainWindow
        print("MainWindow class imported successfully!")
        
        # Attempt to access the required dependencies
        print("Checking MainWindow dependencies...")
        
        print("Checking TextProcessingPipeline...")
        from processing.pipeline import TextProcessingPipeline
        print("TextProcessingPipeline imported successfully!")
        
        print("Checking VectorGenerator...")
        from vector.generator import VectorGenerator
        print("VectorGenerator imported successfully!")
        
        print("Checking VectorDatabase...")
        from vector.database import VectorDatabase
        print("VectorDatabase imported successfully!")
        
        print("Checking ProcessorFactory...")
        from processors.processor_factory import ProcessorFactory
        print("ProcessorFactory imported successfully!")
        
        # Now try to initialize MainWindow with explicit args
        print("Initializing MainWindow with explicit args...")
        window = MainWindow(
            config=config,
            logger=logger,
            progress_tracker=progress_tracker
        )
        print("MainWindow initialized successfully!")
        
        # Don't run the window, just verify initialization
        print("=== DEBUG COMPLETED SUCCESSFULLY ===")
        return 0
        
    except ImportError as e:
        print(f"IMPORT ERROR: {str(e)}")
        traceback.print_exc()
        return 1
    except AttributeError as e:
        print(f"ATTRIBUTE ERROR: {str(e)}")
        print("This might be because of a NoneType object being accessed!")
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"UNEXPECTED ERROR: {str(e)}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main()) 