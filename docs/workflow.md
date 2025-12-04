# TCO Automation - Workflow Guide

**Step-by-Step Process Flows and Procedures**

---

## Table of Contents

- [Overview](#overview)
- [End-to-End Workflow](#end-to-end-workflow)
- [Workflow 1: Single Vendor Processing](#workflow-1-single-vendor-processing)
- [Workflow 2: Side-by-Side Comparison](#workflow-2-side-by-side-comparison)
- [Workflow 3: AI-Powered Extraction](#workflow-3-ai-powered-extraction)
- [Workflow 4: Batch Processing](#workflow-4-batch-processing)
- [Workflow 5: Scheduled Automation](#workflow-5-scheduled-automation)
- [Quality Assurance Workflow](#quality-assurance-workflow)
- [Troubleshooting Workflow](#troubleshooting-workflow)

---

## Overview

This guide provides detailed step-by-step procedures for all common workflows in the TCO Automation System. Each workflow includes prerequisites, steps, expected outcomes, and troubleshooting tips.

### Workflow Summary

| Workflow | Purpose | Estimated Time |
|----------|---------|----------------|
| Single Vendor Processing | Process one vendor proposal | 30 seconds |
| Side-by-Side Comparison | Compare two vendors | 1 minute |
| AI-Powered Extraction | Use Claude for complex docs | 2-3 minutes |
| Batch Processing | Process multiple files | 5-10 minutes |
| Scheduled Automation | Automated recurring jobs | Setup: 10 min |

---

## End-to-End Workflow

### High-Level Process Flow

```
┌─────────────────┐
│  Vendor Proposal │
│  (DOCX/XLSX)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Document Loader  │ ◄── Parse document structure
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Text Processor   │ ◄── Clean and chunk text
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Data Extractor   │ ◄── Extract pricing data
│ (Rule/AI-based)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Quality Assurance│ ◄── Validate and score
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Schema Mapper    │ ◄── Normalize to TCO format
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ TCO Writer       │ ◄── Populate Excel template
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  TCO Excel +     │
│  Audit Trail     │
└─────────────────┘
```

---

## Workflow 1: Single Vendor Processing

### Purpose
Process a single vendor proposal (FIS or Jack Henry) into a TCO template.

### Prerequisites
- [ ] Python environment activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Vendor proposal file available
- [ ] TCO template file available

### Steps

#### Step 1: Verify Input Files

```bash
# Check that files exist
ls data/your_proposal.docx
ls data/TCO_Template.xlsx
```

#### Step 2: Run Extraction

**For FIS Proposal:**
```bash
python main.py \
  --fis data/Echelon_FIS_Proposal.docx \
  --template data/TCO_Template.xlsx \
  --output output/FIS_TCO.xlsx \
  --fis-term 7_year
```

**For Jack Henry Proposal:**
```bash
python main.py \
  --jh data/JH_Deal_Sheet.xlsx \
  --template data/TCO_Template.xlsx \
  --output output/JH_TCO.xlsx \
  --jh-scenario Proposal_1
```

#### Step 3: Review Console Output

Expected output:
```
Starting TCO extraction...
Loading document: data/Echelon_FIS_Proposal.docx
Extracting FIS data...
  - Found 15 bundle items
  - Found 23 non-bundle items
  - Found 5 one-time fees
Normalizing data to TCO schema...
Writing to Excel template...
  - Populated 43 line items
  - FIS columns B-Y
Output saved: output/FIS_TCO.xlsx
Processing complete in 12.3 seconds
```

#### Step 4: Verify Output

1. Open `output/FIS_TCO.xlsx`
2. Navigate to "Line Items" sheet
3. Verify:
   - Column B contains fee types
   - Column O contains solution names
   - Columns S-Y contain costs by year
   - Categories are correctly assigned

#### Step 5: Spot-Check Accuracy

Compare 5-10 random items:
- Match solution names to source document
- Verify monthly fees are correct
- Check annual = monthly × 12
- Confirm category assignments

### Expected Outcome
- Excel file with populated Line Items sheet
- All vendor fees categorized and assigned
- Multi-year costs calculated

### Troubleshooting

| Issue | Solution |
|-------|----------|
| "File not found" | Verify file paths are correct |
| Empty output | Check source document format matches expected |
| Missing categories | Update `config.py` keyword mappings |

---

## Workflow 2: Side-by-Side Comparison

### Purpose
Process both FIS and Jack Henry proposals into a single TCO template for comparison.

### Prerequisites
- [ ] Both vendor proposals available
- [ ] TCO template with both vendor column sections

### Steps

#### Step 1: Prepare Files

```bash
# Verify all input files
ls data/FIS_Proposal.docx
ls data/JH_Deal_Sheet.xlsx
ls data/TCO_Template.xlsx
```

#### Step 2: Run Combined Extraction

```bash
python main.py \
  --fis data/FIS_Proposal.docx \
  --jh data/JH_Deal_Sheet.xlsx \
  --template data/TCO_Template.xlsx \
  --output output/TCO_Comparison.xlsx \
  --fis-term 7_year \
  --jh-scenario Proposal_1
```

#### Step 3: Review Output Structure

Open `output/TCO_Comparison.xlsx`:

| Section | Columns | Vendor |
|---------|---------|--------|
| Left | B-Y | FIS |
| Right | AO-BL | Jack Henry |

#### Step 4: Create Comparison Analysis

1. Sum total costs for each vendor
2. Compare by category:
   - Bundle costs
   - Non-bundle required costs
   - Non-bundle optional costs
   - One-time costs
3. Calculate 7-year TCO for each

#### Step 5: Generate Executive Summary

Create pivot table or summary with:
- Total Year 1 cost per vendor
- Total 7-year TCO per vendor
- Difference ($ and %)
- Top 10 cost items per vendor

### Expected Outcome
- Single Excel file with both vendors
- Side-by-side comparison capability
- Ready for financial analysis

---

## Workflow 3: AI-Powered Extraction

### Purpose
Use Claude AI for intelligent extraction with confidence scoring and validation.

### Prerequisites
- [ ] Anthropic API key configured
- [ ] Network connectivity
- [ ] Source document ready

### Steps

#### Step 1: Configure API Key

```bash
# Set environment variable
export ANTHROPIC_API_KEY="sk-ant-your-key-here"

# Or add to .env file
echo 'ANTHROPIC_API_KEY=sk-ant-your-key-here' >> .env
```

#### Step 2: Run Pipeline with AI

```bash
python run_pipeline.py data/proposal.docx \
  --vendor FIS \
  --term 7_year \
  -o data/output \
  --json \
  --verbose
```

#### Step 3: Review AI Extraction Results

Check JSON output for:
```json
{
  "overall_confidence": 0.94,
  "items_extracted": 43,
  "auto_accept_count": 38,
  "review_required_count": 5,
  "processing_time_seconds": 45.2
}
```

#### Step 4: Handle Bucket Routing

**Bucket 1 (Auto-Accept, >= 90%):**
- Items automatically populated to Excel
- No manual review needed

**Bucket 2 (Quick Review, 70-89%):**
- Review generated Word document
- Compare flagged items to source
- Accept or correct values

**Bucket 3 (Manual Entry, < 70%):**
- Use extracted data as reference
- Manually enter into template

#### Step 5: Complete Review Document

For Bucket 2 items:
1. Open `output/review_report.docx`
2. For each flagged item:
   - Verify source context
   - Accept suggested value OR
   - Enter correct value
3. Mark as reviewed

### Expected Outcome
- High-confidence items auto-populated
- Review document for manual validation
- Complete audit trail in JSON

---

## Workflow 4: Batch Processing

### Purpose
Process multiple proposal files in a single run.

### Prerequisites
- [ ] Multiple proposal files in a directory
- [ ] Consistent naming convention

### Steps

#### Step 1: Organize Input Files

```
data/proposals/
├── FIS_Client1.docx
├── FIS_Client2.docx
├── JH_Client1.xlsx
└── JH_Client2.xlsx
```

#### Step 2: Run Batch Processing

```bash
python run_pipeline.py data/proposals/ \
  -o data/output \
  --vendor auto \
  --json
```

#### Step 3: Monitor Progress

```
Processing batch: 4 files found
[1/4] FIS_Client1.docx ... done (12.3s)
[2/4] FIS_Client2.docx ... done (11.8s)
[3/4] JH_Client1.xlsx ... done (8.2s)
[4/4] JH_Client2.xlsx ... done (9.1s)

Batch complete: 4/4 successful
Total time: 41.4 seconds
```

#### Step 4: Review Batch Output

```
data/output/
├── FIS_Client1_TCO.xlsx
├── FIS_Client2_TCO.xlsx
├── JH_Client1_TCO.xlsx
├── JH_Client2_TCO.xlsx
└── batch_summary.json
```

#### Step 5: Check Batch Summary

```json
{
  "total_files": 4,
  "successful": 4,
  "failed": 0,
  "total_items_extracted": 172,
  "average_confidence": 0.91,
  "total_processing_time": 41.4
}
```

### Expected Outcome
- All files processed to separate outputs
- Batch summary with metrics
- Any errors isolated and logged

---

## Workflow 5: Scheduled Automation

### Purpose
Set up recurring automated processing jobs.

### Prerequisites
- [ ] Job configuration file
- [ ] Input directory structure
- [ ] Permissions for daemon operation

### Steps

#### Step 1: Create Job Configuration

Create `config/jobs.json`:
```json
{
  "jobs": [
    {
      "name": "daily_fis_processing",
      "schedule": "0 8 * * *",
      "input_directory": "data/incoming/fis/",
      "output_directory": "data/processed/fis/",
      "vendor": "FIS",
      "term": "7_year",
      "enabled": true
    },
    {
      "name": "weekly_jh_processing",
      "schedule": "0 9 * * 1",
      "input_directory": "data/incoming/jh/",
      "output_directory": "data/processed/jh/",
      "vendor": "Jack Henry",
      "scenario": "Proposal_1",
      "enabled": true
    }
  ]
}
```

#### Step 2: Test Job Configuration

```bash
# Run specific job manually
python run_pipeline.py --schedule config/jobs.json --run-job daily_fis_processing
```

#### Step 3: Start Scheduler Daemon

```bash
# Start in background
python run_pipeline.py --schedule config/jobs.json &

# Or with nohup for persistence
nohup python run_pipeline.py --schedule config/jobs.json > scheduler.log 2>&1 &
```

#### Step 4: Monitor Scheduled Jobs

```bash
# Check scheduler log
tail -f scheduler.log

# View job status
cat data/scheduler_status.json
```

#### Step 5: Manage Jobs

```bash
# Stop scheduler
pkill -f "run_pipeline.py --schedule"

# Update configuration
# Edit config/jobs.json, then restart scheduler
```

### Expected Outcome
- Automated processing at scheduled times
- Logs and status tracking
- Minimal manual intervention

---

## Quality Assurance Workflow

### Purpose
Validate extraction accuracy before delivery.

### Steps

#### Step 1: Run Cell Validation

```bash
python cell_validator.py \
  --source data/JH_Deal_Sheet.xlsx \
  --tco output/TCO_Result.xlsx \
  --scenario Proposal_1
```

#### Step 2: Review Validation Report

```
Cell Validation Report
======================
Total cells checked: 7,497
Matched: 7,420 (99.0%)
Mismatched: 52 (0.7%)
Missing in source: 25 (0.3%)

Top Mismatches:
- Row 45, Col S: Expected $12,500, Found $12,550
- Row 67, Col T: Expected $8,200, Found $8,000
```

#### Step 3: Investigate Mismatches

For each mismatch:
1. Check source document
2. Identify cause (rounding, formula, extraction error)
3. Correct if needed

#### Step 4: Run QA Validator

```bash
python qa_validator.py output/TCO_Result.xlsx
```

#### Step 5: Sign Off

- [ ] Coverage >= 98%
- [ ] Mismatches reviewed and acceptable
- [ ] Business rules passed
- [ ] Ready for delivery

---

## Troubleshooting Workflow

### Purpose
Diagnose and resolve extraction issues.

### Steps

#### Step 1: Enable Verbose Logging

```bash
python main.py ... --verbose 2>&1 | tee debug.log
```

#### Step 2: Run Individual Extractor

```bash
# Test FIS extractor alone
python -m extractors.fis_extractor data/proposal.docx

# Test Jack Henry extractor alone
python -m extractors.jh_extractor data/deal_sheet.xlsx
```

#### Step 3: Check Extraction Summary

Review console output for:
- Tables detected
- Items extracted per category
- Warnings or errors

#### Step 4: Validate Configuration

```bash
# Check config.py settings
python -c "import config; print(config.LINE_ITEM_START_ROWS)"
```

#### Step 5: Test Schema Mapping

```bash
python -m mappers.schema_mapper
```

#### Step 6: Document Issue

If unresolved:
1. Save debug.log
2. Note steps to reproduce
3. Capture error messages
4. Report issue with details

---

## Quick Reference

### Common Commands

```bash
# Single FIS extraction
python main.py --fis FILE --template TEMPLATE --output OUTPUT --fis-term 7_year

# Single JH extraction
python main.py --jh FILE --template TEMPLATE --output OUTPUT --jh-scenario Proposal_1

# Both vendors
python main.py --fis FIS_FILE --jh JH_FILE --template TEMPLATE --output OUTPUT

# Batch processing
python run_pipeline.py DIRECTORY -o OUTPUT --vendor auto

# Validation
python cell_validator.py --source SOURCE --tco TCO --scenario SCENARIO
```

### File Locations

| Purpose | Location |
|---------|----------|
| Input proposals | `data/` |
| TCO templates | `data/` |
| Output files | `output/` |
| Configuration | `config.py`, `config/` |
| Logs | `logs/` |

---

*Last Updated: December 2024*
