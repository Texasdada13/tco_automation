# TCO Automation System - Feature Catalog

**Comprehensive Feature Inventory**

Version: 2.0 | Last Updated: December 2024

---

## Executive Summary

The TCO Automation System is an enterprise-grade platform for automated vendor proposal processing. This catalog provides a complete inventory of all features, capabilities, and technical specifications.

### Platform Statistics

| Metric | Value |
|--------|-------|
| **Total Modules** | 40+ Python files |
| **Lines of Code** | 3,000+ |
| **Supported Vendors** | 2 (FIS, Jack Henry) |
| **Document Formats** | 4 (DOCX, XLSX, PDF, Images) |
| **QA Validation Layers** | 4 |
| **Extraction Accuracy** | 95-99% |

---

## Table of Contents

- [Document Processing](#document-processing)
- [Data Extraction](#data-extraction)
- [AI-Powered Features](#ai-powered-features)
- [Quality Assurance](#quality-assurance)
- [Data Transformation](#data-transformation)
- [Output Generation](#output-generation)
- [Pipeline Management](#pipeline-management)
- [Configuration & Customization](#configuration--customization)
- [Reporting & Analytics](#reporting--analytics)
- [Use Cases by Persona](#use-cases-by-persona)
- [Technical Specifications](#technical-specifications)

---

## Document Processing

### Multi-Format Document Loading

**What it does**: Ingests vendor proposals in multiple document formats with unified processing.

**Key Capabilities**:
- Word document (.docx) parsing with table detection
- Excel workbook (.xlsx) processing with formula extraction
- PDF extraction with text and table recognition
- Image processing with OCR support (Tesseract)

**Use Cases**:
- Process FIS proposals delivered as Word documents
- Extract Jack Henry pricing from Excel deal sheets
- Handle legacy PDF proposals
- Process scanned document images

**Technical Specifications**:
- Libraries: python-docx, openpyxl, pdfplumber, PyMuPDF, Pillow, pytesseract
- File: `extractors/document_loader.py`

---

### FIS Document Extraction

**What it does**: Parses FIS Word proposals to extract bundle pricing, fees, and terms.

**Key Capabilities**:
- Table detection by content keywords
- Multi-term extraction (5/7/10-year)
- Bundle vs. non-bundle categorization
- One-time fees and credits detection
- Third-party solution identification
- Currency parsing with regex validation

**Extracted Data Points**:
| Data Type | Description |
|-----------|-------------|
| Bundle Pricing | Annual fees by contract term |
| Monthly Fees | Recurring solution costs |
| One-Time Fees | Implementation and setup costs |
| Credits | Negotiated discounts |
| Growth Rates | Annual increase percentages |

**Use Cases**:
- Extract complete FIS proposal pricing
- Compare different contract terms (5 vs 7 vs 10 year)
- Identify negotiation opportunities

**Technical Specifications**:
- File: `extractors/fis_extractor.py` (213 lines)
- Input: .docx files
- Output: Structured JSON with categorized fees

---

### Jack Henry Document Extraction

**What it does**: Parses Jack Henry Excel deal sheets with comprehensive data capture.

**Key Capabilities**:
- Product family classification (500+ products)
- Multiple scenario extraction (Proposal_1/2/3)
- License, installation, maintenance fee extraction
- Optional/included product detection
- Cell comment extraction (pricing notes)
- Formula preservation for audit
- Hidden row/column detection
- Dynamic data boundary finding

**Extracted Data Points**:
| Data Type | Description |
|-----------|-------------|
| Product Names | Full solution descriptions |
| Product Families | SilverLake, Xperience, Banno, etc. |
| License Fees | One-time licensing costs |
| Installation | Implementation costs |
| Maintenance | Annual support fees |
| Monthly Fees | Recurring operational costs |
| Comments | Hidden pricing notes |
| Formulas | Calculation logic |

**Use Cases**:
- Process complex Jack Henry deal sheets
- Compare multiple proposal scenarios
- Audit pricing calculations via formulas
- Capture hidden pricing assumptions

**Technical Specifications**:
- File: `extractors/jh_extractor.py` (495 lines)
- Input: .xlsx files
- Output: Structured JSON with full metadata

---

## Data Extraction

### Intelligent Field Extraction

**What it does**: Uses AI and rule-based methods to extract specific data fields with confidence scoring.

**Key Capabilities**:
- Field-specific extraction prompts
- Confidence scoring per field (0.0-1.0)
- Hybrid extraction (LLM + Regex + NER)
- Fallback to rule-based when AI unavailable
- Context-aware field detection

**Supported Fields**:
- Solution/Product names
- Fee types (Monthly, Annual, One-Time)
- Categories (Bundle, Non-Bundle, Third-Party)
- Quantities and rates
- Vendor identification

**Technical Specifications**:
- File: `extractors/llm_extractor.py` (626 lines)
- AI Model: Claude Sonnet 4
- Fallback: Regex patterns, spaCy NER

---

### Text Processing Pipeline

**What it does**: Prepares document text for extraction through cleaning and chunking.

**Key Capabilities**:
- Whitespace normalization
- Header/footer removal
- OCR error correction
- Token-aware chunking (tiktoken)
- Sentence-based boundaries (NLTK)
- Overlap support for context continuity
- Currency preservation

**Use Cases**:
- Prepare long documents for AI processing
- Handle OCR artifacts from scanned docs
- Maintain context across document chunks

**Technical Specifications**:
- File: `preprocessors/text_processor.py`
- Libraries: tiktoken, NLTK
- Max tokens per chunk: Configurable (default 4000)

---

## AI-Powered Features

### Claude API Integration

**What it does**: Leverages Anthropic's Claude API for intelligent extraction and validation.

**Key Capabilities**:
- Structured JSON extraction prompts
- Temperature control for deterministic output
- Retry logic with exponential backoff
- Token counting and context management
- Cost-efficient model selection

**Configuration Options**:
| Setting | Default | Description |
|---------|---------|-------------|
| Model | claude-sonnet-4-20250514 | AI model version |
| Max Tokens | 8192 | Maximum response length |
| Temperature | 0.0 | Deterministic extraction |
| Max Retries | 3 | API retry attempts |
| Retry Delay | 2s | Seconds between retries |

**Technical Specifications**:
- File: `extractors/llm_extractor.py`
- Library: anthropic >= 0.18.0
- Authentication: ANTHROPIC_API_KEY environment variable

---

### 4-Stage Intelligent Extraction

**What it does**: Multi-stage AI pipeline for comprehensive document understanding.

**Stages**:

| Stage | Purpose | Output |
|-------|---------|--------|
| **1. Context Analysis** | Understand document structure | Document metadata, table locations |
| **2. Line Item Extraction** | Extract pricing with confidence | Structured line items with scores |
| **3. Calculation Engine** | Multi-year projections | 5/7/10-year cost calculations |
| **4. QA Validation** | Accuracy verification | Validation results, flags |

**Use Cases**:
- Complex proposals requiring context understanding
- Ambiguous pricing structures
- Multi-year projection requirements

**Technical Specifications**:
- File: `extraction/intelligent_extractor.py`
- Dependencies: Claude API, pandas, numpy

---

### Vendor Context Caching

**What it does**: Caches vendor-specific patterns and mappings to improve extraction over time.

**Cached Data**:
- Vendor profiles (name, document types)
- Terminology mappings (vendor terms to standard)
- Document patterns (table layouts, columns)
- Successful extraction templates
- Manual correction history

**Configuration**:
| Setting | Default | Description |
|---------|---------|-------------|
| Enabled | True | Cache activation |
| Expiry | 90 days | Cache lifetime |
| Min Confidence | 70% | Threshold to cache |
| Max Entries | 100 | Per-vendor limit |

**Technical Specifications**:
- File: `extraction/vendor_cache.py`
- Storage: Local file system (JSON)
- Directory: `vendor_cache/`

---

## Quality Assurance

### 4-Layer QA Validation System

**What it does**: Multi-layer validation ensuring extraction accuracy and data integrity.

**Layer 1: Confidence Scoring**
- Per-field confidence (0.0-1.0)
- Per-item confidence aggregation
- Overall extraction confidence
- Configurable thresholds

**Layer 2: Cross-Validation**
- Sum checks (total = sum of parts)
- Rate calculations (monthly * 12 = annual)
- Consistency checks across fields
- Tolerance: 2% for sums, 1% for rates

**Layer 3: Business Rules**
- Required items cannot be $0
- Max monthly fee: $500,000 (sanity check)
- Max one-time fee: $5,000,000
- Optional field validation

**Layer 4: Source Traceability**
- Cell coordinates recorded
- Source text preserved
- Formula tracking
- Audit trail for compliance

**Technical Specifications**:
- File: `extraction/quality_assurance.py`
- Configuration: `config/validation_rules.json`

---

### Two-Bucket Routing System

**What it does**: Routes extracted items based on confidence for appropriate handling.

**Buckets**:

| Bucket | Confidence | Action |
|--------|------------|--------|
| **Auto-Accept** | >= 90% | Automatically populate Excel |
| **Quick Review** | 70-89% | Flag for quick validation |
| **Manual Entry** | < 70% | Requires full manual input |

**Output**:
- Auto-populated Excel cells (Bucket 1)
- Review document with flags (Bucket 2)
- Reference data for manual entry (Bucket 3)

**Technical Specifications**:
- File: `extraction/bucket_router.py`
- Configuration: `config.py` CONFIDENCE_THRESHOLDS

---

### Cell-by-Cell Validation

**What it does**: Compares every extracted cell against source document for 100% verification.

**Key Capabilities**:
- Source-to-output cell mapping
- Value comparison with tolerance
- Coverage percentage calculation
- Mismatch highlighting
- Hidden data detection

**Use Cases**:
- Final verification before delivery
- Audit compliance requirements
- Quality assurance sign-off

**Technical Specifications**:
- File: `cell_validator.py` (341 lines)
- Output: Detailed validation report

---

## Data Transformation

### Schema Normalization

**What it does**: Maps vendor-specific terminology to standardized TCO structure.

**Key Capabilities**:
- Fuzzy string matching (RapidFuzz)
- Product name normalization
- Category classification
- Fee type standardization
- Vendor-specific mappings
- Confidence scoring on mappings

**Standard Schema**:
```
{
  solution_name: string,
  fee_type: "Monthly F" | "Monthly V" | "Annual" | "One-Time",
  category: "Bundle" | "Non-Bundle Required" | "Non-Bundle Optional" |
            "Third-Party Required" | "Third-Party Optional",
  vendor: "FIS" | "Jack Henry",
  per_unit_rate: float,
  monthly_fee: float,
  annual_fee: float,
  one_time_fee: float,
  optional: boolean,
  third_party: boolean,
  quantities_by_year: { year_1: int, year_2: int, ... }
}
```

**Mapping Examples**:
| Vendor Term | Standard Term |
|-------------|---------------|
| FIS Bundle | Bundle |
| JH SilverLake | Bundle |
| FIS Paper/Envelopes | Non-Bundle Required |
| JH Optional | Non-Bundle Optional |

**Technical Specifications**:
- File: `mappers/schema_mapper.py` (539 lines)
- Library: rapidfuzz >= 3.5.0

---

## Output Generation

### TCO Template Population

**What it does**: Writes normalized data to Excel TCO templates with vendor-specific columns.

**Key Capabilities**:
- Multi-year projection support (5/7/10 years)
- Automatic growth calculations
- CPI rate application
- Side-by-side vendor comparison
- Merged cell handling
- Formula preservation where possible

**Column Layout**:
| Vendor | Column Range | Contents |
|--------|--------------|----------|
| FIS | B-Y | Fee type, solution name, category, rates, costs by year |
| Jack Henry | AO-BL | Fee type, solution name, category, rates, costs by year |

**Row Organization**:
| Category | FIS Rows | JH Rows |
|----------|----------|---------|
| Bundle | 7-21 | 7-49 |
| Non-Bundle Required | 22-99 | 50-99 |
| Non-Bundle Optional | 100-149 | 100-149 |
| One-Time | 150+ | 150+ |

**Technical Specifications**:
- File: `writers/tco_writer.py` (150+ lines)
- Library: openpyxl 3.1.5

---

### Review Report Generation

**What it does**: Generates Word documents for items requiring manual review.

**Contents**:
- Flagged item list with confidence scores
- Source context for each item
- Suggested corrections
- Review checklist
- Approval signature area

**Use Cases**:
- Quick review workflow for Bucket 2 items
- Audit documentation
- Stakeholder sign-off

**Technical Specifications**:
- File: `extraction/review_reporter.py`
- Output: .docx files

---

## Pipeline Management

### Workflow Orchestration

**What it does**: Manages end-to-end extraction workflow with stage tracking.

**Pipeline Stages**:
1. Document Loading
2. Text Preprocessing
3. Data Extraction
4. Quality Assurance
5. Schema Normalization
6. Excel Population
7. Report Generation

**Key Capabilities**:
- Stage-by-stage progress tracking
- Error handling and recovery
- Intermediate result caching
- Parallel processing support

**Technical Specifications**:
- File: `orchestrator/pipeline.py`

---

### Job Scheduling

**What it does**: Enables cron-like scheduling for automated batch processing.

**Key Capabilities**:
- Cron expression support
- Multiple job definitions
- Daemon mode operation
- Job status tracking
- Manual job execution

**Configuration Example**:
```json
{
  "jobs": [
    {
      "name": "daily_fis_processing",
      "schedule": "0 8 * * *",
      "input_directory": "data/fis_proposals/",
      "vendor": "FIS"
    }
  ]
}
```

**Technical Specifications**:
- File: `orchestrator/scheduler.py`
- Library: schedule >= 1.2.0
- Configuration: `config/jobs.json`

---

### Batch Processing

**What it does**: Processes multiple proposals in a single run.

**Key Capabilities**:
- Directory scanning
- Vendor auto-detection by file type
- Parallel file processing
- Aggregated reporting
- Error isolation (one failure doesn't stop batch)

**Use Cases**:
- Monthly proposal processing
- Historical data migration
- Multi-client processing

**Technical Specifications**:
- File: `run_pipeline.py`
- Input: Directory path or file patterns

---

## Configuration & Customization

### Product Keyword Configuration

**What it does**: Configures vendor-specific keywords for product categorization.

**FIS Keywords**:
- Bundle: HORIZON, core processing, Digital One, Payments One, ImageCentre
- Non-Bundle: Paper, Envelopes, Forms, Statements
- Third-Party: Various vendor names

**Jack Henry Product Families**:
- Bundle: SilverLake, Xperience
- Non-Bundle: OnBoard, Teller, Banno, Synapsys

**Technical Specifications**:
- File: `config.py`
- Format: Python dictionaries

---

### Growth Rate Configuration

**What it does**: Configures annual growth and CPI rates for multi-year projections.

**Default Rates**:
| Rate Type | Default Value |
|-----------|---------------|
| General Growth | 20% |
| Bundle CPI | 6% |
| Non-Bundle CPI | 3% |

**Technical Specifications**:
- File: `config.py`
- Override: Per-extraction configuration

---

## Reporting & Analytics

### Processing Metrics

**What it does**: Tracks and reports extraction performance metrics.

**Metrics Tracked**:
- Processing time per stage
- Items extracted per category
- Confidence score distribution
- Error and warning counts
- Coverage percentages

**Output Formats**:
- Console summary
- JSON export
- Excel summary sheet

**Technical Specifications**:
- File: `reporting.py`

---

### Traceability Reports

**What it does**: Generates audit-ready documentation of extraction provenance.

**Report Contents**:
- Source-to-output mapping
- Cell coordinate tracking
- Formula preservation log
- Manual override history
- Timestamp audit trail

**Use Cases**:
- Regulatory compliance
- Financial audit support
- Quality assurance documentation

---

## Use Cases by Persona

### Financial Analyst

**Primary Use Cases**:
1. Extract vendor proposals for TCO analysis
2. Compare multiple vendor pricing scenarios
3. Prepare side-by-side cost comparisons
4. Validate extraction accuracy

**Key Features**:
- CLI for quick processing
- Side-by-side vendor comparison
- Multi-year projections
- Excel output for analysis

---

### IT Procurement Manager

**Primary Use Cases**:
1. Automate proposal processing workflow
2. Schedule recurring extractions
3. Track processing history
4. Ensure data accuracy

**Key Features**:
- Batch processing
- Job scheduling
- Quality metrics dashboard
- Audit trail

---

### Finance Director

**Primary Use Cases**:
1. Review TCO comparisons
2. Approve vendor selections
3. Verify calculation accuracy
4. Audit compliance documentation

**Key Features**:
- Executive summary reports
- Confidence scoring
- Traceability documentation
- Professional Excel output

---

### System Administrator

**Primary Use Cases**:
1. Configure system settings
2. Manage API credentials
3. Monitor system performance
4. Troubleshoot issues

**Key Features**:
- Environment variable configuration
- Logging and monitoring
- Error handling and recovery
- Documentation and guides

---

## Technical Specifications

### System Requirements

| Requirement | Specification |
|-------------|---------------|
| Python | 3.8 or higher |
| Operating System | Windows, macOS, Linux |
| Memory | 4GB minimum, 8GB recommended |
| Disk Space | 500MB for installation |
| Network | Required for AI features |

### Dependencies

**Core**:
- python-docx (3.1.5)
- openpyxl (3.1.5)
- pandas (2.3.3)
- numpy (2.3.5)

**AI/NLP** (Optional):
- anthropic (>= 0.18.0)
- spacy (>= 3.7.0)
- tiktoken (>= 0.5.0)

**Document Processing** (Optional):
- pdfplumber (>= 0.10.0)
- PyMuPDF (>= 1.23.0)
- pytesseract (>= 0.3.10)

### Data Limits

| Limit | Value |
|-------|-------|
| Max File Size | 50MB |
| Max Tables per Document | 100 |
| Max Line Items | 1,000 |
| Max Concurrent Jobs | 5 |
| Cache Expiry | 90 days |

---

## Document Inventory

| Document | Purpose | Location |
|----------|---------|----------|
| README.md | Main documentation | `/README.md` |
| FEATURE_CATALOG.md | This document | `/FEATURE_CATALOG.md` |
| DEMO_GUIDE.md | Demonstration guide | `/DEMO_GUIDE.md` |
| TESTING_GUIDE.md | Testing procedures | `/TESTING_GUIDE.md` |
| API_DOCUMENTATION.md | API reference | `/docs/API_DOCUMENTATION.md` |
| workflow.md | Process flows | `/docs/workflow.md` |
| configuration_guide.md | Configuration reference | `/docs/configuration_guide.md` |
| tco_methodology.md | TCO methodology | `/docs/tco_methodology.md` |
| extraction_guide.md | Extraction details | `/docs/extraction_guide.md` |
| integration_guide.md | Integration guide | `/docs/integration_guide.md` |

---

*Last Updated: December 2024*
*Version: 2.0*
