# Quick QA Test Script

This guide shows you how to use the QA tools.

## Files You Now Have

1. **qa_validator.py** - Automated validation checks
2. **qa_comparison.py** - Compares source to output
3. **QA_CHECKLIST.md** - Manual verification checklist

## How to Use

### 1. Run Automated QA Validator

This checks extraction, mapping, and population automatically:

```powershell
python qa_validator.py --fis data/Echelon_FIS_Proposal_10_29_25.docx --jh data/Updated_With_all_products__Deal_Sheet_Clearwater__FL_-_Echelon_Bank__InOrg__-_New_Core_SilverLake_OL_PAP_08_27_25.xlsx --tco full_comparison.xlsx --report qa_report.txt
```

**What it does:**
- ✅ Validates FIS extraction (bundle pricing, fees, credits)
- ✅ Validates Jack Henry extraction (products, scenarios)
- ✅ Validates data mapping (categories, fee types)
- ✅ Validates TCO population (row counts, data integrity)
- 📄 Generates detailed report: `qa_report.txt`

**You should see:**
```
QA CHECK: FIS EXTRACTION
✓ Bundle years extracted: 7
✓ Monthly fees extracted: 30
✓ One-time credits extracted: 7
✅ FIS extraction validation PASSED

QA CHECK: JACK HENRY EXTRACTION
✓ Scenarios extracted: 3
✓ Proposal_1: 173 products
✅ Jack Henry extraction validation PASSED

...

✅ QA Validation Complete!
```

### 2. Run Comparison Tool

This creates an Excel report comparing source data to TCO output:

```powershell
python qa_comparison.py --fis data/Echelon_FIS_Proposal_10_29_25.docx --jh data/Updated_With_all_products__Deal_Sheet_Clearwater__FL_-_Echelon_Bank__InOrg__-_New_Core_SilverLake_OL_PAP_08_27_25.xlsx --tco full_comparison.xlsx --output comparison_report.xlsx
```

**What it creates:**
- 📊 Excel file: `comparison_report.xlsx`
- Sheet 1: FIS Comparison (source vs TCO)
- Sheet 2: JH Comparison (source vs TCO)

**Shows you:**
- Which items matched perfectly (✓)
- Which items didn't match (✗)
- Which items need manual review (?)

### 3. Manual Checklist

Open `QA_CHECKLIST.md` and follow the step-by-step verification:

```powershell
code QA_CHECKLIST.md
```

This gives you:
- Pre-processing checks
- Item-by-item verification steps
- Spot-check methods
- Sign-off template

## Quick Verification Process

### Step 1: Run the Automation
```powershell
python main.py --fis data/your_fis.docx --jh data/your_jh.xlsx --template data/your_template.xlsx --output result.xlsx
```

### Step 2: Run QA Validator
```powershell
python qa_validator.py --fis data/your_fis.docx --jh data/your_jh.xlsx --tco result.xlsx
```

### Step 3: Review QA Report
```powershell
cat qa_report.txt
# Or open in notepad:
notepad qa_report.txt
```

### Step 4: Run Comparison
```powershell
python qa_comparison.py --fis data/your_fis.docx --jh data/your_jh.xlsx --tco result.xlsx
```

### Step 5: Open Comparison Report
```powershell
# Open in Excel
start comparison_report.xlsx
```

### Step 6: Manual Spot Check
1. Pick 5 random items from source proposals
2. Search for them in TCO (Ctrl+F)
3. Verify amounts match
4. Check categories make sense

## What to Look For

### ✅ Good Signs
- QA report shows "PASSED" for all sections
- Comparison report shows ✓ for bundle pricing
- No major discrepancies in amounts
- Row counts match expectations
- Categories are logical

### ⚠️ Warning Signs
- QA report shows "FAILED" for any section
- Comparison shows multiple ✗ mismatches
- Missing products that should be there
- All-zero values for major items
- Wrong categories (Bundle items as Optional, etc.)

### 🔴 Red Flags
- Extraction fails completely
- TCO file has #REF! or #VALUE! errors
- Major items missing (core processing, etc.)
- Values off by 10x or 100x
- No data in vendor columns

## Troubleshooting

### Issue: "Module not found" error
**Fix:** Make sure you're in the tco_automation folder
```powershell
cd C:\Users\dada_\OneDrive\Documents\TCO_Automation\tco_automation
```

### Issue: QA validator shows mismatches
**Fix:** 
1. Check if you used the right term (5/7/10 year)
2. Check if you used the right scenario (Proposal_1/2/3)
3. Review extraction logs for warnings

### Issue: Comparison report shows "NOT FOUND"
**Fix:**
- Item might be in different category section
- Check if item name was truncated/changed
- Search manually in TCO file

## Integration into Workflow

### Recommended Process

**For every TCO you create:**

1. Run automation → Get `output.xlsx`
2. Run QA validator → Get `qa_report.txt`
3. Review report → Check for PASS/FAIL
4. Run comparison → Get `comparison_report.xlsx`
5. Review comparison → Spot check matches
6. Manual verification → Use QA_CHECKLIST.md
7. Sign off → Document in checklist

**Time Required:**
- Automation: 30 seconds
- QA validation: 30 seconds
- Review reports: 5 minutes
- Manual spot check: 5 minutes
- **Total: ~10 minutes** (vs. hours of manual work!)

## Advanced: Custom Validations

You can modify `qa_validator.py` to add custom checks:

```python
# Add your own validation logic
def validate_custom_rule(self, data):
    # Example: Check if core processing is present
    has_core = any('core processing' in item['solution_name'].lower() 
                   for item in data)
    if not has_core:
        self.validation_results['issues'].append('Core processing not found!')
```

---

**Questions? Need help customizing the QA process?** Let me know!
