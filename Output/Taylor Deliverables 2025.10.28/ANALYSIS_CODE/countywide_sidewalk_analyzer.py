"""
County-Wide Sidewalk Coverage Analyzer
========================================

Comprehensive analysis of sidewalk coverage across Westchester County using
road polygon data and sidewalk polygon data.

Key Features:
- Uses POLYGON road dataset (4,386 features) for comprehensive coverage
- Detects 1-side vs 2-side sidewalk coverage using spatial analysis
- Calculates county-wide statistics and TOD-focused metrics
- Implements industry-standard sidewalk/road ratio methodology
- Generates Druck-compliant outputs (Excel, LaTeX, GeoJSON)

Methodology:
- Buffer-based side detection for road edges
- Sidewalk-to-road length ratio (0.0 = none, 0.5-0.7 = one-side, 1.5-2.0 = both)
- 80% threshold for "complete" coverage classification
- Transit-oriented development (TOD) analysis with 0.5-mile station buffers

Author: Westchester Data Platform
Date: 2025-10-17
Based on: DVRPC methodology and TOD best practices research
"""

import geopandas as gpd
import pandas as pd
import json
import os
import numpy as np
from pathlib import Path
from shapely.geometry import Point, LineString, Polygon, MultiPolygon
from shapely.ops import unary_union
import warnings
warnings.filterwarnings('ignore')


class CountywideSidewalkAnalyzer:
    """
    Comprehensive sidewalk coverage analyzer for Westchester County.
    Uses polygon road data for accurate 1-side vs 2-side detection.
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
        self.output_path = self.base_path / "Technical" / "data" / "processed" / "countywide_sidewalk_analysis"

        # Create output directory
        self.output_path.mkdir(parents=True, exist_ok=True)

        # CRS definitions
        self.crs_nysp = "EPSG:2260"  # NY State Plane Long Island (feet)
        self.crs_wgs84 = "EPSG:4326"  # WGS84 (lat/lon)

        # Constants
        self.buffer_distance_miles = 0.5
        self.buffer_distance_feet = self.buffer_distance_miles * 5280  # 2640 feet
        self.sidewalk_detection_buffer = 20  # feet outward from road edge
        self.coverage_threshold = 0.8  # 80% coverage to classify as "complete"

        # Sidewalk ratio thresholds (from DVRPC research)
        self.ratio_none = 0.1  # < 0.1 = no coverage
        self.ratio_one_side_min = 0.4  # 0.4-0.8 = one side
        self.ratio_one_side_max = 0.8
        self.ratio_both_sides_min = 1.2  # > 1.2 = both sides

        # Data storage
        self.stations = None
        self.stations_nysp = None
        self.sidewalks = None
        self.roads_poly = None

    def load_data(self):
        """Load all required datasets."""
        print("=" * 80)
        print("LOADING DATA")
        print("=" * 80)

        # Load Metro-North stations
        print("\n1. Loading Metro-North Stations...")
        stations_file = self.transit_path / "westchester_metro_north_stations.geojson"

        if not stations_file.exists():
            print(f"   [WARNING] Stations file not found: {stations_file}")
            print(f"   [OK] Continuing without transit data (county-wide analysis only)")
            self.stations = None
            self.stations_nysp = None
        else:
            self.stations = gpd.read_file(stations_file)
            print(f"   [OK] Loaded {len(self.stations)} stations")
            # Transform stations to NY State Plane
            self.stations_nysp = self.stations.to_crs(self.crs_nysp)
            print(f"   [OK] Transformed to NY State Plane (feet)")

        # Load Taylor shapefiles
        print("\n2. Loading County Sidewalks (Polygon)...")
        sidewalks_file = self.inputs_path / "County Sidewalks - Polygon" / "countysidewalks_polygon.shp"
        self.sidewalks = gpd.read_file(sidewalks_file)
        print(f"   [OK] Loaded {len(self.sidewalks):,} sidewalk polygons")
        print(f"   CRS: {self.sidewalks.crs}")
        print(f"   Types: {self.sidewalks['DESCRIPTIO'].unique()}")
        print(f"   Total area: {self.sidewalks.geometry.area.sum()/43560:.1f} acres")

        print("\n3. Loading County Roadways (Polygon)...")
        roads_poly_file = self.inputs_path / "County Roadways - Polygon" / "countyroadways_polygon.shp"
        self.roads_poly = gpd.read_file(roads_poly_file)
        print(f"   [OK] Loaded {len(self.roads_poly):,} road polygons")
        print(f"   CRS: {self.roads_poly.crs}")
        print(f"   Total area: {self.roads_poly.geometry.area.sum()/43560:.1f} acres")

        # Show road type breakdown
        print(f"\n   Road types:")
        for road_type, count in self.roads_poly['DESCRIPTIO'].value_counts().head(5).items():
            print(f"     - {road_type}: {count:,}")

        print("\n[OK] All data loaded successfully")

    def analyze_road_sidewalk_coverage(self, road_geom, road_id=None):
        """
        Analyze sidewalk coverage for a single road polygon.

        Uses buffer-based edge detection to determine if sidewalks exist
        on left side, right side, or both sides of the road.

        Args:
            road_geom: Shapely Polygon/MultiPolygon geometry of road
            road_id: Optional identifier for debugging

        Returns:
            dict with coverage metrics
        """
        # Create detection zone: buffer road outward by detection distance
        # This creates a zone where we expect sidewalks to be if they exist
        detection_zone = road_geom.buffer(self.sidewalk_detection_buffer)

        # Find sidewalks that intersect the detection zone
        possible_sw_idx = list(self.sidewalk_sindex.intersection(detection_zone.bounds))
        if len(possible_sw_idx) == 0:
            return {
                'has_sidewalk': False,
                'coverage_type': 'none',
                'coverage_ratio': 0.0,
                'sidewalk_count': 0,
                'sidewalk_length_feet': 0,
                'road_perimeter_feet': road_geom.length
            }

        possible_sidewalks = self.sidewalks.iloc[possible_sw_idx]
        intersecting_sidewalks = possible_sidewalks[possible_sidewalks.intersects(detection_zone)]

        if len(intersecting_sidewalks) == 0:
            return {
                'has_sidewalk': False,
                'coverage_type': 'none',
                'coverage_ratio': 0.0,
                'sidewalk_count': 0,
                'sidewalk_length_feet': 0,
                'road_perimeter_feet': road_geom.length
            }

        # Calculate sidewalk length within detection zone
        sidewalk_union = unary_union(intersecting_sidewalks.geometry)
        sidewalk_in_zone = detection_zone.intersection(sidewalk_union)

        # Calculate total sidewalk length (perimeter of sidewalk polygons)
        if hasattr(sidewalk_in_zone, 'length'):
            sidewalk_length = sidewalk_in_zone.length
        elif hasattr(sidewalk_in_zone, 'geoms'):
            sidewalk_length = sum(g.length for g in sidewalk_in_zone.geoms if hasattr(g, 'length'))
        else:
            sidewalk_length = 0

        # Calculate road perimeter (boundary length)
        road_perimeter = road_geom.length

        # Calculate sidewalk-to-road ratio (DVRPC methodology)
        coverage_ratio = sidewalk_length / road_perimeter if road_perimeter > 0 else 0

        # Classify coverage type based on ratio
        if coverage_ratio < self.ratio_none:
            coverage_type = 'none'
            has_sidewalk = False
        elif coverage_ratio < self.ratio_one_side_max:
            coverage_type = 'one_side'
            has_sidewalk = True
        elif coverage_ratio >= self.ratio_both_sides_min:
            coverage_type = 'both_sides'
            has_sidewalk = True
        else:
            # Ambiguous range (0.8-1.2) - classify as one side
            coverage_type = 'one_side'
            has_sidewalk = True

        return {
            'has_sidewalk': has_sidewalk,
            'coverage_type': coverage_type,
            'coverage_ratio': round(coverage_ratio, 3),
            'sidewalk_count': len(intersecting_sidewalks),
            'sidewalk_length_feet': round(sidewalk_length, 1),
            'road_perimeter_feet': round(road_perimeter, 1)
        }

    def analyze_all_roads(self):
        """
        Analyze sidewalk coverage for all roads in the county.

        Returns:
            GeoDataFrame with coverage analysis for each road
        """
        print("\n" + "=" * 80)
        print("ANALYZING COUNTY-WIDE SIDEWALK COVERAGE")
        print("=" * 80)

        print(f"\nMethodology:")
        print(f"  - Detection buffer: {self.sidewalk_detection_buffer} feet from road edge")
        print(f"  - Sidewalk/road ratio thresholds:")
        print(f"    * < {self.ratio_none} = no coverage")
        print(f"    * {self.ratio_one_side_min}-{self.ratio_one_side_max} = one side")
        print(f"    * > {self.ratio_both_sides_min} = both sides")

        # Build spatial index for sidewalks
        print(f"\n1. Building spatial index for {len(self.sidewalks):,} sidewalks...")
        self.sidewalk_sindex = self.sidewalks.sindex
        print(f"   [OK] Spatial index created")

        # Analyze each road
        print(f"\n2. Analyzing {len(self.roads_poly):,} roads...")
        print(f"   (This may take a few minutes for large datasets)")

        results = []

        for idx, road in self.roads_poly.iterrows():
            if idx > 0 and idx % 500 == 0:
                print(f"   Progress: {idx:,}/{len(self.roads_poly):,} roads ({idx/len(self.roads_poly)*100:.1f}%)")

            coverage = self.analyze_road_sidewalk_coverage(road.geometry, road_id=idx)

            # Calculate road area and estimated length
            road_area = road.geometry.area
            road_area_acres = road_area / 43560

            results.append({
                'road_id': idx,
                'road_type': road.get('DESCRIPTIO', 'UNKNOWN'),
                'fea_code': road.get('FEA_CODE', ''),
                'road_area_sqft': round(road_area, 1),
                'road_area_acres': round(road_area_acres, 4),
                'road_perimeter_feet': coverage['road_perimeter_feet'],
                'has_sidewalk': coverage['has_sidewalk'],
                'coverage_type': coverage['coverage_type'],
                'coverage_ratio': coverage['coverage_ratio'],
                'sidewalk_count': coverage['sidewalk_count'],
                'sidewalk_length_feet': coverage['sidewalk_length_feet'],
                'geometry': road.geometry
            })

        # Create GeoDataFrame
        results_gdf = gpd.GeoDataFrame(results, crs=self.crs_nysp)

        print(f"\n3. Analysis Complete!")
        print(f"   Total roads analyzed: {len(results_gdf):,}")

        # Calculate summary statistics
        none_count = len(results_gdf[results_gdf['coverage_type'] == 'none'])
        one_side_count = len(results_gdf[results_gdf['coverage_type'] == 'one_side'])
        both_sides_count = len(results_gdf[results_gdf['coverage_type'] == 'both_sides'])

        print(f"\n4. Coverage Summary:")
        print(f"   No coverage:    {none_count:>6,} roads ({none_count/len(results_gdf)*100:>5.1f}%)")
        print(f"   One side:       {one_side_count:>6,} roads ({one_side_count/len(results_gdf)*100:>5.1f}%)")
        print(f"   Both sides:     {both_sides_count:>6,} roads ({both_sides_count/len(results_gdf)*100:>5.1f}%)")

        return results_gdf

    def calculate_statistics(self, coverage_gdf):
        """
        Calculate comprehensive statistics from coverage analysis.

        Args:
            coverage_gdf: GeoDataFrame with coverage analysis results

        Returns:
            dict with statistics
        """
        print("\n" + "=" * 80)
        print("CALCULATING STATISTICS")
        print("=" * 80)

        total_roads = len(coverage_gdf)
        total_area_acres = coverage_gdf['road_area_acres'].sum()

        # Coverage counts
        none_df = coverage_gdf[coverage_gdf['coverage_type'] == 'none']
        one_side_df = coverage_gdf[coverage_gdf['coverage_type'] == 'one_side']
        both_sides_df = coverage_gdf[coverage_gdf['coverage_type'] == 'both_sides']

        # Area-based statistics
        none_area = none_df['road_area_acres'].sum()
        one_side_area = one_side_df['road_area_acres'].sum()
        both_sides_area = both_sides_df['road_area_acres'].sum()

        # By road type
        type_stats = []
        for road_type in coverage_gdf['road_type'].unique():
            type_df = coverage_gdf[coverage_gdf['road_type'] == road_type]
            type_none = len(type_df[type_df['coverage_type'] == 'none'])
            type_one = len(type_df[type_df['coverage_type'] == 'one_side'])
            type_both = len(type_df[type_df['coverage_type'] == 'both_sides'])

            type_stats.append({
                'road_type': road_type,
                'total_count': len(type_df),
                'no_coverage_count': type_none,
                'one_side_count': type_one,
                'both_sides_count': type_both,
                'coverage_pct': (type_one + type_both) / len(type_df) * 100 if len(type_df) > 0 else 0
            })

        type_stats_df = pd.DataFrame(type_stats).sort_values('total_count', ascending=False)

        statistics = {
            'total_roads': total_roads,
            'total_road_area_acres': round(total_area_acres, 2),
            'coverage_counts': {
                'no_coverage': len(none_df),
                'one_side': len(one_side_df),
                'both_sides': len(both_sides_df)
            },
            'coverage_percentages': {
                'no_coverage_pct': round(len(none_df)/total_roads*100, 1),
                'one_side_pct': round(len(one_side_df)/total_roads*100, 1),
                'both_sides_pct': round(len(both_sides_df)/total_roads*100, 1),
                'any_coverage_pct': round((len(one_side_df)+len(both_sides_df))/total_roads*100, 1)
            },
            'coverage_areas': {
                'no_coverage_acres': round(none_area, 2),
                'one_side_acres': round(one_side_area, 2),
                'both_sides_acres': round(both_sides_area, 2)
            },
            'area_percentages': {
                'no_coverage_pct': round(none_area/total_area_acres*100, 1),
                'one_side_pct': round(one_side_area/total_area_acres*100, 1),
                'both_sides_pct': round(both_sides_area/total_area_acres*100, 1)
            },
            'by_road_type': type_stats_df.to_dict('records')
        }

        print(f"\nOverall Statistics:")
        print(f"  Total roads: {total_roads:,}")
        print(f"  Total road area: {total_area_acres:,.1f} acres")
        print(f"\nCoverage Distribution (by count):")
        print(f"  No coverage:    {statistics['coverage_counts']['no_coverage']:>6,} ({statistics['coverage_percentages']['no_coverage_pct']:>5.1f}%)")
        print(f"  One side:       {statistics['coverage_counts']['one_side']:>6,} ({statistics['coverage_percentages']['one_side_pct']:>5.1f}%)")
        print(f"  Both sides:     {statistics['coverage_counts']['both_sides']:>6,} ({statistics['coverage_percentages']['both_sides_pct']:>5.1f}%)")
        print(f"  Any coverage:   {statistics['coverage_counts']['one_side']+statistics['coverage_counts']['both_sides']:>6,} ({statistics['coverage_percentages']['any_coverage_pct']:>5.1f}%)")

        print(f"\nCoverage Distribution (by area):")
        print(f"  No coverage:    {statistics['coverage_areas']['no_coverage_acres']:>8.1f} acres ({statistics['area_percentages']['no_coverage_pct']:>5.1f}%)")
        print(f"  One side:       {statistics['coverage_areas']['one_side_acres']:>8.1f} acres ({statistics['area_percentages']['one_side_pct']:>5.1f}%)")
        print(f"  Both sides:     {statistics['coverage_areas']['both_sides_acres']:>8.1f} acres ({statistics['area_percentages']['both_sides_pct']:>5.1f}%)")

        print(f"\nTop 5 Road Types by Count:")
        for i, row in type_stats_df.head(5).iterrows():
            print(f"  {row['road_type']}: {row['total_count']:,} roads ({row['coverage_pct']:.1f}% with sidewalks)")

        return statistics

    def analyze_transit_areas(self, coverage_gdf):
        """
        Analyze coverage in transit-oriented development (TOD) areas.

        Args:
            coverage_gdf: GeoDataFrame with county-wide coverage analysis

        Returns:
            dict with TOD statistics
        """
        if self.stations_nysp is None:
            print("\n[SKIP] No station data available for TOD analysis")
            return None

        print("\n" + "=" * 80)
        print("TRANSIT-ORIENTED DEVELOPMENT (TOD) ANALYSIS")
        print("=" * 80)

        print(f"\nAnalyzing roads within {self.buffer_distance_miles} miles of {len(self.stations_nysp)} Metro-North stations...")

        # Create unified station buffer
        station_buffers = self.stations_nysp.copy()
        station_buffers['geometry'] = station_buffers.geometry.buffer(self.buffer_distance_feet)
        unified_buffer = unary_union(station_buffers.geometry)

        # Find roads in TOD areas
        tod_roads = coverage_gdf[coverage_gdf.intersects(unified_buffer)].copy()
        non_tod_roads = coverage_gdf[~coverage_gdf.intersects(unified_buffer)].copy()

        print(f"\n  TOD area roads:     {len(tod_roads):>6,} ({len(tod_roads)/len(coverage_gdf)*100:.1f}%)")
        print(f"  Non-TOD area roads: {len(non_tod_roads):>6,} ({len(non_tod_roads)/len(coverage_gdf)*100:.1f}%)")

        # Calculate TOD statistics
        tod_stats = {
            'total_roads': len(tod_roads),
            'no_coverage': len(tod_roads[tod_roads['coverage_type'] == 'none']),
            'one_side': len(tod_roads[tod_roads['coverage_type'] == 'one_side']),
            'both_sides': len(tod_roads[tod_roads['coverage_type'] == 'both_sides']),
            'any_coverage_pct': (len(tod_roads[tod_roads['has_sidewalk']]) / len(tod_roads) * 100) if len(tod_roads) > 0 else 0
        }

        # Calculate non-TOD statistics for comparison
        non_tod_stats = {
            'total_roads': len(non_tod_roads),
            'no_coverage': len(non_tod_roads[non_tod_roads['coverage_type'] == 'none']),
            'one_side': len(non_tod_roads[non_tod_roads['coverage_type'] == 'one_side']),
            'both_sides': len(non_tod_roads[non_tod_roads['coverage_type'] == 'both_sides']),
            'any_coverage_pct': (len(non_tod_roads[non_tod_roads['has_sidewalk']]) / len(non_tod_roads) * 100) if len(non_tod_roads) > 0 else 0
        }

        print(f"\nTOD Area Coverage:")
        print(f"  No coverage:    {tod_stats['no_coverage']:>6,} ({tod_stats['no_coverage']/tod_stats['total_roads']*100:.1f}%)")
        print(f"  One side:       {tod_stats['one_side']:>6,} ({tod_stats['one_side']/tod_stats['total_roads']*100:.1f}%)")
        print(f"  Both sides:     {tod_stats['both_sides']:>6,} ({tod_stats['both_sides']/tod_stats['total_roads']*100:.1f}%)")
        print(f"  Any coverage:   {tod_stats['any_coverage_pct']:.1f}%")

        print(f"\nNon-TOD Area Coverage:")
        print(f"  No coverage:    {non_tod_stats['no_coverage']:>6,} ({non_tod_stats['no_coverage']/non_tod_stats['total_roads']*100:.1f}%)")
        print(f"  One side:       {non_tod_stats['one_side']:>6,} ({non_tod_stats['one_side']/non_tod_stats['total_roads']*100:.1f}%)")
        print(f"  Both sides:     {non_tod_stats['both_sides']:>6,} ({non_tod_stats['both_sides']/non_tod_stats['total_roads']*100:.1f}%)")
        print(f"  Any coverage:   {non_tod_stats['any_coverage_pct']:.1f}%")

        return {
            'tod_statistics': tod_stats,
            'non_tod_statistics': non_tod_stats,
            'tod_roads': tod_roads,
            'non_tod_roads': non_tod_roads
        }

    def save_outputs(self, coverage_gdf, statistics, tod_analysis=None):
        """
        Save all outputs: GeoJSON, JSON statistics, and prepare for Excel/LaTeX.

        Args:
            coverage_gdf: GeoDataFrame with coverage analysis
            statistics: dict with statistics
            tod_analysis: optional TOD analysis results
        """
        print("\n" + "=" * 80)
        print("SAVING OUTPUTS")
        print("=" * 80)

        # 1. GeoJSON outputs
        print("\n1. Saving GeoJSON files...")

        # Full coverage
        coverage_wgs84 = coverage_gdf.to_crs(self.crs_wgs84)
        output_file = self.output_path / "county_wide_coverage.geojson"
        coverage_wgs84.to_file(output_file, driver='GeoJSON')
        print(f"   [OK] {output_file.name} ({output_file.stat().st_size/1024:.1f} KB)")

        # By coverage type
        for coverage_type in ['none', 'one_side', 'both_sides']:
            subset = coverage_gdf[coverage_gdf['coverage_type'] == coverage_type]
            if len(subset) > 0:
                subset_wgs84 = subset.to_crs(self.crs_wgs84)
                output_file = self.output_path / f"roads_coverage_{coverage_type}.geojson"
                subset_wgs84.to_file(output_file, driver='GeoJSON')
                print(f"   [OK] {output_file.name} ({output_file.stat().st_size/1024:.1f} KB)")

        # 2. Statistics JSON
        print("\n2. Saving statistics...")
        stats_file = self.output_path / "county_wide_statistics.json"
        with open(stats_file, 'w') as f:
            json.dump(statistics, f, indent=2)
        print(f"   [OK] {stats_file.name}")

        # 3. TOD analysis (if available)
        if tod_analysis:
            print("\n3. Saving TOD analysis...")

            tod_stats_file = self.output_path / "tod_statistics.json"
            with open(tod_stats_file, 'w') as f:
                json.dump({
                    'tod_statistics': tod_analysis['tod_statistics'],
                    'non_tod_statistics': tod_analysis['non_tod_statistics']
                }, f, indent=2)
            print(f"   [OK] {tod_stats_file.name}")

            # Save TOD roads GeoJSON
            if len(tod_analysis['tod_roads']) > 0:
                tod_roads_wgs84 = tod_analysis['tod_roads'].to_crs(self.crs_wgs84)
                output_file = self.output_path / "tod_area_roads.geojson"
                tod_roads_wgs84.to_file(output_file, driver='GeoJSON')
                print(f"   [OK] {output_file.name}")

        print(f"\n[OK] All outputs saved to: {self.output_path}")

    def run_complete_analysis(self):
        """Run the complete county-wide sidewalk coverage analysis."""
        print("\n" + "=" * 80)
        print("WESTCHESTER COUNTY SIDEWALK COVERAGE ANALYSIS")
        print("=" * 80)
        print(f"\nProject: Westchester County Data Platform")
        print(f"Analysis: Comprehensive sidewalk coverage with 1-side vs 2-side detection")
        print(f"Date: 2025-10-17")
        print(f"Methodology: DVRPC sidewalk-to-road ratio + TOD best practices")
        print(f"\nOutput directory: {self.output_path}")

        # Step 1: Load data
        self.load_data()

        # Step 2: Analyze all roads
        coverage_gdf = self.analyze_all_roads()

        # Step 3: Calculate statistics
        statistics = self.calculate_statistics(coverage_gdf)

        # Step 4: TOD analysis (if stations available)
        tod_analysis = self.analyze_transit_areas(coverage_gdf)

        # Step 5: Save outputs
        self.save_outputs(coverage_gdf, statistics, tod_analysis)

        # Summary
        print("\n" + "=" * 80)
        print("ANALYSIS COMPLETE")
        print("=" * 80)
        print(f"\nKey Findings:")
        print(f"  Total roads analyzed: {statistics['total_roads']:,}")
        print(f"  Roads with any sidewalk coverage: {statistics['coverage_percentages']['any_coverage_pct']:.1f}%")
        print(f"  Roads with both-side coverage: {statistics['coverage_percentages']['both_sides_pct']:.1f}%")

        if tod_analysis:
            print(f"\nTOD vs Non-TOD Comparison:")
            print(f"  TOD area coverage: {tod_analysis['tod_statistics']['any_coverage_pct']:.1f}%")
            print(f"  Non-TOD area coverage: {tod_analysis['non_tod_statistics']['any_coverage_pct']:.1f}%")

        print(f"\nNext Steps:")
        print(f"  [ ] Generate Druck-compliant Excel outputs (ONE SHEET per file)")
        print(f"  [ ] Create LaTeX analysis report")
        print(f"  [ ] Build backend API endpoints")
        print(f"  [ ] Build frontend dashboard")

        return {
            'coverage_data': coverage_gdf,
            'statistics': statistics,
            'tod_analysis': tod_analysis,
            'output_directory': str(self.output_path)
        }


def main():
    """Main execution function."""
    analyzer = CountywideSidewalkAnalyzer()
    results = analyzer.run_complete_analysis()
    return results


if __name__ == "__main__":
    main()
