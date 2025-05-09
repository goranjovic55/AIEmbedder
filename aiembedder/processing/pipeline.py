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
        respect_document_structure: bool = True,
        chunk_flexibility_percent: int = 30,
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
            respect_document_structure: Whether to respect document structure when chunking
            chunk_flexibility_percent: How much chunk size can vary to align with document structure
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
        if not 0 <= chunk_flexibility_percent <= 100:
            raise ProcessingError("Chunk flexibility percent must be between 0 and 100")
        
        self.cleaning_level = cleaning_level
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.similarity_threshold = similarity_threshold
        self.optimize_for_gpt4all = optimize_for_gpt4all
        self.respect_document_structure = respect_document_structure
        self.chunk_flexibility_percent = chunk_flexibility_percent
        
        self.logger.info(
            f"Pipeline initialized with cleaning_level={cleaning_level}, "
            f"chunk_size={chunk_size}, chunk_overlap={chunk_overlap}, "
            f"similarity_threshold={similarity_threshold}, use_gpu={use_gpu}, "
            f"optimize_for_gpt4all={optimize_for_gpt4all}, "
            f"respect_document_structure={respect_document_structure}, "
            f"chunk_flexibility_percent={chunk_flexibility_percent}"
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
            
            # Chunk text using structure-aware chunking if enabled
            self.progress_tracker.update_task(task_id, current=2, status="Chunking text")
            
            if self.respect_document_structure:
                self.logger.info("Using structure-aware chunking with flexibility")
                chunk_data = self.chunker.chunk_with_structure(
                    cleaned_text,
                    target_chunk_size=self.chunk_size,
                    chunk_overlap=self.chunk_overlap,
                    flexibility_percent=self.chunk_flexibility_percent
                )
                # Extract just the text for deduplication
                chunks = [chunk["text"] for chunk in chunk_data]
            else:
                # Use regular chunking
                chunks = self.chunker.chunk(
                    cleaned_text,
                    chunk_size=self.chunk_size,
                    chunk_overlap=self.chunk_overlap
                )
                # Create simple chunk data
                chunk_data = [{"text": chunk} for chunk in chunks]
            
            # Deduplicate chunks
            self.progress_tracker.update_task(task_id, current=3, status="Deduplicating chunks")
            
            # Find indices of unique chunks
            unique_indices = self.deduplicator.deduplicate_indices(
                chunks,
                threshold=self.similarity_threshold
            )
            
            # Filter to unique chunks
            unique_chunk_data = [chunk_data[i] for i in unique_indices]
            
            # Add metadata
            self.progress_tracker.update_task(task_id, current=4, status="Adding metadata")
            processed_chunks = []
            
            # Get document context from metadata if available
            document_context = {}
            if metadata:
                # Extract document info from metadata
                for key in ['source', 'file_name', 'file_path', 'file_size']:
                    if key in metadata:
                        document_context[key] = metadata[key]
            
            # Calculate estimated content length (character count)
            estimated_content_length = sum(len(chunk["text"]) for chunk in unique_chunk_data)
            
            # Process each chunk with enhanced metadata
            for i, chunk_item in enumerate(unique_chunk_data):
                # Extract text and any existing chunk metadata
                chunk_text = chunk_item["text"]
                
                # Calculate chunk position information for better context
                is_first = i == 0
                is_last = i == len(unique_chunk_data) - 1
                position = chunk_item.get("section", "middle")
                if position == "Start":
                    position = "beginning"
                elif position == "End of Document":
                    position = "end"
                
                # Create enhanced metadata for better GPT4All embeddings
                chunk_data = {
                    "text": chunk_text,
                    "chunk_index": i,
                    "total_chunks": len(unique_chunk_data),
                    "position": position,
                    "is_first_chunk": is_first,
                    "is_last_chunk": is_last,
                    "cleaning_level": self.cleaning_level,
                    "chunk_size": self.chunk_size,
                    "chunk_overlap": self.chunk_overlap,
                    "content_length": len(chunk_text),
                    "doc_content_length": estimated_content_length,
                    "processing_timestamp": str(int(time.time()))
                }
                
                # Add section info if it exists
                if "section" in chunk_item:
                    chunk_data["section"] = chunk_item["section"]
                
                # Add token count if it exists
                if "token_count" in chunk_item:
                    chunk_data["token_count"] = chunk_item["token_count"]
                
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
            "optimize_for_gpt4all": self.optimize_for_gpt4all,
            "respect_document_structure": self.respect_document_structure,
            "chunk_flexibility_percent": self.chunk_flexibility_percent
        } 