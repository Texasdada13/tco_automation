# TCO Automation - Integration Guide

**Third-Party Integrations and API Reference**

---

## Table of Contents

- [Overview](#overview)
- [Claude API Integration](#claude-api-integration)
- [Excel Integration](#excel-integration)
- [Document Processing Libraries](#document-processing-libraries)
- [NLP Libraries](#nlp-libraries)
- [Custom Integrations](#custom-integrations)
- [API Reference](#api-reference)
- [Webhooks and Callbacks](#webhooks-and-callbacks)

---

## Overview

The TCO Automation System integrates with various external services and libraries. This guide provides detailed information on how these integrations work and how to configure them.

### Integration Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   TCO Automation System                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Claude    │  │   Excel     │  │    NLP      │         │
│  │    API      │  │  Libraries  │  │  Libraries  │         │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘         │
│         │                │                │                 │
│         ▼                ▼                ▼                 │
│  ┌──────────────────────────────────────────────┐          │
│  │           Integration Layer                   │          │
│  └──────────────────────────────────────────────┘          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Claude API Integration

### Overview

The system uses Anthropic's Claude API for intelligent extraction, classification, and validation.

### Setup

#### 1. Install the Library

```bash
pip install anthropic
```

#### 2. Configure API Key

```bash
# Environment variable
export ANTHROPIC_API_KEY="sk-ant-your-key-here"

# Or in .env file
echo 'ANTHROPIC_API_KEY=sk-ant-your-key-here' >> .env
```

#### 3. Verify Connection

```python
from anthropic import Anthropic

client = Anthropic()
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=100,
    messages=[{"role": "user", "content": "Hello"}]
)
print(response.content[0].text)
```

### Usage Examples

#### Basic Extraction

```python
from extractors.llm_extractor import LLMExtractor

extractor = LLMExtractor()
result = extractor.extract_fields(
    document_text="...",
    fields=['solution_name', 'monthly_fee', 'category']
)
```

#### Batch Processing

```python
from extractors.llm_extractor import LLMExtractor

extractor = LLMExtractor()
documents = ["doc1 text", "doc2 text", "doc3 text"]

results = []
for doc in documents:
    result = extractor.extract_fields(doc, fields=['solution_name', 'fee'])
    results.append(result)
```

### Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `model` | claude-sonnet-4-20250514 | Claude model to use |
| `max_tokens` | 8192 | Maximum response tokens |
| `temperature` | 0.0 | Response randomness (0=deterministic) |
| `max_retries` | 3 | API retry attempts |
| `retry_delay` | 2 | Seconds between retries |

### Error Handling

```python
from anthropic import APIError, RateLimitError

try:
    result = extractor.extract_fields(document_text, fields)
except RateLimitError:
    print("Rate limit reached. Waiting...")
    time.sleep(60)
    result = extractor.extract_fields(document_text, fields)
except APIError as e:
    print(f"API error: {e}")
    # Fallback to rule-based extraction
    result = rule_based_extract(document_text, fields)
```

### Rate Limiting

| Model | RPM | TPM |
|-------|-----|-----|
| Claude Sonnet | 60 | 100,000 |
| Claude Opus | 30 | 50,000 |
| Claude Haiku | 120 | 200,000 |

Implement rate limiting:

```python
import time
from functools import wraps

def rate_limit(calls_per_minute=60):
    interval = 60.0 / calls_per_minute

    def decorator(func):
        last_call = [0.0]

        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_call[0]
            if elapsed < interval:
                time.sleep(interval - elapsed)
            result = func(*args, **kwargs)
            last_call[0] = time.time()
            return result

        return wrapper
    return decorator

@rate_limit(calls_per_minute=50)
def call_claude_api(prompt):
    # API call here
    pass
```

---

## Excel Integration

### Overview

The system uses `openpyxl` for reading and writing Excel files.

### Setup

```bash
pip install openpyxl
```

### Reading Excel Files

```python
from openpyxl import load_workbook

# Load with formulas
wb = load_workbook("file.xlsx", data_only=False)
ws = wb.active

# Load with calculated values
wb_values = load_workbook("file.xlsx", data_only=True)
ws_values = wb_values.active
```

### Writing Excel Files

```python
from openpyxl import load_workbook

wb = load_workbook("template.xlsx")
ws = wb["Line Items"]

# Write data
ws['B7'] = 'Monthly F'
ws['O7'] = 'Product Name'
ws['S7'] = 15000.00

# Save
wb.save("output.xlsx")
```

### Advanced Features

#### Preserving Formatting

```python
from openpyxl.styles import Font, Alignment

# Copy formatting from template
source_cell = ws['B7']
target_cell = ws['B8']

target_cell.font = source_cell.font.copy()
target_cell.alignment = source_cell.alignment.copy()
target_cell.number_format = source_cell.number_format
```

#### Handling Merged Cells

```python
def write_to_cell_safe(ws, row, col, value):
    cell = ws.cell(row, col)

    # Check if cell is merged
    for merged_range in ws.merged_cells.ranges:
        if cell.coordinate in merged_range:
            # Get top-left cell of merged range
            top_left = merged_range.min_col, merged_range.min_row
            cell = ws.cell(top_left[1], top_left[0])
            break

    cell.value = value
```

#### Working with Comments

```python
from openpyxl.comments import Comment

# Read comment
cell = ws['A1']
if cell.comment:
    print(cell.comment.text)

# Write comment
cell.comment = Comment("This is a note", "Author")
```

---

## Document Processing Libraries

### python-docx (Word Documents)

#### Setup

```bash
pip install python-docx
```

#### Reading Documents

```python
from docx import Document

doc = Document("proposal.docx")

# Get all paragraphs
for para in doc.paragraphs:
    print(para.text)

# Get all tables
for table in doc.tables:
    for row in table.rows:
        for cell in row.cells:
            print(cell.text)
```

### pdfplumber (PDF Documents)

#### Setup

```bash
pip install pdfplumber
```

#### Reading PDFs

```python
import pdfplumber

with pdfplumber.open("document.pdf") as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        tables = page.extract_tables()
```

### PyMuPDF (PDF Processing)

#### Setup

```bash
pip install PyMuPDF
```

#### Advanced PDF Processing

```python
import fitz  # PyMuPDF

doc = fitz.open("document.pdf")
for page in doc:
    text = page.get_text()
    # Extract images
    images = page.get_images()
```

### pytesseract (OCR)

#### Setup

```bash
pip install pytesseract Pillow

# Also install Tesseract OCR engine
# Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
# macOS: brew install tesseract
# Linux: sudo apt-get install tesseract-ocr
```

#### Usage

```python
from PIL import Image
import pytesseract

# OCR an image
text = pytesseract.image_to_string(Image.open("scan.png"))
```

---

## NLP Libraries

### spaCy (Named Entity Recognition)

#### Setup

```bash
pip install spacy
python -m spacy download en_core_web_sm
```

#### Usage

```python
import spacy

nlp = spacy.load("en_core_web_sm")
doc = nlp("The monthly fee is $15,000 for HORIZON processing.")

# Extract entities
for ent in doc.ents:
    print(ent.text, ent.label_)
    # $15,000 MONEY
```

### NLTK (Text Processing)

#### Setup

```bash
pip install nltk
python -c "import nltk; nltk.download('punkt')"
```

#### Usage

```python
import nltk

# Sentence tokenization
sentences = nltk.sent_tokenize(text)

# Word tokenization
words = nltk.word_tokenize(text)
```

### tiktoken (Token Counting)

#### Setup

```bash
pip install tiktoken
```

#### Usage

```python
import tiktoken

enc = tiktoken.encoding_for_model("claude-3-sonnet-20240229")
tokens = enc.encode("Your text here")
print(f"Token count: {len(tokens)}")
```

### RapidFuzz (Fuzzy Matching)

#### Setup

```bash
pip install rapidfuzz
```

#### Usage

```python
from rapidfuzz import fuzz, process

# Simple ratio
score = fuzz.ratio("SilverLake System", "Silverlake Sys")
# 85

# Find best match
matches = process.extract(
    "SilverLake",
    ["SilverLake System", "Gold Lake", "Silver Creek"],
    limit=3
)
```

---

## Custom Integrations

### Creating a Custom Extractor

```python
from extractors.base_extractor import BaseExtractor

class CustomVendorExtractor(BaseExtractor):
    def __init__(self):
        super().__init__()
        self.vendor_name = "Custom Vendor"

    def extract(self, file_path):
        # Load document
        doc = self.load_document(file_path)

        # Extract data
        data = self.parse_document(doc)

        # Normalize
        normalized = self.normalize(data)

        return normalized

    def parse_document(self, doc):
        # Custom parsing logic
        pass

    def normalize(self, data):
        # Map to standard schema
        pass
```

### Registering Custom Extractor

```python
from extractors import register_extractor

register_extractor('custom_vendor', CustomVendorExtractor)

# Usage
from extractors import get_extractor

extractor = get_extractor('custom_vendor')
result = extractor.extract("custom_proposal.docx")
```

---

## API Reference

### Python API

#### Main Classes

```python
# Extractors
from extractors.fis_extractor import FISExtractor
from extractors.jh_extractor import JHExtractor
from extractors.llm_extractor import LLMExtractor

# Mappers
from mappers.schema_mapper import SchemaMapper

# Writers
from writers.tco_writer import TCOWriter

# Pipeline
from orchestrator.pipeline import Pipeline
```

#### FISExtractor

```python
class FISExtractor:
    def extract(self, file_path: str, term: str = '7_year') -> dict:
        """
        Extract data from FIS Word proposal.

        Args:
            file_path: Path to .docx file
            term: Contract term ('5_year', '7_year', '10_year')

        Returns:
            Dictionary with extracted data
        """
        pass
```

#### JHExtractor

```python
class JHExtractor:
    def extract(self, file_path: str, scenario: str = 'Proposal_1') -> dict:
        """
        Extract data from Jack Henry Excel deal sheet.

        Args:
            file_path: Path to .xlsx file
            scenario: Proposal scenario ('Proposal_1', 'Proposal_2', 'Proposal_3')

        Returns:
            Dictionary with extracted data
        """
        pass
```

#### SchemaMapper

```python
class SchemaMapper:
    def normalize(self, data: dict, vendor: str, term: str) -> list:
        """
        Normalize vendor data to TCO schema.

        Args:
            data: Extracted vendor data
            vendor: Vendor name ('FIS', 'Jack Henry')
            term: Contract term

        Returns:
            List of normalized line items
        """
        pass
```

#### TCOWriter

```python
class TCOWriter:
    def __init__(self, template_path: str, output_path: str):
        """
        Initialize TCO writer.

        Args:
            template_path: Path to TCO template
            output_path: Path for output file
        """
        pass

    def write_vendor_data(self, data: list, vendor: str) -> None:
        """
        Write vendor data to template.

        Args:
            data: Normalized line items
            vendor: Vendor name
        """
        pass

    def save(self) -> None:
        """Save the populated template."""
        pass
```

### CLI Interface

```bash
# Main entry point
python main.py [OPTIONS]

# Options:
#   --fis PATH          FIS proposal file
#   --jh PATH           Jack Henry deal sheet
#   --template PATH     TCO template (required)
#   --output PATH       Output file (required)
#   --fis-term TERM     FIS term (5_year, 7_year, 10_year)
#   --jh-scenario NAME  JH scenario (Proposal_1/2/3)
```

---

## Webhooks and Callbacks

### Event Hooks

The system supports event hooks for custom processing:

```python
from orchestrator.pipeline import Pipeline

def on_extraction_complete(result):
    print(f"Extracted {len(result['items'])} items")
    # Send notification, update database, etc.

def on_error(error):
    print(f"Error occurred: {error}")
    # Log error, send alert, etc.

pipeline = Pipeline()
pipeline.on('extraction_complete', on_extraction_complete)
pipeline.on('error', on_error)

pipeline.run(input_file, output_file)
```

### Custom Callbacks

```python
class ProcessingCallbacks:
    def on_start(self, file_path):
        print(f"Starting: {file_path}")

    def on_progress(self, stage, percent):
        print(f"{stage}: {percent}%")

    def on_complete(self, result):
        print(f"Complete: {result['output_file']}")

    def on_error(self, error):
        print(f"Error: {error}")

callbacks = ProcessingCallbacks()
pipeline.run(input_file, output_file, callbacks=callbacks)
```

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes (for AI) | Claude API key |
| `LOG_LEVEL` | No | Logging level (DEBUG, INFO, etc.) |
| `CACHE_DIR` | No | Cache directory |
| `OUTPUT_DIR` | No | Default output directory |

---

*Last Updated: December 2024*
