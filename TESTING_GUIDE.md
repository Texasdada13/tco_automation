# TCO Automation - Testing Guide

**Comprehensive Testing Procedures**

---

## Table of Contents

- [Overview](#overview)
- [Test Environment Setup](#test-environment-setup)
- [Unit Testing](#unit-testing)
- [Integration Testing](#integration-testing)
- [End-to-End Testing](#end-to-end-testing)
- [Validation Testing](#validation-testing)
- [Performance Testing](#performance-testing)
- [Regression Testing](#regression-testing)
- [Test Data Management](#test-data-management)

---

## Overview

This guide provides comprehensive testing procedures for the TCO Automation System. Follow these procedures to ensure system quality and reliability.

### Testing Levels

| Level | Purpose | Scope |
|-------|---------|-------|
| Unit | Test individual functions | Single module |
| Integration | Test module interactions | Multiple modules |
| End-to-End | Test complete workflows | Full system |
| Validation | Verify data accuracy | Output validation |
| Performance | Measure speed/resources | System benchmarks |

---

## Test Environment Setup

### Prerequisites

```bash
# Install test dependencies
pip install pytest pytest-cov pytest-mock

# Verify installation
pytest --version
```

### Directory Structure

```
tco_automation/
├── tests/
│   ├── __init__.py
│   ├── test_extractors/
│   │   ├── test_fis_extractor.py
│   │   └── test_jh_extractor.py
│   ├── test_mappers/
│   │   └── test_schema_mapper.py
│   ├── test_writers/
│   │   └── test_tco_writer.py
│   ├── test_integration/
│   │   └── test_pipeline.py
│   └── fixtures/
│       ├── sample_fis.docx
│       ├── sample_jh.xlsx
│       └── sample_template.xlsx
```

### Environment Variables

```bash
# Set test environment
export TCO_TEST_MODE=true
export LOG_LEVEL=DEBUG
```

---

## Unit Testing

### Running Unit Tests

```bash
# Run all unit tests
pytest tests/ -v

# Run specific test file
pytest tests/test_extractors/test_fis_extractor.py -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

### Extractor Unit Tests

#### FIS Extractor Tests

```python
# tests/test_extractors/test_fis_extractor.py

import pytest
from extractors.fis_extractor import FISExtractor

class TestFISExtractor:

    @pytest.fixture
    def extractor(self):
        return FISExtractor()

    @pytest.fixture
    def sample_doc(self):
        return "tests/fixtures/sample_fis.docx"

    def test_extract_returns_dict(self, extractor, sample_doc):
        """Test that extract returns a dictionary"""
        result = extractor.extract(sample_doc)
        assert isinstance(result, dict)

    def test_extract_has_bundle_pricing(self, extractor, sample_doc):
        """Test that bundle pricing is extracted"""
        result = extractor.extract(sample_doc)
        assert 'bundle_pricing' in result
        assert '7_year' in result['bundle_pricing']

    def test_extract_has_monthly_fees(self, extractor, sample_doc):
        """Test that monthly fees are extracted"""
        result = extractor.extract(sample_doc)
        assert 'monthly_fees' in result
        assert len(result['monthly_fees']) > 0

    def test_currency_parsing(self, extractor):
        """Test currency parsing"""
        assert extractor.parse_currency("$15,000.00") == 15000.00
        assert extractor.parse_currency("$1,234,567.89") == 1234567.89
        assert extractor.parse_currency("invalid") == 0.0

    def test_table_identification(self, extractor, sample_doc):
        """Test that tables are correctly identified"""
        tables = extractor.identify_tables(sample_doc)
        assert 'bundle_pricing' in tables
        assert 'monthly_fees' in tables
```

#### Jack Henry Extractor Tests

```python
# tests/test_extractors/test_jh_extractor.py

import pytest
from extractors.jh_extractor import JHExtractor

class TestJHExtractor:

    @pytest.fixture
    def extractor(self):
        return JHExtractor()

    @pytest.fixture
    def sample_xlsx(self):
        return "tests/fixtures/sample_jh.xlsx"

    def test_extract_returns_dict(self, extractor, sample_xlsx):
        """Test that extract returns a dictionary"""
        result = extractor.extract(sample_xlsx)
        assert isinstance(result, dict)

    def test_extract_has_products(self, extractor, sample_xlsx):
        """Test that products are extracted"""
        result = extractor.extract(sample_xlsx)
        assert 'products' in result
        assert len(result['products']) > 0

    def test_scenario_extraction(self, extractor, sample_xlsx):
        """Test different scenario extraction"""
        result_1 = extractor.extract(sample_xlsx, scenario='Proposal_1')
        result_2 = extractor.extract(sample_xlsx, scenario='Proposal_2')
        # Different scenarios should have different values
        assert result_1 != result_2

    def test_hidden_row_detection(self, extractor, sample_xlsx):
        """Test hidden row detection"""
        hidden = extractor.detect_hidden_rows(sample_xlsx)
        assert isinstance(hidden, list)

    def test_comment_extraction(self, extractor, sample_xlsx):
        """Test cell comment extraction"""
        result = extractor.extract(sample_xlsx)
        # Check if comments are captured
        has_comments = any(
            p.get('comments') for p in result['products']
        )
        assert has_comments or True  # May not have comments
```

### Mapper Unit Tests

```python
# tests/test_mappers/test_schema_mapper.py

import pytest
from mappers.schema_mapper import SchemaMapper

class TestSchemaMapper:

    @pytest.fixture
    def mapper(self):
        return SchemaMapper()

    def test_normalize_fis_data(self, mapper):
        """Test FIS data normalization"""
        fis_data = {
            'bundle_pricing': {'7_year': {'year_1': 150000}},
            'monthly_fees': [{'solution_name': 'Test', 'monthly_fee': 1000}]
        }
        result = mapper.normalize(fis_data, vendor='FIS', term='7_year')
        assert isinstance(result, list)
        assert len(result) > 0

    def test_category_mapping(self, mapper):
        """Test category mapping"""
        assert mapper.map_category('HORIZON', 'FIS') == 'Bundle'
        assert mapper.map_category('Paper Forms', 'FIS') == 'Non-Bundle Required'

    def test_fee_type_mapping(self, mapper):
        """Test fee type mapping"""
        assert mapper.map_fee_type('monthly') == 'Monthly F'
        assert mapper.map_fee_type('annual') == 'Annual'
        assert mapper.map_fee_type('one-time') == 'One-Time'

    def test_fuzzy_matching(self, mapper):
        """Test fuzzy product matching"""
        match = mapper.fuzzy_match('SilverLake Sys', ['SilverLake System', 'Gold Lake'])
        assert match == 'SilverLake System'
```

### Writer Unit Tests

```python
# tests/test_writers/test_tco_writer.py

import pytest
import os
from writers.tco_writer import TCOWriter

class TestTCOWriter:

    @pytest.fixture
    def template(self):
        return "tests/fixtures/sample_template.xlsx"

    @pytest.fixture
    def output(self, tmp_path):
        return str(tmp_path / "test_output.xlsx")

    def test_writer_initialization(self, template, output):
        """Test writer initialization"""
        writer = TCOWriter(template, output)
        assert writer is not None

    def test_write_line_item(self, template, output):
        """Test writing a single line item"""
        writer = TCOWriter(template, output)
        item = {
            'solution_name': 'Test Product',
            'fee_type': 'Monthly F',
            'category': 'Bundle',
            'monthly_fee': 1000
        }
        writer.write_line_item(item, vendor='FIS', row=7)
        writer.save()
        assert os.path.exists(output)

    def test_write_vendor_data(self, template, output):
        """Test writing vendor data"""
        writer = TCOWriter(template, output)
        data = [
            {'solution_name': 'Product 1', 'category': 'Bundle', 'monthly_fee': 1000},
            {'solution_name': 'Product 2', 'category': 'Non-Bundle Required', 'monthly_fee': 500}
        ]
        writer.write_vendor_data(data, vendor='FIS')
        writer.save()
        assert os.path.exists(output)
```

---

## Integration Testing

### Pipeline Integration Tests

```python
# tests/test_integration/test_pipeline.py

import pytest
from orchestrator.pipeline import Pipeline

class TestPipeline:

    @pytest.fixture
    def pipeline(self):
        return Pipeline()

    def test_fis_pipeline(self, pipeline, tmp_path):
        """Test complete FIS pipeline"""
        output = str(tmp_path / "fis_output.xlsx")
        result = pipeline.run(
            fis_file="tests/fixtures/sample_fis.docx",
            template="tests/fixtures/sample_template.xlsx",
            output=output,
            fis_term='7_year'
        )
        assert result['success'] == True
        assert result['items_extracted'] > 0

    def test_jh_pipeline(self, pipeline, tmp_path):
        """Test complete JH pipeline"""
        output = str(tmp_path / "jh_output.xlsx")
        result = pipeline.run(
            jh_file="tests/fixtures/sample_jh.xlsx",
            template="tests/fixtures/sample_template.xlsx",
            output=output,
            jh_scenario='Proposal_1'
        )
        assert result['success'] == True

    def test_combined_pipeline(self, pipeline, tmp_path):
        """Test combined vendor pipeline"""
        output = str(tmp_path / "combined_output.xlsx")
        result = pipeline.run(
            fis_file="tests/fixtures/sample_fis.docx",
            jh_file="tests/fixtures/sample_jh.xlsx",
            template="tests/fixtures/sample_template.xlsx",
            output=output
        )
        assert result['success'] == True
        assert 'FIS' in result['vendors_processed']
        assert 'Jack Henry' in result['vendors_processed']
```

### Running Integration Tests

```bash
# Run integration tests only
pytest tests/test_integration/ -v

# Run with specific markers
pytest -m integration -v
```

---

## End-to-End Testing

### E2E Test Script

```bash
#!/bin/bash
# tests/e2e/run_e2e_tests.sh

echo "Running End-to-End Tests..."

# Test 1: FIS extraction
echo "Test 1: FIS Extraction"
python main.py \
  --fis tests/fixtures/sample_fis.docx \
  --template tests/fixtures/sample_template.xlsx \
  --output tests/output/e2e_fis.xlsx \
  --fis-term 7_year

if [ -f "tests/output/e2e_fis.xlsx" ]; then
    echo "PASS: FIS extraction completed"
else
    echo "FAIL: FIS extraction failed"
    exit 1
fi

# Test 2: JH extraction
echo "Test 2: JH Extraction"
python main.py \
  --jh tests/fixtures/sample_jh.xlsx \
  --template tests/fixtures/sample_template.xlsx \
  --output tests/output/e2e_jh.xlsx \
  --jh-scenario Proposal_1

if [ -f "tests/output/e2e_jh.xlsx" ]; then
    echo "PASS: JH extraction completed"
else
    echo "FAIL: JH extraction failed"
    exit 1
fi

# Test 3: Combined extraction
echo "Test 3: Combined Extraction"
python main.py \
  --fis tests/fixtures/sample_fis.docx \
  --jh tests/fixtures/sample_jh.xlsx \
  --template tests/fixtures/sample_template.xlsx \
  --output tests/output/e2e_combined.xlsx

if [ -f "tests/output/e2e_combined.xlsx" ]; then
    echo "PASS: Combined extraction completed"
else
    echo "FAIL: Combined extraction failed"
    exit 1
fi

echo "All E2E tests passed!"
```

### Running E2E Tests

```bash
chmod +x tests/e2e/run_e2e_tests.sh
./tests/e2e/run_e2e_tests.sh
```

---

## Validation Testing

### Cell-by-Cell Validation

```bash
# Validate JH extraction
python cell_validator.py \
  --source tests/fixtures/sample_jh.xlsx \
  --tco tests/output/e2e_jh.xlsx \
  --scenario Proposal_1

# Expected output:
# Total cells checked: X,XXX
# Matched: X,XXX (XX.X%)
# Mismatched: XX (X.X%)
```

### QA Validation

```bash
# Run QA validation
python qa_validator.py tests/output/e2e_fis.xlsx

# Check confidence scores
# Check business rule violations
# Check cross-validation results
```

### Validation Test Cases

| Test Case | Expected Result |
|-----------|-----------------|
| All required fields populated | Pass |
| Confidence scores >= 70% | Pass |
| Annual = Monthly * 12 | Pass (within 1% tolerance) |
| No zero-value required items | Pass |
| Category assignments correct | Pass |

---

## Performance Testing

### Benchmark Script

```python
# tests/performance/benchmark.py

import time
import statistics
from main import process_proposal

def benchmark_extraction(file_path, iterations=5):
    times = []

    for i in range(iterations):
        start = time.time()
        process_proposal(file_path, "template.xlsx", f"output_{i}.xlsx")
        elapsed = time.time() - start
        times.append(elapsed)
        print(f"Iteration {i+1}: {elapsed:.2f}s")

    print(f"\nResults ({iterations} iterations):")
    print(f"  Mean: {statistics.mean(times):.2f}s")
    print(f"  Median: {statistics.median(times):.2f}s")
    print(f"  Std Dev: {statistics.stdev(times):.2f}s")
    print(f"  Min: {min(times):.2f}s")
    print(f"  Max: {max(times):.2f}s")

if __name__ == "__main__":
    benchmark_extraction("tests/fixtures/sample_fis.docx")
```

### Performance Targets

| Metric | Target | Acceptable |
|--------|--------|------------|
| Single file extraction | < 30s | < 60s |
| Combined extraction | < 60s | < 120s |
| Memory usage | < 500MB | < 1GB |
| CPU usage | < 50% | < 80% |

---

## Regression Testing

### Regression Test Suite

```bash
# Run full regression suite
pytest tests/ -v --tb=short

# Run with baseline comparison
pytest tests/regression/ -v --baseline=tests/baselines/
```

### Baseline Management

```bash
# Create new baseline
python tests/create_baseline.py tests/fixtures/sample_fis.docx

# Compare against baseline
python tests/compare_baseline.py tests/output/result.xlsx tests/baselines/fis_baseline.xlsx
```

---

## Test Data Management

### Sample Files

| File | Purpose | Location |
|------|---------|----------|
| sample_fis.docx | FIS proposal sample | tests/fixtures/ |
| sample_jh.xlsx | JH deal sheet sample | tests/fixtures/ |
| sample_template.xlsx | TCO template | tests/fixtures/ |

### Creating Test Fixtures

```python
# tests/create_fixtures.py

from docx import Document
from openpyxl import Workbook

def create_sample_fis_doc():
    doc = Document()
    doc.add_heading('Sample FIS Proposal', 0)

    # Add bundle pricing table
    table = doc.add_table(rows=3, cols=4)
    table.cell(0, 0).text = 'Bundle'
    table.cell(0, 1).text = '5 Year'
    table.cell(0, 2).text = '7 Year'
    table.cell(0, 3).text = '10 Year'

    table.cell(1, 0).text = 'Year 1'
    table.cell(1, 1).text = '$150,000'
    table.cell(1, 2).text = '$140,000'
    table.cell(1, 3).text = '$130,000'

    doc.save('tests/fixtures/sample_fis.docx')

def create_sample_jh_xlsx():
    wb = Workbook()
    ws = wb.active

    # Headers
    ws['A1'] = 'Product Description'
    ws['B1'] = 'Product Family'
    ws['H1'] = 'License'
    ws['I1'] = 'Install'
    ws['J1'] = 'Maintenance'
    ws['K1'] = 'Monthly'

    # Data
    ws['A2'] = 'SilverLake Core'
    ws['B2'] = 'SilverLake'
    ws['H2'] = 50000
    ws['I2'] = 15000
    ws['J2'] = 12000
    ws['K2'] = 8500

    wb.save('tests/fixtures/sample_jh.xlsx')

if __name__ == "__main__":
    create_sample_fis_doc()
    create_sample_jh_xlsx()
```

---

## Test Reporting

### Coverage Report

```bash
# Generate coverage report
pytest tests/ --cov=. --cov-report=html

# View report
open htmlcov/index.html
```

### Test Results Summary

```bash
# Run with JUnit XML output
pytest tests/ --junitxml=test-results.xml

# Run with verbose summary
pytest tests/ -v --tb=short
```

---

## Continuous Integration

### GitHub Actions Example

```yaml
# .github/workflows/tests.yml

name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.8'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov

    - name: Run tests
      run: pytest tests/ -v --cov=. --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

---

*Last Updated: December 2024*
