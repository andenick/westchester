"""
Transit Sidewalk Coverage Analyzer
===================================

Analyzes sidewalk coverage on roads within 0.5 miles of Metro-North train stations
in Westchester County.

Data Sources:
- Taylor Shapefiles (County Sidewalks, County Roadways)
- Metro-North Station Data (existing platform)

Analysis Approach:
1. Load Metro-North stations and create 0.5-mile buffers
2. Identify roads within transit buffer zones
3. Match sidewalk polygons to road centerlines
4. Calculate coverage statistics by station
5. Identify priority gaps for improvement

Author: Westchester Data Platform
Date: 2025-10-17
"""

import geopandas as gpd
import pandas as pd
import json
import os
from pathlib import Path
from shapely.geometry import Point, LineString, Polygon, MultiPolygon
from shapely.ops import unary_union
import warnings
warnings.filterwarnings('ignore')


class TransitSidewalkAnalyzer:
    """
    Analyzes sidewalk coverage near Metro-North stations in Westchester County.
    """

    def __init__(self, base_path=None):
        """
        Initialize the analyzer with paths to data files.

        Args:
            base_path: Base directory for the project (default: auto-detect)
        """
        if base_path is None:
            # Auto-detect base path
            current_file = Path(__file__).resolve()
            self.base_path = current_file.parents[3]  # Go up to project root
        else:
            self.base_path = Path(base_path)

        # Define paths
        self.inputs_path = self.base_path / "Inputs" / "TaylorFiles" / "County Shapefiles"
        self.transit_path = self.base_path / "Technical" / "data" / "raw" / "transit"
        self.output_path = self.base_path / "Technical" / "data" / "processed" / "transit_sidewalk_analysis"

        # Create output directory
        self.output_path.mkdir(parents=True, exist_ok=True)

        # CRS definitions
        self.crs_nysp = "EPSG:2260"  # NY State Plane Long Island (feet)
        self.crs_wgs84 = "EPSG:4326"  # WGS84 (lat/lon)

        # Constants
        self.buffer_distance_miles = 0.5
        self.buffer_distance_feet = self.buffer_distance_miles * 5280  # 2640 feet
        self.sidewalk_buffer_feet = 10  # Buffer for matching sidewalks to roads

        # Data storage
        self.stations = None
        self.stations_nysp = None
        self.sidewalks = None
        self.roads_line = None
        self.roads_poly = None

    def load_data(self):
        """Load all required datasets."""
        print("=" * 80)
        print("LOADING DATA")
        print("=" * 80)

        # Load Metro-North stations
        print("\n1. Loading Metro-North Stations...")
        stations_file = self.transit_path / "westchester_metro_north_stations.geojson"
        self.stations = gpd.read_file(stations_file)
        print(f"   [OK] Loaded {len(self.stations)} stations")
        print(f"   CRS: {self.stations.crs}")

        # Transform stations to NY State Plane
        print(f"\n2. Transforming stations to {self.crs_nysp}...")
        self.stations_nysp = self.stations.to_crs(self.crs_nysp)
        print(f"   [OK] Transformed to NY State Plane (feet)")

        # Load Taylor shapefiles
        print("\n3. Loading County Sidewalks (Polygon)...")
        sidewalks_file = self.inputs_path / "County Sidewalks - Polygon" / "countysidewalks_polygon.shp"
        self.sidewalks = gpd.read_file(sidewalks_file)
        print(f"   [OK] Loaded {len(self.sidewalks):,} sidewalk polygons")
        print(f"   CRS: {self.sidewalks.crs}")
        print(f"   Types: {self.sidewalks['DESCRIPTIO'].unique()}")

        print("\n4. Loading County Roadways (Line)...")
        roads_line_file = self.inputs_path / "County Roadways - Line" / "countyroads_line.shp"
        self.roads_line = gpd.read_file(roads_line_file)
        print(f"   [OK] Loaded {len(self.roads_line):,} road centerlines")
        print(f"   CRS: {self.roads_line.crs}")

        print("\n5. Loading County Roadways (Polygon)...")
        roads_poly_file = self.inputs_path / "County Roadways - Polygon" / "countyroadways_polygon.shp"
        self.roads_poly = gpd.read_file(roads_poly_file)
        print(f"   [OK] Loaded {len(self.roads_poly):,} road polygons")
        print(f"   CRS: {self.roads_poly.crs}")

        print("\n[OK] All data loaded successfully")

    def create_station_buffers(self):
        """
        Create 0.5-mile buffers around each Metro-North station.

        Returns:
            GeoDataFrame with buffered station areas
        """
        print("\n" + "=" * 80)
        print("CREATING STATION BUFFERS")
        print("=" * 80)

        print(f"\nBuffer distance: {self.buffer_distance_miles} miles ({self.buffer_distance_feet:.0f} feet)")

        # Create buffers in NY State Plane (feet)
        buffers = self.stations_nysp.copy()
        buffers['geometry'] = buffers.geometry.buffer(self.buffer_distance_feet)

        print(f"\n[OK] Created {len(buffers)} station buffers")

        # Save buffers as GeoJSON (transform back to WGS84 for web use)
        buffers_wgs84 = buffers.to_crs(self.crs_wgs84)
        output_file = self.output_path / "metro_north_station_buffers.geojson"
        buffers_wgs84.to_file(output_file, driver='GeoJSON')
        print(f"[OK] Saved to: {output_file}")

        return buffers

    def identify_transit_adjacent_roads(self, station_buffers):
        """
        Identify roads within 0.5 miles of any Metro-North station.

        Args:
            station_buffers: GeoDataFrame with station buffer polygons

        Returns:
            GeoDataFrame with transit-adjacent road segments
        """
        print("\n" + "=" * 80)
        print("IDENTIFYING TRANSIT-ADJACENT ROADS")
        print("=" * 80)

        # Create unified buffer zone (merge overlapping buffers)
        print("\n1. Creating unified transit buffer zone...")
        unified_buffer = unary_union(station_buffers.geometry)
        print(f"   [OK] Merged {len(station_buffers)} buffers into unified zone")

        # Spatial join: Find roads within buffer
        print("\n2. Finding road centerlines within buffer...")

        # Use spatial index for performance
        roads_within = self.roads_line[self.roads_line.intersects(unified_buffer)].copy()

        print(f"   [OK] Found {len(roads_within)} road centerlines within 0.5 miles of stations")
        print(f"   ({len(roads_within)/len(self.roads_line)*100:.1f}% of all roads)")

        # Calculate total length
        roads_within['length_feet'] = roads_within.geometry.length
        roads_within['length_miles'] = roads_within['length_feet'] / 5280

        total_length_miles = roads_within['length_miles'].sum()
        print(f"   Total road length: {total_length_miles:.2f} miles")

        # Save transit-adjacent roads
        roads_wgs84 = roads_within.to_crs(self.crs_wgs84)
        output_file = self.output_path / "transit_adjacent_roads.geojson"
        roads_wgs84.to_file(output_file, driver='GeoJSON')
        print(f"\n[OK] Saved to: {output_file}")

        return roads_within

    def analyze_sidewalk_coverage(self, transit_roads):
        """
        Analyze sidewalk coverage for transit-adjacent roads.

        Args:
            transit_roads: GeoDataFrame with transit-adjacent road centerlines

        Returns:
            Tuple of (roads_with_sidewalks, roads_without_sidewalks, statistics)
        """
        print("\n" + "=" * 80)
        print("ANALYZING SIDEWALK COVERAGE")
        print("=" * 80)

        print(f"\nSidewalk matching approach:")
        print(f"  - Buffer each road centerline by {self.sidewalk_buffer_feet} feet")
        print(f"  - Check if sidewalk polygon intersects road buffer")
        print(f"  - Calculate coverage percentage per road segment")

        # Create spatial index for sidewalks (performance optimization)
        print("\n1. Building spatial index for sidewalk matching...")
        sidewalk_sindex = self.sidewalks.sindex
        print(f"   [OK] Spatial index created for {len(self.sidewalks):,} sidewalk polygons")

        # Analyze each road segment
        print("\n2. Analyzing coverage for each road segment...")

        coverage_results = []

        for idx, road in transit_roads.iterrows():
            # Create buffer around road centerline
            road_buffer = road.geometry.buffer(self.sidewalk_buffer_feet)

            # Find potentially intersecting sidewalks using spatial index
            possible_matches_idx = list(sidewalk_sindex.intersection(road_buffer.bounds))
            possible_matches = self.sidewalks.iloc[possible_matches_idx]

            # Check actual intersections
            intersecting_sidewalks = possible_matches[possible_matches.intersects(road_buffer)]

            # Calculate coverage
            has_sidewalk = len(intersecting_sidewalks) > 0
            sidewalk_count = len(intersecting_sidewalks)

            # Calculate intersection length as proxy for coverage
            if has_sidewalk:
                # Union all intersecting sidewalks
                sidewalk_union = unary_union(intersecting_sidewalks.geometry)
                # Calculate intersection with road buffer
                intersection = road_buffer.intersection(sidewalk_union)
                # Estimate coverage percentage
                coverage_length = intersection.length if hasattr(intersection, 'length') else 0
                road_length = road.geometry.length
                coverage_pct = min(100, (coverage_length / road_length) * 100) if road_length > 0 else 0
            else:
                coverage_pct = 0

            coverage_results.append({
                'road_id': idx,
                'road_name': road.get('NAME', 'Unnamed'),
                'road_description': road.get('DESCRIPTIO', ''),
                'road_class': road.get('STRCL_CODE', ''),
                'length_feet': road['length_feet'],
                'length_miles': road['length_miles'],
                'has_sidewalk': has_sidewalk,
                'sidewalk_count': sidewalk_count,
                'coverage_pct': coverage_pct,
                'geometry': road.geometry
            })

        # Create GeoDataFrame with results
        coverage_gdf = gpd.GeoDataFrame(coverage_results, crs=self.crs_nysp)

        print(f"\n3. Coverage Analysis Results:")
        print(f"   Total roads analyzed: {len(coverage_gdf)}")
        print(f"   Roads with sidewalks: {len(coverage_gdf[coverage_gdf['has_sidewalk']])} ({len(coverage_gdf[coverage_gdf['has_sidewalk']])/len(coverage_gdf)*100:.1f}%)")
        print(f"   Roads without sidewalks: {len(coverage_gdf[~coverage_gdf['has_sidewalk']])} ({len(coverage_gdf[~coverage_gdf['has_sidewalk']])/len(coverage_gdf)*100:.1f}%)")

        # Split into covered and uncovered
        roads_with_sidewalks = coverage_gdf[coverage_gdf['has_sidewalk']].copy()
        roads_without_sidewalks = coverage_gdf[~coverage_gdf['has_sidewalk']].copy()

        # Calculate statistics
        total_miles = coverage_gdf['length_miles'].sum()
        covered_miles = roads_with_sidewalks['length_miles'].sum()
        uncovered_miles = roads_without_sidewalks['length_miles'].sum()
        coverage_pct_overall = (covered_miles / total_miles * 100) if total_miles > 0 else 0

        statistics = {
            'total_road_segments': len(coverage_gdf),
            'total_road_miles': round(total_miles, 2),
            'segments_with_sidewalks': len(roads_with_sidewalks),
            'miles_with_sidewalks': round(covered_miles, 2),
            'segments_without_sidewalks': len(roads_without_sidewalks),
            'miles_without_sidewalks': round(uncovered_miles, 2),
            'overall_coverage_pct': round(coverage_pct_overall, 1),
            'avg_coverage_pct_when_present': round(roads_with_sidewalks['coverage_pct'].mean(), 1) if len(roads_with_sidewalks) > 0 else 0
        }

        print(f"\n4. Overall Statistics:")
        print(f"   Total road miles: {statistics['total_road_miles']:.2f}")
        print(f"   Miles with sidewalks: {statistics['miles_with_sidewalks']:.2f} ({coverage_pct_overall:.1f}%)")
        print(f"   Miles without sidewalks: {statistics['miles_without_sidewalks']:.2f}")

        # Save outputs
        print("\n5. Saving analysis outputs...")

        # Roads with sidewalks
        if len(roads_with_sidewalks) > 0:
            roads_with_sw_wgs84 = roads_with_sidewalks.to_crs(self.crs_wgs84)
            output_file = self.output_path / "roads_with_sidewalks.geojson"
            roads_with_sw_wgs84.to_file(output_file, driver='GeoJSON')
            print(f"   [OK] Saved roads with sidewalks: {output_file}")

        # Roads without sidewalks
        if len(roads_without_sidewalks) > 0:
            roads_without_sw_wgs84 = roads_without_sidewalks.to_crs(self.crs_wgs84)
            output_file = self.output_path / "roads_without_sidewalks.geojson"
            roads_without_sw_wgs84.to_file(output_file, driver='GeoJSON')
            print(f"   [OK] Saved roads without sidewalks: {output_file}")

        # Statistics JSON
        stats_file = self.output_path / "sidewalk_coverage_statistics.json"
        with open(stats_file, 'w') as f:
            json.dump(statistics, f, indent=2)
        print(f"   [OK] Saved statistics: {stats_file}")

        return roads_with_sidewalks, roads_without_sidewalks, statistics

    def analyze_coverage_by_station(self, transit_roads, station_buffers):
        """
        Calculate sidewalk coverage statistics for each Metro-North station.

        Args:
            transit_roads: GeoDataFrame with coverage-analyzed roads
            station_buffers: GeoDataFrame with station buffer polygons

        Returns:
            DataFrame with per-station statistics
        """
        print("\n" + "=" * 80)
        print("ANALYZING COVERAGE BY STATION")
        print("=" * 80)

        station_stats = []

        for idx, station in station_buffers.iterrows():
            station_name = station.get('name', f'Station {idx}')
            station_buffer = station.geometry

            # Find roads within this station's buffer
            roads_in_buffer = transit_roads[transit_roads.intersects(station_buffer)].copy()

            if len(roads_in_buffer) == 0:
                # No roads in buffer (unlikely but handle it)
                station_stats.append({
                    'station_name': station_name,
                    'station_id': station.get('id', idx),
                    'total_road_segments': 0,
                    'total_road_miles': 0,
                    'segments_with_sidewalks': 0,
                    'miles_with_sidewalks': 0,
                    'segments_without_sidewalks': 0,
                    'miles_without_sidewalks': 0,
                    'coverage_pct': 0
                })
                continue

            # Calculate statistics for this station
            total_miles = roads_in_buffer['length_miles'].sum()
            roads_with_sw = roads_in_buffer[roads_in_buffer['has_sidewalk']]
            covered_miles = roads_with_sw['length_miles'].sum()
            uncovered_miles = total_miles - covered_miles
            coverage_pct = (covered_miles / total_miles * 100) if total_miles > 0 else 0

            station_stats.append({
                'station_name': station_name,
                'station_id': station.get('id', idx),
                'total_road_segments': len(roads_in_buffer),
                'total_road_miles': round(total_miles, 2),
                'segments_with_sidewalks': len(roads_with_sw),
                'miles_with_sidewalks': round(covered_miles, 2),
                'segments_without_sidewalks': len(roads_in_buffer) - len(roads_with_sw),
                'miles_without_sidewalks': round(uncovered_miles, 2),
                'coverage_pct': round(coverage_pct, 1)
            })

        station_stats_df = pd.DataFrame(station_stats)

        # Sort by coverage percentage (ascending - worst first)
        station_stats_df = station_stats_df.sort_values('coverage_pct')

        print(f"\n[OK] Analyzed coverage for {len(station_stats_df)} stations")
        print(f"\nTop 5 stations with LOWEST coverage:")
        for i, row in station_stats_df.head(5).iterrows():
            print(f"  {row['station_name']}: {row['coverage_pct']:.1f}% ({row['miles_with_sidewalks']:.2f}/{row['total_road_miles']:.2f} miles)")

        print(f"\nTop 5 stations with HIGHEST coverage:")
        for i, row in station_stats_df.tail(5).iterrows():
            print(f"  {row['station_name']}: {row['coverage_pct']:.1f}% ({row['miles_with_sidewalks']:.2f}/{row['total_road_miles']:.2f} miles)")

        # Save station statistics
        output_file = self.output_path / "sidewalk_coverage_by_station.json"
        station_stats_df.to_json(output_file, orient='records', indent=2)
        print(f"\n[OK] Saved station statistics: {output_file}")

        return station_stats_df

    def identify_priority_gaps(self, roads_without_sidewalks, top_n=20):
        """
        Identify priority sidewalk gaps for improvement.

        Ranking criteria:
        - Road length (longer = higher priority)
        - Road class (major roads = higher priority)

        Args:
            roads_without_sidewalks: GeoDataFrame with uncovered road segments
            top_n: Number of top gaps to return

        Returns:
            GeoDataFrame with priority gaps
        """
        print("\n" + "=" * 80)
        print("IDENTIFYING PRIORITY GAPS")
        print("=" * 80)

        if len(roads_without_sidewalks) == 0:
            print("\n[OK] No gaps found - all roads have sidewalk coverage!")
            return gpd.GeoDataFrame()

        # Calculate priority score
        # Higher score = higher priority
        gaps = roads_without_sidewalks.copy()

        # Score based on length (normalize to 0-100)
        max_length = gaps['length_miles'].max()
        gaps['length_score'] = (gaps['length_miles'] / max_length) * 100 if max_length > 0 else 0

        # Score based on road class (if available)
        # STRCL_CODE: Lower numbers typically = more important roads
        if 'road_class' in gaps.columns and gaps['road_class'].notna().any():
            # Invert so lower codes get higher scores
            gaps['class_score'] = 100 - gaps['road_class'].fillna(100)
        else:
            gaps['class_score'] = 50  # Default score if no class info

        # Combined priority score (weighted average)
        gaps['priority_score'] = (gaps['length_score'] * 0.7 + gaps['class_score'] * 0.3)

        # Sort by priority
        gaps = gaps.sort_values('priority_score', ascending=False)

        # Get top N
        priority_gaps = gaps.head(top_n)

        print(f"\nTop {len(priority_gaps)} Priority Gaps:")
        for i, (idx, row) in enumerate(priority_gaps.iterrows(), 1):
            road_name = row['road_name'] if row['road_name'] else 'Unnamed'
            print(f"  {i}. {road_name}: {row['length_miles']:.2f} miles (score: {row['priority_score']:.1f})")

        # Save priority gaps
        priority_gaps_wgs84 = priority_gaps.to_crs(self.crs_wgs84)
        output_file = self.output_path / "priority_sidewalk_gaps.geojson"
        priority_gaps_wgs84.to_file(output_file, driver='GeoJSON')
        print(f"\n[OK] Saved priority gaps: {output_file}")

        # Save as JSON for API
        gaps_json = []
        for idx, row in priority_gaps.iterrows():
            gaps_json.append({
                'road_name': row['road_name'],
                'road_description': row['road_description'],
                'length_miles': round(row['length_miles'], 2),
                'priority_score': round(row['priority_score'], 1),
                'rank': len(gaps_json) + 1
            })

        json_file = self.output_path / "priority_gaps_list.json"
        with open(json_file, 'w') as f:
            json.dump(gaps_json, f, indent=2)
        print(f"[OK] Saved priority gaps list: {json_file}")

        return priority_gaps

    def run_complete_analysis(self):
        """Run the complete transit sidewalk coverage analysis."""
        print("\n" + "=" * 80)
        print("WESTCHESTER TRANSIT SIDEWALK COVERAGE ANALYSIS")
        print("=" * 80)
        print(f"\nProject: Westchester County Data Platform")
        print(f"Analysis: Sidewalk coverage within 0.5 miles of Metro-North stations")
        print(f"Date: 2025-10-17")
        print(f"\nOutput directory: {self.output_path}")

        # Step 1: Load data
        self.load_data()

        # Step 2: Create station buffers
        station_buffers = self.create_station_buffers()

        # Step 3: Identify transit-adjacent roads
        transit_roads = self.identify_transit_adjacent_roads(station_buffers)

        # Step 4: Analyze sidewalk coverage
        roads_with_sw, roads_without_sw, overall_stats = self.analyze_sidewalk_coverage(transit_roads)

        # Combine coverage results for station analysis
        if len(roads_with_sw) > 0 or len(roads_without_sw) > 0:
            import pandas as pd
            coverage_analyzed_roads = pd.concat([roads_with_sw, roads_without_sw], ignore_index=True)
            coverage_analyzed_roads = gpd.GeoDataFrame(coverage_analyzed_roads, crs=self.crs_nysp)
        else:
            coverage_analyzed_roads = gpd.GeoDataFrame(columns=['has_sidewalk', 'length_miles'], crs=self.crs_nysp)

        # Step 5: Analyze coverage by station
        station_stats = self.analyze_coverage_by_station(coverage_analyzed_roads, station_buffers)

        # Step 6: Identify priority gaps
        priority_gaps = self.identify_priority_gaps(roads_without_sw)

        # Summary
        print("\n" + "=" * 80)
        print("ANALYSIS COMPLETE")
        print("=" * 80)
        print(f"\nOverall Results:")
        print(f"  Total Metro-North Stations: {len(self.stations)}")
        print(f"  Total Road Miles Analyzed: {overall_stats['total_road_miles']}")
        print(f"  Miles with Sidewalks: {overall_stats['miles_with_sidewalks']} ({overall_stats['overall_coverage_pct']:.1f}%)")
        print(f"  Miles without Sidewalks: {overall_stats['miles_without_sidewalks']}")
        print(f"  Priority Gaps Identified: {len(priority_gaps)}")

        print(f"\nOutput Files Generated:")
        for file in sorted(self.output_path.glob("*")):
            if file.is_file():
                size_kb = file.stat().st_size / 1024
                print(f"  - {file.name} ({size_kb:.1f} KB)")

        print(f"\n[OK] All analysis outputs saved to: {self.output_path}")

        return {
            'overall_statistics': overall_stats,
            'station_statistics': station_stats,
            'priority_gaps': priority_gaps,
            'output_directory': str(self.output_path)
        }


def main():
    """Main execution function."""
    analyzer = TransitSidewalkAnalyzer()
    results = analyzer.run_complete_analysis()
    return results


if __name__ == "__main__":
    main()
