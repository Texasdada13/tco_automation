# Extraction Rules & Standards

## HARDCODED RULES

### Rule 1: JSON File Storage
**ALL extraction JSON files MUST be saved to the `Extracted JSON/` folder.**

### Rule 2: Excel Output Storage
**ALL TCO Excel output files MUST be saved to the `TCO Output/` folder.**

These are mandatory rules for the entire project going forward.

---

## File Naming Conventions

### JSON Extraction Files

| File Type | Naming Pattern | Example |
|-----------|----------------|---------|
| Raw Extraction | `{vendor}_raw_extraction.json` | `csi_raw_extraction.json` |
| AI-Enhanced | `{vendor}_extraction_ai.json` | `csi_extraction_ai.json` |
| Custom | `{vendor}_extraction_{type}.json` | `liberty_extraction_custom.json` |

**Vendor names**: Use lowercase, replace spaces with underscores
- `fis` - FIS
- `csi` - Computer Services, Inc.
- `jh` or `jack_henry` - Jack Henry
- `liberty` - Liberty Capital Bank proposals

### Excel TCO Output Files

| File Type | Naming Pattern | Example |
|-----------|----------------|---------|
| Standard Output | `{Vendor}_TCO_Output_{version}.xlsx` | `CSI_TCO_Output_v1.xlsx` |
| Final Version | `{Vendor}_TCO_Output_final.xlsx` | `Liberty_TCO_Output_final.xlsx` |
| With Timestamp | `{Vendor}_TCO_Output_{version}_{timestamp}.xlsx` | `FIS_TCO_Output_v2_20241207_1430.xlsx` |

**Vendor names for Excel**: Title case, replace spaces with underscores
- `FIS` - FIS
- `CSI` - Computer Services, Inc.
- `JH` or `Jack_Henry` - Jack Henry
- `Liberty` - Liberty Capital Bank proposals

---

## Standard Extraction Process

### Step 1: Raw Extraction
Extract tables/data from source document (PDF, DOCX, etc.)

```python
from extraction_config import get_extraction_output_path

output_path = get_extraction_output_path('csi', 'raw')
# Returns: Extracted JSON/csi_raw_extraction.json

with open(output_path, 'w') as f:
    json.dump(raw_data, f, indent=2)
```

### Step 2: AI Enhancement
Process raw data with Claude AI for intelligent extraction

```python
output_path = get_extraction_output_path('csi', 'ai')
# Returns: Extracted JSON/csi_extraction_ai.json

with open(output_path, 'w') as f:
    json.dump(ai_enhanced_data, f, indent=2)
```

---

## Using the Unified Extraction Script

For all new proposals, use the unified extraction script:

```bash
python extract_proposal.py <pdf_file> <vendor_name>
```

**Example:**
```bash
python extract_proposal.py "CSI Proposal.pdf" "csi"
```

This automatically:
1. Extracts raw data → saves to `Extracted JSON/csi_raw_extraction.json`
2. Enhances with AI → saves to `Extracted JSON/csi_extraction_ai.json`
3. Follows all naming conventions
4. Uses centralized config

---

## Populating TCO Workbooks

For generating Excel TCO outputs, use the unified population script:

```bash
python populate_tco_workbook.py <json_file> [version]
```

**Example:**
```bash
python populate_tco_workbook.py "Extracted JSON/csi_extraction_ai.json"
python populate_tco_workbook.py "Extracted JSON/csi_extraction_ai.json" v2
```

This automatically:
1. Loads data from JSON file
2. Populates WORKBOOK2.xlsx template
3. Auto-saves to `TCO Output/{Vendor}_TCO_Output_{version}.xlsx`
4. Follows all naming conventions
5. Uses centralized config

---

## Configuration Module

The `extraction_config.py` module provides:

```python
from extraction_config import (
    # Directories
    EXTRACTED_JSON_DIR,           # Path to "Extracted JSON" folder
    TCO_OUTPUT_DIR,               # Path to "TCO Output" folder

    # JSON extraction functions
    get_extraction_output_path,   # Get standardized JSON file path
    get_all_extracted_files,      # List all extraction JSON files
    list_extractions,             # Print extraction file listing

    # Excel output functions
    get_tco_output_path,          # Get standardized Excel file path
    get_all_tco_outputs,          # List all TCO output Excel files
    list_tco_outputs              # Print TCO output file listing
)
```

### Example Usage:

```python
# Get JSON extraction path
json_path = get_extraction_output_path('csi', 'raw')

# Get Excel output path
excel_path = get_tco_output_path('csi', 'v1')

# List all extractions
list_extractions()

# List all TCO outputs
list_tco_outputs()

# Get all files
json_files = get_all_extracted_files()
excel_files = get_all_tco_outputs()
```

---

## WHY These Rules Exist

### Benefits for JSON Extraction Files
1. **Organization** - Keep all extraction outputs in one place
2. **Version Control** - Easier to .gitignore the entire folder
3. **Cleanup** - Simple to delete all extractions at once
4. **Discovery** - Know exactly where to find extraction files
5. **Consistency** - All team members/scripts use same location

### Benefits for Excel TCO Outputs
1. **Organization** - Separate outputs from templates and source files
2. **Versioning** - Clear version tracking (v1, v2, final)
3. **Comparison** - Easy to compare different vendor proposals
4. **Cleanup** - Simple to archive or delete old outputs
5. **Sharing** - One folder to zip and share with stakeholders

---

## DO NOT:

### For JSON Files:
❌ Save extraction JSONs to project root
❌ Use custom folder names
❌ Mix extraction files with other JSON files
❌ Save to subdirectories within "Extracted JSON"

### For Excel Files:
❌ Save TCO Excel files to project root
❌ Save Excel files outside "TCO Output" folder
❌ Use inconsistent naming patterns
❌ Manually edit output filenames after generation

## DO:

### For JSON Files:
✅ Always use `extraction_config.py` functions
✅ Use `extract_proposal.py` for new extractions
✅ Follow naming conventions
✅ Save all extraction JSONs to `Extracted JSON/` folder

### For Excel Files:
✅ Always use `populate_tco_workbook.py` for population
✅ Let the script auto-generate filenames
✅ Use version identifiers (v1, v2, final)
✅ Save all TCO outputs to `TCO Output/` folder

---

## For Developers

### When creating new extraction scripts:

```python
# WRONG - Don't do this
with open('my_extraction.json', 'w') as f:  # Saves to root ❌
    json.dump(data, f)

# CORRECT - Do this
from extraction_config import get_extraction_output_path

output_path = get_extraction_output_path('vendor_name', 'extraction_type')
with open(output_path, 'w') as f:  # Saves to Extracted JSON/ ✅
    json.dump(data, f)
```

### When creating new Excel population scripts:

```python
# WRONG - Don't do this
wb.save('my_tco_output.xlsx')  # Saves to root ❌

# CORRECT - Do this
from extraction_config import get_tco_output_path

output_path = get_tco_output_path('vendor_name', 'v1')
wb.save(output_path)  # Saves to TCO Output/ ✅
```

### Using populate_workbook function:

```python
from populate_tco_workbook import populate_workbook

# Auto-generates filename and saves to TCO Output/
output_path, report = populate_workbook(
    json_file='Extracted JSON/csi_extraction_ai.json',
    version='v1'
)

# Output: TCO Output/CSI_TCO_Output_v1.xlsx
```

---

## Quick Reference

| What | Where | Function |
|------|-------|----------|
| JSON extractions | `Extracted JSON/` | `get_extraction_output_path()` |
| Excel TCO outputs | `TCO Output/` | `get_tco_output_path()` |

---

*Last Updated: December 2024*
*These are HARDCODED RULES - do not deviate without explicit approval*
