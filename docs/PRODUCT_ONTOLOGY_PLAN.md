# Product Ontology & Field-by-Field Comparison System

## Executive Summary

This plan implements a **hybrid product matching system** that enables true apples-to-apples comparison across vendor proposals. The system combines:
- Static product ontology (fast, deterministic, auditable)
- Fuzzy matching fallback (handles typos/variations)
- AI-assisted suggestions (for unknown products)
- Human review workflow (quality control + continuous learning)

**Goal:** When Echelon Bank receives proposals from FIS, Jack Henry, and CSI, generate a comparison showing equivalent products side-by-side with pricing.

---

## Problem Statement

### Current State
- Comparison works at **bucket level** (totals by category)
- Cannot answer: "How much does Core Banking cost across vendors?"
- No way to map "FIS HORIZON" = "JH SilverLake" = "CSI NuPoint"

### Desired State
- **Product-level comparison** across vendors
- Automatic matching of equivalent products
- Gap detection (Vendor A offers X, Vendor B doesn't)
- Self-improving system that learns from human feedback

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     PRODUCT MATCHING PIPELINE                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  EXTRACTION JSON ──────────────────────────────────────────────────┐    │
│  (FIS, JH, CSI)                                                    │    │
│                                                                    ▼    │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ STEP 1: ONTOLOGY LOOKUP                                          │  │
│  │ ─────────────────────                                            │  │
│  │ • Load product_ontology.yaml                                     │  │
│  │ • For each line item, check if vendor+product exists             │  │
│  │ • If found → assign canonical_category                           │  │
│  │ • Expected match rate: 80-90%                                    │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                         │                                               │
│                         │ Unmatched items                               │
│                         ▼                                               │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ STEP 2: FUZZY MATCHING                                           │  │
│  │ ─────────────────────                                            │  │
│  │ • Use rapidfuzz to find similar product names                    │  │
│  │ • Threshold: 85% similarity                                      │  │
│  │ • Catches: typos, abbreviations, minor variations                │  │
│  │ • Expected additional match rate: 5-10%                          │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                         │                                               │
│                         │ Still unmatched                               │
│                         ▼                                               │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ STEP 3: AI SUGGESTION (Optional)                                 │  │
│  │ ─────────────────────────────                                    │  │
│  │ • Call Claude API with unmatched product + context               │  │
│  │ • Returns: suggested match + confidence score                    │  │
│  │ • NEVER auto-accepted (goes to review queue)                     │  │
│  │ • Can be disabled for offline/cost-sensitive scenarios           │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                         │                                               │
│                         │ AI suggestions + truly unknown               │
│                         ▼                                               │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ STEP 4: HUMAN REVIEW QUEUE                                       │  │
│  │ ───────────────────────────                                      │  │
│  │ • CLI tool: python review_matches.py                             │  │
│  │ • Shows unmatched product + AI suggestion (if any)               │  │
│  │ • Human decides: accept / reject / create new / skip             │  │
│  │ • Approved matches → automatically added to ontology             │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                         │                                               │
│                         │ All products now have canonical category     │
│                         ▼                                               │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ STEP 5: GENERATE COMPARISON                                      │  │
│  │ ─────────────────────────────                                    │  │
│  │ • Group products by canonical_category                           │  │
│  │ • Create side-by-side Excel with:                                │  │
│  │   - Product names from each vendor                               │  │
│  │   - Pricing (monthly, one-time, 7-year TCO)                      │  │
│  │   - Gaps highlighted (product missing from vendor)               │  │
│  │   - Winner highlighted (lowest cost per category)                │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Data Structures

### 1. Product Ontology Schema (`ontology/product_ontology.yaml`)

```yaml
# Product Ontology for Banking Core System Vendors
# Version: 1.0
# Last Updated: 2026-01-15

metadata:
  version: "1.0"
  last_updated: "2026-01-15"
  total_categories: 25
  total_vendor_terms: 150

# Canonical product categories with vendor-specific terms
categories:

  # ═══════════════════════════════════════════════════════════════════
  # CORE BANKING
  # ═══════════════════════════════════════════════════════════════════

  core_banking_platform:
    canonical_name: "Core Banking Platform"
    description: "Primary core banking/accounting system"
    typical_cost_range: "$10,000 - $50,000/month"
    vendor_terms:
      FIS:
        - "HORIZON"
        - "Core: HORIZON"
        - "HORIZON Core"
        - "IBS"
      JACK_HENRY:
        - "SilverLake"
        - "Core: SilverLake"
        - "SilverLake System"
        - "20/20"
        - "Core Director"
      CSI:
        - "NuPoint"
        - "NuPoint Core"
      FISERV:
        - "DNA"
        - "Premier"
        - "Signature"
        - "Cleartouch"
      FINASTRA:
        - "Fusion Phoenix"
        - "Phoenix"

  # ═══════════════════════════════════════════════════════════════════
  # DIGITAL BANKING
  # ═══════════════════════════════════════════════════════════════════

  digital_banking_platform:
    canonical_name: "Digital Banking Platform"
    description: "Online and mobile banking suite"
    typical_cost_range: "$15,000 - $60,000/month"
    vendor_terms:
      FIS:
        - "D1 Flex"
        - "D1 Business"
        - "Digital: D1 Flex"
        - "Digital: D1 Flex, D1 Business, Mobile, Bill Pay"
      JACK_HENRY:
        - "Banno"
        - "Banno Digital"
        - "Banno Mobile"
        - "Banno Online"
        - "NetTeller"
      CSI:
        - "CSI Digital"
        - "NuPoint Digital"
        - "Internet Banking"
      FISERV:
        - "Architect"
        - "Corillian"
        - "Digital One"

  website_services:
    canonical_name: "Website Services"
    description: "Bank website hosting and management"
    vendor_terms:
      FIS:
        - "Website Services"
        - "Digital: Website Services"
      JACK_HENRY:
        - "Web Design"
        - "Banno Website"
      CSI:
        - "Web Services"

  zelle_p2p:
    canonical_name: "Zelle P2P Payments"
    description: "Zelle person-to-person payment service"
    vendor_terms:
      FIS:
        - "Zelle"
        - "Digital: Zelle"
        - "Zelle (Consumer and Small Business)"
      JACK_HENRY:
        - "Zelle"
        - "P2P Zelle"
      CSI:
        - "Zelle"
      FISERV:
        - "Zelle"

  # ═══════════════════════════════════════════════════════════════════
  # PAYMENTS & EFT
  # ═══════════════════════════════════════════════════════════════════

  eft_debit_processing:
    canonical_name: "EFT/Debit Processing"
    description: "Electronic funds transfer and debit card processing"
    vendor_terms:
      FIS:
        - "EFT Norcross"
        - "EFT: EFT Norcross"
        - "EFT: EFT Norcross, 3D Secure, Tokenization, SecurLOCK"
      JACK_HENRY:
        - "JHA EFT"
        - "EFT Processing"
      CSI:
        - "EFT Services"

  tokenization_security:
    canonical_name: "Tokenization & Card Security"
    description: "Card tokenization, 3D Secure, digital wallet support"
    vendor_terms:
      FIS:
        - "Tokenization"
        - "Tokenization (ApplePay, Additional Pays)"
        - "3D Secure"
        - "SecurLOCK"
      JACK_HENRY:
        - "CardValet"
        - "Card Management"
      CSI:
        - "Card Security"

  rtp_receive:
    canonical_name: "Real-Time Payments (Receive)"
    description: "RTP receive-only capability"
    vendor_terms:
      FIS:
        - "RTP (Receive)"
        - "Image Solutions: RTP (Receive)"
        - "Real-Time Payments (RTP) (Receive Only)"
      JACK_HENRY:
        - "RTP Receive"
      CSI:
        - "RTP"

  rtp_send:
    canonical_name: "Real-Time Payments (Send)"
    description: "RTP send capability"
    vendor_terms:
      FIS:
        - "RTP Send"
        - "Image Solutions: RTP Send for Business"
        - "Image Solutions: RTP Send for D1B"
      JACK_HENRY:
        - "RTP Send"

  fednow:
    canonical_name: "FedNow Instant Payments"
    description: "Federal Reserve instant payment service"
    vendor_terms:
      FIS:
        - "FedNOW"
        - "FedNOW (Receive Only)"
        - "Image Solutions: FedNOW (both Send/Receive)"
        - "Image Solutions: FedNOW (Send and Receive) D1B"
      JACK_HENRY:
        - "FedNow"
      CSI:
        - "FedNow"

  # ═══════════════════════════════════════════════════════════════════
  # TREASURY MANAGEMENT
  # ═══════════════════════════════════════════════════════════════════

  wire_transfer_business:
    canonical_name: "Wire Transfer (Business)"
    description: "Business wire transfer services"
    vendor_terms:
      FIS:
        - "eWire"
        - "eWire (Business)"
        - "Treasury: eWire (Business)"
      JACK_HENRY:
        - "JHA Wire"
        - "Wire Transfer"
      CSI:
        - "Wire Services"

  wire_transfer_consumer:
    canonical_name: "Wire Transfer (Consumer)"
    description: "Consumer wire transfer services"
    vendor_terms:
      FIS:
        - "eWire (Consumer)"
        - "Treasury: eWire (Consumer)"
      JACK_HENRY:
        - "Consumer Wire"

  account_analysis:
    canonical_name: "Account Analysis"
    description: "Treasury account analysis and reporting"
    vendor_terms:
      FIS:
        - "Extended Account Analysis"
        - "Treasury: Extended Account Analysis (XAA)"
        - "Treasury: Extended Account Analysis"
        - "XAA"
      JACK_HENRY:
        - "Account Analysis"
      CSI:
        - "Account Analysis"

  # ═══════════════════════════════════════════════════════════════════
  # ITEM PROCESSING
  # ═══════════════════════════════════════════════════════════════════

  item_processing_suite:
    canonical_name: "Item Processing Suite"
    description: "Check processing, image capture, branch capture"
    vendor_terms:
      FIS:
        - "Item Processing"
        - "Item Processing: FCM, IP, Branch Capture, CCX, FXD, DLRR"
        - "FCM"
        - "Branch Capture"
      JACK_HENRY:
        - "Synergy"
        - "Item Processing"
      CSI:
        - "Item Processing"

  remote_deposit:
    canonical_name: "Remote Deposit Capture"
    description: "Consumer and merchant remote deposit"
    vendor_terms:
      FIS:
        - "DirectLink Merchant"
        - "IP: DirectLink Merchant (via RDC)"
        - "IP: DirectLink Merchant (via RegO)"
        - "DirectLink Consumer"
        - "IP: DirectLink Consumer (via FXD)"
        - "IP: DirectLink Consumer (via FIS)"
      JACK_HENRY:
        - "Remote Deposit"
        - "RDC"
      CSI:
        - "Remote Deposit"

  chargeback_management:
    canonical_name: "Chargeback Management"
    description: "Dispute and chargeback handling"
    vendor_terms:
      FIS:
        - "Chargeback Manager"
        - "Image Solutions: Chargeback Manager"
      JACK_HENRY:
        - "Chargeback"
      CSI:
        - "Dispute Management"

  # ═══════════════════════════════════════════════════════════════════
  # RISK & FRAUD
  # ═══════════════════════════════════════════════════════════════════

  fraud_detection:
    canonical_name: "Fraud Detection & Prevention"
    description: "Fraud monitoring and prevention tools"
    vendor_terms:
      FIS:
        - "Decision Solutions"
        - "Risk, Fraud & Compliance: Decision Solutions"
        - "DirectLink Risk Review"
        - "DirectLink Risk Review (DLRR)"
        - "DLRR"
      JACK_HENRY:
        - "Fraud Detection"
        - "Enterprise Fraud"
      CSI:
        - "Fraud Prevention"

  debit_card_fraud:
    canonical_name: "Debit Card Fraud Services"
    description: "Debit card fraud case investigation and disputes"
    vendor_terms:
      FIS:
        - "Payments One Debit Card Fraud Case Investigation"
        - "Payments One Full-Service Debit Card Fraud Disputes"
      JACK_HENRY:
        - "Card Fraud Services"

  # ═══════════════════════════════════════════════════════════════════
  # LENDING
  # ═══════════════════════════════════════════════════════════════════

  loan_origination:
    canonical_name: "Loan Origination System"
    description: "Lending origination and processing"
    vendor_terms:
      FIS:
        - "FLO"
        - "Lending: FLO"
      JACK_HENRY:
        - "LOS"
        - "Loan Origination"
      CSI:
        - "Lending"

  cra_compliance:
    canonical_name: "CRA/Fair Lending Compliance"
    description: "Community Reinvestment Act compliance"
    vendor_terms:
      FIS:
        - "CRA Wiz"
        - "CRA Wiz/Fair Lending"
        - "Lending: CRA Wiz/Fair Lending"
      JACK_HENRY:
        - "CRA"
        - "Fair Lending"
      CSI:
        - "CRA Compliance"

  # ═══════════════════════════════════════════════════════════════════
  # FORMS & OUTPUT
  # ═══════════════════════════════════════════════════════════════════

  forms_output_services:
    canonical_name: "Forms & Output Services"
    description: "Statement printing, forms, eDelivery"
    vendor_terms:
      FIS:
        - "FOS"
        - "FOS: eDelivery, Print/Render, Forms & Envelopes"
        - "eDelivery"
        - "Print/Render"
        - "Paper and Envelopes"
      JACK_HENRY:
        - "Forms"
        - "Output Services"
      CSI:
        - "Forms Services"

  # ═══════════════════════════════════════════════════════════════════
  # COMPLIANCE & REPORTING
  # ═══════════════════════════════════════════════════════════════════

  regulatory_compliance:
    canonical_name: "Regulatory Compliance"
    description: "Regulatory reporting and compliance tools"
    vendor_terms:
      FIS:
        - "Regulatory Compliance"
        - "Information Services: Regulatory Compliance"
      JACK_HENRY:
        - "Compliance"
      CSI:
        - "Compliance Services"

  irs_reporting:
    canonical_name: "IRS Reporting"
    description: "Tax reporting services (1099, W-2, etc.)"
    vendor_terms:
      FIS:
        - "IRS Reporting"
        - "Information Services: IRS Reporting"
      JACK_HENRY:
        - "Tax Reporting"
      CSI:
        - "IRS Services"

  business_intelligence:
    canonical_name: "Business Intelligence/Reporting"
    description: "Analytics, reporting, dashboards"
    vendor_terms:
      FIS:
        - "IBM Cognos"
        - "IBM Cognos (HORIZON 360)"
        - "HORIZON 360"
      JACK_HENRY:
        - "Analytics"
        - "Reporting"
      CSI:
        - "Business Intelligence"

  # ═══════════════════════════════════════════════════════════════════
  # THIRD-PARTY / ANCILLARY
  # ═══════════════════════════════════════════════════════════════════

  network_connectivity:
    canonical_name: "Network Connectivity"
    description: "Data center connectivity, network services"
    vendor_terms:
      FIS:
        - "Network Services"
        - "Network Services (connectivity to data center)"
        - "Network: Network Connectivity Services"
      JACK_HENRY:
        - "Network"
        - "Connectivity"
      CSI:
        - "Network Services"

  esignature:
    canonical_name: "eSignature"
    description: "Electronic signature services"
    vendor_terms:
      FIS:
        - "SmartSign"
        - "SmartSign (eSignature)"
      JACK_HENRY:
        - "eSign"
        - "DocuSign"
      CSI:
        - "eSignature"

  document_services:
    canonical_name: "Document Services"
    description: "Account documents, disclosures"
    vendor_terms:
      FIS:
        - "TruStage"
        - "TruStage (new deposit account documents)"
      JACK_HENRY:
        - "Document Services"
      CSI:
        - "Documents"

  debit_card_production:
    canonical_name: "Debit Card Production"
    description: "Card production and fulfillment"
    vendor_terms:
      FIS:
        - "Debit Card Production"
        - "CardPro Connect"
        - "EFT: Debit Card Production"
      JACK_HENRY:
        - "Card Production"
      CSI:
        - "Card Production"

  debit_card_network:
    canonical_name: "Debit Card Network"
    description: "Card network participation (NYCE, STAR, etc.)"
    vendor_terms:
      FIS:
        - "NYCE"
        - "NYCE Preferred Debit Card Network"
        - "EFT: NYCE Debit Card Network"
      JACK_HENRY:
        - "STAR"
        - "Card Network"
      CSI:
        - "Network Fees"
```

### 2. Match Review Queue Schema (`ontology/review_queue.json`)

```json
{
  "queue_metadata": {
    "created_at": "2026-01-15T10:00:00Z",
    "last_updated": "2026-01-15T14:32:00Z",
    "pending_reviews": 3,
    "completed_today": 5
  },
  "pending_items": [
    {
      "item_id": "review_001",
      "created_at": "2026-01-15T14:30:00Z",
      "source_comparison": "echelon_bank",
      "unmatched_product": {
        "vendor": "CSI",
        "solution_name": "NuPoint Advanced Teller",
        "category": "Core Banking",
        "monthly_fee": 2450.00,
        "context": "Line item from CSI proposal table 2, row 5"
      },
      "ai_suggestion": {
        "suggested_category": "core_banking_platform",
        "suggested_match": "FIS HORIZON Teller module",
        "confidence": 0.78,
        "reasoning": "Both are teller-facing modules within core banking"
      },
      "skip_count": 0,
      "assigned_to": null
    }
  ],
  "completed_items": [
    {
      "item_id": "review_000",
      "completed_at": "2026-01-15T14:25:00Z",
      "reviewer": "john.smith",
      "decision": "accept_ai_suggestion",
      "time_to_review_seconds": 18,
      "added_to_ontology": true
    }
  ]
}
```

### 3. Match Audit Log Schema (`ontology/audit_log.json`)

```json
{
  "audit_entries": [
    {
      "audit_id": "audit_20260115_001",
      "timestamp": "2026-01-15T14:32:00Z",
      "action": "product_matched",
      "reviewer": "john.smith@bank.com",
      "source_product": {
        "vendor": "CSI",
        "name": "NuPoint Advanced Teller"
      },
      "matched_to": {
        "canonical_category": "core_banking_platform",
        "category_name": "Core Banking Platform"
      },
      "match_method": "human_approved_ai_suggestion",
      "ai_confidence": 0.78,
      "ontology_updated": true,
      "new_term_added": "NuPoint Advanced Teller"
    }
  ]
}
```

---

## Implementation Phases

### Phase 1: Foundation (Core Data Structures)
**Estimated effort: 2-3 hours**

| Task | Description | Files |
|------|-------------|-------|
| 1.1 | Create product ontology YAML with initial ~25 categories | `ontology/product_ontology.yaml` |
| 1.2 | Create ProductMatcher class with ontology loading | `core/product_matcher.py` |
| 1.3 | Implement exact match lookup | `core/product_matcher.py` |
| 1.4 | Add unit tests for matcher | `tests/test_product_matcher.py` |

**Deliverable:** Can load ontology and match known products.

---

### Phase 2: Fuzzy Matching
**Estimated effort: 1-2 hours**

| Task | Description | Files |
|------|-------------|-------|
| 2.1 | Add fuzzy matching with rapidfuzz | `core/product_matcher.py` |
| 2.2 | Implement configurable threshold | `core/product_matcher.py` |
| 2.3 | Add match confidence scoring | `core/product_matcher.py` |
| 2.4 | Test with variations/typos | `tests/test_product_matcher.py` |

**Deliverable:** Can match "D1Flex" to "D1 Flex", "HORIZION" to "HORIZON".

---

### Phase 3: AI Suggestion (Optional)
**Estimated effort: 2-3 hours**

| Task | Description | Files |
|------|-------------|-------|
| 3.1 | Create AI suggestion prompt template | `config/matching_prompts.py` |
| 3.2 | Implement Claude API call for suggestions | `core/product_matcher.py` |
| 3.3 | Parse AI response with confidence | `core/product_matcher.py` |
| 3.4 | Add enable/disable flag | `core/product_matcher.py` |

**Deliverable:** Unknown products get AI suggestions with confidence scores.

---

### Phase 4: Human Review CLI
**Estimated effort: 3-4 hours**

| Task | Description | Files |
|------|-------------|-------|
| 4.1 | Create review queue data structure | `ontology/review_queue.json` |
| 4.2 | Build CLI review tool | `review_matches.py` |
| 4.3 | Implement decision handlers | `review_matches.py` |
| 4.4 | Auto-update ontology on approval | `core/product_matcher.py` |
| 4.5 | Create audit logging | `ontology/audit_log.json` |

**Deliverable:** `python review_matches.py` provides interactive review workflow.

---

### Phase 5: Enhanced Comparison Output
**Estimated effort: 3-4 hours**

| Task | Description | Files |
|------|-------------|-------|
| 5.1 | Integrate matcher into comparison generator | `generate_comparison.py` |
| 5.2 | Add product-level comparison tab | `generate_comparison.py` |
| 5.3 | Add gap detection (missing products) | `generate_comparison.py` |
| 5.4 | Add match confidence indicators | `generate_comparison.py` |
| 5.5 | Create contract terms comparison tab | `generate_comparison.py` |

**Deliverable:** Excel output with field-by-field product comparison.

---

### Phase 6: Documentation & Polish
**Estimated effort: 1-2 hours**

| Task | Description | Files |
|------|-------------|-------|
| 6.1 | Create user guide for reviewers | `docs/REVIEWER_GUIDE.md` |
| 6.2 | Document ontology maintenance | `docs/ONTOLOGY_GUIDE.md` |
| 6.3 | Add CLI help text | `review_matches.py` |
| 6.4 | Update README | `README.md` |

**Deliverable:** Complete documentation for users and maintainers.

---

## File Structure

```
tco_automation/
├── ontology/                          # NEW DIRECTORY
│   ├── product_ontology.yaml          # Master product mappings
│   ├── review_queue.json              # Pending human reviews
│   ├── audit_log.json                 # Match decision history
│   └── README.md                      # Ontology documentation
│
├── core/
│   ├── product_matcher.py             # NEW: Main matching engine
│   ├── cost_normalizer.py             # Existing (minor updates)
│   └── ...
│
├── config/
│   ├── matching_prompts.py            # NEW: AI prompt templates
│   └── ...
│
├── docs/
│   ├── PRODUCT_ONTOLOGY_PLAN.md       # This document
│   ├── REVIEWER_GUIDE.md              # NEW: How to review matches
│   └── ONTOLOGY_GUIDE.md              # NEW: How to maintain ontology
│
├── tests/
│   ├── test_product_matcher.py        # NEW: Matcher tests
│   └── ...
│
├── generate_comparison.py             # MODIFIED: Add product-level comparison
├── review_matches.py                  # NEW: CLI review tool
└── ...
```

---

## Success Criteria

### Functional Requirements
- [ ] Match 90%+ of products automatically (ontology + fuzzy)
- [ ] AI suggestions for unknown products (when enabled)
- [ ] Human review workflow with <30 second average review time
- [ ] Automatic ontology updates on approval
- [ ] Full audit trail for all match decisions

### Output Requirements
- [ ] Excel comparison shows product-by-product pricing
- [ ] Gaps highlighted (product in one vendor, not others)
- [ ] Lowest cost highlighted per product category
- [ ] Match confidence visible for transparency

### Quality Requirements
- [ ] All match decisions auditable
- [ ] Ontology version controlled (YAML in git)
- [ ] Review queue persists across sessions
- [ ] Graceful handling of API failures

---

## Open Questions for Discussion

1. **AI Usage:** Should AI suggestions be enabled by default, or opt-in?
   - Pro: Better coverage for unknown products
   - Con: API cost, latency, potential hallucinations

2. **Review Assignment:** Should reviews be assigned to specific users?
   - Pro: Accountability
   - Con: Bottleneck if person unavailable

3. **Auto-Approval Threshold:** Should very high confidence matches (>95%) auto-approve?
   - Pro: Reduces review burden
   - Con: Risk of bad matches slipping through

4. **Ontology Storage:** YAML file vs database?
   - YAML: Simple, version controlled, easy to edit
   - DB: Better for large scale, query support

5. **Escalation:** What happens to items skipped multiple times?
   - Option A: Flag for senior review
   - Option B: Mark as "unique" and exclude from comparison
   - Option C: Leave unmatched (show as separate row)

---

## Next Steps

1. Review this plan and provide feedback
2. Agree on open questions
3. Begin Phase 1 implementation
4. Iterate based on real-world testing

---

*Document created: 2026-01-15*
*Author: Claude + Human collaboration*
*Branch: feature/product-ontology-matching*
