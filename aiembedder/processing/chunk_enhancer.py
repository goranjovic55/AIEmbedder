"""
Chunk enhancer for optimizing text chunks for GPT4All embeddings.
"""

import re
from typing import Dict, Any, List, Optional
import nltk
from nltk.tokenize import sent_tokenize
from nltk.stem import WordNetLemmatizer

try:
    from nltk.corpus import stopwords
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False

class ChunkEnhancer:
    """Enhances text chunks for better GPT4All embeddings."""
    
    def __init__(self):
        """Initialize the chunk enhancer."""
        # Ensure NLTK resources are available
        try:
            # First try to find resources
            try:
                nltk.data.find('tokenizers/punkt')
            except LookupError:
                # If not found, download
                print("Downloading NLTK punkt data...")
                nltk.download('punkt')
            
            try:
                nltk.data.find('corpora/stopwords')
            except LookupError:
                print("Downloading NLTK stopwords data...")
                nltk.download('stopwords')
                
            try:
                nltk.data.find('corpora/wordnet')
            except LookupError:
                print("Downloading NLTK wordnet data...")
                nltk.download('wordnet')
        except Exception as e:
            print(f"Error initializing NLTK resources: {e}")
            print("NLTK resources may need to be downloaded manually:")
            print("Run 'python -m nltk.downloader punkt stopwords wordnet'")
        
        self.lemmatizer = WordNetLemmatizer()
        self.stopwords = set(stopwords.words('english')) if NLTK_AVAILABLE else set()
    
    def enhance_chunk(self, chunk_text: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance a text chunk for better GPT4All embeddings.
        
        Args:
            chunk_text: The text content of the chunk
            metadata: The metadata associated with the chunk
            
        Returns:
            Enhanced chunk with optimized text and metadata
        """
        # Extract key information from metadata
        document_title = self._get_document_title(metadata)
        document_type = self._detect_document_type(metadata, chunk_text)
        position_info = self._get_position_info(metadata, document_type)
        
        # Extract structural elements
        headings = self._extract_headings(chunk_text)
        entities = self._extract_entities(chunk_text)
        keywords = self._extract_keywords(chunk_text)
        
        # Normalize text
        normalized_text = self._normalize_text(chunk_text)
        
        # Create context prefix
        context_prefix = self._create_context_prefix(document_title, document_type, position_info, headings)
        
        # Combine prefix with normalized text
        enhanced_text = f"{context_prefix}\n{normalized_text}"
        
        # Update metadata with extracted information
        enhanced_metadata = metadata.copy()
        enhanced_metadata.update({
            "headings": ", ".join(headings) if headings else "",
            "entities": ", ".join(entities) if entities else "",
            "keywords": ", ".join(keywords) if keywords else "",
            "document_type": document_type,
            "enhanced": True
        })
        
        # Create enhanced chunk
        enhanced_chunk = {
            "text": enhanced_text,
            **enhanced_metadata
        }
        
        return enhanced_chunk
    
    def _get_document_title(self, metadata: Dict[str, Any]) -> str:
        """Extract document title from metadata.
        
        Args:
            metadata: Chunk metadata
            
        Returns:
            Document title or source filename
        """
        if "title" in metadata:
            return metadata["title"]
        elif "file_name" in metadata:
            # Remove extension and replace underscores with spaces
            return re.sub(r'\.\w+$', '', metadata["file_name"]).replace('_', ' ')
        elif "source" in metadata:
            # Extract filename from path
            filename = metadata["source"].split('/')[-1].split('\\')[-1]
            return re.sub(r'\.\w+$', '', filename).replace('_', ' ')
        else:
            return "Document"
    
    def _detect_document_type(self, metadata: Dict[str, Any], text: str) -> str:
        """Detect document type from metadata and content.
        
        Args:
            metadata: Chunk metadata
            text: Chunk text
            
        Returns:
            Document type
        """
        # Try to get from metadata first
        if "document_type" in metadata:
            return metadata["document_type"]
            
        # Check file extension
        if "source" in metadata:
            file_path = metadata["source"]
            ext = file_path.split('.')[-1].lower() if '.' in file_path else ""
            
            if ext in ["pdf"]:
                # Look for common manual indicators in text
                if any(kw in text.lower() for kw in ["user guide", "manual", "documentation", 
                                                   "guide", "reference", "handbook"]):
                    return "Manual"
                # Check for tutorial content    
                elif any(kw in text.lower() for kw in ["tutorial", "how to", "step by step"]):
                    return "Tutorial"
            
            elif ext in ["docx", "doc"]:
                # Check for formal document types
                if any(kw in text.lower() for kw in ["report", "analysis", "summary", "findings"]):
                    return "Report"
                    
            elif ext in ["txt", "md"]:
                # Check for notes/documentation
                if any(kw in text.lower() for kw in ["notes:", "note:", "todo:", "summary:"]):
                    return "Notes"
                    
            # Look for Q&A patterns
            if re.search(r'(?:Q:|Question:|Q[0-9]+:)', text):
                return "Q&A"
        
        # Default type based on headings
        headings = self._extract_headings(text)
        if headings and any("chapter" in h.lower() for h in headings):
            return "Manual"
        elif len(headings) > 3:
            return "Documentation"
        
        # Generic fallback
        return "Document"
    
    def _get_position_info(self, metadata: Dict[str, Any], document_type: str) -> str:
        """Get position information from metadata.
        
        Args:
            metadata: Chunk metadata
            document_type: Type of document
            
        Returns:
            Position information
        """
        # If position is explicitly provided, use it
        if "position" in metadata:
            return metadata["position"].capitalize()
            
        # Get basic position indicators
        is_first = metadata.get("is_first_chunk", False)
        is_last = metadata.get("is_last_chunk", False)
        
        idx = metadata.get("chunk_index", None)
        total = metadata.get("total_chunks", None)
        
        if idx is not None and total is not None:
            is_first = idx == 0
            is_last = idx == total - 1
            percentage = int((idx / total) * 100)
        
        # Tailor position information based on document type
        if document_type == "Manual":
            # For manuals, use chapter-oriented positioning
            if is_first:
                return "Introduction"
            elif is_last:
                return "Conclusion/Reference"
            elif idx is not None and total is not None:
                return f"Chapter {idx+1}/{total} ({percentage}%)"
            else:
                return "Main Content"
                
        elif document_type == "Tutorial":
            # For tutorials, use step-oriented positioning
            if is_first:
                return "Setup/Introduction"
            elif is_last:
                return "Final Steps"
            elif idx is not None and total is not None:
                return f"Step {idx+1}/{total} ({percentage}%)"
            else:
                return "Instructions"
                
        elif document_type == "Q&A":
            # For Q&A documents, use Q&A-oriented positioning
            if idx is not None and total is not None:
                return f"Q&A Section {idx+1}/{total} ({percentage}%)"
            else:
                return "Q&A Content"
                
        elif document_type == "Notes":
            # For notes, use section-oriented positioning
            if is_first:
                return "Initial Notes"
            elif is_last:
                return "Final Notes"
            elif idx is not None and total is not None:
                return f"Note Section {idx+1}/{total} ({percentage}%)"
            else:
                return "Notes Content"
                
        elif document_type == "Report":
            # For reports, use section-oriented positioning
            if is_first:
                return "Executive Summary"
            elif is_last:
                return "Conclusion/Recommendations"
            elif idx is not None and total is not None:
                return f"Section {idx+1}/{total} ({percentage}%)"
            else:
                return "Main Analysis"
                
        else:
            # Default positioning for general documents
            if is_first:
                return "Beginning"
            elif is_last:
                return "End"
            elif idx is not None and total is not None:
                return f"Section {idx+1}/{total} ({percentage}%)"
            else:
                return "Main Content"
                
    def _extract_headings(self, text: str) -> List[str]:
        """Extract potential headings from text.
        
        Args:
            text: Chunk text
            
        Returns:
            List of extracted headings
        """
        # Simple heuristic: Look for short lines ending without punctuation
        # or lines in ALL CAPS or Title Case followed by newlines
        headings = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if line is a potential heading
            if (len(line) < 100 and not line[-1] in '.,:;?!') or \
               line.isupper() or \
               (line.istitle() and len(line.split()) <= 10):
                headings.append(line)
                
            # Limit to top 3 headings
            if len(headings) >= 3:
                break
                
        return headings
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extract named entities from text using simple heuristics.
        
        Args:
            text: Chunk text
            
        Returns:
            List of potential named entities
        """
        # This is a simplified version - ideally would use a proper NER tagger
        words = text.split()
        entities = []
        
        try:
            # Look for capitalized words not at the start of sentences
            sentences = self._safe_sent_tokenize(text)
            for sentence in sentences:
                words = sentence.split()
                if len(words) <= 1:
                    continue
                    
                # Skip first word and look for capitalized words
                for word in words[1:]:
                    clean_word = re.sub(r'[^\w\s]', '', word)
                    if clean_word and clean_word[0].isupper() and len(clean_word) > 1:
                        entities.append(clean_word)
        except Exception as e:
            print(f"Error extracting entities: {e}")
            # Just use simple heuristic on words if sentence tokenization fails
            for word in words:
                clean_word = re.sub(r'[^\w\s]', '', word)
                if clean_word and clean_word[0].isupper() and len(clean_word) > 1:
                    entities.append(clean_word)
        
        # Return unique entities, limit to top 10
        unique_entities = list(set(entities))
        return unique_entities[:10]
    
    def _safe_sent_tokenize(self, text: str) -> List[str]:
        """Safely tokenize sentences with fallback.
        
        Args:
            text: Text to tokenize
            
        Returns:
            List of sentences
        """
        try:
            return sent_tokenize(text)
        except Exception as e:
            print(f"Error using NLTK sent_tokenize: {e}")
            # Simple fallback using regex
            sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s', text)
            return [s.strip() for s in sentences if s.strip()]
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text.
        
        Args:
            text: Chunk text
            
        Returns:
            List of keywords
        """
        # Simple keyword extraction based on word frequency
        words = re.findall(r'\b\w{3,}\b', text.lower())
        
        # Filter out stopwords
        keywords = [word for word in words if word not in self.stopwords]
        
        # Count word frequencies
        word_counts = {}
        for word in keywords:
            # Lemmatize words for better grouping
            try:
                lemma = self.lemmatizer.lemmatize(word)
                word_counts[lemma] = word_counts.get(lemma, 0) + 1
            except Exception as e:
                # If lemmatization fails, use the word as is
                word_counts[word] = word_counts.get(word, 0) + 1
        
        # Sort by frequency
        sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Return top 10 keywords
        return [word for word, count in sorted_words[:10]]
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for better embedding.
        
        Args:
            text: Chunk text
            
        Returns:
            Normalized text
        """
        # Normalize whitespace
        normalized = re.sub(r'\s+', ' ', text)
        
        # Normalize quotes - use unicode escape sequences to avoid regex parsing issues
        normalized = re.sub(r'[\u201c\u201d]', '"', normalized)  # Smart double quotes
        normalized = re.sub(r'[\u2018\u2019]', "'", normalized)  # Smart single quotes
        
        # Normalize dashes
        normalized = re.sub(r'[\u2014\u2013]', '-', normalized)  # Em-dash and en-dash
        
        # Normalize ellipses
        normalized = re.sub(r'\.{2,}', '...', normalized)
        
        # Preserve paragraph structure with single newlines
        normalized = re.sub(r'\n{2,}', '\n', normalized)
        
        return normalized.strip()
    
    def _create_context_prefix(self, 
                              title: str,
                              doc_type: str,
                              position: str, 
                              headings: List[str]) -> str:
        """Create a context prefix for the chunk.
        
        Args:
            title: Document title
            doc_type: Document type
            position: Position information
            headings: Extracted headings
            
        Returns:
            Context prefix
        """
        prefix_parts = []
        
        # Add document title
        prefix_parts.append(f"Document: {title}")
        
        # Add document type
        prefix_parts.append(f"Type: {doc_type}")
        
        # Add position
        prefix_parts.append(f"Position: {position}")
        
        # Add headings if available
        if headings:
            prefix = "Section:" if len(headings) == 1 else "Sections:"
            heading_text = " > ".join(headings)
            prefix_parts.append(f"{prefix} {heading_text}")
        
        # Join with newlines
        return "\n".join(prefix_parts) 