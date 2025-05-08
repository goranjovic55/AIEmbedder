"""
Text processing pipeline that combines cleaning, chunking, and deduplication.
"""

from typing import List, Optional, Dict, Any
import logging
from pathlib import Path

from aiembedder.processing.text_cleaner import TextCleaner
from aiembedder.processing.text_chunker import TextChunker
from aiembedder.processing.deduplicator import Deduplicator
from aiembedder.utils.errors import ProcessingError
from aiembedder.utils.progress import ProgressTracker

class TextProcessingPipeline:
    """Pipeline for processing text through cleaning, chunking, and deduplication."""
    
    def __init__(
        self,
        cleaning_level: str = "medium",
        chunk_size: int = 400,
        chunk_overlap: int = 50,
        similarity_threshold: float = 0.95,
        use_gpu: bool = True,
        progress_tracker: Optional[ProgressTracker] = None
    ):
        """Initialize the pipeline.
        
        Args:
            cleaning_level: Level of text cleaning (light, medium, aggressive)
            chunk_size: Size of text chunks in tokens
            chunk_overlap: Overlap between chunks in tokens
            similarity_threshold: Threshold for considering chunks as duplicates
            use_gpu: Whether to use GPU for deduplication
            progress_tracker: Optional progress tracker
        """
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing text processing pipeline")
        
        self.cleaner = TextCleaner()
        self.chunker = TextChunker()
        self.deduplicator = Deduplicator(use_gpu=use_gpu)
        self.progress_tracker = progress_tracker or ProgressTracker()
        
        # Validate parameters
        if cleaning_level not in self.cleaner.get_cleaning_levels():
            raise ProcessingError(f"Invalid cleaning level: {cleaning_level}")
        if chunk_size <= 0:
            raise ProcessingError("Chunk size must be positive")
        if chunk_overlap >= chunk_size:
            raise ProcessingError("Chunk overlap must be less than chunk size")
        if not 0 < similarity_threshold < 1:
            raise ProcessingError("Similarity threshold must be between 0 and 1")
        
        self.cleaning_level = cleaning_level
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.similarity_threshold = similarity_threshold
        
        self.logger.info(
            f"Pipeline initialized with cleaning_level={cleaning_level}, "
            f"chunk_size={chunk_size}, chunk_overlap={chunk_overlap}, "
            f"similarity_threshold={similarity_threshold}, use_gpu={use_gpu}"
        )
    
    def process_text(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Process text through the pipeline.
        
        Args:
            text: Text to process
            metadata: Optional metadata to attach to chunks
            
        Returns:
            List of processed chunks with metadata
        """
        try:
            # Start processing task
            task_id = self.progress_tracker.start_task(
                "text_processing",
                total=4,  # cleaning, chunking, deduplication, metadata
                status="Processing text"
            )
            
            # Clean text
            self.progress_tracker.update_task(task_id, current=1, status="Cleaning text")
            cleaned_text = self.cleaner.clean(text, self.cleaning_level)
            
            # Chunk text
            self.progress_tracker.update_task(task_id, current=2, status="Chunking text")
            chunks = self.chunker.chunk(
                cleaned_text,
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap
            )
            
            # Deduplicate chunks
            self.progress_tracker.update_task(task_id, current=3, status="Deduplicating chunks")
            unique_chunks = self.deduplicator.deduplicate(
                chunks,
                threshold=self.similarity_threshold
            )
            
            # Add metadata
            self.progress_tracker.update_task(task_id, current=4, status="Adding metadata")
            processed_chunks = []
            for i, chunk in enumerate(unique_chunks):
                chunk_data = {
                    "text": chunk,
                    "chunk_index": i,
                    "total_chunks": len(unique_chunks),
                    "cleaning_level": self.cleaning_level,
                    "chunk_size": self.chunk_size,
                    "chunk_overlap": self.chunk_overlap,
                }
                if metadata:
                    chunk_data.update(metadata)
                processed_chunks.append(chunk_data)
            
            # Complete task
            self.progress_tracker.complete_task(task_id)
            
            self.logger.info(
                f"Processed text into {len(processed_chunks)} chunks "
                f"(from {len(chunks)} before deduplication)"
            )
            return processed_chunks
            
        except Exception as e:
            self.logger.error(f"Error processing text: {str(e)}")
            if task_id:
                self.progress_tracker.add_error(task_id, str(e))
            raise ProcessingError(f"Failed to process text: {str(e)}")
    
    def process_file(
        self,
        file_path: Path,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Process text from a file through the pipeline.
        
        Args:
            file_path: Path to the file to process
            metadata: Optional metadata to attach to chunks
            
        Returns:
            List of processed chunks with metadata
        """
        try:
            if not file_path.exists():
                raise ProcessingError(f"File not found: {file_path}")
            
            # Read file
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
            
            # Add file metadata
            file_metadata = {
                "file_path": str(file_path),
                "file_name": file_path.name,
                "file_size": file_path.stat().st_size,
            }
            if metadata:
                file_metadata.update(metadata)
            
            # Process text
            return self.process_text(text, file_metadata)
            
        except Exception as e:
            self.logger.error(f"Error processing file {file_path}: {str(e)}")
            raise ProcessingError(f"Failed to process file {file_path}: {str(e)}")
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get statistics about the processing pipeline.
        
        Returns:
            Dictionary of processing statistics
        """
        return {
            "cleaning_level": self.cleaning_level,
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "similarity_threshold": self.similarity_threshold,
            "use_gpu": self.deduplicator.use_gpu,
            "available_cleaning_levels": self.cleaner.get_cleaning_levels(),
        } 