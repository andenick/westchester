#!/usr/bin/env python3
"""
Convert GeoJSON tax parcel data to CSV format for the tax parcel parser
"""

import json
import csv
from pathlib import Path

def convert_geojson_to_csv():
    # Input and output paths
    geojson_file = Path("D:/Arcanum/Projects/Westchester2_Final/Westchester/Technical/data/raw/WCGIS.tax-parcels.geojson")
    csv_file = Path("D:/Arcanum/Projects/Westchester2_Final/Westchester/Technical/data/raw/WCGIS.tax-parcels.csv")

    print(f"Reading GeoJSON from: {geojson_file}")

    # Load GeoJSON
    with open(geojson_file, 'r', encoding='utf-8') as f:
        geojson_data = json.load(f)

    features = geojson_data.get('features', [])
    print(f"Found {len(features)} parcel features")

    if not features:
        print("No features found in GeoJSON!")
        return

    # Get all unique property fields from the first feature
    sample_props = features[0].get('properties', {})
    fieldnames = list(sample_props.keys())

    # Add basic geometry info
    fieldnames.extend(['geometry_type', 'coordinates'])

    print(f"Fields found: {fieldnames}")

    # Write CSV
    print(f"Writing CSV to: {csv_file}")

    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for i, feature in enumerate(features):
            if i % 50000 == 0:
                print(f"Processing feature {i:,}/{len(features):,}")

            props = feature.get('properties', {})
            geometry = feature.get('geometry', {})

            # Add geometry info
            props['geometry_type'] = geometry.get('type', '')
            coords = geometry.get('coordinates', [])
            props['coordinates'] = str(coords) if coords else ''

            writer.writerow(props)

    print(f"✅ Successfully converted {len(features):,} parcels to CSV")
    print(f"CSV file size: {csv_file.stat().st_size:,} bytes")

if __name__ == "__main__":
    convert_geojson_to_csv()