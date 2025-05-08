# AIEmbedder Project Context

**Last Updated: 2024-03-19**

## Context Portability Guide

This PROJECT_CONTEXT.md file is designed to be portable across projects. To use this context system in a new project:

### Metadata
```json
{
  "context_version": "1.0",
  "project_id": "AIEmbedder",
  "initialized_date": "2024-03-19",
  "template_version": "1.0" 
}
```

## Project Overview
AIEmbedder is a specialized tool designed to process various document formats (HTML, DOC/DOCX, PDF, TXT) and convert them into vector embeddings for use with LocalDocsV3. The project aims to provide a user-friendly interface for document processing while maintaining high performance and accuracy.

## Current State
- Project structure and blueprints have been created
- Development roadmap has been established
- Dependencies have been defined in requirements.txt
- Core architecture has been designed

## Project Structure
```
aiembedder/
├── processors/          # Document format processors
├── processing/          # Text processing components
├── vector/             # Vector generation and database
├── gui/                # User interface components
├── utils/              # Utility functions
└── tests/              # Test suite
```

## Dependencies
- Core: python-docx, PyPDF2, beautifulsoup4, nltk, langchain, sentence-transformers, chromadb, gpt4all
- GUI: tkinter, ttkthemes
- Processing: numpy, pandas, torch, transformers
- Development: pytest, black, flake8, mypy

## Development Timeline
1. Week 1: Project Setup and Core Infrastructure
2. Week 2: Document Processing Implementation
3. Week 3: Vector Database Implementation
4. Week 4: GUI Development
5. Week 5: Integration and Testing
6. Week 6: Deployment and Release

## Next Steps
1. Set up development environment
2. Implement core infrastructure
3. Begin document processor development
4. Create initial test suite

## Technical Requirements
- Python 3.10+
- CUDA support (optional)
- 4GB+ RAM
- 1GB+ free disk space

## Performance Targets
- Processing speed: 1000 chunks/minute
- Memory usage: < 4GB
- GPU utilization: > 80%
- Error rate: < 1%

## Quality Standards
- Test coverage: > 90%
- Documentation completeness
- User satisfaction
- Bug resolution time

## Risk Management
- Performance issues with large documents
- Memory constraints
- GPU compatibility
- Database scaling

## Success Criteria
1. All document formats processed successfully
2. Vector database generation working
3. GUI responsive and user-friendly
4. Performance targets met
5. Documentation complete

## Documentation Status
- [x] Project Context
- [x] System Architecture Blueprint
- [x] Interface Blueprint
- [x] Data Flow Blueprint
- [x] Development Roadmap
- [ ] API Documentation
- [ ] User Guide
- [ ] Installation Guide

## Development Guidelines
1. Follow PEP 8 style guide
2. Write unit tests for all components
3. Document all public APIs
4. Use type hints
5. Implement error handling
6. Add logging

## Testing Strategy
1. Unit tests for all components
2. Integration tests for pipelines
3. Performance tests
4. User acceptance testing

## Deployment Strategy
1. Create virtual environment
2. Install dependencies
3. Configure settings
4. Run tests
5. Package application
6. Create installer

## Maintenance Plan
1. Regular updates
2. Bug fixes
3. Performance optimization
4. Feature additions
5. Documentation updates

## Future Enhancements
1. Additional document formats
2. Advanced text cleaning
3. Custom chunking
4. API interface
5. Performance optimization
6. User experience improvements

## 1. Project Overview

**Project Name:** AIEmbedder  
**Description:** A document preprocessing and embedding tool that creates GPT4All LocalDocsV3-compatible vector databases from various document formats.

**Goals:**
- Support multiple document formats (HTML, DOC, DOCX, PDF, TXT)
- Create LocalDocsV3-compatible vector databases
- Provide GPU-accelerated processing
- Maintain simple GUI interface
- Enable configurable document processing settings
- Support real-time progress tracking

**Scope:**
- Document preprocessing and cleaning
- Text chunking and deduplication
- Vector database creation
- GUI for configuration and monitoring
- GPU acceleration support
- Progress tracking and logging

**Key Components:**
- Document Processors (HTML, DOC/DOCX, PDF, TXT)
- Text Cleaner and Chunker
- Vector Database Generator
- GUI Interface
- Progress Tracker

## 2. Project Focus

**Current Focus:** Core Implementation  
**Started:** 2024-03-19  
**Status:** Initial Development

**Tasks:**
- ✅ Define project requirements and architecture
- ❌ Implement document processors
- ❌ Implement text cleaning and chunking
- ❌ Implement vector database generation
- ❌ Implement GUI interface
- ❌ Implement progress tracking
- ❌ Add GPU acceleration support

**Impact Map:**
- **Document Processing:** Multiple format support with proper parsing
- **Text Processing:** Efficient cleaning and chunking
- **Vector Database:** LocalDocsV3 compatibility
- **User Interface:** Intuitive configuration and monitoring
- **Performance:** GPU acceleration for faster processing

**Cross-Component Dependencies:**
```
┌────────────────┐      ┌─────────────────┐
│                │      │                 │
│  GUI Interface │◄─────┤  Configuration  │
│                │      │                 │
└────────┬───────┘      └────────┬────────┘
         │                       │
         ▼                       ▼
┌────────────────┐      ┌─────────────────┐
│                │      │                 │
│  Document      │◄─────┤  Text           │
│  Processors    │      │  Processing     │
│                │      │                 │
└────────┬───────┘      └────────┬────────┘
         │                       │
         ▼                       ▼
┌────────────────┐      ┌─────────────────┐
│                │      │                 │
│  Vector        │◄─────┤  Progress       │
│  Database      │      │  Tracking       │
│                │      │                 │
└────────────────┘      └─────────────────┘
```

## 3. System Architecture

**Architecture Pattern:** Modular Pipeline Architecture

The AIEmbedder application follows a modular pipeline architecture with:

1. **Input Layer** - Document loading and format detection
2. **Processing Layer** - Text cleaning and chunking
3. **Vector Layer** - Embedding generation and database creation
4. **Interface Layer** - GUI and progress tracking

**Key Dependencies:**
- BeautifulSoup4 for HTML processing
- python-docx for DOC/DOCX processing
- PyPDF2 for PDF processing
- langchain for text processing
- GPT4AllEmbeddings for vector generation
- Chroma for database management
- tkinter for GUI
- torch for GPU acceleration
- tqdm for progress tracking

**Data Flow:**
1. User selects input/output folders and settings via GUI
2. Documents are loaded and processed based on format
3. Text is cleaned and chunked according to settings
4. Chunks are embedded and stored in vector database
5. Progress is tracked and displayed in real-time

## 4. Component Overview

### Document Processors
- **HTMLProcessor** (`processors/html_processor.py`): HTML parsing with BeautifulSoup
- **DocProcessor** (`processors/doc_processor.py`): DOC/DOCX processing with python-docx
- **PdfProcessor** (`processors/pdf_processor.py`): PDF processing with PyPDF2
- **TextProcessor** (`processors/text_processor.py`): Plain text processing

### Text Processing
- **TextCleaner** (`processing/text_cleaner.py`): Text cleaning with configurable levels
- **TextChunker** (`processing/text_chunker.py`): Text chunking with overlap
- **Deduplicator** (`processing/deduplicator.py`): Chunk deduplication with GPU support

### Vector Database
- **VectorGenerator** (`vector/vector_generator.py`): Embedding generation with GPT4AllEmbeddings
- **DatabaseManager** (`vector/database_manager.py`): Chroma database management

### Interface
- **MainWindow** (`gui/main_window.py`): Main application window
- **SettingsPanel** (`gui/settings_panel.py`): Configuration interface
- **ProgressTracker** (`gui/progress_tracker.py`): Progress monitoring

## 5. Implementation Details

### Document Processing
```python
class DocumentProcessor:
    def process(self, file_path: str) -> str:
        """Process document and return text content"""
        pass

class HTMLProcessor(DocumentProcessor):
    def process(self, file_path: str) -> str:
        with open(file_path, "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file, "html.parser")
            for element in soup(["script", "style", "comment"]):
                element.decompose()
            return soup.get_text(separator=" ", strip=True)
```

### Text Processing
```python
class TextCleaner:
    def clean(self, text: str, level: str) -> str:
        """Clean text based on specified level"""
        pass

class TextChunker:
    def chunk(self, text: str, size: int, overlap: int) -> List[str]:
        """Split text into chunks with overlap"""
        pass
```

### Vector Database
```python
class VectorGenerator:
    def generate(self, chunks: List[str]) -> List[float]:
        """Generate embeddings for text chunks"""
        pass

class DatabaseManager:
    def create_database(self, chunks: List[str], embeddings: List[float]):
        """Create LocalDocsV3-compatible database"""
        pass
```

## 6. Configuration Options

### Document Processing
- Input folder selection
- Output folder selection
- Collection name for database

### Text Processing
- Cleaning level (light, medium, aggressive)
- Chunk size (200-400 tokens)
- Chunk overlap (50-100 tokens)
- Deduplication threshold (0.9-0.99)
- Stopword removal option

### Vector Database
- Database creation toggle
- GPU acceleration toggle
- Progress tracking options

## 7. Development Roadmap

### Phase 1: Core Implementation
- Basic document processing
- Text cleaning and chunking
- Simple GUI interface

### Phase 2: Vector Database
- LocalDocsV3 compatibility
- Database management
- Progress tracking

### Phase 3: Optimization
- GPU acceleration
- Performance improvements
- Enhanced error handling

### Phase 4: Polish
- UI improvements
- Additional format support
- Documentation

## 8. Known Limitations

**HTML Processing:**
- Static HTML only (no JavaScript rendering)
- May miss dynamic content

**Performance:**
- Large corpora may be slow
- GPU acceleration limited to deduplication

**Database Compatibility:**
- Requires testing with GPT4All
- May need schema adjustments

## 9. Development Environment

**Language:** Python 3.10+
**Dependencies:**
- beautifulsoup4
- python-docx
- PyPDF2
- langchain
- gpt4all
- chromadb
- torch
- tkinter
- tqdm

**Setup:**
```bash
pip install beautifulsoup4 python-docx PyPDF2 langchain gpt4all chromadb torch tqdm
python -m nltk.downloader punkt wordnet stopwords
```

## 10. Decision Log

| Date | Component | Decision | Rationale |
|------|-----------|----------|-----------|
| 2024-03-19 | Architecture | Modular Pipeline | Clear separation of concerns |
| 2024-03-19 | Document Processing | Format-specific processors | Better maintainability |
| 2024-03-19 | Vector Database | LocalDocsV3 compatibility | Direct GPT4All integration |
| 2024-03-19 | GUI | tkinter | Simple and lightweight |
| 2024-03-19 | Progress Tracking | tqdm | Real-time progress display | 