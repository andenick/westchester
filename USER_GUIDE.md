# Westchester County Data Platform - User Guide

**Version:** 1.0.0  
**Last Updated:** October 13, 2025

---

## 🚀 Quick Start

### Accessing the Platform

1. **Open your web browser**
2. **Navigate to:** http://localhost:5173/
3. **Start exploring!**

### System Requirements
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Internet connection (for map tiles)
- JavaScript enabled

---

## 📍 Main Navigation

### Homepage
- **URL:** http://localhost:5173/
- Overview of the platform
- Quick links to dashboards
- Platform statistics

### Dashboard Menu
Click **"Dashboards"** in the top navigation bar to access:
- 📊 Overview Dashboard
- 👥 Demographics
- 🚂 Transit Access
- 🏘️ Property Tax
- 💰 County Budget
- 🚒 Municipal Services
- ⚖️ Municipality Comparison

---

## 🗺️ Using the Interactive Map

### Overview Dashboard Map
The main map is located in the **Overview Dashboard**.

### Map Controls

#### Basemap Selection
1. Click the **layers icon** (top-right corner)
2. Choose your preferred basemap:
   - **Street Map** - Standard roads and labels
   - **Satellite** - Aerial imagery
   - **Terrain** - Topographic view

#### Data Layers (Toggle On/Off)
Check/uncheck to show or hide:
- ✅ 🚂 **Metro-North Stations** (56 stations)
- ✅ 🏞️ **Parks & Recreation** (1,140 parks)
- ✅ 🚶 **Trails & Bike Paths** (895 trails)
- ✅ 📍 **Public Amenities** (158 facilities)

#### Interactive Features
- **Click** any feature for detailed popup information
- **Zoom** using mouse wheel or +/- buttons
- **Pan** by clicking and dragging
- **View Legend** at bottom-left for feature counts

### Map Legend
The legend shows:
- Feature types and their icons
- Count of features for each layer
- Always visible at bottom-left

---

## 📊 Dashboard Guide

### 1. Overview Dashboard

**What it shows:**
- County-level demographics summary
- Interactive map with all data layers
- Data availability status
- Quick statistics cards

**How to use:**
1. View demographic cards at the top
2. Explore the interactive map (toggle layers)
3. Check data availability section

**Key Features:**
- Real-time data loading
- Multi-layer map visualization
- County statistics

---

### 2. Demographics Dashboard

**What it shows:**
- Population by municipality (bar chart)
- Race/ethnicity distribution (pie chart)
- Income distribution (bar chart)
- Housing statistics
- Employment metrics

**How to use:**
1. Scroll through demographic cards
2. Analyze population charts
3. Review housing and employment data
4. Compare municipalities visually

**Key Metrics:**
- Total Population
- Median Household Income
- Median Home Value
- Unemployment Rate

---

### 3. Transit Dashboard

**What it shows:**
- 56 Metro-North Railroad stations
- Station directory with details
- Accessibility information
- Interactive transit map

**How to use:**
1. View summary cards (total stations, accessible count)
2. Explore station locations on map
3. Click stations for details
4. Browse station directory table

**Key Information:**
- Station names and codes
- Wheelchair accessibility
- Geographic coordinates
- Coverage analysis

---

### 4. Property Tax Dashboard

**What it shows:**
- Property tax assessment trends
- Tax rates by municipality
- Geographic distribution

**How to use:**
1. Review average assessment trends
2. Compare tax rates across municipalities
3. Analyze geographic distribution

**Note:** Currently shows sample/demonstration data.

---

### 5. Budget Dashboard

**What it shows:**
- County spending by department
- Budget trends (2019-2023)
- Top spending priorities

**How to use:**
1. Review pie chart for budget allocation
2. Analyze spending trends over time
3. Explore top priorities

**Key Sections:**
- Education (35%)
- Public Safety (22%)
- Health & Human Services (15%)
- Other departments

---

### 6. Municipal Services Dashboard

**What it shows:**
- Police, fire, library coverage
- Emergency response times
- Service facilities by municipality

**How to use:**
1. View service coverage cards
2. Check emergency response times
3. Browse facility inventory table

**Services Tracked:**
- Police Departments
- Fire Districts
- Public Libraries
- Municipal Services

---

### 7. Municipality Comparison Dashboard

**What it shows:**
- Side-by-side comparison of municipalities
- Population, income, housing metrics
- Interactive charts and tables

**How to use:**
1. **Select municipalities** (up to 4)
   - Click buttons to select/deselect
   - Selected municipalities show ✓ mark
2. **View comparison charts**
   - Population comparison
   - Income comparison
   - Home value comparison
3. **Review detailed table**
   - All metrics side-by-side
   - Easy comparison

**Available Metrics:**
- Population
- Median Household Income
- Median Home Value
- Area (square miles)
- Population Density
- Tax Rate

---

## 📈 Understanding the Data

### Data Sources

All data comes from official sources:

1. **U.S. Census Bureau**
   - Demographics (2022 ACS 5-Year Estimates)
   - 241 census tracts
   - County and municipality data

2. **Metro-North Railroad**
   - GTFS transit feed
   - 56 stations in Westchester
   - Real schedule and accessibility data

3. **OpenStreetMap**
   - 1,140 parks and recreation areas
   - 895 trails and bike paths
   - 158 public amenities

4. **NY State Open Data**
   - Crime statistics
   - Health facilities
   - Government records

### Data Quality Indicators

**⭐⭐⭐⭐⭐ (5 stars)** - Official government, regularly updated, complete  
**⭐⭐⭐⭐ (4 stars)** - Reliable source, mostly complete  
**⭐⭐⭐ (3 stars)** - Useful data, some gaps  

### Data Freshness

Check the **Overview Dashboard** for:
- Data availability status
- Last updated dates
- Data source attribution

---

## 🔍 Tips & Tricks

### Map Usage
- **Start with 1-2 layers** to avoid overcrowding
- **Use satellite view** for geographic context
- **Click features** for detailed information
- **Toggle layers** to compare different datasets

### Chart Interaction
- **Hover over charts** for exact values
- **View top municipalities** in ranked charts
- **Check data year** noted below charts

### Navigation
- **Use dropdown menu** to quickly switch dashboards
- **Click platform title** to return to homepage
- **Check footer** for additional links

### Performance
- **Disable unused layers** if map is slow
- **Zoom in** to specific areas for better detail
- **Refresh page** if data doesn't load

---

## 📱 Mobile & Responsive Design

### Mobile Access
The platform works on mobile devices:
- Responsive layouts adapt to screen size
- Touch-friendly controls
- Optimized for tablets and phones

### Best Experience
For the best experience, use:
- Desktop or laptop (1920x1080 or higher)
- Tablet in landscape mode (minimum 768px width)
- Modern browser with JavaScript enabled

---

## 🛠️ Troubleshooting

### Common Issues

**Map not displaying:**
1. Check internet connection (needed for map tiles)
2. Verify backend API is running (http://localhost:8000/api/health)
3. Clear browser cache and refresh

**No data on charts:**
1. Ensure data has been downloaded
2. Check API endpoints: http://localhost:8000/docs
3. Look for error messages in browser console (F12)

**Dashboard not loading:**
1. Verify frontend server is running (http://localhost:5173)
2. Check browser console for errors (F12)
3. Try refreshing the page

**Layers not showing:**
1. Make sure layer is checked in layer control
2. Zoom in/out to see features
3. Verify data files exist (check API /metadata endpoint)

---

## 📊 Data Export & Download

### Excel Files
Pre-generated Excel files are available in:
```
Output/Data/Results/
```

Files include:
- County demographics
- Census tract data
- Metro-North stations
- Transit accessibility analysis

### PDF Reports
Professional reports available in:
```
Output/PDFs/
```

Reports include:
- Methodology Report
- Executive Summary
- Reporting Strategy

### API Data Access
Use the API to get raw data:
```
http://localhost:8000/docs
```

All endpoints provide JSON data that can be:
- Downloaded directly
- Integrated into other applications
- Analyzed programmatically

---

## 🔗 Important URLs

### Application
- **Homepage:** http://localhost:5173/
- **Dashboards:** http://localhost:5173/dashboards/overview

### API
- **API Root:** http://localhost:8000/
- **Documentation:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/api/health
- **Metadata:** http://localhost:8000/api/metadata

### Data Endpoints
- **Transit Stations:** /api/transit/stations
- **Demographics:** /api/demographics/county
- **Parks:** /api/infrastructure/parks
- **Trails:** /api/infrastructure/trails
- **Amenities:** /api/infrastructure/amenities

---

## 📚 Additional Resources

### Documentation
- **Data Sources Catalog:** `DATA_SOURCES_CATALOG.md`
- **Manual Import Guide:** `MANUAL_DATA_IMPORT_GUIDE.md`
- **Launch Report:** `[2025.10.13] LAUNCH_REPORT.md`

### Reports
- **Methodology Report:** `Output/PDFs/westchester_methodology_report.pdf`
- **Executive Summary:** `Output/PDFs/westchester_executive_summary.pdf`
- **Reporting Strategy:** `Output/PDFs/westchester_reporting_strategy.pdf`

### Technical
- **API Documentation:** http://localhost:8000/docs
- **Developer Guide:** `Technical/DEVELOPER_GUIDE.md` (to be created)

---

## 💡 Feature Highlights

### Interactive Map
- ✨ **Multiple basemaps** - Street, Satellite, Terrain
- ✨ **4 data layers** - Toggle any combination
- ✨ **2,491 features** - Stations, parks, trails, amenities
- ✨ **Rich popups** - Detailed information on click
- ✨ **Legend** - Always visible with counts

### Dashboards
- ✨ **7 dashboards** - Comprehensive coverage
- ✨ **Interactive charts** - Tooltips and details
- ✨ **Real data** - Official government sources
- ✨ **Responsive** - Works on all devices

### Data Quality
- ✨ **6 sources** - Diverse, authoritative data
- ✨ **100% Druck compliance** - Professional standards
- ✨ **Complete metadata** - Full documentation
- ✨ **Regular updates** - Scheduled refresh

---

## 🎯 Getting the Most Out of the Platform

### For County Officials
1. Use **Demographics Dashboard** for planning decisions
2. Review **Transit Dashboard** for accessibility analysis
3. Analyze **Budget Dashboard** for spending insights
4. Compare municipalities with **Comparison Dashboard**

### For Researchers
1. Access raw data via **API endpoints**
2. Download **Excel files** for analysis
3. Review **methodology reports** for data quality
4. Use **census tract data** for granular analysis

### For Residents
1. Explore **Interactive Map** to find parks and trails
2. Check **Transit Dashboard** for station locations
3. View **Demographics** to understand your community
4. Use **Municipality Comparison** to compare towns

### For Planners
1. Analyze **service coverage** for gaps
2. Review **infrastructure data** for improvements
3. Use **geographic data** for spatial planning
4. Reference **budget data** for allocation decisions

---

## 📞 Support

### Questions or Issues?
1. Check this User Guide first
2. Review [2025.10.13] LAUNCH_REPORT.md
3. Consult DATA_SOURCES_CATALOG.md
4. Check browser console for error messages (F12)

### Feedback
Your feedback helps improve the platform:
- Report bugs or issues
- Suggest new features
- Request additional data sources
- Share use cases

---

**Happy Exploring!**

The Westchester County Data Platform provides comprehensive, authoritative data to support evidence-based decision making for county planning, policy analysis, and research.

---

**Platform Version:** 1.0.0  
**Last Updated:** October 13, 2025  
**Maintained by:** Arcanum Research Initiative

