# Product Match Reviewer Guide

This guide explains how to review and approve product matches in the TCO Automation system.

## Overview

When extracting vendor proposals, the system matches product names to canonical categories using:
1. **Exact matching** - Known terms from the product ontology
2. **Fuzzy matching** - Similar terms with typos or variations
3. **AI suggestions** - Claude AI suggestions for unknown products

Products that can't be matched automatically are placed in a **review queue** for human verification.

---

## Quick Start

```bash
# Load extractions and populate the review queue
python review_matches.py --load "Extracted JSON"

# View queue statistics
python review_matches.py --stats

# Start reviewing items
python review_matches.py

# Export unmatched products to CSV
python review_matches.py --export
```

---

## Review Process

### 1. Loading Items

Before reviewing, load extraction files to populate the queue:

```bash
python review_matches.py --load "Extracted JSON"
```

This will:
- Scan all `*_extraction_ai.json` files
- Run the product matcher on each item
- Add unmatched items to the review queue
- Show statistics when complete

### 2. Viewing Queue Statistics

Check the current state of the queue:

```bash
python review_matches.py --stats
```

Output example:
```
REVIEW QUEUE STATISTICS
==============================
Pending reviews:     45
Completed reviews:   23
Skipped (3+ times):  5
Total processed:     28
Ontology categories: 60
==============================
```

### 3. Interactive Review

Start an interactive review session:

```bash
python review_matches.py
```

For each item, you'll see:
```
============================================================
REVIEW ITEM 1 of 45
============================================================
Product Name: Treasury: ACH Plus Services
Vendor:       FIS
Source File:  echelon_bank_fis_extraction_ai.json
Category:     Treasury Management

AI Suggestion: ach_processing (75% confidence)
Reasoning:     "ACH Plus indicates ACH processing services"

What would you like to do?
  [A] Accept AI suggestion (ach_processing)
  [C] Choose from category list
  [S] Skip this item
  [Q] Quit review session

Your choice:
```

### 4. Making Decisions

#### Accept AI Suggestion [A]
- Adds the product term to the suggested category in the ontology
- The term will match automatically in future extractions
- Logged in audit trail

#### Choose Category [C]
- Shows a numbered list of all 60+ categories
- Enter the number to select a category
- If the suggestion doesn't seem right, you can choose a different one

#### Skip [S]
- Moves the item to the end of the queue
- After 3 skips, item is marked as "skipped" (excluded from main queue)
- Skipped items appear in the "Unmatched Products" tab in Excel output

#### Quit [Q]
- Saves progress and exits
- All decisions are saved automatically
- Resume anytime

---

## Understanding Match Types

### Exact Match (100% confidence)
- The product name was found verbatim in the ontology
- No review needed - automatically approved

### Fuzzy Match (85-99% confidence)
- Similar to a known term (typo, abbreviation, etc.)
- If >= 95%: Auto-approved
- If < 95%: Needs quick verification

### AI Suggestion (50-100% confidence)
- Claude AI analyzed the product name and suggested a category
- **Always needs human review** - AI suggestions are never auto-approved
- Review the reasoning provided to decide

### Unmatched (0% confidence)
- No match or suggestion found
- Requires manual categorization from the full list

---

## Best Practices

### 1. Review High-Impact Items First
Products with higher costs should be prioritized. The queue is sorted by 7-year TCO impact.

### 2. Use Context Clues
- Look at the vendor prefix (Core:, Digital:, Treasury:, etc.)
- Check the source file for more context
- Consider what similar products you've seen

### 3. When to Skip
Skip if:
- The product is vendor-specific with no equivalent
- You're unsure and want someone else to review
- Need more research before deciding

### 4. Adding New Categories
If a product doesn't fit any existing category:
1. Skip the item
2. Contact the ontology maintainer
3. A new category can be added to `product_ontology.yaml`

### 5. Quality Over Speed
- It's better to skip and come back than to make incorrect matches
- Incorrect matches affect comparison accuracy
- All decisions are logged for audit

---

## Audit Trail

Every decision is logged in `ontology/review_audit_log.json`:

```json
{
  "timestamp": "2026-01-15T14:32:00",
  "reviewer": "john.smith",
  "action": "accept_ai_suggestion",
  "product_name": "Treasury: ACH Plus",
  "vendor": "FIS",
  "assigned_category": "ach_processing",
  "ai_confidence": 75,
  "source_file": "echelon_bank_fis_extraction_ai.json"
}
```

This provides:
- Full traceability for compliance
- Learning data for improving the ontology
- Accountability for decisions

---

## Troubleshooting

### "No items to review"
- Run `--load` first to populate the queue
- Check if all items have been reviewed or skipped

### "AI suggestions disabled"
- The `ANTHROPIC_API_KEY` environment variable is not set
- AI suggestions require a valid API key
- The system will still work with exact and fuzzy matching

### "Category not found"
- The ontology may have been updated
- Reload the matcher: `matcher.reload_ontology()`

### "Queue file corrupted"
- Delete `ontology/review_queue.json`
- Re-run `--load` to rebuild the queue

---

## Command Reference

| Command | Description |
|---------|-------------|
| `python review_matches.py` | Start interactive review |
| `python review_matches.py --load <dir>` | Load extractions and populate queue |
| `python review_matches.py --stats` | Show queue statistics |
| `python review_matches.py --export` | Export unmatched to CSV |
| `python review_matches.py --no-ai` | Disable AI suggestions |
| `python review_matches.py --help` | Show all options |

---

## Related Documentation

- [ONTOLOGY_GUIDE.md](ONTOLOGY_GUIDE.md) - How to maintain the product ontology
- [IMPLEMENTATION_LOG.md](IMPLEMENTATION_LOG.md) - Technical implementation details
- [PRODUCT_ONTOLOGY_PLAN.md](PRODUCT_ONTOLOGY_PLAN.md) - Original design document

---

*Last updated: 2026-01-15*
