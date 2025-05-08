"""
Tests for document processors.
"""

import os
import tempfile
from pathlib import Path

import pytest

from aiembedder.processors.base_processor import BaseProcessor
from aiembedder.processors.html_processor import HTMLProcessor
from aiembedder.processors.doc_processor import DocProcessor
from aiembedder.processors.pdf_processor import PDFProcessor
from aiembedder.processors.text_processor import TextProcessor
from aiembedder.processors.processor_factory import ProcessorFactory
from aiembedder.utils.errors import FileAccessError, ProcessingError
from aiembedder.utils.logging import Logger

# Test HTML Processor
def test_html_processor():
    """Test HTML processor."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test HTML file
        html_content = """
        <html>
            <head>
                <title>Test Page</title>
                <script>console.log('test');</script>
                <style>body { color: black; }</style>
            </head>
            <body>
                <h1>Test Heading</h1>
                <p>Test paragraph 1</p>
                <p>Test paragraph 2</p>
            </body>
        </html>
        """
        html_file = os.path.join(temp_dir, "test.html")
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Test processor
        processor = HTMLProcessor()
        text = processor.process(html_file)
        
        assert "Test Heading" in text
        assert "Test paragraph 1" in text
        assert "Test paragraph 2" in text
        assert "console.log" not in text
        assert "color: black" not in text

# Test DOC Processor
def test_doc_processor():
    """Test DOC processor."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test DOC file
        doc = Document()
        doc.add_paragraph("Test paragraph 1")
        doc.add_paragraph("Test paragraph 2")
        
        doc_file = os.path.join(temp_dir, "test.docx")
        doc.save(doc_file)
        
        # Test processor
        processor = DocProcessor()
        text = processor.process(doc_file)
        
        assert "Test paragraph 1" in text
        assert "Test paragraph 2" in text

# Test PDF Processor
def test_pdf_processor():
    """Test PDF processor."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test PDF file
        pdf_file = os.path.join(temp_dir, "test.pdf")
        with open(pdf_file, 'wb') as f:
            # Create a simple PDF with PyPDF2
            writer = PdfWriter()
            page = writer.add_page()
            page.merge_page(PdfReader(BytesIO(b'%PDF-1.4\nTest content')).pages[0])
            writer.write(f)
        
        # Test processor
        processor = PDFProcessor()
        text = processor.process(pdf_file)
        
        assert "Test content" in text

# Test Text Processor
def test_text_processor():
    """Test text processor."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test text file
        text_content = "Test line 1\nTest line 2"
        text_file = os.path.join(temp_dir, "test.txt")
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write(text_content)
        
        # Test processor
        processor = TextProcessor()
        text = processor.process(text_file)
        
        assert "Test line 1" in text
        assert "Test line 2" in text

# Test Processor Factory
def test_processor_factory():
    """Test processor factory."""
    factory = ProcessorFactory()
    
    # Test supported extensions
    assert '.html' in factory.get_supported_extensions()
    assert '.docx' in factory.get_supported_extensions()
    assert '.pdf' in factory.get_supported_extensions()
    assert '.txt' in factory.get_supported_extensions()
    
    # Test processor creation
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test files
        html_file = os.path.join(temp_dir, "test.html")
        doc_file = os.path.join(temp_dir, "test.docx")
        pdf_file = os.path.join(temp_dir, "test.pdf")
        txt_file = os.path.join(temp_dir, "test.txt")
        
        # Create empty files
        for file in [html_file, doc_file, pdf_file, txt_file]:
            Path(file).touch()
        
        # Test processor creation
        assert isinstance(factory.get_processor(html_file), HTMLProcessor)
        assert isinstance(factory.get_processor(doc_file), DocProcessor)
        assert isinstance(factory.get_processor(pdf_file), PDFProcessor)
        assert isinstance(factory.get_processor(txt_file), TextProcessor)
        
        # Test unsupported file type
        with pytest.raises(ProcessingError):
            factory.get_processor(os.path.join(temp_dir, "test.xyz"))
        
        # Test file type support check
        assert factory.is_supported(html_file)
        assert factory.is_supported(doc_file)
        assert factory.is_supported(pdf_file)
        assert factory.is_supported(txt_file)
        assert not factory.is_supported(os.path.join(temp_dir, "test.xyz"))

# Test Error Handling
def test_error_handling():
    """Test error handling in processors."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Test non-existent file
        processor = TextProcessor()
        with pytest.raises(FileAccessError):
            processor.process(os.path.join(temp_dir, "nonexistent.txt"))
        
        # Test empty file
        empty_file = os.path.join(temp_dir, "empty.txt")
        Path(empty_file).touch()
        with pytest.raises(ProcessingError):
            processor.process(empty_file)
        
        # Test invalid file type
        factory = ProcessorFactory()
        with pytest.raises(ProcessingError):
            factory.get_processor(os.path.join(temp_dir, "test.xyz")) 