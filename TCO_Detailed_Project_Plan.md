# TCO Automation - Detailed Project Plan

**Project:** Vendor Proposal Extraction & Multi-Vendor TCO Comparison
**Client:** Arriba Advisors (Karishma)
**Timeline:** 2 days (20 developer hours)
**Date:** January 2026

---

# PAGE 1: PROBLEM STATEMENT

## Business Context

**Arriba Advisors** is a financial advisory firm that helps banking clients (e.g., Echelon Bank, Liberty Capital Bank) select core banking vendors. Multiple vendors (FIS, Jack Henry, CSI, etc.) submit proposals with complex pricing structures. Arriba needs to:

1. **Extract** pricing data from vendor proposals (PDF/Word/Excel)
2. **Standardize** the data into consistent formats for comparison
3. **Calculate** Total Cost of Ownership (TCO) with growth and CPI assumptions
4. **Compare** vendors side-by-side in an apples-to-apples format
5. **Present** TCO analysis to banking clients for decision-making

## Current Pain Points

### Manual Data Entry Burden
- Arriba employees manually copy/paste line items from proposals into Excel
- Each proposal takes 4-6 hours of manual data entry
- High error rate due to repetitive work
- Different vendor formats require custom handling each time

### Inconsistent Vendor Formats
- **FIS:** Word documents with tables
- **Jack Henry:** Excel spreadsheets with multiple scenarios
- **CSI:** PDF proposals with varied structures
- Each vendor uses different terminology, categories, and pricing models

### Complex TCO Calculations
- Must apply growth rates (typically 20%) and CPI (3-6%)
- Calculate monthly and annual costs for 5-10 year contracts
- Track one-time vs. recurring fees
- Categorize costs (Required, Optional, Bundled)
- Manual Excel formulas are error-prone and time-consuming

### Multi-Vendor Comparison Difficulty
- No standardized format for comparing vendors
- Hard to ensure apples-to-apples comparison
- Clients need clear traceability for every cost item
- Current process produces separate files per vendor, not side-by-side comparison

## Client's Stated Requirements

**From Karishma's Email:**
> "What I'm envisioning is an Excel or PDF we can upload in a consistent format, plus some automation (macros/formulas with a click) to capture monthly and annual totals, with growth and CPI built in (with tweakable assumptions on our end). It doesn't need to be 100% accurate—goal is to limit manual customization to ~10–15% and avoid repetitive copy/paste."

## Problem Statement (Concise)

**Arriba Advisors needs an automated system that:**
1. Extracts vendor proposal data into a **consistent Excel format** (regardless of vendor)
2. Accepts uploads of these standardized vendor extracts into a **calculation workbook**
3. Applies **one-click automation** with adjustable formulas (growth rate, CPI, contract term)
4. Generates a **multi-vendor TCO comparison** ready to drop into Arriba's financial models
5. Reduces manual data entry from 100% to 10-15% (85-90% automation)

**Key Constraint:** Accuracy is secondary to automation. The goal is to eliminate repetitive work, with manual review/adjustment accounting for the remaining 10-15%.

---

# PAGE 2: SOLUTION OUTCOMES & SUCCESS CRITERIA

## Desired Solution Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    VENDOR PROPOSALS (Input)                     │
│  - FIS (Word)  - Jack Henry (Excel)  - CSI (PDF)  - Others     │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│              EXTRACTION LAYER (Already Built ✅)                │
│     AI-powered extraction to JSON with categorization           │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│        VENDOR EXTRACT EXCEL (Consistent Format) ⚠️ NEW          │
│  - Standardized schema (all vendors)                            │
│  - Categories: Required, Optional, Bundled, One-Time            │
│  - One file per vendor per proposal                             │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│      TCO CALCULATOR WORKBOOK (Excel + Macros) ⚠️ NEW            │
│  - Upload/paste multiple vendor extracts                        │
│  - Adjustable parameters (Growth %, CPI %, Term)                │
│  - One-click "Calculate TCO" macro button                       │
│  - Pre-built formulas for monthly/annual totals                 │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│      TCO OUTPUT (Multi-Vendor Comparison) ⚠️ MODIFIED           │
│  - Side-by-side vendor comparison                               │
│  - Monthly and annual totals (Years 1-7)                        │
│  - Category breakdowns                                          │
│  - Ready to drop into Arriba's financial model                  │
└─────────────────────────────────────────────────────────────────┘
```

## Solution Components

### Component 1: Vendor Extract Excel Template
**Purpose:** Consistent intermediate format for all vendor data

**Structure:**
- **Sheet 1: Line Items**
  - Solution Name, Category, Fee Type, Per Unit Rate, Volume, Unit, Notes
  - Rows organized by category (Required, Optional, Bundled, One-Time)
- **Sheet 2: Metadata**
  - Vendor Name, Client Name, Proposal Date, Contract Term

**Output:** One Excel file per vendor (e.g., `FIS_Echelon_Extract_2026.xlsx`)

### Component 2: JSON-to-Vendor-Extract Converter
**Purpose:** Transform existing JSON extraction output to Vendor Extract format

**Technical Approach:**
- Modify existing `json_to_excel_mapper.py`
- Simplify output (remove complex formulas, focus on raw data)
- Ensure consistent categorization across vendors
- Add data validation rules

### Component 3: TCO Calculator Workbook (Excel + VBA)
**Purpose:** Accept vendor extracts, apply calculations, generate comparison

**Sheet Structure:**
1. **Import Zone:** Paste vendor extract data here
2. **Parameters:** Growth Rate %, CPI %, Contract Term (user-adjustable)
3. **Vendor 1 Calculations:** Formulas applied to Vendor 1 data
4. **Vendor 2 Calculations:** Formulas applied to Vendor 2 data
5. **Vendor 3+ Calculations:** Additional vendor sheets as needed
6. **TCO Output:** Final multi-vendor comparison

**VBA Macro:** "Calculate_TCO"
- Read imported vendor data
- Detect number of vendors
- Create calculation sheets dynamically
- Apply formulas for Years 1-7
- Populate TCO Output sheet

### Component 4: TCO Output Sheet
**Purpose:** Final deliverable for Arriba's financial model

**Layout:**
- Rows: Line items grouped by category
- Columns: Vendor A | Vendor B | Vendor C | Variance
- Summary section: Total costs by year, monthly averages
- Charts: Visual comparison (optional)

## Success Criteria

| Criterion | Target | Measurement Method |
|-----------|--------|-------------------|
| **Automation Rate** | 85-90% automated | Time study: manual vs. automated workflow |
| **Data Consistency** | 100% schema compliance | All vendor extracts follow same structure |
| **Extraction Accuracy** | 95%+ (already achieved) | Existing QA validation process |
| **Formula Correctness** | 100% calculation accuracy | Manual validation of sample calculations |
| **Multi-Vendor Support** | 3+ vendors in single output | Test with FIS, CSI, Jack Henry |
| **User Experience** | ≤5 clicks to complete | User flow testing |
| **Customization Flexibility** | Growth/CPI adjustable per vendor | UI testing |
| **Manual Review Time** | 10-15% of total effort | Karishma's stated goal |
| **Output Compatibility** | Drops directly into financial model | Arriba team validation |
| **Documentation Quality** | User can operate without training | Independent user test |

## Key Performance Indicators (KPIs)

**Before Automation:**
- Time per proposal: 4-6 hours manual data entry
- Error rate: ~15-20% (estimates, formulas)
- Multi-vendor comparison time: Additional 2-3 hours

**After Automation:**
- Time per proposal: 30-45 minutes (upload, review, adjust)
- Error rate: <5% (AI extraction + formula automation)
- Multi-vendor comparison time: Included (one-click)

**ROI:** ~85-90% time savings per proposal

---

# PAGE 3: KEY IMPLEMENTATION STEPS

## Phase 1: Design & Schema Definition (Day 1 Morning - 1 hour)

### Joint Activity (Both Developers)

**Objective:** Define the data contract between Vendor Extract and Calculator Workbook

**Deliverable:** Schema document with field definitions

**Key Decisions:**
1. **Column structure** for Vendor Extract Line Items sheet
2. **Metadata fields** required (vendor, client, proposal date, contract term)
3. **Category taxonomy** (Required, Optional, Bundled, One-Time)
4. **Fee type definitions** (Monthly F, Monthly V, Annual, One-Time)
5. **Naming conventions** for files and sheets

**Output:** `SCHEMA_DEFINITION.md` (agreed by both developers)

## Phase 2: Vendor Extract Pipeline (Day 1-2 - Developer 1)

### Step 1: Create Vendor Extract Template (2 hours)
- Design `Vendor_Extract_Template.xlsx`
- Set up data validation rules
- Add conditional formatting for data quality
- Create instructions sheet

### Step 2: Modify JSON-to-Excel Converter (2 hours)
- Clone `json_to_excel_mapper.py` → `json_to_vendor_extract.py`
- Simplify output structure (remove formulas)
- Map JSON fields to Vendor Extract schema
- Add metadata population logic
- Handle edge cases (missing data, multi-fee items)

### Step 3: Generate Sample Vendor Extracts (2 hours)
- Run converter on existing JSON files:
  - FIS (Echelon Bank proposal)
  - CSI (Liberty Capital Bank proposal)
  - Jack Henry (if available)
- Validate schema compliance
- Visual QA review
- Fix any mapping issues

### Step 4: Documentation (1.5 hours)
- Create `Vendor_Extract_Guide.md`:
  - Schema reference
  - Field definitions
  - Category taxonomy
  - Usage instructions for Arriba team
- Add code comments
- Update README

### Step 5: Integration Testing (1.5 hours)
- Import sample vendor extracts into Dev 2's calculator
- Verify data integrity
- Test edge cases
- Fix any compatibility issues

## Phase 3: Excel Calculator Workbook (Day 1-2 - Developer 2)

### Step 1: Create Workbook Structure (1.5 hours)
- Create `TCO_Calculator_Master.xlsm` (macro-enabled)
- Set up sheet structure (Import Zone, Parameters, Vendor Calcs, TCO Output)
- Design user interface (buttons, instructions)
- Add sheet protection for formula areas

### Step 2: Build Parameters Sheet (1 hour)
- Create input cells:
  - Growth Rate % (default: 20%)
  - CPI % (default: 3-6%, customizable per vendor)
  - Contract Term (5/7/10 years dropdown)
- Add data validation
- Named ranges for formulas
- Help text/tooltips

### Step 3: Build Formula Layer (2.5 hours)
- **Import Zone:**
  - Structured table for paste operations
  - Data validation on paste
- **Vendor Calculation Sheets:**
  - Monthly cost formulas: `=IF(FeeType="Monthly F", Rate, IF(FeeType="Monthly V", Rate*Qty, ...))`
  - Annual cost formulas: `=Monthly * 12` or `=AnnualRate`
  - Year-over-year growth: `=PrevYear * (1 + GrowthRate) * (1 + CPI)`
  - Category subtotals: `=SUMIF(Category, "Required", AnnualCost)`
- **TCO Output Sheet:**
  - Side-by-side vendor references
  - Variance calculations
  - Summary totals

### Step 4: Create VBA Macro (2 hours)
- **Macro: `Calculate_TCO`**
  - Read Import Zone data
  - Detect number of vendors (from metadata)
  - Create vendor calculation sheets dynamically
  - Copy data to appropriate sheets
  - Trigger formula calculation
  - Populate TCO Output sheet
  - Format results (currency, colors, borders)
- Add error handling
- Progress indicator
- User confirmation prompts

### Step 5: Build TCO Output Sheet (1 hour)
- Design multi-vendor comparison layout
- Add summary section (totals by year)
- Create charts (optional):
  - Cost breakdown by category
  - Vendor comparison bar chart
  - Year-over-year trend
- Apply professional formatting

### Step 6: Testing & User Guide (1.5 hours)
- Test with Dev 1's sample vendor extracts
- Validate calculations manually
- Test edge cases (1 vendor, 5 vendors, missing data)
- Create user guide:
  - Step-by-step instructions with screenshots
  - Troubleshooting section
  - FAQs
- Embed instructions in workbook (Sheet 0: "How to Use")

## Phase 4: Integration & Testing (Day 2 Afternoon - Both Developers)

### Integration Testing (1.5 hours)
1. **End-to-End Workflow Test:**
   - Proposal PDF → JSON → Vendor Extract → Calculator → TCO Output
2. **Multi-Vendor Test:**
   - Upload 3 vendor extracts simultaneously
   - Run Calculate_TCO macro
   - Verify output correctness
3. **Parameter Testing:**
   - Test different growth rates (10%, 20%, 30%)
   - Test different CPI rates (2%, 5%, 8%)
   - Test different contract terms (5/7/10 years)
4. **Edge Case Testing:**
   - Single vendor
   - Missing data fields
   - Zero-cost items
   - Negative costs (credits)
5. **Manual Validation:**
   - Spot-check 10 line items
   - Verify formulas match expected results
   - Compare against manual Excel calculation

### Final Review (30 minutes)
- Code review (cross-review each other's work)
- Documentation review
- Prepare demo for stakeholders
- Create issues list for future enhancements

---

# PAGE 4: DEVELOPER-WISE WORK SPLIT

## Developer 1: Data Pipeline & Vendor Extract

### Responsibilities
- Vendor Extract Excel template design
- JSON-to-Vendor-Extract conversion script
- Sample vendor extract generation
- Data quality validation
- Documentation for Arriba team

### Detailed Task Breakdown

#### Day 1 (5 hours)
| Time | Task | Details | Hours |
|------|------|---------|-------|
| 9:00-10:00 | Joint schema meeting | Define data contract with Dev 2 | 1h |
| 10:00-12:00 | Create Vendor Extract template | Excel file with Line Items + Metadata sheets | 2h |
| 12:00-1:00 | Lunch break | - | - |
| 1:00-3:00 | Start JSON converter script | Clone and modify json_to_excel_mapper.py | 2h |

**End of Day 1 Deliverables:**
- `Vendor_Extract_Template.xlsx` (draft)
- `json_to_vendor_extract.py` (50% complete)
- Commit to `feature/vendor-extract-pipeline` branch

#### Day 2 (5 hours)
| Time | Task | Details | Hours |
|------|------|---------|-------|
| 9:00-11:00 | Complete JSON converter | Finish script, test with sample JSON | 2h |
| 11:00-12:00 | Generate sample extracts | Run for FIS, CSI, Jack Henry | 1h |
| 12:00-1:00 | Lunch break | - | - |
| 1:00-2:00 | Documentation | Create Vendor_Extract_Guide.md | 1h |
| 2:00-3:30 | Integration testing | Test with Dev 2's calculator | 1.5h |

**End of Day 2 Deliverables:**
- `Vendor_Extract_Template.xlsx` (final)
- `json_to_vendor_extract.py` (complete)
- 3 sample vendor extract files
- `Vendor_Extract_Guide.md`
- Merged to `main` branch

### Technical Stack
- **Languages:** Python 3.11+
- **Libraries:** openpyxl, json, pathlib
- **Files Modified:**
  - New: `scripts/json_to_vendor_extract.py`
  - New: `Templates/Vendor_Extract_Template.xlsx`
  - New: `docs/Vendor_Extract_Guide.md`

### Testing Checklist
- [ ] Vendor Extract template has correct schema
- [ ] JSON converter handles all 3 vendor types (FIS, CSI, Jack Henry)
- [ ] Category mapping is consistent
- [ ] Metadata populates correctly
- [ ] Sample extracts validate without errors
- [ ] Data imports cleanly into Dev 2's calculator

---

## Developer 2: Excel Calculator Workbook

### Responsibilities
- TCO Calculator Workbook design
- VBA macro development
- Formula implementation
- TCO Output sheet layout
- User guide creation

### Detailed Task Breakdown

#### Day 1 (5 hours)
| Time | Task | Details | Hours |
|------|------|---------|-------|
| 9:00-10:00 | Joint schema meeting | Define data contract with Dev 1 | 1h |
| 10:00-11:30 | Create workbook structure | Set up sheets, basic layout | 1.5h |
| 11:30-12:30 | Build Parameters sheet | Input cells with validation | 1h |
| 12:30-1:30 | Lunch break | - | - |
| 1:30-4:00 | Build formula layer | Monthly/annual cost formulas | 2.5h |

**End of Day 1 Deliverables:**
- `TCO_Calculator_Master.xlsm` (skeleton)
- Parameters sheet (complete)
- Formula layer (80% complete)
- Commit to `feature/excel-calculator` branch

#### Day 2 (5 hours)
| Time | Task | Details | Hours |
|------|------|---------|-------|
| 9:00-11:00 | Create VBA macro | Calculate_TCO macro code | 2h |
| 11:00-12:00 | Build TCO Output sheet | Multi-vendor comparison layout | 1h |
| 12:00-1:00 | Lunch break | - | - |
| 1:00-2:00 | User guide & testing | Documentation + validation | 1h |
| 2:00-3:30 | Integration testing | Test with Dev 1's vendor extracts | 1.5h |

**End of Day 2 Deliverables:**
- `TCO_Calculator_Master.xlsm` (complete with macros)
- VBA code documented
- User guide (PDF + embedded in workbook)
- Test validation report
- Merged to `main` branch

### Technical Stack
- **Software:** Microsoft Excel (macro-enabled)
- **Languages:** VBA (Visual Basic for Applications), Excel formulas
- **Files Created:**
  - New: `Templates/TCO_Calculator_Master.xlsm`
  - New: `docs/TCO_Calculator_User_Guide.pdf`

### VBA Macro Pseudocode

```vba
Sub Calculate_TCO()
    ' 1. Read Import Zone
    Set importData = Worksheets("Import Zone").Range("A:G")

    ' 2. Detect number of vendors
    vendorCount = DetectVendorCount(importData)

    ' 3. Create vendor calculation sheets
    For i = 1 To vendorCount
        CreateVendorSheet("Vendor " & i)
        PopulateVendorData(i, importData)
    Next i

    ' 4. Apply formulas
    For i = 1 To vendorCount
        ApplyCalculationFormulas("Vendor " & i)
    Next i

    ' 5. Populate TCO Output
    PopulateTCOOutput(vendorCount)

    ' 6. Format results
    FormatTCOOutput()

    MsgBox "TCO calculation complete! See 'TCO Output' sheet."
End Sub
```

### Testing Checklist
- [ ] Import Zone accepts pasted data correctly
- [ ] Parameters sheet validation works
- [ ] Formulas calculate correctly for all fee types
- [ ] VBA macro runs without errors
- [ ] TCO Output populates with correct data
- [ ] Multi-vendor comparison (3 vendors) works
- [ ] Edge cases handled (missing data, 1 vendor, 5 vendors)
- [ ] User guide is clear and complete

---

## Coordination Points Between Developers

### Daily Standups (15 minutes each)
- **Day 1 - 9:00 AM:** Schema definition meeting (1 hour)
- **Day 1 - 3:00 PM:** Mid-point sync (30 min)
  - Dev 1 shares draft vendor extract template
  - Dev 2 provides feedback on schema
- **Day 2 - 11:00 AM:** Quick sync (15 min)
  - Dev 1 shares sample vendor extract files
  - Dev 2 imports for initial testing
- **Day 2 - 2:00 PM:** Integration testing (1.5 hours)
  - Joint end-to-end workflow testing
  - Bug fixes and final adjustments

### Shared Deliverables

Both developers contribute to:
1. **SCHEMA_DEFINITION.md** (Day 1 AM)
2. **Integration test report** (Day 2 PM)
3. **README.md updates** (Day 2 PM)

### Communication Protocol
- Use Git commit messages for async updates
- Slack/Teams for quick questions
- Screen share for complex issues
- Tag commits with `[Dev1]` or `[Dev2]` prefix

---

# PAGE 5: GITHUB WORKFLOW FOR CLEAN INTEGRATION

## Branch Strategy

```
main (production-ready code)
  ├── feature/vendor-extract-pipeline (Developer 1)
  └── feature/excel-calculator (Developer 2)
```

### Branch Naming Convention
- `feature/vendor-extract-pipeline` - Dev 1's work
- `feature/excel-calculator` - Dev 2's work
- No other branches needed for 2-day sprint

## Git Workflow - Step by Step

### Day 1 - Morning (Both Developers)

```bash
# Both developers start from latest main
git checkout main
git pull origin main

# Developer 1 creates feature branch
git checkout -b feature/vendor-extract-pipeline

# Developer 2 creates feature branch
git checkout -b feature/excel-calculator
```

### Day 1 - Afternoon (Both Developers)

**Developer 1:**
```bash
# Add Vendor Extract template and initial converter script
git add Templates/Vendor_Extract_Template.xlsx
git add scripts/json_to_vendor_extract.py
git commit -m "[Dev1] Add Vendor Extract template and converter script (WIP)"
git push origin feature/vendor-extract-pipeline
```

**Developer 2:**
```bash
# Add calculator workbook skeleton
git add Templates/TCO_Calculator_Master.xlsm
git add docs/calculator_design.md
git commit -m "[Dev2] Add TCO Calculator workbook structure and parameters sheet"
git push origin feature/excel-calculator
```

### Day 1 - End of Day

Both developers commit and push their work in progress.

### Day 2 - Morning

**Developer 1:**
```bash
# Continue work on converter script
git add scripts/json_to_vendor_extract.py
git add "Vendor Extracts/FIS_Echelon_Extract_2026.xlsx"
git add "Vendor Extracts/CSI_Liberty_Extract_2026.xlsx"
git commit -m "[Dev1] Complete vendor extract converter with sample outputs"
git push origin feature/vendor-extract-pipeline
```

**Developer 2:**
```bash
# Complete VBA macro and TCO Output sheet
git add Templates/TCO_Calculator_Master.xlsm
git commit -m "[Dev2] Add VBA macro and TCO Output sheet"
git push origin feature/excel-calculator
```

### Day 2 - Mid-Day (Developer 1 Merges First)

**Developer 1 creates Pull Request:**
```bash
# Push final changes
git add docs/Vendor_Extract_Guide.md
git commit -m "[Dev1] Add vendor extract documentation"
git push origin feature/vendor-extract-pipeline

# Create PR via GitHub UI or CLI
gh pr create --title "Vendor Extract Pipeline" \
             --body "Adds vendor extract template and JSON converter"
```

**Code Review (5 minutes):**
- Developer 2 reviews PR
- Check for conflicts with `main`
- Approve if no issues

**Merge to Main:**
```bash
# Developer 1 merges PR
gh pr merge --merge
```

### Day 2 - Afternoon (Developer 2 Integration)

**Developer 2 rebases on latest main:**
```bash
# Pull latest main (includes Dev 1's work)
git checkout main
git pull origin main

# Rebase feature branch on main
git checkout feature/excel-calculator
git rebase main

# If conflicts, resolve them
# (Unlikely since developers worked on separate files)

# Push updated branch
git push origin feature/excel-calculator --force-with-lease
```

**Integration Testing:**
- Use Dev 1's sample vendor extracts
- Test calculator workbook
- Fix any issues found

**Final Commit:**
```bash
git add Templates/TCO_Calculator_Master.xlsm
git add docs/TCO_Calculator_User_Guide.pdf
git commit -m "[Dev2] Final calculator workbook with tested integration"
git push origin feature/excel-calculator
```

**Developer 2 creates Pull Request:**
```bash
gh pr create --title "Excel Calculator Workbook" \
             --body "Adds TCO calculator with VBA macros and multi-vendor comparison"
```

**Merge to Main:**
```bash
gh pr merge --merge
```

### Day 2 - End (Final Testing on Main)

```bash
# Both developers checkout main
git checkout main
git pull origin main

# Run end-to-end test
# Verify all components work together
```

## Conflict Prevention Strategy

### File Ownership

**Developer 1 owns:**
- `scripts/json_to_vendor_extract.py`
- `Templates/Vendor_Extract_Template.xlsx`
- `Vendor Extracts/*.xlsx` (sample files)
- `docs/Vendor_Extract_Guide.md`

**Developer 2 owns:**
- `Templates/TCO_Calculator_Master.xlsm`
- `docs/TCO_Calculator_User_Guide.pdf`

**Shared files (coordinate before committing):**
- `README.md` - Developer 2 updates at end
- `requirements.txt` - Developer 1 adds dependencies first
- `SCHEMA_DEFINITION.md` - Joint creation on Day 1

### Merge Conflict Resolution

**If conflicts occur (unlikely):**
1. Identify conflicting files
2. Communicate via Slack/Teams
3. Decide who resolves (usually file owner)
4. Use `git mergetool` or manual resolution
5. Test after resolution
6. Commit resolved files

## Commit Message Convention

```
[DevX] <Type>: <Short description>

<Optional longer description>

Examples:
[Dev1] feat: Add vendor extract Excel template
[Dev2] feat: Implement Calculate_TCO VBA macro
[Dev1] fix: Handle missing metadata in JSON converter
[Dev2] docs: Add user guide for calculator workbook
[Dev1] test: Add sample vendor extracts for FIS and CSI
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `test`: Test files or testing
- `refactor`: Code refactoring
- `chore`: Maintenance tasks

## Pull Request Template

```markdown
## Description
Brief description of changes

## Changes Made
- List of specific changes
- Files added/modified
- Features implemented

## Testing
- [ ] Unit testing complete
- [ ] Integration testing complete
- [ ] Manual validation performed

## Screenshots (if applicable)
Attach screenshots of Excel templates/output

## Related Issues
Closes #123 (if applicable)

## Checklist
- [ ] Code follows project style guidelines
- [ ] Documentation updated
- [ ] Tests pass
- [ ] Ready for merge
```

## Deployment/Release Process

Since this is an Excel-based solution with Python scripts:

**After both PRs are merged to main:**

1. **Tag Release:**
```bash
git tag -a v1.0.0 -m "Initial release: Vendor Extract Pipeline + TCO Calculator"
git push origin v1.0.0
```

2. **Package Deliverables:**
```bash
# Create release folder
mkdir TCO_Automation_v1.0.0

# Copy files
cp Templates/Vendor_Extract_Template.xlsx TCO_Automation_v1.0.0/
cp Templates/TCO_Calculator_Master.xlsm TCO_Automation_v1.0.0/
cp scripts/json_to_vendor_extract.py TCO_Automation_v1.0.0/
cp docs/*.md TCO_Automation_v1.0.0/
cp docs/*.pdf TCO_Automation_v1.0.0/

# Create ZIP
zip -r TCO_Automation_v1.0.0.zip TCO_Automation_v1.0.0/
```

3. **Deliver to Client (Arriba):**
- Send ZIP file via email/cloud storage
- Schedule training session (30 min walkthrough)
- Provide support contact information

## Rollback Plan

**If issues are found after merge:**

```bash
# Revert specific commit
git revert <commit-hash>

# Or revert entire PR merge
git revert -m 1 <merge-commit-hash>

# Push revert
git push origin main
```

## Best Practices

1. **Commit often** - Small, logical commits are easier to review and revert
2. **Write clear commit messages** - Future you will thank present you
3. **Test before committing** - Don't commit broken code
4. **Pull before push** - Always get latest changes first
5. **Communicate** - Let your partner know about big changes
6. **Review your own PR** - Catch obvious issues before requesting review
7. **Use .gitignore** - Don't commit temporary files, logs, or OS files

## .gitignore Additions

```gitignore
# Excel temporary files
~$*.xlsx
~$*.xlsm

# Python cache
__pycache__/
*.pyc
*.pyo

# Logs
logs/*.log

# OS files
.DS_Store
Thumbs.db

# IDE files
.vscode/
.idea/
*.swp
```

---

**END OF DETAILED PROJECT PLAN**

---

## Quick Reference Summary

**Total Time:** 20 hours (2 days × 2 developers × 5 hours/day)

**Key Milestones:**
- Day 1 AM: Schema defined
- Day 1 PM: Templates created, initial code written
- Day 2 AM: Code complete, sample files generated
- Day 2 PM: Integration tested, merged to main

**Final Deliverables:**
1. Vendor Extract Template (Excel)
2. JSON-to-Vendor-Extract converter (Python)
3. TCO Calculator Workbook (Excel + VBA)
4. Sample vendor extract files (3)
5. Documentation (guides, schema, README)
6. Tested, integrated system on `main` branch

**Success Metric:** 85-90% reduction in manual data entry for Arriba Advisors
