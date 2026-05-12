#!/usr/bin/env python3
"""
Prepare Westchester v5.3 sidewalk coverage data for web mapping.

Reads the definitive v5.3 GeoJSON (EPSG:2260, 62MB, 60,626 features),
reprojects to EPSG:4326, simplifies geometries, strips excess precision,
and exports an optimized GeoJSON + summary statistics JSON for the frontend.
"""

import geopandas as gpd
import json
import os
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
INPUT_FILE = PROJECT_ROOT / "TAYLOR_DELIVERABLES_v5.3" / "westchester_sidewalk_v5.3.geojson"
OUTPUT_DIR = PROJECT_ROOT / "Westchester" / "Technical" / "src" / "frontend" / "public" / "data"

KEEP_COLUMNS = ["road_id", "coverage_type", "left_pct", "right_pct", "road_length_ft"]
SIMPLIFY_TOLERANCE = 0.00005  # ~5m at 41N latitude
COORDINATE_PRECISION = 6


def round_coords(geom, precision: int):
    """Round all coordinates in a geometry to given decimal places."""
    from shapely.ops import transform

    def _round(x, y, z=None):
        if z is not None:
            return tuple(round(v, precision) for v in [x, y, z])
        return round(x, precision), round(y, precision)

    return transform(_round, geom)


def prepare_geojson() -> gpd.GeoDataFrame:
    """Load, reproject, simplify, and clean the v5.3 data."""
    print(f"Loading {INPUT_FILE}...")
    t0 = time.time()
    gdf = gpd.read_file(str(INPUT_FILE))
    print(f"  Loaded {len(gdf):,} features in {time.time() - t0:.1f}s")
    print(f"  CRS: {gdf.crs}")
    print(f"  Columns: {list(gdf.columns)}")

    print("Reprojecting EPSG:2260 -> EPSG:4326...")
    gdf = gdf.to_crs(epsg=4326)

    print(f"Simplifying geometries (tolerance={SIMPLIFY_TOLERANCE})...")
    gdf["geometry"] = gdf["geometry"].simplify(SIMPLIFY_TOLERANCE, preserve_topology=True)

    print(f"Rounding coordinates to {COORDINATE_PRECISION} decimal places...")
    gdf["geometry"] = gdf["geometry"].apply(lambda g: round_coords(g, COORDINATE_PRECISION))

    print("Removing empty/invalid geometries...")
    before = len(gdf)
    gdf = gdf[~gdf.is_empty & gdf.is_valid].copy()
    after = len(gdf)
    if before != after:
        print(f"  Removed {before - after} invalid features")

    available = [c for c in KEEP_COLUMNS if c in gdf.columns]
    gdf = gdf[available + ["geometry"]]
    print(f"  Kept columns: {available}")

    return gdf


def export_geojson(gdf: gpd.GeoDataFrame) -> Path:
    """Export optimized GeoJSON."""
    out_path = OUTPUT_DIR / "sidewalk_coverage_v5.3.geojson"
    print(f"Exporting optimized GeoJSON to {out_path}...")
    t0 = time.time()
    gdf.to_file(str(out_path), driver="GeoJSON")
    size_mb = os.path.getsize(out_path) / (1024 * 1024)
    print(f"  Written {len(gdf):,} features, {size_mb:.1f} MB in {time.time() - t0:.1f}s")
    return out_path


def export_stats(gdf: gpd.GeoDataFrame) -> Path:
    """Generate summary statistics JSON for the dashboard."""
    out_path = OUTPUT_DIR / "sidewalk_stats_v5.3.json"

    counts = gdf["coverage_type"].value_counts().to_dict()
    total = len(gdf)

    total_miles = gdf["road_length_ft"].sum() / 5280 if "road_length_ft" in gdf.columns else 0
    miles_by_type = {}
    if "road_length_ft" in gdf.columns:
        for ctype in ["none", "one_side", "both_sides"]:
            subset = gdf[gdf["coverage_type"] == ctype]
            miles_by_type[ctype] = round(subset["road_length_ft"].sum() / 5280, 1)

    stats = {
        "version": "5.3",
        "validation_accuracy": "100% (17/17)",
        "total_roads": total,
        "total_road_miles": round(total_miles, 1),
        "coverage_counts": {
            "none": counts.get("none", 0),
            "one_side": counts.get("one_side", 0),
            "both_sides": counts.get("both_sides", 0),
        },
        "coverage_percentages": {
            "none": round(counts.get("none", 0) / total * 100, 1),
            "one_side": round(counts.get("one_side", 0) / total * 100, 1),
            "both_sides": round(counts.get("both_sides", 0) / total * 100, 1),
        },
        "coverage_miles": miles_by_type,
        "methodology": {
            "buffer_distance_ft": 35,
            "detection_threshold_pct": 0.35,
            "sampling_interval_ft": 10,
            "source_roads": "roads2.shp (60,676 segments)",
            "source_sidewalks": "countysidewalks_polygon.shp (77,558 polygons)",
            "approach": "DVRPC-inspired, engineering-optimized",
        },
    }

    print(f"Exporting statistics to {out_path}...")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)
    print(f"  Coverage: {stats['coverage_percentages']}")

    return out_path


def main():
    print("=" * 60)
    print("Westchester v5.3 Sidewalk Data — Web Optimization Pipeline")
    print("=" * 60)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    gdf = prepare_geojson()
    geojson_path = export_geojson(gdf)
    stats_path = export_stats(gdf)

    input_size = os.path.getsize(INPUT_FILE) / (1024 * 1024)
    output_size = os.path.getsize(geojson_path) / (1024 * 1024)
    reduction = (input_size - output_size) / input_size * 100

    print()
    print("=" * 60)
    print("Pipeline Complete")
    print(f"  Input:  {input_size:.1f} MB ({INPUT_FILE.name})")
    print(f"  Output: {output_size:.1f} MB ({geojson_path.name})")
    print(f"  Reduction: {reduction:.1f}%")
    print(f"  Stats:  {stats_path.name}")
    print(f"  Features: {len(gdf):,}")
    print("=" * 60)


if __name__ == "__main__":
    main()
