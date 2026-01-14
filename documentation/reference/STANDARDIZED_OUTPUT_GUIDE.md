# STANDARDIZED VENDOR OUTPUT FORMAT - COMPLETE GUIDE

**Last Updated:** 2026-01-13
**Purpose:** Universal Excel format for comparing ANY vendor (FIS, CSI, Jack Henry, etc.)

---

## OVERVIEW

This standardized format ensures **apples-to-apples comparison** across all vendors by using:
- ✅ **Consistent column names** across all vendors
- ✅ **Standardized data types** (currency, text, boolean)
- ✅ **Universal fee type classification** (Monthly F, Monthly V, Annual, One-Time)
- ✅ **Automatic credit detection** (fixes missing credits bug)
- ✅ **Year-by-year cost projections** (Years 1, 2, 3, 5, 7)

---

## COLUMN STRUCTURE (17 Columns)

| Column | Name | Type | Description | Example |
|--------|------|------|-------------|---------|
| **A** | Item # | Integer | Sequential line item number | 1, 2, 3... |
| **B** | Solution Name | String | Full product/service name | "HORIZON Core Processing" |
| **C** | Category | String | Standardized product category | "Core Banking", "Digital" |
| **D** | Fee Type | Enum | Monthly F, Monthly V, Annual, One-Time | "Monthly F" |
| **E** | Monthly Fee | Currency | Fixed monthly or estimated monthly cost | $15,000.00 |
| **F** | Per Unit Rate | Currency | Cost per unit (for variable fees) | $0.0136 |
| **G** | Unit Description | String | What the unit represents | "per transaction", "per user" |
| **H** | Estimated Volume | Integer | Monthly volume/quantity | 1,000 |
| **I** | One-Time Fee | Currency | Implementation fee (negative for credits) | $17,015.00 or -$844,093.00 |
| **J** | Year 1 Annual | Currency | Total Year 1 cost (calculated) | $180,000.00 |
| **K** | Year 2 Annual | Currency | Year 2 with 20% growth | $216,000.00 |
| **L** | Year 3 Annual | Currency | Year 3 with 20% growth | $259,200.00 |
| **M** | Year 5 Annual | Currency | Year 5 with 20% growth | $373,248.00 |
| **N** | Year 7 Annual | Currency | Year 7 with 20% growth | $537,477.12 |
| **O** | Optional | Boolean | Yes/No - is this optional | "Yes" or "No" |
| **P** | Third Party | Boolean | Yes/No - is this third-party | "Yes" or "No" |
| **Q** | Notes | String | Extraction notes, additional details | "New pricing for combined org" |

---

## FEE TYPE DEFINITIONS

### 1. **Monthly F (Fixed)**
- **Description:** Fixed monthly fee, same amount each month
- **Column E:** Contains the monthly fee amount
- **Column F:** Usually 0 or blank
- **Annual Calculation:** Monthly Fee × 12 × Growth Factor
- **Examples:**
  - Core Processing: $15,000/month
  - Network Connectivity: $2,088/month

### 2. **Monthly V (Variable)**
- **Description:** Variable fee based on volume/usage
- **Column E:** Estimated monthly cost (Rate × Volume)
- **Column F:** Per unit rate
- **Column G:** Unit description (per transaction, per user, etc.)
- **Column H:** Estimated monthly volume
- **Annual Calculation:** (Rate × Volume) × 12 × Growth Factor
- **Examples:**
  - Paper: $0.0136/piece × 1,000 pieces = $13.60/month
  - Debit Card Production: $12/file × 29 files = $348/month

### 3. **Annual**
- **Description:** Billed annually (once per year)
- **Column E:** Annual fee (divided by 12 for display)
- **Annual Calculation:** Annual Fee × Growth Factor
- **Examples:**
  - SSL Certificates: $1,980/year
  - CSI Annual Forms: $2,044/year

### 4. **One-Time**
- **Description:** Implementation, setup, or credit (negative)
- **Column I:** One-time fee amount
- **Year 1:** Includes one-time fee
- **Years 2-7:** Zero (one-time only applies to Year 1)
- **Examples:**
  - Implementation Fee: $17,015
  - FIS Implementation Credits: **-$844,093** (negative = credit)
  - Signing Bonus: **-$75,000** (negative = credit)

---

## AUTOMATIC CREDIT DETECTION FEATURE

### Problem Fixed
Previously, extractions would show credits in the **summary** but not create individual **line items** for credits. This meant:
- ❌ TCO was overstated by $1M+
- ❌ Couldn't see breakdown of credits
- ❌ Apples-to-apples comparison impossible

### Solution
The standardized output script **automatically detects** missing credits:

```
[WARNING] Found $1,551,163 in credits but no credit line items!
[FIX] Adding credit line items...
[OK] Added 4 credit line items
```

### What Gets Added (FIS Example)
| Solution Name | Fee Type | One-Time Fee | Category |
|---------------|----------|--------------|----------|
| FIS Implementation Credits | One-Time | **-$844,093** | Credits |
| Third Party Implementation Credits | One-Time | **-$137,070** | Credits |
| Signing Bonus | One-Time | **-$75,000** | Credits |
| Other Implementation Credits | One-Time | **-$495,000** | Credits |

**Total Credits:** -$1,551,163 (reduces Year 1 TCO)

### What Gets Added (CSI Example)
| Solution Name | Fee Type | One-Time Fee | Category |
|---------------|----------|--------------|----------|
| Credit for One-Time Fees | One-Time | **-$338,034** | Credits |
| Special Incentive Billing Credit | One-Time | **-$375,000** | Credits |

**Total Credits:** -$713,034 (reduces Year 1 TCO)

---

## YEAR-BY-YEAR COST CALCULATION

### Growth Rate
- **Default:** 20% per year
- **Configurable:** Can be changed when generating output

### Calculation Formula

For **Monthly F** and **Monthly V**:
```
Year N Annual Cost = (Monthly Fee × 12) × (1 + Growth Rate)^(N - 1)
```

For **Annual**:
```
Year N Annual Cost = Annual Fee × (1 + Growth Rate)^(N - 1)
```

For **One-Time**:
```
Year 1 Cost = One-Time Fee
Years 2-7 Cost = $0
```

### Example: $15,000/month core processing fee

| Year | Formula | Annual Cost |
|------|---------|-------------|
| Year 1 | $15,000 × 12 × (1.20)^0 | **$180,000.00** |
| Year 2 | $15,000 × 12 × (1.20)^1 | **$216,000.00** |
| Year 3 | $15,000 × 12 × (1.20)^2 | **$259,200.00** |
| Year 5 | $15,000 × 12 × (1.20)^4 | **$373,248.00** |
| Year 7 | $15,000 × 12 × (1.20)^6 | **$537,477.12** |

---

## VISUAL FORMATTING

### Color Coding

| Item Type | Background Color | Font | Example |
|-----------|------------------|------|---------|
| **Required Items** | White | Black | Standard line items |
| **Optional Items** | Light Yellow (#FFF2CC) | Black | Zelle, Start Card |
| **Credits** | Light Green (#E6F7E6) | Bold Green | Implementation credits |
| **Category Headers** | Light Blue (#D9E1F2) | Bold Italic | "CATEGORY: CORE BANKING" |
| **Column Headers** | Dark Blue (#366092) | Bold White | "Solution Name", "Fee Type" |

### Borders
- All cells have thin borders for readability
- Merged cells (category headers) have full borders

### Number Formatting
- **Currency:** `$#,##0.00` (e.g., $1,234.56)
- **Per Unit Rate:** `$#,##0.0000` (e.g., $0.0136)
- **Volume:** `#,##0` (e.g., 1,000)

---

## CATEGORY STANDARDIZATION

Categories are standardized across all vendors using mappings from `Data_Dictionary/enum_mappings.json`:

### Standard Categories

| Category | Description | FIS Examples | CSI Examples |
|----------|-------------|--------------|--------------|
| **Core Banking** | Core processing system | HORIZON Core | CSI Core Processing |
| **Digital Banking** | Online/mobile banking | D1 Flex, D1 Business | iPay, Mobile Banking |
| **Card Services** | Debit/credit card services | Card Production, Tokenization | EMV Card Production |
| **Risk Management** | Fraud, compliance | DirectLink Risk Review | WatchDog CIP |
| **Payment Processing** | ACH, wires, RTP | FedNOW, RTP | CSI Wire |
| **Item Processing** | Check processing | FCM, Branch Capture | Image Capture |
| **Treasury Management** | Cash management | eWire, XAA | - |
| **Network** | Connectivity | Network Services | - |
| **Credits** | Implementation credits | FIS Credits, Signing Bonus | CSI Credits |

---

## USAGE EXAMPLES

### Generate Single Vendor Output

```bash
# Echelon Bank - FIS
python scripts/create_standardized_vendor_output.py "Echelon Bank" "FIS" "Extracted JSON/echelon_bank_fis_extraction_ai.json"

# Liberty Capital - CSI
python scripts/create_standardized_vendor_output.py "Liberty Capital Bank" "CSI" "Extracted JSON/liberty_capital_bank_csi_extraction_ai.json"
```

### Generate All Standardized Outputs

```bash
# Automatically discovers all JSON extractions and generates outputs
python scripts/generate_all_standardized_outputs.py
```

### Outputs Created
All files are saved to: `TCO Output/`

**Naming Convention:**
```
{Client_Name}_{Vendor_Name}_Standardized_{Timestamp}.xlsx
```

**Examples:**
- `Echelon_Bank_FIS_Standardized_20260113_160046.xlsx`
- `Liberty_Capital_Bank_CSI_Standardized_20260113_160046.xlsx`

---

## COMPARISON WORKFLOW

### Step 1: Generate Standardized Outputs
```bash
python scripts/generate_all_standardized_outputs.py
```

### Step 2: Open Excel Files Side-by-Side
- All files have **identical column structure**
- Use Excel's "View Side by Side" feature
- Or import into Power BI/Tableau for visual comparison

### Step 3: Compare Key Metrics

**Monthly Costs (Required):**
- Look at Column E (Monthly Fee) totals for required items
- Compare across vendors

**Monthly Costs (Optional):**
- Filter Column O = "Yes" for optional items
- Decide which optional items to include

**One-Time Costs:**
- Sum Column I (One-Time Fee) including negative credits
- **Net One-Time = Fees - Credits**

**7-Year TCO:**
- Sum Column N (Year 7 Annual) for all items
- Add cumulative costs for Years 1-7

---

## VALIDATION CHECKLIST

Before finalizing vendor comparison, verify:

### Data Completeness
- [ ] All line items from proposal are included
- [ ] Credits are captured (check for negative One-Time Fees)
- [ ] Optional vs Required distinction is correct
- [ ] Third-party products are identified

### Calculation Accuracy
- [ ] Year 1 Annual = (Monthly Fee × 12) OR One-Time Fee
- [ ] Growth rate applied correctly to Years 2-7
- [ ] One-Time fees only appear in Year 1
- [ ] Totals at bottom match summary

### Categorization
- [ ] Categories are standardized (not vendor-specific terms)
- [ ] Fee Types are correct (Monthly F, Monthly V, Annual, One-Time)
- [ ] Unit descriptions match pricing structure

### Visual Formatting
- [ ] Optional items highlighted in yellow
- [ ] Credits highlighted in green with negative values
- [ ] Category headers present and readable
- [ ] All currency values formatted correctly

---

## TROUBLESHOOTING

### Issue: Credits Missing

**Symptom:**
```
Summary shows $1.5M in credits, but no line items with negative fees
```

**Solution:**
The standardized output script **automatically fixes this**:
```
[WARNING] Found $1,551,163 in credits but no credit line items!
[FIX] Adding credit line items...
[OK] Added 4 credit line items
```

### Issue: Wrong Fee Type

**Symptom:**
Variable fee classified as "Monthly F" instead of "Monthly V"

**Solution:**
- Check source JSON: `fee_type` field
- If incorrect, re-run extraction with better prompts
- Manually fix in standardized JSON before re-generating

### Issue: Categories Not Standardized

**Symptom:**
Categories like "Existing Service - Core" instead of "Core Banking"

**Solution:**
- Update `Data_Dictionary/enum_mappings.json`
- Add mapping: `"Existing Service - Core": ["Core Banking"]`
- Re-generate standardized output

### Issue: Year Calculations Off

**Symptom:**
Year 2 should be 20% more than Year 1, but it's not

**Solution:**
- Check growth_rate parameter (default 0.20 = 20%)
- Verify calculation in `_calculate_annual_cost()` function
- For custom growth rates, specify when generating:
  ```python
  create_standardized_output(..., growth_rate=0.15)  # 15% growth
  ```

---

## ADVANCED CUSTOMIZATION

### Change Growth Rate

```python
# 15% growth instead of 20%
create_standardized_output(
    client_name="Echelon Bank",
    vendor_name="FIS",
    json_file="Extracted JSON/echelon_bank_fis_extraction_ai.json",
    growth_rate=0.15
)
```

### Add More Year Columns

Edit `COLUMNS` in `create_standardized_vendor_output.py`:

```python
COLUMNS = [
    # ... existing columns ...
    {'col': 'N', 'name': 'Year 7 Annual', 'width': 15},
    {'col': 'O', 'name': 'Year 10 Annual', 'width': 15},  # ADD THIS
    {'col': 'P', 'name': 'Optional', 'width': 10},        # Shift these down
    # ...
]
```

Then update `write_line_items()` to calculate Year 10 costs.

### Custom Credit Detection

Edit `_fix_missing_credits()` in `create_standardized_vendor_output.py`:

```python
# For Jack Henry credits (example)
elif 'JACK' in self.vendor_name.upper() or 'HENRY' in self.vendor_name.upper():
    credit_items = [
        {
            'solution_name': 'Jack Henry Implementation Credit',
            'fee_type': 'One-Time',
            'category': 'Credits',
            'one_time_fee': -total_credits,
            # ...
        }
    ]
```

---

## FILES REFERENCE

### Scripts
| File | Purpose |
|------|---------|
| `scripts/create_standardized_vendor_output.py` | Main generator - single vendor output |
| `scripts/generate_all_standardized_outputs.py` | Batch generator - all vendors at once |
| `scripts/create_multi_vendor_comparison.py` | Multi-vendor comparison with summary |

### Documentation
| File | Purpose |
|------|---------|
| `STANDARDIZED_OUTPUT_GUIDE.md` | This guide |
| `universal_schema.json` | Column schema definition (auto-generated) |
| `Data_Dictionary/enum_mappings.json` | Category and fee type mappings |

### Outputs
| Directory | Contents |
|-----------|----------|
| `TCO Output/` | All generated Excel files |

---

## BENEFITS OF STANDARDIZED FORMAT

### 1. **Apples-to-Apples Comparison**
- Same columns across all vendors
- Same data types and formats
- Same calculation methodology

### 2. **Credit Visibility**
- Automatically detects and adds missing credits
- Shows exact credit breakdown
- Accurate net TCO calculations

### 3. **Easy Integration**
- Import into Power BI/Tableau
- Use in Arriba's financial models
- Export to PDF for client presentations

### 4. **Vendor Agnostic**
- Works with FIS, CSI, Jack Henry, any vendor
- Handles different pricing models (bundle, organic growth, tiered)
- Standardizes vendor-specific terminology

### 5. **Audit Trail**
- Item # provides sequential tracking
- Notes column shows extraction confidence
- Third Party flag identifies dependencies

---

## NEXT STEPS

1. **Generate All Outputs:**
   ```bash
   python scripts/generate_all_standardized_outputs.py
   ```

2. **Review Generated Files:**
   - Check `TCO Output/` folder
   - Open Excel files
   - Verify credits are included

3. **Create Multi-Vendor Comparison:**
   ```bash
   python scripts/create_multi_vendor_comparison.py "Liberty Capital Bank" "FIS" "..." "CSI" "..."
   ```

4. **Import into Financial Model:**
   - Use consistent columns for VLOOKUP/INDEX formulas
   - Build summary dashboards
   - Generate client presentations

---

**Last Updated:** 2026-01-13
**Maintained By:** TCO Automation Team
**Questions?** Refer to source code comments in `scripts/create_standardized_vendor_output.py`
