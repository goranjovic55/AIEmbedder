"""
Main entry point for AIEmbedder.
"""

import sys
import traceback
from pathlib import Path

def main():
    """Main entry point for AIEmbedder."""
    try:
        print("Starting AIEmbedder...")
        
        # Initialize core components
        print("Importing Config...")
        from aiembedder.utils.config import Config
        print("Initializing Config...")
        config = Config()
        print("Config initialized successfully!")
        
        print("Importing Logger...")
        from aiembedder.utils.logging import Logger
        print("Initializing Logger...")
        logger = Logger()
        print("Logger initialized successfully!")
        
        print("Importing ProgressTracker...")
        from aiembedder.utils.progress import ProgressTracker
        print("Initializing ProgressTracker...")
        progress_tracker = ProgressTracker()
        print("ProgressTracker initialized successfully!")
        
        # Set up logging level from config
        print("Setting up logging level...")
        log_level = config.get("gui", "log_level", "INFO")
        logger.set_level(log_level)
        print("Logging level set successfully!")
        
        # Log startup
        print("Logging startup message...")
        logger.info("Starting AIEmbedder...")
        print("Startup message logged successfully!")
        
        # Initialize GUI
        print("Importing MainWindow...")
        from aiembedder.gui.main_window import MainWindow
        print("Initializing MainWindow...")
        window = MainWindow(config=config, logger=logger, progress_tracker=progress_tracker)
        print("MainWindow initialized successfully!")
        
        print("Running MainWindow...")
        window.run()
        print("MainWindow exited successfully!")
        
        return 0
        
    except ImportError as e:
        print(f"Import error: {str(e)}")
        traceback.print_exc()
        return 1
    except AttributeError as e:
        print(f"Attribute error: {str(e)}")
        print("This might be because of a NoneType object being accessed!")
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main()) 