# TCO Automation - Configuration Guide

**Complete Configuration Reference**

---

## Table of Contents

- [Overview](#overview)
- [Configuration Files](#configuration-files)
- [Main Configuration (config.py)](#main-configuration-configpy)
- [Environment Variables](#environment-variables)
- [AI Configuration](#ai-configuration)
- [Quality Assurance Settings](#quality-assurance-settings)
- [Vendor-Specific Configuration](#vendor-specific-configuration)
- [Excel Template Configuration](#excel-template-configuration)
- [Caching Configuration](#caching-configuration)
- [Logging Configuration](#logging-configuration)
- [Advanced Configuration](#advanced-configuration)

---

## Overview

The TCO Automation System uses multiple configuration sources to customize behavior. This guide provides a complete reference for all configuration options.

### Configuration Hierarchy

```
1. Environment Variables (.env)     ◄── Highest priority
2. Command-line Arguments
3. config.py Settings
4. Default Values                   ◄── Lowest priority
```

---

## Configuration Files

| File | Purpose | Format |
|------|---------|--------|
| `config.py` | Main configuration | Python |
| `.env` | Environment variables | Key=Value |
| `config/jobs.json` | Scheduler jobs | JSON |
| `config/validation_rules.json` | Custom validation | JSON |
| `config/extraction_prompts.py` | AI prompts | Python |

---

## Main Configuration (config.py)

### Fee Type Mappings

Define how fee types are labeled in the TCO template:

```python
FEE_TYPES = {
    'monthly_fixed': 'Monthly F',
    'monthly_variable': 'Monthly V',
    'annual': 'Annual',
    'one_time': 'One-Time'
}
```

**Customization**: Modify values to match your template's fee type labels.

---

### Product Categories

Define product categorization labels:

```python
PRODUCT_CATEGORIES = {
    'BUNDLE': 'Bundle',
    'NON_BUNDLE_REQUIRED': 'Non-Bundle Required',
    'NON_BUNDLE_OPTIONAL': 'Non-Bundle Optional',
    'THIRD_PARTY_REQUIRED': 'Third-Party Required',
    'THIRD_PARTY_OPTIONAL': 'Third-Party Optional'
}
```

**Customization**: Adjust labels to match your TCO template.

---

### FIS-Specific Keywords

Keywords used to identify FIS product categories:

```python
FIS_BUNDLE_KEYWORDS = [
    'HORIZON',
    'core processing',
    'bundle',
    'Digital One',
    'Payments One',
    'ImageCentre'
]

FIS_NON_BUNDLE_KEYWORDS = [
    'Paper',
    'Envelopes',
    'Forms',
    'Statements'
]

FIS_THIRD_PARTY_KEYWORDS = [
    'third party',
    'third-party',
    '3rd party'
]
```

**Customization**: Add or remove keywords based on your FIS proposal terminology.

---

### Jack Henry Product Families

Map Jack Henry product families to categories:

```python
JH_PRODUCT_FAMILIES = {
    'SilverLake': 'BUNDLE',
    'Xperience': 'BUNDLE',
    'OnBoard': 'NON_BUNDLE',
    'Teller': 'NON_BUNDLE',
    'Banno': 'NON_BUNDLE',
    'Synapsys': 'NON_BUNDLE',
    'jhaPaymentSolutions': 'NON_BUNDLE',
    'ProfitStars': 'NON_BUNDLE'
}
```

**Customization**: Add new product families as they appear in proposals.

---

### Growth Rate Configuration

Default rates for multi-year projections:

```python
# Annual growth rate for quantities
DEFAULT_GROWTH_RATE = 0.20  # 20%

# CPI (Cost Per Item) increase rates
DEFAULT_CPI_BUNDLE = 0.06      # 6% for bundle items
DEFAULT_CPI_NON_BUNDLE = 0.03  # 3% for non-bundle items
DEFAULT_CPI_THIRD_PARTY = 0.05 # 5% for third-party
```

**Customization**: Adjust based on your organization's projection assumptions.

---

### Excel Column Mappings

Define which columns in the TCO template correspond to which data:

```python
TCO_COLUMNS = {
    'FIS': {
        'fee_type': 'B',
        'quantity_year_1': 'C',
        'quantity_year_2': 'D',
        'quantity_year_3': 'E',
        'quantity_year_4': 'F',
        'quantity_year_5': 'G',
        'quantity_year_6': 'H',
        'quantity_year_7': 'I',
        'solution_name': 'O',
        'category': 'P',
        'per_unit_rate': 'Q',
        'year_1_cost': 'S',
        'year_2_cost': 'T',
        'year_3_cost': 'U',
        'year_4_cost': 'V',
        'year_5_cost': 'W',
        'year_6_cost': 'X',
        'year_7_cost': 'Y'
    },
    'JACK_HENRY': {
        'fee_type': 'AO',
        'quantity_year_1': 'AP',
        'quantity_year_2': 'AQ',
        'quantity_year_3': 'AR',
        'quantity_year_4': 'AS',
        'quantity_year_5': 'AT',
        'quantity_year_6': 'AU',
        'quantity_year_7': 'AV',
        'solution_name': 'BB',
        'category': 'BC',
        'per_unit_rate': 'BD',
        'year_1_cost': 'BF',
        'year_2_cost': 'BG',
        'year_3_cost': 'BH',
        'year_4_cost': 'BI',
        'year_5_cost': 'BJ',
        'year_6_cost': 'BK',
        'year_7_cost': 'BL'
    }
}
```

**Customization**: Update column letters if your template structure differs.

---

### Starting Row Configuration

Define where each category section begins in the template:

```python
LINE_ITEM_START_ROWS = {
    'FIS_BUNDLE': 7,
    'FIS_NON_BUNDLE_REQUIRED': 22,
    'FIS_NON_BUNDLE_OPTIONAL': 100,
    'FIS_ONE_TIME': 150,
    'JH_BUNDLE': 7,
    'JH_NON_BUNDLE_REQUIRED': 50,
    'JH_NON_BUNDLE_OPTIONAL': 100,
    'JH_ONE_TIME': 150
}
```

**Customization**: Adjust row numbers based on your template layout.

---

## Environment Variables

### Required Variables

```bash
# Anthropic API key (required for AI features)
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### Optional Variables

```bash
# Logging level: DEBUG, INFO, WARNING, ERROR
LOG_LEVEL=INFO

# Cache directory for vendor context
CACHE_DIR=vendor_cache

# Default output directory
OUTPUT_DIR=data/output

# Enable/disable features
ENABLE_LLM=true
ENABLE_CACHING=true
ENABLE_VALIDATION=true
```

### Creating .env File

```bash
# Copy example file
cp config/.env.example .env

# Edit with your values
nano .env
```

Example `.env`:
```
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxx
LOG_LEVEL=INFO
CACHE_DIR=vendor_cache
OUTPUT_DIR=data/output
ENABLE_LLM=true
```

---

## AI Configuration

### Model Settings

```python
AI_CONFIG = {
    # Claude model to use
    'model': 'claude-sonnet-4-20250514',

    # Maximum tokens in response
    'max_tokens': 8192,

    # Temperature (0.0 = deterministic)
    'temperature': 0.0,

    # Retry settings
    'max_retries': 3,
    'retry_delay_seconds': 2,

    # Token limits
    'max_input_tokens': 100000,
    'chunk_size': 4000,
    'chunk_overlap': 200
}
```

### Model Options

| Model | Speed | Cost | Best For |
|-------|-------|------|----------|
| `claude-sonnet-4-20250514` | Fast | Low | Standard extraction |
| `claude-opus-4-20250514` | Slow | High | Complex documents |
| `claude-haiku-3-5-20241022` | Fastest | Lowest | Simple extraction |

### Prompt Configuration

Edit `config/extraction_prompts.py`:

```python
EXTRACTION_PROMPT = """
Extract pricing information from the following document.

Return a JSON object with:
- solution_name: Product/service name
- fee_type: One of "Monthly F", "Monthly V", "Annual", "One-Time"
- amount: Numeric value
- confidence: Your confidence score (0.0-1.0)

Document:
{document_text}
"""
```

---

## Quality Assurance Settings

### Confidence Thresholds

```python
CONFIDENCE_THRESHOLDS = {
    # Items >= this are auto-accepted
    'auto_accept': 0.90,

    # Items >= this but < auto_accept need quick review
    'manual_review': 0.70,

    # Items < this are rejected/flagged
    'reject': 0.50
}
```

### QA Configuration

```python
QA_CONFIG = {
    # Enable/disable QA layers
    'enable_confidence_check': True,
    'enable_cross_validation': True,
    'enable_business_rules': True,
    'enable_traceability': True,

    # Confidence requirements
    'min_field_confidence': 0.85,
    'min_item_confidence': 0.90,

    # Business rule settings
    'allow_zero_required_items': False,
    'max_monthly_fee': 500000,
    'max_one_time_fee': 5000000,

    # Tolerance for calculations
    'sum_tolerance': 0.02,      # 2%
    'rate_tolerance': 0.01      # 1%
}
```

### Custom Validation Rules

Edit `config/validation_rules.json`:

```json
{
  "rules": [
    {
      "name": "monthly_fee_range",
      "field": "monthly_fee",
      "condition": "between",
      "min": 0,
      "max": 500000,
      "severity": "error"
    },
    {
      "name": "required_solution_name",
      "field": "solution_name",
      "condition": "not_empty",
      "severity": "error"
    },
    {
      "name": "annual_monthly_consistency",
      "condition": "expression",
      "expression": "annual_fee == monthly_fee * 12",
      "tolerance": 0.01,
      "severity": "warning"
    }
  ]
}
```

---

## Vendor-Specific Configuration

### FIS Configuration

```python
FIS_CONFIG = {
    # Document structure
    'table_detection_keywords': [
        'bundle pricing',
        'monthly fees',
        'one-time fees',
        'implementation'
    ],

    # Contract terms
    'supported_terms': ['5_year', '7_year', '10_year'],
    'default_term': '7_year',

    # Currency parsing
    'currency_pattern': r'\$[\d,]+\.?\d*',
    'thousand_separator': ',',
    'decimal_separator': '.'
}
```

### Jack Henry Configuration

```python
JH_CONFIG = {
    # Sheet structure
    'data_sheet_name': 'Pricing',
    'header_row': 1,
    'data_start_row': 2,

    # Scenario columns
    'scenarios': {
        'Proposal_1': {'start_col': 'H', 'end_col': 'L'},
        'Proposal_2': {'start_col': 'M', 'end_col': 'Q'},
        'Proposal_3': {'start_col': 'R', 'end_col': 'V'}
    },

    # Column mappings
    'column_mappings': {
        'product_description': 'A',
        'product_family': 'B',
        'delivery_method': 'C',
        'install': 'D',
        'license': 'E',
        'maintenance': 'F',
        'monthly': 'G'
    },

    # Detection options
    'detect_hidden_rows': True,
    'detect_hidden_columns': True,
    'extract_comments': True,
    'extract_formulas': True
}
```

---

## Excel Template Configuration

### Template Structure

```python
TEMPLATE_CONFIG = {
    # Sheet names
    'line_items_sheet': 'Line Items',
    'summary_sheet': 'Summary',

    # Vendor sections
    'fis_section': {
        'start_col': 'B',
        'end_col': 'Y'
    },
    'jh_section': {
        'start_col': 'AO',
        'end_col': 'BL'
    },

    # Row limits
    'max_bundle_rows': 50,
    'max_non_bundle_rows': 100,
    'max_one_time_rows': 50,

    # Formatting
    'preserve_formulas': True,
    'preserve_formatting': True,
    'auto_fit_columns': False
}
```

### Output Configuration

```python
OUTPUT_CONFIG = {
    # File naming
    'timestamp_format': '%Y%m%d_%H%M%S',
    'default_suffix': '_TCO',

    # Backup
    'create_backup': True,
    'backup_suffix': '_backup',

    # Audit trail
    'generate_audit_json': True,
    'generate_review_doc': True
}
```

---

## Caching Configuration

### Vendor Context Cache

```python
CACHE_CONFIG = {
    # Enable/disable caching
    'enabled': True,

    # Storage location
    'cache_directory': 'vendor_cache',

    # Cache lifetime
    'cache_expiry_days': 90,

    # Quality thresholds
    'min_confidence_to_cache': 0.70,

    # Size limits
    'max_cache_entries_per_vendor': 100,
    'max_cache_size_mb': 50
}
```

### Cache Management Commands

```bash
# Clear all cache
rm -rf vendor_cache/*

# Clear specific vendor cache
rm -rf vendor_cache/FIS/*

# View cache status
python -c "from extraction.vendor_cache import VendorCache; vc = VendorCache(); print(vc.status())"
```

---

## Logging Configuration

### Log Settings

```python
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
        'detailed': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'standard',
            'stream': 'ext://sys.stdout'
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'detailed',
            'filename': 'logs/tco_automation.log',
            'maxBytes': 10485760,
            'backupCount': 5
        }
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['console', 'file']
    }
}
```

### Log Levels

| Level | Purpose |
|-------|---------|
| DEBUG | Detailed debugging information |
| INFO | General progress information |
| WARNING | Potential issues |
| ERROR | Errors that need attention |
| CRITICAL | Critical failures |

---

## Advanced Configuration

### Performance Tuning

```python
PERFORMANCE_CONFIG = {
    # Parallel processing
    'max_workers': 4,
    'enable_multiprocessing': False,

    # Memory management
    'chunk_size': 1000,
    'batch_size': 10,

    # Timeouts
    'api_timeout_seconds': 120,
    'file_timeout_seconds': 60
}
```

### Security Settings

```python
SECURITY_CONFIG = {
    # API key handling
    'mask_api_keys_in_logs': True,

    # File handling
    'max_file_size_mb': 50,
    'allowed_extensions': ['.docx', '.xlsx', '.pdf'],

    # Output
    'sanitize_output_filenames': True
}
```

### Feature Flags

```python
FEATURE_FLAGS = {
    # Extraction features
    'enable_llm_extraction': True,
    'enable_regex_fallback': True,
    'enable_ner_extraction': True,

    # QA features
    'enable_confidence_scoring': True,
    'enable_cross_validation': True,
    'enable_business_rules': True,

    # Output features
    'enable_audit_trail': True,
    'enable_review_reports': True,

    # Experimental
    'enable_pdf_extraction': False,
    'enable_ocr': False
}
```

---

## Configuration Examples

### Minimal Configuration

For basic operation with defaults:

```python
# config.py - minimal
FEE_TYPES = {'monthly_fixed': 'Monthly F', 'one_time': 'One-Time'}
PRODUCT_CATEGORIES = {'BUNDLE': 'Bundle', 'NON_BUNDLE_REQUIRED': 'Non-Bundle Required'}
LINE_ITEM_START_ROWS = {'FIS_BUNDLE': 7, 'FIS_NON_BUNDLE_REQUIRED': 22}
```

### Production Configuration

For production deployment:

```python
# Enable all QA features
QA_CONFIG = {
    'enable_confidence_check': True,
    'enable_cross_validation': True,
    'enable_business_rules': True,
    'enable_traceability': True,
    'min_item_confidence': 0.90
}

# Strict thresholds
CONFIDENCE_THRESHOLDS = {
    'auto_accept': 0.95,
    'manual_review': 0.80,
    'reject': 0.60
}

# Full logging
LOGGING_CONFIG = {
    'root': {'level': 'INFO', 'handlers': ['console', 'file']}
}
```

---

## Troubleshooting Configuration

### Common Issues

| Issue | Solution |
|-------|----------|
| API key not found | Check `.env` file exists and has correct key |
| Wrong columns populated | Verify `TCO_COLUMNS` matches your template |
| Categories incorrect | Update keyword lists in config.py |
| Cache not working | Check `CACHE_CONFIG['enabled']` is True |

### Validation Commands

```bash
# Validate config.py syntax
python -c "import config; print('Config OK')"

# Check environment variables
python -c "import os; print(os.environ.get('ANTHROPIC_API_KEY', 'NOT SET'))"

# Test column mappings
python -c "from config import TCO_COLUMNS; print(TCO_COLUMNS['FIS'])"
```

---

*Last Updated: December 2024*
