# Manual Data Import Guide

**Westchester County Data Platform**  
**Last Updated:** October 13, 2025

---

## Overview

This guide provides step-by-step instructions for manually importing data sources that cannot be automatically downloaded via API. Follow these procedures to maintain data quality and consistency.

---

## Table of Contents

1. [School Directory Data](#1-school-directory-data)
2. [EPA Air Quality Data](#2-epa-air-quality-data)
3. [Westchester County Building Permits](#3-westchester-county-building-permits)
4. [NCES School Performance Data](#4-nces-school-performance-data)
5. [Additional Census Data](#5-additional-census-data)

---

## 1. School Directory Data

### Data Source
- **Source:** New York State Education Department
- **Website:** https://data.nysed.gov/
- **Alternative:** https://data.ny.gov/ (search "school directory")

### Manual Download Steps

#### Option A: NY State Open Data Portal
1. Navigate to https://data.ny.gov/
2. Search for "School Directory"
3. Look for dataset "School Directory"
4. Click "Export" → "CSV" or "JSON"
5. Filter results:
   - Column: "County"
   - Value: "Westchester"
6. Download filtered data

#### Option B: NYSED Direct Download
1. Go to https://data.nysed.gov/downloads.php
2. Select "Institutional Data"
3. Choose "Public School Enrollment"
4. Select most recent year
5. Download CSV file
6. Open in spreadsheet software
7. Filter for County = "Westchester"
8. Export filtered data

### File Placement
```
Technical/data/raw/schools/
├── westchester_schools.csv          # Manual download
├── westchester_schools.json         # Optional: convert CSV to JSON
└── westchester_schools.geojson      # Optional: add coordinates
```

### Data Validation
After importing, verify:
- [ ] County field contains "Westchester"
- [ ] School names are present
- [ ] Addresses are complete
- [ ] Grade levels are specified
- [ ] File contains 50-150 schools (expected range)

---

## 2. EPA Air Quality Data

### Data Source
- **Source:** U.S. Environmental Protection Agency
- **Website:** https://www.epa.gov/outdoor-air-quality-data
- **API:** https://aqs.epa.gov/data/api (requires registration)

### Manual Download Steps

#### Step 1: Register for API Access
1. Visit https://aqs.epa.gov/data/api/signup
2. Complete registration form
3. Receive API key via email (may take 1-2 business days)
4. Store API key in Robin: `Council/Robin/ADMIN/api-keys/[2025.09.28] api_keys.json`

#### Step 2: Download Data via Web Interface
If API is not working:
1. Go to https://www.epa.gov/outdoor-air-quality-data/download-daily-data
2. Select criteria:
   - **Pollutant:** PM2.5, Ozone (select all relevant)
   - **Year:** Most recent available
   - **Geographic Area:** New York → Westchester County
3. Click "Get Data"
4. Download CSV file

#### Step 3: Process Downloaded Data
1. Open CSV in text editor or spreadsheet
2. Verify columns include:
   - Monitor ID / Site ID
   - Latitude / Longitude
   - Parameter (pollutant type)
   - Date
   - AQI Value
3. Save to appropriate location

### File Placement
```
Technical/data/raw/environmental/
├── westchester_air_quality_monitors.csv    # Station locations
├── westchester_air_quality_daily.csv       # Daily readings
└── westchester_air_quality_metadata.json   # API metadata
```

### Data Processing
After download, run:
```bash
python Technical/src/processors/process_environmental.py
```

---

## 3. Westchester County Building Permits

### Data Source
- **Source:** Westchester County Open Data Portal
- **Website:** TBD (check county website)
- **Alternative:** Individual municipality building departments

### Manual Download Steps

#### Step 1: Locate Data Portal
1. Visit https://westchestergov.com/ or https://giswww.westchestergov.com/
2. Look for "Open Data" or "GIS Data" section
3. Search for "Building Permits" or "Construction Permits"

#### Step 2: Download Options
**If portal exists:**
1. Navigate to building permits dataset
2. Apply filters:
   - Date range: Last 12 months (or specify range)
   - Status: All or Active only
3. Export as CSV or Excel
4. Download file

**If no portal (municipal approach):**
1. Contact individual town/city building departments
2. Request public records for building permits
3. Compile data from multiple sources
4. Standardize format

### File Placement
```
Technical/data/raw/permits/
├── westchester_building_permits.csv
├── westchester_building_permits.json
└── permits_metadata.json
```

### Expected Data Fields
- Permit Number
- Issue Date
- Address / Parcel ID
- Permit Type (residential, commercial, etc.)
- Construction Value
- Contractor Information
- Status (issued, approved, completed)

---

## 4. NCES School Performance Data

### Data Source
- **Source:** National Center for Education Statistics
- **Website:** https://nces.ed.gov/ccd/
- **Data Tool:** https://nces.ed.gov/ccd/elsi/

### Manual Download Steps

#### Using ELSI (Elementary/Secondary Information System)
1. Go to https://nces.ed.gov/ccd/elsi/
2. Select "Build a Table"
3. Configure query:
   - **Year:** Most recent
   - **Geography:** New York → Westchester County
   - **School Level:** All
4. Select variables:
   - Enrollment by grade
   - Student demographics
   - Free/reduced lunch eligibility
   - Teacher-student ratio
5. Click "View Table"
6. Export as CSV or Excel

#### Alternative: Direct Download
1. Visit https://nces.ed.gov/ccd/files.asp
2. Download "Public School Universe" file for New York
3. Filter for Westchester County (County FIPS: 36119)
4. Extract relevant fields

### File Placement
```
Technical/data/raw/schools/
├── westchester_school_performance.csv
├── westchester_school_enrollment.csv
└── school_performance_metadata.json
```

---

## 5. Additional Census Data

### Data Source
- **Source:** U.S. Census Bureau
- **Website:** https://data.census.gov/

### Manual Download Steps

#### For Specific Census Tables Not in API
1. Navigate to https://data.census.gov/
2. Use Advanced Search
3. Select filters:
   - **Geography:** Westchester County, NY (or Census Tracts in Westchester)
   - **Survey:** ACS 5-Year Estimates
   - **Year:** 2022 (most recent)
   - **Topics:** Select specific table (e.g., B19001 - Income distribution)
4. Click "Download"
5. Choose format: CSV (recommended)
6. Download and extract ZIP file

#### Specific Useful Tables
- **B19001** - Household Income Distribution
- **B25024** - Units in Structure (housing types)
- **B08301** - Means of Transportation to Work (detailed)
- **B15002** - Educational Attainment (detailed)

### File Placement
```
Technical/data/raw/demographics/additional/
├── westchester_income_distribution.csv
├── westchester_housing_types.csv
└── westchester_commute_detailed.csv
```

---

## General Import Procedures

### 1. File Naming Convention
All manually imported files should follow:
```
westchester_[category]_[subcategory].csv
```

Examples:
- `westchester_schools_directory.csv`
- `westchester_permits_building.csv`
- `westchester_air_quality_monitors.csv`

### 2. Required Metadata
For each manual import, create a metadata JSON file:

```json
{
  "source": "Official Source Name",
  "source_url": "https://...",
  "download_date": "2025-10-13",
  "downloaded_by": "User Name",
  "data_year": 2024,
  "record_count": 150,
  "county": "Westchester",
  "notes": "Any important notes about the data",
  "manual_steps_required": true
}
```

### 3. Data Validation Checklist
Before finalizing any manual import:

- [ ] File is in correct format (CSV, JSON, or GeoJSON)
- [ ] Column headers are present and clear
- [ ] No obvious data corruption or encoding issues
- [ ] Geographic data (if any) is within Westchester County bounds
- [ ] Dates are in consistent format (YYYY-MM-DD preferred)
- [ ] Metadata file created and complete
- [ ] File placed in correct directory
- [ ] README updated in data directory

### 4. Coordinate Validation
For geographic data, verify coordinates are within Westchester:
- **Latitude:** 40.9° to 41.4° N
- **Longitude:** -74.0° to -73.5° W

### 5. Data Quality Checks
Run validation script after import:
```bash
python Technical/scripts/validate_manual_imports.py
```

---

## Post-Import Integration

### 1. Update Data Catalog
Edit `DATA_SOURCES_CATALOG.md` to include:
- New data source details
- Manual download procedures
- Update frequency
- Known limitations

### 2. Create Processing Script
If data needs processing:
1. Create processor in `Technical/src/processors/`
2. Follow existing patterns
3. Generate Druck-compliant Excel output

### 3. Update Backend API
Add new endpoints in `Technical/src/api/main.py` if needed:
```python
@app.get("/api/schools")
async def get_schools():
    # Load and return school data
    pass
```

### 4. Update Frontend
Add data visualization in appropriate dashboard:
- Schools → Education dashboard (create if needed)
- Air quality → Environmental dashboard
- Permits → Development dashboard

---

## Troubleshooting

### Common Issues

**Issue:** Downloaded file has wrong encoding
- **Solution:** Open in text editor, save as UTF-8

**Issue:** CSV has inconsistent delimiters
- **Solution:** Use `pandas.read_csv()` with `sep` parameter

**Issue:** Coordinates not in expected format
- **Solution:** Convert using:
  ```python
  lat, lon = convert_coordinates(original_format)
  ```

**Issue:** Data contains duplicate records
- **Solution:** Use `df.drop_duplicates()` before saving

---

## Contact for Assistance

**Data Issues:** Check `Technical/DEVELOPER_GUIDE.md`  
**API Problems:** Review `DATA_SOURCES_CATALOG.md`  
**Processing Questions:** See existing processors in `Technical/src/processors/`

---

## Update History

| Date | Dataset | Action | Notes |
|------|---------|--------|-------|
| 2025-10-13 | Initial guide | Created | Manual import procedures established |

---

**Maintained by:** Arcanum Research Initiative  
**Project:** Westchester County Data Platform

