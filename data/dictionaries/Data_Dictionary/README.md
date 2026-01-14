# TCO Data Dictionary - README

**Version:** 1.0
**Date:** 2025-12-08
**Purpose:** Documentation for TCO Excel data structures, schemas, and mappings

---

## Overview

This folder contains comprehensive documentation for the TCO (Total Cost of Ownership) automation system. The data dictionary defines all fields, transformations, and business rules used to convert vendor proposal JSON data into standardized Excel TCO reports.

---

## Files in This Directory

### 1. **tco_workbook2_analysis.md**
**Purpose:** Complete analysis of the client's existing TCO template (WORKBOOK2.xlsx)

**Contents:**
- Sheet-by-sheet structure breakdown
- Column mappings and data types
- Row categories and sections
- Business rules and formulas
- Design principles for new template

**Use This For:**
- Understanding the client's expected TCO format
- Reference when designing new templates
- Mapping specifications

---

### 2. **client_data_dictionary.json**
**Purpose:** Machine-readable field specifications for all TCO data elements

**Structure:**
```json
{
  "metadata": {...},
  "fields": [
    {
      "field_name": "fee_type",
      "display_name": "Fee Type",
      "datatype": "enum",
      "allowed_values": ["Monthly F", "Monthly V", "Annual", "One-Time"],
      "required": true,
      "description": "...",
      "validation_rules": "...",
      "business_meaning": "..."
    },
    ...
  ],
  "derived_fields": [...],
  "aggregations": [...],
  "validation_rules": {...},
  "business_rules": {...}
}
```

**Use This For:**
- Field-level validation
- Understanding data types and constraints
- Building transformation scripts
- Database schema design

---

### 3. **derived_schema.json**
**Purpose:** Machine-readable schema for the NEW TCO Excel template

**Structure:**
```json
{
  "excel_template": {
    "sheets": [
      {
        "sheet_name": "Line_Items",
        "columns": [
          {
            "column": "B",
            "field_name": "fee_type",
            "datatype": "enum",
            "width": 12,
            "validation": "List",
            "formula": "..."
          },
          ...
        ]
      },
      ...
    ]
  },
  "data_flow": {...},
  "validation_rules": {...},
  "formatting_standards": {...}
}
```

**Use This For:**
- Programmatically generating Excel templates
- Understanding column mappings
- Formula specifications
- Formatting standards

---

### 4. **enum_mappings.json**
**Purpose:** Normalization mappings for all enum fields

**Structure:**
```json
{
  "fee_type_mappings": {
    "standard_values": ["Monthly F", "Monthly V", "Annual", "One-Time"],
    "mappings": {
      "Monthly F": ["Monthly F", "Monthly Fixed", "monthly_f", ...]
    }
  },
  "category_mappings": {...},
  "vendor_mappings": {...},
  "transformation_functions": {...}
}
```

**Use This For:**
- Normalizing vendor proposal data
- Handling variations in terminology
- Building data cleaning scripts
- Extending to new vendors

---

## How the Schema Was Derived

### Step 1: Analysis of Existing Template (WORKBOOK2.xlsx)
- Opened and analyzed all sheets
- Documented column headers, data types, formulas
- Identified business rules (e.g., One-Time fees only in Year 1)
- Mapped row sections (Bundle, Required, Optional, etc.)
- Extracted CPI calculations and aggregation logic

### Step 2: Analysis of JSON Extraction Files
- Reviewed liberty_extraction_ai.json, csi_extraction_ai.json
- Identified common fields across vendors
- Noted variations (monthly_fee vs per_unit_rate)
- Found special cases (items with both monthly + one-time fees)
- Documented confidence scores and extraction notes

### Step 3: Gap Analysis
- Compared JSON structure to Excel requirements
- Identified missing fields (third_party, optional flags)
- Determined transformation rules
- Defined splitting logic for complex items

### Step 4: Schema Design
- Created normalized field list
- Defined enum values and mappings
- Specified validation rules
- Documented business logic
- Designed new Excel template structure

### Step 5: Validation
- Cross-referenced with actual proposal documents
- Validated formulas match client expectations
- Tested edge cases (credits, zero costs, missing data)
- Verified sorting and grouping logic

---

## Assumptions Made

1. **Contract Term:** Default 7 years (configurable in Metadata sheet)

2. **CPI (Cost Price Index):** Default 2% annual increase for recurring fees

3. **Growth Rate:** Not applied in new template (can be added)

4. **Bundle Identification:**
   - Items with category="Core" are Bundle items
   - Items with solution_name containing "HORIZON" or "Bundle" are Bundle items

5. **Third-Party Identification:**
   - Explicit `third_party` field in JSON
   - OR solution_name contains known third-party vendor names

6. **Optional Flag:**
   - Explicit `optional` field in JSON
   - OR solution_name contains "Optional" keyword

7. **Fee Type Normalization:**
   - "Monthly F" = Fixed monthly fee (consistent cost regardless of usage)
   - "Monthly V" = Variable monthly fee (depends on transaction volume)
   - "Annual" = Billed once per year
   - "One-Time" = Implementation/setup fee (Year 1 only)

8. **Item Splitting:**
   - If JSON item has both `monthly_fee > 0` AND `one_time_fee > 0`, split into 2 rows
   - Monthly row keeps original solution_name
   - One-time row appends " - Implementation Fee" to solution_name

9. **Missing Data Handling:**
   - Missing `fee_type` → default to "Monthly F"
   - Missing `category` → default to "Other"
   - Missing `third_party` → default to FALSE
   - Missing `optional` → default to FALSE
   - Missing `average_monthly_qty` for "Monthly V" → default to 1 and flag issue

10. **Negative Costs:**
    - Allowed for One-Time fees (represents credits)
    - Flagged for review if in Monthly/Annual fees

---

## How to Use the Mapping Script

### Basic Usage
```bash
python scripts/json_to_excel_mapper.py "Extracted JSON/vendor_extraction_ai.json"
```

### Specify Output File
```bash
python scripts/json_to_excel_mapper.py "Extracted JSON/vendor_extraction_ai.json" "TCO Output/Custom_Name.xlsx"
```

### What the Script Does
1. Loads and validates JSON file
2. Normalizes all enum fields using enum_mappings.json
3. Splits items with both monthly + one-time fees
4. Transforms to Excel row format
5. Sorts by optional, third_party, fee_type, category
6. Writes to Line_Items sheet with formulas
7. Populates Metadata sheet
8. Generates Data_Quality report
9. Saves to TCO Output folder

### Output
- **Excel file:** `TCO Output/{Vendor}_TCO_New_{Date}.xlsx`
- **Log file:** `logs/mapping_errors.log`
- **Console output:** Transformation summary

---

## Validation Logic

### Pre-Ingestion Validation
- JSON structure has required top-level fields (vendor, client, line_items)
- `line_items` is non-empty array
- Each line item has `solution_name` and pricing field

### Post-Ingestion Validation
- All `fee_type` values are valid enums
- Monthly V items have `average_monthly_qty > 0`
- One-Time items only have cost in Year 1
- Confidence scores are 0.0-1.0
- Required fields are non-null

### Data Quality Checks
The script automatically flags:
- Low confidence scores (< 0.80)
- Missing required fields
- Invalid enum values
- Zero cost items
- Negative costs (except One-Time)
- Missing quantities for variable fees

All flagged items appear in the Data_Quality sheet.

---

## Extending the Schema

### Adding a New Category
1. Edit `enum_mappings.json`
2. Add to `category_mappings.mappings`
3. Update `Data_Dictionary/client_data_dictionary.json` field definition
4. Re-run mapping script

### Adding a New Vendor
1. Edit `enum_mappings.json`
2. Add to `vendor_mappings.mappings`
3. No code changes needed

### Adding a New Fee Type
1. Edit `enum_mappings.json` → `fee_type_mappings`
2. Update Excel template Enums sheet
3. Add calculation logic in `json_to_excel_mapper.py` if needed

### Supporting 10-Year Contracts
1. Edit `Templates/New_TCO_Excel_v1.xlsx`
2. Add Year 8, 9, 10 columns (S, T, U)
3. Extend formulas in `json_to_excel_mapper.py`
4. Update `derived_schema.json`

---

## Common Issues and Solutions

### Issue: "Invalid JSON: missing 'line_items'"
**Solution:** Ensure JSON has top-level `line_items` array

### Issue: "Could not normalize fee_type 'XYZ'"
**Solution:** Add variant to `enum_mappings.json` → `fee_type_mappings`

### Issue: "Monthly V requires average_monthly_qty"
**Solution:** Add `average_monthly_qty` field to JSON or allow default to 1

### Issue: Items not splitting correctly
**Solution:** Verify both `monthly_fee` and `one_time_fee` are > 0

### Issue: Summary formulas not calculating
**Solution:** Ensure Excel is set to auto-calculate (File → Options → Formulas)

---

## File Naming Conventions

### JSON Extraction Files
- Format: `{vendor}_extraction_ai.json`
- Location: `Extracted JSON/`
- Examples: `liberty_extraction_ai.json`, `csi_extraction_ai.json`

### Excel TCO Output Files
- Format: `{Vendor}_TCO_New_{YYYYMMDD}.xlsx`
- Location: `TCO Output/`
- Examples: `FIS_TCO_New_20251208.xlsx`

---

## Support and Contact

**Issues:** Log in `logs/mapping_errors.log`
**Documentation:** This folder
**Source Code:** `scripts/json_to_excel_mapper.py`

---

**Document Version:** 1.0
**Last Updated:** 2025-12-08
**Maintained By:** TCO Automation Project
