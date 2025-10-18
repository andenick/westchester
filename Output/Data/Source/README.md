# Westchester County Data Sources

**Project**: Westchester County Data Platform  
**Created**: October 12, 2025  
**Last Updated**: October 12, 2025

---

## 📋 Overview

This document catalogs all data sources used in the Westchester County Data Platform, including access methods, data quality assessments, and update schedules.

---

## 🌐 Primary Data Sources

### 1. Westchester County Open Data Portal

**URL**: https://data.westchestergov.com/  
**Access**: Public API (Socrata platform)  
**API Format**: JSON, CSV, GeoJSON  
**Authentication**: None required for public datasets  
**Status**: 🔄 Researching available datasets

#### Available Datasets (To Be Cataloged)
- Property assessments
- County budget data
- Building permits
- Code violations
- GIS/mapping data
- Municipal boundaries

**Data Quality**: To be assessed  
**Update Frequency**: Varies by dataset  
**Last Accessed**: Not yet accessed

---

### 2. New York State Open Data

**URL**: https://data.ny.gov/  
**Access**: Public API (Socrata platform)  
**API Format**: JSON, CSV, GeoJSON  
**Authentication**: App token recommended (optional)  
**Status**: 🔄 Researching Westchester-specific datasets

#### Relevant Datasets
- Property tax data (Office of Real Property Tax Services)
- Crime statistics (Division of Criminal Justice Services)
- Environmental data (DEC)
- Health data (DOH)
- Education data (State Education Department)

**Data Quality**: High (official state data)  
**Update Frequency**: Varies by dataset  
**Last Accessed**: Not yet accessed

**API Documentation**: https://dev.socrata.com/

---

### 3. Metro-North Railroad (MTA)

**URL**: http://web.mta.info/developers/  
**Access**: Public GTFS feeds  
**Format**: GTFS (General Transit Feed Specification)  
**Authentication**: None required  
**Status**: ✅ Source identified

#### Data Available
- Station locations (with coordinates)
- Route information (Harlem, Hudson, New Haven lines)
- Schedule data (stops, times, trips)
- Real-time data (if available)

**GTFS Feed URL**: http://web.mta.info/developers/data/mnr/google_transit.zip  
**Data Quality**: High (official MTA data)  
**Update Frequency**: Static: occasional updates; Real-time: continuous  
**Coverage**: All Metro-North stations including 56+ in Westchester County

**Last Accessed**: Not yet accessed  
**GTFS Specification**: https://gtfs.org/reference/static/

---

### 4. U.S. Census Bureau

**URL**: https://www.census.gov/data/developers.html  
**Access**: Public API  
**API Format**: JSON  
**Authentication**: API key required (free)  
**Status**: ✅ API identified

#### Available Datasets
- **Decennial Census**: Population counts every 10 years
- **American Community Survey (ACS)**: Annual demographic estimates
  - 1-year estimates (for areas 65K+ population)
  - 5-year estimates (all areas)
- **Economic Census**: Business and economic data

#### Key Variables for Westchester
- **Population**: Total, by age, race, ethnicity
- **Housing**: Units, occupancy, value, costs
- **Income**: Household income, poverty rates
- **Employment**: Labor force, occupation, commuting
- **Education**: Educational attainment levels

**API Endpoint**: https://api.census.gov/data/  
**Documentation**: https://www.census.gov/data/developers/guidance.html  
**Data Quality**: Very high (official federal data)  
**Update Frequency**: Annual (ACS), decennial (Census)

**Geographic Filters**:
- State: 36 (New York)
- County: 119 (Westchester County)
- Place codes for municipalities
- Census tract and block group codes

**API Key**: Request at https://api.census.gov/data/key_signup.html  
**Last Accessed**: Not yet accessed

---

### 5. Westchester County GIS

**URL**: https://giswww.westchestergov.com/  
**Access**: Public download portal and WMS/WFS services  
**Format**: Shapefile, GeoJSON, KML  
**Authentication**: None for public data  
**Status**: 🔄 Researching available layers

#### Expected Datasets
- County boundary
- Municipality boundaries (cities, towns, villages)
- Census tracts and block groups
- Zoning districts
- Parks and recreation areas
- Roads and transportation infrastructure
- Water features
- Tax parcels (if publicly available)

**Data Quality**: High (official county GIS)  
**Update Frequency**: Varies by layer  
**Coordinate System**: Typically NAD83 / New York State Plane  
**Last Accessed**: Not yet accessed

---

## 🔍 Secondary Data Sources

### 6. OpenStreetMap

**URL**: https://www.openstreetmap.org/  
**Access**: Public API and data extracts  
**Format**: XML, PBF, GeoJSON  
**Use Case**: Supplementary geographic data (roads, buildings, POIs)  
**Status**: 📋 Optional/backup source

**Overpass API**: https://overpass-api.de/  
**Geofabrik Extracts**: https://download.geofabrik.de/north-america/us/new-york.html

---

### 7. National Elevation Dataset (USGS)

**URL**: https://www.usgs.gov/national-hydrography/national-elevation-dataset  
**Use Case**: Topographic data for Westchester County  
**Status**: 📋 Optional for advanced visualizations

---

### 8. EPA Environmental Data

**URL**: https://www.epa.gov/data  
**Datasets**: Air quality, water quality, brownfields  
**Status**: 📋 Optional/supplementary

---

## 📊 Data Collection Status

### High Priority (Phase 1-2)
| Source | Status | Priority | Downloaded |
|--------|--------|----------|------------|
| Metro-North GTFS | ✅ Identified | High | ❌ No |
| Westchester County GIS | 🔄 Researching | High | ❌ No |
| Census ACS (Westchester) | ✅ Identified | High | ❌ No |
| Westchester Open Data | 🔄 Researching | High | ❌ No |
| NY State Open Data | 🔄 Researching | High | ❌ No |

### Medium Priority (Phase 3-4)
| Source | Status | Priority | Downloaded |
|--------|--------|----------|------------|
| County Budget Data | 🔄 Researching | Medium | ❌ No |
| Property Tax Records | 🔄 Researching | Medium | ❌ No |
| Building Permits | 🔄 Researching | Medium | ❌ No |

### Lower Priority (Phase 5+)
| Source | Status | Priority | Downloaded |
|--------|--------|----------|------------|
| OpenStreetMap | 📋 Planned | Low | ❌ No |
| EPA Environmental | 📋 Planned | Low | ❌ No |
| USGS Elevation | 📋 Planned | Low | ❌ No |

---

## 🔐 API Keys & Authentication

### Required API Keys
| Service | Key Required | Status | Notes |
|---------|--------------|--------|-------|
| Census API | Yes | ❌ Not obtained | Free registration at census.gov |
| Westchester Open Data | No (optional) | N/A | Optional app token for higher limits |
| NY State Open Data | No (optional) | N/A | Optional app token for higher limits |
| Metro-North GTFS | No | N/A | Public feed |

### API Key Storage
- Store in `Technical/configs/.env` file
- Never commit to version control
- Use `.env.template` for documentation

---

## 📥 Data Download Plan

### Phase 1: Foundation Data
1. **Metro-North GTFS** → `Technical/data/raw/transit/metro_north_gtfs.zip`
2. **Westchester County Boundary** → `Technical/data/raw/geographic/westchester_boundary.geojson`
3. **Municipality Boundaries** → `Technical/data/raw/geographic/municipalities.geojson`
4. **Census ACS (Westchester)** → `Technical/data/raw/demographics/census_acs_*.csv`

### Phase 2: Government Data
1. **Property Assessments** → `Technical/data/raw/property/assessments_*.csv`
2. **County Budget** → `Technical/data/raw/budget/county_budget_*.csv`
3. **Building Permits** → `Technical/data/raw/permits/building_permits_*.csv`

### Phase 3: Supplementary Data
1. **Parks & Recreation** → `Technical/data/raw/geographic/parks.geojson`
2. **Roads & Infrastructure** → `Technical/data/raw/geographic/roads.geojson`
3. **Environmental Data** → `Technical/data/raw/environment/*.csv`

---

## 📝 Data Documentation Template

For each dataset downloaded, create a metadata file:

```markdown
# Dataset Name

**Source**: [URL]
**Downloaded**: [Date]
**Format**: [CSV/JSON/GeoJSON/etc.]
**Size**: [File size]
**Records**: [Number of records]

## Fields
- field_name: description, data type
- ...

## Data Quality
- Completeness: [%]
- Issues found: [List any issues]
- Cleaning required: [Yes/No - describe]

## Update Schedule
- Frequency: [Daily/Weekly/Monthly/Annual]
- Last updated by source: [Date]
- Next update: [Expected date]

## Processing Notes
[Any notes about processing this data]
```

---

## 🔄 Update Schedule

### Automated Updates (Future)
- Daily: Real-time transit data (if implemented)
- Weekly: County Open Data portal check
- Monthly: Census estimates (when released)
- Quarterly: Budget data
- Annual: ACS data, property assessments

### Manual Updates
- On-demand: Special requests or new datasets
- As needed: Bug fixes or data corrections

---

## ⚠️ Data Quality Notes

### Known Issues
(None yet - to be documented as data is acquired)

### Data Gaps
(To be identified during Phase 2 data collection)

### Validation Checklist
- [ ] All coordinate systems documented and consistent
- [ ] All dates in ISO format (YYYY-MM-DD)
- [ ] Missing values handled consistently
- [ ] Data dictionaries created for all datasets
- [ ] Source attribution included in all outputs

---

## 📚 Reference Documentation

### Socrata API (Westchester & NY State Open Data)
- Developer Portal: https://dev.socrata.com/
- Query Language (SoQL): https://dev.socrata.com/docs/queries/
- App Token: https://dev.socrata.com/docs/app-tokens.html

### GTFS Reference
- Specification: https://gtfs.org/reference/static/
- Best Practices: https://gtfs.org/best-practices/
- Validation: https://gtfs-validator.mobilitydata.org/

### Census API
- Getting Started: https://www.census.gov/data/developers/guidance/api-user-guide.html
- Variable Search: https://api.census.gov/data.html
- Geographic Areas: https://www.census.gov/programs-surveys/geography/guidance/geo-identifiers.html

---

## 📞 Data Source Contacts

### Westchester County
- Open Data Portal Support: (To be identified)
- GIS Department: (To be identified)

### New York State
- Open Data Support: opendata@its.ny.gov

### MTA Metro-North
- Developer Support: https://new.mta.info/developers

### U.S. Census Bureau
- API Support: https://www.census.gov/data/developers/about/contact-us.html

---

## 🔄 Change Log

### 2025-10-12
- Initial data sources document created
- Identified primary sources (5 main sources)
- Documented Census API structure for Westchester County
- Created data download plan

---

**Next Steps**:
1. Register for Census API key
2. Explore Westchester County Open Data portal
3. Download Metro-North GTFS data
4. Begin cataloging available datasets
5. Create data importers for priority sources

---

*Complete catalog of data sources for Westchester County Data Platform*

