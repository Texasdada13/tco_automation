# TCO Automation - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### 1. Install Dependencies

```bash
cd tco_automation
pip install python-docx openpyxl pandas --break-system-packages
```

### 2. Prepare Your Files

Place these files in the `data/` directory:
- **FIS Proposal**: Word document (.docx)
- **Jack Henry Proposal**: Excel file (.xlsx)  
- **TCO Template**: Your Excel TCO template

### 3. Run the Automation

#### Option A: Process Both Vendors (Recommended)

```bash
python main.py \
  --fis data/your_fis_proposal.docx \
  --jh data/your_jh_proposal.xlsx \
  --template data/your_tco_template.xlsx \
  --output output/tco_comparison.xlsx
```

#### Option B: Process FIS Only

```bash
python main.py \
  --fis data/your_fis_proposal.docx \
  --template data/your_tco_template.xlsx \
  --output output/fis_tco.xlsx \
  --fis-term 7_year
```

#### Option C: Process Jack Henry Only

```bash
python main.py \
  --jh data/your_jh_proposal.xlsx \
  --template data/your_tco_template.xlsx \
  --output output/jh_tco.xlsx \
  --jh-scenario Proposal_1
```

### 4. Review the Output

Open the generated Excel file to review:
- ✅ Extracted pricing data
- ✅ Categorized line items  
- ✅ Multi-year cost projections
- ✅ Side-by-side vendor comparison (if both vendors processed)

## 📊 What Gets Automated?

### From FIS Proposals:
- Bundle pricing by year and contract term
- Monthly fees for non-bundle solutions
- One-time implementation fees and credits
- Third-party solution pricing

### From Jack Henry Proposals:
- Product-level pricing (License, Install, Maintenance, Monthly)
- Product family categorization (SilverLake, OnBoard, Teller, etc.)
- Included vs. Optional solutions
- Multiple proposal scenarios

### Into TCO Template:
- Line Items sheet populated with all solutions
- Quantities by year (with growth projections)
- Cost calculations for Years 1-7
- Proper categorization (Bundle, Non-Bundle, Optional, Third-Party)

## 🎯 Example Workflow

Using the included sample files:

```bash
# Full comparison with FIS 7-year term and Jack Henry Proposal_1
python main.py \
  --fis data/Echelon_FIS_Proposal_10_29_25.docx \
  --jh data/Updated_With_all_products__Deal_Sheet_Clearwater__FL_-_Echelon_Bank__InOrg__-_New_Core_SilverLake_OL_PAP_08_27_25.xlsx \
  --template data/Echelon_Primary_TCO_v5_11_13_25.xlsx \
  --output output/echelon_tco_comparison.xlsx
```

**Result**: TCO template with 42 FIS line items and 134 Jack Henry line items populated!

## 🔧 Customization

### Change FIS Contract Term

```bash
--fis-term 10_year  # Options: 5_year, 7_year, 10_year
```

### Change Jack Henry Scenario

```bash
--jh-scenario Proposal_2  # Options: Proposal_1, Proposal_2, Proposal_3
```

### Customize Categories and Mappings

Edit `config.py` to adjust:
- Product category mappings
- Fee type classifications
- Growth rates
- Starting row numbers in TCO template

## ⚡ Pro Tips

1. **Verify Extraction First**: Run individual extractors to check data quality:
   ```bash
   python -m extractors.fis_extractor data/your_proposal.docx
   ```

2. **Review Logs**: Check console output for extraction summaries and warnings

3. **Backup Templates**: Always keep a copy of your original TCO template

4. **Test with Samples**: Run on the included sample files first to understand the output

5. **Incremental Processing**: Process one vendor at a time if troubleshooting issues

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Import errors | Run `pip install` command again |
| File not found | Check file paths are relative to project root |
| Missing data | Verify proposal format matches FIS/JH structure |
| Wrong categories | Update product keywords in `config.py` |

## 📚 Next Steps

1. ✅ Run the example workflow above
2. ✅ Review the generated TCO comparison file
3. ✅ Try with your own vendor proposals
4. ✅ Customize mappings in `config.py` for your needs
5. ✅ Check the full README.md for advanced features

## 💡 Need Help?

- Read the full README.md for detailed documentation
- Check the troubleshooting section
- Review extraction logs for warnings
- Verify your proposals match expected formats

---

**Time Saved**: What used to take hours of manual copy/paste now takes seconds! 🎉
