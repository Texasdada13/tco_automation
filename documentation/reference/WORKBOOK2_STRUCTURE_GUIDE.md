# WORKBOOK2.xlsx - VISUAL STRUCTURE GUIDE

Complete reference for understanding WORKBOOK2's expected format for FIS line items.

---

## 📐 SHEET LAYOUT

```
┌─────────────────────────────────────────────────────────────────┐
│                    WORKBOOK2.xlsx                                │
│                    Sheet: "Line Items"                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Row 1:  [Title Row] → FIS header in column O                   │
│  Row 2:  Years→ [7] | Growth→ [0.2]                            │
│  Row 3:  (empty)                                                 │
│  Row 4:  Column headers (Type, Avg Monthly QTY, FIS, etc.)      │
│  Row 5:  Sub-headers (Proposal, Year 1-10 Quantity, etc.)       │
│  Row 6:  ══════ SECTION: Bundle FIS Products ══════            │
│  Row 7-13: [7 line items - Year 1-7 Bundle Pricing]             │
│  Row 14-20: (blank/formulas)                                     │
│  Row 21: ══════ SECTION: Non-Bundle REQUIRED FIS ══════        │
│  Row 22-77: [35+ line items - Granular FIS products]            │
│  Row 78-85: ══════ SECTION: Required Third Parties ══════      │
│  Row 86: ══════ SECTION: Implementation Fees ══════            │
│  Row 87-120: [30+ one-time fees and credits]                    │
│  Row 121: ══════ SECTION: Optional FIS ══════                  │
│  Row 122-129: [Optional FIS products]                            │
│  Row 130: ══════ SECTION: Optional Third Party ══════          │
│  Row 131-151: [Optional third-party products]                   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 COLUMN STRUCTURE (Columns A-AN)

### Core Identification Columns

```
A: (blank/notes)
B: Fee Type
   ├── Monthly F  (Fixed monthly fee)
   ├── Monthly V  (Variable monthly fee - depends on quantity)
   ├── Annual     (Annual fee)
   └── One-Time   (One-time implementation/setup fee)

C: Proposal (11/2025)
   └── Quantity from proposal or indicator (usually 1)

O: Solution Name/Description
   └── Full product/service name

P: Category
   └── Product category (e.g., "CardProd", "DirectLink", "ATM/EFT")
```

### Quantity Columns

```
D: Average Monthly QTY
   └── Average monthly quantity (calculated)

E: Year 1 Quantity
F: Year 2 Quantity
G: Year 3 Quantity
H: Year 4 Quantity
I: Year 5 Quantity
J: Year 6 Quantity
K: Year 7 Quantity
L: Year 8 Quantity
M: Year 9 Quantity
N: Year 10 Quantity
```

### Pricing Columns

```
Q: Per Unit Rate
   └── Cost per unit (e.g., $0.0136 per paper sheet)

R: Year 1 Monthly Cost
   └── Calculated monthly cost for Year 1

S: Year 1 Cost (Annual)
T: Year 2 Cost (Annual)
U: Year 3 Cost (Annual)
V: Year 4 Cost (Annual)
W: Year 5 Cost (Annual)
X: Year 6 Cost (Annual)
Y: Year 7 Cost (Annual)
Z: Year 8 Cost (Annual)
AA: Year 9 Cost (Annual)
AB: Year 10 Cost (Annual)

AC-AN: Additional calculations (CPI, totals, etc.)
```

---

## 📝 SECTION 1: BUNDLE FIS PRODUCTS (Rows 7-13)

### Example Structure

| Row | Fee Type | Qty | Solution Name | Category | Per Unit Rate | Year 1 Cost |
|-----|----------|-----|---------------|----------|---------------|-------------|
| 7 | Monthly F | 1 | Year 1 CORE PROCESSING (Bundle) | HORIZON CORE... | $15,000 | [Formula] |
| 8 | Monthly F | 1 | Year 2 CORE PROCESSING (Bundle) | HORIZON CORE... | $17,500 | [Formula] |
| 9 | Monthly F | 1 | Year 3 CORE PROCESSING (Bundle) | HORIZON CORE... | $22,500 | [Formula] |
| 10 | Monthly F | 1 | Year 4 CORE PROCESSING (Bundle) | HORIZON CORE... | $28,000 | [Formula] |
| 11 | Monthly F | 1 | Year 5 CORE PROCESSING (Bundle) | HORIZON CORE... | $35,000 | [Formula] |
| 12 | Monthly F | 1 | Year 6 CORE PROCESSING (Bundle) - CPI Increase Begins | HORIZON CORE... | $35,000 | [Formula] |
| 13 | Monthly F | 1 | Year 7 CORE PROCESSING (Bundle) - CPI Increase | HORIZON CORE... | =AN12/12 | [Formula] |

**Key Points:**
- ✅ Each year is a separate line item
- ✅ Pricing increases over time (tiered structure)
- ✅ Year 6-7: CPI adjustments begin
- ❌ Our extraction captures only Year 1

---

## 📝 SECTION 2: NON-BUNDLE REQUIRED FIS (Rows 22-77)

### Example 1: Paper and Envelopes (Granular Breakdown)

| Row | Fee Type | Qty | Solution Name | Category | Per Unit Rate |
|-----|----------|-----|---------------|----------|---------------|
| 22 | (section header) | | Paper and Envelopes | | |
| 23 | Monthly V | 1,000 | Per piece of paper | Output Solutions | $0.0136 |
| 24 | Monthly V | 5,000 | Per envelope x 500 | Output Solutions | $0.0314 |

**Our Extraction:**
```json
{
  "solution_name": "Paper and Envelopes",
  "monthly_fee": 29.00,
  "per_unit_rate": 0.0136
}
```
❌ **Issue:** Aggregated into 1 item instead of 2

---

### Example 2: Card Production (3 Components)

| Row | Fee Type | Qty | Solution Name | Category | Per Unit Rate |
|-----|----------|-----|---------------|----------|---------------|
| 25 | (section header) | | Card Production | | |
| 26 | Monthly F | 1 | Card Pro Connect | CardProd | $500 |
| 27 | Monthly V | 29 | Debit Card Production Files/Jobs per month | CardProd | $12 |
| 28 | Monthly V | 25 | Debit Cards Produced per month | CardProd | $6.82 |

**Our Extraction:**
```json
{
  "solution_name": "Debit Card Production",
  "monthly_fee": 1018.00,
  "per_unit_rate": 12.00,
  "one_time_fee": 1250
}
```
❌ **Issue:** Aggregated into 1 item instead of 3

---

### Example 3: DirectLink Risk Review (Monthly Minimum + Variable)

| Row | Fee Type | Qty | Solution Name | Category | Per Unit Rate |
|-----|----------|-----|---------------|----------|---------------|
| 29 | (section header) | | DirectLink Risk Review | | |
| 30 | Monthly F | 1 | Monthly Minimum | DirectLink | $200 |
| 31 | Monthly V | 10,000 | DirectLink Risk Review (Transactions) | DirectLink | $0.0033 |

**Our Extraction:**
```json
{
  "solution_name": "DirectLink Risk Review (DLRR)",
  "monthly_fee": 233.00,
  "per_unit_rate": 0.0033
}
```
❌ **Issue:** Monthly minimum not separated from variable fee

---

### Example 4: Card Suite Pro (3 Fee Components)

| Row | Fee Type | Qty | Solution Name | Category | Per Unit Rate |
|-----|----------|-----|---------------|----------|---------------|
| 32 | (section header) | | Card Suite Pro | | |
| 33 | Monthly V | 189 | Active Users | Card | $1.24 |
| 34 | Monthly F | 0 | Active Users (Monthly Minimum) | Card | $375 |
| 35 | Monthly F | 1 | Monthly Minimum, Call Center Assistance $1.50/minute | Card | $50 |

**Our Extraction:**
```json
{
  "solution_name": "Card Suite Pro",
  "monthly_fee": 425.00,
  "per_unit_rate": 1.24
}
```
❌ **Issue:** $425 = $375 + $50, but components not separated

---

### Example 5: Tokenization (7+ Components - Completely Missing!)

| Row | Fee Type | Qty | Solution Name | Category | Per Unit Rate |
|-----|----------|-----|---------------|----------|---------------|
| 43 | (section header) | | Tokenization | | |
| 44 | Monthly V | 16 | Token Provisioning | ATM/EFT | $1.00 |
| 45 | Monthly F | 1 | Step Up Authentication | ATM/EFT | $100 |
| 46 | Monthly F | 1 | Call Center Support | ATM/EFT | $65 |
| 47 | Monthly V | 45 | Call Center Support per minute | ATM/EFT | $1.50 |
| 48 | Monthly F | 1 | Automated Customer Notification | ATM/EFT | $100 |
| 49 | Monthly V | 50 | Email Notices | ATM/EFT | $1.00 |
| 50 | Monthly V | 50 | SMS Notices | ATM/EFT | $3.00 |

**Our Extraction:**
```json
{
  "solution_name": "Tokenization",
  "monthly_fee": 337.00,
  "per_unit_rate": 0.05
}
```
❌ **Issue:** Only captured aggregate, missing all 7 components!

---

## 📝 SECTION 3: IMPLEMENTATION FEES (Rows 87-120)

### Structure: One-Time Fees + Credits

| Row | Fee Type | Qty | Solution Name | Category | Per Unit Rate |
|-----|----------|-----|---------------|----------|---------------|
| 87 | One-Time | 1 | Card Production Implementation Fee | Card Production | $1,250 |
| 88 | One-Time | 1 | DirectLink Risk Review (DLRR) Implementation Fee | DirectLink... | $17,015 |
| 89 | One-Time | 1 | Card Suite Pro Implementation Fee | Card Suite Pro | $4,000 |
| 90 | One-Time | 1 | Payments One Full-Service Debit Card Fraud Disputes | Payments One | $1,500 |
| 91 | One-Time | 1 | Tokenization (Apple Pay, Additional Pays) | Tokenization | $13,600 |
| 92 | One-Time | 1 | NYCE Preferred Debit Card Network | NYCE | $1,500 |
| 93 | One-Time | 1 | **FIS Implementation Credits** | | **-$844,093** |
| 94 | One-Time | 1 | **Third Party Implementation Credits** | | **-$137,070** |
| 95 | One-Time | 1 | **Signing Bonus** | | **-$50,000** |
| 96 | One-Time | 1 | D1 Commercial Implementation Fee | D1 Commercial | $350,000 |

**Our Extraction:**
- ✅ Some implementation fees captured (attached to recurring items)
- ❌ **Critical missing:** Implementation credits (-$1,031,163 total!)

**Impact:**
- Without credits, TCO is **overstated by over $1 million**
- Credits must be captured as separate line items with negative values

---

## 🔄 FORMULAS IN WORKBOOK2

### Year 1 Annual Cost (Column S)

For Monthly F:
```excel
=IF(B7="Annual", Q7, IF(B7="Monthly F", Q7*12, IF(B7="Monthly V", Q7*D7*12, 0)))
```

For Monthly V:
```excel
=IF(B7="Monthly V", Q7 * D7 * 12, 0)
```

For One-Time:
```excel
=IF(B7="One-Time", Q7, 0)
```

### Year 2-10 Costs (Columns T-AB)

With growth applied:
```excel
=IF(B7="One-Time", 0, S7 * (1 + $D$3))
```
Where `$D$3` = Growth Rate (20% = 0.2)

### Summary Calculations

Total for section:
```excel
=SUM(S7:S20)  // Sum all Year 1 costs in section
```

---

## 🎯 KEY TAKEAWAYS

### Structure Requirements

1. **One product ≠ One line item**
   - Complex products must be broken down into components
   - Example: "Card Suite Pro" = 3 line items

2. **Fee components must be separate**
   - Monthly minimums vs. variable fees
   - Base fees vs. add-on fees
   - Recurring vs. one-time

3. **Year-by-year pricing**
   - Bundle pricing requires 7 separate rows
   - Each year's rate is different

4. **Implementation section is critical**
   - Separate line items for all one-time fees
   - Credits (negative values) must be included
   - Can exceed $1M in total credits

### Data Integrity Rules

| Rule | Description | Example |
|------|-------------|---------|
| **Granularity** | Break down to smallest component | Paper AND Envelopes = 2 items |
| **Completeness** | Include all fee types | Monthly minimum + Variable fee |
| **Accuracy** | Exact rates, not aggregates | $0.0136/sheet, not $29/month total |
| **Traceability** | Each cost item traceable to proposal | "Per piece of paper" matches proposal line |
| **Credits** | Negative values must be captured | -$844,093 Implementation Credits |

---

## 📋 VALIDATION CHECKLIST

Before finalizing WORKBOOK2 output, verify:

### Structural Checks
- [ ] Each year (1-7) has bundle pricing row
- [ ] Complex products broken into components
- [ ] Monthly minimums separated from variable fees
- [ ] Implementation fees in separate section
- [ ] Implementation credits included (negative values)

### Data Checks
- [ ] All quantities present
- [ ] Per unit rates match proposal
- [ ] Fee types correct (Monthly F/V, Annual, One-Time)
- [ ] Categories assigned
- [ ] Formulas calculating correctly

### Completeness Checks
- [ ] All required products included
- [ ] Optional products marked correctly
- [ ] Third-party products identified
- [ ] No duplicate line items
- [ ] Total costs sum correctly

---

## 🚀 USAGE WITH MAPPER

The `json_to_workbook2_mapper.py` handles:

✅ **Automatically:**
- Bundle pricing expansion (1 → 7 items)
- Paper/Envelopes breakdown (1 → 2 items)
- Card Production breakdown (1 → 3 items)
- Implementation fee separation
- Implementation credits addition

⚠️ **Needs Manual Review:**
- Quantity validation
- Category assignments
- Missing optional products
- Vendor-specific variations

---

**Last Updated:** 2026-01-13
**Reference:** WORKBOOK2.xlsx (Echelon Primary TCO v5)
