# Westchester County Data Platform - Multi-LLM Agent Instructions

## Project Overview

**Purpose**: Comprehensive data platform for Westchester County providing demographic, economic, transit, and geographic analysis through interactive web interface.

**Tech Stack**:
- Frontend: React 19 + TypeScript + Vite + Tailwind CSS + Leaflet (maps) + Recharts (charts)
- Backend: FastAPI + Python + pandas + geopandas
- Data Sources: Census API, GTFS transit data, NY State datasets

**Directory Structure**: Shaikh Tonak Pattern (95% success rate)
```
Westchester/
├── Output/              # User-facing deliverables
│   ├── Data/           # Excel files (ONE SHEET per file)
│   ├── PDFs/           # LaTeX-generated reports
│   └── README.md       # User quick start
├── Technical/          # Implementation details
│   ├── src/           # Source code
│   ├── data/          # Raw/processed data
│   ├── docs/          # LaTeX sources
│   ├── scripts/       # Automation
│   └── README.md      # Technical guide
└── HANDOFF_DOCUMENTATION.md
```

## MULTI-LLM COMPATIBILITY (UNIVERSAL AGENT STANDARDS)

### Platform-Agnostic Development
This project supports all LLM platforms equally:
- **Claude Code**: Primary development environment
- **GLM-4.6**: Use `glmcc` launcher for full compatibility
- **Perplexity**: Enhanced research capabilities across all platforms

### Universal DALM Processing
All platforms use identical DALM (Direct Agent LLM Method) procedures:
- **File Size Limits**: 1MB max per chunk, 10 pages max per segment
- **Processing Method**: Universal DALM orchestrator handles all LLMs
- **Attribution Tracking**: All platforms log which LLM processed each document
- **Quality Standards**: Identical validation regardless of LLM used

### Cross-Platform Commands
All Arcanum slash commands work identically across platforms:
- `/readystart` - Initialize any agent with project context
- `/status` - Check workspace status across all platforms
- `/workspace` - Navigate and understand project structure
- `/library-index` - Process research materials (Robert integration)
- `/latex-report` - Generate professional reports
- `/methodology` - Apply research frameworks
- `/research` - Execute systematic research workflows

### Performance Standards
- **Instance Limits**: Maximum 4 concurrent instances across ALL platforms
- **Resource Monitoring**: Druck tracks usage regardless of LLM platform
- **Quality Assurance**: Identical standards for all platforms

---

## MANDATORY DRUCK STANDARDS (NON-NEGOTIABLE)

### 1. Excel Files - ONE SHEET PER FILE
```
✅ ALWAYS: Create separate Excel files for each dataset
✅ ALWAYS: Use machine-readable column names
✅ ALWAYS: Black & White formatting only
✅ ALWAYS: Save to Output/Data/
❌ NEVER: Create multiple sheets/tabs in one file
```

**Validation Script**: `Technical/scripts/validate_excel.py`

### 2. LaTeX Reports - ALL FINALS IN LATEX
```
✅ ALWAYS: Use LaTeX for final reports
✅ ALWAYS: Save .tex sources in Technical/docs/
✅ ALWAYS: Compile PDFs to Output/PDFs/
✅ ALWAYS: Embed visualizations (no separate images)
❌ NEVER: Use Markdown or Word for final reports
```

**Templates Available**:
- `methodology_report_template.tex` - Technical foundation
- `analysis_report_template.tex` - Findings with visualizations
- `executive_summary_template.tex` - Non-technical overview
- `reporting_strategy_template.tex` - Output catalog

### 3. Data Processing - NO SILENT DECISIONS
```
🚨 CRITICAL: Document EVERY data processing step
🚨 CRITICAL: Ask before ANY data treatment choices
🚨 CRITICAL: NO shortcuts in replication
🚨 CRITICAL: NO interpolation without permission
✅ ALWAYS: Create DATA_PROCESSING_LOG.md
✅ ALWAYS: Explain rationale for each step
```

### 4. Production Quality - BLOOMBERG STANDARDS
```
✅ Professional UI/UX (not prototype quality)
✅ Mobile-responsive design (test on tablets)
✅ Fast performance (< 2 second load times)
✅ Comprehensive error handling
✅ Production-ready code from day one
```

### 5. Progress Tracking - HYPER-DETAILED LOGGING
```
✅ Update Technical/PROGRESS_LOG.md every session
✅ Document ALL decisions made
✅ Log rationale and alternatives considered
✅ Note how to roll back if needed
✅ Minimal status updates to Nick (major milestones only)
```

## COMPLETION RATING FORMULA

```
Completion % =
  (Core Functionality Working × 50%) +
  (Output Formats Correct × 20%) +
  (Documentation Complete × 15%) +
  (Testing/Validation Done × 10%) +
  (Production Polish × 5%)
```

**Reality Checks Before Claiming 90%+**:
- [ ] Main feature works in fresh environment?
- [ ] All Excel files have ONE sheet?
- [ ] PDFs exist in Output/PDFs/?
- [ ] Fresh environment test passed?
- [ ] Mobile-responsive verified?

## PROJECT-SPECIFIC REQUIREMENTS

### Data Sources
1. **Census API**: Demographic and economic data
   - Store API key in environment variables (never commit)
   - Document all API calls in Technical/docs/DATA_SOURCES.md
   - Cache responses to minimize API usage

2. **GTFS Transit Data**: Public transportation information
   - Download and process GTFS feeds
   - Document update frequency and sources

3. **NY State Data Portal**: State-level datasets
   - Document data provenance
   - Track version and update dates

### Robin Data Integration
- **NEVER modify original Robin data**
- Copy to `Technical/data/robin_sourced/`
- Document usage in `Technical/data/ROBIN_DATA_USAGE.md`
- Process local copies only

### Frontend Development
- **React Components**: Organize by feature (charts/, map/, dashboards/)
- **TypeScript**: Strict type checking enabled
- **Tailwind CSS**: Use utility-first approach
- **Leaflet Maps**: Ensure proper attribution
- **Recharts**: Responsive chart configurations
- **Mobile Testing**: Test on 375px (phone) and 768px (tablet) viewports

### Backend Development
- **FastAPI**: RESTful API design
- **Error Handling**: Return informative error messages
- **Data Validation**: Use Pydantic models
- **CORS**: Configure appropriately for frontend
- **Logging**: Comprehensive logging for debugging

## VALIDATION CHECKLIST

Before Handoff:
- [ ] Fresh environment test passed
- [ ] All Excel files validated (ONE sheet each)
- [ ] LaTeX PDFs compiled and in Output/PDFs/
- [ ] Primary functionality works without errors
- [ ] Mobile responsiveness verified
- [ ] PROGRESS_LOG.md current and complete
- [ ] HANDOFF_DOCUMENTATION.md comprehensive
- [ ] All decisions documented with rationale

## WHEN TO ASK NICK

✅ **Always Ask About**:
- Requirements clarification
- Data processing approaches
- Accuracy vs. performance tradeoffs
- Major architecture changes

❌ **Don't Ask About**:
- Implementation details (decide & document)
- Minor UI adjustments
- Code organization choices
- Library/package selections

## ESSENTIAL DRUCK DOCUMENTS

Read these for complete standards:
1. `D:/Arcanum/Council/Druck/AGENT_QUICK_START_GUIDE.md`
2. `D:/Arcanum/Council/Druck/AGENT_STANDARDS_AND_BEST_PRACTICES.md`
3. `D:/Arcanum/Council/Druck/COMPLETE_STANDARDS_FRAMEWORK_OCT2025.md`
4. `D:/Arcanum/Council/Druck/QUICK_REFERENCE_CARD.md`

## SUCCESS FORMULA

1. Understand Nick's requirements completely
2. Use Shaikh Tonak directory structure
3. Document decisions (PROGRESS_LOG.md)
4. Test functionality (fresh environment)
5. Validate outputs (ONE-SHEET Excel, LaTeX PDFs)
6. Complete documentation (HANDOFF_DOCUMENTATION.md)
7. Pass all validation checks
= **90%+ Success Rate**

---

## 🚨 NEXT STEPS - IMMEDIATE ACTION REQUIRED

### Current Project Status: 70% Complete
**Critical Blocker**: Manual PDF data collection from Westchester County sources
**Timeline to Completion**: 3-4 weeks
**Priority**: HIGH - Complete existing near-finished project

---

## 📊 Data Collection Strategy (Critical Path)

### Files Needed: 70 Total Documents
**Priority Order**:

#### 1. Budget Data (15 files) - HIGHEST PRIORITY
- **2024 Adopted Budget PDF** - Core financial data
- **2023-2025 Proposed Budget PDFs** - Multi-year planning
- **Budget Narrative Documents** - Explanations and context
- **Capital Budget PDFs** - Infrastructure spending plans

#### 2. Tax Levy Reports (12 files) - CORE FUNCTIONALITY
- **Annual Tax Levy Reports** (2020-2024) - Revenue analysis
- **Property Tax Assessment Data** - Base calculations
- **Tax Rate History** - Trend analysis foundation
- **Special District Tax Reports** - Granular revenue data

#### 3. Infrastructure Data (20 files) - COMPREHENSIVE COVERAGE
- **Capital Improvement Plans** - Project pipeline
- **Road Maintenance Reports** - Transportation network
- **Bridge Inspection Reports** - Infrastructure condition
- **Water System Reports** - Utility infrastructure
- **Public Works Project Lists** - Municipal services

#### 4. Transit Data (8 files) - MOBILITY INSIGHTS
- **Metro-North Ridership Reports** - Commuter patterns
- **Bus Route Performance Data** - Local transit analysis
- **Transit Development Plans** - Future improvements
- **Transportation Studies** - Planning documents

#### 5. Historical Trends (15 files) - TIME SERIES ANALYSIS
- **Economic Indicators** - Business climate metrics
- **Population Growth Data** - Demographic changes
- **Housing Market Reports** - Real estate trends
- **Employment Statistics** - Labor market analysis

---

## 🤖 Automation Implementation Plan

### Target Automation Rates:
- **PDF Extraction Automation**: 60% of files (42 documents)
- **Web Scraping**: 25% of files (17 documents)
- **Manual Data Entry**: 15% of files (11 documents)

### Scripts to Create (in Technical/scripts/):

#### 1. PDF Extraction Pipeline
```python
# Technical/scripts/pdf_extractor.py
"""
Automated PDF table extraction for Westchester documents.

Capabilities:
- Detect and extract tables from PDFs
- Handle multi-page tables
- Clean and normalize extracted data
- Validate data structure
- Export to standardized format
"""

Dependencies: tabula-py, pdfplumber, pandas, camelot
```

#### 2. Web Scraping Framework
```python
# Technical/scripts/westchester_scraper.py
"""
Westchester County website data scraper.

Target Sites:
- westchestergov.com (Budget Office)
- finance.westchestergov.com (Tax data)
- westchestergov.com/transportation (Transit data)
- planning.westchestergov.com (Planning documents)

Features:
- Rate limiting and respectful scraping
- PDF download and processing
- Data structure normalization
- Error handling and retries
"""

Dependencies: requests, beautifulsoup4, selenium, pandas
```

#### 3. Data Validation System
```python
# Technical/scripts/data_validator.py
"""
Validate extracted Westchester data against expected patterns.

Validation Rules:
- Data type consistency
- Value range validation
- Format compliance
- Completeness checks
- Cross-source validation
"""

Dependencies: pandas, numpy, pytest
```

#### 4. Manual Data Entry Helper
```python
# Technical/scripts/manual_entry_helper.py
"""
Web interface for efficient manual data entry.

Features:
- Form pre-filling from partial extraction
- Data validation during entry
- Progress tracking
- Quality control checkpoints
"""

Dependencies: streamlit, pandas, pydantic
```

---

## 📅 Implementation Timeline

### Week 1: Foundation (Oct 14-20)
**Objective**: Set up automation infrastructure

**Tasks**:
- [ ] Create PDF extraction pipeline (pdf_extractor.py)
- [ ] Build web scraping framework (westchester_scraper.py)
- [ ] Implement data validation system (data_validator.py)
- [ ] Test automation on 5 high-priority documents
- [ ] Document extraction patterns and success rates

**Expected Output**: Automation tools ready for 60% of documents

### Week 2: Budget & Tax Data (Oct 21-27)
**Objective**: Complete core financial data integration

**Tasks**:
- [ ] Process all Budget PDFs (15 files)
- [ ] Extract Tax Levy Reports (12 files)
- [ ] Integrate data into FastAPI backend
- [ ] Update frontend dashboards with real financial data
- [ ] Validate data accuracy and completeness
- [ ] Create data export functionality

**Expected Output**: Budget and Tax dashboards fully functional with real data

### Week 3: Infrastructure & Transit (Oct 28 - Nov 3)
**Objective**: Complete transportation and infrastructure data

**Tasks**:
- [ ] Extract Infrastructure data (20 files)
- [ ] Process Transit reports (8 files)
- [ ] Update geographic visualizations
- [ ] Implement map-based infrastructure analysis
- [ ] Create transit ridership trend analysis
- [ ] Test all data integrations

**Expected Output**: Infrastructure and Transit dashboards complete

### Week 4: Historical Data & Production Deployment (Nov 4-10)
**Objective**: Final data integration and go-live

**Tasks**:
- [ ] Process Historical Trend documents (15 files)
- [ ] Complete all data validations
- [ ] Deploy frontend to Netlify
- [ ] Deploy backend to Render.com
- [ ] Configure domain and monitoring
- [ ] Conduct final testing and validation
- [ ] Create production documentation

**Expected Output**: Fully deployed production platform

---

## 🚀 Production Deployment Strategy

### Frontend Deployment (Netlify)
```bash
# Build for production
cd frontend
npm run build

# Deploy to Netlify
# 1. Connect GitHub repository to Netlify
# 2. Set build command: npm run build
# 3. Set publish directory: frontend/dist
# 4. Configure environment variables:
#    - VITE_API_URL: https://westchester-api.onrender.com
#    - VITE_APP_TITLE: Westchester County Data Platform
```

### Backend Deployment (Render.com)
```bash
# Deploy to Render
# 1. Connect GitHub repository to Render
# 2. Set build command: pip install -r requirements.txt
# 3. Set start command: uvicorn main:app --host 0.0.0.0 --port $PORT
# 4. Configure environment variables:
#    - ENVIRONMENT: production
#    - DEBUG: false
#    - CORS_ORIGINS: ["https://westchester-data.netlify.app"]
```

### Domain Configuration (Namecheap)
```
# DNS Settings
CNAME: westchester → westchester-data.netlify.app
CNAME: api → westchester-api.onrender.com
```

### Monitoring & Error Tracking
- **Uptime monitoring**: UptimeRobot (FREE)
- **Error tracking**: Sentry (FREE tier available)
- **Performance monitoring**: Render.com built-in metrics
- **Analytics**: Google Analytics or Plausible (privacy-friendly)

---

## 🔧 Enhancement Opportunities (Post-Completion)

### 1. Predictive Analytics Module
```python
# Features to add:
- Infrastructure maintenance predictions
- Budget trend forecasting
- Population growth projections
- Transit ridership modeling
```

### 2. Alert System
```typescript
// Features to implement:
- Budget variance alerts
- Infrastructure condition warnings
- Unusual demographic change notifications
- Data quality issue alerts
```

### 3. Advanced Data Export
```python
# Export formats to add:
- Custom Excel reports with charts
- PDF reports with executive summaries
- GIS data exports for mapping
- API data access for developers
```

### 4. User Interaction Features
```typescript
// UX improvements:
- Personalized dashboards
- Data bookmarking and sharing
- Interactive scenario modeling
- Mobile app version
```

---

## 📊 Success Metrics for Completion

### Functional Requirements (Must Have)
- [ ] All 70 data files processed and integrated
- [ ] Real data displayed in all dashboards (no sample data)
- [ ] PDF extraction automation working for 60% of files
- [ ] All exports working (Excel, PDF, CSV)
- [ ] Mobile responsive design verified
- [ ] Production deployment successful

### Quality Requirements (Druck Standards)
- [ ] All Excel files have ONE sheet each
- [ ] All final reports in LaTeX format in Output/PDFs/
- [ ] Fresh environment test passed
- [ ] Hyper-detailed progress logging maintained
- [ ] Complete HANDOFF_DOCUMENTATION.md
- [ ] Evidence-based completion rating (>85%)

### Performance Requirements
- [ ] Page load time < 3 seconds
- [ ] All API responses < 1 second
- [ ] Mobile performance acceptable
- [ ] Error rate < 1%
- [ ] Uptime > 99%

---

## 🚨 Critical Warnings (What NOT to Do)

### Data Processing
- ❌ NEVER interpolate data without explicit permission
- ❌ NEVER make assumptions about missing data
- ❌ NEVER modify original source data
- ❌ NEVER skip data validation steps

### Technical Implementation
- ❌ NEVER use sample data in production
- ❌ NEVER deploy without fresh environment testing
- ❌ NEVER skip mobile responsiveness testing
- ❌ NEVER ignore performance optimization

### Documentation
- ❌ NEVER claim completion without evidence
- ❌ NEVER create multi-sheet Excel files
- ❌ NEVER skip progress logging
- ❌ NEVER forget rollback plans

---

## 📞 Escalation Triggers

Contact Nick immediately if:

### Data Issues
- **PDF extraction success rate < 40%** - Automation not working
- **Critical data files not found** - Sources may have changed
- **Data quality problems detected** - Validation failures

### Technical Issues
- **Performance benchmarks not met** - Load times > 3 seconds
- **Deployment problems** - Cannot deploy to production
- **Integration failures** - Frontend/backend communication issues

### Timeline Issues
- **Week delays projected** - Timeline slipping significantly
- **Resource needs identified** - Additional tools/services required
- **Requirements clarification needed** - Unclear specifications

---

## 🎯 Immediate Action Items (This Week)

### Today (Oct 14)
- [ ] Create PDF extraction pipeline (pdf_extractor.py)
- [ ] Set up web scraping framework (westchester_scraper.py)
- [ ] Test automation on 2-3 budget documents

### Tomorrow (Oct 15)
- [ ] Implement data validation system (data_validator.py)
- [ ] Create manual data entry interface (manual_entry_helper.py)
- [ ] Document extraction patterns and success rates

### This Week
- [ ] Process 5 high-priority budget documents
- [ ] Integrate extracted data into backend
- [ ] Update frontend dashboards with new data
- [ ] Validate data accuracy and completeness

---

## 📈 Progress Tracking Template

### Daily Progress Log
```markdown
## YYYY-MM-DD - Westchester Data Collection

### Files Processed Today
- [x] [Document Name] - Extraction method, success rate, issues
- [x] [Document Name] - Extraction method, success rate, issues

### Automation Progress
- **PDF Extraction**: X/42 files automated (Y% success rate)
- **Web Scraping**: X/17 files automated (Y% success rate)
- **Manual Entry**: X/11 files completed

### Issues Encountered
- **Issue**: [Description]
- **Impact**: [How it affects progress]
- **Solution**: [How to resolve]

### Tomorrow's Priorities
1. [Most important task]
2. [Second priority]
3. [Backup task if blocked]

### Time Tracking
- **Total Time**: X hours
- **Automation Development**: Y hours
- **Data Processing**: Z hours
```

---

## ✅ Completion Validation Checklist

### Before Production Deployment
- [ ] All 70 data files processed and validated
- [ ] All dashboards showing real data (no sample data)
- [ ] All export formats working (Excel, PDF, CSV)
- [ ] Mobile responsive design tested and verified
- [ ] Performance benchmarks met (< 3 second load)
- [ ] Error handling comprehensive and tested
- [ ] Security vulnerabilities scanned and resolved
- [ ] Browser compatibility tested (Chrome, Firefox, Safari, Edge)
- [ ] Accessibility compliance verified (WCAG 2.1 AA)

### Druck Standards Compliance
- [ ] All Excel files have ONE sheet each
- [ ] All final reports in LaTeX format in Output/PDFs/
- [ ] Fresh environment test passed successfully
- [ ] Complete HANDOFF_DOCUMENTATION.md with all sections
- [ ] Evidence-based completion rating calculated and justified
- [ ] Hyper-detailed progress logging maintained throughout
- [ ] All decisions documented with rationale and rollback plans

---

*Following these next steps will complete the Westchester project to production standards while maintaining Druck quality requirements.*
*Evidence-based timeline based on 70% current completion and proven automation strategies.*

---

*Following these standards ensures high-quality deliverables and smooth agent handoffs.*
*Evidence-based patterns from 18+ successful Arcanum projects.*

