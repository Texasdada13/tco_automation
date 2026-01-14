# TCO Automation - Gap Analysis

**Date:** 2026-01-13
**Purpose:** Compare client requirements vs. what has been built

---

## 📋 Client Problem Statement Summary

### **Core Requirements:**

1. **Automate extraction** from vendor proposals (PDF, Word, Excel) - FIS and JHA
2. **Standardize** different vendor formats into "apples-to-apples" structure
3. **Populate 5-year TCO template** automatically
4. **Excel/PDF output** in consistent format for upload to financial modeling
5. **Macros/formulas** to capture monthly and annual totals with a click
6. **Growth and CPI** built in with tweakable assumptions
7. **90% accuracy** - limit manual customization to 10-15%
8. **Clear traceability** for the client

### **Key Quote:**
> "Excel or PDF we can upload in a consistent format, plus some automation (macros/formulas with a click) to capture monthly and annual totals, with growth and CPI built in (with tweakable assumptions on our end)."

---

## ✅ What Has Been Built (Strengths)

### 1. **Extraction Pipeline** ✅ EXCELLENT
- ✅ `extraction/extract_proposal.py` - Main extraction script
- ✅ `extraction/extract_proposal_direct.py` - Direct PDF extraction
- ✅ `extraction/extract_proposal_hybrid.py` - Hybrid method
- ✅ AI-powered using Anthropic Claude API
- ✅ Successfully extracts from PDF proposals
- ✅ Works with FIS and CSI vendors

**Evidence:**
- Echelon Bank FIS: 22 items extracted
- Liberty Capital FIS: 30 items extracted
- Liberty Capital CSI: 38 items extracted

### 2. **Standardized Schema** ✅ EXCELLENT
- ✅ Universal 17-column format for all vendors
- ✅ Consistent fee types: Monthly F, Monthly V, Annual, One-Time
- ✅ Standardized categories across vendors
- ✅ Data dictionary for mappings

**Files:**
- `scripts/create_standardized_vendor_output.py`
- `data/templates/universal_schema.json`
- `data/dictionaries/Data_Dictionary/enum_mappings.json`

### 3. **Multi-Vendor Comparison** ✅ GOOD
- ✅ Side-by-side vendor comparison
- ✅ Summary sheet with TCO calculations
- ✅ Works for FIS vs CSI

**File:** `scripts/create_multi_vendor_comparison.py`

### 4. **Year-by-Year Projections** ✅ GOOD
- ✅ Supports Years 1, 2, 3, 5, 7 (extendable to 10)
- ✅ Growth rate support (20% default)
- ✅ Calculates annual costs with compounding

### 5. **Credit Detection** ✅ EXCELLENT
- ✅ Automatically detects missing credits in extractions
- ✅ Fixed critical $1.5M missing credit bug for Echelon FIS
- ✅ Properly handles negative values

### 6. **Documentation** ✅ EXCELLENT
- ✅ Comprehensive guides (13 user guides)
- ✅ Reference documentation (5 docs)
- ✅ Project documentation (15 docs)
- ✅ Well-organized structure

### 7. **Code Quality** ✅ EXCELLENT
- ✅ Clean, organized project structure
- ✅ 130+ files organized into logical folders
- ✅ Modular, maintainable code
- ✅ Version controlled with clean history

---

## ❌ Critical Gaps

### **GAP #1: Not Populating Client's ACTUAL TCO Template** ⚠️ CRITICAL

**Client Expects:**
> "Automatically populate the 5-year TCO template"

**What's Built:**
- Creates NEW standardized Excel files
- Does NOT populate their existing "Echelon_Primary TCO.xlsx" template
- Generates separate outputs instead of integrating with their model

**Impact:** 🔴 HIGH
- Client still needs to manually copy data from our output to their template
- Defeats the purpose of automation
- Still requires significant manual work

**Evidence:**
- Output files: `Echelon_Bank_FIS_Standardized_*.xlsx` (new files)
- No integration with client's existing TCO model
- WORKBOOK2 might be a template but unclear if it's THE client template

**What's Needed:**
1. Get actual "Echelon_Primary TCO.xlsx" from client
2. Build mapper to populate THAT specific template
3. Preserve their formulas, formatting, and structure
4. Only populate the data cells they need

---

### **GAP #2: No Excel Formulas - Values Only** ⚠️ CRITICAL

**Client Expects:**
> "macros/formulas with a click to capture monthly and annual totals, with growth and CPI built in (with tweakable assumptions on our end)"

**What's Built:**
- Python calculates values
- Writes **hardcoded numbers** to Excel
- No Excel formulas for recalculation
- Client can't tweak assumptions without re-running Python

**Code Evidence:**
```python
# scripts/create_standardized_vendor_output.py
year_costs[year] = self._calculate_annual_cost(...)
ws.cell(row, col).value = year_costs[1]  # ← HARDCODED VALUE
```

**Impact:** 🔴 HIGH
- Client can't adjust growth rates in Excel
- Can't tweak CPI assumptions
- No "what-if" analysis capability
- Must re-run Python script for any changes

**What's Needed:**
1. Replace hardcoded values with Excel formulas
2. Add parameter cells for growth rate, CPI, etc.
3. Make all calculations formula-based
4. Example: `=E7*12*(1+$B$1)^(YEAR-1)` instead of `180000`

---

### **GAP #3: No Macros or "Click" Automation** ⚠️ HIGH

**Client Expects:**
> "macros/formulas with a click"

**What's Built:**
- Command-line Python scripts only
- No Excel macros
- No "click to run" functionality
- Requires technical knowledge to run

**Impact:** 🔴 HIGH
- Not user-friendly for client
- Requires Python environment
- Can't be used by non-technical staff

**What's Needed:**
1. Excel VBA macros for automation
2. Buttons in Excel to trigger actions
3. OR: Simple web interface
4. OR: Excel add-in

---

### **GAP #4: CPI Not Explicitly Implemented** ⚠️ MEDIUM

**Client Expects:**
> "growth and CPI built in (with tweakable assumptions)"

**What's Built:**
- ✅ Growth rate: 20% default (can be adjusted in code)
- ❌ CPI: Referenced in WORKBOOK2 analysis but not implemented
- ❌ No separate CPI handling for later years

**Code Evidence:**
```python
# Only growth rate, no CPI distinction
annual_cost = monthly_fee * 12 * ((1 + self.growth_rate) ** (year_num - 1))
```

**Impact:** 🟡 MEDIUM
- Less accurate for multi-year projections
- Missing realistic inflation modeling

**What's Needed:**
1. Add CPI parameter (e.g., 2-3% starting Year 6)
2. Separate growth vs. inflation
3. Make both tweakable in Excel

---

### **GAP #5: No JHA (Jack Henry) Support Demonstrated** ⚠️ MEDIUM

**Client Expects:**
> "vendor proposals (FIS and JHA)"

**What's Built:**
- ✅ FIS extraction working (Echelon, Liberty Capital, FSB)
- ✅ CSI extraction working (Liberty Capital)
- ❌ No JHA extractions in sample data
- ⚠️ `extractors/jh_extractor.py` exists but may be empty/untested

**Impact:** 🟡 MEDIUM
- Can't compare FIS vs JHA as client requested
- Only half of requested vendors supported

**What's Needed:**
1. Get JHA proposal samples
2. Test/complete JHA extraction
3. Validate JHA standardized output

---

### **GAP #6: 5-Year vs. 7-Year Term** ⚠️ LOW

**Client Expects:**
> "5-year TCO template"

**What's Built:**
- Default: 7-year projections
- Supports up to 10 years
- Outputs Years 1, 2, 3, 5, 7

**Impact:** 🟢 LOW
- Easy to adjust
- Not a functional issue

**What's Needed:**
- Change default to 5 years
- Or make term configurable in output

---

### **GAP #7: No Upload/Import Mechanism** ⚠️ MEDIUM

**Client Expects:**
> "Excel or PDF we can upload in a consistent format"

**What's Built:**
- ❌ No upload interface
- ❌ No web UI
- ✅ Command-line only
- ✅ Consistent OUTPUT format

**Impact:** 🟡 MEDIUM
- Not as user-friendly as described
- Implies they wanted an interface to upload proposals

**What's Needed:**
1. Web interface for uploading proposals
2. OR: Excel-based interface
3. OR: Drag-and-drop folder watching

---

### **GAP #8: Traceability - No Page References** ⚠️ LOW

**Client Expects:**
> "clear traceability for the client"

**What's Built:**
- ✅ Notes column with extraction notes
- ✅ Confidence scores
- ❌ No page numbers from source PDF
- ❌ No direct link to proposal sections

**Impact:** 🟢 LOW
- Would be nice to have
- Not critical for functionality

**What's Needed:**
- Add page/section references in extraction
- Link each line item to proposal page

---

### **GAP #9: Accuracy Not Validated Against Client TCOs** ⚠️ HIGH

**Client Expects:**
> "goal is to limit manual customization to 10-15%"

**What's Built:**
- ✅ Gap analysis done (31% → 73% coverage for Echelon FIS)
- ❌ No validation against client's ACTUAL TCO
- ❌ No measurement of the 10-15% target
- ❌ No QA workflow comparing our output vs. their manual TCO

**Impact:** 🔴 HIGH
- Don't know if we're meeting the 90% accuracy goal
- Can't measure success

**What's Needed:**
1. Get client's manually-created TCO for Echelon/Liberty Capital
2. Compare line-by-line against our output
3. Measure accuracy percentage
4. Identify systematic gaps

---

### **GAP #10: No "Drop into Financial Modeling" Integration** ⚠️ CRITICAL

**Client Expects:**
> "structured so it can be dropped into our financial modeling"

**What's Built:**
- Creates standalone Excel files
- No integration with their financial modeling system
- Unknown what their "financial modeling" tool is

**Impact:** 🔴 HIGH
- May require additional transformation
- Client might use different software (Excel, specific models, databases)

**What's Needed:**
1. Understand their financial modeling workflow
2. Ensure output format matches their input requirements
3. Test actual "drop in" process

---

## 📊 Gap Summary Table

| Gap | Priority | Status | Impact |
|-----|----------|--------|--------|
| #1: Not populating client's actual TCO template | 🔴 CRITICAL | ❌ Missing | HIGH |
| #2: No Excel formulas (values only) | 🔴 CRITICAL | ❌ Missing | HIGH |
| #3: No macros or "click" automation | 🔴 HIGH | ❌ Missing | HIGH |
| #4: CPI not implemented | 🟡 MEDIUM | ⚠️ Partial | MEDIUM |
| #5: No JHA support demonstrated | 🟡 MEDIUM | ⚠️ Partial | MEDIUM |
| #6: 5-year vs 7-year term | 🟢 LOW | ⚠️ Easy fix | LOW |
| #7: No upload interface | 🟡 MEDIUM | ❌ Missing | MEDIUM |
| #8: No page references | 🟢 LOW | ⚠️ Partial | LOW |
| #9: Accuracy not validated | 🔴 HIGH | ❌ Missing | HIGH |
| #10: No financial modeling integration | 🔴 CRITICAL | ❌ Unknown | HIGH |

---

## 🎯 What's Working Well (Don't Change)

1. ✅ **Extraction quality** - Successfully extracts complex proposals
2. ✅ **Standardization** - Universal schema works across vendors
3. ✅ **Credit detection** - Catches missing credits automatically
4. ✅ **Multi-vendor comparison** - Good side-by-side analysis
5. ✅ **Code organization** - Professional, maintainable structure
6. ✅ **Documentation** - Comprehensive guides

---

## 🔧 Recommended Actions (Priority Order)

### **Phase 1: Critical Gaps (Must Fix)**

1. **Get Client's Actual TCO Template**
   - Request "Echelon_Primary TCO.xlsx" from client
   - Understand their exact structure and formulas
   - Map our extraction to their template

2. **Add Excel Formulas (Not Values)**
   - Rewrite standardized output to use formulas
   - Add parameter cells for growth rate, CPI
   - Make all year projections formula-based
   - Example structure:
     ```
     B1: Growth Rate (20%)
     B2: CPI Rate (2.5%)
     B3: CPI Start Year (6)

     Year 1: =E7*12
     Year 2: =E7*12*(1+$B$1)
     Year 6: =E7*12*(1+$B$1)^5*(1+$B$2)
     ```

3. **Validate Accuracy**
   - Get client's manually-created TCOs
   - Compare line-by-line
   - Measure % accuracy
   - Fix systematic issues

4. **Template Population Script**
   - Build script to populate THEIR template
   - Preserve their formulas and formatting
   - Only update data cells

### **Phase 2: High Priority**

5. **Add Excel Macros**
   - Create VBA macros for automation
   - Add buttons: "Load Proposal", "Calculate TCO", "Compare Vendors"
   - Make user-friendly

6. **Implement CPI**
   - Add explicit CPI handling
   - Separate from growth rate
   - Apply starting Year 6-7 (typical)

7. **Test JHA Support**
   - Get JHA proposal samples
   - Test extraction
   - Validate output

### **Phase 3: Medium Priority**

8. **Add Upload Interface** (Optional)
   - Simple web UI or Excel interface
   - Drag-and-drop proposals
   - Click to generate TCO

9. **5-Year Default**
   - Change default from 7 to 5 years
   - Make configurable

### **Phase 4: Nice to Have**

10. **Add Page References**
    - Link line items to proposal pages
    - Improve traceability

---

## 💡 Key Insight

**The current solution is 70% complete:**
- ✅ Extraction: Working well
- ✅ Standardization: Excellent
- ✅ Comparison: Good
- ❌ Integration: Missing
- ❌ Interactivity: Missing
- ❌ Validation: Not done

**Core Issue:**
The system creates **NEW standardized files** but the client needs us to **POPULATE THEIR EXISTING TCO TEMPLATE**. It's like building a great data extraction pipeline but not connecting it to the final destination.

**Analogy:**
- We built: "Extract proposal → Create standardized Excel file"
- Client wants: "Extract proposal → Populate MY TCO template with formulas → I can tweak and use"

---

## 📋 Questions for Client

1. **Can you provide your actual TCO template?**
   - "Echelon_Primary TCO.xlsx" or similar
   - We need to see the exact format you use

2. **What is your "financial modeling" system?**
   - Is it Excel-based?
   - Do you use specific software?
   - What format do you need?

3. **Do you have a manually-created TCO we can validate against?**
   - To measure our 90% accuracy goal
   - To identify gaps

4. **What assumptions do you typically tweak?**
   - Growth rate?
   - CPI?
   - Volume/quantities?
   - This helps us make the right things formula-based

5. **Do you have Jack Henry (JHA) proposal samples?**
   - To test and validate JHA extraction

6. **How do you envision "clicking" to run automation?**
   - Excel macro button?
   - Web interface?
   - Desktop application?

---

## ✅ Success Criteria (Not Yet Met)

**Client's Goal:**
> "limit manual customization to 10-15%"

**To Achieve This:**
1. ✅ Extract 90% of line items correctly (close to achieved)
2. ❌ Populate THEIR template (not built)
3. ❌ Use formulas for tweakability (not built)
4. ❌ Validate against their actual TCO (not done)
5. ❌ Make it "click to run" easy (not built)

**Current State:** ~60-70% of full requirements met

---

**Last Updated:** 2026-01-13
**Next Steps:** Address Critical Gaps in Phase 1
