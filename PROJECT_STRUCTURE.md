# TCO Automation - Project Structure

**Last Updated:** 2026-01-13
**Purpose:** Complete guide to the reorganized project structure

---

## 📁 Project Organization

```
tco_automation/
│
├── 📄 main.py                          # Main entry point
├── 📄 requirements.txt                 # Python dependencies
├── 📄 verify_install.py                # Installation verification
├── 📄 .env.example                     # Environment variables template
├── 📄 .gitignore                       # Git ignore rules
│
├── 📂 analysis/                        # Data analysis scripts
│   ├── analyze_fis_line_items.py       # FIS line item analysis
│   ├── analyze_vendor_data_structures.py # Vendor data structure analysis
│   ├── analyze_workbook2.py            # WORKBOOK2 analysis
│   ├── analyze_workbook2_full_structure.py # Complete WORKBOOK2 structure
│   ├── compare_extractions.py          # Compare different extractions
│   ├── compare_fis_extractions.py      # FIS-specific comparison
│   └── read_workbook2_raw.py           # Raw WORKBOOK2 data reader
│
├── 📂 config/                          # Configuration files
│   ├── __init__.py
│   ├── config.py                       # Main configuration
│   ├── extraction_config.py            # Extraction-specific config
│   ├── extraction_prompts.py           # AI extraction prompts
│   ├── validation_rules.json           # Validation rules
│   └── .env.example                    # Environment template
│
├── 📂 extraction/                      # Extraction pipeline
│   ├── __init__.py
│   ├── extract_proposal.py             # Main extraction script
│   ├── extract_proposal_direct.py      # Direct PDF extraction
│   ├── extract_proposal_hybrid.py      # Hybrid extraction method
│   ├── ai_pipeline.py                  # AI extraction pipeline
│   ├── bucket_router.py                # Route to appropriate extractor
│   ├── intelligent_extractor.py        # Intelligent extraction logic
│   ├── quality_assurance.py            # QA for extractions
│   ├── review_reporter.py              # Generate extraction reports
│   └── vendor_cache.py                 # Cache vendor data
│
├── 📂 extractors/                      # Vendor-specific extractors
│   ├── __init__.py
│   ├── document_loader.py              # Load various document formats
│   ├── fis_extractor.py                # FIS-specific extraction
│   ├── jh_extractor.py                 # Jack Henry extractor
│   └── llm_extractor.py                # LLM-based extraction
│
├── 📂 mappers/                         # Data mapping logic
│   ├── __init__.py
│   └── schema_mapper.py                # Schema transformation
│
├── 📂 orchestrator/                    # Workflow orchestration
│   ├── __init__.py
│   ├── pipeline.py                     # Pipeline orchestration
│   └── scheduler.py                    # Job scheduling
│
├── 📂 preprocessors/                   # Data preprocessing
│   ├── __init__.py
│   └── text_processor.py               # Text processing utilities
│
├── 📂 writers/                         # Output writers
│   ├── __init__.py
│   └── tco_writer.py                   # Write TCO Excel files
│
├── 📂 utils/                           # Utility functions
│   ├── __init__.py
│   ├── helpers.py                      # Helper functions
│   ├── logging_config.py               # Logging configuration
│   └── validators.py                   # Validation utilities
│
├── 📂 scripts/                         # Standalone scripts
│   ├── create_excel_template.py        # Create Excel templates
│   ├── create_multi_vendor_comparison.py # Multi-vendor comparison
│   ├── create_standardized_vendor_output.py # Standardized output generator
│   ├── create_vendor_extract.py        # Vendor extract generator
│   ├── generate_all_standardized_outputs.py # Batch generator
│   ├── json_to_excel_mapper.py         # JSON to Excel mapping
│   ├── json_to_workbook2_mapper.py     # JSON to WORKBOOK2 mapping
│   └── populate_tco_workbook.py        # Populate TCO workbook
│
├── 📂 tools/                           # Utility tools
│   ├── converters/                     # Conversion tools
│   │   ├── json_to_excel_mapping.py    # JSON to Excel converter
│   │   └── preview_excel.py            # Excel preview tool
│   └── validators/                     # Validation tools
│       ├── cell_validator.py           # Cell-level validation
│       ├── qa_validator.py             # Quality assurance validator
│       └── qa_comparison.py            # QA comparison tool
│
├── 📂 reports/                         # Report generation
│   ├── create_csi_report.py            # CSI-specific reports
│   ├── generate_word_report.py         # Generate Word reports
│   ├── convert_to_word.py              # Convert to Word format
│   └── reporting.py                    # General reporting utilities
│
├── 📂 tests/                           # Test suites
│   └── test_mapping.py                 # Mapping tests
│
├── 📂 data/                            # All data files
│   ├── proposals/                      # Proposal documents
│   │   ├── Proposal/                   # Main proposal folder
│   │   └── Extracted JSON/             # Extracted JSON data
│   ├── outputs/                        # Generated outputs
│   │   ├── TCO Output/                 # TCO Excel outputs
│   │   └── Vendor Extracts/            # Vendor-specific extracts
│   ├── templates/                      # Template files
│   │   ├── Templates/                  # Excel templates
│   │   ├── WORKBOOK1.xlsx              # Template workbook 1
│   │   ├── WORKBOOK2.xlsx              # Template workbook 2
│   │   ├── workbook2_complete_structure.json
│   │   ├── workbook2_fis_items.json
│   │   └── universal_schema.json       # Universal schema definition
│   ├── dictionaries/                   # Data dictionaries
│   │   └── Data_Dictionary/            # Complete data dictionary
│   ├── mappings/                       # Mapping definitions
│   │   └── Mappings/                   # JSON to Excel mappings
│   └── validation/                     # Validation data
│       └── Accuracy/                   # Accuracy reports and samples
│
├── 📂 documentation/                   # All documentation
│   ├── guides/                         # User guides
│   │   ├── EXTRACTION_METHODS_GUIDE.md
│   │   ├── EXTRACTION_RULES.md
│   │   ├── DEMO_GUIDE.md
│   │   ├── DEMO_CHEAT_SHEET.md
│   │   ├── QUICK_START_NEW_EXTRACTION.md
│   │   ├── TESTING_GUIDE.md
│   │   ├── API_DOCUMENTATION.md
│   │   ├── configuration_guide.md
│   │   ├── extraction_guide.md
│   │   ├── integration_guide.md
│   │   ├── tco_methodology.md
│   │   └── workflow.md
│   ├── reference/                      # Reference documentation
│   │   ├── STANDARDIZED_OUTPUT_GUIDE.md
│   │   ├── STANDARDIZED_FORMAT_SUMMARY.md
│   │   ├── WORKBOOK2_STRUCTURE_GUIDE.md
│   │   ├── FIS_EXTRACTION_GAP_ANALYSIS.md
│   │   └── SOLUTION_SUMMARY.md
│   └── project/                        # Project documentation
│       ├── DELIVERABLES_CHECKLIST.md
│       ├── FEATURE_CATALOG.md
│       ├── FEATURE_SUMMARY.md
│       ├── FUTURE_ENHANCEMENTS.md
│       ├── PROJECT_STATUS.md
│       ├── PRODUCTION_RUN_SUMMARY.md
│       ├── PITCH_AND_VALUE_PROPOSITION.md
│       ├── AI_Strategy_Enterprise_Scale.md
│       ├── TCO_Automation_Solution_Report_2025.md
│       ├── TCO_DATA_DICTIONARY.md
│       ├── TCO_Detailed_Project_Plan.md
│       ├── TCO_Quick_Implementation_Plan.md
│       ├── TCO_Automation_Architecture_Report_v2.docx
│       ├── TCO_Automation_Solution_Report_2025.docx
│       ├── TCO_Detailed_Project_Plan.docx
│       └── TCO_Quick_Implementation_Plan.docx
│
├── 📂 archive/                         # Archived/deprecated files
│   ├── ai_review_report.docx           # Old AI review reports
│   ├── ai_review_report_20251203_182609.docx
│   ├── audit_trail.json                # Old audit trails
│   ├── extraction_result.json          # Old extraction results
│   ├── sample_traceability_report.txt  # Sample reports
│   ├── karishma_docs/                  # Karishma's documents
│   ├── update_milestones.py            # Old update scripts
│   ├── update_milestones_compressed.py
│   ├── update_milestones_final.py
│   ├── update_sow.py
│   ├── update_sow_edge_cases.py
│   ├── update_work_packages.py
│   ├── run_pipeline.py                 # Old pipeline runners
│   ├── run_tco_pipeline.py
│   ├── tco_pipeline_v2.py
│   └── ai_tco_calculator.py            # Old calculator
│
└── 📂 logs/                            # Log files (gitignored)

```

---

## 🎯 Key Organizational Principles

### 1. **Separation of Concerns**
- **Source code** (extraction/, mappers/, etc.) separated from **data** and **documentation**
- **Active scripts** in main folders, **deprecated** in archive/
- **Configuration** centralized in config/

### 2. **Logical Grouping**
- **Analysis** - All analysis and comparison scripts
- **Extraction** - All extraction-related code
- **Reports** - Report generation scripts
- **Tools** - Utility tools (validators, converters)
- **Data** - All data files (proposals, outputs, templates)
- **Documentation** - All docs organized by type

### 3. **Clear Hierarchy**
- **Root** - Only essential files (main.py, README, requirements.txt)
- **First level** - Major functional areas
- **Second level** - Specific implementations

---

## 🚀 Quick Start Locations

### Running Extractions
```bash
# Main extraction script
python extraction/extract_proposal.py <pdf_file> <vendor>

# Direct PDF extraction
python extraction/extract_proposal_direct.py <pdf_file> <vendor>

# Hybrid extraction
python extraction/extract_proposal_hybrid.py <pdf_file> <vendor>
```

### Generating Standardized Outputs
```bash
# Single vendor
python scripts/create_standardized_vendor_output.py "Client" "Vendor" "file.json"

# All vendors (batch)
python scripts/generate_all_standardized_outputs.py

# Multi-vendor comparison
python scripts/create_multi_vendor_comparison.py "Client" "V1" "file1.json" "V2" "file2.json"
```

### Analysis
```bash
# Analyze WORKBOOK2
python analysis/analyze_workbook2.py

# Compare extractions
python analysis/compare_extractions.py

# Analyze vendor data structures
python analysis/analyze_vendor_data_structures.py
```

---

## 📖 Documentation Locations

### For Users
- **Getting Started:** documentation/guides/QUICK_START_NEW_EXTRACTION.md
- **Extraction Guide:** documentation/guides/EXTRACTION_METHODS_GUIDE.md
- **Demo Guide:** documentation/guides/DEMO_GUIDE.md

### For Developers
- **API Docs:** documentation/guides/API_DOCUMENTATION.md
- **Configuration:** documentation/guides/configuration_guide.md
- **Integration:** documentation/guides/integration_guide.md

### Reference
- **Standardized Output:** documentation/reference/STANDARDIZED_OUTPUT_GUIDE.md
- **WORKBOOK2 Structure:** documentation/reference/WORKBOOK2_STRUCTURE_GUIDE.md
- **Gap Analysis:** documentation/reference/FIS_EXTRACTION_GAP_ANALYSIS.md

---

## 💾 Data Locations

### Input Data
- **Proposals:** data/proposals/Proposal/
- **Raw PDFs:** data/proposals/Proposal/*.pdf
- **Extracted JSON:** data/proposals/Extracted JSON/

### Output Data
- **TCO Excel Files:** data/outputs/TCO Output/
- **Vendor Extracts:** data/outputs/Vendor Extracts/
- **Standardized Outputs:** data/outputs/TCO Output/*_Standardized_*.xlsx

### Templates & Schemas
- **Excel Templates:** data/templates/Templates/
- **WORKBOOK Templates:** data/templates/WORKBOOK*.xlsx
- **Schema Definitions:** data/templates/*.json

---

## 🔧 Configuration

### Environment Setup
1. Copy `.env.example` to `.env`
2. Add your Anthropic API key:
   ```
   ANTHROPIC_API_KEY=your_key_here
   ```

### Configuration Files
- **Main Config:** config/config.py
- **Extraction Config:** config/extraction_config.py
- **Prompts:** config/extraction_prompts.py
- **Validation Rules:** config/validation_rules.json

---

## 🗂️ Migration Notes

### What Moved Where

**Root → analysis/**
- All `analyze_*.py` files
- All `compare_*.py` files
- `read_workbook2_raw.py`

**Root → extraction/**
- `extract_proposal*.py` files

**Root → reports/**
- `create_csi_report.py`
- `generate_word_report.py`
- `convert_to_word.py`
- `reporting.py`

**Root → tools/**
- `validators/`: `cell_validator.py`, `qa_*.py`
- `converters/`: `json_to_excel_mapping.py`, `preview_excel.py`

**Root → data/**
- `Proposal/` → `data/proposals/Proposal/`
- `Extracted JSON/` → `data/proposals/Extracted JSON/`
- `TCO Output/` → `data/outputs/TCO Output/`
- `Templates/` → `data/templates/Templates/`
- `Data_Dictionary/` → `data/dictionaries/Data_Dictionary/`
- `Mappings/` → `data/mappings/Mappings/`

**Root → documentation/**
- All `.md` files (except README*, CONTRIBUTING, etc.)
- `docs/` merged into `documentation/guides/`

**Root → archive/**
- All `update_*.py` scripts
- Old pipeline scripts
- Old reports and documents

---

## 🎓 Best Practices

### Adding New Files

1. **New extraction method?** → `extraction/`
2. **New analysis script?** → `analysis/`
3. **New report generator?** → `reports/`
4. **New utility tool?** → `tools/validators/` or `tools/converters/`
5. **New documentation?** → `documentation/guides/` or `documentation/reference/`
6. **Old/deprecated code?** → `archive/`

### Naming Conventions

- **Scripts:** `verb_noun.py` (e.g., `extract_proposal.py`, `generate_report.py`)
- **Modules:** `noun.py` (e.g., `helpers.py`, `validators.py`)
- **Documentation:** `NOUN_DESCRIPTION.md` (e.g., `EXTRACTION_METHODS_GUIDE.md`)

---

## 📝 Notes

- **Logs** are in `logs/` (gitignored)
- **Virtual environment** is in `venv/` (gitignored)
- **Environment variables** in `.env` (gitignored)
- **Temp files** (`tmpclaude-*`) are gitignored

---

**Last Updated:** 2026-01-13
**Maintained By:** TCO Automation Team
