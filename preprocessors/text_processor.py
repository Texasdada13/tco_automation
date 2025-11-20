"""
Text Processor Module

Handles text cleaning, tokenization, and chunking for LLM processing.
Optimizes text for context windows while preserving semantic meaning.
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field

# Token counting
try:
    import tiktoken
    HAS_TIKTOKEN = True
except ImportError:
    HAS_TIKTOKEN = False

# Sentence tokenization
try:
    import nltk
    from nltk.tokenize import sent_tokenize
    HAS_NLTK = True
except ImportError:
    HAS_NLTK = False


logger = logging.getLogger(__name__)


@dataclass
class TextChunk:
    """A chunk of text with metadata."""
    text: str
    chunk_index: int
    start_char: int
    end_char: int
    token_count: int
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def char_count(self) -> int:
        return len(self.text)


class TextProcessor:
    """
    Process and prepare text for LLM extraction.

    Features:
    - Text cleaning (normalize whitespace, remove artifacts)
    - Token-aware chunking for context windows
    - Sentence-based splitting to preserve meaning
    - Overlap support for context continuity
    """

    # Default cleaning patterns
    CLEANING_PATTERNS = [
        # Remove multiple spaces
        (r' +', ' '),
        # Remove multiple newlines (keep max 2)
        (r'\n{3,}', '\n\n'),
        # Remove page numbers (common formats)
        (r'\n\s*Page \d+ of \d+\s*\n', '\n'),
        (r'\n\s*-\s*\d+\s*-\s*\n', '\n'),
        # Remove headers/footers (common patterns)
        (r'\n\s*CONFIDENTIAL\s*\n', '\n'),
        (r'\n\s*DRAFT\s*\n', '\n'),
        # Fix common OCR errors
        (r'\bl\s*\|\s*', 'I'),  # l| -> I
        (r'\bO\s+', '0 '),  # O -> 0 in numbers context
        # Normalize dashes
        (r'[–—]', '-'),
        # Remove non-printable characters (except newlines/tabs)
        (r'[^\x20-\x7E\n\t]', ''),
    ]

    # Currency patterns for preservation
    CURRENCY_PATTERN = re.compile(
        r'\$[\d,]+(?:\.\d{2})?|\d+(?:,\d{3})*(?:\.\d{2})?\s*(?:USD|dollars?)',
        re.IGNORECASE
    )

    def __init__(
        self,
        model: str = 'cl100k_base',
        max_chunk_tokens: int = 4000,
        overlap_tokens: int = 200,
        preserve_tables: bool = True
    ):
        """
        Initialize text processor.

        Args:
            model: Tiktoken model for token counting (default: cl100k_base for Claude)
            max_chunk_tokens: Maximum tokens per chunk
            overlap_tokens: Token overlap between chunks
            preserve_tables: Whether to keep tables intact
        """
        self.max_chunk_tokens = max_chunk_tokens
        self.overlap_tokens = overlap_tokens
        self.preserve_tables = preserve_tables

        # Initialize tokenizer
        if HAS_TIKTOKEN:
            try:
                self.tokenizer = tiktoken.get_encoding(model)
            except Exception:
                self.tokenizer = tiktoken.get_encoding('cl100k_base')
        else:
            self.tokenizer = None
            logger.warning("tiktoken not available - using character-based estimation")

        # Initialize NLTK if available
        if HAS_NLTK:
            try:
                nltk.data.find('tokenizers/punkt')
            except LookupError:
                try:
                    nltk.download('punkt', quiet=True)
                except Exception:
                    pass

    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text.

        Args:
            text: Input text

        Returns:
            Token count
        """
        if self.tokenizer:
            return len(self.tokenizer.encode(text))
        else:
            # Rough estimation: ~4 chars per token
            return len(text) // 4

    def clean(self, text: str, custom_patterns: Optional[List[Tuple[str, str]]] = None) -> str:
        """
        Clean and normalize text.

        Args:
            text: Raw input text
            custom_patterns: Additional regex patterns to apply

        Returns:
            Cleaned text
        """
        if not text:
            return ''

        cleaned = text

        # Apply default cleaning patterns
        for pattern, replacement in self.CLEANING_PATTERNS:
            cleaned = re.sub(pattern, replacement, cleaned)

        # Apply custom patterns
        if custom_patterns:
            for pattern, replacement in custom_patterns:
                cleaned = re.sub(pattern, replacement, cleaned)

        # Strip leading/trailing whitespace
        cleaned = cleaned.strip()

        return cleaned

    def clean_for_extraction(self, text: str) -> str:
        """
        Clean text specifically for data extraction.

        Preserves:
        - Currency values
        - Percentages
        - Dates
        - Table structure

        Args:
            text: Raw text

        Returns:
            Cleaned text optimized for extraction
        """
        # Basic cleaning
        cleaned = self.clean(text)

        # Normalize currency formats
        cleaned = re.sub(r'\$\s+', '$', cleaned)

        # Normalize percentage formats
        cleaned = re.sub(r'(\d+)\s*%', r'\1%', cleaned)

        # Normalize date separators
        cleaned = re.sub(r'(\d{1,2})\s*/\s*(\d{1,2})\s*/\s*(\d{2,4})', r'\1/\2/\3', cleaned)

        return cleaned

    def split_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences.

        Args:
            text: Input text

        Returns:
            List of sentences
        """
        if HAS_NLTK:
            try:
                return sent_tokenize(text)
            except Exception:
                pass

        # Fallback: simple sentence splitting
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]

    def chunk(
        self,
        text: str,
        max_tokens: Optional[int] = None,
        overlap: Optional[int] = None
    ) -> List[TextChunk]:
        """
        Split text into chunks suitable for LLM processing.

        Uses sentence boundaries when possible to preserve meaning.

        Args:
            text: Input text
            max_tokens: Maximum tokens per chunk (default: self.max_chunk_tokens)
            overlap: Token overlap between chunks (default: self.overlap_tokens)

        Returns:
            List of TextChunk objects
        """
        if not text:
            return []

        max_tokens = max_tokens or self.max_chunk_tokens
        overlap = overlap or self.overlap_tokens

        # If text fits in one chunk, return as-is
        total_tokens = self.count_tokens(text)
        if total_tokens <= max_tokens:
            return [TextChunk(
                text=text,
                chunk_index=0,
                start_char=0,
                end_char=len(text),
                token_count=total_tokens
            )]

        # Split into sentences
        sentences = self.split_sentences(text)

        chunks = []
        current_chunk = []
        current_tokens = 0
        chunk_start = 0
        char_position = 0

        for sentence in sentences:
            sentence_tokens = self.count_tokens(sentence)

            # If single sentence exceeds max, split it
            if sentence_tokens > max_tokens:
                # Save current chunk if any
                if current_chunk:
                    chunk_text = ' '.join(current_chunk)
                    chunks.append(TextChunk(
                        text=chunk_text,
                        chunk_index=len(chunks),
                        start_char=chunk_start,
                        end_char=char_position,
                        token_count=current_tokens
                    ))
                    current_chunk = []
                    current_tokens = 0

                # Split long sentence by tokens
                words = sentence.split()
                word_chunk = []
                word_tokens = 0
                word_start = char_position

                for word in words:
                    word_token_count = self.count_tokens(word + ' ')
                    if word_tokens + word_token_count > max_tokens and word_chunk:
                        chunk_text = ' '.join(word_chunk)
                        chunks.append(TextChunk(
                            text=chunk_text,
                            chunk_index=len(chunks),
                            start_char=word_start,
                            end_char=char_position,
                            token_count=word_tokens
                        ))
                        # Keep overlap
                        overlap_words = word_chunk[-overlap // 10:] if overlap else []
                        word_chunk = overlap_words + [word]
                        word_tokens = self.count_tokens(' '.join(word_chunk))
                        word_start = char_position
                    else:
                        word_chunk.append(word)
                        word_tokens += word_token_count

                if word_chunk:
                    current_chunk = word_chunk
                    current_tokens = word_tokens
                    chunk_start = word_start

                char_position += len(sentence) + 1
                continue

            # Check if adding sentence would exceed limit
            if current_tokens + sentence_tokens > max_tokens and current_chunk:
                # Save current chunk
                chunk_text = ' '.join(current_chunk)
                chunks.append(TextChunk(
                    text=chunk_text,
                    chunk_index=len(chunks),
                    start_char=chunk_start,
                    end_char=char_position,
                    token_count=current_tokens
                ))

                # Start new chunk with overlap
                if overlap > 0:
                    # Keep last few sentences for context
                    overlap_sentences = []
                    overlap_tokens = 0
                    for sent in reversed(current_chunk):
                        sent_tokens = self.count_tokens(sent)
                        if overlap_tokens + sent_tokens <= overlap:
                            overlap_sentences.insert(0, sent)
                            overlap_tokens += sent_tokens
                        else:
                            break
                    current_chunk = overlap_sentences
                    current_tokens = overlap_tokens
                else:
                    current_chunk = []
                    current_tokens = 0

                chunk_start = char_position

            current_chunk.append(sentence)
            current_tokens += sentence_tokens
            char_position += len(sentence) + 1

        # Don't forget the last chunk
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunks.append(TextChunk(
                text=chunk_text,
                chunk_index=len(chunks),
                start_char=chunk_start,
                end_char=char_position,
                token_count=current_tokens
            ))

        return chunks

    def extract_sections(self, text: str) -> Dict[str, str]:
        """
        Extract named sections from text based on headers.

        Args:
            text: Input text

        Returns:
            Dictionary of section_name -> section_content
        """
        sections = {}

        # Common header patterns
        header_patterns = [
            r'^#+\s+(.+)$',  # Markdown headers
            r'^([A-Z][A-Za-z\s]+):$',  # Title case with colon
            r'^(\d+\.\s+[A-Z][A-Za-z\s]+)$',  # Numbered sections
            r'^([A-Z\s]{3,})$',  # ALL CAPS headers
        ]

        combined_pattern = '|'.join(f'({p})' for p in header_patterns)

        lines = text.split('\n')
        current_section = 'Introduction'
        current_content = []

        for line in lines:
            is_header = False
            for pattern in header_patterns:
                match = re.match(pattern, line.strip(), re.MULTILINE)
                if match:
                    # Save previous section
                    if current_content:
                        sections[current_section] = '\n'.join(current_content).strip()

                    # Start new section
                    current_section = match.group(1).strip()
                    current_content = []
                    is_header = True
                    break

            if not is_header:
                current_content.append(line)

        # Save last section
        if current_content:
            sections[current_section] = '\n'.join(current_content).strip()

        return sections

    def extract_tables_text(self, text: str) -> List[str]:
        """
        Extract table-like structures from text.

        Args:
            text: Input text

        Returns:
            List of table text blocks
        """
        tables = []

        # Pattern for pipe-delimited tables
        pipe_table_pattern = r'(\|.+\|(?:\n\|.+\|)+)'
        matches = re.findall(pipe_table_pattern, text)
        tables.extend(matches)

        # Pattern for tab-delimited tables
        tab_pattern = r'((?:^[^\n]*\t[^\n]*$\n?){3,})'
        matches = re.findall(tab_pattern, text, re.MULTILINE)
        tables.extend(matches)

        return tables


def clean_text(text: str) -> str:
    """
    Convenience function to clean text.

    Args:
        text: Raw text

    Returns:
        Cleaned text
    """
    processor = TextProcessor()
    return processor.clean_for_extraction(text)


def chunk_text(
    text: str,
    max_tokens: int = 4000,
    overlap: int = 200
) -> List[TextChunk]:
    """
    Convenience function to chunk text.

    Args:
        text: Input text
        max_tokens: Maximum tokens per chunk
        overlap: Token overlap between chunks

    Returns:
        List of TextChunk objects
    """
    processor = TextProcessor(max_chunk_tokens=max_tokens, overlap_tokens=overlap)
    return processor.chunk(text)


def tokenize_text(text: str) -> List[str]:
    """
    Convenience function to split text into sentences.

    Args:
        text: Input text

    Returns:
        List of sentences
    """
    processor = TextProcessor()
    return processor.split_sentences(text)


if __name__ == '__main__':
    # Example usage
    sample_text = """
    This is a sample document for testing the text processor. It contains multiple
    sentences and paragraphs.

    Section 1: Introduction
    This section introduces the main concepts. We will discuss pricing and costs
    including $1,234.56 and 15% discounts.

    Section 2: Details
    More detailed information follows here. The implementation date is 01/15/2025.

    | Product | Price | Quantity |
    |---------|-------|----------|
    | Item A  | $100  | 10       |
    | Item B  | $200  | 5        |
    """

    processor = TextProcessor(max_chunk_tokens=100)

    # Clean
    cleaned = processor.clean_for_extraction(sample_text)
    print("Cleaned text:")
    print(cleaned[:200])
    print()

    # Chunk
    chunks = processor.chunk(cleaned)
    print(f"Created {len(chunks)} chunks:")
    for chunk in chunks:
        print(f"  Chunk {chunk.chunk_index}: {chunk.token_count} tokens, {chunk.char_count} chars")
    print()

    # Extract sections
    sections = processor.extract_sections(cleaned)
    print(f"Found {len(sections)} sections:")
    for name in sections:
        print(f"  - {name}")
