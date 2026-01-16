# Product Ontology Maintenance Guide

This guide explains how to maintain and extend the product ontology that powers cross-vendor comparison.

## Overview

The **Product Ontology** (`ontology/product_ontology.yaml`) is the master reference for mapping vendor-specific product names to canonical categories. It enables:

- Automatic product matching across vendors
- Apples-to-apples comparison of equivalent products
- Gap detection (products offered by some vendors but not others)

---

## File Structure

```
ontology/
├── product_ontology.yaml       # Master product mappings (VERSION CONTROLLED)
├── auto_approved_matches.json  # Log of auto-approved matches (audit trail)
├── review_queue.json           # Pending human reviews (transient)
└── review_audit_log.json       # All human review decisions (audit trail)
```

---

## Ontology Schema

### Basic Structure

```yaml
metadata:
  version: "1.0"
  last_updated: "2026-01-15"
  total_categories: 60
  total_vendor_terms: 400

categories:
  category_key:
    canonical_name: "Human Readable Name"
    description: "What this category covers"
    typical_cost_range: "$X - $Y/month"
    vendor_terms:
      FIS:
        - "Term 1"
        - "Term 2"
      JACK_HENRY:
        - "Term A"
        - "Term B"
      CSI:
        - "Term X"
```

### Category Fields

| Field | Required | Description |
|-------|----------|-------------|
| `canonical_name` | Yes | Human-readable category name |
| `description` | Yes | Brief description of what products belong here |
| `typical_cost_range` | No | Reference cost range for sanity checks |
| `vendor_terms` | Yes | Dict of vendor -> list of product names |

### Supported Vendors

```yaml
FIS          # HORIZON, Digital One, Payments One
JACK_HENRY   # SilverLake, Banno, Symitar
CSI          # NuPoint
FISERV       # DNA, Premier, Signature
FINASTRA     # Fusion Phoenix
```

---

## Common Tasks

### Adding a New Term to Existing Category

When a product isn't matching but should belong to an existing category:

**Option 1: Edit YAML directly**

```yaml
# In ontology/product_ontology.yaml
core_banking_platform:
  vendor_terms:
    FIS:
      - "HORIZON"
      - "Core: HORIZON"
      - "HORIZON Core Module"  # ← Add new term here
```

**Option 2: Use the review CLI**

```bash
python review_matches.py
# When the item appears, choose [C] and select the category
# The term is automatically added to the ontology
```

**Option 3: Programmatic addition**

```python
from core.product_matcher import ProductMatcher

matcher = ProductMatcher()
matcher.add_term_to_ontology(
    category_key="core_banking_platform",
    vendor="FIS",
    new_term="HORIZON Core Module"
)
```

### Adding a New Category

When products don't fit any existing category:

1. **Choose a category key** (lowercase, underscores)
2. **Define canonical name** (human-readable)
3. **Add description**
4. **Map vendor terms**

Example:

```yaml
# Add to ontology/product_ontology.yaml

instant_payments:
  canonical_name: "Instant Payments Platform"
  description: "Unified instant payment services (RTP + FedNow)"
  typical_cost_range: "$1,000 - $5,000/month"
  vendor_terms:
    FIS:
      - "Instant Payments Suite"
      - "RTP/FedNow Bundle"
    JACK_HENRY:
      - "Real-Time Payments"
    FISERV:
      - "NOW Network"
```

### Adding a New Vendor

To support a new vendor:

1. Add terms to existing categories where the vendor has equivalent products
2. Use `None` or empty list for categories the vendor doesn't offer

```yaml
core_banking_platform:
  vendor_terms:
    FIS:
      - "HORIZON"
    NEW_VENDOR:
      - "Their Core Product"
      - "Their Core Pro"
```

---

## Naming Conventions

### Category Keys
- Lowercase with underscores
- Descriptive but concise
- Examples: `core_banking_platform`, `wire_transfer_business`, `fraud_detection`

### Vendor Codes
- Uppercase
- Use underscores for multi-word names
- Standard codes: `FIS`, `JACK_HENRY`, `CSI`, `FISERV`, `FINASTRA`

### Product Terms
- Match exactly as they appear in proposals
- Include common variations
- Preserve prefixes (e.g., "Core:", "Digital:", "Treasury:")

---

## Best Practices

### 1. Be Comprehensive with Variations

Include all ways a product might appear:

```yaml
digital_banking_platform:
  vendor_terms:
    FIS:
      - "D1 Flex"
      - "Digital: D1 Flex"
      - "D1 Flex Digital Banking"
      - "Digital: D1 Flex, D1 Business, Mobile, Bill Pay"
```

### 2. Use Prefixes Consistently

Vendors often prefix product names by category:
- `Core:` - Core banking
- `Digital:` - Digital/online banking
- `Treasury:` - Treasury management
- `EFT:` - Electronic funds transfer
- `IP:` - Item processing

Include both prefixed and non-prefixed versions.

### 3. Document Reasoning

Use YAML comments for non-obvious mappings:

```yaml
tokenization_security:
  vendor_terms:
    FIS:
      - "SecurLOCK"  # Card security app, often bundled with tokenization
      - "3D Secure"
```

### 4. Keep Categories Granular

- Avoid catch-all categories
- Split if products serve different functions
- Example: `wire_transfer_business` and `wire_transfer_consumer` are separate

### 5. Version Control Changes

- All changes to `product_ontology.yaml` are tracked in git
- Use descriptive commit messages
- Review changes in PR before merging

---

## Category Reference

### Core Banking
| Category Key | Description |
|--------------|-------------|
| `core_banking_platform` | Primary core/accounting system |
| `hosting_services` | Core system hosting |

### Digital Banking
| Category Key | Description |
|--------------|-------------|
| `digital_banking_platform` | Online/mobile banking suite |
| `mobile_banking` | Mobile banking app |
| `bill_pay` | Bill payment services |
| `website_services` | Bank website hosting |
| `zelle_p2p` | Zelle P2P payments |

### Payments & EFT
| Category Key | Description |
|--------------|-------------|
| `eft_debit_processing` | EFT/debit card processing |
| `ach_processing` | ACH transaction processing |
| `rtp_receive` | Real-time payments (receive) |
| `rtp_send` | Real-time payments (send) |
| `fednow` | FedNow instant payments |

### Treasury Management
| Category Key | Description |
|--------------|-------------|
| `treasury_management_suite` | Full treasury suite |
| `wire_transfer_business` | Business wire services |
| `wire_transfer_consumer` | Consumer wire services |
| `positive_pay` | Check fraud prevention |
| `remote_deposit` | Remote deposit capture |
| `lockbox_services` | Lockbox processing |

### Risk & Compliance
| Category Key | Description |
|--------------|-------------|
| `fraud_detection` | Fraud monitoring/prevention |
| `fraud_analytics` | Fraud analysis tools |
| `regulatory_compliance` | Regulatory reporting |
| `cra_compliance` | CRA/fair lending |
| `irs_reporting` | Tax reporting |

### Implementation
| Category Key | Description |
|--------------|-------------|
| `core_implementation` | Core system implementation |
| `data_migration` | Data conversion/migration |
| `training_services` | User training |
| `project_management` | Implementation PM |

---

## Troubleshooting

### "Term not matching even though it's in ontology"

1. Check for exact character match (spaces, capitalization)
2. Verify the vendor code matches
3. Try reloading: `matcher.reload_ontology()`

### "YAML parse error"

Common causes:
- Missing quotes around strings with special characters
- Incorrect indentation (use 2 spaces, not tabs)
- Unescaped colons in values

### "Category key not found"

- Ensure category key is lowercase with underscores
- Check spelling matches exactly
- Verify the category exists in the file

### "Merge conflicts in ontology"

The YAML structure is designed to minimize conflicts:
- Categories are alphabetically ordered
- Vendor terms are listed under each category
- Add new terms at the end of vendor lists

---

## Validation

### Run Tests

```bash
python -m pytest tests/test_product_matcher.py -v
```

### Check Match Rate

```python
from core.product_matcher import ProductMatcher, print_match_summary

matcher = ProductMatcher()
results = matcher.match_batch(your_items)
print_match_summary(results, matcher)
```

### Validate Ontology Structure

```python
import yaml

with open('ontology/product_ontology.yaml') as f:
    data = yaml.safe_load(f)

print(f"Categories: {len(data['categories'])}")
print(f"Last updated: {data['metadata']['last_updated']}")
```

---

## Related Documentation

- [REVIEWER_GUIDE.md](REVIEWER_GUIDE.md) - How to review product matches
- [IMPLEMENTATION_LOG.md](IMPLEMENTATION_LOG.md) - Technical implementation details
- [PRODUCT_ONTOLOGY_PLAN.md](PRODUCT_ONTOLOGY_PLAN.md) - Original design document

---

*Last updated: 2026-01-15*
