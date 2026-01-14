# TCO Automation - Demo Cheat Sheet

**Quick Reference for Live Demonstrations**

---

## Pre-Demo Checklist

```
[ ] Environment activated
[ ] Files in data/ directory
[ ] output/ directory exists
[ ] API key set (for AI features)
[ ] Backup output files ready
```

---

## Quick Commands

### Single Vendor (FIS)

```bash
python main.py \
  --fis data/Echelon_FIS_Proposal_10_29_25.docx \
  --template data/Echelon_Primary_TCO_v5.xlsx \
  --output output/demo_fis.xlsx \
  --fis-term 7_year
```

### Single Vendor (Jack Henry)

```bash
python main.py \
  --jh data/JH_Deal_Sheet.xlsx \
  --template data/Echelon_Primary_TCO_v5.xlsx \
  --output output/demo_jh.xlsx \
  --jh-scenario Proposal_1
```

### Both Vendors (Comparison)

```bash
python main.py \
  --fis data/Echelon_FIS_Proposal_10_29_25.docx \
  --jh data/JH_Deal_Sheet.xlsx \
  --template data/Echelon_Primary_TCO_v5.xlsx \
  --output output/demo_comparison.xlsx \
  --fis-term 7_year \
  --jh-scenario Proposal_1
```

### AI Pipeline

```bash
python run_pipeline.py data/Echelon_FIS_Proposal_10_29_25.docx \
  --vendor FIS \
  --term 7_year \
  -o output \
  --json
```

### Validation

```bash
python cell_validator.py \
  --source data/JH_Deal_Sheet.xlsx \
  --tco output/demo_comparison.xlsx \
  --scenario Proposal_1
```

---

## Key Numbers to Remember

| Metric | Value |
|--------|-------|
| Time saved | 4-10 hours |
| Processing time | < 60 seconds |
| Accuracy | 95-99% |
| Auto-accept threshold | >= 90% |
| Review threshold | 70-89% |

---

## Excel Output Locations

| Vendor | Columns | Start Row |
|--------|---------|-----------|
| FIS | B-Y | 7 (bundle) |
| Jack Henry | AO-BL | 7 (bundle) |

---

## Common Questions - Quick Answers

**"What vendors?"**
> FIS and Jack Henry (configurable for others)

**"How accurate?"**
> 95-99% with AI validation

**"Security?"**
> Local processing, no data stored externally

**"ROI?"**
> 80-500 hours saved annually

**"Implementation time?"**
> 1-2 days for full deployment

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Module not found | `pip install -r requirements.txt` |
| File not found | Check path with `ls data/` |
| Empty output | Use backup files |
| API error | Disable with `--no-llm` |

---

## Key Talking Points

1. **Before**: 4-10 hours manual work
2. **After**: 60 seconds automated
3. **Accuracy**: 95-99% with AI validation
4. **Output**: Side-by-side vendor comparison
5. **Audit**: Complete source traceability

---

## Demo Flow (15 min)

1. **2 min** - Problem statement
2. **3 min** - Single vendor demo
3. **3 min** - Comparison demo
4. **2 min** - AI features
5. **2 min** - Validation
6. **3 min** - Q&A

---

*Keep this sheet visible during demos*
