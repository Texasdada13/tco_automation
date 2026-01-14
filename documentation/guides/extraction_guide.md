# TCO Automation - Extraction Guide

**Detailed Extraction Documentation**

---

## Table of Contents

- [Overview](#overview)
- [Extraction Architecture](#extraction-architecture)
- [FIS Extraction](#fis-extraction)
- [Jack Henry Extraction](#jack-henry-extraction)
- [AI-Powered Extraction](#ai-powered-extraction)
- [Quality Assurance](#quality-assurance)
- [Schema Mapping](#schema-mapping)
- [Troubleshooting](#troubleshooting)

---

## Overview

The TCO Automation System uses multiple extraction methods to process vendor proposals. This guide provides detailed documentation on how extraction works for each vendor and method.

### Extraction Methods

| Method | Use Case | Accuracy | Speed |
|--------|----------|----------|-------|
| **Rule-Based** | Structured documents | 95%+ | Fast |
| **AI-Powered** | Complex/varied documents | 90-99% | Moderate |
| **Hybrid** | Best of both | 95-99% | Moderate |

---

## Extraction Architecture

### High-Level Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Document  │────▶│   Loader    │────▶│  Extractor  │
│   (Input)   │     │             │     │             │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
                    ┌─────────────────────────┐│
                    │     QA Validator        ││
                    └───────────┬─────────────┘│
                                │              │
                    ┌───────────▼─────────────▼┐
                    │     Schema Mapper        │
                    └───────────┬──────────────┘
                                │
                    ┌───────────▼──────────────┐
                    │     TCO Writer           │
                    └──────────────────────────┘
```

### Module Responsibilities

| Module | File | Responsibility |
|--------|------|----------------|
| Document Loader | `document_loader.py` | Load and parse documents |
| FIS Extractor | `fis_extractor.py` | Extract FIS Word proposals |
| JH Extractor | `jh_extractor.py` | Extract Jack Henry Excel |
| LLM Extractor | `llm_extractor.py` | AI-powered extraction |
| Text Processor | `text_processor.py` | Clean and chunk text |
| QA Validator | `quality_assurance.py` | Validate extraction |
| Schema Mapper | `schema_mapper.py` | Normalize to TCO format |

---

## FIS Extraction

### Document Structure

FIS proposals typically contain:
- Cover page with summary
- Pricing tables for different terms
- Bundle pricing section
- Monthly fees section
- One-time fees section
- Terms and conditions

### Extraction Process

#### Step 1: Load Document

```python
from docx import Document

doc = Document("fis_proposal.docx")
tables = doc.tables
paragraphs = doc.paragraphs
```

#### Step 2: Identify Tables

Tables are identified by content keywords:

```python
TABLE_IDENTIFIERS = {
    'bundle_pricing': ['bundle', 'HORIZON', 'core processing'],
    'monthly_fees': ['monthly', 'recurring', 'fee'],
    'one_time': ['one-time', 'implementation', 'setup'],
    'credits': ['credit', 'discount', 'waiver']
}
```

#### Step 3: Extract Table Data

```python
def extract_fis_table(table):
    data = []
    for row in table.rows:
        row_data = []
        for cell in row.cells:
            row_data.append(cell.text.strip())
        data.append(row_data)
    return data
```

#### Step 4: Parse Pricing

Currency parsing with regex:

```python
import re

CURRENCY_PATTERN = r'\$[\d,]+\.?\d*'

def parse_currency(text):
    match = re.search(CURRENCY_PATTERN, text)
    if match:
        value = match.group().replace('$', '').replace(',', '')
        return float(value)
    return 0.0
```

### FIS Data Structure

Extracted FIS data format:

```python
{
    'bundle_pricing': {
        '5_year': {
            'year_1': 150000.00,
            'year_2': 159000.00,
            # ...
        },
        '7_year': { ... },
        '10_year': { ... }
    },
    'monthly_fees': [
        {
            'solution_name': 'Statement Processing',
            'monthly_fee': 2500.00,
            'category': 'Non-Bundle Required'
        },
        # ...
    ],
    'one_time_fees': [
        {
            'description': 'Implementation Fee',
            'amount': 75000.00
        },
        # ...
    ],
    'credits': [
        {
            'description': 'Signing Bonus',
            'amount': -25000.00
        }
    ]
}
```

### FIS-Specific Challenges

| Challenge | Solution |
|-----------|----------|
| Multiple terms in one table | Parse column headers for term |
| Merged cells | Handle with try/except |
| Inconsistent formatting | Multiple regex patterns |
| Missing data | Default values with warnings |

---

## Jack Henry Extraction

### Document Structure

Jack Henry deal sheets contain:
- Product catalog with families
- Multiple proposal scenarios
- Licensing information
- Implementation costs
- Cell comments with notes

### Extraction Process

#### Step 1: Load Workbook

```python
from openpyxl import load_workbook

wb = load_workbook("jh_deal_sheet.xlsx", data_only=False)
ws = wb.active
```

#### Step 2: Find Data Boundaries

```python
def find_data_boundaries(ws):
    # Find header row
    header_row = 1
    for row in range(1, 10):
        if ws.cell(row, 1).value and 'Product' in str(ws.cell(row, 1).value):
            header_row = row
            break

    # Find data end
    data_end = header_row + 1
    while ws.cell(data_end, 1).value:
        data_end += 1

    return header_row, data_end - 1
```

#### Step 3: Extract Column Data

```python
def extract_jh_row(ws, row, scenario='Proposal_1'):
    scenario_cols = {
        'Proposal_1': {'license': 8, 'install': 9, 'maint': 10, 'monthly': 11},
        'Proposal_2': {'license': 13, 'install': 14, 'maint': 15, 'monthly': 16},
        'Proposal_3': {'license': 18, 'install': 19, 'maint': 20, 'monthly': 21}
    }

    cols = scenario_cols[scenario]

    return {
        'product_description': ws.cell(row, 1).value,
        'product_family': ws.cell(row, 2).value,
        'delivery_method': ws.cell(row, 3).value,
        'license_fee': parse_number(ws.cell(row, cols['license']).value),
        'install_fee': parse_number(ws.cell(row, cols['install']).value),
        'maintenance_fee': parse_number(ws.cell(row, cols['maint']).value),
        'monthly_fee': parse_number(ws.cell(row, cols['monthly']).value)
    }
```

#### Step 4: Extract Comments

```python
def extract_comments(ws, row, col):
    cell = ws.cell(row, col)
    if cell.comment:
        return cell.comment.text
    return None
```

#### Step 5: Extract Formulas

```python
def extract_formula(ws, row, col, data_only=False):
    if not data_only:
        cell = ws.cell(row, col)
        if cell.value and str(cell.value).startswith('='):
            return cell.value
    return None
```

### Jack Henry Data Structure

```python
{
    'products': [
        {
            'product_description': 'SilverLake Core System',
            'product_family': 'SilverLake',
            'delivery_method': 'In-House',
            'license_fee': 50000.00,
            'install_fee': 15000.00,
            'maintenance_fee': 12000.00,
            'monthly_fee': 8500.00,
            'optional': False,
            'comments': {
                'license': 'Negotiated rate',
                'monthly': 'Based on 50,000 accounts'
            },
            'formulas': {
                'total': '=H5+I5+J5+(K5*12)'
            }
        },
        # ...
    ],
    'metadata': {
        'scenario': 'Proposal_1',
        'total_products': 523,
        'hidden_rows': [45, 67, 89],
        'hidden_columns': ['L', 'M']
    }
}
```

### Jack Henry-Specific Features

#### Hidden Data Detection

```python
def detect_hidden_rows(ws):
    hidden = []
    for row in range(1, ws.max_row + 1):
        if ws.row_dimensions[row].hidden:
            hidden.append(row)
    return hidden

def detect_hidden_columns(ws):
    hidden = []
    for col in range(1, ws.max_column + 1):
        col_letter = get_column_letter(col)
        if ws.column_dimensions[col_letter].hidden:
            hidden.append(col_letter)
    return hidden
```

#### Product Family Classification

```python
PRODUCT_FAMILIES = {
    'SilverLake': 'BUNDLE',
    'Xperience': 'BUNDLE',
    'Banno': 'NON_BUNDLE',
    'OnBoard': 'NON_BUNDLE',
    'Teller': 'NON_BUNDLE',
    'Synapsys': 'NON_BUNDLE'
}

def classify_product(product_family, is_optional):
    base_category = PRODUCT_FAMILIES.get(product_family, 'NON_BUNDLE')

    if base_category == 'BUNDLE':
        return 'Bundle'
    elif is_optional:
        return 'Non-Bundle Optional'
    else:
        return 'Non-Bundle Required'
```

---

## AI-Powered Extraction

### When to Use AI

| Scenario | Recommendation |
|----------|----------------|
| Standard FIS/JH formats | Rule-based (faster) |
| Non-standard formats | AI extraction |
| Complex tables | Hybrid approach |
| Ambiguous categories | AI classification |

### Claude API Integration

#### API Call Structure

```python
from anthropic import Anthropic

client = Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])

def extract_with_llm(document_text, fields):
    prompt = f"""
    Extract the following fields from this vendor proposal:
    {json.dumps(fields)}

    Return a JSON object with each field and its value.
    Include a confidence score (0.0-1.0) for each field.

    Document:
    {document_text}
    """

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=8192,
        temperature=0.0,
        messages=[{"role": "user", "content": prompt}]
    )

    return json.loads(response.content[0].text)
```

### 4-Stage AI Pipeline

#### Stage 1: Context Analysis

```python
def analyze_context(document_text):
    prompt = """
    Analyze this vendor proposal and identify:
    1. Vendor name
    2. Document type (proposal, quote, contract)
    3. Key sections and their locations
    4. Table structures present

    Return structured JSON.
    """
    # ... API call
```

#### Stage 2: Line Item Extraction

```python
def extract_line_items(document_text, context):
    prompt = f"""
    Extract all pricing line items from this proposal.

    Context: {json.dumps(context)}

    For each line item, extract:
    - solution_name
    - fee_type (Monthly, Annual, One-Time)
    - amount
    - category
    - confidence (0.0-1.0)

    Return as JSON array.
    """
    # ... API call
```

#### Stage 3: Calculation Engine

```python
def calculate_projections(line_items, term_years=7):
    for item in line_items:
        item['projections'] = {}
        base = item['monthly_fee'] * 12 if item['fee_type'] == 'Monthly' else item['annual_fee']

        for year in range(1, term_years + 1):
            cpi = get_cpi_rate(item['category'])
            item['projections'][f'year_{year}'] = base * (1 + cpi) ** (year - 1)

    return line_items
```

#### Stage 4: QA Validation

```python
def validate_extraction(line_items, original_document):
    results = {
        'passed': [],
        'flagged': [],
        'failed': []
    }

    for item in line_items:
        confidence = item.get('confidence', 0.0)

        if confidence >= 0.90:
            results['passed'].append(item)
        elif confidence >= 0.70:
            results['flagged'].append(item)
        else:
            results['failed'].append(item)

    return results
```

### Hybrid Extraction

```python
def hybrid_extract(document_path, vendor):
    # Try rule-based first
    if vendor == 'FIS':
        rule_results = fis_extractor.extract(document_path)
    elif vendor == 'Jack Henry':
        rule_results = jh_extractor.extract(document_path)

    # Check confidence
    low_confidence_items = [
        item for item in rule_results
        if item.get('confidence', 1.0) < 0.90
    ]

    # Use AI for low-confidence items
    if low_confidence_items:
        ai_results = llm_extractor.extract(
            document_path,
            focus_items=low_confidence_items
        )

        # Merge results
        rule_results = merge_results(rule_results, ai_results)

    return rule_results
```

---

## Quality Assurance

### Confidence Scoring

```python
def calculate_field_confidence(extracted_value, context):
    confidence = 1.0

    # Check if value seems reasonable
    if not validate_value_range(extracted_value):
        confidence -= 0.2

    # Check source clarity
    if is_ambiguous_source(context):
        confidence -= 0.15

    # Check extraction method
    if used_fallback_pattern():
        confidence -= 0.1

    return max(0.0, confidence)
```

### Cross-Validation

```python
def cross_validate(line_items):
    issues = []

    for item in line_items:
        # Check annual = monthly * 12
        if item['monthly_fee'] > 0 and item['annual_fee'] > 0:
            expected_annual = item['monthly_fee'] * 12
            if abs(item['annual_fee'] - expected_annual) > expected_annual * 0.01:
                issues.append({
                    'item': item['solution_name'],
                    'issue': 'Annual/Monthly mismatch',
                    'expected': expected_annual,
                    'actual': item['annual_fee']
                })

    return issues
```

### Business Rules

```python
BUSINESS_RULES = [
    {
        'name': 'non_zero_required',
        'condition': lambda item: item['category'] != 'Optional' and item['monthly_fee'] > 0,
        'message': 'Required items must have non-zero fees'
    },
    {
        'name': 'max_monthly_fee',
        'condition': lambda item: item['monthly_fee'] <= 500000,
        'message': 'Monthly fee exceeds maximum threshold'
    }
]

def apply_business_rules(line_items):
    violations = []
    for item in line_items:
        for rule in BUSINESS_RULES:
            if not rule['condition'](item):
                violations.append({
                    'item': item['solution_name'],
                    'rule': rule['name'],
                    'message': rule['message']
                })
    return violations
```

---

## Schema Mapping

### Normalization Process

```python
def normalize_to_tco(extracted_data, vendor):
    normalized = []

    for item in extracted_data:
        normalized_item = {
            'solution_name': normalize_solution_name(item),
            'fee_type': map_fee_type(item, vendor),
            'category': map_category(item, vendor),
            'vendor': vendor,
            'per_unit_rate': item.get('unit_rate', 0.0),
            'monthly_fee': item.get('monthly_fee', 0.0),
            'annual_fee': item.get('annual_fee', 0.0),
            'one_time_fee': item.get('one_time_fee', 0.0),
            'optional': item.get('optional', False),
            'third_party': item.get('third_party', False),
            'quantities_by_year': calculate_quantities(item)
        }
        normalized.append(normalized_item)

    return normalized
```

### Fuzzy Matching

```python
from rapidfuzz import fuzz, process

def fuzzy_match_product(product_name, known_products):
    matches = process.extract(
        product_name,
        known_products.keys(),
        scorer=fuzz.token_set_ratio,
        limit=3
    )

    if matches and matches[0][1] >= 80:  # 80% match threshold
        return known_products[matches[0][0]]

    return None
```

---

## Troubleshooting

### Common Extraction Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Missing tables | Table not recognized | Add keywords to identifiers |
| Wrong category | Keyword mismatch | Update category keywords |
| Zero values | Parse failure | Check regex patterns |
| Duplicate items | Row re-processing | Add deduplication |

### Debug Commands

```bash
# Test FIS extraction
python -m extractors.fis_extractor data/test_fis.docx --debug

# Test JH extraction
python -m extractors.jh_extractor data/test_jh.xlsx --debug

# Test schema mapping
python -m mappers.schema_mapper --test

# Validate extraction
python qa_validator.py output/result.xlsx --verbose
```

### Logging

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('extraction')
```

View extraction logs:

```bash
tail -f logs/extraction.log
```

---

*Last Updated: December 2024*
