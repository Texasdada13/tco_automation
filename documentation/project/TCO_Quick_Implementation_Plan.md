# TCO Automation - Quick Implementation Plan (2 Days)

---

## PAGE 1: CURRENT STATE vs. WHAT NEEDS TO BE DONE

### ✅ WHAT'S ALREADY BUILT

| Component | Status | Details |
|-----------|--------|---------|
| **Proposal Extraction** | ✅ Complete | PDF/Word/Excel → JSON extraction working for FIS, CSI, Jack Henry |
| **JSON to Excel Mapper** | ✅ Complete | `json_to_excel_mapper.py` transforms JSON → structured Excel |
| **TCO Template** | ✅ Complete | `Templates/New_TCO_Excel_v1.xlsx` with formulas for Years 1-7 |
| **Data Quality Pipeline** | ✅ Complete | Validation, normalization, confidence scoring |
| **Category Organization** | ✅ Complete | Line items already categorized (Required, Optional, Bundled, One-Time) |

**Current Flow (Working):**
```
Proposal PDF → JSON Extraction → Excel with Line Items (single vendor) → TCO Output
```

### ❌ WHAT NEEDS TO BE DONE

| Gap | Description | Priority |
|-----|-------------|----------|
| **Vendor Extract Format** | Need consistent intermediate Excel format for Arriba to upload | HIGH |
| **Excel Calculator Workbook** | Master workbook with macros for one-click calculation | HIGH |
| **Multi-Vendor Support** | Upload multiple vendor extracts and compare side-by-side | HIGH |
| **Customizable Formulas** | Adjustable Growth %, CPI %, Contract Term in calculator | MEDIUM |
| **TCO Output Format** | Final output must match Arriba's financial model format | HIGH |

**Desired Flow (To Build):**
```
Proposal PDF → JSON → Vendor Extract Excel (consistent format)
                         ↓
Multiple Vendor Extracts → Upload to Calculator Workbook
                         ↓
One-Click Macro → Apply Growth/CPI Formulas
                         ↓
TCO Output (Multi-Vendor Comparison) → Drop into Arriba's Financial Model
```

### KEY INSIGHT

**We are 70% complete.** The extraction pipeline works perfectly. We just need to:
1. Modify output format (JSON → Vendor Extract Excel instead of direct TCO)
2. Create Calculator Workbook with macros
3. Update final TCO Output format for multi-vendor comparison

**Estimated Effort:** 20 hours total (2 days, 2 developers working in parallel)

---

## PAGE 2: 2-DAY WORK PLAN (10 HOURS PER DEVELOPER)

### DEVELOPER 1: Data Pipeline & Vendor Extract

**Total Time:** 10 hours over 2 days

| Time | Task | Deliverable | Hours |
|------|------|-------------|-------|
| **Day 1 AM** | Design Vendor Extract Excel schema with Dev 2 (joint meeting) | Agreed schema document | 1h |
| **Day 1** | Create `Vendor_Extract_Template.xlsx` with consistent structure | Template file | 2h |
| **Day 1** | Modify `json_to_excel_mapper.py` to output Vendor Extract format | Updated script | 2h |
| **Day 2 AM** | Test extraction for FIS, CSI, Jack Henry proposals | 3 sample vendor extract files | 2h |
| **Day 2** | Create documentation: schema, field mappings, usage guide | `Vendor_Extract_Guide.md` | 1.5h |
| **Day 2 PM** | Integration testing with Dev 2's calculator workbook | Verified end-to-end flow | 1.5h |

**Key Outputs:**
- `Templates/Vendor_Extract_Template.xlsx` - Standardized template
- Modified `scripts/json_to_vendor_extract.py` - Conversion script
- 3 sample vendor extract files (FIS, CSI, Jack Henry)
- Documentation for Arriba team

**Technical Approach:**
- Reuse existing `json_to_excel_mapper.py` logic (already has categorization)
- Change output format to simpler "Line Items" structure
- Remove complex formulas (those go in Calculator Workbook)
- Add metadata sheet (Vendor, Client, Proposal Date, Contract Term)

---

### DEVELOPER 2: Excel Calculator Workbook

**Total Time:** 10 hours over 2 days

| Time | Task | Deliverable | Hours |
|------|------|-------------|-------|
| **Day 1 AM** | Define Vendor Extract Excel schema with Dev 1 (joint meeting) | Agreed schema document | 1h |
| **Day 1** | Create `TCO_Calculator_Master.xlsm` structure (4 sheets) | Workbook skeleton | 1.5h |
| **Day 1** | Build Parameters sheet with adjustable inputs (Growth %, CPI %, Term) | Parameters sheet with validation | 1h |
| **Day 1** | Build formulas for monthly/annual calculations (Years 1-7) | Working formula layer | 2.5h |
| **Day 2 AM** | Create VBA macro for "Calculate TCO" button | Working macro | 2h |
| **Day 2** | Build TCO Output sheet (multi-vendor comparison format) | Final output sheet | 1h |
| **Day 2 PM** | Testing with Dev 1's sample vendor extracts & user guide | Final workbook + guide | 1.5h |

**Key Outputs:**
- `Templates/TCO_Calculator_Master.xlsm` - Calculator workbook with macros
- VBA code for one-click calculation
- User guide (embedded + PDF)
- Test validation report

**Technical Approach:**
- **Sheet 1 (Import Zone):** Paste vendor extract data here
- **Sheet 2 (Parameters):** Growth Rate %, CPI %, Contract Term (user adjustable)
- **Sheet 3+ (Vendor Calcs):** One sheet per vendor with formulas
- **Final Sheet (TCO Output):** Side-by-side vendor comparison
- **VBA Macro:** Read Import Zone → Apply formulas → Populate TCO Output

---

### JOINT ACTIVITIES (Both Developers)

| Time | Activity | Duration |
|------|----------|----------|
| **Day 1 - 9:00 AM** | Schema definition meeting (define data contract) | 1 hour |
| **Day 1 - 3:00 PM** | Mid-point sync (Dev 1 shares sample extract, Dev 2 tests import) | 30 min |
| **Day 2 - 2:00 PM** | Integration testing (full workflow end-to-end) | 1.5 hours |
| **Day 2 - 5:00 PM** | Final review & demo preparation | 30 min |

---

### DATA CONTRACT (To Define in Day 1 Meeting)

Both developers must agree on this before starting independent work:

#### Vendor Extract Excel Schema

**Sheet 1: Line Items**
- Column A: Solution Name
- Column B: Category (Required | Optional | Bundled | One-Time)
- Column C: Fee Type (Monthly F | Monthly V | Annual | One-Time)
- Column D: Per Unit Rate
- Column E: Volume/Quantity
- Column F: Unit Description
- Column G: Notes

**Sheet 2: Metadata**
- Vendor: FIS | CSI | Jack Henry | Other
- Client: [Client Name]
- Proposal Date: YYYY-MM-DD
- Contract Term: 5 | 7 | 10 years

#### Category Definitions
- **Required:** Core platform, mandatory modules
- **Optional:** Add-on features, optional modules
- **Bundled:** Package deals, bundled pricing
- **One-Time:** Implementation, setup, conversion fees

---

### SUCCESS CRITERIA (End of Day 2)

| Metric | Target | Verification |
|--------|--------|--------------|
| Vendor Extract Consistency | 100% schema match across vendors | Visual inspection of 3 sample files |
| Calculator Import Success | All 3 vendor extracts import without errors | Test in Excel |
| Formula Accuracy | Calculations match manual validation | Spot-check 5 line items |
| Macro Functionality | One-click execution, no errors | Test with all 3 vendors |
| Multi-Vendor Comparison | Side-by-side output with 3 vendors | Visual review of TCO Output |
| Documentation Complete | User can follow guide without help | Peer review |
| Manual Entry Reduction | 85-90% automation (Karishma's goal) | Time comparison test |

---

### GIT WORKFLOW (Simple)

**Branches:**
```
main
├── feature/vendor-extract-pipeline (Dev 1)
└── feature/excel-calculator (Dev 2)
```

**Day 1 End:**
- Both developers commit to their feature branches
- Push to remote

**Day 2 Mid-Point:**
- Dev 1 merges `feature/vendor-extract-pipeline` → `main`
- Dev 2 rebases on latest `main`, tests integration

**Day 2 End:**
- Dev 2 merges `feature/excel-calculator` → `main`
- Final testing on `main` branch

**Conflict Prevention:**
- Dev 1 owns: `scripts/`, `Templates/Vendor_Extract_Template.xlsx`
- Dev 2 owns: `Templates/TCO_Calculator_Master.xlsm`, user guides
- Shared: `requirements.txt` (coordinate before committing)

---

### DELIVERABLES SUMMARY

**From Dev 1:**
1. ✅ `Templates/Vendor_Extract_Template.xlsx`
2. ✅ `scripts/json_to_vendor_extract.py`
3. ✅ 3 sample vendor extract files
4. ✅ `docs/Vendor_Extract_Guide.md`

**From Dev 2:**
1. ✅ `Templates/TCO_Calculator_Master.xlsm`
2. ✅ VBA macro code
3. ✅ User guide (PDF + embedded)
4. ✅ Test validation report

**Integrated System:**
- ✅ Full workflow: Proposal → JSON → Vendor Extract → Calculator → TCO Output
- ✅ Multi-vendor comparison (3+ vendors)
- ✅ One-click automation
- ✅ 85-90% reduction in manual data entry

---

**END OF QUICK IMPLEMENTATION PLAN**
