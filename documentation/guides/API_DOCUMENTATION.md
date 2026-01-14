# TCO Automation - API Documentation

**Complete Python API Reference**

---

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Extractors](#extractors)
  - [FISExtractor](#fisextractor)
  - [JHExtractor](#jhextractor)
  - [LLMExtractor](#llmextractor)
- [Mappers](#mappers)
  - [SchemaMapper](#schemamapper)
- [Writers](#writers)
  - [TCOWriter](#tcowriter)
- [Pipeline](#pipeline)
- [Quality Assurance](#quality-assurance)
- [Utilities](#utilities)
- [Data Models](#data-models)

---

## Overview

The TCO Automation System provides a Python API for programmatic access to all extraction, mapping, and writing functionality.

### Module Structure

```
tco_automation/
├── extractors/           # Document extraction
│   ├── fis_extractor.py
│   ├── jh_extractor.py
│   └── llm_extractor.py
├── mappers/              # Data transformation
│   └── schema_mapper.py
├── writers/              # Output generation
│   └── tco_writer.py
├── orchestrator/         # Pipeline management
│   └── pipeline.py
└── extraction/           # AI-powered extraction
    └── quality_assurance.py
```

---

## Quick Start

### Basic Usage

```python
from extractors.fis_extractor import FISExtractor
from mappers.schema_mapper import SchemaMapper
from writers.tco_writer import TCOWriter

# Extract
extractor = FISExtractor()
data = extractor.extract("proposal.docx", term="7_year")

# Normalize
mapper = SchemaMapper()
normalized = mapper.normalize(data, vendor="FIS", term="7_year")

# Write
writer = TCOWriter("template.xlsx", "output.xlsx")
writer.write_vendor_data(normalized, vendor="FIS")
writer.save()
```

### Using the Pipeline

```python
from orchestrator.pipeline import Pipeline

pipeline = Pipeline()
result = pipeline.run(
    fis_file="fis_proposal.docx",
    jh_file="jh_deal_sheet.xlsx",
    template="template.xlsx",
    output="result.xlsx",
    fis_term="7_year",
    jh_scenario="Proposal_1"
)

print(f"Success: {result['success']}")
print(f"Items extracted: {result['items_extracted']}")
```

---

## Extractors

### FISExtractor

Extracts data from FIS Word proposals.

#### Class Definition

```python
class FISExtractor:
    """
    Extractor for FIS Word document proposals.

    Parses tables containing bundle pricing, monthly fees,
    one-time fees, and credits.
    """
```

#### Constructor

```python
def __init__(self):
    """Initialize the FIS extractor."""
```

#### Methods

##### extract()

```python
def extract(
    self,
    file_path: str,
    term: str = "7_year"
) -> dict:
    """
    Extract data from FIS proposal.

    Args:
        file_path: Path to the .docx file
        term: Contract term ('5_year', '7_year', '10_year')

    Returns:
        Dictionary containing:
        - bundle_pricing: Dict with pricing by term and year
        - monthly_fees: List of monthly fee items
        - one_time_fees: List of one-time fee items
        - credits: List of credit items

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file is not a valid Word document

    Example:
        >>> extractor = FISExtractor()
        >>> data = extractor.extract("proposal.docx", term="7_year")
        >>> print(data['bundle_pricing']['7_year']['year_1'])
        150000.0
    """
```

##### identify_tables()

```python
def identify_tables(
    self,
    file_path: str
) -> dict:
    """
    Identify and categorize tables in the document.

    Args:
        file_path: Path to the .docx file

    Returns:
        Dictionary mapping table types to table objects

    Example:
        >>> tables = extractor.identify_tables("proposal.docx")
        >>> print(tables.keys())
        dict_keys(['bundle_pricing', 'monthly_fees', 'one_time_fees'])
    """
```

##### parse_currency()

```python
def parse_currency(self, text: str) -> float:
    """
    Parse currency string to float.

    Args:
        text: Currency string (e.g., "$15,000.00")

    Returns:
        Float value (e.g., 15000.0)

    Example:
        >>> extractor.parse_currency("$1,234,567.89")
        1234567.89
    """
```

#### Usage Example

```python
from extractors.fis_extractor import FISExtractor

# Initialize
extractor = FISExtractor()

# Extract with default term
data = extractor.extract("data/fis_proposal.docx")

# Extract with specific term
data = extractor.extract("data/fis_proposal.docx", term="5_year")

# Access bundle pricing
year_1_cost = data['bundle_pricing']['7_year']['year_1']
print(f"Year 1 bundle cost: ${year_1_cost:,.2f}")

# Access monthly fees
for fee in data['monthly_fees']:
    print(f"{fee['solution_name']}: ${fee['monthly_fee']:,.2f}/month")

# Access one-time fees
total_one_time = sum(f['amount'] for f in data['one_time_fees'])
print(f"Total one-time fees: ${total_one_time:,.2f}")
```

---

### JHExtractor

Extracts data from Jack Henry Excel deal sheets.

#### Class Definition

```python
class JHExtractor:
    """
    Extractor for Jack Henry Excel deal sheets.

    Parses product catalog with multiple scenarios,
    including comments and formulas.
    """
```

#### Constructor

```python
def __init__(self):
    """Initialize the Jack Henry extractor."""
```

#### Methods

##### extract()

```python
def extract(
    self,
    file_path: str,
    scenario: str = "Proposal_1"
) -> dict:
    """
    Extract data from Jack Henry deal sheet.

    Args:
        file_path: Path to the .xlsx file
        scenario: Proposal scenario ('Proposal_1', 'Proposal_2', 'Proposal_3')

    Returns:
        Dictionary containing:
        - products: List of product dictionaries
        - metadata: Extraction metadata

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file is not a valid Excel file

    Example:
        >>> extractor = JHExtractor()
        >>> data = extractor.extract("deal_sheet.xlsx", scenario="Proposal_1")
        >>> print(len(data['products']))
        523
    """
```

##### detect_hidden_rows()

```python
def detect_hidden_rows(self, file_path: str) -> list:
    """
    Detect hidden rows in the Excel file.

    Args:
        file_path: Path to the .xlsx file

    Returns:
        List of hidden row numbers

    Example:
        >>> hidden = extractor.detect_hidden_rows("deal_sheet.xlsx")
        >>> print(hidden)
        [45, 67, 89]
    """
```

##### detect_hidden_columns()

```python
def detect_hidden_columns(self, file_path: str) -> list:
    """
    Detect hidden columns in the Excel file.

    Args:
        file_path: Path to the .xlsx file

    Returns:
        List of hidden column letters

    Example:
        >>> hidden = extractor.detect_hidden_columns("deal_sheet.xlsx")
        >>> print(hidden)
        ['L', 'M']
    """
```

##### extract_comments()

```python
def extract_comments(
    self,
    file_path: str,
    row: int,
    col: int
) -> str | None:
    """
    Extract cell comment if present.

    Args:
        file_path: Path to the .xlsx file
        row: Row number (1-indexed)
        col: Column number (1-indexed)

    Returns:
        Comment text or None if no comment

    Example:
        >>> comment = extractor.extract_comments("deal_sheet.xlsx", 5, 8)
        >>> print(comment)
        "Negotiated rate - valid until 12/31/2024"
    """
```

#### Usage Example

```python
from extractors.jh_extractor import JHExtractor

# Initialize
extractor = JHExtractor()

# Extract default scenario
data = extractor.extract("data/jh_deal_sheet.xlsx")

# Extract specific scenario
data = extractor.extract("data/jh_deal_sheet.xlsx", scenario="Proposal_2")

# Access products
for product in data['products']:
    print(f"{product['product_description']}")
    print(f"  Family: {product['product_family']}")
    print(f"  Monthly: ${product['monthly_fee']:,.2f}")
    print(f"  License: ${product['license_fee']:,.2f}")

# Check for hidden data
hidden_rows = extractor.detect_hidden_rows("data/jh_deal_sheet.xlsx")
if hidden_rows:
    print(f"Warning: {len(hidden_rows)} hidden rows detected")

# Access metadata
print(f"Total products: {data['metadata']['total_products']}")
print(f"Scenario: {data['metadata']['scenario']}")
```

---

### LLMExtractor

AI-powered extraction using Claude API.

#### Class Definition

```python
class LLMExtractor:
    """
    AI-powered extractor using Claude API.

    Provides intelligent field extraction with
    confidence scoring and validation.
    """
```

#### Constructor

```python
def __init__(
    self,
    api_key: str | None = None,
    model: str = "claude-sonnet-4-20250514"
):
    """
    Initialize the LLM extractor.

    Args:
        api_key: Anthropic API key (defaults to env var)
        model: Claude model to use
    """
```

#### Methods

##### extract_fields()

```python
def extract_fields(
    self,
    document_text: str,
    fields: list[str]
) -> dict:
    """
    Extract specific fields from document text.

    Args:
        document_text: Text content to analyze
        fields: List of field names to extract

    Returns:
        Dictionary with field values and confidence scores

    Example:
        >>> extractor = LLMExtractor()
        >>> result = extractor.extract_fields(
        ...     text, ['solution_name', 'monthly_fee']
        ... )
        >>> print(result)
        {
            'solution_name': {'value': 'HORIZON', 'confidence': 0.95},
            'monthly_fee': {'value': 15000.0, 'confidence': 0.92}
        }
    """
```

##### extract_line_items()

```python
def extract_line_items(
    self,
    document_text: str
) -> list[dict]:
    """
    Extract all line items from document.

    Args:
        document_text: Text content to analyze

    Returns:
        List of extracted line items with confidence scores

    Example:
        >>> items = extractor.extract_line_items(text)
        >>> for item in items:
        ...     print(f"{item['solution_name']}: {item['confidence']}")
    """
```

#### Usage Example

```python
from extractors.llm_extractor import LLMExtractor

# Initialize with environment variable
extractor = LLMExtractor()

# Initialize with explicit key
extractor = LLMExtractor(api_key="sk-ant-...")

# Extract specific fields
with open("proposal.txt") as f:
    text = f.read()

result = extractor.extract_fields(text, [
    'solution_name',
    'monthly_fee',
    'category'
])

for field, data in result.items():
    print(f"{field}: {data['value']} (confidence: {data['confidence']:.2%})")

# Extract all line items
items = extractor.extract_line_items(text)
print(f"Found {len(items)} line items")

# Filter by confidence
high_confidence = [i for i in items if i['confidence'] >= 0.90]
needs_review = [i for i in items if 0.70 <= i['confidence'] < 0.90]
```

---

## Mappers

### SchemaMapper

Normalizes vendor data to TCO schema.

#### Class Definition

```python
class SchemaMapper:
    """
    Maps vendor-specific data to standardized TCO schema.

    Handles fee type mapping, category classification,
    and fuzzy product matching.
    """
```

#### Methods

##### normalize()

```python
def normalize(
    self,
    data: dict,
    vendor: str,
    term: str = "7_year"
) -> list[dict]:
    """
    Normalize vendor data to TCO schema.

    Args:
        data: Extracted vendor data
        vendor: Vendor name ('FIS', 'Jack Henry')
        term: Contract term for projections

    Returns:
        List of normalized line items

    Example:
        >>> mapper = SchemaMapper()
        >>> normalized = mapper.normalize(fis_data, 'FIS', '7_year')
        >>> print(normalized[0].keys())
        dict_keys(['solution_name', 'fee_type', 'category', ...])
    """
```

##### map_fee_type()

```python
def map_fee_type(self, fee_type: str) -> str:
    """
    Map vendor fee type to standard format.

    Args:
        fee_type: Vendor-specific fee type

    Returns:
        Standard fee type string

    Example:
        >>> mapper.map_fee_type('monthly')
        'Monthly F'
    """
```

##### map_category()

```python
def map_category(
    self,
    product_name: str,
    vendor: str
) -> str:
    """
    Classify product into category.

    Args:
        product_name: Product/solution name
        vendor: Vendor name

    Returns:
        Category string

    Example:
        >>> mapper.map_category('HORIZON Bundle', 'FIS')
        'Bundle'
    """
```

##### fuzzy_match()

```python
def fuzzy_match(
    self,
    query: str,
    candidates: list[str],
    threshold: int = 80
) -> str | None:
    """
    Find best fuzzy match for product name.

    Args:
        query: Product name to match
        candidates: List of known product names
        threshold: Minimum match score (0-100)

    Returns:
        Best matching product name or None

    Example:
        >>> mapper.fuzzy_match('SilverLake Sys', ['SilverLake System'])
        'SilverLake System'
    """
```

#### Usage Example

```python
from mappers.schema_mapper import SchemaMapper

mapper = SchemaMapper()

# Normalize FIS data
fis_normalized = mapper.normalize(fis_data, vendor='FIS', term='7_year')

# Normalize JH data
jh_normalized = mapper.normalize(jh_data, vendor='Jack Henry', term='7_year')

# Manual mappings
print(mapper.map_fee_type('monthly'))  # 'Monthly F'
print(mapper.map_category('HORIZON', 'FIS'))  # 'Bundle'

# Fuzzy matching
known_products = ['SilverLake System', 'Gold Lake', 'Silver Creek']
match = mapper.fuzzy_match('SilverLake Sys', known_products)
print(match)  # 'SilverLake System'
```

---

## Writers

### TCOWriter

Writes data to TCO Excel templates.

#### Class Definition

```python
class TCOWriter:
    """
    Writes normalized data to TCO Excel templates.

    Handles column mapping, row positioning,
    and multi-year calculations.
    """
```

#### Constructor

```python
def __init__(
    self,
    template_path: str,
    output_path: str
):
    """
    Initialize the TCO writer.

    Args:
        template_path: Path to TCO template file
        output_path: Path for output file
    """
```

#### Methods

##### write_vendor_data()

```python
def write_vendor_data(
    self,
    data: list[dict],
    vendor: str
) -> int:
    """
    Write vendor data to template.

    Args:
        data: List of normalized line items
        vendor: Vendor name ('FIS', 'Jack Henry')

    Returns:
        Number of items written

    Example:
        >>> writer = TCOWriter("template.xlsx", "output.xlsx")
        >>> count = writer.write_vendor_data(data, 'FIS')
        >>> print(f"Wrote {count} items")
    """
```

##### write_line_item()

```python
def write_line_item(
    self,
    item: dict,
    vendor: str,
    row: int
) -> None:
    """
    Write single line item to specific row.

    Args:
        item: Normalized line item dictionary
        vendor: Vendor name
        row: Target row number
    """
```

##### save()

```python
def save(self) -> None:
    """
    Save the workbook to output path.

    Raises:
        PermissionError: If file is locked
    """
```

#### Usage Example

```python
from writers.tco_writer import TCOWriter

# Initialize
writer = TCOWriter("data/template.xlsx", "output/result.xlsx")

# Write FIS data
fis_count = writer.write_vendor_data(fis_normalized, vendor='FIS')
print(f"Wrote {fis_count} FIS items")

# Write JH data
jh_count = writer.write_vendor_data(jh_normalized, vendor='Jack Henry')
print(f"Wrote {jh_count} JH items")

# Save
writer.save()
print("Output saved successfully")
```

---

## Pipeline

### Pipeline Class

Orchestrates complete extraction workflow.

```python
from orchestrator.pipeline import Pipeline

pipeline = Pipeline()

# Simple run
result = pipeline.run(
    fis_file="proposal.docx",
    template="template.xlsx",
    output="output.xlsx"
)

# Full options
result = pipeline.run(
    fis_file="fis_proposal.docx",
    jh_file="jh_deal_sheet.xlsx",
    template="template.xlsx",
    output="result.xlsx",
    fis_term="7_year",
    jh_scenario="Proposal_1",
    enable_llm=True,
    validate=True
)

# Check result
print(f"Success: {result['success']}")
print(f"Items: {result['items_extracted']}")
print(f"Time: {result['processing_time']:.2f}s")
print(f"Confidence: {result['average_confidence']:.2%}")
```

---

## Quality Assurance

### QAValidator

Validates extraction results.

```python
from extraction.quality_assurance import QAValidator

validator = QAValidator()

# Validate extraction
result = validator.validate(extracted_items)

print(f"Passed: {result['passed']}")
print(f"Confidence: {result['overall_confidence']:.2%}")
print(f"Bucket: {result['bucket']}")

# Get details
for check in result['checks']:
    print(f"{check['name']}: {check['status']}")
```

---

## Data Models

### Line Item Schema

```python
@dataclass
class LineItem:
    solution_name: str
    fee_type: str  # 'Monthly F', 'Monthly V', 'Annual', 'One-Time'
    category: str  # 'Bundle', 'Non-Bundle Required', etc.
    vendor: str  # 'FIS', 'Jack Henry'
    per_unit_rate: float
    monthly_fee: float
    annual_fee: float
    one_time_fee: float
    optional: bool
    third_party: bool
    quantities_by_year: dict[str, int]
    confidence: float
    source_location: str
```

### Extraction Result

```python
@dataclass
class ExtractionResult:
    success: bool
    items_extracted: int
    line_items: list[dict]
    warnings: list[str]
    errors: list[str]
    processing_time: float
    average_confidence: float
```

---

*Last Updated: December 2024*
