#!/usr/bin/env python
"""
Test script to debug text chunking in AIEmbedder.
"""

import os
import sys
from pathlib import Path
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aiembedder.processing.text_chunker import TextChunker
from aiembedder.processing.pipeline import TextProcessingPipeline

def test_text_chunker_directly():
    """Test the TextChunker directly with controlled input."""
    logger.info("Testing TextChunker directly...")
    
    chunker = TextChunker()
    
    # Create a test text with known sentence structure
    sentences = ["This is test sentence " + str(i) + "." for i in range(1, 101)]
    test_text = " ".join(sentences)
    
    logger.info(f"Created test text with {len(sentences)} sentences and {len(test_text.split())} words")
    
    # Test with different chunk sizes and overlaps
    test_configs = [
        {"chunk_size": 10, "chunk_overlap": 2},
        {"chunk_size": 20, "chunk_overlap": 5},
        {"chunk_size": 50, "chunk_overlap": 10},
        {"chunk_size": 100, "chunk_overlap": 20},
    ]
    
    for config in test_configs:
        chunk_size = config["chunk_size"]
        chunk_overlap = config["chunk_overlap"]
        
        logger.info(f"Testing with chunk_size={chunk_size}, chunk_overlap={chunk_overlap}")
        
        try:
            start_time = time.time()
            chunks = chunker.chunk(test_text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
            end_time = time.time()
            
            logger.info(f"Created {len(chunks)} chunks in {end_time - start_time:.2f} seconds")
            
            # Log chunk sizes
            chunk_sizes = [len(chunk.split()) for chunk in chunks]
            logger.info(f"Chunk sizes (words): {chunk_sizes}")
            
            # Check if chunks are respecting size limits
            oversized = [size for size in chunk_sizes if size > chunk_size]
            if oversized:
                logger.warning(f"Found {len(oversized)} chunks exceeding chunk_size: {oversized}")
            
        except Exception as e:
            logger.error(f"Error during chunking: {str(e)}")

def test_with_real_file(file_path):
    """Test chunking with a real file.
    
    Args:
        file_path: Path to the file to test
    """
    logger.info(f"Testing with real file: {file_path}")
    
    if not os.path.exists(file_path):
        logger.error(f"File does not exist: {file_path}")
        return
    
    # Read the file
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        logger.error(f"Error reading file: {str(e)}")
        return
    
    logger.info(f"Read {len(text)} characters, {len(text.split())} words from file")
    
    # Test chunking directly
    chunker = TextChunker()
    
    # Test with different chunk sizes
    test_configs = [
        {"chunk_size": 100, "chunk_overlap": 20},
        {"chunk_size": 200, "chunk_overlap": 50},
        {"chunk_size": 500, "chunk_overlap": 100},
    ]
    
    for config in test_configs:
        chunk_size = config["chunk_size"]
        chunk_overlap = config["chunk_overlap"]
        
        logger.info(f"Testing with chunk_size={chunk_size}, chunk_overlap={chunk_overlap}")
        
        try:
            start_time = time.time()
            chunks = chunker.chunk(text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
            end_time = time.time()
            
            logger.info(f"Created {len(chunks)} chunks in {end_time - start_time:.2f} seconds")
            
            if len(chunks) == 1:
                logger.warning("Only one chunk was created! This suggests a problem with chunking.")
                logger.info(f"First chunk size (words): {len(chunks[0].split())}")
            
        except Exception as e:
            logger.error(f"Error during chunking: {str(e)}")
    
    # Test with the pipeline
    test_pipeline(text)

def test_pipeline(text):
    """Test the entire processing pipeline.
    
    Args:
        text: Text to process
    """
    logger.info("Testing the full TextProcessingPipeline...")
    
    # Test with different settings
    test_configs = [
        {"cleaning_level": "light", "chunk_size": 200, "chunk_overlap": 50},
        {"cleaning_level": "medium", "chunk_size": 300, "chunk_overlap": 50},
    ]
    
    for config in test_configs:
        cleaning_level = config["cleaning_level"]
        chunk_size = config["chunk_size"]
        chunk_overlap = config["chunk_overlap"]
        
        logger.info(f"Testing pipeline with cleaning_level={cleaning_level}, "
                   f"chunk_size={chunk_size}, chunk_overlap={chunk_overlap}")
        
        try:
            pipeline = TextProcessingPipeline(
                cleaning_level=cleaning_level,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )
            
            start_time = time.time()
            chunks = pipeline.process_text(text)
            end_time = time.time()
            
            logger.info(f"Pipeline created {len(chunks)} chunks in {end_time - start_time:.2f} seconds")
            
            if len(chunks) == 1:
                logger.warning("Pipeline created only one chunk! This suggests a problem.")
                
        except Exception as e:
            logger.error(f"Error during pipeline processing: {str(e)}")

def main():
    """Main function."""
    # First test with controlled input
    test_text_chunker_directly()
    
    # Then test with real file if provided
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        test_with_real_file(file_path)
    else:
        logger.info("No file path provided. Skipping file test.")
        logger.info("Usage: python test_chunking.py [file_path]")

if __name__ == "__main__":
    main() 