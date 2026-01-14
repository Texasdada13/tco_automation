# TCO Automation - TCO Methodology Guide

**Total Cost of Ownership Analysis Framework**

---

## Table of Contents

- [Overview](#overview)
- [What is TCO?](#what-is-tco)
- [TCO Components](#tco-components)
- [Multi-Year Projections](#multi-year-projections)
- [Vendor Comparison Framework](#vendor-comparison-framework)
- [Calculation Methodology](#calculation-methodology)
- [Category Classification](#category-classification)
- [Growth Rate Application](#growth-rate-application)
- [Best Practices](#best-practices)

---

## Overview

This guide explains the Total Cost of Ownership (TCO) methodology used by the TCO Automation System. Understanding this methodology is essential for accurate vendor comparison and financial analysis.

---

## What is TCO?

### Definition

**Total Cost of Ownership (TCO)** is a financial estimate that helps determine the direct and indirect costs of a product or system over its lifetime. For vendor software solutions, TCO includes:

- Initial purchase/licensing costs
- Implementation and setup fees
- Recurring operational costs
- Maintenance and support
- Training and change management
- Infrastructure requirements
- Hidden costs and growth projections

### Why TCO Matters

| Factor | Impact |
|--------|--------|
| **True Cost Visibility** | See beyond initial pricing to total commitment |
| **Vendor Comparison** | Compare apples-to-apples across vendors |
| **Budget Planning** | Accurate multi-year financial forecasting |
| **Negotiation Leverage** | Identify high-cost areas for negotiation |
| **Risk Assessment** | Understand long-term financial implications |

---

## TCO Components

### Cost Categories

The TCO Automation System organizes costs into the following categories:

#### 1. Bundle Costs

**Definition**: Core system/platform costs typically sold as a package.

**Characteristics**:
- Primary vendor solution
- Usually non-negotiable
- Includes base functionality
- Subject to CPI increases

**Examples**:
- FIS HORIZON Bundle
- Jack Henry SilverLake System
- Core processing platform
- Digital banking suite

#### 2. Non-Bundle Required Costs

**Definition**: Additional products/services required for operation but not included in the bundle.

**Characteristics**:
- Necessary for full functionality
- May have volume-based pricing
- Often overlooked in initial quotes
- Subject to growth projections

**Examples**:
- Statement processing
- Paper/forms/envelopes
- Required integrations
- Compliance modules

#### 3. Non-Bundle Optional Costs

**Definition**: Products/services that are optional but may add value.

**Characteristics**:
- Nice-to-have features
- Can be deferred or eliminated
- Negotiation opportunities
- May become required later

**Examples**:
- Advanced reporting
- Mobile add-ons
- Premium support
- Custom integrations

#### 4. Third-Party Costs

**Definition**: Costs for products/services from vendors other than the primary.

**Characteristics**:
- May be required or optional
- Different pricing structures
- Separate support relationships
- Integration complexity

**Examples**:
- Card processing networks
- ATM/ITM providers
- Specialized software
- Consulting services

#### 5. One-Time Costs

**Definition**: Non-recurring costs typically incurred during implementation.

**Characteristics**:
- Upfront investment
- Implementation phase
- May be amortized
- Negotiation opportunities

**Examples**:
- Implementation fees
- Data conversion
- Training
- Custom development
- License fees

---

## Multi-Year Projections

### Supported Terms

| Term | Years | Use Case |
|------|-------|----------|
| 5-Year | 1-5 | Standard contracts |
| 7-Year | 1-7 | Extended contracts |
| 10-Year | 1-10 | Long-term planning |

### Projection Components

#### Year 1 (Base Year)

```
Year 1 Cost = Base Monthly Fee × 12
            + Annual Fees
            + One-Time Fees (amortized or full)
```

#### Years 2-N (Growth Years)

```
Year N Cost = Year (N-1) Cost × (1 + Growth Rate)
            + CPI Adjustment
            + Volume Growth
```

### Growth Assumptions

| Cost Type | Default Growth | Rationale |
|-----------|---------------|-----------|
| Bundle | 6% CPI | Contractual increase |
| Non-Bundle | 3% CPI | Lower increase rate |
| Third-Party | 5% CPI | Market average |
| One-Time | 0% | Non-recurring |

---

## Vendor Comparison Framework

### Side-by-Side Analysis

The TCO template enables direct vendor comparison:

```
┌─────────────────────────────────────────────────────────────┐
│                     TCO Template                             │
├─────────────────────────────┬───────────────────────────────┤
│         FIS Section         │      Jack Henry Section        │
│       (Columns B-Y)         │       (Columns AO-BL)         │
├─────────────────────────────┼───────────────────────────────┤
│ Bundle Items                │ Bundle Items                   │
│ Non-Bundle Required         │ Non-Bundle Required            │
│ Non-Bundle Optional         │ Non-Bundle Optional            │
│ One-Time Costs              │ One-Time Costs                 │
├─────────────────────────────┼───────────────────────────────┤
│ TOTAL FIS TCO               │ TOTAL JH TCO                  │
└─────────────────────────────┴───────────────────────────────┘
```

### Comparison Metrics

| Metric | Calculation |
|--------|-------------|
| **Total 7-Year TCO** | Sum of all costs over 7 years |
| **Average Annual Cost** | Total TCO ÷ 7 |
| **Year 1 Investment** | One-Time + Year 1 Recurring |
| **Break-Even Point** | When cumulative costs equal |
| **Cost Difference** | Vendor A TCO - Vendor B TCO |
| **Percentage Difference** | (Difference ÷ Higher TCO) × 100 |

### Comparison Categories

| Category | FIS Total | JH Total | Difference |
|----------|-----------|----------|------------|
| Bundle | $X,XXX,XXX | $X,XXX,XXX | $XXX,XXX |
| Non-Bundle Required | $XXX,XXX | $XXX,XXX | $XX,XXX |
| Non-Bundle Optional | $XX,XXX | $XX,XXX | $X,XXX |
| Third-Party | $XXX,XXX | $XXX,XXX | $XX,XXX |
| One-Time | $XXX,XXX | $XXX,XXX | $XX,XXX |
| **TOTAL TCO** | **$X,XXX,XXX** | **$X,XXX,XXX** | **$XXX,XXX** |

---

## Calculation Methodology

### Monthly to Annual Conversion

```
Annual Fee = Monthly Fee × 12
```

### Multi-Year Calculation

```python
def calculate_multi_year_cost(base_cost, years, cpi_rate):
    costs = []
    current_cost = base_cost

    for year in range(1, years + 1):
        costs.append(current_cost)
        current_cost = current_cost * (1 + cpi_rate)

    return costs
```

### Total TCO Calculation

```
Total TCO = Σ(Annual Costs for all years)
          + Σ(One-Time Costs)

Where Annual Costs = Bundle + Non-Bundle + Third-Party
```

### Quantity-Based Calculation

```
Annual Cost = Per Unit Rate × Quantity × 12 (if monthly)
            = Per Unit Rate × Quantity (if annual)
```

### Volume Growth

```
Year N Quantity = Year 1 Quantity × (1 + Growth Rate)^(N-1)

Year N Cost = Year N Quantity × Unit Rate × CPI Adjustment
```

---

## Category Classification

### Classification Logic

```
┌─────────────────────────────────────────┐
│           Product/Service               │
└─────────────────┬───────────────────────┘
                  │
         Is it bundled?
          ┌───────┴───────┐
         Yes              No
          │               │
     "Bundle"       Is it required?
                    ┌─────┴─────┐
                   Yes          No
                    │           │
              Is it 3rd party?  Is it 3rd party?
              ┌────┴────┐      ┌────┴────┐
             Yes        No    Yes        No
              │         │      │         │
         "Third-Party  "Non-Bundle  "Third-Party  "Non-Bundle
          Required"    Required"    Optional"     Optional"
```

### Keyword-Based Classification

**FIS Classification**:
```python
if any(keyword in product_name for keyword in FIS_BUNDLE_KEYWORDS):
    return 'Bundle'
elif any(keyword in product_name for keyword in FIS_THIRD_PARTY_KEYWORDS):
    return 'Third-Party Required'
else:
    return 'Non-Bundle Required'
```

**Jack Henry Classification**:
```python
product_family = get_product_family(product_name)
if product_family in ['SilverLake', 'Xperience']:
    return 'Bundle'
elif is_optional:
    return 'Non-Bundle Optional'
else:
    return 'Non-Bundle Required'
```

---

## Growth Rate Application

### CPI (Cost Per Item) Application

```
Year N Rate = Year 1 Rate × (1 + CPI)^(N-1)

Example (6% CPI):
Year 1: $10,000
Year 2: $10,000 × 1.06 = $10,600
Year 3: $10,600 × 1.06 = $11,236
Year 4: $11,236 × 1.06 = $11,910
Year 5: $11,910 × 1.06 = $12,625
Year 6: $12,625 × 1.06 = $13,382
Year 7: $13,382 × 1.06 = $14,185
```

### Volume Growth Application

```
Year N Quantity = Year 1 Quantity × (1 + Growth)^(N-1)

Example (20% growth):
Year 1: 1,000 units
Year 2: 1,000 × 1.20 = 1,200 units
Year 3: 1,200 × 1.20 = 1,440 units
...
```

### Combined Effect

```
Year N Cost = (Base Rate × CPI Adjustment) × (Quantity × Volume Growth)
            = Year 1 Rate × (1 + CPI)^(N-1) × Year 1 Qty × (1 + Growth)^(N-1)
```

---

## Best Practices

### Data Accuracy

1. **Verify Source Data**: Double-check extracted values against proposals
2. **Validate Calculations**: Confirm annual = monthly × 12
3. **Cross-Reference**: Compare similar items across vendors
4. **Document Assumptions**: Note growth rates and exclusions

### Completeness

1. **Include All Costs**: Don't overlook small items
2. **Consider Hidden Costs**: Implementation, training, integration
3. **Account for Growth**: Volume and rate increases
4. **Plan for Contingency**: Add buffer for unknowns

### Consistency

1. **Use Same Term**: Compare 7-year to 7-year
2. **Apply Same Growth**: Consistent CPI across vendors
3. **Normalize Categories**: Map to standard structure
4. **Document Methodology**: Explain any deviations

### Analysis

1. **Calculate Totals**: Overall and by category
2. **Identify Drivers**: What costs the most?
3. **Find Opportunities**: Where can you negotiate?
4. **Consider Qualitative**: Not just cheapest = best

---

## Example TCO Analysis

### Scenario: 7-Year Comparison

**Input Data**:
- FIS Bundle: $15,000/month
- FIS Non-Bundle: $5,000/month
- JH Bundle: $14,000/month
- JH Non-Bundle: $6,500/month

**Calculations**:

| Year | FIS Bundle | FIS Non-Bundle | FIS Total | JH Bundle | JH Non-Bundle | JH Total |
|------|------------|----------------|-----------|-----------|---------------|----------|
| 1 | $180,000 | $60,000 | $240,000 | $168,000 | $78,000 | $246,000 |
| 2 | $190,800 | $61,800 | $252,600 | $178,080 | $80,340 | $258,420 |
| 3 | $202,248 | $63,654 | $265,902 | $188,765 | $82,750 | $271,515 |
| 4 | $214,383 | $65,564 | $279,947 | $200,091 | $85,232 | $285,323 |
| 5 | $227,246 | $67,531 | $294,777 | $212,096 | $87,789 | $299,885 |
| 6 | $240,881 | $69,557 | $310,438 | $224,822 | $90,423 | $315,245 |
| 7 | $255,334 | $71,644 | $326,978 | $238,312 | $93,135 | $331,447 |
| **TOTAL** | **$1,510,892** | **$459,750** | **$1,970,642** | **$1,410,166** | **$597,669** | **$2,007,835** |

**Analysis**:
- FIS 7-Year TCO: $1,970,642
- JH 7-Year TCO: $2,007,835
- Difference: $37,193 (JH higher)
- Percentage: 1.9% difference

**Conclusion**: FIS slightly lower TCO, but difference is minimal. Consider qualitative factors.

---

## TCO Template Structure

### Line Items Sheet Layout

| Row Range | FIS Content | JH Content |
|-----------|-------------|------------|
| 7-21 | Bundle Items | Bundle Items |
| 22-99 | Non-Bundle Required | - |
| 50-99 | - | Non-Bundle Required |
| 100-149 | Non-Bundle Optional | Non-Bundle Optional |
| 150+ | One-Time Costs | One-Time Costs |
| 200+ | Totals & Summary | Totals & Summary |

### Column Layout

**FIS Columns (B-Y)**:
- B: Fee Type
- C-I: Quantities by Year
- O: Solution Name
- P: Category
- Q: Per Unit Rate
- S-Y: Costs by Year

**JH Columns (AO-BL)**:
- AO: Fee Type
- AP-AV: Quantities by Year
- BB: Solution Name
- BC: Category
- BD: Per Unit Rate
- BF-BL: Costs by Year

---

## Summary

The TCO methodology provides a comprehensive framework for:

1. **Organizing** vendor costs into standard categories
2. **Projecting** costs over multiple years
3. **Comparing** vendors on equal terms
4. **Analyzing** total financial impact
5. **Supporting** informed decision-making

By following this methodology consistently, organizations can make better vendor selection decisions based on true total cost rather than initial pricing alone.

---

*Last Updated: December 2024*
