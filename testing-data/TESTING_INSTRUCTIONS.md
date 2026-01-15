# TCO Extraction Pipeline Testing Instructions

This guide explains how to test the TCO automation platform with sample proposals using the existing extraction pipeline.

## Prerequisites

### 1. Environment Setup
```bash
# Navigate to project directory
cd /path/to/tco_automation

# Activate virtual environment (if using)
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Verify dependencies
pip install -r requirements.txt
```

### 2. API Key Configuration
```bash
# Set Anthropic API key for AI extraction
export ANTHROPIC_API_KEY="your-api-key-here"

# Or on Windows:
set ANTHROPIC_API_KEY=your-api-key-here
```

### 3. Verify Template Files
Ensure TCO templates are available:
- `WORKBOOK1.xlsx` - Standard TCO template
- `WORKBOOK2.xlsx` - Enhanced TCO template
- `Templates/New_TCO_Excel_v1.xlsx` - Alternative template

---

## Running Single Proposal Extractions

### FIS Proposals (Word Documents)

```bash
# Basic FIS extraction
python main.py --fis testing-data/dummy-proposals/fis-like/proposal.docx \
               --template WORKBOOK1.xlsx \
               --output testing-data/extraction-results/fis_test_output.xlsx

# With specific contract term
python main.py --fis testing-data/dummy-proposals/fis-like/proposal.docx \
               --template WORKBOOK1.xlsx \
               --output testing-data/extraction-results/fis_7year.xlsx \
               --fis-term 7_year
```

**FIS Term Options:** `5_year`, `7_year`, `10_year`

### Jack Henry Proposals (Excel Files)

```bash
# Basic Jack Henry extraction
python main.py --jh testing-data/dummy-proposals/jack-henry-like/proposal.xlsx \
               --template WORKBOOK1.xlsx \
               --output testing-data/extraction-results/jh_test_output.xlsx

# With specific scenario
python main.py --jh testing-data/dummy-proposals/jack-henry-like/proposal.xlsx \
               --template WORKBOOK1.xlsx \
               --output testing-data/extraction-results/jh_scenario2.xlsx \
               --jh-scenario Proposal_2
```

**JH Scenario Options:** `Proposal_1`, `Proposal_2`, `Proposal_3`

### Multi-Vendor Comparison

```bash
# Side-by-side FIS and Jack Henry
python main.py --fis testing-data/dummy-proposals/fis-like/proposal.docx \
               --jh testing-data/dummy-proposals/jack-henry-like/proposal.xlsx \
               --template WORKBOOK1.xlsx \
               --output testing-data/extraction-results/comparison.xlsx
```

---

## Using the AI Pipeline Directly

For more control and detailed metrics, use the AI pipeline module:

### Python Script Method

```python
import os
import sys
sys.path.insert(0, '.')

from extraction.ai_pipeline import AIPipeline

# Initialize pipeline
pipeline = AIPipeline(
    api_key=os.environ.get('ANTHROPIC_API_KEY'),
    contract_term=7,
    annual_increase=0.03
)

# Process a document
result = pipeline.process_document(
    document_path='testing-data/dummy-proposals/fis-like/proposal.pdf',
    output_excel='testing-data/extraction-results/ai_output.xlsx',
    save_audit=True
)

# Check results
print(f"Success: {result.success}")
print(f"Items extracted: {len(result.extraction_result.line_items)}")
print(f"Confidence: {result.extraction_result.overall_confidence:.1%}")
print(f"Processing time: {result.processing_time_seconds:.1f}s")
print(f"QA Bucket: {result.qa_result.bucket.value}")
```

### Interactive Testing (Python REPL)

```python
>>> from extraction.ai_pipeline import AIPipeline
>>> pipeline = AIPipeline()
>>> result = pipeline.process_document('path/to/proposal.pdf')
>>> result.summary
```

---

## Batch Testing Multiple Proposals

### Shell Script Method (Linux/Mac)

Create a batch test script:

```bash
#!/bin/bash
# batch_test.sh

PROPOSALS_DIR="testing-data/dummy-proposals"
OUTPUT_DIR="testing-data/extraction-results"
TEMPLATE="WORKBOOK1.xlsx"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Process FIS proposals
for file in "$PROPOSALS_DIR/fis-like"/*.docx; do
    if [ -f "$file" ]; then
        filename=$(basename "$file" .docx)
        echo "Processing: $file"
        python main.py --fis "$file" \
                       --template "$TEMPLATE" \
                       --output "$OUTPUT_DIR/${filename}_output.xlsx"
    fi
done

# Process Jack Henry proposals
for file in "$PROPOSALS_DIR/jack-henry-like"/*.xlsx; do
    if [ -f "$file" ]; then
        filename=$(basename "$file" .xlsx)
        echo "Processing: $file"
        python main.py --jh "$file" \
                       --template "$TEMPLATE" \
                       --output "$OUTPUT_DIR/${filename}_output.xlsx"
    fi
done

echo "Batch processing complete!"
```

### Windows Batch Method

```batch
@echo off
REM batch_test.bat

set PROPOSALS_DIR=testing-data\dummy-proposals
set OUTPUT_DIR=testing-data\extraction-results
set TEMPLATE=WORKBOOK1.xlsx

mkdir %OUTPUT_DIR% 2>nul

REM Process FIS proposals
for %%f in (%PROPOSALS_DIR%\fis-like\*.docx) do (
    echo Processing: %%f
    python main.py --fis "%%f" --template %TEMPLATE% --output "%OUTPUT_DIR%\%%~nf_output.xlsx"
)

REM Process Jack Henry proposals
for %%f in (%PROPOSALS_DIR%\jack-henry-like\*.xlsx) do (
    echo Processing: %%f
    python main.py --jh "%%f" --template %TEMPLATE% --output "%OUTPUT_DIR%\%%~nf_output.xlsx"
)

echo Batch processing complete!
```

---

## Validating Extraction Results

### Manual Validation Steps

1. **Open Source Document:** View the original proposal
2. **Open Output Excel:** View the extracted TCO file
3. **Compare Key Fields:**
   - Solution/product names
   - Monthly fees
   - One-time fees
   - Categories (Bundle, Non-Bundle, etc.)

### Validation Checklist Per Document

```
Document: [filename]
Date Tested: [date]

PRE-EXTRACTION:
[ ] Document readable (not corrupted)
[ ] Document contains pricing data
[ ] Page count: _____

EXTRACTION METRICS:
[ ] Processing time: _____ seconds (target: <120s)
[ ] Items extracted: _____
[ ] Overall confidence: _____% (target: >=90%)

QA RESULTS:
[ ] QA Bucket: [Auto-Accept / Quick-Review / Manual-Entry]
[ ] Items passed: _____
[ ] Items flagged: _____
[ ] Items failed: _____

ACCURACY CHECK (sample 5-10 items):
[ ] Item 1: [name] - Price correct? [Y/N]
[ ] Item 2: [name] - Price correct? [Y/N]
[ ] Item 3: [name] - Price correct? [Y/N]
[ ] Item 4: [name] - Price correct? [Y/N]
[ ] Item 5: [name] - Price correct? [Y/N]

Estimated accuracy: _____/%

ISSUES/NOTES:
_________________________________
```

---

## Analyzing Extraction JSON

When `save_audit=True`, the pipeline creates JSON audit files:

```python
import json

# Load audit file
with open('audit_20251215_120000.json') as f:
    audit = json.load(f)

# Examine extraction details
print(f"Document: {audit['document']}")
print(f"Items: {audit['extraction']['line_items_count']}")
print(f"Confidence: {audit['extraction']['overall_confidence']}")

# Check QA results
qa = audit['qa']
print(f"QA Passed: {qa['passed']}")
print(f"Routing: {qa['bucket']}")

# List any failed checks
for check in qa['checks']:
    if check['status'] == 'failed':
        print(f"  FAILED: {check['check_name']} - {check['message']}")
```

---

## Success Criteria

### Per-Document Thresholds

| Metric | Target | Acceptable |
|--------|--------|------------|
| Processing Time | <60s | <120s |
| Overall Confidence | >=95% | >=90% |
| Items Extracted | >0 | >0 |
| QA Bucket | Auto-Accept | Quick-Review |

### Batch Validation Thresholds

| Metric | Target |
|--------|--------|
| Document Success Rate | >=90% |
| Average Confidence | >=90% |
| Zero Crashes | Required |
| Average Processing Time | <120s |

---

## Troubleshooting

### Common Issues

**1. "No line items extracted"**
- Check document format (PDF/DOCX/XLSX)
- Verify document contains pricing tables
- Try rule-based extractor fallback

**2. "API key not found"**
- Set `ANTHROPIC_API_KEY` environment variable
- Or pass directly to AIPipeline constructor

**3. "Processing timeout"**
- Document may be too large
- Try splitting into smaller sections
- Check network connectivity

**4. Low confidence scores**
- Document format may be unusual
- Manual review may be required
- Check for scanned images (need OCR)

**5. "Template not found"**
- Verify template path is correct
- Check file permissions

### Debug Mode

Enable debug logging for more details:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Then run extraction
result = pipeline.process_document(...)
```

---

## Recording Test Results

After testing, record results in `validation-reports/`:

1. **Create test summary:** `test_run_[date].md`
2. **Save extraction outputs:** `extraction-results/`
3. **Document any issues:** Note edge cases, failures, improvements needed

See `VALIDATION_REPORT_TEMPLATE.md` for the recommended format.
