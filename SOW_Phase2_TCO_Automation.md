# Statement of Work (SOW)
## TCO Automation System - Phase 2: Enterprise Scale-Up

**Document Version:** 1.0
**Date:** January 9, 2026
**Prepared For:** [Client Name]
**Prepared By:** [Consultant Name]

---

## 1. Executive Summary

### 1.1 Background

Phase 1 of the TCO Automation System has been successfully completed, demonstrating the ability to:
- Extract pricing data from FIS Word proposals and Jack Henry Excel deal sheets
- Normalize vendor-specific data into a standardized TCO schema with confidence scoring
- Populate Excel TCO templates with side-by-side vendor comparisons
- Achieve 95-99% extraction accuracy with complete audit trails
- Reduce manual TCO creation time from 2-4 hours to under 60 seconds per vendor

**Phase 1 Deliverables Completed:**
1. **TCO_Test_Output.xlsx** - FIS-only populated TCO template (42 normalized line items)
2. **TCO_Complete_Comparison.xlsx** - Side-by-side vendor comparison (176 total line items)
3. **Extracted JSON Files** - 6 validated extraction outputs with confidence scores

### 1.2 Phase 2 Objectives

Phase 2 expands the system to support enterprise-scale operations:
- **Volume Processing:** Handle 20+ new proposals per month
- **Historical Analysis:** Process and analyze historical proposal archives
- **Multi-Model Support:** Accommodate multiple TCO output models (various template formats)
- **Production Operations:** Establish sustainable operational workflows

---

## 2. Scope of Work

### 2.0 Discovery Phase (Pre-Development)

Before development begins, a structured Discovery Phase will validate assumptions, gather requirements, and reduce project risk. Discovery findings will directly inform the technical approach and may result in scope adjustments.

#### 2.0.1 Discovery Objectives

| ID | Objective | Output |
|----|-----------|--------|
| D0.1 | Validate volume assumptions | Confirmed monthly proposal volume and peak periods |
| D0.2 | Inventory historical proposals | File count, formats, date ranges, storage locations |
| D0.3 | Catalog TCO templates | Complete list of template variants with sample files |
| D0.4 | Assess legacy format complexity | Format compatibility matrix with effort estimates |
| D0.5 | Define exception handling requirements | Business rules for manual review triggers |
| D0.6 | Identify integration touchpoints | Upstream/downstream system dependencies |
| D0.7 | Document operational workflows | Current state vs. future state process maps |

#### 2.0.2 Discovery Activities

| Activity | Description | Duration |
|----------|-------------|----------|
| Stakeholder Interviews | Meet with analysts, managers, IT to gather requirements | 2-3 sessions |
| Historical Data Analysis | Sample and analyze historical proposal files | Collaborative |
| Template Inventory | Collect and document all TCO template variants | Collaborative |
| Current State Mapping | Document existing manual TCO creation process | 1 session |
| Technical Assessment | Evaluate infrastructure, access, deployment options | 1 session |
| Discovery Findings Review | Present findings and confirm scope | 1 session |

#### 2.0.3 Discovery Deliverables

| # | Deliverable | Description |
|---|-------------|-------------|
| DD1 | Discovery Report | Comprehensive findings document with recommendations |
| DD2 | Historical Proposal Inventory | Catalog of all historical files with metadata |
| DD3 | Template Catalog | All TCO templates with mapping requirements |
| DD4 | Format Compatibility Matrix | Support level for each document format found |
| DD5 | Updated Risk Register | Risks identified during discovery with mitigations |
| DD6 | Refined Scope Document | Any scope adjustments based on discovery findings |

#### 2.0.4 Discovery Exit Criteria

Discovery Phase is complete when:
- [ ] All discovery questions (Appendix D) have been answered
- [ ] Historical proposal inventory is complete (file count, formats, locations)
- [ ] All TCO template variants have been collected and cataloged
- [ ] Stakeholder sign-off on discovery findings
- [ ] Scope adjustments (if any) have been agreed upon
- [ ] Development phase can proceed with validated requirements

---

### 2.1 In-Scope Activities

#### 2.1.1 Volume Processing Infrastructure

| ID | Deliverable | Description |
|----|-------------|-------------|
| 2.1.1.1 | Batch Processing Engine | Automated system to process multiple proposals in queue |
| 2.1.1.2 | Job Scheduler | Configurable scheduling for processing windows (daily/weekly) |
| 2.1.1.3 | Progress Dashboard | Real-time visibility into processing status and queue |
| 2.1.1.4 | Notification System | Email/Slack alerts for completion, errors, and exceptions |
| 2.1.1.5 | Parallel Processing | Concurrent processing of multiple proposals |

#### 2.1.2 Historical Proposal Processing

| ID | Deliverable | Description |
|----|-------------|-------------|
| 2.1.2.1 | Bulk Import Utility | Tool to ingest historical proposal archives |
| 2.1.2.2 | Document Classification | Auto-detect vendor type (FIS/JH) and document format |
| 2.1.2.3 | Version Handling | Support for legacy document formats and variations |
| 2.1.2.4 | De-duplication Logic | Identify and handle duplicate proposals |
| 2.1.2.5 | Historical Data Store | Structured storage for processed historical data |

#### 2.1.3 Multi-Model TCO Support

| ID | Deliverable | Description |
|----|-------------|-------------|
| 2.1.3.1 | Template Registry | Centralized management of multiple TCO templates |
| 2.1.3.2 | Template Detection | Auto-match proposals to appropriate TCO model |
| 2.1.3.3 | Dynamic Column Mapping | Configurable field-to-column mappings per template |
| 2.1.3.4 | Template Versioning | Track and manage template versions |
| 2.1.3.5 | Custom Template Support | Ability to add new TCO models without code changes |

#### 2.1.4 Quality Assurance & Validation

| ID | Deliverable | Description |
|----|-------------|-------------|
| 2.1.4.1 | Confidence Threshold Rules | Configurable thresholds per field type |
| 2.1.4.2 | Exception Queue | Manual review workflow for low-confidence extractions |
| 2.1.4.3 | Validation Reports | Detailed accuracy reports per batch |
| 2.1.4.4 | Audit Trail Enhancement | Complete lineage from source to output |
| 2.1.4.5 | Reconciliation Tools | Compare automated vs. manual TCO outputs |

#### 2.1.5 Operational Infrastructure

| ID | Deliverable | Description |
|----|-------------|-------------|
| 2.1.5.1 | Configuration Management | Environment-based settings (dev/test/prod) |
| 2.1.5.2 | Logging & Monitoring | Centralized logging with error tracking |
| 2.1.5.3 | Backup & Recovery | Data backup and disaster recovery procedures |
| 2.1.5.4 | Security Hardening | Access controls, encryption, secure storage |
| 2.1.5.5 | Performance Optimization | Handle 20+ proposals/month efficiently |

### 2.2 Out-of-Scope Activities

The following items are explicitly excluded from this engagement:
- Integration with external CRM/ERP systems (future phase)
- Mobile application development
- Custom vendor extractors beyond FIS and Jack Henry
- Cloud hosting infrastructure setup (on-premise deployment only)
- End-user training beyond documented procedures
- Support for non-Excel TCO output formats

---

## 3. Deliverables

### 3.1 Software Deliverables

| # | Deliverable | Format | Description |
|---|-------------|--------|-------------|
| D1 | Batch Processing Module | Python Package | Queue management and parallel processing |
| D2 | Job Scheduler | Python + Config | Automated scheduling with cron-like syntax |
| D3 | Template Registry System | Python + JSON | Multi-template management and mapping |
| D4 | Bulk Import Utility | CLI Tool | Historical proposal ingestion |
| D5 | Exception Management UI | Web Interface | Review queue for manual validation |
| D6 | Monitoring Dashboard | Web Interface | Real-time processing status |
| D7 | Reporting Module | Python + Excel | Batch processing and accuracy reports |

### 3.2 Documentation Deliverables

| # | Deliverable | Description |
|---|-------------|-------------|
| D8 | Operations Manual | Step-by-step procedures for daily operations |
| D9 | Template Configuration Guide | How to add/modify TCO templates |
| D10 | Troubleshooting Guide | Common issues and resolution steps |
| D11 | API Documentation | Technical reference for all modules |
| D12 | System Architecture Document | Updated architecture with Phase 2 components |

### 3.3 Process Deliverables

| # | Deliverable | Description |
|---|-------------|-------------|
| D13 | Standard Operating Procedures | Runbooks for common operational tasks |
| D14 | Exception Handling Workflow | Process for manual review cases |
| D15 | Quality Control Checklist | Validation procedures for output review |

---

## 4. Technical Approach

### 4.1 Architecture Enhancement

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        PHASE 2 ARCHITECTURE                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐               │
│  │   INGESTION  │    │  PROCESSING  │    │    OUTPUT    │               │
│  │    LAYER     │    │    LAYER     │    │    LAYER     │               │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘               │
│         │                   │                   │                        │
│  ┌──────▼───────┐    ┌──────▼───────┐    ┌──────▼───────┐               │
│  │ File Watcher │    │ Job Queue    │    │ Template     │               │
│  │ Bulk Import  │    │ Scheduler    │    │ Registry     │               │
│  │ Doc Classify │    │ Workers (N)  │    │ Writer Engine│               │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘               │
│         │                   │                   │                        │
│         └───────────────────┼───────────────────┘                        │
│                             │                                            │
│                    ┌────────▼────────┐                                   │
│                    │   DATA STORE    │                                   │
│                    │  ─────────────  │                                   │
│                    │ Proposals DB    │                                   │
│                    │ Extractions     │                                   │
│                    │ Templates       │                                   │
│                    │ Audit Logs      │                                   │
│                    └────────┬────────┘                                   │
│                             │                                            │
│         ┌───────────────────┼───────────────────┐                        │
│         │                   │                   │                        │
│  ┌──────▼───────┐    ┌──────▼───────┐    ┌──────▼───────┐               │
│  │  MONITORING  │    │  EXCEPTION   │    │  REPORTING   │               │
│  │  Dashboard   │    │  Queue UI    │    │  Engine      │               │
│  │  Alerts      │    │  Review Flow │    │  Analytics   │               │
│  └──────────────┘    └──────────────┘    └──────────────┘               │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Technology Stack Additions

| Component | Technology | Purpose |
|-----------|------------|---------|
| Job Queue | Celery + Redis | Distributed task processing |
| Database | SQLite/PostgreSQL | Structured data storage |
| Web Framework | FastAPI | Dashboard and API endpoints |
| Monitoring | Prometheus + Grafana | Metrics and alerting |
| File Watching | Watchdog | Auto-detect new proposals |

### 4.3 Multi-Template Architecture

```
Template Registry
├── templates/
│   ├── tco_7year_standard/
│   │   ├── template.xlsx
│   │   ├── mapping.json
│   │   └── config.yaml
│   ├── tco_5year_compact/
│   │   ├── template.xlsx
│   │   ├── mapping.json
│   │   └── config.yaml
│   └── tco_10year_detailed/
│       ├── template.xlsx
│       ├── mapping.json
│       └── config.yaml
└── registry.json (template index with metadata)
```

---

## 5. Project Plan

### 5.1 Phase 2 Work Breakdown Structure

```
Phase 2: Enterprise Scale-Up
│
├── WP1: Foundation & Infrastructure
│   ├── 1.1 Database schema design
│   ├── 1.2 Job queue implementation
│   ├── 1.3 Configuration management
│   └── 1.4 Logging infrastructure
│
├── WP2: Batch Processing Engine
│   ├── 2.1 Queue management system
│   ├── 2.2 Parallel worker implementation
│   ├── 2.3 Error handling & retry logic
│   └── 2.4 Progress tracking
│
├── WP3: Template Registry System
│   ├── 3.1 Template storage & versioning
│   ├── 3.2 Dynamic mapping engine
│   ├── 3.3 Template detection logic
│   └── 3.4 Configuration UI
│
├── WP4: Historical Processing
│   ├── 4.1 Bulk import utility
│   ├── 4.2 Document classification
│   ├── 4.3 Legacy format handlers
│   └── 4.4 De-duplication logic
│
├── WP5: Exception Management
│   ├── 5.1 Review queue backend
│   ├── 5.2 Web-based review UI
│   ├── 5.3 Approval workflow
│   └── 5.4 Feedback loop integration
│
├── WP6: Monitoring & Reporting
│   ├── 6.1 Status dashboard
│   ├── 6.2 Notification system
│   ├── 6.3 Analytics & reporting
│   └── 6.4 Audit trail enhancement
│
├── WP7: Testing & Validation
│   ├── 7.1 Unit test expansion
│   ├── 7.2 Integration testing
│   ├── 7.3 Volume testing (20+ proposals)
│   └── 7.4 User acceptance testing
│
└── WP8: Documentation & Training
    ├── 8.1 Technical documentation
    ├── 8.2 Operations manual
    ├── 8.3 User guides
    └── 8.4 Knowledge transfer sessions
```

### 5.2 Milestone Schedule

| Milestone | Description | Work Packages |
|-----------|-------------|---------------|
| **M0** | **Discovery Complete** | **Discovery Phase (Section 2.0)** |
| M1 | Foundation Complete | WP1 |
| M2 | Batch Processing Operational | WP2 |
| M3 | Multi-Template Support | WP3 |
| M4 | Historical Processing Ready | WP4 |
| M5 | Exception Management Live | WP5 |
| M6 | Monitoring & Reporting | WP6 |
| M7 | Testing Complete | WP7 |
| M8 | Documentation & Go-Live | WP8 |

**Critical Gate:** Development work packages (WP1-WP8) do not begin until Discovery (M0) is complete and findings are accepted.

### 5.3 Dependencies

```
WP1 ──────┬──────> WP2 ─────┐
          │                 │
          ├──────> WP3 ─────┼──────> WP5 ──────> WP6 ──────> WP7 ──────> WP8
          │                 │
          └──────> WP4 ─────┘
```

---

## 6. Resource Requirements

### 6.1 Team Structure

| Role | Responsibility | Allocation |
|------|----------------|------------|
| Project Lead | Overall delivery, stakeholder management | Part-time |
| Senior Developer | Core development, architecture decisions | Full-time |
| Developer | Feature implementation, testing | Full-time |
| QA Engineer | Testing, validation, documentation | Part-time |
| Business Analyst | Requirements, UAT coordination | Part-time |

### 6.2 Client Resources Required

| Resource | Purpose | When Needed |
|----------|---------|-------------|
| Historical Proposals | Training data for legacy format handling | WP4 |
| TCO Templates (All Variants) | Template registry setup | WP3 |
| Business SME | Requirements clarification, UAT | Throughout |
| IT Support | Environment access, deployment | WP1, WP8 |
| Sample Review Cases | Exception workflow validation | WP5 |

---

## 7. Assumptions & Constraints

### 7.1 Assumptions

1. Historical proposals are available in digital format (Word/Excel)
2. All TCO template variants follow similar structural patterns
3. Client will provide timely access to sample files and SME resources
4. Existing Phase 1 codebase remains the foundation
5. Processing volume of 20 proposals/month is the target capacity
6. On-premise deployment (no cloud infrastructure required)

### 7.2 Constraints

1. Must maintain backward compatibility with Phase 1 outputs
2. Processing must complete within business hours for new proposals
3. Historical processing can run during off-peak hours
4. Manual review turnaround target: 24 hours for exceptions

### 7.3 Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Historical documents in unknown formats | High | Medium | Early discovery phase with sample analysis |
| TCO template variations more complex than expected | Medium | Medium | Flexible mapping engine with fallback options |
| Volume exceeds 20/month capacity | Low | Low | Scalable architecture with parallel processing |
| Integration dependencies with other systems | Medium | Low | Modular design with clear API boundaries |

---

## 8. Acceptance Criteria

### 8.1 Functional Acceptance

| ID | Criteria | Validation Method |
|----|----------|-------------------|
| AC1 | System processes 20+ proposals per month without manual intervention | Volume test with real proposals |
| AC2 | Historical proposals are imported and processed with >90% success rate | Batch processing report |
| AC3 | All TCO template variants are supported via configuration | Template coverage test |
| AC4 | Exception queue enables manual review with resolution tracking | Workflow walkthrough |
| AC5 | Monitoring dashboard shows real-time status and alerts | UI demonstration |

### 8.2 Performance Acceptance

| ID | Criteria | Target |
|----|----------|--------|
| PA1 | Single proposal processing time | < 2 minutes |
| PA2 | Batch of 20 proposals | < 30 minutes |
| PA3 | Dashboard response time | < 3 seconds |
| PA4 | System availability | 99% during business hours |

### 8.3 Quality Acceptance

| ID | Criteria | Target |
|----|----------|--------|
| QA1 | Extraction accuracy (auto-accepted) | > 95% |
| QA2 | Overall processing success rate | > 98% |
| QA3 | Zero data loss or corruption | 100% |
| QA4 | Complete audit trail for all outputs | 100% |

---

## 9. Change Management

### 9.1 Change Request Process

1. Change requests submitted in writing with business justification
2. Impact assessment by project team (scope, effort, dependencies)
3. Client approval required for material changes
4. Approved changes documented and baselined

### 9.2 Scope Change Pricing

Changes outside the defined scope will be estimated and quoted separately based on:
- Complexity and effort required
- Impact on existing deliverables
- Timeline implications

---

## 10. Commercial Terms

### 10.1 Pricing Structure

| Component | Pricing Model | Notes |
|-----------|---------------|-------|
| Phase 2 Development | Fixed Price | Based on defined scope |
| Additional Templates | Per Template | Beyond initial 5 templates |
| Additional Vendors | Per Vendor | Beyond FIS and Jack Henry |
| Support & Maintenance | Monthly Retainer | Post go-live support |

### 10.2 Payment Schedule

| Milestone | Payment | Trigger |
|-----------|---------|---------|
| Project Kickoff | 15% | SOW Execution |
| Discovery Complete | 10% | Discovery Report Accepted |
| M4 Complete (Historical Processing) | 25% | Milestone Acceptance |
| M7 Complete (Testing) | 25% | UAT Sign-off |
| M8 Complete (Go-Live) | 25% | Final Acceptance |

**Note:** Discovery Phase findings may result in scope adjustments. Any material scope changes will be documented and may affect subsequent milestone pricing.

### 10.3 Warranty

- 30-day warranty period following final acceptance
- Defect resolution at no additional cost
- Excludes changes to requirements or new features

---

## 11. Governance

### 11.1 Communication Plan

| Meeting | Frequency | Participants | Purpose |
|---------|-----------|--------------|---------|
| Status Update | Weekly | Project Team + Client PM | Progress review |
| Steering Committee | Bi-weekly | Leadership | Escalations, decisions |
| Technical Review | As needed | Technical leads | Architecture decisions |
| Demo Sessions | Per milestone | All stakeholders | Deliverable review |

### 11.2 Escalation Path

```
Level 1: Project Manager (response: 24 hours)
    ↓
Level 2: Engagement Lead (response: 48 hours)
    ↓
Level 3: Executive Sponsor (response: 72 hours)
```

---

## 12. Signatures

This Statement of Work is agreed upon by:

**Client:**

Name: ________________________________

Title: ________________________________

Signature: ____________________________

Date: ________________________________


**Consultant:**

Name: ________________________________

Title: ________________________________

Signature: ____________________________

Date: ________________________________

---

## Appendix A: Phase 1 Summary

### Completed Deliverables

1. **FIS Extractor** - Parses Word documents, extracts 9 tables, 42 normalized line items
2. **Jack Henry Extractor** - Parses Excel workbooks, 14 sheets, 134+ line items
3. **Schema Mapper** - Normalizes vendor data to standardized TCO schema
4. **TCO Writer** - Populates Excel templates with validation
5. **Quality Assurance** - 4-layer validation with confidence scoring
6. **CLI Interface** - Command-line tool for batch processing

### Validated Outputs

| Output File | Content | Line Items |
|-------------|---------|------------|
| TCO_Test_Output.xlsx | FIS-only TCO | 42 |
| TCO_Complete_Comparison.xlsx | FIS + Jack Henry comparison | 176 |
| Extracted JSON (6 files) | Raw and AI-processed extractions | Various |

### Performance Metrics

- Processing time per vendor: < 60 seconds
- Extraction accuracy: 95-99%
- Manual effort reduction: 2-4 hours → < 1 minute

---

## Appendix B: Template Registry Specification

### Template Configuration Schema

```yaml
# Example: tco_7year_standard/config.yaml
template:
  name: "7-Year Standard TCO"
  version: "1.0"
  file: "template.xlsx"

sheets:
  line_items:
    name: "Line Items"

sections:
  fis:
    bundle:
      start_row: 7
      end_row: 21
    non_bundle_required:
      start_row: 22
      end_row: 99
    non_bundle_optional:
      start_row: 100
      end_row: 120
    one_time:
      start_row: 121
      end_row: 140

  jack_henry:
    bundle:
      start_row: 7
      end_row: 50
    # ... additional sections

columns:
  solution_name: B
  fee_type: C
  category: D
  year_1_qty: E
  year_1_cost: F
  # ... additional columns

growth_rates:
  default: 0.03
  cpi_adjustment: 0.025

validation:
  sum_check: true
  rate_validation: true
```

---

## Appendix C: Historical Processing Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                 HISTORICAL PROCESSING FLOW                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. DISCOVERY                                                │
│     ├── Scan archive folders                                 │
│     ├── Inventory all files (Word, Excel, PDF)              │
│     ├── Generate discovery report                           │
│     └── Identify unknown formats                            │
│                                                              │
│  2. CLASSIFICATION                                           │
│     ├── Auto-detect vendor (FIS/JH/Unknown)                 │
│     ├── Identify document version/format                    │
│     ├── Match to appropriate template                       │
│     └── Flag exceptions for review                          │
│                                                              │
│  3. PROCESSING                                               │
│     ├── Queue files by priority                             │
│     ├── Process in parallel batches                         │
│     ├── Track progress and errors                           │
│     └── Generate extraction outputs                         │
│                                                              │
│  4. VALIDATION                                               │
│     ├── Apply confidence scoring                            │
│     ├── Route low-confidence to review                      │
│     ├── Generate validation reports                         │
│     └── Update processing statistics                        │
│                                                              │
│  5. STORAGE                                                  │
│     ├── Store in structured database                        │
│     ├── Link source documents to outputs                    │
│     ├── Maintain audit trail                                │
│     └── Enable search and retrieval                         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Appendix D: Discovery Questions Checklist

The following questions must be answered during the Discovery Phase. Responses will inform scope refinement, technical approach, and risk mitigation strategies.

### D.1 Volume & Capacity Questions

| # | Question | Priority | Answer |
|---|----------|----------|--------|
| D.1.1 | What is the current monthly volume of new vendor proposals? | High | |
| D.1.2 | What is the expected volume growth over the next 12-24 months? | Medium | |
| D.1.3 | Are there seasonal peaks (e.g., quarter-end, budget cycles)? | Medium | |
| D.1.4 | What is the maximum volume during peak periods? | High | |
| D.1.5 | What is the required turnaround time for new proposals? | High | |
| D.1.6 | How many analysts will be using the system concurrently? | Medium | |

### D.2 Historical Proposal Questions

| # | Question | Priority | Answer |
|---|----------|----------|--------|
| D.2.1 | How many historical proposals exist in total? | High | |
| D.2.2 | What date range do the historical proposals cover? | High | |
| D.2.3 | Where are historical proposals currently stored? (File shares, SharePoint, local drives) | High | |
| D.2.4 | Are historical proposals organized by any structure? (By year, client, vendor) | Medium | |
| D.2.5 | What file formats are present? (Word versions, Excel versions, PDFs) | High | |
| D.2.6 | Are there any scanned/image-based documents requiring OCR? | High | |
| D.2.7 | Do historical files include the corresponding completed TCO outputs? | Medium | |
| D.2.8 | Are there any access restrictions or permissions issues? | Medium | |
| D.2.9 | What is the priority for processing historical data? (All at once, phased by date) | Medium | |
| D.2.10 | Are there any historical proposals that should be excluded? | Low | |

### D.3 TCO Template Questions

| # | Question | Priority | Answer |
|---|----------|----------|--------|
| D.3.1 | How many distinct TCO template variants are currently in use? | High | |
| D.3.2 | What are the key differences between template variants? | High | |
| D.3.3 | Are templates organized by term length? (5-year, 7-year, 10-year) | High | |
| D.3.4 | Are there client-specific or deal-specific template customizations? | Medium | |
| D.3.5 | Who owns/maintains the TCO templates? | Medium | |
| D.3.6 | How often do templates change? | Medium | |
| D.3.7 | Is there a master/golden template that others derive from? | Medium | |
| D.3.8 | Do templates contain macros or VBA code? | High | |
| D.3.9 | Are there formula dependencies that must be preserved? | High | |
| D.3.10 | Can we obtain a copy of each template variant for analysis? | High | |

### D.4 Vendor & Document Format Questions

| # | Question | Priority | Answer |
|---|----------|----------|--------|
| D.4.1 | Are FIS and Jack Henry the only vendors, or are there others? | High | |
| D.4.2 | If other vendors exist, what is the volume for each? | High | |
| D.4.3 | Have FIS proposal formats changed over time? (Layout, sections, tables) | High | |
| D.4.4 | Have Jack Henry proposal formats changed over time? | High | |
| D.4.5 | Are there multiple proposal types per vendor? (Initial, renewal, amendment) | Medium | |
| D.4.6 | Do proposals include attachments or supplementary files? | Medium | |
| D.4.7 | Are there password-protected or encrypted documents? | Medium | |
| D.4.8 | Do proposals contain handwritten annotations or comments? | Low | |

### D.5 Exception Handling & Quality Questions

| # | Question | Priority | Answer |
|---|----------|----------|--------|
| D.5.1 | What confidence level triggers manual review? (Current: 90%) | High | |
| D.5.2 | Who is responsible for reviewing exceptions? | High | |
| D.5.3 | What is the expected exception rate? | Medium | |
| D.5.4 | What is the acceptable turnaround for exception resolution? | Medium | |
| D.5.5 | What fields are most critical for accuracy? | High | |
| D.5.6 | Are there business rules that should trigger review? (e.g., large dollar variances) | Medium | |
| D.5.7 | How should conflicts between automated and manual values be resolved? | Medium | |
| D.5.8 | Should corrections feed back to improve future extractions? | Medium | |

### D.6 Operational & Process Questions

| # | Question | Priority | Answer |
|---|----------|----------|--------|
| D.6.1 | What is the current manual process for creating TCOs? | High | |
| D.6.2 | How long does manual TCO creation currently take? | High | |
| D.6.3 | Who are the primary users of the system? (Titles, number of users) | High | |
| D.6.4 | What business hours should the system be available? | Medium | |
| D.6.5 | Are there SLAs for TCO delivery to clients? | Medium | |
| D.6.6 | How are completed TCOs currently delivered/stored? | Medium | |
| D.6.7 | Is there an existing approval workflow for TCOs? | Medium | |
| D.6.8 | What happens when a proposal is revised/updated? | Medium | |

### D.7 Technical & Infrastructure Questions

| # | Question | Priority | Answer |
|---|----------|----------|--------|
| D.7.1 | Where will the system be deployed? (On-premise server, cloud, user workstations) | High | |
| D.7.2 | What operating system is available? (Windows Server, Linux) | High | |
| D.7.3 | What database platform is preferred? (SQLite, PostgreSQL, SQL Server) | Medium | |
| D.7.4 | Are there firewall or network restrictions? | Medium | |
| D.7.5 | Is there an existing authentication system to integrate with? (AD, SSO) | Medium | |
| D.7.6 | What email system is available for notifications? (SMTP, Exchange, O365) | Medium | |
| D.7.7 | Is Slack or Teams available for notifications? | Low | |
| D.7.8 | What is the backup/disaster recovery strategy? | Medium | |
| D.7.9 | Who will provide IT support for the deployed system? | Medium | |
| D.7.10 | Are there any security or compliance requirements? (SOC2, data residency) | High | |

### D.8 Integration Questions

| # | Question | Priority | Answer |
|---|----------|----------|--------|
| D.8.1 | Where do new proposals currently come from? (Email, file drop, portal) | High | |
| D.8.2 | Should the system integrate with a CRM or deal management system? | Medium | |
| D.8.3 | Should completed TCOs be uploaded to a document management system? | Medium | |
| D.8.4 | Are there reporting or BI systems that should consume the data? | Low | |
| D.8.5 | Are there any APIs or systems we need to call or receive calls from? | Medium | |

### D.9 Reporting & Analytics Questions

| # | Question | Priority | Answer |
|---|----------|----------|--------|
| D.9.1 | What reports are needed for daily operations? | High | |
| D.9.2 | What management/executive reports are required? | Medium | |
| D.9.3 | What metrics are most important to track? | High | |
| D.9.4 | How should reports be delivered? (Dashboard, email, scheduled export) | Medium | |
| D.9.5 | Are there historical trend analysis requirements? | Medium | |
| D.9.6 | Should the system support ad-hoc queries or custom reports? | Low | |

### D.10 Training & Change Management Questions

| # | Question | Priority | Answer |
|---|----------|----------|--------|
| D.10.1 | Who needs training on the new system? | High | |
| D.10.2 | What is the preferred training format? (In-person, remote, self-service) | Medium | |
| D.10.3 | Is there a change management process for new tools? | Medium | |
| D.10.4 | Who will be the system administrator(s)? | High | |
| D.10.5 | What level of ongoing support is expected post-launch? | High | |

---

## Appendix E: Discovery Session Agenda Templates

### E.1 Stakeholder Interview Agenda (90 minutes)

```
1. Introduction & Context (10 min)
   - Project background
   - Interview objectives

2. Current State (25 min)
   - Walk through current TCO creation process
   - Pain points and challenges
   - Volume and capacity discussion

3. Requirements Discussion (30 min)
   - Review discovery questions relevant to stakeholder
   - Template and format discussion
   - Exception handling preferences

4. Future State Vision (15 min)
   - Desired improvements
   - Success criteria from stakeholder perspective

5. Wrap-up (10 min)
   - Action items
   - Next steps
```

### E.2 Historical Data Analysis Session (2 hours)

```
1. Access & Inventory (30 min)
   - Connect to file storage locations
   - Run file inventory scan
   - Categorize by type/vendor/date

2. Sampling & Analysis (60 min)
   - Select representative samples from each category
   - Open and analyze document structures
   - Identify format variations
   - Document anomalies

3. Compatibility Assessment (20 min)
   - Test sample files against current extractors
   - Identify gaps requiring new handlers
   - Estimate effort for legacy support

4. Documentation (10 min)
   - Update inventory spreadsheet
   - Document findings
   - Flag issues for follow-up
```

### E.3 Template Catalog Session (90 minutes)

```
1. Template Collection (20 min)
   - Gather all template variants
   - Organize by type/purpose

2. Template Analysis (45 min)
   - For each template:
     - Document structure (sheets, sections)
     - Identify column mappings
     - Note formulas and dependencies
     - Flag macros or special features

3. Mapping Requirements (15 min)
   - Document mapping differences between templates
   - Identify common patterns
   - Assess configuration complexity

4. Documentation (10 min)
   - Complete template catalog
   - Note questions for follow-up
```

---

## Appendix F: Discovery Findings Template

### F.1 Executive Summary
[Brief summary of key findings and recommendations]

### F.2 Volume Analysis
| Metric | Current | Expected | Notes |
|--------|---------|----------|-------|
| Monthly new proposals | | | |
| Peak volume | | | |
| Historical backlog | | | |

### F.3 Historical Proposal Inventory
| Category | Count | Date Range | Formats | Compatibility |
|----------|-------|------------|---------|---------------|
| FIS Proposals | | | | |
| Jack Henry Proposals | | | | |
| Other Vendors | | | | |
| Unknown/Mixed | | | | |

### F.4 Template Inventory
| Template Name | Term | Usage | Complexity | Notes |
|---------------|------|-------|------------|-------|
| | | | | |

### F.5 Key Risks Identified
| Risk | Impact | Mitigation |
|------|--------|------------|
| | | |

### F.6 Scope Adjustments
[Any recommended changes to scope based on findings]

### F.7 Next Steps
[Recommended path forward]

---

*End of Statement of Work*
