# TCO Workbook Data Dictionary

## Document: WORKBOOK2.xlsx

---

## 1. Workbook Overview

| Property | Value |
|----------|-------|
| Total Sheets | 6 |
| Primary Data Sheet | Line Items |
| Summary Sheet | Summary |
| Configuration Sheets | Control, Years 1-7 |

### Sheet Purposes

| Sheet Name | Purpose |
|------------|---------|
| **Control** | Fee type dropdown values (Monthly F, Monthly V, Annual, One-Time) |
| **DeleteThisPageThenSave** | Instruction page (delete before final save) |
| **Confidentiality&Non-Disclosure** | Legal disclaimer page |
| **Line Items** | Main data entry - all vendor pricing line items |
| **Years 1-7** | Summary calculations by year for both vendors |
| **Summary** | High-level TCO comparison between FIS and Jack Henry |

---

## 2. Control Sheet - Fee Types

| Cell | Value | Description |
|------|-------|-------------|
| A4 | `Monthly F` | Monthly Fixed fee - same quantity every month (qty = 12/year) |
| A5 | `Monthly V` | Monthly Variable fee - quantity varies with growth rate |
| A6 | `Annual` | Annual fee - billed once per year (qty = 1/year) |
| A7 | `One-Time` | One-time fee - Year 1 only (qty = 1 in Y1, 0 thereafter) |

---

## 3. Line Items Sheet - Global Configuration

### Configuration Cells (Rows 1-3)

| Cell | Value | Description |
|------|-------|-------------|
| D2 | `7` | Contract term in years |
| D3 | `0.2` | Volume growth rate (20%) for Monthly V items |
| Q2 | `0.06` | CPI rate for Bundle items (6%) |
| Q3 | `0.03` | CPI rate for Non-Bundle items (3%) |

---

## 4. Line Items Sheet - FIS Section (Columns B-AN)

### Column Structure

| Column | Header | Data Type | Input/Formula | Description |
|--------|--------|-----------|---------------|-------------|
| **B** | Type (Monthly/Annual) | Text | INPUT | Fee type: "Monthly F", "Monthly V", "Annual", "One-Time" |
| **C** | Proposal | Number | INPUT | Proposal quantity (usually 1) |
| **D** | Average Monthly QTY | Number | FORMULA | `=IFERROR(AVERAGE(C:C),0)` |
| **E** | Year 1 Quantity | Number | FORMULA | Auto-calculates based on fee type |
| **F-N** | Year 2-10 Quantity | Number | FORMULA | Auto-calculates with growth for Monthly V |
| **O** | Solution Name/Description | Text | INPUT | Name of the service/product |
| **P** | Category | Text | INPUT | Category grouping (e.g., "CardProd", "HORIZON") |
| **Q** | Per Unit Rate | Currency | INPUT | Monthly or annual rate per unit |
| **R** | Year 1 Monthly Cost | Currency | FORMULA | `=S/12` |
| **S** | Year 1 Cost | Currency | FORMULA | `=IFERROR($Q*E,0)` |
| **T-AB** | Year 2-10 Cost | Currency | FORMULA | `=IFERROR($Q*[qty],0)` |
| **AC-AL** | Year 1-10 CPI | Currency | FORMULA | CPI adjustments per year |
| **AM** | CPI | Currency | FORMULA | `=SUM(AC:AL)` - Total CPI adjustment |
| **AN** | Total Term Cost | Currency | FORMULA | `=SUM(AM,S:AB)` - Grand total |

### Row Sections (FIS)

| Section | Row Range | Category | Description |
|---------|-----------|----------|-------------|
| **Header** | 4-6 | - | Column headers and section title |
| **Bundle FIS Products** | 7-20 | Bundle | Core processing bundle (Years 1-7) |
| **Non-Bundle Required FIS** | 22-54 | Non-Bundle Required | Required FIS products (not in bundle) |
| **Non-Bundle Required Third Parties** | 55-85 | Non-Bundle Required | Required third-party integrations |
| **Implementation Credits/Fees (FIS)** | 86-109 | One-Time | One-time fees and credits |
| **Implementation (Third Party)** | 110-120 | One-Time | Third-party implementation fees |
| **Optional FIS Solutions** | 121-129 | Optional | Optional FIS add-on products |
| **Optional Third-Party Solutions** | 130-164 | Optional | Optional third-party products |

---

## 5. Line Items Sheet - Jack Henry Section (Columns AP-CA)

### Column Structure

| Column | Header | Data Type | Input/Formula | Description |
|--------|--------|-----------|---------------|-------------|
| **AP** | Type (Monthly/Annual) | Text | INPUT | Fee type |
| **AQ** | Average Monthly QTY | Number | FORMULA | Average quantity |
| **AR-BA** | Year 1-10 Quantity | Number | FORMULA | Quantities per year |
| **BB** | Solution Name/Description | Text | INPUT | Service/product name |
| **BC** | Category | Text | INPUT | Category grouping |
| **BD** | Per Unit Rate | Currency | INPUT | Rate per unit |
| **BE** | Year 1 Monthly Cost | Currency | FORMULA | Monthly cost |
| **BF-BO** | Year 1-10 Cost | Currency | FORMULA | Annual costs |
| **BP-BY** | Year 1-10 CPI | Currency | FORMULA | CPI adjustments |
| **BZ** | CPI | Currency | FORMULA | Total CPI |
| **CA** | Total Term Cost | Currency | FORMULA | Grand total |

---

## 6. Data Entry Rules

### Required Input Fields (Per Line Item)

| Field | Column (FIS) | Column (JH) | Required | Format |
|-------|--------------|-------------|----------|--------|
| Fee Type | B | AP | Yes | Dropdown: Monthly F, Monthly V, Annual, One-Time |
| Proposal Qty | C | (AQ area) | Yes | Integer (usually 1) |
| Solution Name | O | BB | Yes | Text |
| Category | P | BC | Optional | Text |
| Per Unit Rate | Q | BD | Yes | Currency (no $, just number) |

### Formula Fields (Auto-Calculated)

| Calculation | Description |
|-------------|-------------|
| Quantity (E-N) | Based on fee type: Monthly F=12, Monthly V=12*(1+growth)^year, Annual=1, One-Time=1 in Y1 only |
| Year Costs (S-AB) | Rate × Quantity |
| CPI (AC-AL) | `((1+CPI_rate)^year - 1) × Year_Cost` |
| Total (AN) | Sum of all year costs + CPI adjustments |

---

## 7. Section-to-Category Mapping

### For JSON to Excel Mapping

| JSON Category | Excel Section | Row Range (FIS) | Notes |
|---------------|---------------|-----------------|-------|
| `Bundle` | Bundle FIS Products | 7-20 | One row per year (Years 1-7) |
| `Non-Bundle Required` | Non-Bundle Required FIS | 22-54 | FIS products |
| `Non-Bundle Required` + `third_party: true` | Non-Bundle Required Third Parties | 55-85 | Third-party products |
| `One-Time Fee` | Implementation Credits/Fees | 86-109 | Positive values |
| `One-Time Credit` | Implementation Credits/Fees | 86-109 | Negative values |
| `Non-Bundle Optional` | Optional FIS Solutions | 121-129 | FIS optional |
| `Non-Bundle Optional` + `third_party: true` | Optional Third-Party | 130-164 | Third-party optional |

---

## 8. Summary Sheet Structure

### FIS Summary (Columns B-D)

| Row | Description | Formula Reference |
|-----|-------------|-------------------|
| 3 | Bundle FIS Products Total | `=SUM('Line Items'!AN7:AN19)` |
| 4 | Non-Bundle FIS Required | `=SUM('Line Items'!AN22:AN54)` |
| 5 | Non-Bundle Required Third Parties | `=SUM('Line Items'!AN58:AN84)` |
| 6 | Sub-Total Required | `=SUM(C3:C5)` |
| 7 | Implementation Credits (FIS) | `=SUM('Line Items'!AN93)` |
| 8 | Implementation Credits (Third Party) | `='Line Items'!AN94` |
| 9 | Total Required (minus credits) | `=SUM(C6:D8)` |
| 12 | Optional FIS Solutions | `=SUM('Line Items'!AN122:AN129)` |
| 13 | Optional Third-Party | `=SUM('Line Items'!AN131:AN151)` |
| 15 | Total Optional | `=SUM(C12:C13)` |

### Jack Henry Summary (Columns E-G)

| Row | Description | Formula Reference |
|-----|-------------|-------------------|
| 3 | JH Monthly & Annual Products | `=SUM('Line Items'!CA7:CA77)` |
| 4 | Licensed Products | `=SUM('Line Items'!CA79:CA84)` |
| 6 | Sub-Total Required | `=SUM(F3:F5)` |
| 7 | Implementation Credits | `=-SUM('Line Items'!CA87:CA92)` |
| 9 | Total Required (minus credits) | `=SUM(F6:F8)` |

---

## 9. Years 1-7 Sheet Structure

### FIS Section (Rows 3-8)

| Row | Description |
|-----|-------------|
| 4 | Year headers (Year 1-7) |
| 5 | Required Annual Fees |
| 6 | Optional Annual Fees |
| 7 | Credits (negative) |
| 8 | Totals (SUM of rows 5-7) |

### Jack Henry Section (Rows 12-16)

| Row | Description |
|-----|-------------|
| 13 | Year headers (Year 1-7) |
| 14 | Required Annual Fees |
| 15 | Optional Annual Fees |
| 16 | Totals |

---

## 10. Key Formulas Reference

### Quantity Calculation (Column E)
```excel
=IF($B="Annual",1,IF($B="Monthly F",12,IF($B="Monthly V",12*(1+$D$3)^0,0)))
```

### Year Cost Calculation (Column S)
```excel
=IFERROR($Q*E,0)
```

### CPI Calculation (Non-Bundle, Column AD for Year 2)
```excel
=IF(VALUE(MID(AD$5,6,1))<=$D$2,((1+$Q$3)^1-1)*T,0)
```

### Total Term Cost (Column AN)
```excel
=SUM(AM,S:AB)
```

---

## 11. JSON to Excel Field Mapping

| JSON Field | Excel Column (FIS) | Notes |
|------------|-------------------|-------|
| `solution_name` | O | Direct mapping |
| `fee_type` | B | "Monthly F", "Monthly V", "Annual", "One-Time" |
| `category` | P | Category description |
| `monthly_fee` | Q | For Monthly types |
| `one_time_fee` | Q | For One-Time type |
| `per_unit_rate` | Q | Alternative to monthly_fee |
| `optional` | - | Determines section (Required vs Optional rows) |
| `third_party` | - | Determines section (FIS vs Third-Party rows) |

---

## 12. Important Notes

1. **Row Order Matters**: Items must be placed in correct row ranges based on category
2. **Negative Values**: Credits should be entered as negative numbers
3. **Bundle Items**: Each year of bundle pricing gets its own row (rows 7-13)
4. **CPI Auto-Calculates**: Don't manually enter CPI - formulas handle it
5. **Quantities Auto-Calculate**: Based on fee type, don't manually enter
6. **Total Formulas**: AN column and Summary sheet auto-calculate from input data

---

*Data Dictionary Generated: December 2024*
*Source: WORKBOOK2.xlsx Analysis*
