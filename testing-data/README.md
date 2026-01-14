# Testing Data Directory

This directory contains all testing materials for validating the TCO automation platform's extraction capabilities.

## Directory Structure

```
testing-data/
├── dummy-proposals/           # Sample vendor proposals for testing
│   ├── fis-like/             # FIS-style banking proposals
│   ├── jack-henry-like/      # Jack Henry-style proposals
│   ├── csi-like/             # CSI-style proposals
│   └── other-vendors/        # Other banking vendor proposals
├── extraction-results/        # Pipeline extraction outputs (auto-populated)
└── validation-reports/        # Accuracy reports and logs
```

## Document Requirements

### Target Characteristics
- **Format**: PDF (primary), DOCX, XLSX
- **Page Count**: Mix of simple (10-20), medium (30-50), complex (60+)
- **Content Types**:
  - Pricing tables and cost breakdowns
  - Service descriptions and deliverables
  - Executive summaries
  - Technical specifications
  - Implementation timelines

### Target Vendors
- **Primary**: FIS, Jack Henry, CSI (core banking system vendors)
- **Secondary**: Fiserv, Finastra, similar enterprise banking software

## Testing Goals

1. Validate extraction accuracy across diverse document formats
2. Stress-test pipeline with various document complexities
3. Identify edge cases and failure modes
4. Document extraction accuracy metrics
5. Verify processing time benchmarks (<2 min/doc)

## Success Criteria

- [ ] Extraction accuracy ≥90% for core fields
- [ ] Processing time <2 minutes per document
- [ ] Zero crashes or unhandled exceptions
- [ ] Graceful handling of malformed documents
- [ ] All edge cases documented
