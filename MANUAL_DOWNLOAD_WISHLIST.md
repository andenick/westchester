# Manual Download Wishlist - Westchester County Real Data

## Purpose
This document lists all PDF and online data sources that require manual download or agent assistance to replace sample data in the Westchester County Data Platform.

**Download Location**: `Projects/Westchester/Technical/data/raw/manual_downloads/`

**Priority**: HIGH - Required to eliminate all sample data from website

---

## 1. Westchester County Budget Documents (HIGHEST PRIORITY)

### Adopted Operating Budgets (2020-2025)

**Source**: Westchester County Department of Budget  
**URL**: https://www.westchestergov.com/county-budgets

#### Files Needed:
- [ ] **2025 Adopted Operating Budget**
  - URL: https://www.westchestergov.com/images/stories/budget/2025/2025_Adopted_Operating_Budget.pdf
  - Save as: `westchester_county_2025_adopted_operating_budget.pdf`
  - Extract: Total budget, department allocations, planning department budget

- [ ] **2024 Adopted Operating Budget**
  - URL: https://www.westchestergov.com/images/stories/budget/2024/2024_Adopted_Operating_Budget.pdf
  - Save as: `westchester_county_2024_adopted_operating_budget.pdf`

- [ ] **2023 Adopted Operating Budget**
  - URL: https://www.westchestergov.com/images/stories/budget/2023/2023_Adopted_Operating_Budget.pdf
  - Save as: `westchester_county_2023_adopted_operating_budget.pdf`

- [ ] **2022 Adopted Operating Budget**
  - URL: https://www.westchestergov.com/images/stories/budget/2022/2022_Adopted_Operating_Budget.pdf
  - Save as: `westchester_county_2022_adopted_operating_budget.pdf`

- [ ] **2021 Adopted Operating Budget**
  - URL: https://www.westchestergov.com/images/stories/budget/2021/2021_Adopted_Operating_Budget.pdf
  - Save as: `westchester_county_2021_adopted_operating_budget.pdf`

- [ ] **2020 Adopted Operating Budget**
  - URL: https://www.westchestergov.com/images/stories/budget/2020/2020_Adopted_Operating_Budget.pdf
  - Save as: `westchester_county_2020_adopted_operating_budget.pdf`

#### Data to Extract:
- Total operating budget by year
- Department budget allocations:
  - Education
  - Public Safety  
  - Health & Human Services
  - Public Works
  - Parks & Recreation
  - **Planning Department** (CRITICAL for user requirement)
  - Administration
  - Other departments
- Year-over-year growth rates
- Per capita spending

---

## 2. Annual Comprehensive Financial Reports (ACFRs)

**Source**: Westchester County Department of Finance  
**URL**: https://finance.westchestergov.com/?id=136&view=category

#### Files Needed:
- [ ] **2024 ACFR** (if available)
- [ ] **2023 ACFR**
- [ ] **2022 ACFR**
- [ ] **2021 ACFR**
- [ ] **2020 ACFR**
- [ ] **2019 ACFR**
- [ ] **2018 ACFR**
- [ ] **2017 ACFR**
- [ ] **2016 ACFR**
- [ ] **2015 ACFR**

**Save as**: `westchester_county_[year]_acfr.pdf`

#### Data to Extract:
- Historical expenditure trends
- Function-based expenditure breakdown
- Planning and development spending details
- Capital project spending
- Debt service information

---

## 3. Property Tax Data

### A. NY State Office of Real Property Tax Services - Municipal Profiles

**Source**: NY State Tax Department  
**URL**: https://www.tax.ny.gov/research/property/reports.htm

#### Files Needed (45 municipalities):

**Cities:**
- [ ] Yonkers municipal profile (2015-2024)
- [ ] New Rochelle municipal profile (2015-2024)
- [ ] Mount Vernon municipal profile (2015-2024)
- [ ] White Plains municipal profile (2015-2024)
- [ ] Rye municipal profile (2015-2024)
- [ ] Peekskill municipal profile (2015-2024)

**Major Towns/Villages:**
- [ ] Scarsdale municipal profile (2015-2024)
- [ ] Port Chester municipal profile (2015-2024)
- [ ] Harrison municipal profile (2015-2024)
- [ ] Mamaroneck municipal profile (2015-2024)
- [ ] Greenburgh municipal profile (2015-2024)
- [ ] Bronxville municipal profile (2015-2024)
- [ ] Tarrytown municipal profile (2015-2024)
- [ ] Sleepy Hollow municipal profile (2015-2024)
- [ ] Dobbs Ferry municipal profile (2015-2024)
- [ ] Hastings-on-Hudson municipal profile (2015-2024)
- [ ] Irvington municipal profile (2015-2024)
- [ ] Ardsley municipal profile (2015-2024)
- [ ] Elmsford municipal profile (2015-2024)
- [ ] Tuckahoe municipal profile (2015-2024)
- [ ] Pelham municipal profile (2015-2024)
- [ ] Larchmont municipal profile (2015-2024)
- [ ] Rye Brook municipal profile (2015-2024)
- [ ] Croton-on-Hudson municipal profile (2015-2024)
- [ ] Briarcliff Manor municipal profile (2015-2024)
- [ ] Buchanan municipal profile (2015-2024)
- [ ] Ossining municipal profile (2015-2024)
- [ ] Cortlandt municipal profile (2015-2024)
- [ ] Yorktown municipal profile (2015-2024)
- [ ] Somers municipal profile (2015-2024)
- [ ] North Salem municipal profile (2015-2024)
- [ ] Lewisboro municipal profile (2015-2024)
- [ ] Pound Ridge municipal profile (2015-2024)
- [ ] Bedford municipal profile (2015-2024)
- [ ] Mount Pleasant municipal profile (2015-2024)
- [ ] New Castle municipal profile (2015-2024)
- [ ] North Castle municipal profile (2015-2024)
- [ ] Pelham Manor municipal profile (2015-2024)

**Save as**: `nys_tax_[municipality_name]_[year]_profile.pdf`

#### Data to Extract:
- Effective tax rate per municipality
- Tax levy amounts
- Assessed valuations
- Equalization rates
- Historical trends (1990-2024 if available)

### B. Westchester County GIS - Property Tax Parcels

**Already Have**: `WCGIS.tax-parcels.csv` and `WCGIS.tax-parcels.geojson`

**Action**: Parse existing file to extract:
- Total parcel count
- Average assessment by municipality
- Median assessment by municipality
- Assessment distribution

---

## 4. Westchester County Databook

**Source**: Westchester County Planning Department  
**URL**: https://planning.westchestergov.com/census-and-statistics/databook

#### Files Needed:
- [ ] **Latest Westchester County Databook (2024 or 2023 edition)**
  - Comprehensive county statistics
  - Demographics, economics, housing
  - Business and employment data
  
**Save as**: `westchester_county_databook_[year].pdf`

#### Data to Extract:
- Key county statistics
- Historical demographic trends
- Economic indicators
- Housing market data

---

## 5. School District Budget Data (For Education Spending)

**Source**: Westchester Index or individual school districts  
**URL**: https://www.westchesterindex.org/education/per-student-spending

#### Files Needed:
- [ ] **Per-student spending data**
- [ ] **Total school expenditures by district**
- [ ] **School budget historical trends**

**Save as**: `westchester_school_spending_[year].csv` or `.pdf`

---

## 6. Municipal Service Data

### Police Departments
- [ ] **List of all police departments in Westchester County**
- [ ] **Station locations (if not available from OSM)**
- **Source**: County emergency services directory

### Fire Districts
- [ ] **List of all fire districts and departments**
- [ ] **Station locations**
- **Source**: Westchester County Fire Coordinator

### Libraries
- [ ] **Complete library system inventory**
- [ ] **Branch locations and hours**
- **Source**: Westchester Library System

---

## Download Instructions for Agent

### Step 1: Create Directory
```bash
mkdir -p Projects/Westchester/Technical/data/raw/manual_downloads
cd Projects/Westchester/Technical/data/raw/manual_downloads
```

### Step 2: Download Priority Order

1. **FIRST**: Budget PDFs (2020-2025) - 6 files
2. **SECOND**: ACFR reports (2020-2024) - 5 files  
3. **THIRD**: Tax municipal profiles (top 10 municipalities) - 50 files
4. **FOURTH**: County Databook - 1 file
5. **FIFTH**: School spending data - varies

### Step 3: Verification

After download, verify:
- All PDFs are readable
- File sizes are reasonable (not error pages)
- Years match filenames
- Total file count matches checklist

### Step 4: Notify for Processing

Once downloaded, notify user so we can create:
- PDF extraction scripts
- Data consolidation scripts
- Time series generation
- Dashboard integration

---

## Alternative: Web Scraping Approach (If PDFs Not Accessible)

If direct PDF downloads fail, we can:

1. **Budget Data**: Scrape from https://www.westchestergov.com/county-budgets
2. **Tax Data**: Scrape from municipality websites
3. **Financial Data**: Request via FOIL (Freedom of Information Law)

---

## Expected Deliverables

After manual downloads are complete:

1. **Budget Time Series (2015-2025)**
   - JSON file with year-by-year totals
   - Department breakdowns
   - Planning department percentages

2. **Tax Rate Database (1990-2024)**
   - CSV with municipality, year, rate, levy
   - Historical trends

3. **Service Inventory**
   - Police departments: 42+
   - Fire districts: 58+
   - Libraries: 38+
   - Parks: From OSM (already have)

---

## Current Status

- [ ] Budget PDFs: **NOT DOWNLOADED** - Need agent assistance
- [ ] ACFR reports: **NOT DOWNLOADED** - Need agent assistance
- [ ] Tax profiles: **NOT DOWNLOADED** - Need agent assistance
- [ ] County Databook: **NOT DOWNLOADED** - Need agent assistance
- [ ] School data: **NOT DOWNLOADED** - Need agent assistance

**Next Action**: Assign to agent or begin manual download process

---

## Notes

- All downloaded files should be stored in `manual_downloads/` subdirectory
- After download, create extraction scripts for each document type
- Prioritize most recent 5 years for immediate use
- Historical data (1990-2019) can be added in phase 2
- Some data may only be available through FOIL requests

**Created**: 2025-10-14  
**Last Updated**: 2025-10-14  
**Status**: PENDING DOWNLOAD

