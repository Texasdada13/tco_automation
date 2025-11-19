# TCO Automation - QA Checklist

Use this checklist to manually verify the automation results.

## Pre-Processing Checks

### Source Files
- [ ] FIS proposal is a Word document (.docx)
- [ ] Jack Henry proposal is an Excel file (.xlsx)
- [ ] TCO template is the correct version
- [ ] All files are readable (not corrupted)

## Extraction Validation

### FIS Proposal
- [ ] All tables were detected (check console output for "Found X tables")
- [ ] Bundle pricing extracted for all years
- [ ] Monthly fees count matches visual inspection of proposal
- [ ] One-time credits captured (including negatives for credits)
- [ ] No "Unknown table type" for important tables

**Quick Check:**
1. Open FIS proposal
2. Count the pricing tables manually
3. Compare with extraction log

### Jack Henry Proposal
- [ ] All scenarios detected (Proposal_1, Proposal_2, Proposal_3)
- [ ] Product count matches expectations (~150-200 products typical)
- [ ] Summary sheet data extracted
- [ ] No missing product families

**Quick Check:**
1. Open JH Excel file → Proposal_1 sheet
2. Scroll to bottom to see last product row
3. Compare with extraction log "Extracted X products"

## Mapping Validation

### Data Normalization
- [ ] All line items have solution names
- [ ] Fee types are valid (Monthly F, Monthly V, Annual, One-Time)
- [ ] Categories are assigned correctly:
  - [ ] Bundle items marked as "Bundle"
  - [ ] Required items marked as "Non-Bundle Required"
  - [ ] Optional items marked as "Non-Bundle Optional"
  - [ ] Third-party items identified
- [ ] No line items with all zero values (unless intentional)

**Quick Check:**
Run the QA validator:
```bash
python qa_validator.py --fis data/proposal.docx --jh data/jh.xlsx --tco output.xlsx
```

## TCO Population Validation

### Excel Template
- [ ] Line Items sheet exists and is populated
- [ ] FIS data in correct columns (B-AN)
- [ ] Jack Henry data in correct columns (AR-CA) if processed
- [ ] No overwritten formulas in calculation cells
- [ ] Row spacing is correct (no gaps in data)

### Data Accuracy

#### Bundle Pricing (FIS)
- [ ] Year 1 bundle price matches FIS proposal
- [ ] Year 2 bundle price matches FIS proposal
- [ ] Year 3 bundle price matches FIS proposal
- [ ] Prices match the selected term (5/7/10 year)

**Manual Check:**
1. Open FIS proposal → Find bundle pricing table
2. Open TCO output → Line Items sheet
3. Find "Year 1 CORE PROCESSING (Bundle)" row
4. Compare values

#### Monthly Fees
- [ ] Sample 5 monthly fees from source
- [ ] Verify they appear in TCO with correct amounts
- [ ] Check fee type assignment (Fixed vs Variable)

**Manual Check:**
1. Pick 3-5 products from source proposals
2. Search for them in TCO Line Items sheet (Ctrl+F)
3. Verify amounts match

#### One-Time Fees/Credits
- [ ] Implementation fees captured
- [ ] Credits are negative values
- [ ] Values match source proposal

### Calculations

#### Quantities
- [ ] Year 1 quantities populated
- [ ] Growth applied to subsequent years (if applicable)
- [ ] Quantity = 12 for monthly items (12 months)
- [ ] Quantity = 0 for one-time items

#### Costs
- [ ] Year 1 costs calculated correctly
- [ ] Multi-year projections filled
- [ ] One-time fees only in Year 1
- [ ] Monthly fees multiplied by quantities

**Sample Calculation Check:**
```
Monthly Fee: $1,000
Quantity Year 1: 12 months
Expected Cost Year 1: $1,000 × 12 = $12,000
```

## Side-by-Side Comparison (Both Vendors)

If processing both FIS and Jack Henry:

- [ ] Both vendor columns populated
- [ ] No data overlap between vendors
- [ ] Categories align for comparison
- [ ] Totals can be calculated

## Output Quality

### Professional Standards
- [ ] No #REF! or #VALUE! errors in Excel
- [ ] No obviously wrong values (e.g., $0 for major items)
- [ ] Solution names are readable (not truncated badly)
- [ ] Categories are consistent

### Business Logic
- [ ] Bundle pricing increases over years (FIS)
- [ ] Optional items clearly marked
- [ ] Third-party solutions identified
- [ ] Major cost items present (core processing, digital banking, etc.)

## Automated QA Reports

### Run QA Validator
```bash
python qa_validator.py --fis data/proposal.docx --jh data/jh.xlsx --tco output.xlsx --report qa_report.txt
```

**Check Report For:**
- [ ] All extraction tests passed
- [ ] All mapping tests passed
- [ ] All population tests passed
- [ ] No critical issues flagged

### Run Comparison Tool
```bash
python qa_comparison.py --fis data/proposal.docx --jh data/jh.xlsx --tco output.xlsx --output comparison.xlsx
```

**Review Comparison Report:**
- [ ] Bundle pricing matches (✓ in Match column)
- [ ] Sample monthly fees present
- [ ] No major discrepancies

## Final Verification

### Spot Check Method
1. **Pick 10 random items** from source proposals
2. **Search for them** in TCO output (Ctrl+F)
3. **Verify amounts** match
4. **Check categories** are logical
5. **Verify fee types** are appropriate

### Reasonableness Test
- [ ] Total Year 1 cost seems reasonable
- [ ] FIS vs JH totals are in expected range
- [ ] No single line item is >50% of total (unless expected)
- [ ] Bundle costs are largest portion

### Deliverable Check
- [ ] File opens in Excel without errors
- [ ] All sheets present
- [ ] Ready to present to bank

## Sign-Off

**Date:** _______________

**Validated By:** _______________

**Issues Found:** 
___ None
___ Minor (documented below)
___ Major (documented below)

**Notes:**
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________

**Approved for Delivery:** ☐ Yes  ☐ No (needs rework)

---

## Common Issues & Fixes

| Issue | Likely Cause | Fix |
|-------|-------------|-----|
| Missing products | Wrong scenario selected | Re-run with correct --jh-scenario |
| Wrong bundle price | Wrong term selected | Re-run with correct --fis-term |
| All zeros | Source format changed | Update extractor patterns |
| Wrong categories | Keyword mismatch | Update config.py mappings |
| Missing rows | Starting row wrong | Update LINE_ITEM_START_ROWS in config.py |

## QA Tools Quick Reference

```bash
# Full QA validation with report
python qa_validator.py --fis data/fis.docx --jh data/jh.xlsx --tco output.xlsx

# Comparison report
python qa_comparison.py --fis data/fis.docx --jh data/jh.xlsx --tco output.xlsx

# Test extraction only
python -m extractors.fis_extractor data/fis.docx

# Test mapping only
python -m mappers.schema_mapper
```
