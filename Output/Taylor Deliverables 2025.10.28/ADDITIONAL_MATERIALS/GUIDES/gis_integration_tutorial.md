# GIS Integration Tutorial
## Westchester County Sidewalk Analysis Data Package

### Overview
This tutorial provides step-by-step guidance for integrating the Westchester County Sidewalk Analysis geospatial data into your GIS workflow. The package contains over 40 GeoJSON files with comprehensive sidewalk infrastructure data.

### Table of Contents
1. [Quick Start Guide](#quick-start)
2. [Software-Specific Instructions](#software-instructions)
3. [Data Dictionary](#data-dictionary)
4. [Analysis Examples](#analysis-examples)
5. [Troubleshooting](#troubleshooting)

---

### Quick Start Guide {#quick-start}

#### Step 1: Locate the Data
```
GEOSPATIAL_DATA/
├── processed/           # Analysis results (9 files)
├── raw/
│   ├── infrastructure/  # Infrastructure layers (10 files)
│   ├── boundaries/      # Boundary layers (6 files)
│   ├── transit/         # Transit data (1 file)
│   └── municipal_services/ # Municipal services (5 files)
```

#### Step 2: Choose Your GIS Software
- QGIS (recommended for free/open source)
- ArcGIS Pro
- Python with GeoPandas
- R with sf package

#### Step 3: Load the Data
1. Open your GIS software
2. Navigate to the GEOSPATIAL_DATA folder
3. Add desired layers (start with `processed/county_wide_coverage.geojson`)

---

### Software-Specific Instructions {#software-instructions}

#### QGIS Integration
**Recommended for most users**

1. **Installation**: Download from qgis.org
2. **Loading Data**:
   - `Layer → Add Layer → Add Vector Layer`
   - Browse to GEOSPATIAL_DATA directory
   - Select GeoJSON files
   - Click "Add"

3. **Reproject for Analysis**:
   ```
   Right-click layer → Properties → Source
   Set CRS to EPSG:2263 (NAD83 / New York Long Island)
   ```

4. **Basic Analysis Example**:
   ```
   Load: county_wide_coverage.geojson
   Load: westchester_metro_north_stations.geojson
   Vector → Analysis Tools → Buffer (0.5 miles)
   Vector → Analysis Tools → Clip
   ```

#### ArcGIS Pro Integration

1. **Loading Data**:
   - `Add Data` button → Browse to GEOSPATIAL_DATA
   - Or drag-and-drop GeoJSON files into Contents pane

2. **Projection**:
   ```
   Right-click layer → Properties → Source → Spatial Reference
   Set to NAD 1983 StatePlane New York Long Island FIPS 3104
   ```

3. **Analysis Tools**:
   ```
   Analysis → Tools → Buffer (0.5 miles)
   Analysis → Tools → Intersect
   Analysis → Tools → Summary Statistics
   ```

#### Python Integration

```python
import geopandas as gpd
import matplotlib.pyplot as plt

# Load data
coverage = gpd.read_file('processed/county_wide_coverage.geojson')
stations = gpd.read_file('raw/transit/westchester_metro_north_stations.geojson')

# Reproject to NY State Plane
coverage = coverage.to_crs('EPSG:2263')
stations = stations.to_crs('EPSG:2263')

# Create 0.5-mile buffers
stations_buffer = stations.buffer(2640)  # 2640 feet = 0.5 miles

# Find roads within buffers
roads_in_buffers = gpd.sjoin(coverage, gpd.GeoDataFrame(geometry=stations_buffer),
                             how='inner', op='within')

# Calculate statistics
coverage_stats = roads_in_buffers.groupby('coverage_status').size()
print(coverage_stats)
```

#### R Integration

```r
library(sf)
library(dplyr)

# Load data
coverage <- st_read('processed/county_wide_coverage.geojson')
stations <- st_read('raw/transit/westchester_metro_north_stations.geojson')

# Reproject
coverage_proj <- st_transform(coverage, 2263)
stations_proj <- st_transform(stations, 2263)

# Create buffers
station_buffers <- st_buffer(stations_proj, 2640)  # 0.5 miles

# Find intersecting roads
roads_in_buffers <- st_intersection(coverage_proj, station_buffers)

# Calculate statistics
coverage_summary <- roads_in_buffers %>%
  group_by(coverage_status) %>%
  summarise(count = n(), total_length = sum(road_length_ft))

print(coverage_summary)
```

---

### Data Dictionary {#data-dictionary}

#### Key Layers

**county_wide_coverage.geojson** (Primary analysis layer)
- `road_id`: Unique identifier
- `coverage_status`: 'both_sides', 'one_side', 'none'
- `coverage_percentage`: Percentage of road with sidewalks
- `priority_rank`: Priority ranking (1-502)
- `estimated_cost`: Construction cost in dollars

**priority_sidewalk_gaps.geojson** (Priority gaps)
- `gap_id`: Unique gap identifier
- `priority_score`: Composite score (0-100)
- `proximity_to_transit`: Distance to nearest station (miles)
- `implementation_phase`: Recommended phase (1-4)

**tod_area_roads.geojson** (TOD analysis)
- `station_name`: Associated Metro-North station
- `distance_to_station`: Distance in miles
- `coverage_status`: Current sidewalk coverage
- `ridership_daily`: Daily station boardings

**westchester_metro_north_stations.geojson** (Transit stations)
- `station_name`: Official station name
- `line`: Metro-North line (Hudson, Harlem, New Haven)
- `daily_ridership`: Average daily boardings
- `parking_spaces`: Available parking

#### Coordinate System
- **Native format**: EPSG:4326 (WGS 84)
- **Recommended for analysis**: EPSG:2263 (NAD83 / New York Long Island)
- **Units**: Feet for analysis, decimal degrees for storage

---

### Analysis Examples {#analysis-examples}

#### Example 1: Coverage Analysis by Municipality

```python
import geopandas as gpd

# Load data
coverage = gpd.read_file('processed/county_wide_coverage.geojson')

# Calculate coverage by municipality
municipality_coverage = coverage.groupby('municipality').agg({
    'road_length_ft': 'sum',
    'sidewalk_length_ft': 'sum'
}).reset_index()

# Calculate coverage percentage
municipality_coverage['coverage_percentage'] = (
    municipality_coverage['sidewalk_length_ft'] /
    municipality_coverage['road_length_ft'] * 100
)

# Sort by coverage rate
municipality_coverage = municipality_coverage.sort_values('coverage_percentage', ascending=False)
print(municipality_coverage.head(10))
```

#### Example 2: Priority Gap Analysis

```python
# Load priority gaps
gaps = gpd.read_file('processed/priority_sidewalk_gaps.geojson')

# Find gaps near transit
transit_gaps = gaps[gaps['proximity_to_transit'] <= 0.5]
print(f"Gaps within 0.5 miles of transit: {len(transit_gaps)}")

# Gaps near schools
school_gaps = gaps[gaps['school_proximity'] == True]
print(f"Gaps near schools: {len(school_gaps)}")

# High-priority gaps (score > 80)
high_priority_gaps = gaps[gaps['priority_score'] > 80]
print(f"High-priority gaps: {len(high_priority_gaps)}")

# Visualize priority distribution
gaps.plot(column='priority_score', legend=True, figsize=(12, 8))
```

#### Example 3: Economic Impact Analysis

```python
# Combine coverage with property value analysis
coverage = gpd.read_file('processed/county_wide_coverage.geojson')

# Estimate property value increases
coverage['property_value_increase'] = coverage['sidewalk_length_ft'] * 450000 * 0.035 / 5280
# Assuming $450k avg property, 3.5% increase, average lot 5280 ft

# Calculate total economic impact by municipality
economic_impact = coverage.groupby('municipality').agg({
    'property_value_increase': 'sum',
    'road_length_ft': 'sum'
}).reset_index()

economic_impact = economic_impact.sort_values('property_value_increase', ascending=False)
print(economic_impact.head(10))
```

#### Example 4: Station Area Analysis

```python
# Load TOD and station data
tod_roads = gpd.read_file('processed/tod_area_roads.geojson')
stations = gpd.read_file('raw/transit/westchester_metro_north_stations.geojson')

# Coverage statistics by station
station_coverage = tod_roads.groupby('station_name').agg({
    'road_length_ft': 'sum',
    'sidewalk_length_ft': 'sum',
    'distance_to_station': 'mean'
}).reset_index()

station_coverage['coverage_percentage'] = (
    station_coverage['sidewalk_length_ft'] /
    station_coverage['road_length_ft'] * 100
)

# Find stations with lowest coverage
lowest_coverage = station_coverage.nsmallest(5, 'coverage_percentage')
print("Stations needing priority attention:")
print(lowest_coverage[['station_name', 'coverage_percentage']])
```

---

### Troubleshooting {#troubleshooting}

#### Common Issues

**Q: Data doesn't display or appears empty**
A: Check coordinate reference system. Try reprojecting to EPSG:2263 for New York area analysis.

**Q: Performance is slow with large datasets**
A:
- Use spatial indexing
- Filter data to your area of interest
- Consider using a subset for initial analysis

**Q: Attribute data seems incorrect**
A:
- Check data types (some fields may be strings instead of numbers)
- Verify null values are handled appropriately
- Refer to data dictionary for field descriptions

**Q: Can't join layers**
A:
- Ensure both layers have the same coordinate system
- Check field names and data types
- Verify spatial relationships (intersects, contains, etc.)

#### Performance Tips

1. **Use spatial indexes** when performing spatial joins
2. **Filter data** to your area of interest before complex operations
3. **Reproject to appropriate coordinate system** for distance/area calculations
4. **Use appropriate data types** (numeric vs string)
5. **Consider processing in chunks** for very large datasets

#### Getting Help

- **Technical support**: gis@westchestergov.com
- **Data questions**: planning@westchestergov.com
- **Documentation**: See full `geospatial_data_documentation.pdf`
- **Online resources**: QGIS/ArcGIS documentation, GeoPandas tutorials

---

### Next Steps

After mastering basic data integration:

1. **Combine multiple layers** for comprehensive analysis
2. **Create custom visualizations** and maps
3. **Develop automated analysis workflows**
4. **Integrate with your existing GIS systems**
5. **Share findings** with stakeholders

Remember to cite the data source:
"Westchester County Sidewalk Coverage Analysis (2025). Westchester County Department of Planning."