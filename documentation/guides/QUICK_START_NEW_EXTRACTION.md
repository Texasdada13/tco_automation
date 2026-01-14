# Quick Start: Fix FSB FIS Horizon 2024 Extraction

## Problem Summary
Current extraction: **8 generic items** with poor quality
Expected: **100-200+ specific items** with full details

## ✅ Solution: Direct PDF to Claude API

### Step 1: Run Direct Extraction (Recommended)

```bash
python extract_proposal_direct.py "Proposal/FSB Proposal FIS Horizon 2024.pdf" "fsb"
```

**What happens:**
- Sends PDF directly to Claude API
- Claude reads it natively (like you would)
- Extracts ALL line items with full details
- Saves to: `Extracted JSON/fsb_extraction_direct.json`

**Expected time:** 30-60 seconds
**Expected cost:** $1-3 (API usage)
**Expected result:** 100-200+ line items

---

### Step 2: Compare Results

```bash
python compare_extractions.py fsb
```

**Output:**
```
Method                     Items    Categories   Monthly $        One-Time $      Details
--------------------------------------------------------------------------------
Direct PDF                 187      12          $72,497.00       $154,600.00     ✅
Current (2-step AI)        8        8           $28,018.41       $35,760.37      ❌
```

---

### Step 3: Review Extracted Data

Open: `Extracted JSON/fsb_extraction_direct.json`

**Check for:**
- ✅ Exact service names (e.g., "FIS EFT Processing - PaymentsOne")
- ✅ Current AND Proposed fees
- ✅ Graduated pricing tiers
- ✅ Per-unit rates with volumes
- ✅ Implementation fees
- ✅ Credits and discounts

---

### Alternative: Hybrid Extraction (Maximum Accuracy)

If Direct PDF needs improvement:

```bash
python extract_proposal_hybrid.py "Proposal/FSB Proposal FIS Horizon 2024.pdf" "fsb"
```

**When to use:**
- Direct PDF missed some details
- Need maximum confidence
- Critical proposal requiring verification

---

## Why This Works

**Current method fails:**
- pdfplumber can't parse complex table layouts
- Side-by-side "Current vs Proposed" tables break it
- Merged cells and nested categories get mangled
- Result: garbage data → AI can't fix it

**Direct PDF succeeds:**
- Claude sees the PDF visually (like you do)
- Understands complex layouts natively
- No intermediate parsing to break
- Designed for structured extraction from documents

---

## Files Created

New extraction scripts:
- ✅ `extract_proposal_direct.py` - Direct PDF to Claude API
- ✅ `extract_proposal_hybrid.py` - PDF + Vision for max accuracy
- ✅ `compare_extractions.py` - Compare different extraction methods
- ✅ `EXTRACTION_METHODS_GUIDE.md` - Complete documentation

Kept for simple proposals:
- 📝 `extract_proposal.py` - Original 2-step method (still useful for simple formats)

---

## Next Steps

1. **Test on FSB FIS Horizon:**
   ```bash
   python extract_proposal_direct.py "Proposal/FSB Proposal FIS Horizon 2024.pdf" "fsb"
   ```

2. **Compare with current extraction:**
   ```bash
   python compare_extractions.py fsb
   ```

3. **If satisfied, use for TCO mapping:**
   ```bash
   python scripts/json_to_excel_mapper.py "Extracted JSON/fsb_extraction_direct.json"
   ```

4. **Use for future proposals:**
   - Try current 2-step method first (cheapest)
   - If < 50 items extracted → use Direct PDF
   - For critical proposals → use Hybrid verification

---

## Cost Optimization Tips

### 1. Page Targeting (modify script)
Only send pricing pages (2-10) instead of full PDF:
```python
# In extract_proposal_direct.py
# Extract only pages 2-10 from PDF before encoding
```

### 2. Use Prompt Caching
Cache the extraction prompt for 90% savings on repeat extractions:
```python
system=[{
    "type": "text",
    "text": EXTRACTION_PROMPT,
    "cache_control": {"type": "ephemeral"}
}]
```

### 3. Batch Processing
Process multiple proposals in one session to reuse cached prompt.

### 4. Use Haiku for Simple Proposals
Switch to `claude-haiku-4-20250514` for 20x cost savings on simple formats.

---

## Troubleshooting

**Issue:** `ImportError: No module named 'anthropic'`
**Fix:** `pip install anthropic`

**Issue:** API key error
**Fix:** Check ANTHROPIC_API_KEY in extract_proposal_direct.py line 28

**Issue:** JSON parsing error
**Fix:** Check `Extracted JSON/fsb_extraction_direct_error.txt` for raw response

**Issue:** Low item count
**Fix:** Try hybrid extraction: `python extract_proposal_hybrid.py ...`

---

## Success Criteria

✅ Line items: 100-200+ (vs current 8)
✅ Service names: Exact from proposal (not generic)
✅ Pricing: Current AND Proposed fees
✅ Details: Volumes, rates, tiers, minimums
✅ Metadata: Client, date, contract term
✅ Confidence: 90%+ accuracy

---

## Questions?

Read full guide: `EXTRACTION_METHODS_GUIDE.md`
