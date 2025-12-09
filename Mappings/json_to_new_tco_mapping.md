# JSON to New TCO Excel Mapping Specification

**Version:** 1.0
**Date:** 2025-12-08
**Purpose:** Complete mapping specification from extracted JSON to New_TCO_Excel_v1.xlsx

---

## Overview

This document defines the exact transformation rules for converting extracted JSON data (from proposals) into the New TCO Excel format. The mapping handles:

- Field-level transformations
- Enum normalization
- Item splitting (monthly + one-time fees)
- Formula calculations
- Data validation
- Error handling

---

## JSON Input Structure

### Top-Level Fields

| JSON Path | Excel Destination | Transformation |
|-----------|-------------------|----------------|
| `$.vendor` | Metadata!B2 | Direct mapping, normalize vendor name |
| `$.client` | Metadata!B3 | Direct mapping |
| `$.proposal_type` | Metadata!B4 | Normalize using proposal_type_mappings |
| `$.document_date` | Metadata!B5 | Parse date, format as MM/DD/YYYY |
| `$.contract_term` | Metadata!B6 | Direct mapping (integer) |
| `$.acquisition_target` | Metadata!B13 (new) | Direct mapping if present |
| `$.extraction_metadata.extraction_date` | Metadata!B10 | Format as datetime |
| `$.extraction_metadata.model` | Metadata!B11 | Direct mapping |
| `$.extraction_metadata.source_file` | Metadata!B12 | Extract filename only |

### Line Items Array

**JSON Path:** `$.line_items[*]`
**Excel Destination:** Line_Items sheet, rows 2+

---

## Line Item Field Mappings

### Column A: Row ID
- **Source:** Auto-generated
- **Type:** Integer
- **Logic:** Sequential numbering starting from 1
- **Excel Formula:** None (static value)

### Column B: Fee Type
- **Source:** `$.fee_type`
- **Type:** Enum
- **Logic:** Normalize using `enum_mappings.json -> fee_type_mappings`
- **Allowed Values:** `Monthly F`, `Monthly V`, `Annual`, `One-Time`
- **Transformation:**
  ```python
  normalized = normalize_fee_type(json_value)
  # Maps "Monthly Fixed" → "Monthly F"
  # Maps "monthly_v" → "Monthly V"
  # Maps "OneTime" → "One-Time"
  ```
- **Validation:** Must be one of the 4 allowed values
- **Default:** `Monthly F` (if cannot be normalized)

### Column C: Solution Name
- **Source:** `$.solution_name`
- **Type:** String
- **Logic:** Direct mapping, trim whitespace
- **Max Length:** 255 characters
- **Required:** Yes
- **Validation:** Non-empty string
- **Special Case:** If item is split (has both monthly + one-time), append `" - Implementation Fee"` to one-time version

**Example:**
```json
Input: {"solution_name": "IP: DirectLink Merchant (via RDC)", "monthly_fee": 3402.14, "one_time_fee": 21943}

Output (2 rows):
Row 1: "IP: DirectLink Merchant (via RDC)" (monthly)
Row 2: "IP: DirectLink Merchant (via RDC) - Implementation Fee" (one-time)
```

### Column D: Category
- **Source:** `$.category`
- **Type:** Enum
- **Logic:** Normalize using `enum_mappings.json -> category_mappings`
- **Allowed Values:** 14 standard categories (Core, Digital, EFT, etc.)
- **Transformation:**
  ```python
  normalized = normalize_category(json_value)
  # Maps "Existing Service - Core" → "Core"
  # Maps "Digital Banking" → "Digital"
  # Maps "Unknown Category" → "Other"
  ```
- **Fuzzy Matching:** If exact match not found, perform keyword search
- **Default:** `Other`

### Column E: Third Party
- **Source:** `$.third_party`
- **Type:** Boolean
- **Logic:** Normalize using `enum_mappings.json -> boolean_mappings`
- **Allowed Values:** `TRUE`, `FALSE`
- **Transformation:**
  ```python
  normalized = normalize_boolean(json_value)
  # Maps true, "yes", "Y", 1 → TRUE
  # Maps false, "no", "N", 0, null → FALSE
  ```
- **Required:** Yes
- **Default:** `FALSE`

### Column F: Optional
- **Source:** `$.optional`
- **Type:** Boolean
- **Logic:** Same as Third Party column
- **Required:** Yes
- **Default:** `FALSE`

### Column G: Per Unit Rate
- **Source:** Multiple possible sources
- **Type:** Currency (USD)
- **Format:** `$#,##0.00`
- **Logic:**
  ```python
  if fee_type == "One-Time" and one_time_fee > 0:
      per_unit_rate = one_time_fee
  elif monthly_fee > 0:
      per_unit_rate = monthly_fee
  elif per_unit_rate in json:
      per_unit_rate = json.per_unit_rate
  else:
      per_unit_rate = 0.0
  ```
- **Source Priority:**
  1. If One-Time row: use `$.one_time_fee`
  2. If Monthly row: use `$.monthly_fee`
  3. Else: use `$.per_unit_rate`
- **Validation:** Numeric, can be negative (credits)

### Column H: Unit Description
- **Source:** `$.unit_description`
- **Type:** String
- **Logic:** Direct mapping if present, else derive from fee_type
- **Transformation:**
  ```python
  if unit_description:
      return unit_description
  elif fee_type == "Monthly F":
      return "per month"
  elif fee_type == "Monthly V":
      return "per transaction"
  elif fee_type == "Annual":
      return "per year"
  elif fee_type == "One-Time":
      return "one-time"
  ```
- **Optional:** Yes

### Column I: Average Monthly Qty
- **Source:** `$.average_monthly_qty` or derived
- **Type:** Numeric
- **Format:** `#,##0`
- **Logic:**
  ```python
  if fee_type == "Monthly V":
      qty = json.get('average_monthly_qty', 1)
  else:
      qty = None  # Leave blank
  ```
- **Validation:** Required if fee_type = "Monthly V"
- **Default:** 1 (if Monthly V and not provided)

### Column J: Year 1 Monthly Cost
- **Source:** Calculated field
- **Type:** Currency
- **Format:** `$#,##0.00`
- **Excel Formula:**
  ```excel
  =IF(B{row}="Monthly F", G{row},
     IF(B{row}="Monthly V", G{row}*I{row},
        IF(B{row}="Annual", G{row}/12, 0)))
  ```
- **Logic:**
  - Monthly F: per_unit_rate
  - Monthly V: per_unit_rate × quantity
  - Annual: per_unit_rate ÷ 12
  - One-Time: 0

### Column K: Year 1 Annual Cost
- **Source:** Calculated field
- **Type:** Currency
- **Format:** `$#,##0.00`
- **Excel Formula:**
  ```excel
  =IF(B{row}="One-Time", G{row}, J{row}*12)
  ```
- **Logic:**
  - One-Time: per_unit_rate (charged once)
  - Other: monthly_cost × 12

### Columns L-Q: Year 2-7 Costs
- **Source:** Calculated fields
- **Type:** Currency
- **Format:** `$#,##0.00`
- **Excel Formula (Year 2, column L):**
  ```excel
  =IF(B{row}="One-Time", 0, K{row}*(1+Metadata!$B$8))
  ```
- **Logic:**
  - One-Time items: $0 for Years 2-7
  - Recurring items: Previous year × (1 + CPI rate)
- **Formula Pattern:**
  - Year 2 (L): `Year 1 × (1 + CPI)`
  - Year 3 (M): `Year 2 × (1 + CPI)`
  - Year 4 (N): `Year 3 × (1 + CPI)`
  - Year 5 (O): `Year 4 × (1 + CPI)`
  - Year 6 (P): `Year 5 × (1 + CPI)`
  - Year 7 (Q): `Year 6 × (1 + CPI)`

### Column R: Total 7-Year Cost
- **Source:** Calculated field
- **Type:** Currency
- **Format:** `$#,##0.00`
- **Excel Formula:**
  ```excel
  =SUM(K{row}:Q{row})
  ```
- **Logic:** Sum of Years 1-7

### Column S: Confidence Score
- **Source:** `$.overall_confidence`
- **Type:** Percentage
- **Format:** `0.00%`
- **Logic:** Direct mapping, convert to decimal (0.98 → 98%)
- **Validation:** Must be between 0.0 and 1.0
- **Optional:** Yes (can be blank)
- **Conditional Formatting:**
  - 0.00-0.69: Red background (low confidence)
  - 0.70-0.89: Yellow background (medium confidence)
  - 0.90-1.00: Green background (high confidence)

### Column T: Notes
- **Source:** `$.extraction_notes`
- **Type:** String
- **Max Length:** 500 characters
- **Logic:** Direct mapping
- **Optional:** Yes

---

## Item Splitting Logic

**Rule:** If a JSON line item has **both** `monthly_fee > 0` AND `one_time_fee > 0`, split into TWO Excel rows:

### Row 1: Monthly Fee Row
```python
{
    "fee_type": original_fee_type (e.g., "Monthly F"),
    "solution_name": original_solution_name,
    "per_unit_rate": monthly_fee,
    "category": original_category,
    # ... other fields unchanged
}
```

### Row 2: One-Time Fee Row
```python
{
    "fee_type": "One-Time",
    "solution_name": f"{original_solution_name} - Implementation Fee",
    "per_unit_rate": one_time_fee,
    "category": original_category,
    # ... other fields unchanged
}
```

### Example

**Input JSON:**
```json
{
  "solution_name": "HORIZON: Conditional Processing",
  "fee_type": "Monthly F",
  "category": "Core",
  "monthly_fee": 1076.80,
  "one_time_fee": 15000.00,
  "third_party": false,
  "optional": false
}
```

**Output Excel (2 rows):**

| Row | Fee Type | Solution Name | Per Unit Rate | Year 1 Annual |
|-----|----------|--------------|---------------|---------------|
| 42 | Monthly F | HORIZON: Conditional Processing | $1,076.80 | $12,921.60 |
| 88 | One-Time | HORIZON: Conditional Processing - Implementation Fee | $15,000.00 | $15,000.00 |

---

## Sorting and Organization

After mapping all items, sort rows by:

1. **Optional** (FALSE first, then TRUE)
2. **Third_Party** (FALSE first, then TRUE)
3. **Fee_Type** (Monthly F, Monthly V, Annual, One-Time)
4. **Category** (alphabetical)
5. **Solution_Name** (alphabetical)

**Result:** Required items appear first, followed by optional items, with logical grouping.

---

## Summary Sheet Calculations

### Required Items Summary

| Metric | Formula | Description |
|--------|---------|-------------|
| Bundle Products | `=SUMIFS(Line_Items!$R:$R, Line_Items!$D:$D, "Core", Line_Items!$F:$F, FALSE)` | 7-year total for Core/Bundle items |
| Non-Bundle Required - Vendor | `=SUMIFS(Line_Items!$R:$R, Line_Items!$E:$E, FALSE, Line_Items!$F:$F, FALSE, Line_Items!$D:$D, "<>Core", Line_Items!$B:$B, "<>One-Time")` | Non-core, non-third-party, recurring |
| Required Third-Party | `=SUMIFS(Line_Items!$R:$R, Line_Items!$E:$E, TRUE, Line_Items!$F:$F, FALSE, Line_Items!$B:$B, "<>One-Time")` | Third-party recurring fees |
| One-Time Fees | `=SUMIFS(Line_Items!$K:$K, Line_Items!$B:$B, "One-Time", Line_Items!$F:$F, FALSE)` | All required one-time fees (Year 1 only) |
| **Total Required TCO** | `=SUM(C5:C8)` | Sum of above |
| **Average Monthly** | `=C10/84` | Total TCO ÷ 84 months |

### Optional Items Summary

| Metric | Formula | Description |
|--------|---------|-------------|
| Optional Solutions | `=SUMIFS(Line_Items!$R:$R, Line_Items!$F:$F, TRUE)` | All optional items (7-year total) |

---

## Year Summary Sheet Calculations

### Annual Breakdown (Years 1-7)

| Category | Year 1 Formula | Year 2 Formula | ... | Description |
|----------|----------------|----------------|-----|-------------|
| Required Annual Fees | `=SUMIFS(Line_Items!$K:$K, Line_Items!$F:$F, FALSE, Line_Items!$B:$B, "<>One-Time")` | `=SUMIFS(Line_Items!$L:$L, Line_Items!$F:$F, FALSE, Line_Items!$B:$B, "<>One-Time")` | ... | Recurring required fees |
| Optional Annual Fees | `=SUMIFS(Line_Items!$K:$K, Line_Items!$F:$F, TRUE)` | `=SUMIFS(Line_Items!$L:$L, Line_Items!$F:$F, TRUE)` | ... | Recurring optional fees |
| One-Time Fees | `=SUMIFS(Line_Items!$K:$K, Line_Items!$B:$B, "One-Time")` | `0` | `0` | One-time fees (Year 1 only) |
| **Total Annual Cost** | `=SUM(Year1_Required:Year1_OneTime)` | `=SUM(Year2_Required:Year2_Optional)` | ... | Sum for each year |

---

## Data Quality Sheet Population

Automatically flag items with data quality issues:

| Issue Type | Condition | Description |
|------------|-----------|-------------|
| Low Confidence | `confidence_score < 0.80` | Requires manual review |
| Missing Required Field | `solution_name = NULL OR fee_type = NULL` | Critical validation failure |
| Invalid Fee Type | `fee_type NOT IN enum list` | Data normalization failed |
| Missing Qty for Variable Fee | `fee_type = "Monthly V" AND average_monthly_qty = NULL` | Required field missing |
| Zero Cost Item | `per_unit_rate = 0 AND fee_type <> "One-Time"` | Potential data issue |
| Negative Cost (Review) | `per_unit_rate < 0 AND fee_type <> "One-Time"` | May be legitimate credit |

---

## Error Handling

### Missing Required Fields

| Field | Action | Error Message |
|-------|--------|---------------|
| `solution_name` | Skip item, log error | "Missing solution_name for item at index {i}" |
| `fee_type` | Use default "Monthly F", flag in Data_Quality | "Invalid fee_type '{value}', defaulted to Monthly F" |
| `per_unit_rate` AND `monthly_fee` | Set to 0, flag in Data_Quality | "No pricing found for {solution_name}" |

### Invalid Enum Values

| Field | Action | Error Message |
|-------|--------|---------------|
| `fee_type` | Attempt normalization → use default if fails | "Could not normalize fee_type '{value}'" |
| `category` | Attempt fuzzy match → use "Other" if fails | "Unknown category '{value}', using 'Other'" |

### Data Type Mismatches

| Field | Expected Type | Action | Example |
|-------|---------------|--------|---------|
| `monthly_fee` | Float | Convert to float, set 0 if fails | "abc" → 0.0 |
| `third_party` | Boolean | Normalize, default FALSE | "yes" → TRUE |
| `confidence_score` | Float 0.0-1.0 | Clamp to range, default 0.5 | 1.5 → 1.0 |

---

## Transformation Pipeline Steps

### Step 1: Load and Validate JSON
```python
1. Load JSON file
2. Validate structure (has vendor, client, line_items)
3. Check line_items is non-empty array
4. Log JSON metadata
```

### Step 2: Normalize Top-Level Fields
```python
1. Extract vendor, client, proposal_type, etc.
2. Normalize vendor name
3. Parse and format dates
4. Write to Metadata sheet
```

### Step 3: Process Line Items
```python
For each item in line_items:
    1. Check if item needs splitting (monthly_fee > 0 AND one_time_fee > 0)
    2. If split: create 2 row objects
    3. If no split: create 1 row object
    4. Normalize all enum fields
    5. Calculate per_unit_rate
    6. Validate required fields
    7. Add to output list
```

### Step 4: Sort and Write Line Items
```python
1. Sort items by: optional, third_party, fee_type, category, solution_name
2. Write to Line_Items sheet starting at row 2
3. Auto-increment Row ID
4. Apply formulas to calculated columns (J-R)
5. Apply data validation to enum columns
```

### Step 5: Calculate Summaries
```python
1. Wait for Excel to calculate formulas
2. Verify summary totals
3. Write to Summary sheet
4. Write to Year_Summary sheet
```

### Step 6: Generate Data Quality Report
```python
1. Scan all line items for issues
2. Flag low confidence, missing fields, invalid values
3. Write flagged items to Data_Quality sheet
4. Generate summary statistics
```

### Step 7: Save and Log
```python
1. Save workbook to TCO Output folder
2. Log mapping report (# items, # splits, # errors)
3. Return output path
```

---

## Validation Checklist

After transformation, validate:

- [ ] All required fields populated (solution_name, fee_type, per_unit_rate)
- [ ] All fee_type values are valid enums
- [ ] All category values are valid enums
- [ ] All boolean fields are TRUE or FALSE
- [ ] Monthly V items have average_monthly_qty > 0
- [ ] One-Time items only have cost in Year 1 (Years 2-7 = $0)
- [ ] Summary totals match sum of Line_Items details
- [ ] Year_Summary totals match Line_Items year columns
- [ ] Confidence scores are between 0.0 and 1.0
- [ ] Item splitting correctly created separate rows
- [ ] Row IDs are sequential without gaps

---

## Example: Complete Transformation

### Input JSON (single item)
```json
{
  "solution_name": "IP: DirectLink Merchant (via RDC)",
  "fee_type": "Monthly V",
  "category": "Item Processing",
  "monthly_fee": 3402.14,
  "one_time_fee": 21943.00,
  "per_unit_rate": 3402.14,
  "unit_description": "per transaction",
  "average_monthly_qty": 1,
  "third_party": false,
  "optional": false,
  "overall_confidence": 0.95,
  "extraction_notes": "Variable pricing based on transaction volume"
}
```

### Output Excel (2 rows)

**Row 40 (Monthly):**
| A | B | C | D | E | F | G | H | I | J | K | R | S | T |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 40 | Monthly V | IP: DirectLink Merchant (via RDC) | Item Processing | FALSE | FALSE | $3,402.14 | per transaction | 1 | $3,402.14 | $40,825.68 | $298,527.45 | 95.00% | Variable pricing based on transaction volume |

**Row 86 (One-Time):**
| A | B | C | D | E | F | G | H | I | J | K | R | S | T |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 86 | One-Time | IP: DirectLink Merchant (via RDC) - Implementation Fee | Item Processing | FALSE | FALSE | $21,943.00 | one-time | | $0.00 | $21,943.00 | $21,943.00 | 95.00% | Variable pricing based on transaction volume |

---

## Notes

1. **Formula Preservation:** Calculated columns (J-R) use Excel formulas, NOT static values. This allows dynamic recalculation if per_unit_rate or CPI changes.

2. **Data Validation:** Dropdowns are applied to columns B, D, E, F to ensure data integrity during manual edits.

3. **Sorting:** Items are sorted to group required vs optional, vendor vs third-party, and by fee type for easy analysis.

4. **Item Splitting:** Critical for accurate TCO calculation. Without splitting, one-time fees would be incorrectly amortized over 7 years.

5. **Error Logging:** All transformation errors, warnings, and data quality issues are logged to both:
   - Data_Quality sheet (visible to user)
   - logs/mapping_errors.log (detailed technical log)

6. **Extensibility:** Schema supports 8-10 year contracts by adding columns after Q. Formulas automatically extend.

---

**Document Version:** 1.0
**Last Updated:** 2025-12-08
**Author:** TCO Automation Project
**Status:** Complete
