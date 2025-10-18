# Westchester County Data Platform - Data Sources Catalog

**Last Updated:** October 13, 2025  
**Platform Version:** 1.0

---

## Overview

This document catalogs all data sources integrated into the Westchester County Data Platform, including URLs, access methods, update frequencies, quality assessments, and citation formats.

---

## Currently Integrated Data Sources

### 1. U.S. Census Bureau - American Community Survey (ACS)

**Source:** U.S. Census Bureau  
**Dataset:** ACS 5-Year Estimates (2022)  
**API Endpoint:** `https://api.census.gov/data/2022/acs/acs5`  
**Geographic Scope:** Westchester County, NY (FIPS: 36119)

**Data Files:**
- `westchester_county_demographics_2022.json/csv` - County-level demographics
- `westchester_tracts_demographics_2022.json/csv` - 241 census tracts
- `westchester_municipalities_demographics_2022.json/csv` - Municipality-level data

**Variables Collected:**
- Population (total, by age, by sex, by race/ethnicity)
- Housing (units, occupancy, values, rent)
- Income (median household, per capita, poverty)
- Employment (labor force, employed, unemployed)
- Education (bachelor's, master's, doctorate degrees)
- Commuting (mode, travel time)

**Update Frequency:** Annual (released ~December for prior year)  
**Access Method:** REST API (no key required, recommended for rate limits)  
**Data Quality:** ⭐⭐⭐⭐⭐ (Official government statistics)  
**Known Limitations:** 5-year estimates lag current year by 1-2 years

**Citation:**
```
U.S. Census Bureau. (2022). American Community Survey 5-Year Estimates. 
Retrieved from https://www.census.gov/programs-surveys/acs
```

---

### 2. Metro-North Railroad - GTFS Transit Feed

**Source:** Metropolitan Transportation Authority (MTA)  
**Dataset:** Metro-North Railroad GTFS (General Transit Feed Specification)  
**Download URL:** `http://web.mta.info/developers/data/mnr/google_transit.zip`  
**Geographic Scope:** Westchester County stations (56 stations)

**Data Files:**
- `westchester_metro_north_stations.json` - Station directory
- `westchester_metro_north_stations.geojson` - Geographic data
- `westchester_metro_north_metadata.json` - Dataset metadata
- `metro_north_gtfs.zip` - Full GTFS archive
- GTFS tables: stops, routes, trips, stop_times, agency

**Data Points:**
- Station names, IDs, and codes
- Geographic coordinates (lat/lon)
- Wheelchair accessibility
- Route information (Harlem, Hudson, New Haven lines)

**Update Frequency:** Monthly (or as schedules change)  
**Access Method:** Direct ZIP download  
**Data Quality:** ⭐⭐⭐⭐ (Official transit authority data)  
**Known Limitations:** Schedule data only; no real-time or ridership statistics

**Citation:**
```
Metropolitan Transportation Authority. (2025). Metro-North Railroad GTFS Feed. 
Retrieved from http://web.mta.info/developers/
```

---

### 3. NY State Open Data - Crime Statistics

**Source:** New York State Division of Criminal Justice Services  
**Dataset:** Index Crimes by County  
**API Endpoint:** `https://data.ny.gov/resource/ca8h-8gjq.json`  
**Platform:** Socrata Open Data  
**Geographic Scope:** Westchester County (1,611 records)

**Data Files:**
- `westchester_crime_data.json/csv` - Crime statistics

**Data Points:**
- Crime types and counts
- Annual statistics
- County-level aggregation

**Update Frequency:** Quarterly  
**Access Method:** Socrata API with app token  
**Data Quality:** ⭐⭐⭐⭐ (Official state data)  
**Known Limitations:** Aggregated at county level; no geographic coordinates

**Citation:**
```
New York State Division of Criminal Justice Services. (2025). 
Index Crimes by County. Retrieved from https://data.ny.gov/
```

---

### 4. NY State Open Data - Health Facilities

**Source:** New York State Department of Health  
**Dataset:** Health Facility General Information  
**API Endpoint:** `https://data.ny.gov/resource/vn5v-hh5r.json`  
**Platform:** Socrata Open Data  
**Geographic Scope:** Westchester County (330 facilities)

**Data Files:**
- `westchester_health_facilities.json/csv` - Licensed health facilities

**Data Points:**
- Facility names and types
- Addresses and locations
- License information
- Contact details

**Update Frequency:** Monthly  
**Access Method:** Socrata API with app token  
**Data Quality:** ⭐⭐⭐⭐ (Official state licensing data)  
**Known Limitations:** Some coordinate data may be incomplete

**Citation:**
```
New York State Department of Health. (2025). Health Facility General Information. 
Retrieved from https://data.ny.gov/
```

---

### 5. U.S. Census Bureau - TIGER/Line Shapefiles

**Source:** U.S. Census Bureau Geography Division  
**Dataset:** TIGER/Line Shapefiles - County Faces  
**Download:** Census FTP/Web Interface  
**Geographic Scope:** Westchester County (FIPS: 36119)

**Data Files:**
- `tl_2019_36119_faces.*` - County boundary faces shapefile

**Data Points:**
- Geographic boundaries
- Face IDs and coordinates
- Topological relationships

**Update Frequency:** Annual  
**Access Method:** Direct download  
**Data Quality:** ⭐⭐⭐⭐⭐ (Official Census geography)  
**Known Limitations:** 2019 vintage may not reflect recent boundary changes

**Citation:**
```
U.S. Census Bureau. (2019). TIGER/Line Shapefiles. 
Retrieved from https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html
```

---

### 6. Westchester County GIS - Tax Parcels

**Source:** Westchester County Geographic Information Systems  
**Dataset:** Tax Parcel Data  
**Download:** Westchester County Open Data Portal  
**Geographic Scope:** All county parcels (~350,000)

**Data Files:**
- `WCGIS.tax-parcels.csv` - Parcel attributes
- `WCGIS.tax-parcels.geojson` - Geographic parcels

**Data Points:**
- Parcel IDs and addresses
- Assessment values
- Property types
- Owner information
- Geographic boundaries

**Update Frequency:** Quarterly  
**Access Method:** Direct download from county portal  
**Data Quality:** ⭐⭐⭐⭐ (Official county assessment data)  
**Known Limitations:** Large file size; requires processing for analysis

**Citation:**
```
Westchester County GIS. (2025). Tax Parcel Data. 
Retrieved from Westchester County Open Data Portal
```

---

## Recommended Additional Data Sources

### 7. NCES School Directory (TO BE INTEGRATED)

**Source:** National Center for Education Statistics  
**API:** https://nces.ed.gov/ccd/  
**Scope:** Public and private schools in Westchester County

**Potential Data:**
- School locations (lat/lon)
- Enrollment numbers
- School types and levels
- District information

---

### 8. EPA Air Quality (TO BE INTEGRATED)

**Source:** Environmental Protection Agency  
**API:** https://aqs.epa.gov/data/api  
**Scope:** Air quality monitoring stations in Westchester

**Potential Data:**
- Monitor locations
- Pollutant measurements (PM2.5, Ozone, etc.)
- Historical readings

---

### 9. OpenStreetMap (TO BE INTEGRATED)

**Source:** OpenStreetMap  
**API:** Overpass API  
**Scope:** Parks, amenities, infrastructure

**Potential Data:**
- Park boundaries
- Recreational facilities
- Bike paths and trails
- Points of interest

---

### 10. Westchester County - Building Permits (TO BE INTEGRATED)

**Source:** Westchester County Open Data  
**Scope:** Building permits and inspections

**Potential Data:**
- Permit types and dates
- Construction values
- Addresses and locations

---

## Data Quality Standards

**Quality Rating System:**
- ⭐⭐⭐⭐⭐ (5 stars): Official government source, regularly updated, complete
- ⭐⭐⭐⭐ (4 stars): Reliable source, mostly complete, minor limitations
- ⭐⭐⭐ (3 stars): Useful data, some gaps or outdated elements
- ⭐⭐ (2 stars): Limited reliability or significant gaps
- ⭐ (1 star): Use with caution, major quality concerns

**Validation Procedures:**
1. Coordinate verification (within Westchester bounds)
2. Date range validation
3. Completeness checks (non-null critical fields)
4. Cross-reference with official sources
5. Statistical outlier detection

---

## Data Update Schedule

| Data Source | Frequency | Last Updated | Next Update |
|-------------|-----------|--------------|-------------|
| Census ACS | Annual | 2022 | Dec 2025 |
| Metro-North GTFS | Monthly | Oct 2025 | Nov 2025 |
| NY Crime Data | Quarterly | Oct 2025 | Jan 2026 |
| NY Health Facilities | Monthly | Oct 2025 | Nov 2025 |
| Tax Parcels | Quarterly | Oct 2025 | Jan 2026 |

---

## API Access Information

### Census Bureau API
- **Endpoint:** `https://api.census.gov/data/`
- **Authentication:** None required (API key recommended)
- **Rate Limit:** 500 requests/day (unlimited with key)
- **Documentation:** https://www.census.gov/data/developers/guidance/api-user-guide.html

### NY State Open Data (Socrata)
- **Base URL:** `https://data.ny.gov/resource/`
- **Authentication:** App token (stored in Robin)
- **Rate Limit:** 1000 requests/day (with token)
- **Documentation:** https://dev.socrata.com/

### Metro-North GTFS
- **URL:** `http://web.mta.info/developers/data/mnr/google_transit.zip`
- **Authentication:** None
- **Update Check:** HTTP HEAD request for Last-Modified header
- **Documentation:** https://gtfs.org/

---

## Data Processing Notes

### Geographic Filtering
**Westchester County Bounds:**
- Latitude: 40.9° to 41.4° N
- Longitude: -74.0° to -73.5° W
- FIPS Code: 36119
- State FIPS: 36 (New York)

### Data Transformations
1. **Coordinate Systems:** All geographic data normalized to WGS84 (EPSG:4326)
2. **Date Formats:** ISO 8601 format (YYYY-MM-DD)
3. **Column Names:** Standardized to snake_case for machine readability
4. **Missing Values:** Coded as NULL in databases, empty in CSV, null in JSON

---

## Contact & Support

**Data Questions:** Review methodology report (`westchester_methodology_report.pdf`)  
**API Issues:** See API documentation links above  
**Platform Support:** See `USER_GUIDE.md` and `Technical/DEVELOPER_GUIDE.md`

---

**Maintained by:** Arcanum Research Initiative  
**Project:** Westchester County Data Platform  
**Version:** 1.0 (October 2025)

