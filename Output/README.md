# Westchester County Data Platform - User Guide

## What This Delivers

A comprehensive data platform providing demographic, economic, transit, and geographic analysis for Westchester County, NY. Access evidence-based insights through professional reports and machine-readable datasets for county planning, research, and decision-making.

**Key Features**:
- **Demographics**: Population, age, income, housing data at county, municipality, and census tract levels
- **Transit Analysis**: GTFS-based public transportation data and accessibility metrics
- **Geographic Data**: Interactive maps and spatial analysis
- **Economic Indicators**: Employment, business, and economic development data
- **Municipal Comparisons**: Side-by-side analysis across Westchester's cities, towns, and villages

## Quick Start

### For Report Readers
1. **Navigate to `PDFs/` directory** for professional LaTeX-generated reports:
   - `westchester_methodology_report.pdf` - Understand data sources and technical approach
   - `westchester_analysis_report.pdf` - Detailed findings with visualizations
   - `westchester_executive_summary.pdf` - High-level overview for stakeholders
   - `westchester_reporting_strategy.pdf` - Complete catalog of deliverables

2. **Review key findings** in the executive summary (typically 5-10 pages)

3. **Dive deeper** into specific topics using the analysis report

### For Data Users
1. **Navigate to `Data/` directory** for Excel datasets
   - Each file contains **ONE sheet** (Druck standard for machine readability)
   - Files organized by source and theme
   - Machine-readable column names compatible with R, Python, Excel

2. **Key Dataset Categories**:
   - `Data/Robin/` - Integration with Robin master database
   - `Data/Source/` - Original data from Census, GTFS, NY State
   - `Data/Results/` - Processed analysis outputs

3. **Open in your tool of choice**:
   - Microsoft Excel or LibreOffice Calc
   - R: `read.xlsx()` or `readxl` package
   - Python: `pandas.read_excel()`
   - Statistical packages: SPSS, Stata, SAS

## Key Files

### Professional Reports (PDFs)
| File | Purpose | Audience | Pages |
|------|---------|----------|-------|
| `westchester_methodology_report.pdf` | Technical foundation, data sources, processing methodology | Technical users, researchers | 15-25 |
| `westchester_analysis_report.pdf` | Detailed findings with charts, maps, statistical analysis | Analysts, planners | 30-50 |
| `westchester_executive_summary.pdf` | Key findings and recommendations | Decision-makers, stakeholders | 5-10 |
| `westchester_reporting_strategy.pdf` | Complete output catalog and usage guide | All users | 10-15 |

### Data Files (Excel - ONE SHEET each)
**Demographic Data**:
- `westchester_county_demographics_[year].xlsx` - County-level population, age, income, housing
- `westchester_municipalities_demographics_[year].xlsx` - Municipality-level breakdowns
- `westchester_census_tracts_demographics_[year].xlsx` - Fine-grained tract-level data

**Transit Data**:
- `westchester_transit_stations.xlsx` - Metro-North and bus stops with locations
- `westchester_transit_routes.xlsx` - Service routes and schedules
- `westchester_transit_accessibility.xlsx` - Coverage and access metrics

**Geographic Data**:
- `westchester_municipal_boundaries.xlsx` - Administrative boundaries with coordinates
- `westchester_points_of_interest.xlsx` - Key locations (government, services, etc.)

**Economic Data**:
- `westchester_employment_data_[year].xlsx` - Employment by sector and location
- `westchester_business_statistics_[year].xlsx` - Business counts, types, sizes

*(Note: Specific files created as data processing progresses)*

## Requirements

### To Read PDF Reports
- **PDF Reader**: Adobe Acrobat Reader, browser PDF viewer, or equivalent
- **No special software required** - reports are self-contained

### To Use Excel Data
**Option 1: Microsoft Excel** (Recommended for most users)
- Excel 2016 or later
- Windows or Mac version

**Option 2: Free Alternatives**
- LibreOffice Calc (free, open source)
- Google Sheets (web-based, upload files)

**Option 3: Programming Languages**
- **Python**: `pandas`, `openpyxl` libraries
  ```python
  import pandas as pd
  df = pd.read_excel('westchester_county_demographics_2022.xlsx')
  ```
- **R**: `readxl` or `openxlsx` package
  ```r
  library(readxl)
  data <- read_excel("westchester_county_demographics_2022.xlsx")
  ```

### System Requirements
- **Storage**: ~500 MB for all datasets and reports
- **Internet**: Not required for viewing offline files
- **Operating System**: Any (Windows, Mac, Linux)

## Data Standards

All datasets follow these quality standards:

✅ **ONE SHEET PER FILE** - Easy to import, no tab navigation needed
✅ **Machine-Readable Columns** - Compatible with all statistical programs
✅ **Professional Formatting** - Clean, black and white, publication-ready
✅ **Consistent Structure** - Predictable column order and naming
✅ **Documented Sources** - Data provenance noted in reports
✅ **Date-Stamped** - Version control through filename dates

## Understanding the Data

### Data Sources
1. **US Census Bureau**: American Community Survey (ACS), Decennial Census
2. **GTFS Transit Feeds**: Metro-North Railroad, Bee-Line Bus System
3. **NY State Open Data**: Economic, environmental, administrative data
4. **Robin Database**: Integrated Arcanum data repository

### Update Frequency
- **Census Data**: Annual (ACS 1-year and 5-year estimates)
- **Transit Data**: Quarterly or as schedules change
- **Economic Data**: Varies by indicator (monthly to annual)

### Geographic Levels
Data available at multiple resolutions:
- **County**: Westchester County aggregate
- **Municipality**: 6 cities, 19 towns, 23 villages
- **Census Tract**: ~240 tracts for fine-grained analysis
- **Block Group**: Selected demographics at smallest Census unit

## Common Use Cases

### For County Planners
- Compare municipal demographics for resource allocation
- Analyze transit coverage and identify gaps
- Track population trends for infrastructure planning

### For Researchers
- Academic research on suburban development
- Demographic and economic analysis
- Transportation and accessibility studies

### For Policy Makers
- Evidence-based decision making
- Constituent demographic profiles
- Impact assessment for policy proposals

### For Developers & Consultants
- Market analysis for development projects
- Site selection using multiple criteria
- Demographic profiling for business planning

## Support

### For Questions About Data
- **Review methodology report** first for data source details
- **Check reporting strategy** for complete output catalog
- **Contact**: Reference `../HANDOFF_DOCUMENTATION.md` for project status

### For Technical Issues
- **Excel won't open**: Ensure you have Excel 2016+ or LibreOffice Calc
- **PDF won't display**: Try alternate PDF reader (Adobe Acrobat Reader recommended)
- **File format questions**: See methodology report for dataset specifications

### For Development/Customization
- **Technical documentation**: `../Technical/README.md`
- **Source code**: `../Technical/src/`
- **Developer setup**: `../PROJECT_INDEX.md`

## Citation

When using this data in publications or presentations:

**Suggested Citation**:
> Westchester County Data Platform. (2025). [Dataset/Report Name]. Arcanum Projects. Retrieved from [Date].

**Data Source Attribution**:
Please cite original sources as documented in the methodology report:
- US Census Bureau (demographic data)
- GTFS transit operators (transportation data)
- NY State Open Data Portal (state datasets)

## Version History

- **Current Version**: In Development (as of 2025-10-12)
- **Data Vintage**: 2020-2024 (varies by source)
- **Last Updated**: 2025-10-12

---

*This platform follows Druck standards for professional data delivery.*
*All Excel files contain ONE sheet per file for maximum compatibility.*
*Reports generated using LaTeX for publication-quality output.*