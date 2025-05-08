"""
Main entry point for AIEmbedder application.
"""

import sys
import traceback
import logging
from pathlib import Path

def main():
    """Run AIEmbedder application."""
    try:
        print("Starting AIEmbedder...")
        
        # Initialize core components
        print("Importing Config...")
        from aiembedder.utils.config import Config
        print("Initializing Config...")
        config = Config()
        print("Config initialized!")
        
        print("Importing Logger...")
        from aiembedder.utils.logging import Logger
        print("Initializing Logger...")
        logger = Logger()
        print("Logger initialized!")
        
        print("Importing ProgressTracker...")
        from aiembedder.utils.progress import ProgressTracker
        print("Initializing ProgressTracker...")
        progress_tracker = ProgressTracker()
        print("ProgressTracker initialized!")
        
        # Set logging level
        print("Setting log level...")
        log_level_str = config.get("gui", "log_level", "INFO")
        logger.set_level(log_level_str)
        print(f"Log level set to {log_level_str}!")
        
        # Log startup
        print("Logging startup message...")
        logger.info(f"Starting AIEmbedder")
        print("Startup message logged!")
        
        # Initialize GUI
        print("Importing MainWindow...")
        from aiembedder.gui.main_window import MainWindow
        print("Initializing MainWindow...")
        window = MainWindow(config=config, logger=logger, progress_tracker=progress_tracker)
        print("MainWindow initialized!")
        
        print("Running MainWindow...")
        window.run()
        print("MainWindow exited!")
        
        return 0
        
    except ImportError as e:
        print(f"Import error: {str(e)}")
        traceback.print_exc()
        return 1
    except AttributeError as e:
        print(f"Attribute error: {str(e)}")
        print("This might be because a None object is being accessed!")
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main()) 