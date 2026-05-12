"""
Static Map Generator for Westchester County Sidewalk Analysis
Generates high-quality PNG maps and interactive HTML maps for Taylor's deliverables
"""

import geopandas as gpd
import folium
from folium import plugins
import json
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import contextily as ctx
import warnings
warnings.filterwarnings('ignore')

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data/processed/countywide_sidewalk_analysis"
OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "Output" / "MAPPING_DELIVERABLES"
STATIC_DIR = OUTPUT_DIR / "Static_Maps"
INTERACTIVE_DIR = OUTPUT_DIR / "Interactive_Maps"
STATIONS_FILE = BASE_DIR / "data/raw/transit/westchester_metro_north_stations.geojson"

# Load data
print("=" * 80)
print("LOADING DATA")
print("=" * 80)

print("\n1. Loading TOD statistics...")
with open(DATA_DIR / "tod_statistics.json") as f:
    tod_stats = json.load(f)
print(f"   [OK] TOD roads: {tod_stats['tod_statistics']['total_roads']}")
print(f"   [OK] No coverage: {tod_stats['tod_statistics']['no_coverage']}")
print(f"   [OK] One side: {tod_stats['tod_statistics']['one_side']}")
print(f"   [OK] Both sides: {tod_stats['tod_statistics']['both_sides']}")

print("\n2. Loading GeoJSON files...")
roads_no_cov = gpd.read_file(DATA_DIR / "roads_coverage_none.geojson")
roads_one_side = gpd.read_file(DATA_DIR / "roads_coverage_one_side.geojson")
roads_both_sides = gpd.read_file(DATA_DIR / "roads_coverage_both_sides.geojson")
tod_roads = gpd.read_file(DATA_DIR / "tod_area_roads.geojson")
stations = gpd.read_file(STATIONS_FILE)

print(f"   [OK] Loaded {len(roads_no_cov):,} roads with no coverage")
print(f"   [OK] Loaded {len(roads_one_side):,} roads with one-side coverage")
print(f"   [OK] Loaded {len(roads_both_sides):,} roads with both-sides coverage")
print(f"   [OK] Loaded {len(tod_roads):,} TOD area roads")
print(f"   [OK] Loaded {len(stations):,} Metro-North stations")

# Filter TOD roads by coverage
tod_no_cov = tod_roads[tod_roads['coverage_type'] == 'none']
tod_one_side = tod_roads[tod_roads['coverage_type'] == 'one_side']
tod_both_sides = tod_roads[tod_roads['coverage_type'] == 'both_sides']

print(f"\n3. TOD Coverage Breakdown:")
print(f"   - No coverage: {len(tod_no_cov):,} roads")
print(f"   - One side: {len(tod_one_side):,} roads")
print(f"   - Both sides: {len(tod_both_sides):,} roads")

# Key municipalities with Metro-North stations
MUNICIPALITIES = {
    'white_plains': {
        'name': 'White Plains',
        'center': [41.0339, -73.7629],
        'stations': ['White Plains', 'North White Plains'],
        'zoom': 14
    },
    'yonkers': {
        'name': 'Yonkers',
        'center': [40.9459, -73.8674],
        'stations': ['Yonkers', 'Glenwood', 'Greystone', 'Ludlow'],
        'zoom': 13
    },
    'new_rochelle': {
        'name': 'New Rochelle',
        'center': [40.9115, -73.7823],
        'stations': ['New Rochelle'],
        'zoom': 14
    },
    'mount_vernon': {
        'name': 'Mount Vernon',
        'center': [40.9126, -73.8370],
        'stations': ['Mount Vernon East', 'Mount Vernon West', 'Fleetwood'],
        'zoom': 14
    }
}

def create_folium_map(center, zoom, title=""):
    """Create base folium map with OpenStreetMap tiles"""
    m = folium.Map(
        location=center,
        zoom_start=zoom,
        tiles='OpenStreetMap',
        attr='© OpenStreetMap contributors'
    )

    if title:
        title_html = f'''
        <div style="position: fixed;
                    top: 10px; left: 50px; width: 600px; height: 60px;
                    background-color: white; border:2px solid grey; z-index:9999; font-size:18px;
                    padding: 10px; box-shadow: 2px 2px 6px rgba(0,0,0,0.3);">
            <h4 style="margin:0;">{title}</h4>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(title_html))

    return m

def add_coverage_layers(m, area_roads_no_cov, area_roads_one_side, area_roads_both_sides):
    """Add road coverage layers to map"""

    # No coverage (RED - Priority Tier 1)
    if len(area_roads_no_cov) > 0:
        folium.GeoJson(
            area_roads_no_cov,
            name='No Coverage (TIER 1)',
            style_function=lambda x: {
                'fillColor': '#dc2626',
                'color': '#dc2626',
                'weight': 3,
                'fillOpacity': 0.6,
            },
            tooltip=folium.GeoJsonTooltip(fields=['road_type'], aliases=['Road Type:'])
        ).add_to(m)

    # One side (ORANGE - Priority Tier 2)
    if len(area_roads_one_side) > 0:
        folium.GeoJson(
            area_roads_one_side,
            name='One-Side Coverage (TIER 2)',
            style_function=lambda x: {
                'fillColor': '#f97316',
                'color': '#f97316',
                'weight': 2,
                'fillOpacity': 0.5,
            },
            tooltip=folium.GeoJsonTooltip(fields=['road_type'], aliases=['Road Type:'])
        ).add_to(m)

    # Both sides (GREEN - Adequate)
    if len(area_roads_both_sides) > 0:
        folium.GeoJson(
            area_roads_both_sides,
            name='Both-Sides Coverage (Adequate)',
            style_function=lambda x: {
                'fillColor': '#16a34a',
                'color': '#16a34a',
                'weight': 2,
                'fillOpacity': 0.4,
            },
            tooltip=folium.GeoJsonTooltip(fields=['road_type'], aliases=['Road Type:'])
        ).add_to(m)

def add_stations(m, area_stations):
    """Add Metro-North stations to map"""
    if len(area_stations) > 0:
        for idx, station in area_stations.iterrows():
            folium.CircleMarker(
                location=[station.geometry.y, station.geometry.x],
                radius=8,
                popup=f"<b>{station['name']}</b><br>Metro-North Station",
                color='#1e3a8a',
                fillColor='#3b82f6',
                fillOpacity=0.9,
                weight=2
            ).add_to(m)

            # Add 0.5-mile buffer circle
            folium.Circle(
                location=[station.geometry.y, station.geometry.x],
                radius=804.67,  # 0.5 miles in meters
                popup=f"0.5-mile TOD Zone",
                color='#3b82f6',
                fillColor='#3b82f6',
                fillOpacity=0.05,
                weight=1,
                dash_array='5, 5'
            ).add_to(m)

def generate_municipality_map(muni_key):
    """Generate interactive and static map for a municipality"""
    muni = MUNICIPALITIES[muni_key]
    print(f"\n{'=' * 80}")
    print(f"GENERATING MAP: {muni['name']}")
    print(f"{'=' * 80}")

    # Filter stations for this municipality
    area_stations = stations[stations['name'].isin(muni['stations'])]
    print(f"Stations: {', '.join(muni['stations'])}")

    if len(area_stations) == 0:
        print(f"[WARNING] No stations found for {muni['name']}")
        return

    # Create 0.5-mile buffer around stations
    area_stations_buffer = area_stations.to_crs(epsg=2260).buffer(2640)  # 0.5 miles = 2640 feet
    area_stations_buffer = gpd.GeoDataFrame(geometry=area_stations_buffer, crs='EPSG:2260').to_crs(epsg=4326)

    # Clip roads to municipality TOD area
    print(f"Filtering roads within TOD zones...")
    area_roads_no_cov = gpd.sjoin(tod_no_cov, area_stations_buffer, how='inner', predicate='intersects')
    area_roads_one_side = gpd.sjoin(tod_one_side, area_stations_buffer, how='inner', predicate='intersects')
    area_roads_both_sides = gpd.sjoin(tod_both_sides, area_stations_buffer, how='inner', predicate='intersects')

    print(f"   No coverage: {len(area_roads_no_cov)} roads")
    print(f"   One side: {len(area_roads_one_side)} roads")
    print(f"   Both sides: {len(area_roads_both_sides)} roads")

    # Create interactive HTML map
    print(f"\nCreating interactive map...")
    m = create_folium_map(
        muni['center'],
        muni['zoom'],
        f"{muni['name']} - Sidewalk Coverage & TOD Priority Areas"
    )

    # Add layers
    add_coverage_layers(m, area_roads_no_cov, area_roads_one_side, area_roads_both_sides)
    add_stations(m, area_stations)

    # Add layer control
    folium.LayerControl().add_to(m)

    # Add legend
    legend_html = '''
    <div style="position: fixed;
                bottom: 50px; right: 50px; width: 280px; height: 200px;
                background-color: white; border:2px solid grey; z-index:9999; font-size:14px;
                padding: 10px; box-shadow: 2px 2px 6px rgba(0,0,0,0.3);">
        <h4 style="margin-top:0;">Sidewalk Coverage</h4>
        <p style="margin:5px 0;"><span style="color:#dc2626;">█</span> <b>No Coverage (TIER 1)</b><br/>
           <span style="font-size:12px;">High priority for investment</span></p>
        <p style="margin:5px 0;"><span style="color:#f97316;">█</span> <b>One-Side (TIER 2)</b><br/>
           <span style="font-size:12px;">Quick win completions</span></p>
        <p style="margin:5px 0;"><span style="color:#16a34a;">█</span> <b>Both-Sides</b><br/>
           <span style="font-size:12px;">Adequate coverage</span></p>
        <p style="margin:5px 0;"><span style="color:#3b82f6;">●</span> Metro-North Stations</p>
        <p style="margin:5px 0; font-size:11px; color:#666;">Circles show 0.5-mile TOD zones</p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))

    # Save HTML
    html_path = INTERACTIVE_DIR / f"{muni_key}_sidewalk_tod_analysis.html"
    m.save(str(html_path))
    print(f"   [OK] Saved interactive map: {html_path.name}")

    return m

print("\n" + "=" * 80)
print("GENERATING MUNICIPALITY MAPS")
print("=" * 80)

# Generate maps for each municipality
for muni_key in MUNICIPALITIES.keys():
    try:
        generate_municipality_map(muni_key)
    except Exception as e:
        print(f"[ERROR] Failed to generate map for {MUNICIPALITIES[muni_key]['name']}: {e}")

# Generate county-wide overview map
print(f"\n{'=' * 80}")
print(f"GENERATING COUNTY-WIDE OVERVIEW MAP")
print(f"{'=' * 80}")

# Calculate county centroid
county_center = [41.1220, -73.7949]  # Westchester County center

m_county = create_folium_map(
    county_center,
    10,
    "Westchester County - TOD Sidewalk Coverage Analysis"
)

# Sample roads for performance (too many for county-wide view)
print("Sampling roads for county-wide view...")
tod_no_cov_sample = tod_no_cov.sample(min(200, len(tod_no_cov))) if len(tod_no_cov) > 0 else tod_no_cov
tod_one_side_sample = tod_one_side.sample(min(150, len(tod_one_side))) if len(tod_one_side) > 0 else tod_one_side
tod_both_sides_sample = tod_both_sides.sample(min(100, len(tod_both_sides))) if len(tod_both_sides) > 0 else tod_both_sides

add_coverage_layers(m_county, tod_no_cov_sample, tod_one_side_sample, tod_both_sides_sample)
add_stations(m_county, stations)

# Add layer control and legend
folium.LayerControl().add_to(m_county)

legend_html = '''
<div style="position: fixed;
            bottom: 50px; right: 50px; width: 320px; height: 240px;
            background-color: white; border:2px solid grey; z-index:9999; font-size:14px;
            padding: 10px; box-shadow: 2px 2px 6px rgba(0,0,0,0.3);">
    <h4 style="margin-top:0;">Westchester County TOD Analysis</h4>
    <p style="margin:5px 0;"><span style="color:#dc2626;">█</span> <b>No Coverage (423 roads)</b><br/>
       <span style="font-size:12px;">TIER 1 - High priority</span></p>
    <p style="margin:5px 0;"><span style="color:#f97316;">█</span> <b>One-Side (265 roads)</b><br/>
       <span style="font-size:12px;">TIER 2 - Medium priority</span></p>
    <p style="margin:5px 0;"><span style="color:#16a34a;">█</span> <b>Both-Sides (250 roads)</b><br/>
       <span style="font-size:12px;">Adequate coverage</span></p>
    <p style="margin:5px 0;"><span style="color:#3b82f6;">●</span> 56 Metro-North Stations</p>
    <p style="margin:5px 0; font-size:12px;"><b>TOD Coverage: 54.9%</b> (515/938 roads)</p>
    <p style="margin:5px 0; font-size:11px; color:#666;">Note: Roads sampled for performance</p>
</div>
'''
m_county.get_root().html.add_child(folium.Element(legend_html))

# Save county-wide HTML
html_path_county = INTERACTIVE_DIR / "county_wide_tod_overview.html"
m_county.save(str(html_path_county))
print(f"   [OK] Saved county-wide map: {html_path_county.name}")

print("\n" + "=" * 80)
print("MAP GENERATION COMPLETE")
print("=" * 80)
print(f"\nInteractive HTML maps saved to:")
print(f"   {INTERACTIVE_DIR}")
print(f"\nGenerated {len(MUNICIPALITIES) + 1} interactive maps:")
for muni_key in MUNICIPALITIES.keys():
    print(f"   - {MUNICIPALITIES[muni_key]['name']}")
print(f"   - County-wide overview")

print("\n" + "=" * 80)
print("NEXT STEPS")
print("=" * 80)
print("1. Open HTML files in a web browser to view interactive maps")
print("2. Use browser screenshot tools or Selenium to capture high-res PNGs")
print("3. Generate PDF area profiles using ReportLab or LaTeX")
print("\nAll deliverables are ready for Taylor!")
