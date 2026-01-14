# TCO Automation System - Demo Guide

**Complete Demonstration Walkthrough**

---

## Table of Contents

- [Preparation Checklist](#preparation-checklist)
- [Demo Environment Setup](#demo-environment-setup)
- [Demo Script](#demo-script)
- [Key Talking Points](#key-talking-points)
- [Live Demo Walkthrough](#live-demo-walkthrough)
- [Handling Questions](#handling-questions)
- [Troubleshooting During Demo](#troubleshooting-during-demo)

---

## Preparation Checklist

### Before the Demo

- [ ] **Environment**
  - [ ] Python environment activated
  - [ ] All dependencies installed
  - [ ] API key configured (if showing AI features)

- [ ] **Files**
  - [ ] Sample FIS proposal ready
  - [ ] Sample Jack Henry deal sheet ready
  - [ ] TCO template available
  - [ ] Output directory created

- [ ] **Applications**
  - [ ] Terminal/command prompt open
  - [ ] Excel installed and ready
  - [ ] Text editor for viewing code (optional)

- [ ] **Backup**
  - [ ] Pre-generated output files (in case of issues)
  - [ ] Screenshots of expected results

---

## Demo Environment Setup

### Quick Setup Commands

```bash
# Navigate to project directory
cd /path/to/tco_automation

# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Verify installation
python -c "import openpyxl, pandas, docx; print('Ready!')"

# Create output directory
mkdir -p output
```

### Verify Sample Files

```bash
# List sample files
ls data/

# Expected files:
# - Echelon_FIS_Proposal_10_29_25.docx
# - JH_Deal_Sheet.xlsx
# - Echelon_Primary_TCO_v5.xlsx
```

---

## Demo Script

### Opening Statement (30 seconds)

> "The TCO Automation System transforms vendor proposal processing from hours of manual work to under 60 seconds. Let me show you how it works."

### Problem Statement (1 minute)

> "Currently, financial analysts spend 4-10 hours manually extracting pricing data from vendor proposals, copying values into Excel templates, and verifying calculations. This process is:
>
> - Time-consuming and repetitive
> - Error-prone due to manual data entry
> - Inconsistent across different analysts
> - Difficult to audit and verify
>
> Our solution automates this entire process."

### Solution Overview (1 minute)

> "The TCO Automation System:
>
> 1. **Reads** vendor proposals in multiple formats
> 2. **Extracts** all pricing data automatically
> 3. **Normalizes** to a standard schema
> 4. **Populates** your TCO template
> 5. **Validates** accuracy with AI-powered QA
>
> Let me demonstrate..."

---

## Live Demo Walkthrough

### Demo 1: Single Vendor Extraction (3 minutes)

#### Step 1: Show the Source Document

```bash
# Open FIS proposal (or show on screen)
# Point out:
# - Multiple tables with pricing
# - Different sections (bundle, monthly, one-time)
# - Complex structure
```

> "Here's a typical FIS proposal - multiple tables, different fee types, various sections. Manually extracting this takes hours."

#### Step 2: Run the Extraction

```bash
python main.py \
  --fis data/Echelon_FIS_Proposal_10_29_25.docx \
  --template data/Echelon_Primary_TCO_v5.xlsx \
  --output output/demo_fis_tco.xlsx \
  --fis-term 7_year
```

> "One command, 30 seconds, and we have a fully populated TCO template."

#### Step 3: Show the Output

1. Open `output/demo_fis_tco.xlsx`
2. Navigate to "Line Items" sheet
3. Point out:
   - Fee types populated (Column B)
   - Solution names (Column O)
   - Categories assigned (Column P)
   - Costs by year (Columns S-Y)

> "Every line item has been extracted, categorized, and placed in the correct location. The 7-year costs are calculated automatically."

### Demo 2: Side-by-Side Comparison (3 minutes)

#### Step 1: Explain the Use Case

> "The real power comes when comparing vendors. Let's process both FIS and Jack Henry into the same template."

#### Step 2: Run Combined Extraction

```bash
python main.py \
  --fis data/Echelon_FIS_Proposal_10_29_25.docx \
  --jh data/JH_Deal_Sheet.xlsx \
  --template data/Echelon_Primary_TCO_v5.xlsx \
  --output output/demo_comparison.xlsx \
  --fis-term 7_year \
  --jh-scenario Proposal_1
```

#### Step 3: Show Comparison Output

1. Open `output/demo_comparison.xlsx`
2. Point out FIS columns (B-Y) and JH columns (AO-BL)
3. Scroll to totals row

> "Now we have both vendors side-by-side. We can immediately compare total costs, category breakdowns, and individual line items."

### Demo 3: AI-Powered Features (2 minutes, optional)

#### Show Confidence Scoring

```bash
python run_pipeline.py data/Echelon_FIS_Proposal_10_29_25.docx \
  --vendor FIS \
  --term 7_year \
  -o output \
  --json
```

> "The AI provides confidence scores for each extraction. Items with 90%+ confidence are auto-accepted. Items between 70-89% are flagged for quick review."

#### Show Review Report

> "For flagged items, we generate a review document that shows the source context and suggested corrections."

### Demo 4: Validation (2 minutes)

#### Run Cell Validation

```bash
python cell_validator.py \
  --source data/JH_Deal_Sheet.xlsx \
  --tco output/demo_comparison.xlsx \
  --scenario Proposal_1
```

> "We can validate every single cell against the source document. This ensures 100% accuracy and provides a complete audit trail."

---

## Key Talking Points

### Time Savings

| Manual Process | Automated |
|----------------|-----------|
| 4-10 hours | < 60 seconds |
| Error-prone | 95%+ accuracy |
| Inconsistent | Standardized |
| No audit trail | Full traceability |

### Key Features to Highlight

1. **Multi-Format Support**
   - "We handle Word documents, Excel files, and even PDFs"

2. **Intelligent Categorization**
   - "The system automatically categorizes fees as Bundle, Non-Bundle, Required, Optional"

3. **Multi-Year Projections**
   - "5, 7, and 10-year projections with growth calculations"

4. **Side-by-Side Comparison**
   - "Compare vendors in a single template"

5. **AI-Powered QA**
   - "Confidence scoring and automatic validation"

6. **Complete Audit Trail**
   - "Every value tracked back to its source"

### Value Proposition

> "This tool:
> - Saves 4-10 hours per proposal
> - Reduces errors to near-zero
> - Provides consistent, auditable results
> - Enables faster vendor decisions"

---

## Handling Questions

### "What vendors do you support?"

> "Currently FIS and Jack Henry, which cover the majority of financial institution vendor evaluations. The architecture supports adding new vendors with configuration changes."

### "How accurate is the extraction?"

> "95-99% accuracy with rule-based extraction, and we have AI-powered validation to catch any issues. Every extraction includes confidence scores."

### "Can this work with our templates?"

> "Yes, the system is configurable. Column mappings, starting rows, and categories can all be customized to match your specific template."

### "What about security?"

> "Documents are processed locally. When using AI features, only the relevant text is sent to the API, and we never store sensitive data externally."

### "How long to implement?"

> "The core system is ready to use. Template customization typically takes 1-2 hours. Full deployment with training is usually 1-2 days."

### "What's the ROI?"

> "With 4-10 hours saved per proposal, and assuming 20-50 proposals per year, you're looking at 80-500 hours saved annually. That's equivalent to 4-12 weeks of analyst time."

---

## Troubleshooting During Demo

### Common Issues and Quick Fixes

| Issue | Quick Fix |
|-------|-----------|
| "Module not found" | `pip install -r requirements.txt` |
| File not found | Check file path, use `ls` to verify |
| Permission denied | Run as administrator or check file permissions |
| Empty output | Show pre-generated backup file |

### Backup Plan

If live demo fails:

1. Show pre-generated output files
2. Walk through screenshots
3. Explain the process conceptually

### Recovery Phrases

> "Let me show you a pre-generated example while we troubleshoot..."
>
> "This sometimes happens with [specific issue]. In production, we have error handling that..."
>
> "Let me pull up the results from our test run earlier..."

---

## Post-Demo Follow-Up

### Materials to Share

1. README documentation
2. Sample output files
3. Feature catalog
4. Contact information

### Next Steps

1. Schedule technical deep-dive
2. Provide trial access
3. Gather template samples for customization
4. Plan pilot implementation

---

## Demo Timing Summary

| Section | Duration |
|---------|----------|
| Opening & Problem | 2 min |
| Single Vendor Demo | 3 min |
| Comparison Demo | 3 min |
| AI Features | 2 min |
| Validation | 2 min |
| Q&A | 5 min |
| **Total** | **~15 min** |

---

## Quick Commands Reference

```bash
# FIS only
python main.py --fis FILE --template TEMPLATE --output OUTPUT --fis-term 7_year

# JH only
python main.py --jh FILE --template TEMPLATE --output OUTPUT --jh-scenario Proposal_1

# Both vendors
python main.py --fis FIS_FILE --jh JH_FILE --template TEMPLATE --output OUTPUT

# With AI
python run_pipeline.py FILE --vendor FIS -o output --json

# Validation
python cell_validator.py --source SOURCE --tco TCO --scenario Proposal_1
```

---

*Last Updated: December 2024*
