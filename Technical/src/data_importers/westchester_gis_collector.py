#!/usr/bin/env python3
"""
Westchester County GIS Open Data Portal Collector
Collects geospatial datasets from Westchester County's official GIS portal
Provides access to authoritative county geographic data
"""

import os
import sys
import json
import time
import requests
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import geopandas as gpd
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WestchesterGISCollector:
    """Collects geospatial data from Westchester County GIS Open Data Portal"""

    def __init__(self, output_dir: str = None):
        self.output_dir = Path(output_dir or "data/raw/westchester_gis")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Westchester County GIS Portal endpoints
        self.gis_base_url = "https://gis.westchestergov.com/arcgis/rest/services"
        self.open_data_url = "https://opendata.westchestergov.com"

        # Known GIS datasets for Westchester County
        self.known_datasets = {
            "parcels": {
                "url": "https://gis.westchestergov.com/arcgis/rest/services/OpenData/FeatureServer/0",
                "name": "Tax Parcels",
                "description": "Property tax parcels with assessment information"
            },
            "buildings": {
                "url": "https://gis.westchestergov.com/arcgis/rest/services/OpenData/FeatureServer/1",
                "name": "Building Footprints",
                "description": "Building outlines and structures"
            },
            "zoning": {
                "url": "https://gis.westchestergov.com/arcgis/rest/services/OpenData/FeatureServer/2",
                "name": "Zoning Districts",
                "description": "Zoning boundaries and regulations"
            },
            "flood_zones": {
                "url": "https://gis.westchestergov.com/arcgis/rest/services/OpenData/FeatureServer/3",
                "name": "Flood Zones",
                "description": "FEMA flood hazard areas"
            },
            "voting_precincts": {
                "url": "https://gis.westchestergov.com/arcgis/rest/services/OpenData/FeatureServer/4",
                "name": "Voting Precincts",
                "description": "Election precinct boundaries"
            },
            "school_districts": {
                "url": "https://gis.westchestergov.com/arcgis/rest/services/OpenData/FeatureServer/5",
                "name": "School Districts",
                "description": "Public school district boundaries"
            },
            "hydrology": {
                "url": "https://gis.westchestergov.com/arcgis/rest/services/OpenData/FeatureServer/6",
                "name": "Hydrology",
                "description": "Water bodies, streams, and drainage"
            },
            "contours": {
                "url": "https://gis.westchestergov.com/arcgis/rest/services/OpenData/FeatureServer/7",
                "name": "Topographic Contours",
                "description": "Elevation contour lines"
            },
            "roads": {
                "url": "https://gis.westchestergov.com/arcgis/rest/services/OpenData/FeatureServer/8",
                "name": "Road Centerlines",
                "description": "Public road network"
            },
            "railroads": {
                "url": "https://gis.westchestergov.com/arcgis/rest/services/OpenData/FeatureServer/9",
                "name": "Railroad Lines",
                "description": "Railroad tracks and corridors"
            }
        }

        # Rate limiting
        self.request_delay = 1.0
        self.last_request_time = 0

        # Session for persistent connections
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Westchester Data Platform/1.0 (Data Collection)'
        })

    def _rate_limit(self):
        """Implement rate limiting for requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.request_delay:
            sleep_time = self.request_delay - time_since_last
            logger.info(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def discover_datasets(self) -> List[Dict[str, Any]]:
        """Discover available datasets from Westchester GIS portal"""
        logger.info("Discovering available GIS datasets...")

        datasets = []

        # Try to access the main ArcGIS services directory
        try:
            self._rate_limit()
            response = self.session.get(f"{self.gis_base_url}?f=json")
            response.raise_for_status()

            services_data = response.json()

            if 'services' in services_data:
                for service in services_data['services']:
                    if 'OpenData' in service['name'] or 'Public' in service['name']:
                        dataset_info = {
                            'name': service['name'],
                            'url': f"{self.gis_base_url}/{service['name']}/{service['type']}",
                            'type': service['type']
                        }
                        datasets.append(dataset_info)
                        logger.info(f"Found dataset: {service['name']}")

        except Exception as e:
            logger.warning(f"Could not auto-discover datasets: {e}")
            logger.info("Using known dataset configurations...")

            # Fall back to known datasets
            for dataset_id, config in self.known_datasets.items():
                dataset_info = {
                    'id': dataset_id,
                    'name': config['name'],
                    'url': config['url'],
                    'description': config['description'],
                    'type': 'FeatureServer'
                }
                datasets.append(dataset_info)

        logger.info(f"Discovered {len(datasets)} GIS datasets")
        return datasets

    def get_layer_info(self, dataset_url: str) -> Dict[str, Any]:
        """Get detailed information about a dataset layer"""
        try:
            self._rate_limit()
            response = self.session.get(f"{dataset_url}?f=json")
            response.raise_for_status()

            layer_info = response.json()

            return {
                'id': layer_info.get('id'),
                'name': layer_info.get('name'),
                'description': layer_info.get('description'),
                'geometry_type': layer_info.get('geometryType'),
                'fields': layer_info.get('fields', []),
                'extent': layer_info.get('extent'),
                'count': layer_info.get('count', 0)
            }

        except Exception as e:
            logger.error(f"Failed to get layer info for {dataset_url}: {e}")
            return {}

    def download_dataset(self, dataset: Dict[str, Any], max_features: int = 10000) -> Optional[Dict[str, Any]]:
        """Download a GIS dataset as GeoJSON"""

        dataset_id = dataset.get('id', dataset['name'].lower().replace(' ', '_'))
        dataset_url = dataset['url']

        logger.info(f"Downloading dataset: {dataset['name']}")

        try:
            # Get layer info first
            layer_info = self.get_layer_info(dataset_url)
            if not layer_info:
                logger.error(f"Could not get layer info for {dataset['name']}")
                return None

            # Construct query for features
            query_url = f"{dataset_url}/query"

            # Query parameters
            params = {
                'where': '1=1',  # Get all features
                'outFields': '*',  # All fields
                'outSR': '4326',  # WGS84 coordinate system
                'f': 'geojson',  # Output as GeoJSON
                'resultRecordCount': max_features
            }

            # Add geometry parameter based on layer type
            if layer_info.get('geometry_type'):
                params['returnGeometry'] = 'true'

            self._rate_limit()
            response = self.session.get(query_url, params=params)
            response.raise_for_status()

            # Parse GeoJSON response
            geojson_data = response.json()

            if 'type' not in geojson_data or geojson_data['type'] != 'FeatureCollection':
                logger.error(f"Invalid GeoJSON response for {dataset['name']}")
                return None

            feature_count = len(geojson_data.get('features', []))
            logger.info(f"Downloaded {feature_count} features for {dataset['name']}")

            if feature_count == 0:
                logger.warning(f"No features found for {dataset['name']}")
                return None

            # Add metadata to the GeoJSON
            geojson_data['metadata'] = {
                'source': 'Westchester County GIS Portal',
                'dataset_name': dataset['name'],
                'dataset_url': dataset_url,
                'download_date': datetime.now().isoformat(),
                'feature_count': feature_count,
                'layer_info': layer_info
            }

            # Save to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_westchester_{dataset_id}.geojson"
            output_path = self.output_dir / filename

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(geojson_data, f, indent=2, ensure_ascii=False)

            logger.info(f"Saved dataset to {output_path}")

            # Also save as shapefile for compatibility
            try:
                gdf = gpd.GeoDataFrame.from_features(geojson_data['features'])
                shp_filename = f"{timestamp}_westchester_{dataset_id}.shp"
                shp_output_path = self.output_dir / shp_filename
                gdf.to_file(shp_output_path, driver='ESRI Shapefile')
                logger.info(f"Also saved as shapefile: {shp_output_path}")
            except Exception as e:
                logger.warning(f"Could not save as shapefile: {e}")

            return {
                'dataset_id': dataset_id,
                'name': dataset['name'],
                'description': dataset.get('description', ''),
                'feature_count': feature_count,
                'geojson_file': str(output_path),
                'metadata': geojson_data.get('metadata', {})
            }

        except Exception as e:
            logger.error(f"Failed to download dataset {dataset['name']}: {e}")
            return None

    def download_all_datasets(self, max_features_per_dataset: int = 10000) -> Dict[str, Any]:
        """Download all available datasets"""

        logger.info("Starting comprehensive Westchester GIS data collection...")
        logger.info(f"Output directory: {self.output_dir}")

        # Discover available datasets
        datasets = self.discover_datasets()

        results = {
            'total_datasets': len(datasets),
            'successful_downloads': 0,
            'failed_downloads': 0,
            'total_features': 0,
            'datasets': [],
            'download_time': datetime.now().isoformat()
        }

        # Download each dataset
        for i, dataset in enumerate(datasets, 1):
            logger.info(f"Processing dataset {i}/{len(datasets)}: {dataset['name']}")

            try:
                download_result = self.download_dataset(dataset, max_features_per_dataset)

                if download_result:
                    results['datasets'].append(download_result)
                    results['successful_downloads'] += 1
                    results['total_features'] += download_result['feature_count']
                    logger.info(f"✅ Successfully downloaded {dataset['name']}")
                else:
                    results['failed_downloads'] += 1
                    logger.error(f"❌ Failed to download {dataset['name']}")

            except Exception as e:
                results['failed_downloads'] += 1
                logger.error(f"❌ Error processing {dataset['name']}: {e}")

            # Brief pause between datasets
            time.sleep(0.5)

        # Save summary
        summary_file = self.output_dir / f"westchester_gis_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        logger.info(f"\n🎉 Westchester GIS Data Collection Complete!")
        logger.info(f"✅ Successfully downloaded: {results['successful_downloads']}/{results['total_datasets']} datasets")
        logger.info(f"📊 Total features collected: {results['total_features']:,}")
        logger.info(f"📁 Summary saved to: {summary_file}")

        return results

def main():
    """Main function for command line usage"""
    import argparse

    parser = argparse.ArgumentParser(description='Collect Westchester County GIS Data')
    parser.add_argument('--output-dir', help='Output directory for data files')
    parser.add_argument('--max-features', type=int, default=10000,
                       help='Maximum features per dataset (default: 10000)')
    parser.add_argument('--dataset', help='Download specific dataset only')

    args = parser.parse_args()

    # Initialize collector
    collector = WestchesterGISCollector(output_dir=args.output_dir)

    if args.dataset:
        # Download specific dataset
        datasets = collector.discover_datasets()
        target_dataset = None

        for dataset in datasets:
            if dataset.get('id') == args.dataset or dataset['name'].lower() == args.dataset.lower():
                target_dataset = dataset
                break

        if target_dataset:
            logger.info(f"Downloading specific dataset: {target_dataset['name']}")
            result = collector.download_dataset(target_dataset, args.max_features)
            if result:
                logger.info(f"✅ Successfully downloaded {result['feature_count']} features")
            else:
                logger.error("❌ Failed to download dataset")
        else:
            logger.error(f"Dataset '{args.dataset}' not found")
            logger.info("Available datasets:")
            for dataset in datasets:
                logger.info(f"  - {dataset.get('id', dataset['name'])}: {dataset['name']}")
    else:
        # Download all datasets
        results = collector.download_all_datasets(args.max_features)

        if results['successful_downloads'] > 0:
            logger.info("\n📋 Download Summary:")
            for dataset in results['datasets']:
                logger.info(f"  📊 {dataset['name']}: {dataset['feature_count']:,} features")

        logger.info(f"\n🎯 Total: {results['successful_downloads']} datasets, {results['total_features']:,} features")

if __name__ == "__main__":
    main()