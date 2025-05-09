"""
Text processing pipeline that combines cleaning, chunking, and deduplication.
"""

from typing import List, Optional, Dict, Any
import logging
from pathlib import Path
import time

from aiembedder.processing.text_cleaner import TextCleaner
from aiembedder.processing.text_chunker import TextChunker
from aiembedder.processing.deduplicator import Deduplicator
from aiembedder.processing.chunk_enhancer import ChunkEnhancer
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
        optimize_for_gpt4all: bool = True,
        progress_tracker: Optional[ProgressTracker] = None
    ):
        """Initialize the pipeline.
        
        Args:
            cleaning_level: Level of text cleaning (light, medium, aggressive)
            chunk_size: Size of text chunks in tokens
            chunk_overlap: Overlap between chunks in tokens
            similarity_threshold: Threshold for considering chunks as duplicates
            use_gpu: Whether to use GPU for deduplication
            optimize_for_gpt4all: Whether to optimize chunks for GPT4All embeddings
            progress_tracker: Optional progress tracker
        """
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing text processing pipeline")
        
        self.cleaner = TextCleaner()
        self.chunker = TextChunker()
        self.deduplicator = Deduplicator(use_gpu=use_gpu)
        self.enhancer = ChunkEnhancer() if optimize_for_gpt4all else None
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
        self.optimize_for_gpt4all = optimize_for_gpt4all
        
        self.logger.info(
            f"Pipeline initialized with cleaning_level={cleaning_level}, "
            f"chunk_size={chunk_size}, chunk_overlap={chunk_overlap}, "
            f"similarity_threshold={similarity_threshold}, use_gpu={use_gpu}, "
            f"optimize_for_gpt4all={optimize_for_gpt4all}"
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
                total=5 if self.optimize_for_gpt4all else 4,  # +1 step if enhancing
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
            
            # Get document context from metadata if available
            document_context = {}
            if metadata:
                # Extract document info from metadata
                if 'source' in metadata:
                    document_context['source'] = metadata['source']
                if 'file_name' in metadata:
                    document_context['file_name'] = metadata['file_name']
                if 'file_path' in metadata:
                    document_context['file_path'] = metadata['file_path']
                if 'file_size' in metadata:
                    document_context['file_size'] = metadata['file_size']
            
            # Calculate estimated content length (character count)
            estimated_content_length = sum(len(chunk) for chunk in unique_chunks)
            
            # Process each chunk with enhanced metadata
            for i, chunk in enumerate(unique_chunks):
                # Calculate chunk position information for better context
                is_first = i == 0
                is_last = i == len(unique_chunks) - 1
                position = "beginning" if is_first else "end" if is_last else "middle"
                
                # Create enhanced metadata for better GPT4All embeddings
                chunk_data = {
                    "text": chunk,
                    "chunk_index": i,
                    "total_chunks": len(unique_chunks),
                    "position": position,
                    "is_first_chunk": is_first,
                    "is_last_chunk": is_last,
                    "cleaning_level": self.cleaning_level,
                    "chunk_size": self.chunk_size,
                    "chunk_overlap": self.chunk_overlap,
                    "content_length": len(chunk),
                    "doc_content_length": estimated_content_length,
                    "processing_timestamp": str(int(time.time()))
                }
                
                # Add document context from metadata
                if document_context:
                    chunk_data.update(document_context)
                
                # Add any additional custom metadata
                if metadata:
                    # Only add metadata fields we haven't already processed
                    for key, value in metadata.items():
                        if key not in document_context and key not in chunk_data:
                            chunk_data[key] = value
                
                processed_chunks.append(chunk_data)
            
            # Enhance chunks for GPT4All if enabled
            if self.optimize_for_gpt4all and self.enhancer:
                self.progress_tracker.update_task(task_id, current=5, status="Optimizing for GPT4All")
                self.logger.info("Enhancing chunks for GPT4All embeddings")
                
                enhanced_chunks = []
                for chunk_data in processed_chunks:
                    chunk_text = chunk_data.pop("text")  # Extract text from metadata
                    enhanced_chunk = self.enhancer.enhance_chunk(chunk_text, chunk_data)
                    enhanced_chunks.append(enhanced_chunk)
                
                processed_chunks = enhanced_chunks
                self.logger.info(f"Enhanced {len(processed_chunks)} chunks for GPT4All")
            
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
                "file_type": file_path.suffix.lstrip('.').lower(),
                "modified_time": str(int(file_path.stat().st_mtime))
            }
            
            # Try to extract title from filename
            title = file_path.stem.replace('_', ' ').replace('-', ' ')
            file_metadata["title"] = title
            
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
            "optimize_for_gpt4all": self.optimize_for_gpt4all,
            "available_cleaning_levels": self.cleaner.get_cleaning_levels(),
        } 