# Processed Extractions

This folder contains extraction JSON files that have been corrected for data quality issues.

## Data Quality Issue Identified (2026-01-15)

**Issue:** All three Echelon Bank extraction files have incorrect vendor assignments

| Filename | Expected Vendor | Actual Vendor Field | Content Analysis |
|----------|----------------|---------------------|------------------|
| `echelon_bank_JH_extraction_ai.json` | JACK_HENRY | ECHELON_BANK_FIS_1 | Contains FIS products (FIS Monthly Bundle, HORIZON 360) |
| `echelon_bank_CSI_extraction_ai.json` | CSI | ECHELON_BANK_FIS_2 | Contains FIS products (HORIZON, D1 Flex, SecurLOCK) |
| `echelon_bank_fis_extraction_ai.json` | FIS | ECHELON_BANK_FIS_3 | Contains FIS products (HORIZON) |

**Root Cause:** The extraction pipeline appears to have processed all files using the FIS vendor identifier pattern (FIS_1, FIS_2, FIS_3) regardless of which vendor's proposal was being extracted.

**Impact:**
- Product matching fails for JH and CSI files (0% match rate)
- Cross-vendor comparison is not possible until corrected

## Corrected Files in This Folder

Files in this folder have been copied from `Extracted JSON/` with the vendor field corrected to match what the filename indicates:

- `echelon_bank_fis_extraction_ai.json` -> vendor: "FIS"
- `echelon_bank_JH_extraction_ai.json` -> vendor: "JACK_HENRY"
- `echelon_bank_CSI_extraction_ai.json` -> vendor: "CSI"

**WARNING:** These corrections fix the vendor FIELD but do NOT fix the underlying content issue.

**TEST RESULTS CONFIRMED:** All three files contain FIS product names (HORIZON, D1 Flex, etc.). Even with corrected vendor labels:
- FIS: 100% match rate (22/22 items)
- JH: 0% match rate (contains FIS products, not JH products)
- CSI: 0% match rate (contains FIS products, not CSI products)

**ROOT CAUSE CONFIRMED:** The original source PDFs were all FIS proposals. The actual Jack Henry and CSI proposals for Echelon Bank need to be located and extracted.

## Recommended Actions

1. **Verify source documents:** Confirm that `echelon_bank_JH_extraction_ai.json` was actually extracted from a Jack Henry proposal
2. **Re-extract if needed:** If source documents are correct, re-run extraction pipeline
3. **Fix extraction pipeline:** See GitHub Issue #[TBD] for root cause investigation

## Using These Files

Use files from this folder instead of `Extracted JSON/` for comparison workflows:

```bash
# Generate comparison with corrected data
python generate_comparison.py --input "Processed Extractions" --output "TCO Output"
```

---
*Created: 2026-01-15 during Phase 4 implementation*
