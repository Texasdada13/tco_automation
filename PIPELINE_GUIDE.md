# TCO Automation Pipeline Guide

## Overview

The document processing pipeline automates extraction of pricing data from vendor proposals into structured TCO Excel models.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Process a single document
python run_pipeline.py proposal.docx --vendor FIS --term 5_year

# Process all files in a directory
python run_pipeline.py data/raw/ -o data/output/
```

## Pipeline Stages

### 1. Ingestion
Loads documents and extracts raw content.

**Supported formats:**
- Word documents (.docx) - Native text extraction
- Excel files (.xlsx) - Cell-by-cell extraction
- PDF files (.pdf) - Text extraction + OCR for scanned pages
- Images (.png, .jpg, .tiff) - OCR text extraction

```python
from extractors import load_document

doc = load_document("proposal.docx")
print(doc.raw_text)
print(f"Tables found: {len(doc.tables)}")
```

### 2. Preprocessing
Cleans and prepares text for extraction.

**Features:**
- Whitespace normalization
- OCR error correction
- Token-aware chunking for LLM context windows
- Sentence segmentation

```python
from preprocessors import TextProcessor

processor = TextProcessor(max_chunk_tokens=4000)
chunks = processor.chunk(doc.raw_text)
```

### 3. Extraction
Extracts structured fields using hybrid approach.

**Methods:**
- **Regex patterns** - Currency, percentages, dates
- **NER (spaCy)** - Organizations, money, dates
- **LLM (Claude)** - Complex field extraction, ambiguity resolution

```python
from extractors import LLMExtractor

extractor = LLMExtractor()
result = extractor.extract_tco_fields(text, vendor="FIS")
print(result.fields)
print(f"Confidence: {result.confidence}")
```

### 4. Validation
Validates extracted data and applies corrections.

**Features:**
- JSON schema validation
- Cross-field consistency checks
- Auto-correction of common errors
- Format normalization

### 5. Mapping
Maps vendor-specific data to standardized TCO schema.

**Features:**
- Fuzzy matching for product names
- Category classification
- Fee type normalization
- Mapping audit trail

```python
from mappers import SchemaMapper

mapper = SchemaMapper()
name, confidence = mapper.normalize_product_name("digital bnkng")
# Returns: ("Digital Banking", 0.85)
```

### 6. Output
Writes data to Excel using template.

```python
from writers import TCOWriter

writer = TCOWriter("template.xlsx", "output.xlsx")
writer.write_vendor_data(normalized_data, 'FIS')
writer.save()
```

## Command Line Interface

### Basic Usage

```bash
# Process single file
python run_pipeline.py document.docx

# Specify vendor and term
python run_pipeline.py proposal.docx --vendor FIS --term 7_year

# Specify output location
python run_pipeline.py document.docx -o ./output/

# Use template
python run_pipeline.py document.docx -t template.xlsx

# Disable LLM extraction (rule-based only)
python run_pipeline.py document.docx --no-llm

# Verbose output
python run_pipeline.py document.docx --verbose

# JSON output
python run_pipeline.py document.docx --json
```

### Scheduling

```bash
# Run with job configuration
python run_pipeline.py --schedule config/jobs.json

# Run specific job
python run_pipeline.py --schedule config/jobs.json --run-job daily_fis_processing
```

## Configuration

### Environment Variables

Create `config/.env`:

```env
# Anthropic API Key (for LLM extraction)
ANTHROPIC_API_KEY=sk-ant-...

# Model selection
CLAUDE_MODEL=claude-sonnet-4-20250514

# Processing settings
MAX_CHUNK_TOKENS=4000
OVERLAP_TOKENS=200
```

### Job Configuration

Create `config/jobs.json`:

```json
{
  "jobs": [
    {
      "name": "daily_fis",
      "input_dir": "./data/raw/fis",
      "output_dir": "./data/output",
      "schedule": "daily",
      "vendor": "FIS",
      "term": "7_year",
      "use_llm": true,
      "enabled": true
    }
  ]
}
```

## Python API

### Full Pipeline

```python
from orchestrator import run_pipeline

result = run_pipeline(
    input_path="data/raw/",
    output_dir="data/output/",
    vendor="FIS",
    term="5_year",
    use_llm=True
)

print(f"Success: {result.success}")
print(f"Duration: {result.duration_seconds}s")
print(f"Output: {result.output_file}")
```

### Individual Components

```python
# Load and preprocess
from extractors import load_document
from preprocessors import TextProcessor

doc = load_document("proposal.docx")
processor = TextProcessor()
cleaned = processor.clean_for_extraction(doc.raw_text)

# Extract with LLM
from extractors import LLMExtractor

extractor = LLMExtractor(api_key="sk-ant-...")
result = extractor.extract_tco_fields(cleaned, "FIS")

# Map to schema
from mappers import SchemaMapper

mapper = SchemaMapper()
normalized = mapper.map_fis_data(result.fields, term="7_year")

# Write output
from writers import TCOWriter

writer = TCOWriter("template.xlsx", "output.xlsx")
writer.write_vendor_data(normalized, "FIS")
writer.save()
```

## Utilities

### Validators

```python
from utils import validate_currency, format_currency

valid, amount, error = validate_currency("$1,234.56")
# valid=True, amount=1234.56, error=""

formatted = format_currency(1234.56)
# "$1,234.56"
```

### Helpers

```python
from utils import (
    detect_vendor_from_file,
    calculate_contract_total,
    generate_output_filename
)

vendor = detect_vendor_from_file("FIS_Proposal.docx")
# "FIS"

totals = calculate_contract_total(line_items, term_years=5)
# {'monthly_total': 10000, 'annual_total': 120000, ...}
```

## Logging

```python
from utils import setup_logging, get_logger

# Setup logging
setup_logging(level=logging.INFO, log_dir="./logs")

# Get logger
logger = get_logger(__name__)
logger.info("Processing started")
```

## Troubleshooting

### Common Issues

**"LLM client not initialized"**
- Set `ANTHROPIC_API_KEY` environment variable
- Or pass `api_key` to LLMExtractor

**"pdfplumber not installed"**
- Run: `pip install pdfplumber`

**"spaCy model not found"**
- Run: `python -m spacy download en_core_web_sm`

**OCR not working**
- Install Tesseract: `apt-get install tesseract-ocr`

### Debug Mode

```bash
# Enable verbose logging
python run_pipeline.py document.docx --verbose

# Check specific stage
python -c "
from extractors import load_document
doc = load_document('document.docx')
print(doc.raw_text[:500])
"
```

## Performance Tips

1. **Disable LLM for known formats** - Use `--no-llm` for standard FIS/JH documents
2. **Process in batches** - Use directory input for multiple files
3. **Use appropriate chunk size** - Default 4000 tokens works well
4. **Cache API results** - LLM responses are deterministic with temperature=0

## Extending the Pipeline

### Add New Extractor

```python
from extractors.document_loader import DocumentLoader

class CustomExtractor:
    def extract(self, filepath):
        loader = DocumentLoader()
        doc = loader.load(filepath)
        # Custom extraction logic
        return extracted_data
```

### Add New Validation Rule

Edit `config/validation_rules.json`:

```json
{
  "validation_rules": {
    "cross_field": [
      {
        "name": "custom_check",
        "description": "Custom validation",
        "condition": "your_condition_here"
      }
    ]
  }
}
```

### Add Product Mapping

Edit `mappers/schema_mapper.py`:

```python
PRODUCT_NAME_MAPPINGS = {
    'custom product': 'Standardized Name',
    # ...
}
```
