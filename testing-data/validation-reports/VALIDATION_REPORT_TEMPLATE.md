# TCO Extraction Validation Report

**Test Run Date:** [YYYY-MM-DD]
**Tester:** [Name]
**Branch:** testing/dummy-proposals-validation
**Pipeline Version:** [commit hash or version]

---

## Executive Summary

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Documents Tested | 5-15 | | |
| Success Rate | >=90% | | |
| Avg Confidence | >=90% | | |
| Avg Processing Time | <120s | | |
| Zero Crashes | Yes | | |

**Overall Result:** [ ] PASSED  [ ] NEEDS REVIEW  [ ] FAILED

---

## Test Environment

- **Python Version:**
- **OS:**
- **API Model:** claude-sonnet-4-20250514
- **Template Used:** WORKBOOK1.xlsx / WORKBOOK2.xlsx

---

## Documents Tested

### Summary by Vendor Type

| Vendor Type | Total | Success | Failed | Avg Confidence | Avg Time |
|-------------|-------|---------|--------|----------------|----------|
| FIS-like | | | | | |
| Jack Henry-like | | | | | |
| CSI-like | | | | | |
| Other Vendors | | | | | |
| **TOTAL** | | | | | |

### Summary by Complexity

| Complexity | Total | Success | Avg Confidence | Avg Time |
|------------|-------|---------|----------------|----------|
| Simple (10-20 pg) | | | | |
| Medium (30-50 pg) | | | | |
| Complex (60+ pg) | | | | |

---

## Individual Document Results

### Document 1: [filename]

| Field | Value |
|-------|-------|
| **File** | |
| **Vendor Type** | |
| **Pages** | |
| **File Size** | |
| **Processing Time** | |
| **Items Extracted** | |
| **Overall Confidence** | |
| **QA Bucket** | |
| **Status** | SUCCESS / FAILED |

**Accuracy Spot Check:**
- [ ] Item 1: [name] - Correct
- [ ] Item 2: [name] - Correct
- [ ] Item 3: [name] - Correct

**Notes:**

---

### Document 2: [filename]

| Field | Value |
|-------|-------|
| **File** | |
| **Vendor Type** | |
| **Pages** | |
| **File Size** | |
| **Processing Time** | |
| **Items Extracted** | |
| **Overall Confidence** | |
| **QA Bucket** | |
| **Status** | SUCCESS / FAILED |

**Accuracy Spot Check:**
- [ ] Item 1: [name] - Correct
- [ ] Item 2: [name] - Correct
- [ ] Item 3: [name] - Correct

**Notes:**

---

### Document 3: [filename]

*(Copy this section for each additional document)*

---

## Extraction Accuracy Analysis

### Field-Level Accuracy

| Field | Correct | Incorrect | Not Extracted | Accuracy |
|-------|---------|-----------|---------------|----------|
| Solution Name | | | | |
| Fee Type | | | | |
| Category | | | | |
| Monthly Fee | | | | |
| One-Time Fee | | | | |
| Per-Unit Rate | | | | |

### Common Extraction Patterns

**Successfully Extracted:**
-
-
-

**Commonly Missed:**
-
-
-

---

## Quality Assurance Results

### QA Bucket Distribution

| Bucket | Count | Percentage |
|--------|-------|------------|
| Auto-Accept (>=90%) | | |
| Quick-Review (70-89%) | | |
| Manual-Entry (<70%) | | |

### QA Check Failures

| Check Type | Failure Count | Most Common Issue |
|------------|---------------|-------------------|
| Confidence Scoring | | |
| Cross-Validation | | |
| Business Rules | | |
| Source Traceability | | |

---

## Performance Analysis

### Processing Time Distribution

| Range | Count | Documents |
|-------|-------|-----------|
| <30 seconds | | |
| 30-60 seconds | | |
| 60-120 seconds | | |
| >120 seconds | | |

### Performance by Document Size

| Size Range | Avg Time | Notes |
|------------|----------|-------|
| <1 MB | | |
| 1-5 MB | | |
| >5 MB | | |

---

## Issues Encountered

### Critical Issues (Extraction Failures)

1. **Issue:**
   - **Document:**
   - **Error:**
   - **Impact:**
   - **Resolution:**

### Minor Issues (Warnings/Low Confidence)

1. **Issue:**
   - **Document:**
   - **Details:**
   - **Suggested Fix:**

---

## Edge Cases Identified

### Successfully Handled

1.
2.
3.

### Needs Improvement

1.
2.
3.

---

## Recommendations

### Immediate Actions
- [ ]
- [ ]
- [ ]

### Future Improvements
- [ ]
- [ ]
- [ ]

---

## Conclusion

**Production Readiness Assessment:**

[ ] **READY** - All thresholds met, no critical issues
[ ] **READY WITH CAVEATS** - Minor issues documented, acceptable for production
[ ] **NOT READY** - Critical issues must be addressed before production

**Summary:**



---

## Appendices

### A. Test File Manifest

| File | Source | Date Added |
|------|--------|------------|
| | | |
| | | |

### B. Extraction Output Files

| Input Document | Output Excel | Audit JSON |
|----------------|--------------|------------|
| | | |
| | | |

### C. Error Logs

```
[Paste relevant error logs here]
```

---

*Report generated on [date] by [tester]*
