# AIEmbedder Data Flow Blueprint

## 1. Document Processing Flow

### 1.1 Input Processing
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Input     │────►│  Format     │────►│  Document   │
│   Files     │     │ Detection   │     │ Processor   │
└─────────────┘     └─────────────┘     └─────────────┘
```

**Data Types:**
- Input: File paths (str)
- Format: File extension (str)
- Output: Raw text (str)

**Processing Steps:**
1. File path validation
2. Format detection based on extension
3. Selection of appropriate processor
4. Document loading and parsing
5. Text extraction

### 1.2 Text Processing
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Raw       │────►│   Text      │────►│   Text      │
│   Text      │     │  Cleaner    │     │  Chunker    │
└─────────────┘     └─────────────┘     └─────────────┘
```

**Data Types:**
- Input: Raw text (str)
- Intermediate: Cleaned text (str)
- Output: Text chunks (List[str])

**Processing Steps:**
1. Text cleaning based on level
2. Stopword removal (optional)
3. Text chunking with overlap
4. Chunk validation

### 1.3 Vector Processing
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Text      │────►│  Vector     │────►│  Database   │
│  Chunks     │     │ Generator   │     │  Manager    │
└─────────────┘     └─────────────┘     └─────────────┘
```

**Data Types:**
- Input: Text chunks (List[str])
- Intermediate: Embeddings (List[float])
- Output: Vector database (Chroma)

**Processing Steps:**
1. Chunk embedding generation
2. Vector database creation
3. Metadata association
4. Database persistence

## 2. Configuration Flow

### 2.1 Settings Management
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   User      │────►│ Settings    │────►│ Component   │
│   Input     │     │ Validator   │     │ Config      │
└─────────────┘     └─────────────┘     └─────────────┘
```

**Data Types:**
- Input: User settings (dict)
- Intermediate: Validated settings (dict)
- Output: Component configurations (dict)

**Processing Steps:**
1. Settings validation
2. Default value application
3. Component configuration
4. Settings persistence

### 2.2 Progress Tracking
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Component  │────►│  Progress   │────►│    GUI      │
│   Status    │     │  Tracker    │     │   Update    │
└─────────────┘     └─────────────┘     └─────────────┘
```

**Data Types:**
- Input: Component status (dict)
- Intermediate: Progress data (dict)
- Output: GUI updates (dict)

**Processing Steps:**
1. Status collection
2. Progress calculation
3. GUI update
4. Log generation

## 3. Data Structures

### 3.1 Document Metadata
```python
DocumentMetadata = {
    "file_path": str,
    "file_type": str,
    "file_size": int,
    "creation_date": datetime,
    "modification_date": datetime,
    "processing_status": str,
    "chunk_count": int,
    "error_count": int
}
```

### 3.2 Processing Configuration
```python
ProcessingConfig = {
    "cleaning_level": str,  # light, medium, aggressive
    "chunk_size": int,      # 200-400
    "chunk_overlap": int,   # 50-100
    "remove_stopwords": bool,
    "dedup_threshold": float,  # 0.9-0.99
    "use_gpu": bool
}
```

### 3.3 Vector Database Schema
```python
VectorDatabaseSchema = {
    "collection_name": str,
    "embedding_model": str,
    "chunk_metadata": {
        "source_file": str,
        "chunk_index": int,
        "chunk_text": str,
        "embedding": List[float]
    }
}
```

## 4. Error Handling Flow

### 4.1 Error Processing
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Error     │────►│  Error      │────►│  Error      │
│  Detection  │     │  Handler    │     │  Response   │
└─────────────┘     └─────────────┘     └─────────────┘
```

**Data Types:**
- Input: Error information (dict)
- Intermediate: Handled error (dict)
- Output: User response (dict)

**Processing Steps:**
1. Error detection
2. Error classification
3. Recovery attempt
4. User notification

### 4.2 Error Categories
```python
ErrorCategories = {
    "file_access": {
        "permission_denied": str,
        "file_not_found": str,
        "invalid_format": str
    },
    "processing": {
        "parsing_error": str,
        "cleaning_error": str,
        "chunking_error": str
    },
    "vector": {
        "embedding_error": str,
        "database_error": str,
        "persistence_error": str
    }
}
```

## 5. Logging Flow

### 5.1 Log Generation
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Event     │────►│   Logger    │────►│  Log File   │
│  Detection  │     │             │     │             │
└─────────────┘     └─────────────┘     └─────────────┘
```

**Data Types:**
- Input: Event information (dict)
- Intermediate: Log entry (dict)
- Output: Log file entries (text)

**Processing Steps:**
1. Event detection
2. Log entry creation
3. Log file writing
4. Log rotation

### 5.2 Log Levels
```python
LogLevels = {
    "DEBUG": 10,
    "INFO": 20,
    "WARNING": 30,
    "ERROR": 40,
    "CRITICAL": 50
}
```

## 6. Performance Monitoring

### 6.1 Metrics Collection
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Component  │────►│  Metrics    │────►│ Performance │
│  Metrics    │     │ Collector   │     │   Report    │
└─────────────┘     └─────────────┘     └─────────────┘
```

**Data Types:**
- Input: Component metrics (dict)
- Intermediate: Collected metrics (dict)
- Output: Performance report (dict)

**Processing Steps:**
1. Metric collection
2. Data aggregation
3. Report generation
4. Performance optimization

### 6.2 Key Metrics
```python
PerformanceMetrics = {
    "processing_time": float,
    "memory_usage": int,
    "gpu_utilization": float,
    "chunks_per_second": float,
    "error_rate": float
}
```

## 7. Data Persistence

### 7.1 Configuration Storage
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Current    │────►│ Config      │────►│ Config      │
│  Config     │     │ Serializer  │     │   File      │
└─────────────┘     └─────────────┘     └─────────────┘
```

**Data Types:**
- Input: Current configuration (dict)
- Intermediate: Serialized config (str)
- Output: Configuration file (json)

### 7.2 Database Persistence
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Vector     │────►│ Database    │────►│  Database   │
│  Database   │     │ Serializer  │     │   File      │
└─────────────┘     └─────────────┘     └─────────────┘
```

**Data Types:**
- Input: Vector database (Chroma)
- Intermediate: Serialized database (bytes)
- Output: Database file (sqlite) 