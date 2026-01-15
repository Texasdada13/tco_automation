# Dummy Proposals Directory

Store sample vendor proposals here for testing the TCO extraction pipeline.

## Subdirectories

### `/fis-like/`
FIS-style banking proposals with characteristics:
- HORIZON core processing bundles
- Digital banking packages (Digital One)
- Payment processing (Payments One)
- Monthly fee structures with annual CPI increases
- Multi-year term options (5/7/10 years)

### `/jack-henry-like/`
Jack Henry-style proposals with characteristics:
- Product matrix format (often in Excel)
- SilverLake/Xperience product bundles
- Per-product pricing with multiple scenarios
- Cell comments containing pricing notes

### `/csi-like/`
CSI-style proposals with characteristics:
- Core banking system pricing
- Similar structure to FIS proposals
- Monthly and one-time fee breakdowns

### `/other-vendors/`
Other banking vendor proposals:
- Fiserv
- Finastra
- Treasury management providers
- Other enterprise banking software vendors

## File Naming Convention

Use descriptive names that indicate the source and type:
```
[vendor-type]_[source]_[complexity]_[number].pdf

Examples:
- fis_gov_rfp_simple_001.pdf
- jh_template_medium_001.xlsx
- csi_sample_complex_001.pdf
```

## Sample Sources

See `SAMPLE_ACQUISITION_GUIDE.md` in the parent directory for sources to find sample proposals.
