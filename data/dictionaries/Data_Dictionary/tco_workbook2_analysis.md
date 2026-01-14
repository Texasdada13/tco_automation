# WORKBOOK2.xlsx - Complete Structure Analysis

**Document Purpose:** Total Cost of Ownership (TCO) analysis for financial institution core banking system proposals

**Analysis Date:** 2025-12-08

**Source Workbook:** WORKBOOK2.xlsx (Client Template)

---

## Executive Summary

WORKBOOK2.xlsx is a multi-sheet Excel template designed to calculate and compare Total Cost of Ownership (TCO) for banking system proposals from vendors like FIS and Jack Henry. The workbook supports:

- 7-10 year cost projections with annual growth factors
- Multiple fee types (Monthly Fixed, Monthly Variable, Annual, One-Time)
- Vendor product bundling vs. unbundled pricing
- Third-party solution integration costs
- Implementation fees and credits
- Required vs. optional solutions

---

## Sheet Structure

### 1. **Control Sheet**
**Purpose:** Dropdown list values for data validation

**Key Values:**
- Row 4: `Monthly F` (Monthly Fixed)
- Row 5: `Monthly V` (Monthly Variable)
- Row 6: `Annual`
- Row 7: `One-Time`

**Business Logic:** Defines valid fee types used throughout the workbook

---

### 2. **DeleteThisPageThenSave Sheet**
**Purpose:** Metadata for file naming

**Fields:**
- B2: `OriginalFileName`
- C2: `Echelon_Primary_TCO_` (base filename)

**Usage:** Template instruction sheet, removed before delivery

---

### 3. **Confidentiality & Non-Disclosure Sheet**
**Purpose:** Legal disclaimer page

**Content:** Standard confidentiality agreement text

**Usage:** First page in client deliverable

---

### 4. **Line Items Sheet** ⭐ **PRIMARY DATA SHEET**
**Purpose:** Detailed line-by-line pricing breakdown for all solutions

**Dimensions:** 164 rows × 123 columns (B through DS)

**Header Structure:**
- **Row 2:** Contract parameters (Years, Growth rate)
- **Row 4:** Primary column headers
- **Row 5:** Sub-headers (detailed field names)
- **Row 6+:** Data rows organized by categories

---

## Line Items Sheet - Detailed Column Mapping

### Core Identification Columns

| Column | Header | Data Type | Description | Business Rules |
|--------|--------|-----------|-------------|----------------|
| **B** | Type (Monthly/Annual) | Enum | Fee type | Values: Monthly F, Monthly V, Annual, One-Time |
| **C** | Proposal Date | Text | Proposal version identifier | Format: "Proposal\n(MM/YYYY)" |
| **D** | Average Monthly QTY | Number | Average monthly quantity | Used for variable fee calculations |
| **O** | Solution Name/Description | Text | Product/service name | Primary identifier |
| **P** | Category | Text | Product category | Examples: Core, Digital, EFT, Risk |
| **Q** | Per Unit Rate | Currency | Unit price | Format: USD $X,XXX.XX |

### Quantity Projection Columns

| Column Range | Header Pattern | Data Type | Description |
|--------------|----------------|-----------|-------------|
| **E-N** | Year 1-10 Quantity | Number | Projected quantities per year with growth |

### Cost Projection Columns

| Column Range | Header Pattern | Data Type | Description |
|--------------|----------------|-----------|-------------|
| **R** | Year 1 Monthly Cost | Currency | Month 1 cost |
| **S-AB** | Year 1-10 Cost | Currency | Annual costs per year |
| **AC-AL** | Year 1-10 CPI | Percentage | Cost increase index |

### Additional Columns (Vendor-Specific)

**FIS Columns (B-AB):** Standard pricing structure
**Jack Henry Columns (AM-DS):** Mirror structure for comparison

---

## Line Items Sheet - Row Categories

### Section 1: Bundle Products (Rows 7-20)
**Header Row:** 6
**Category:** "Recurring Monthly and Annual Fees - Bundle FIS products"
**Fee Types:** Primarily Monthly F
**Description:** Core bundled solutions (typically Core Banking + essential modules)
**Business Rules:**
- Usually includes HORIZON core system
- Bundled pricing = single monthly fee for multiple components
- Cannot be unbundled without price changes

### Section 2: Non-Bundle Required - FIS (Rows 22-54)
**Header Row:** 21
**Category:** "Recurring Monthly and Annual Fees - Non-Bundle REQUIRED FIS products"
**Fee Types:** Monthly F, Monthly V, Annual
**Description:** Essential FIS solutions required for operations
**Business Rules:**
- Must be implemented for full functionality
- Individually priced
- Can be variable or fixed cost

### Section 3: Non-Bundle Required - Third Party (Rows 55-84)
**Header Row:** 55
**Category:** "Recurring Monthly and Annual Fees - Non-Bundle REQUIRED Third Parties"
**Fee Types:** Monthly F, Monthly V, Annual, One-Time
**Description:** Required third-party integrations
**Business Rules:**
- Paid to third-party vendors
- Integration required for compliance/operations
- May include one-time setup fees

### Section 4: Implementation & One-Time Fees - FIS (Rows 86-109)
**Header Row:** 86
**Category:** "Implementation Credits and One time fees (FIS ONLY)"
**Fee Types:** One-Time
**Description:** Implementation, conversion, and setup fees
**Business Rules:**
- Charged once (Year 1)
- May include negative values (credits)
- Critical for cash flow analysis

### Section 5: Implementation & One-Time Fees - Third Party (Rows 110-118)
**Header Row:** 110
**Category:** "Implementation/Deconversion/Credits (Third Party)"
**Fee Types:** One-Time
**Description:** Third-party setup costs
**Business Rules:**
- Year 1 only
- Separate from ongoing fees

### Section 6: Non-Bundle Optional - FIS (Rows 121-129)
**Header Row:** 121
**Category:** "Recurring Monthly and Annual Fees - Non-Bundle Optional FIS Solutions"
**Fee Types:** Monthly F, Monthly V
**Description:** Optional enhancements/add-ons
**Business Rules:**
- Not required for core operations
- Can be added/removed during contract
- Excluded from base TCO comparison

### Section 7: Non-Bundle Optional - Third Party (Rows 130+)
**Header Row:** 130
**Category:** "Recurring Monthly and Annual Fees - Optional Third Parties"
**Fee Types:** Various
**Description:** Optional third-party solutions

---

## Years 1-7 Sheet

**Purpose:** Annual cost summary by category

**Structure:**
- Row 4: Year headers (Year 1 through Year 7)
- Row 5+: Category summaries

**Key Metrics:**
- Required Annual Fees
- Optional Annual Fees
- One-Time Fees
- Total Annual Cost
- Cumulative TCO

**Data Source:** Calculated from Line Items sheet

---

## Summary Sheet

**Purpose:** Executive-level TCO comparison

**Structure:**
- Columns A-D: FIS totals
- Columns E-G: Jack Henry totals

**Key Metrics:**
- Bundle FIS Products (7-year total)
- Non-Bundle Required FIS (7-year total)
- Non-Bundle Required Third-Party (7-year total)
- One-Time Fees
- Total 7-Year TCO
- Monthly Average Cost

**Formulas:** All values calculated using SUM() from Line Items sheet specific ranges

---

## Data Type Reference

### Enum: Fee Type
- **Monthly F** = Monthly Fixed Fee (consistent regardless of usage)
- **Monthly V** = Monthly Variable Fee (depends on transaction volume/usage)
- **Annual** = Annual Fee (billed once per year)
- **One-Time** = Implementation/setup fee (Year 1 only)

### Currency Format
- USD with 2 decimal places
- Example: `$16,792.00`
- Negative values allowed for credits: `($10,000.00)`

### Percentage Format
- Decimal representation
- Example: 0.02 = 2% growth
- CPI typically 0.02-0.05 (2-5% annual increase)

### Text Fields
- **Solution Name:** Free text, typically 50-200 characters
- **Category:** Predefined categories (Core, Digital, EFT, Risk, Treasury, etc.)
- **Proposal Date:** Format MM/YYYY in parentheses

---

## Business Rules & Validation

### 1. Fee Type Validation
- Column B must contain only: Monthly F, Monthly V, Annual, One-Time
- Empty cells allowed (indicates row not used)

### 2. Cost Calculations
- **Monthly F:** `Cost = Per Unit Rate × 12`
- **Monthly V:** `Cost = Per Unit Rate × Average Monthly QTY × 12`
- **Annual:** `Cost = Per Unit Rate`
- **One-Time:** `Cost = Per Unit Rate` (Year 1 only)

### 3. Growth Factor
- Row 3, Column D contains growth rate (default: 0.2 = 20%)
- Applied to quantity projections: `Year N Qty = Year 1 Qty × (1 + growth)^(N-1)`

### 4. Required vs Optional
- **Required items:** Included in TCO comparison
- **Optional items:** Shown separately, not included in base TCO
- Separation by row section (see Row Categories above)

### 5. Vendor vs Third-Party
- **Vendor (FIS/Jack Henry):** Primary contract party
- **Third-Party:** Separate vendor, different payment terms
- Critical for cash flow and contract management

---

## Formula Patterns

### Cost Calculation (Example: Cell S7 - Year 1 Cost)
```excel
=IF(B7="Monthly F", Q7*12,
   IF(B7="Monthly V", Q7*D7*12,
      IF(B7="Annual", Q7,
         IF(B7="One-Time", Q7, 0))))
```

### Multi-Year Projection with CPI (Example: Cell T7 - Year 2 Cost)
```excel
=S7 * (1 + AC7)
```

### Summary Totals (Example: Summary Sheet C3)
```excel
=SUM('Line Items'!AN7:AN20)
```

---

## JSON Data Extraction Patterns

Based on analysis of JSON extraction files (liberty_extraction_ai.json, csi_extraction_ai.json):

### JSON Structure
```json
{
  "vendor": "FIS",
  "client": "Liberty Capital Bank",
  "contract_term": 7,
  "line_items": [
    {
      "solution_name": "Core: HORIZON",
      "fee_type": "Monthly F",
      "category": "Existing Service - Core",
      "monthly_fee": 16792.0,
      "one_time_fee": 0.0,
      "per_unit_rate": 0.0,
      "third_party": false,
      "optional": false,
      "overall_confidence": 0.98
    }
  ]
}
```

### Field Mapping JSON → Excel

| JSON Field | Excel Column | Transformation |
|------------|--------------|----------------|
| `fee_type` | B | Direct mapping |
| `solution_name` | O | Direct mapping |
| `category` | P | Direct mapping |
| `per_unit_rate` | Q | If monthly_fee > 0, use monthly_fee; else per_unit_rate |
| `monthly_fee` | Q | Convert to per unit rate (see rules) |
| `one_time_fee` | Q | For One-Time fee rows |
| `third_party` | Row Section | Determines row placement |
| `optional` | Row Section | Required (rows 22-84) vs Optional (rows 121+) |

---

## Section Assignment Logic

Based on JSON fields `third_party`, `optional`, and `fee_type`:

| third_party | optional | fee_type | Excel Section | Row Range |
|-------------|----------|----------|---------------|-----------|
| false | false | Monthly/Annual | Non-Bundle Required - FIS | 22-54 |
| true | false | Monthly/Annual | Non-Bundle Required - Third Party | 55-84 |
| false | false | One-Time | Implementation FIS | 86-109 |
| true | false | One-Time | Implementation Third Party | 110-118 |
| false | true | Monthly/Annual | Optional FIS | 121-129 |
| true | true | Monthly/Annual | Optional Third Party | 130+ |

**Special Case:** `category` contains "Core" or "Bundle" → Bundle section (rows 7-20)

---

## Design Principles for New Excel Template

### 1. Professional Finance Format
- Clean, sans-serif font (Calibri or Arial)
- Currency formatting with thousand separators
- Subtle gridlines, freeze panes at header row
- Conditional formatting for negative values (red)

### 2. Logical Column Organization
- Identification fields first (Fee Type, Solution Name, Category)
- Pricing fields grouped (Per Unit Rate, Year costs)
- Metadata fields last (Confidence scores, notes)

### 3. Sheet Structure
- **Line Items:** Primary data sheet (all line item details)
- **Summary:** Executive-level aggregations
- **Metadata:** Proposal information, contract terms
- **Validation:** Dropdown lists for data entry

### 4. Formula Best Practices
- Named ranges for key parameters (contract_years, growth_rate)
- Consistent formula structure across rows
- Clear error handling (#N/A for incomplete data)

### 5. Data Validation
- Dropdowns for fee_type (from Control sheet equivalent)
- Number ranges for confidence scores (0.0-1.0)
- Required fields marked with bold headers

---

## Assumptions & Clarifications

1. **Contract Term:** Default 7 years, configurable
2. **Growth Rate:** Default 20% annually, applied to variable quantities
3. **CPI (Cost Per Increase):** Assumed 2-5% annually for recurring fees
4. **Bundle Identification:** Based on `category` field containing keywords "Core", "Bundle", "HORIZON"
5. **Third-Party Flag:** Explicit field in JSON, determines payment routing
6. **Optional Flag:** Determines inclusion in base TCO calculation
7. **Fee Type Normalization:**
   - JSON "Monthly F" = Excel "Monthly F"
   - JSON "Monthly V" = Excel "Monthly V"
   - JSON "Annual" = Excel "Annual"
   - JSON "One-Time" = Excel "One-Time"

---

## Known Limitations & Edge Cases

1. **Items with Both Monthly and One-Time Fees:**
   - JSON may have both `monthly_fee` and `one_time_fee` > 0
   - Solution: Split into two Excel rows (implemented in populate_tco_workbook.py)

2. **Missing Quantities for Variable Fees:**
   - Monthly V requires quantity, but JSON may not have it
   - Solution: Use default quantity of 1 or mark as incomplete

3. **Category Normalization:**
   - JSON categories may not match Excel standard categories
   - Solution: Enum mapping table required

4. **Multi-Vendor Comparisons:**
   - Current template supports FIS vs Jack Henry side-by-side
   - New template should support N vendors

5. **Year Range Flexibility:**
   - Template hardcoded for 7 years
   - New template should support configurable term (5-10 years)

---

## Next Steps for New Excel Template Design

1. **Simplify Column Structure:**
   - Reduce redundancy (remove Year 2-10 quantity columns if growth is auto-calculated)
   - Add explicit "Third Party" boolean column
   - Add explicit "Optional" boolean column
   - Add "Confidence Score" column for data quality tracking

2. **Enhance Summary Sheet:**
   - Add vendor comparison charts
   - Include TCO difference calculations
   - Add sensitivity analysis (what-if scenarios)

3. **Add Data Quality Sheet:**
   - Show items with low confidence scores
   - Flag incomplete data
   - Validation error log

4. **Improve Metadata Sheet:**
   - Proposal details (date, version, prepared by)
   - Contract terms (years, growth assumptions, CPI)
   - Extraction metadata (source file, extraction date, model used)

5. **Create Validation Sheet:**
   - Enum lists for Fee Type, Category
   - Configurable parameters (growth rate, CPI, contract term)
   - Vendor information

---

## Glossary

- **TCO:** Total Cost of Ownership - cumulative cost over contract term
- **Bundle:** Group of products sold as package deal
- **CPI:** Cost Price Index (inflation adjustment)
- **FIS:** Fidelity Information Services (major core banking vendor)
- **Jack Henry:** Major core banking vendor (competitor to FIS)
- **Core Banking:** Central system managing accounts, transactions, loans
- **EFT:** Electronic Funds Transfer
- **Digital Banking:** Online/mobile banking solutions
- **Third Party:** External vendor integrated with core system
- **Implementation Fee:** One-time cost for system setup/conversion
- **Per Unit Rate:** Price per transaction/account/user
- **Monthly F:** Fixed monthly fee regardless of usage
- **Monthly V:** Variable monthly fee based on usage/volume

---

**Document Version:** 1.0
**Last Updated:** 2025-12-08
**Author:** TCO Automation Project
**Status:** Complete
