# TCO Automation System

AI-powered system to automate the ingestion of vendor proposals into 5-year TCO (Total Cost of Ownership) Excel models.

## Overview

This system eliminates the time-consuming manual process of extracting pricing data from vendor proposals and populating TCO templates. It uses document parsing, intelligent schema mapping, and automated Excel population to transform unstructured proposals into standardized TCO comparisons.

### Supported Vendors
- **FIS**: Word document proposals (.docx)
- **Jack Henry**: Excel deal sheets (.xlsx)

## Features

- ✅ **Automated Data Extraction**: Parses vendor proposals in multiple formats
- ✅ **Schema Normalization**: Maps vendor-specific terminology to standardized TCO structure
- ✅ **Multi-Year Projections**: Handles 5, 7, and 10-year terms with growth calculations
- ✅ **Side-by-Side Comparisons**: Populate both vendor columns simultaneously
- ✅ **Categorization**: Automatically categorizes fees (Bundle, Non-Bundle, Required, Optional, Third-Party)
- ✅ **Fee Type Detection**: Distinguishes between monthly, annual, and one-time fees

## Installation

### Prerequisites
- Python 3.8+
- pip

### Install Dependencies

```bash
pip install python-docx openpyxl pandas --break-system-packages
```

## Project Structure

```
tco_automation/
├── config.py              # Configuration and mapping rules
├── main.py                # Main orchestration script
├── extractors/
│   ├── __init__.py
│   ├── fis_extractor.py   # FIS Word document parser
│   └── jh_extractor.py    # Jack Henry Excel parser
├── mappers/
│   ├── __init__.py
│   └── schema_mapper.py   # Data normalization engine
├── writers/
│   ├── __init__.py
│   └── tco_writer.py      # TCO Excel template populator
├── data/                  # Input files (proposals, templates)
└── tests/                 # Unit tests
```

## Usage

### Command Line Interface

#### Process FIS Proposal Only

```bash
python main.py \
  --fis data/Echelon_FIS_Proposal_10_29_25.docx \
  --template data/Echelon_Primary_TCO_v5_11_13_25.xlsx \
  --output output/FIS_TCO.xlsx \
  --fis-term 7_year
```

#### Process Jack Henry Proposal Only

```bash
python main.py \
  --jh data/JH_Deal_Sheet.xlsx \
  --template data/Echelon_Primary_TCO_v5_11_13_25.xlsx \
  --output output/JH_TCO.xlsx \
  --jh-scenario Proposal_1
```

#### Process Both Vendors (Side-by-Side Comparison)

```bash
python main.py \
  --fis data/Echelon_FIS_Proposal_10_29_25.docx \
  --jh data/JH_Deal_Sheet.xlsx \
  --template data/Echelon_Primary_TCO_v5_11_13_25.xlsx \
  --output output/TCO_Comparison.xlsx \
  --fis-term 7_year \
  --jh-scenario Proposal_1
```

### Python API

```python
from extractors import extract_fis_proposal, extract_jack_henry_proposal
from mappers import normalize_vendor_data
from writers import TCOWriter

# Extract FIS data
fis_data = extract_fis_proposal("proposal.docx")
fis_normalized = normalize_vendor_data(fis_data, 'FIS', term='7_year')

# Populate TCO template
writer = TCOWriter("template.xlsx", "output.xlsx")
writer.write_vendor_data(fis_normalized, 'FIS')
writer.save()
```

## How It Works

### 1. Data Extraction Phase

#### FIS Extractor
- Parses Word documents using `python-docx`
- Identifies tables by content (bundle pricing, one-time credits, monthly fees)
- Extracts:
  - Bundle pricing by year and term (5/7/10 year)
  - Monthly fees for additional solutions
  - One-time implementation fees and credits
  - Terms and conditions

#### Jack Henry Extractor
- Parses Excel workbooks using `openpyxl`
- Processes multiple proposal scenarios
- Extracts:
  - Product descriptions and families
  - License, installation, maintenance, and monthly fees
  - Category flags (Included/Optional)
  - Delivery methods

### 2. Schema Mapping Phase

Normalizes vendor-specific data into a standardized structure:

```python
{
    'solution_name': 'Product Name',
    'fee_type': 'Monthly F',  # Monthly F, Monthly V, Annual, One-Time
    'category': 'Bundle',     # Bundle, Non-Bundle Required/Optional, Third-Party
    'vendor': 'FIS',
    'per_unit_rate': 15000.0,
    'monthly_fee': 15000.0,
    'annual_fee': 180000.0,
    'one_time_fee': 0,
    'optional': False,
    'third_party': False,
    'quantities_by_year': {
        'year_1': 12,
        'year_2': 12,
        ...
    }
}
```

**Key Mappings:**
- FIS Bundle → "Bundle" category
- FIS Paper/Envelopes → "Non-Bundle Required" 
- JH SilverLake products → "Bundle" category
- JH Included products → "Non-Bundle Required"
- JH Optional products → "Non-Bundle Optional"

### 3. TCO Population Phase

Writes normalized data to Excel template:
- Populates "Line Items" sheet
- Fills columns B-AN for FIS, AR-CA for Jack Henry
- Writes:
  - Fee types
  - Solution names and categories
  - Quantities by year (with growth)
  - Cost calculations by year
- Handles merged cells and preserves formulas

## Configuration

Edit `config.py` to customize:

### Fee Type Mappings
```python
FEE_TYPES = {
    'monthly_fixed': 'Monthly F',
    'monthly_variable': 'Monthly V',
    'annual': 'Annual',
    'one_time': 'One-Time'
}
```

### Product Categories
```python
PRODUCT_CATEGORIES = {
    'BUNDLE': 'Bundle',
    'NON_BUNDLE_REQUIRED': 'Non-Bundle Required',
    'NON_BUNDLE_OPTIONAL': 'Non-Bundle Optional',
    ...
}
```

### Growth Rates
```python
DEFAULT_GROWTH_RATE = 0.20  # 20% annual growth
DEFAULT_CPI_BUNDLE = 0.06    # 6%
DEFAULT_CPI_NON_BUNDLE = 0.03  # 3%
```

### Starting Rows
```python
LINE_ITEM_START_ROWS = {
    'FIS_BUNDLE': 7,
    'FIS_NON_BUNDLE_REQUIRED': 22,
    'FIS_NON_BUNDLE_OPTIONAL': 100,
    ...
}
```

## Testing

### Test Individual Components

```bash
# Test FIS extractor
python -m extractors.fis_extractor data/FIS_proposal.docx

# Test Jack Henry extractor
python -m extractors.jh_extractor data/JH_proposal.xlsx

# Test schema mapper
python -m mappers.schema_mapper

# Test TCO writer
python -m writers.tco_writer
```

### Run Full Workflow Test

```bash
python main.py \
  --fis data/Echelon_FIS_Proposal_10_29_25.docx \
  --template data/Echelon_Primary_TCO_v5_11_13_25.xlsx \
  --output test_output.xlsx
```

## Known Limitations

1. **Template Dependency**: Assumes specific TCO template structure
2. **Merged Cells**: Some template cells may not be writable if merged
3. **Formula Preservation**: Current version writes calculated values, not formulas
4. **Single Term**: FIS processing uses one term at a time (5/7/10 year)
5. **No AI Mapping**: Uses rule-based mapping (future: add Claude API for ambiguous cases)

## Future Enhancements

### Phase 2 - Intelligent Mapping
- [ ] Integrate Claude API for ambiguous product name mapping
- [ ] Machine learning for category classification
- [ ] Historical mapping database

### Phase 3 - Advanced Features
- [ ] PDF proposal support
- [ ] Automated variance analysis
- [ ] Multi-vendor comparison dashboard
- [ ] Formula preservation in Excel output
- [ ] Batch processing of multiple proposals

### Phase 4 - Web Interface
- [ ] Web-based UI for file uploads
- [ ] Real-time processing status
- [ ] Interactive TCO comparison views
- [ ] Export to multiple formats

## Troubleshooting

### "Package not found" Error
- Ensure all dependencies are installed
- Check file paths are correct

### "MergedCell" Errors
- Update template to avoid merged cells in data regions
- Use latest version of `openpyxl`

### Missing Data in Output
- Verify vendor proposal format matches expected structure
- Check `config.py` starting row numbers
- Review extraction logs for warnings

### Incorrect Categorization
- Update product keywords in `config.py`
- Add custom mapping rules
- Check vendor-specific family mappings

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review extraction logs for warnings
3. Verify input file formats match examples
4. Update configuration mappings as needed

## License

Proprietary - Arriba Advisors LLC

## Version History

- **v1.0** (Nov 2024): Initial release
  - FIS Word document extraction
  - Jack Henry Excel extraction
  - Basic schema mapping
  - TCO template population
  - CLI interface
