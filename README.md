# TCO Automation System

<div align="center">

**Enterprise-Grade AI-Powered Vendor Proposal Processing Platform**

[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg)](#license)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-green.svg)](#project-status)

*Transform vendor proposals into standardized TCO comparisons in seconds, not hours.*

[Quick Start](#quick-start) | [Features](#features) | [Documentation](#documentation) | [API Reference](docs/API_DOCUMENTATION.md)

</div>

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
  - [Command Line Interface](#command-line-interface)
  - [Python API](#python-api)
  - [Advanced Pipeline](#advanced-pipeline)
- [Supported Vendors](#supported-vendors)
- [Assessment Criteria](#assessment-criteria)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Quality Assurance](#quality-assurance)
- [Troubleshooting](#troubleshooting)
- [Documentation](#documentation)
- [Technology Stack](#technology-stack)
- [Contributing](#contributing)
- [License](#license)
- [About This Project](#about-this-project)

---

## Overview

The **TCO Automation System** is an enterprise-grade platform that eliminates manual, error-prone data extraction from vendor pricing proposals. Using a combination of intelligent document parsing, AI-powered extraction via Claude API, and multi-layer quality assurance, the system transforms complex vendor proposals into standardized 5-7-10 year Total Cost of Ownership (TCO) Excel templates.

### The Problem

Financial institutions spend **4-10 hours manually** extracting pricing data from vendor proposals, copy-pasting values into Excel templates, and verifying calculations. This process is:
- Time-consuming and repetitive
- Error-prone (human transcription mistakes)
- Inconsistent across analysts
- Difficult to audit and verify

### The Solution

TCO Automation reduces this process to **under 60 seconds** with:
- **95-99% extraction accuracy** with AI-powered validation
- **Complete audit trail** from source to output
- **Side-by-side vendor comparison** in a single template
- **Multi-layer QA** ensuring data integrity

---

## Key Features

### Core Capabilities

| Feature | Description | Status |
|---------|-------------|--------|
| **Multi-Vendor Extraction** | Parse FIS Word documents and Jack Henry Excel files | Production |
| **AI-Powered Intelligence** | Claude API integration for intelligent field extraction | Production |
| **Schema Normalization** | Map vendor terminology to standardized TCO structure | Production |
| **Multi-Year Projections** | Support for 5, 7, and 10-year terms with growth calculations | Production |
| **Quality Assurance** | 4-layer validation with confidence scoring | Production |
| **Audit Trail** | Complete source-to-output traceability | Production |

### NEW! Recent Enhancements

| Feature | Description |
|---------|-------------|
| **Cell-by-Cell Validation** | 100% verification of extraction accuracy |
| **Formula Extraction** | Capture Excel formulas for audit compliance |
| **Comment Extraction** | Extract hidden pricing notes from cell comments |
| **Hidden Data Detection** | Alert when hidden rows/columns contain data |
| **Two-Bucket Routing** | Auto-accept vs. manual review workflow |

### Processing Highlights

- **FIS Proposals**: Bundle pricing, monthly fees, one-time credits, implementation costs
- **Jack Henry Proposals**: 500+ products, 3 scenarios, formulas, comments, licensing
- **Output**: Professional TCO template with side-by-side vendor comparison

---

## Quick Start

Get up and running in 5 minutes:

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd tco_automation

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Key (Optional - for AI features)

```bash
# Copy example environment file
cp config/.env.example .env

# Edit .env and add your Anthropic API key
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### 3. Run Your First Extraction

```bash
# Process a single FIS proposal
python main.py \
  --fis data/your_fis_proposal.docx \
  --template data/TCO_Template.xlsx \
  --output output/TCO_Result.xlsx \
  --fis-term 7_year
```

### 4. Check the Output

Open `output/TCO_Result.xlsx` and review the populated Line Items sheet.

---

## Installation

### Prerequisites

- **Python**: 3.8 or higher
- **pip**: Package installer for Python
- **Operating System**: Windows, macOS, or Linux

### Step 1: Create Virtual Environment

```bash
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Verify Installation

```bash
python -c "import openpyxl, pandas, docx; print('Core dependencies OK')"
```

### Optional: Install AI Features

For Claude API integration:

```bash
pip install anthropic tiktoken

# Set environment variable
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
```

### Optional: Install NLP Features

For enhanced text processing:

```bash
pip install spacy
python -m spacy download en_core_web_sm
```

---

## Usage

### Command Line Interface

The main entry point is `main.py`, which orchestrates the extraction workflow.

#### Process FIS Proposal Only

```bash
python main.py \
  --fis data/Echelon_FIS_Proposal.docx \
  --template data/TCO_Template.xlsx \
  --output output/FIS_TCO.xlsx \
  --fis-term 7_year
```

#### Process Jack Henry Proposal Only

```bash
python main.py \
  --jh data/JH_Deal_Sheet.xlsx \
  --template data/TCO_Template.xlsx \
  --output output/JH_TCO.xlsx \
  --jh-scenario Proposal_1
```

#### Side-by-Side Vendor Comparison

```bash
python main.py \
  --fis data/Echelon_FIS_Proposal.docx \
  --jh data/JH_Deal_Sheet.xlsx \
  --template data/TCO_Template.xlsx \
  --output output/TCO_Comparison.xlsx \
  --fis-term 7_year \
  --jh-scenario Proposal_1
```

#### CLI Arguments Reference

| Argument | Description | Default |
|----------|-------------|---------|
| `--fis PATH` | Path to FIS Word proposal (.docx) | None |
| `--jh PATH` | Path to Jack Henry Excel proposal (.xlsx) | None |
| `--template PATH` | Path to TCO Excel template (required) | - |
| `--output PATH` | Output file path (required) | - |
| `--fis-term` | FIS contract term: `5_year`, `7_year`, `10_year` | `7_year` |
| `--jh-scenario` | Jack Henry scenario: `Proposal_1`, `Proposal_2`, `Proposal_3` | `Proposal_1` |

### Python API

For programmatic integration:

```python
from extractors.fis_extractor import FISExtractor
from extractors.jh_extractor import JHExtractor
from mappers.schema_mapper import SchemaMapper
from writers.tco_writer import TCOWriter

# Extract FIS data
fis_extractor = FISExtractor()
fis_data = fis_extractor.extract("data/fis_proposal.docx")

# Normalize to TCO schema
mapper = SchemaMapper()
normalized_data = mapper.normalize(fis_data, vendor='FIS', term='7_year')

# Write to TCO template
writer = TCOWriter("data/template.xlsx", "output/result.xlsx")
writer.write_vendor_data(normalized_data, vendor='FIS')
writer.save()

print(f"Processed {len(normalized_data)} line items")
```

### Advanced Pipeline

For batch processing and scheduling:

```bash
# Process entire directory
python run_pipeline.py data/proposals/ \
  -o data/output \
  --vendor auto \
  --json

# Run scheduled job
python run_pipeline.py --schedule config/jobs.json --run-job daily_processing

# Enable verbose logging
python run_pipeline.py data/proposal.docx -o output/ --verbose
```

#### Pipeline Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `input` | Input file or directory | - |
| `-o, --output` | Output directory | `./data/output` |
| `-v, --vendor` | Vendor type: `FIS`, `Jack Henry`, `auto` | `auto` |
| `--term` | Contract term | `5_year` |
| `--scenario` | Jack Henry scenario | `Proposal_1` |
| `--no-llm` | Disable AI extraction | False |
| `--json` | Output results as JSON | False |
| `--quiet` | Suppress progress output | False |
| `--verbose` | Enable verbose logging | False |

---

## Supported Vendors

### FIS (Fiserv Integrated Software)

**Document Format**: Word documents (.docx)

**Extracted Data**:
- Bundle pricing by year (5/7/10-year terms)
- Monthly fees for non-bundle solutions
- One-time implementation fees and credits
- Third-party solution pricing
- Terms & conditions (annual increase rates)

**Key Capabilities**:
- Table detection by content keywords
- Multi-term comparison support
- Currency parsing with regex validation

### Jack Henry

**Document Format**: Excel workbooks (.xlsx)

**Extracted Data**:
- Product descriptions and families (500+ products)
- License, installation, maintenance, monthly fees
- Optional/included product flags
- Multiple proposal scenarios (Proposal_1/2/3)
- Cell comments with pricing notes
- Formulas with calculated values

**Key Capabilities**:
- Hidden row/column detection
- Dynamic data boundary finding
- Schema validation per column
- Comment extraction (3-4 levels)
- Formula preservation for audit

---

## Assessment Criteria

### Confidence Scoring System

The system uses a multi-tier confidence scoring approach:

| Tier | Confidence Range | Action |
|------|------------------|--------|
| **Auto-Accept** | >= 90% | Automatically populated, no review needed |
| **Quick Review** | 70-89% | Flagged for quick validation |
| **Manual Entry** | < 70% | Requires full manual input |

### Quality Metrics

| Metric | Target | Description |
|--------|--------|-------------|
| **Extraction Accuracy** | >= 95% | Correct value extraction rate |
| **Field Coverage** | >= 98% | Fields successfully extracted |
| **Cross-Validation** | Pass | Sum checks, rate calculations |
| **Business Rules** | Pass | Required fields, sanity checks |

### Validation Layers

1. **Confidence Scoring**: Per-field and overall confidence metrics
2. **Cross-Validation**: Sum checks, rate calculations, consistency
3. **Business Rules**: Required items, max thresholds, sanity checks
4. **Source Traceability**: Every value tracked to source location

---

## Project Structure

```
tco_automation/
├── main.py                          # CLI entry point
├── run_pipeline.py                  # Advanced pipeline runner
├── config.py                        # Configuration and mappings
├── requirements.txt                 # Python dependencies
│
├── extractors/                      # Data extraction modules
│   ├── fis_extractor.py            # FIS Word document parser
│   ├── jh_extractor.py             # Jack Henry Excel parser
│   ├── llm_extractor.py            # Claude API integration
│   └── document_loader.py          # Unified document loading
│
├── mappers/                         # Data transformation
│   └── schema_mapper.py            # Vendor → TCO normalization
│
├── writers/                         # Output generation
│   └── tco_writer.py               # Excel template population
│
├── extraction/                      # AI-powered extraction
│   ├── ai_pipeline.py              # Main AI orchestrator
│   ├── intelligent_extractor.py    # 4-stage Claude extraction
│   ├── quality_assurance.py        # 4-layer validation system
│   ├── bucket_router.py            # Auto-accept vs review routing
│   ├── review_reporter.py          # Word document generation
│   └── vendor_cache.py             # Context caching
│
├── orchestrator/                    # Pipeline management
│   ├── pipeline.py                 # Workflow orchestration
│   └── scheduler.py                # Job scheduling
│
├── preprocessors/                   # Text preparation
│   └── text_processor.py           # Cleaning, chunking, tokenization
│
├── utils/                           # Shared utilities
│   ├── helpers.py                  # Common functions
│   ├── validators.py               # Data validation
│   └── logging_config.py           # Centralized logging
│
├── config/                          # Configuration files
│   ├── .env.example                # Environment template
│   ├── extraction_prompts.py       # Claude prompts
│   └── validation_rules.json       # Custom rules
│
├── docs/                            # Documentation
│   ├── workflow.md                 # Process flows
│   ├── configuration_guide.md      # Configuration reference
│   ├── tco_methodology.md          # TCO methodology
│   ├── extraction_guide.md         # Extraction details
│   └── integration_guide.md        # Integration guide
│
└── data/                            # Input/output files
    ├── input/                      # Vendor proposals
    ├── output/                     # Generated TCOs
    └── templates/                  # TCO templates
```

---

## Configuration

### Main Configuration (`config.py`)

#### Fee Type Mappings

```python
FEE_TYPES = {
    'monthly_fixed': 'Monthly F',
    'monthly_variable': 'Monthly V',
    'annual': 'Annual',
    'one_time': 'One-Time'
}
```

#### Product Categories

```python
PRODUCT_CATEGORIES = {
    'BUNDLE': 'Bundle',
    'NON_BUNDLE_REQUIRED': 'Non-Bundle Required',
    'NON_BUNDLE_OPTIONAL': 'Non-Bundle Optional',
    'THIRD_PARTY_REQUIRED': 'Third-Party Required',
    'THIRD_PARTY_OPTIONAL': 'Third-Party Optional'
}
```

#### Growth Rates

```python
DEFAULT_GROWTH_RATE = 0.20    # 20% annual growth
DEFAULT_CPI_BUNDLE = 0.06     # 6% for bundle items
DEFAULT_CPI_NON_BUNDLE = 0.03 # 3% for non-bundle items
```

#### AI Configuration

```python
AI_CONFIG = {
    'model': 'claude-sonnet-4-20250514',
    'max_tokens': 8192,
    'temperature': 0.0,
    'max_retries': 3
}
```

#### Confidence Thresholds

```python
CONFIDENCE_THRESHOLDS = {
    'auto_accept': 0.90,
    'manual_review': 0.70,
    'reject': 0.50
}
```

### Environment Variables

Create a `.env` file in the project root:

```env
# Required for AI features
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Optional configuration
LOG_LEVEL=INFO
CACHE_DIR=vendor_cache
OUTPUT_DIR=data/output
```

See [Configuration Guide](docs/configuration_guide.md) for complete reference.

---

## Quality Assurance

### 4-Layer QA System

1. **Confidence Scoring**
   - Per-field confidence (0.0-1.0)
   - Per-item confidence
   - Overall extraction confidence

2. **Cross-Validation**
   - Sum checks (total = sum of components)
   - Rate calculations (monthly * 12 = annual)
   - Consistency checks

3. **Business Rules**
   - Required items cannot be $0
   - Max monthly fee: $500,000
   - Max one-time fee: $5,000,000

4. **Source Traceability**
   - Cell coordinates recorded
   - Source text preserved
   - Formula tracking

### Running Validation

```bash
# Cell-by-cell validation
python cell_validator.py \
  --source data/JH_proposal.xlsx \
  --tco output/TCO_Result.xlsx \
  --scenario Proposal_1

# QA validation only
python qa_validator.py output/TCO_Result.xlsx
```

---

## Troubleshooting

### Common Issues

#### "Package not found" Error

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

#### "MergedCell" Errors

Update template to avoid merged cells in data regions, or use the latest version of openpyxl:

```bash
pip install openpyxl --upgrade
```

#### Missing Data in Output

1. Verify vendor proposal format matches expected structure
2. Check `config.py` starting row numbers
3. Review extraction logs for warnings:
   ```bash
   python main.py ... --verbose
   ```

#### Incorrect Categorization

1. Update product keywords in `config.py`
2. Add custom mapping rules
3. Check vendor-specific family mappings

#### API Rate Limits

```python
# Adjust retry settings in config.py
AI_CONFIG = {
    'max_retries': 5,
    'retry_delay_seconds': 5
}
```

### Getting Help

1. Review the [Documentation](#documentation) section
2. Check [Troubleshooting Guide](docs/troubleshooting.md)
3. Open an issue in the repository

---

## Documentation

| Document | Description |
|----------|-------------|
| [Workflow Guide](docs/workflow.md) | Step-by-step process flows |
| [Configuration Guide](docs/configuration_guide.md) | Complete configuration reference |
| [TCO Methodology](docs/tco_methodology.md) | TCO calculation methodology |
| [Extraction Guide](docs/extraction_guide.md) | Detailed extraction documentation |
| [Integration Guide](docs/integration_guide.md) | Third-party integrations |
| [API Documentation](docs/API_DOCUMENTATION.md) | Python API reference |
| [Feature Catalog](FEATURE_CATALOG.md) | Complete feature inventory |
| [Testing Guide](TESTING_GUIDE.md) | Testing procedures |
| [Demo Guide](DEMO_GUIDE.md) | Demonstration walkthrough |
| [Contributing](CONTRIBUTING.md) | Contribution guidelines |

---

## Technology Stack

### Core Technologies

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.8+ | Core language |
| python-docx | 3.1.5 | Word document parsing |
| openpyxl | 3.1.5 | Excel read/write |
| pandas | 2.3.3 | Data manipulation |
| anthropic | >= 0.18.0 | Claude API integration |

### NLP & AI

| Technology | Purpose |
|------------|---------|
| Claude API | Intelligent extraction |
| spaCy | Named Entity Recognition |
| tiktoken | Token counting |
| RapidFuzz | Fuzzy string matching |

### Document Processing

| Technology | Purpose |
|------------|---------|
| pdfplumber | PDF extraction |
| PyMuPDF | PDF processing |
| Pillow | Image handling |
| pytesseract | OCR |

---

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Quick Contribution Steps

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `python -m pytest tests/`
5. Submit a pull request

---

## License

**Proprietary - Arriba Advisors LLC**

This software is proprietary and confidential. Unauthorized copying, distribution, or use is strictly prohibited.

---

## About This Project

### Demonstrated Skills

This project showcases expertise in:

- **Python Development**: Clean, modular architecture with type hints
- **Document Processing**: Multi-format parsing (DOCX, XLSX, PDF)
- **AI Integration**: Claude API for intelligent extraction
- **Data Engineering**: Schema normalization, validation, transformation
- **Quality Assurance**: Multi-layer validation with confidence scoring
- **DevOps**: CLI tools, configuration management, logging
- **Financial Domain**: TCO analysis, vendor comparison, pricing models

### Author

**Arriba Advisors LLC**

### Version

**v2.0** - December 2024

### Acknowledgments

- [Anthropic](https://anthropic.com) - Claude AI API
- [python-docx](https://python-docx.readthedocs.io/) - Word document library
- [openpyxl](https://openpyxl.readthedocs.io/) - Excel library
- [pandas](https://pandas.pydata.org/) - Data analysis library

---

<div align="center">

**Transform vendor proposals into actionable TCO comparisons.**

[Get Started](#quick-start) | [View Features](#key-features) | [Read Docs](#documentation)

</div>
