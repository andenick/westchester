# Data Attribution and Usage Guide
## Westchester County Sidewalk Analysis Data Package

### Overview
This document provides attribution requirements and usage guidelines for the Westchester County Sidewalk Analysis data package.

---

### License Terms

**Usage Rights:**
- ✅ Free for non-commercial and research purposes
- ✅ Permitted for academic and governmental use
- ✅ Modifications allowed with proper attribution
- ✅ Distribution allowed with inclusion of attribution

**Restrictions:**
- ❌ Commercial resale without permission
- ❌ Removal of attribution notices
- ❌ Misrepresentation of data sources

---

### Required Attribution

#### Standard Attribution
When using this data in publications, presentations, or derived works:

```
Westchester County Sidewalk Coverage Analysis (2025).
Westchester County Department of Planning in partnership with Arcanum Performance Monitoring.
```

#### Academic Citation Format
```
Westchester County Department of Planning. (2025).
Westchester County Sidewalk Coverage Analysis Geospatial Data.
Retrieved October 2025, from [URL or local repository].
```

#### Presentation/Report Attribution
Include on slide footers, report acknowledgments, or map credits:

```
Data Source: Westchester County Department of Planning (2025)
```

---

### Data Component Attribution

#### Primary Data Sources
- **Sidewalk Infrastructure**: Westchester County Department of Public Works
- **Road Network**: Westchester County GIS Division
- **Metro-North Stations**: Metropolitan Transportation Authority (MTA)
- **Demographic Data**: U.S. Census Bureau, American Community Survey
- **Property Data**: Westchester County Department of Finance

#### Analysis and Processing
- **Spatial Analysis**: Arcanum Performance Monitoring
- **Statistical Analysis**: Westchester County Planning Department
- **Cost-Benefit Modeling**: Economic Development Team
- **GIS Processing**: Technical Services Division

---

### Usage Guidelines

#### Academic and Research Use
**Permitted Uses:**
- Thesis and dissertation research
- Academic papers and publications
- Classroom instruction and learning
- Conference presentations and posters

**Requirements:**
- Provide full attribution in all publications
- Share derived datasets with attribution
- Inform Westchester County of significant findings
- Consider collaboration opportunities

#### Government and Municipal Use
**Permitted Uses:**
- Municipal planning and zoning
- Transportation planning studies
- Infrastructure asset management
- Public safety and emergency response

**Requirements:**
- Maintain data currency updates
- Share improvements with County
- Coordinate major analyses with Planning Department
- Follow County GIS standards

#### Non-Profit and Community Use
**Permitted Uses:**
- Community advocacy and organizing
- Non-profit service planning
- Educational outreach programs
- Community improvement initiatives

**Requirements:**
- Non-commercial use only
- Community benefit focus
- Attribution in all materials
- Share results with County when possible

---

### Data Quality and Limitations

#### Known Limitations
- **Temporal accuracy**: Data represents October 2025 conditions
- **Spatial accuracy**: ±10 meters for infrastructure features
- **Completeness**: County-maintained roads only (excludes private roads)
- **Attribute accuracy**: 95% or higher for key attributes

#### Intended Use
- **Planning scale**: Suitable for neighborhood to county-level analysis
- **Not suitable for**: Parcel-level engineering design or legal boundaries
- **Recommended scale**: 1:2,400 to 1:24,000 for mapping applications

---

### Technical Integration

#### GIS Integration
**Coordinate System:** EPSG:4326 (WGS 84) - Reproject to EPSG:2263 for analysis
**Format:** GeoJSON (RFC 7946) compatible with major GIS platforms
**Size:** ~45 MB total dataset (31 files)

#### Web Mapping
**Compatible with:**
- Leaflet.js and OpenLayers
- Google Maps API
- Mapbox GL JS
- ArcGIS Online

**Recommended:** Use tiles for web applications due to file size

#### Database Integration
**Schema:** See data dictionary for field specifications
**Spatial indexing:** Recommended for performance
**Update frequency:** Annual updates planned

---

### Redistribution Guidelines

#### Sharing Derived Data
When creating and sharing derived datasets:

1. **Maintain Attribution**: Include original data source attribution
2. **Document Changes**: Clearly document modifications and enhancements
3. **Share Improvements**: Consider sharing improvements with original source
4. **Version Control**: Track data versions and modification dates

#### Package Distribution
When redistributing the complete or partial data package:

1. **Include Documentation**: Provide this attribution guide
2. **Maintain Structure**: Keep original file organization where possible
3. **Update Contacts**: Include current contact information
4. **Check Currency**: Verify data is current before redistribution

---

### Contact Information

#### Primary Contacts
**Technical Questions:**
- Email: gis@westchestergov.com
- Phone: (914) 995-4700
- Department: Westchester County Planning Department

**Data Updates:**
- Website: www.westchestergov.com/planning
- Data Portal: data.westchestergov.com
- Update Frequency: Annual (or as needed)

#### Collaboration Opportunities
**Research Partnerships:**
- Academic institutions
- Transportation research organizations
- Urban planning programs
- Public health researchers

**Technical Collaboration:**
- GIS software developers
- Open data contributors
- Transportation technology companies
- Civic technology organizations

---

### Version History

| Version | Date | Changes | Contact |
|---------|------|---------|---------|
| 1.0 | October 2025 | Initial release with complete analysis package | Planning Department |
| 1.1 | Planned 2026 | Annual data updates and improvements | Planning Department |

---

### Acknowledgments

This data package was developed through the collaborative efforts of:

- **Westchester County Department of Planning** - Project management and analysis
- **Westchester County Department of Public Works** - Infrastructure data
- **Westchester County GIS Division** - Spatial data management
- **Arcanum Performance Monitoring** - Technical analysis and processing
- **Metropolitan Transportation Authority** - Transit data partnership
- **U.S. Census Bureau** - Demographic data foundation

---

### Additional Resources

#### Documentation
- Complete Technical Report: `LATEX_REPORTS/comprehensive_technical_analysis.pdf`
- GIS Data Documentation: `LATEX_REPORTS/geospatial_data_documentation.pdf`
- Statistical Analysis: `LATEX_REPORTS/statistical_analysis_report.pdf`

#### Online Resources
- Westchester County Planning: www.westchestergov.com/planning
- Open Data Portal: data.westchestergov.com
- Metro-North: new.mta.info/mnr

#### Related Projects
- Complete Streets Analysis
- Transit-Oriented Development Study
- Bicycle Network Analysis
- Pedestrian Safety Analysis

---

This attribution guide should be included with any redistribution of the data package and referenced in all publications or presentations using this data.