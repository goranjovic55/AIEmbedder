# AIEmbedder

AIEmbedder is a powerful tool for embedding documents into vector databases for semantic search. It provides a user-friendly GUI to process, analyze, and search through document collections using modern embedding techniques.

## Features

- Process multiple document formats (TXT, HTML, PDF, DOCX)
- Clean and chunk text with customizable parameters
- Remove duplicates and near-duplicates based on similarity threshold
- Generate embeddings using state-of-the-art models
- Store and query vector embeddings with ChromaDB
- User-friendly GUI with progress tracking and detailed logs

## Installation

### Prerequisites

- Python 3.8 or higher
- Tkinter (usually comes with Python)
- GPU support (optional, for faster processing)

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/aiembedder.git
   cd aiembedder
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python -m aiembedder
   ```

## Usage

### Processing Documents

1. Launch the application
2. Click "Add File" or "Add Directory" to select documents for processing
3. Configure processing options if needed
4. Click "Process Files" to start processing

### Searching

1. Click "Search" in the menu
2. Enter your search query
3. Use metadata filters if needed
4. View and explore results

## Configuration

AIEmbedder can be configured through the Settings dialog:

- **Processing**: Configure cleaning level, chunk size, and overlap
- **Database**: Set collection name and persistence directory
- **Interface**: Customize appearance and logging
- **Advanced**: Configure embedding models and log locations

## Development

### Project Structure

- `aiembedder/`: Main package
  - `gui/`: GUI components
  - `processing/`: Text processing modules
  - `vector/`: Vector database components
  - `processors/`: Document type processors
  - `utils/`: Utility functions and helpers

### Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 