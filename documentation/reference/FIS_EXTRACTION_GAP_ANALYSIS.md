# FIS EXTRACTION GAP ANALYSIS - Echelon Bank
## Comparison: WORKBOOK2.xlsx (Expected) vs. Our Extraction

**Date:** 2026-01-13
**Source:** WORKBOOK2.xlsx vs. echelon_bank_fis_extraction_ai.json

---

## EXECUTIVE SUMMARY

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total items in WORKBOOK2** (Expected) | 72 | 100% |
| **Total items extracted** (Our AI) | 22 | 30.6% |
| **Matched items** (by name) | 6 | 8.3% |
| **Missing from extraction** | 61 | 84.7% |
| **Extra in extraction** (not in WORKBOOK2) | 16 | - |

**Conclusion:** Extraction coverage is ~31%, with significant gaps. The AI extracted aggregated line items, but WORKBOOK2 expects highly granular breakdowns.

---

## KEY GAPS IDENTIFIED

### 1. BUNDLE PRICING - YEAR-BY-YEAR BREAKDOWN ❌

**WORKBOOK2 Expects** (7 separate line items):
- Year 1 CORE PROCESSING (Bundle) - $15,000/month
- Year 2 CORE PROCESSING (Bundle) - $17,500/month
- Year 3 CORE PROCESSING (Bundle) - $22,500/month
- Year 4 CORE PROCESSING (Bundle) - $28,000/month
- Year 5 CORE PROCESSING (Bundle) - $35,000/month
- Year 6 CORE PROCESSING (Bundle) - $35,000/month (CPI Increase Begins)
- Year 7 CORE PROCESSING (Bundle) - Formula based (CPI Increase)

**Our Extraction** (1 aggregated item):
- FIS Monthly Bundle - Year 1 - $15,000/month

**Issue:** Our extraction captures only Year 1 pricing. WORKBOOK2 requires separate rows for each year with different pricing tiers. The FIS proposal likely has a tiered pricing schedule that increases over time, which we're not capturing.

---

### 2. GRANULAR LINE ITEM BREAKDOWN ❌

**Example: Paper and Envelopes**

**WORKBOOK2 Expects** (2 separate items):
- Per piece of paper | Monthly V | $0.0136 per piece | Qty: 1,000
- Per envelope x 500 | Monthly V | $0.0314 per envelope | Qty: 5,000

**Our Extraction** (1 aggregated item):
- Paper and Envelopes | Monthly V | Monthly: $29.00 | Per Unit: $0.0136

**Issue:** We aggregated these into one line item. WORKBOOK2 expects each component (paper, envelopes) as separate rows with their own quantities and rates.

---

**Example: Card Production**

**WORKBOOK2 Expects** (3 separate items):
- Card Pro Connect | Monthly F | $500/month
- Debit Card Production Files/Jobs per month | Monthly V | $12 per file | Qty: 29
- Debit Cards Produced per month | Monthly V | $6.82 per card | Qty: 25

**Our Extraction** (1 aggregated item):
- Debit Card Production | Monthly V | Monthly: $1,018.00 | Per Unit: $12 | One-Time: $1,250

**Issue:** We combined these three components into one line item. The monthly fee ($1,018) appears to be a sum, but WORKBOOK2 needs individual breakdowns for accurate forecasting.

---

### 3. MONTHLY MINIMUMS SEPARATED ❌

**Example: Card Suite Pro**

**WORKBOOK2 Expects** (3 separate items):
- Active Users | Monthly V | $1.24 per user
- Active Users (Monthly Minimum) | Monthly F | $375/month
- Monthly Minimum, Call Center Assistance $1.50/minute | Monthly F | $50/month

**Our Extraction** (1 aggregated item):
- Card Suite Pro | Monthly V | Monthly: $425.00 | Per Unit: $1.24

**Issue:** We captured the variable rate and a combined monthly minimum ($425 = $375 + $50), but didn't separate the base fee from the call center fee.

---

### 4. MISSING IMPLEMENTATION FEES ❌

**WORKBOOK2 Expects (separate one-time line items):**
- Card Production Implementation Fee | One-Time | $1,250
- DirectLink Risk Review (DLRR) Implementation Fee | One-Time | $17,015
- Card Suite Pro Implementation Fee | One-Time | $4,000
- Tokenization Implementation Fee | One-Time | $13,600
- NYCE Implementation Fee | One-Time | $1,500
- FedNOW Implementation Fee | One-Time | $9,000
- Real-Time Payments Implementation Fee | One-Time | $9,000
- Zelle Implementation Fee | One-Time | $37,500
- ... (many more)

**Our Extraction:**
- Implementation fees are sometimes combined with the recurring fee in the same line item (e.g., Debit Card Production has one_time_fee: $1,250), but not as separate rows

**Issue:** WORKBOOK2 expects implementation fees as separate line items, not attached to the recurring line items. This affects the Implementation Credits section calculations.

---

### 5. COMPLETELY MISSING LINE ITEMS ❌

**Not extracted at all:**

**Tokenization Components:**
- Token Provisioning | Monthly V | $1.00 per token
- Step Up Authentication | Monthly F | $100/month
- Call Center Support | Monthly F | $65/month
- Call Center Support per minute | Monthly V | $1.50/minute
- Automated Customer Notification | Monthly F | $100/month
- Email Notices | Monthly V | $1.00 per notice
- SMS Notices | Monthly V | $3.00 per notice

**D1 Commercial:**
- D1 Commercial | Monthly F | $15,000/month
- D1 Commercial Implementation Fee | One-Time | $350,000

**AvidAscend Components:**
- Accounts Payable | Monthly F | $492/month
- Fixed Assets | Monthly F | $311/month
- Prepaids | Monthly F | $109/month
- Approval Workflow | Monthly F | $154/month
- Invoices | Monthly F | $61/month
- AvidAscend Implementation Fee | One-Time | $5,044

**Others:**
- Web Admin | Monthly V | $563/month
- Enterprise License (Up to $250M in assets) | Monthly V | $609/month

---

### 6. IMPLEMENTATION CREDITS MISSING ❌

**WORKBOOK2 Has (critical for TCO calculation):**
- FIS Implementation Credits | One-Time | -$844,093 (negative = credit)
- Third Party Implementation Credits | One-Time | -$137,070
- Signing Bonus | One-Time | -$50,000

**Our Extraction:**
- No credits captured

**Issue:** These are large credits that significantly reduce the total implementation cost. Missing these overstates the TCO by over $1 million.

---

## DETAILED GAP LIST

### MISSING - Bundle FIS Products (7 items)

| Solution Name | Fee Type | Rate | Issue |
|---------------|----------|------|-------|
| Year 1 CORE PROCESSING (Bundle) | Monthly F | $15,000 | ❌ Only extracted as "FIS Monthly Bundle - Year 1" |
| Year 2 CORE PROCESSING (Bundle) | Monthly F | $17,500 | ❌ Not extracted |
| Year 3 CORE PROCESSING (Bundle) | Monthly F | $22,500 | ❌ Not extracted |
| Year 4 CORE PROCESSING (Bundle) | Monthly F | $28,000 | ❌ Not extracted |
| Year 5 CORE PROCESSING (Bundle) | Monthly F | $35,000 | ❌ Not extracted |
| Year 6 CORE PROCESSING (Bundle) - CPI Increase Begins | Monthly F | $35,000 | ❌ Not extracted |
| Year 7 CORE PROCESSING (Bundle) - CPI Increase | Monthly F | Formula | ❌ Not extracted |

---

### MISSING - Non-Bundle REQUIRED FIS Products (35 items missing)

**Paper and Envelopes** (Granularity Issue):
- ❌ Per piece of paper | Monthly V | $0.0136
- ❌ Per envelope x 500 | Monthly V | $0.0314

**Card Production** (Granularity Issue):
- ❌ Card Pro Connect | Monthly F | $500
- ❌ Debit Card Production Files/Jobs per month | Monthly V | $12
- ❌ Debit Cards Produced per month | Monthly V | $6.82

**DirectLink Risk Review** (Granularity Issue):
- ❌ Monthly Minimum | Monthly F | $200
- ❌ DirectLink Risk Review (Transactions) | Monthly V | $0.0033

**Card Suite Pro** (Granularity Issue):
- ❌ Active Users | Monthly V | $1.24
- ❌ Active Users (Monthly Minimum) | Monthly F | $375
- ❌ Monthly Minimum, Call Center Assistance $1.50/minute | Monthly F | $50

**Payments One** (Only partial extraction):
- ❌ Monthly Minimum | Monthly F | $500
- ❌ Monthly Minimum (separate for fraud disputes) | Monthly F | $500

**Tokenization Components** (Missing entirely):
- ❌ Token Provisioning | Monthly V | $1.00
- ❌ Step Up Authentication | Monthly F | $100
- ❌ Call Center Support | Monthly F | $65
- ❌ Call Center Support per minute | Monthly V | $1.50
- ❌ Automated Customer Notification | Monthly F | $100
- ❌ Email Notices | Monthly V | $1.00
- ❌ SMS Notices | Monthly V | $3.00

**NYCE Network** (Partial extraction):
- ❌ Transactions | Monthly V | $0.035
- ❌ Participation Fee | Monthly F | $100

**Third Party Products** (Missing):
- ❌ Web Admin | Monthly V | $563
- ❌ Enterprise License (Up to $250M in assets) | Monthly V | $609

**FedNOW** (Partial extraction):
- ❌ FedNOW (Receive Only) Implementation Fee | One-Time | $9,000

**Real-Time Payments** (Partial extraction):
- ❌ Real Time Payments (Receive Only) Implementation Fee | One-Time | $9,000

**Collaboration Hub** (Partial extraction):
- ❌ Collaboration Hub (Up to 10 Users) ($200 Per additional user) | Monthly V | $900

**Zelle** (Partial extraction):
- ❌ Monthly Participation Fee (Consumer) | Monthly F | $1,000
- ❌ Monthly Participation Fee (Small Business) | Monthly F | $250
- ❌ Consumer and Small Business Transactions | Monthly V | $0.65
- ❌ Zelle Implementation Fee | One-Time | $37,500

---

### MISSING - Implementation Credits and One-Time Fees (30 items)

**One-Time Implementation Fees:**
- ❌ Card Production Implementation Fee | One-Time | $1,250
- ❌ DirectLink Risk Review (DLRR) Implementation Fee | One-Time | $17,015
- ❌ Card Suite Pro Implementation Fee | One-Time | $4,000
- ❌ Payments One Full-Service Debit Card Fraud Disputes | One-Time | $1,500
- ❌ Tokenization Implementation Fee | One-Time | $13,600
- ❌ NYCE Implementation Fee | One-Time | $1,500
- ❌ Network Services Implementation Fee | One-Time | $2,088
- ❌ SmartSign Implementation Fee | One-Time | $478
- ❌ TruStage Implementation Fee | One-Time | $1,158
- ❌ IBM Cognos Implementation Fee | One-Time | $1,172
- ❌ Subpoena Centre Implementation Fee | One-Time | $3,399
- ❌ Start Card Implementation Fee | One-Time | $2,000
- ❌ WebConnect and DirectConnect Implementation Fee | One-Time | $6,099
- ❌ Credit Insights Implementation Fee | One-Time | $5,000
- ❌ AvidAscend Implementation Fee | One-Time | $5,044

**Implementation Credits (Critical - reduces TCO):**
- ❌ FIS Implementation Credits | One-Time | -$844,093
- ❌ Third Party Implementation Credits | One-Time | -$137,070
- ❌ Signing Bonus | One-Time | -$50,000

**Other One-Time Items:**
- ❌ D1 Commercial Implementation Fee | One-Time | $350,000
- ❌ Collaboration Hub Implementation Fee | One-Time | $16,134

**Recurring Fees (in Implementation section - unusual but in WORKBOOK2):**
- ❌ Subpoena Centre | Monthly F | $382
- ❌ Start Card (Temporary Debit Card) | Monthly V | $150
- ❌ D1 Commercial | Monthly F | $15,000
- ❌ Accounts Payable | Monthly F | $492
- ❌ Fixed Assets | Monthly F | $311
- ❌ Prepaids | Monthly F | $109
- ❌ Approval Workflow | Monthly F | $154
- ❌ Invoices | Monthly F | $61

---

## ITEMS EXTRACTED BUT NOT IN WORKBOOK2

These items were extracted by our AI but don't match WORKBOOK2's structure. This suggests aggregation or naming differences:

| Solution Name | Our Category | Fee Type | Issue |
|---------------|--------------|----------|-------|
| FIS Monthly Bundle - Year 1 | Core Banking | Monthly F | ✓ Partial match (only Year 1) |
| Paper and Envelopes | Document Services | Monthly V | ✓ Aggregated (should be 2 items) |
| Debit Card Production | Card Services | Monthly V | ✓ Aggregated (should be 3 items) |
| DirectLink Risk Review (DLRR) | Risk Management | Monthly V | ✓ Aggregated (should be 2 items) |
| Card Suite Pro | Digital Banking | Monthly V | ✓ Aggregated (should be 3 items) |
| Payments One Debit Card Fraud Case Investigation | Fraud Prevention | Monthly V | ⚠️ Not in WORKBOOK2 as separate item |
| Payments One Full-Service Debit Card Fraud Disputes | Fraud Prevention | Monthly V | ✓ In WORKBOOK2 as one-time fee |
| Tokenization | Digital Payments | Monthly V | ✓ Aggregated (should be 7+ items) |
| NYCE Preferred Debit Card Network | Card Networks | Monthly V | ✓ Aggregated (should be 2-3 items) |
| Network Services | Infrastructure | Monthly F | ✓ Match |
| SmartSign | Digital Services | Monthly F | ✓ Match |
| TruStage | Compliance | Annual | ✓ Match |
| IBM Cognos (HORIZON 360) | Reporting | Monthly F | ✓ Match |
| Start Card | Card Services | Monthly V | ✓ Match |
| FedNOW (Receive Only) | Payment Processing | Monthly V | ✓ Partial (missing impl fee) |
| Real-Time Payments (RTP) | Payment Processing | Monthly V | ✓ Partial (missing impl fee) |
| Zelle | Digital Payments | Monthly V | ✓ Aggregated (should be 4 items) |
| Collaboration Hub | Collaboration | Monthly F | ✓ Match |
| WebConnect and DirectConnect | Digital Banking | Monthly F | ✓ Match |
| Credit Insights | Analytics | Monthly F | ✓ Match |
| Subpoena Centre | Compliance | Monthly F | ✓ Match |
| AvidAscend | Financial Management | Monthly F | ✓ Aggregated (should be 5-6 items) |

---

## ROOT CAUSE ANALYSIS

### Why Are We Missing So Much?

1. **AI Aggregation Behavior**: The AI extraction is consolidating related line items into single entries (e.g., combining "Per piece of paper" and "Per envelope" into "Paper and Envelopes")

2. **Multi-Year Pricing Not Captured**: The FIS proposal has tiered pricing (Years 1-7), but the AI is only extracting Year 1 pricing

3. **Component Breakdowns Missing**: Complex products (Card Suite Pro, Tokenization, Zelle) have multiple fee components that should be separate line items

4. **Implementation Fees Not Separated**: Implementation fees are attached to recurring line items instead of being separate rows

5. **Credits Not Recognized**: Large negative values (credits) are not being extracted

6. **Optional/Add-on Products Missed**: Products like D1 Commercial, AvidAscend components are completely missing

---

## RECOMMENDATIONS TO FIX EXTRACTION

### HIGH PRIORITY

1. **Extract Multi-Year Bundle Pricing**
   - Modify extraction to capture each year's bundle pricing as separate line items
   - Source: FIS proposal likely has a pricing schedule table

2. **Break Down Aggregated Line Items**
   - Split "Paper and Envelopes" into 2 items
   - Split "Card Production" into 3 items
   - Split "Card Suite Pro" into 3 items
   - Split "Tokenization" into 7+ items
   - Split "Zelle" into 4 items
   - Split "AvidAscend" into 5-6 items

3. **Extract Implementation Fees as Separate Line Items**
   - Create separate rows for all one-time implementation fees
   - Format: "[Product Name] Implementation Fee | One-Time | $X,XXX"

4. **Extract Implementation Credits**
   - Capture negative values (credits):
     - FIS Implementation Credits: -$844,093
     - Third Party Implementation Credits: -$137,070
     - Signing Bonus: -$50,000

### MEDIUM PRIORITY

5. **Extract Monthly Minimums Separately**
   - Split base monthly fees from variable fees
   - Example: DirectLink = $200 minimum + $0.0033 per transaction

6. **Extract Missing Products**
   - D1 Commercial ($15,000/month + $350,000 implementation)
   - Web Admin ($563/month)
   - Enterprise License ($609/month)

### LOW PRIORITY

7. **Improve Category Mapping**
   - WORKBOOK2 uses different category names than our extraction
   - Align categories to match expected output

---

## IMPACT ON TCO OUTPUT

**Missing these items causes:**

1. **Understated Total Costs**: ~50 line items missing = significant TCO understatement
2. **Incorrect Year-over-Year Projections**: Without multi-year bundle pricing, growth calculations are wrong
3. **Missing Credits**: Overstates implementation costs by ~$1.03M
4. **Inaccurate Category Breakdowns**: Aggregated items prevent accurate category analysis

**Example Impact:**
- WORKBOOK2 shows Year 1 Total: ~$400K (required fees)
- Our extraction shows: ~$15K/month = $180K/year (just the bundle)
- **Gap: ~$220K/year missing in Year 1 alone**

---

## NEXT STEPS

1. Review the source FIS proposal PDF to understand:
   - How multi-year pricing is structured
   - Where component breakdowns exist (tables, appendices)
   - Where implementation fees are listed

2. Update extraction prompts to:
   - Recognize year-by-year pricing schedules
   - Extract each component of complex products
   - Separate implementation fees from recurring fees
   - Capture negative values (credits)

3. Re-run extraction and validate against WORKBOOK2

4. Create mapping logic to transform our extraction format → WORKBOOK2 format

---

## QUESTIONS FOR CLARIFICATION

1. **Is WORKBOOK2.xlsx the definitive "ground truth" for what the extraction should produce?**

2. **Do we need to modify the AI extraction, or can we post-process the JSON to match WORKBOOK2's structure?**

3. **Should we prioritize accuracy (matching WORKBOOK2 100%) or speed (keeping current extraction with manual review)?**

4. **Is there a source mapping document that shows which proposal sections map to which WORKBOOK2 line items?**

---

**Document prepared by:** Claude Code Analysis
**Last updated:** 2026-01-13
