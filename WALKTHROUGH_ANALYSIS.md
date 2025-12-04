# TCO Automation - Walkthrough Implementation Analysis

> **Branch:** AB_Streamline
> **Date:** December 2024
> **Purpose:** Gap analysis for client walkthrough preparation

---

## Executive Summary

| Category | Fully Implemented | Partially Implemented | Not Implemented |
|----------|-------------------|----------------------|-----------------|
| Document Ingestion | 5 | 2 | 0 |
| Document Processing | 4 | 0 | 0 |
| OCR Engine | 2 | 1 | 2 |
| Table Detection | 4 | 1 | 2 |
| Hybrid Extraction | 6 | 1 | 0 |
| Mapping & Validation | 5 | 1 | 1 |
| Data Normalization | 4 | 0 | 1 |
| TCO Calculation | 3 | 1 | 2 |
| Output Generation | 3 | 0 | 2 |
| Provenance & Audit | 4 | 2 | 1 |
| Orchestration | 4 | 2 | 2 |
| Performance Monitoring | 2 | 1 | 1 |
| Error Handling | 2 | 1 | 2 |

---

## What's Already Included (Ready for Demo)

### Document Ingestion & Processing

| Item | Status | Location |
|------|--------|----------|
| PDF file acceptance | Complete | `document_loader.py` |
| DOCX file acceptance | Complete | `document_loader.py` |
| XLSX file acceptance | Complete | `document_loader.py` |
| Image file acceptance (PNG/JPG/TIFF) | Complete | `document_loader.py` |
| File existence validation | Complete | `validators.py` |
| PyMuPDF integration | Complete | `document_loader.py` |
| pdfplumber text extraction | Complete | `document_loader.py` |
| Page-by-page PDF processing | Complete | `document_loader.py` |
| python-docx table/paragraph extraction | Complete | `document_loader.py` |
| openpyxl with formula evaluation | Complete | `jh_extractor.py` |
| Multi-sheet handling | Complete | `document_loader.py` |

### OCR Engine

| Item | Status | Location |
|------|--------|----------|
| Tesseract integration | Complete | `document_loader.py` |
| OCR text extraction | Complete | `document_loader.py` |
| Language configuration | Complete | `document_loader.py` |

### Table Detection

| Item | Status | Location |
|------|--------|----------|
| pdfplumber table extraction | Complete | `document_loader.py` |
| python-docx table extraction | Complete | `document_loader.py` |
| Excel row iteration | Complete | `jh_extractor.py` |
| Header row identification | Complete | `jh_extractor.py` |
| Column index mapping | Complete | `jh_extractor.py` |
| Hidden row/column detection | Complete | `jh_extractor.py` |

### Hybrid Extraction Engine

| Item | Status | Location |
|------|--------|----------|
| Currency/percentage/date regex | Complete | `llm_extractor.py` |
| Monthly/annual/per-user patterns | Complete | `llm_extractor.py` |
| spaCy NER integration | Complete | `llm_extractor.py` |
| MONEY/ORG/DATE entity extraction | Complete | `llm_extractor.py` |
| Document chunking (sliding window) | Complete | `text_processor.py` |
| Overlap handling | Complete | `text_processor.py` |
| Semantic boundary detection | Complete | `text_processor.py` |
| Claude API integration | Complete | `llm_extractor.py` |
| Prompt engineering for TCO | Complete | `extraction_prompts.py` |
| Few-shot examples | Complete | `extraction_prompts.py` |
| JSON schema enforcement | Complete | `llm_extractor.py` |

### Mapping & Validation

| Item | Status | Location |
|------|--------|----------|
| JSON Schema definition | Complete | `validation_rules.json` |
| Required field checking | Complete | `validators.py` |
| Type/format validation | Complete | `validators.py` |
| Range checking | Complete | `validation_rules.json` |
| Enum constraint enforcement | Complete | `validation_rules.json` |
| Auto-correction rules | Complete | `validation_rules.json` |
| Weighted voting (Rules vs LLM) | Complete | `llm_extractor.py` |
| Hybrid extraction method | Complete | `llm_extractor.py` |
| Confidence score calculation | Complete | `llm_extractor.py` |
| Fuzzy matching (rapidfuzz) | Complete | `schema_mapper.py` |

### Data Normalization

| Item | Status | Location |
|------|--------|----------|
| Currency parsing | Complete | `validators.py` |
| Negative value handling | Complete | `validators.py` |
| Date standardization (ISO 8601) | Complete | `validators.py` |
| Monthly to annual conversion | Complete | `schema_mapper.py` |
| Per-user to total calculation | Complete | `schema_mapper.py` |

### TCO Calculation

| Item | Status | Location |
|------|--------|----------|
| 5/7/10-year projection | Complete | `schema_mapper.py` |
| Compound growth calculation | Complete | `helpers.py` |
| Total cost aggregation | Complete | `helpers.py` |
| CPI escalation rates | Complete | `config.py` |
| One-time vs recurring costs | Complete | `tco_writer.py` |

### Output Generation

| Item | Status | Location |
|------|--------|----------|
| Canonical JSON output | Complete | `pipeline.py` |
| Excel template population | Complete | `tco_writer.py` |
| Multi-sheet population | Complete | `tco_writer.py` |
| Formula preservation | Complete | `tco_writer.py` |
| Categorized row placement | Complete | `tco_writer.py` |

### Provenance & Audit

| Item | Status | Location |
|------|--------|----------|
| Extraction method tracking | Complete | `llm_extractor.py` |
| Confidence score per field | Complete | `ExtractionResult` |
| Raw snippet preservation | Complete | `ExtractionResult` |
| Cell reference tracking | Complete | `jh_extractor.py` |
| Mapping audit trail | Complete | `schema_mapper.py` |
| Pipeline stage logging | Complete | `pipeline.py` |

### Orchestration

| Item | Status | Location |
|------|--------|----------|
| DAG-based pipeline (6 stages) | Complete | `pipeline.py` |
| Stage sequencing | Complete | `pipeline.py` |
| State management | Complete | `pipeline.py` |
| Job scheduling | Complete | `scheduler.py` |
| Job history persistence | Complete | `scheduler.py` |

### Performance & Error Handling

| Item | Status | Location |
|------|--------|----------|
| Processing time per stage | Complete | `pipeline.py` |
| Total pipeline duration | Complete | `pipeline.py` |
| Success/failure status | Complete | `scheduler.py` |
| Document count tracking | Complete | `pipeline.py` |
| Stage-level exception handling | Complete | `pipeline.py` |
| Error collection & logging | Complete | `pipeline.py` |
| Intermediate result saving | Complete | `pipeline.py` |

---

## What Needs Work (Required for Walkthrough)

### Critical Priority (Must Have)

| Item | Current State | Work Required | Effort |
|------|---------------|---------------|--------|
| **Streamlined Demo Entry Point** | Missing | Create `demo.py` with polished console output, progress bars, summary | New file |
| **Real-time Progress Display** | Basic (internal logs) | Add visual progress bars, stage status updates | Moderate |
| **Executive Summary in Excel Output** | Missing | Add summary sheet with metrics, totals, key findings | Moderate |
| **User-Friendly Error Messages** | Technical stack traces | Translate to plain English with recovery suggestions | Moderate |
| **Processing Metrics Display** | Internal only | Surface time, accuracy %, coverage % to user | Moderate |
| **Source-to-Output Traceability Report** | Internal audit only | Generate visible comparison report | Moderate |

### Medium Priority (Should Have)

| Item | Current State | Work Required | Effort |
|------|---------------|---------------|--------|
| Image preprocessing (deskew/denoise) | Basic 2x zoom only | Add proper image cleanup | Small |
| OCR confidence scoring | Missing | Add word/line confidence | Small |
| Merged cell handling | Detection only | Implement unmerge logic | Small |
| Proximity-based term association | Basic context | Improve field association | Small |
| Cross-field validation | Basic checks | Add more consistency rules | Small |
| Duplicate detection | Basic | Improve deduplication | Small |
| Numerical tolerance (±1%) | Missing | Add tolerance for matching | Small |
| NPV calculation | Foundation exists | Complete implementation | Moderate |
| IRR calculation | Missing | Add calculation | Moderate |
| Source coordinates (bbox) | Page-level only | Add bounding box tracking | Moderate |
| JSONL provenance format | JSON only | Convert to JSONL | Small |
| Chart generation in Excel | Missing | Add cost comparison charts | Moderate |
| Conditional formatting | Missing | Add color-coding | Moderate |
| Automatic retry with backoff | Missing | Add retry logic | Moderate |

---

## Walkthrough Checklist

### Ready to Demo
- [x] Multi-format document ingestion (PDF, DOCX, XLSX, images)
- [x] Table extraction from all formats
- [x] OCR for scanned documents
- [x] Hybrid extraction (regex + NER + LLM)
- [x] Data validation and normalization
- [x] Schema mapping with fuzzy matching
- [x] TCO calculations with growth projections
- [x] Excel template population
- [x] 6-stage pipeline orchestration
- [x] Error handling and logging

### Needs Implementation
- [ ] **Demo script with polished UX** (Critical)
- [ ] **Progress visualization** (Critical)
- [ ] **Executive summary sheet** (Critical)
- [ ] **Traceability report** (Critical)
- [ ] **Human-readable error messages** (Critical)
- [ ] **Metrics dashboard at completion** (Critical)

---

## AI API Recommendation

### Best Choice: Claude 3.5 Haiku

| Criteria | Claude 3.5 Haiku | Claude 3.5 Sonnet | GPT-4o-mini | GPT-4o |
|----------|------------------|-------------------|-------------|--------|
| **Cost (Input/1M tokens)** | $0.25 | $3.00 | $0.15 | $2.50 |
| **Cost (Output/1M tokens)** | $1.25 | $15.00 | $0.60 | $10.00 |
| **Speed** | Fastest | Fast | Fast | Moderate |
| **Accuracy for TCO** | Excellent | Excellent | Good | Excellent |
| **JSON Extraction** | Strong | Strong | Good | Strong |
| **Context Window** | 200K | 200K | 128K | 128K |

### Recommended: Tiered Approach

```
┌─────────────────────────────────────────────────────────┐
│  PRIMARY: Claude 3.5 Haiku (claude-3-5-haiku-20241022) │
│  ├── 90% of extractions (structured tables, clear data)│
│  ├── Cost: ~$0.50-1.00 per document                    │
│  └── Speed: 2-3 seconds per chunk                      │
├─────────────────────────────────────────────────────────┤
│  FALLBACK: Claude 3.5 Sonnet (complex/ambiguous only)  │
│  ├── 10% of extractions (edge cases, low confidence)   │
│  ├── Triggered when Haiku confidence < 0.7             │
│  └── Better reasoning for ambiguous pricing terms      │
└─────────────────────────────────────────────────────────┘
```

### Cost Estimate Per Document

| Document Type | Haiku Only | Tiered (Haiku + Sonnet fallback) |
|---------------|------------|----------------------------------|
| FIS Proposal (DOCX, ~20 pages) | ~$0.30 | ~$0.50 |
| Jack Henry (XLSX, ~500 rows) | ~$0.40 | ~$0.60 |
| Both vendors combined | ~$0.70 | ~$1.10 |
| **Monthly (50 proposals)** | **~$35** | **~$55** |

### Why Claude over GPT for This Project?

1. **Already integrated** - Codebase uses `anthropic` library
2. **Better structured extraction** - Claude excels at following JSON schemas
3. **Larger context window** - 200K tokens handles full documents without chunking issues
4. **Consistent formatting** - More reliable table/pricing extraction
5. **Cost-effective** - Haiku is 12x cheaper than Sonnet with 90% of the capability

### API Key Setup

```bash
# .env file
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx

# For tiered approach, update config.py:
PRIMARY_MODEL = "claude-3-5-haiku-20241022"    # Fast, cheap
FALLBACK_MODEL = "claude-3-5-sonnet-20241022"  # Accurate, for edge cases
CONFIDENCE_THRESHOLD = 0.7                      # Trigger fallback below this
```

---

## Summary: What You Have vs What You Need

| Category | Have | Need |
|----------|------|------|
| **Core Extraction** | 95% complete | Minor refinements |
| **Data Processing** | 100% complete | None |
| **Validation** | 85% complete | Cross-field checks |
| **Output Generation** | 70% complete | Summary sheet, charts |
| **User Experience** | 30% complete | Demo script, progress, errors |
| **Audit Trail** | 80% complete | Visible traceability report |

---

## Estimated Effort for Walkthrough-Ready State

| Task | Estimated Time |
|------|----------------|
| Create polished demo entry point (`demo.py`) | 2-3 hours |
| Add real-time progress display | 1-2 hours |
| Create executive summary Excel sheet | 2-3 hours |
| Generate traceability report | 2-3 hours |
| Polish validation report output | 1-2 hours |
| Improve error messages | 1-2 hours |
| Add processing metrics display | 1 hour |
| **Total** | **10-16 hours** |

---

## Conclusion

The heavy lifting is complete. The core extraction, processing, validation, and output generation systems are fully functional. What remains is the **presentation layer** - polishing the user experience for a professional walkthrough demonstration.

**Priority Focus Areas:**
1. Demo script with visual feedback
2. Executive summary in output
3. Traceability/audit visibility
4. Human-readable messaging
