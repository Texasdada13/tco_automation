"""
Extractors module for TCO Automation System

Includes document loaders, LLM extractors, and vendor-specific extractors.
"""

from .fis_extractor import FISExtractor, extract_fis_proposal
from .jh_extractor import JackHenryExtractor, extract_jack_henry_proposal
from .document_loader import (
    DocumentLoader,
    DocumentType,
    ExtractedDocument,
    ExtractedPage,
    load_document,
    load_documents
)
from .llm_extractor import (
    LLMExtractor,
    ExtractionResult,
    FieldDefinition,
    extract_fields,
    extract_tco_data
)

__all__ = [
    # Vendor-specific extractors
    'FISExtractor',
    'extract_fis_proposal',
    'JackHenryExtractor',
    'extract_jack_henry_proposal',

    # Document loader
    'DocumentLoader',
    'DocumentType',
    'ExtractedDocument',
    'ExtractedPage',
    'load_document',
    'load_documents',

    # LLM extractor
    'LLMExtractor',
    'ExtractionResult',
    'FieldDefinition',
    'extract_fields',
    'extract_tco_data'
]
