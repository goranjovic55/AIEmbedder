# AIEmbedder Project Blueprints

## 1. System Architecture Blueprint

### 1.1 High-Level Architecture
```
┌─────────────────────────────────────────────────────────┐
│                      GUI Layer                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │
│  │ MainWindow  │  │SettingsPanel│  │ ProgressTracker │  │
│  └─────────────┘  └─────────────┘  └─────────────────┘  │
└───────────────────────────┬─────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────┐
│                    Processing Pipeline                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │
│  │  Document   │  │    Text     │  │     Vector      │  │
│  │ Processors  │─►│  Processing │─►│    Database     │  │
│  └─────────────┘  └─────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 1.2 Component Interactions
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Config    │────►│  Document   │────►│    Text     │
│  Settings   │     │ Processors  │     │  Processing │
└─────────────┘     └─────────────┘     └─────────────┘
                                                    │
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Progress   │◄────│    Vector   │◄────│   Chunks    │
│  Tracking   │     │  Database   │     │             │
└─────────────┘     └─────────────┘     └─────────────┘
```

## 2. Component Blueprints

### 2.1 Document Processors

#### 2.1.1 HTML Processor
- **Purpose**: Extract text from HTML files
- **Dependencies**: BeautifulSoup4
- **Key Features**:
  - Remove script, style, and comment tags
  - Preserve text structure
  - Handle encoding issues
  - Error handling for malformed HTML

#### 2.1.2 DOC/DOCX Processor
- **Purpose**: Extract text from Microsoft Word documents
- **Dependencies**: python-docx
- **Key Features**:
  - Handle both .doc and .docx formats
  - Preserve document structure
  - Extract metadata
  - Handle embedded objects

#### 2.1.3 PDF Processor
- **Purpose**: Extract text from PDF files
- **Dependencies**: PyPDF2
- **Key Features**:
  - Handle multi-page documents
  - Preserve text layout
  - Extract metadata
  - Handle encrypted PDFs

#### 2.1.4 Text Processor
- **Purpose**: Process plain text files
- **Dependencies**: None
- **Key Features**:
  - Handle various encodings
  - Basic text cleaning
  - Line ending normalization

### 2.2 Text Processing

#### 2.2.1 Text Cleaner
- **Purpose**: Clean and normalize text
- **Dependencies**: NLTK
- **Cleaning Levels**:
  - Light: Basic punctuation and whitespace
  - Medium: Case normalization, stopword removal
  - Aggressive: Lemmatization, special character removal

#### 2.2.2 Text Chunker
- **Purpose**: Split text into overlapping chunks
- **Dependencies**: langchain
- **Features**:
  - Configurable chunk size (200-400 tokens)
  - Adjustable overlap (50-100 tokens)
  - Sentence boundary awareness
  - Paragraph preservation

#### 2.2.3 Deduplicator
- **Purpose**: Remove duplicate chunks
- **Dependencies**: sentence-transformers, torch
- **Features**:
  - GPU-accelerated similarity detection
  - Configurable threshold (0.9-0.99)
  - Batch processing
  - Memory-efficient processing

### 2.3 Vector Database

#### 2.3.1 Vector Generator
- **Purpose**: Generate embeddings for text chunks
- **Dependencies**: GPT4AllEmbeddings
- **Features**:
  - LocalDocsV3 compatibility
  - Batch processing
  - Progress tracking
  - Error handling

#### 2.3.2 Database Manager
- **Purpose**: Manage vector database
- **Dependencies**: Chroma
- **Features**:
  - SQLite backend
  - Metadata storage
  - Collection management
  - Database persistence

### 2.4 GUI Components

#### 2.4.1 Main Window
- **Purpose**: Main application interface
- **Dependencies**: tkinter
- **Features**:
  - File/folder selection
  - Process control
  - Status display
  - Error reporting

#### 2.4.2 Settings Panel
- **Purpose**: Configuration interface
- **Dependencies**: tkinter
- **Features**:
  - Processing options
  - Cleaning settings
  - Chunking parameters
  - Database options

#### 2.4.3 Progress Tracker
- **Purpose**: Monitor processing progress
- **Dependencies**: tqdm
- **Features**:
  - Real-time progress bars
  - Status updates
  - Error logging
  - Completion notification

## 3. Data Flow Blueprint

### 3.1 Document Processing Flow
```
Input File
    │
    ▼
Format Detection
    │
    ▼
Document Processor
    │
    ▼
Text Extraction
    │
    ▼
Text Cleaner
    │
    ▼
Text Chunker
    │
    ▼
Deduplicator
    │
    ▼
Vector Generator
    │
    ▼
Database Manager
    │
    ▼
Output Files
```

### 3.2 Configuration Flow
```
User Input
    │
    ▼
Settings Validation
    │
    ▼
Configuration Storage
    │
    ▼
Component Configuration
    │
    ▼
Processing Pipeline
```

## 4. File Structure Blueprint

```
aiembedder/
├── processors/
│   ├── __init__.py
│   ├── html_processor.py
│   ├── doc_processor.py
│   ├── pdf_processor.py
│   └── text_processor.py
├── processing/
│   ├── __init__.py
│   ├── text_cleaner.py
│   ├── text_chunker.py
│   └── deduplicator.py
├── vector/
│   ├── __init__.py
│   ├── vector_generator.py
│   └── database_manager.py
├── gui/
│   ├── __init__.py
│   ├── main_window.py
│   ├── settings_panel.py
│   └── progress_tracker.py
├── utils/
│   ├── __init__.py
│   ├── config.py
│   └── logging.py
├── tests/
│   ├── __init__.py
│   ├── test_processors.py
│   ├── test_processing.py
│   └── test_vector.py
├── main.py
├── requirements.txt
└── README.md
```

## 5. Configuration Blueprint

### 5.1 Processing Settings
```python
PROCESSING_CONFIG = {
    "cleaning_level": "medium",  # light, medium, aggressive
    "chunk_size": 400,          # 200-400 tokens
    "chunk_overlap": 50,        # 50-100 tokens
    "min_chunk_length": 50,     # Minimum chunk size
    "dedup_threshold": 0.95,    # 0.9-0.99
    "remove_stopwords": False,  # Stopword removal flag
}
```

### 5.2 Database Settings
```python
DATABASE_CONFIG = {
    "collection_name": "localdocs_collection",
    "persist_directory": "output/vector_db",
    "embedding_model": "all-MiniLM-L6-v2",
    "use_gpu": True,
}
```

### 5.3 GUI Settings
```python
GUI_CONFIG = {
    "window_title": "AIEmbedder",
    "window_size": "800x600",
    "theme": "default",
    "log_level": "INFO",
}
```

## 6. Error Handling Blueprint

### 6.1 Error Categories
- File Access Errors
- Processing Errors
- Database Errors
- GUI Errors

### 6.2 Error Handling Strategy
- Graceful degradation
- User-friendly error messages
- Error logging
- Recovery procedures

## 7. Testing Blueprint

### 7.1 Unit Tests
- Document processors
- Text processing
- Vector generation
- Database operations

### 7.2 Integration Tests
- Processing pipeline
- GUI functionality
- End-to-end workflows

### 7.3 Performance Tests
- Processing speed
- Memory usage
- GPU utilization

## 8. Deployment Blueprint

### 8.1 Requirements
- Python 3.10+
- CUDA support (optional)
- Required Python packages
- System dependencies

### 8.2 Installation
- Package installation
- Configuration setup
- Environment setup

### 8.3 Usage
- Command-line interface
- GUI usage
- Configuration options
- Output management 