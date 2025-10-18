"""
Metro-North GTFS Data Importer

Downloads and parses Metro-North Railroad GTFS (General Transit Feed Specification) data,
focusing on stations within Westchester County.
"""

import requests
import zipfile
import io
import csv
import json
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime


class MetroNorthGTFSImporter:
    """Import and process Metro-North GTFS data"""
    
    GTFS_URL = "http://web.mta.info/developers/data/mnr/google_transit.zip"
    
    # Westchester County approximate bounds
    WESTCHESTER_BOUNDS = {
        'min_lat': 40.9,
        'max_lat': 41.4,
        'min_lon': -74.0,
        'max_lon': -73.5
    }
    
    def __init__(self, output_dir: str = None):
        """
        Initialize the importer
        
        Args:
            output_dir: Directory to save downloaded data (default: ../../data/raw/transit/)
        """
        if output_dir is None:
            # Default to data/raw/transit relative to this file
            base_path = Path(__file__).parent.parent.parent / "data" / "raw" / "transit"
        else:
            base_path = Path(output_dir)
        
        self.output_dir = base_path
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def download_gtfs(self) -> Path:
        """
        Download Metro-North GTFS data
        
        Returns:
            Path to downloaded ZIP file
        """
        print(f"Downloading Metro-North GTFS data from {self.GTFS_URL}...")
        
        try:
            response = requests.get(self.GTFS_URL, timeout=30)
            response.raise_for_status()
            
            # Save the ZIP file
            zip_path = self.output_dir / "metro_north_gtfs.zip"
            with open(zip_path, 'wb') as f:
                f.write(response.content)
            
            print(f"[SUCCESS] Downloaded {len(response.content)} bytes to {zip_path}")
            return zip_path
            
        except requests.RequestException as e:
            print(f"[FAILED] Error downloading GTFS data: {e}")
            raise
    
    def extract_gtfs(self, zip_path: Path) -> Dict[str, List[Dict]]:
        """
        Extract and parse GTFS files from ZIP
        
        Args:
            zip_path: Path to GTFS ZIP file
            
        Returns:
            Dictionary of GTFS data by file (stops, routes, trips, etc.)
        """
        print(f"Extracting GTFS data from {zip_path}...")
        
        gtfs_data = {}
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Extract all files to a subdirectory
                extract_dir = self.output_dir / "gtfs_extracted"
                extract_dir.mkdir(exist_ok=True)
                zip_ref.extractall(extract_dir)
                
                # Parse key GTFS files
                files_to_parse = ['stops.txt', 'routes.txt', 'trips.txt', 'stop_times.txt', 'agency.txt']
                
                for filename in files_to_parse:
                    file_path = extract_dir / filename
                    if file_path.exists():
                        with open(file_path, 'r', encoding='utf-8-sig') as f:
                            reader = csv.DictReader(f)
                            gtfs_data[filename.replace('.txt', '')] = list(reader)
                        print(f"[SUCCESS] Parsed {filename}: {len(gtfs_data[filename.replace('.txt', '')])} records")
                    else:
                        print(f"[WARNING] {filename} not found in GTFS data")
            
            return gtfs_data
            
        except Exception as e:
            print(f"[FAILED] Error extracting GTFS data: {e}")
            raise
    
    def filter_westchester_stations(self, stops: List[Dict]) -> List[Dict]:
        """
        Filter stations to only those in Westchester County
        
        Args:
            stops: List of all stops from GTFS
            
        Returns:
            List of stops within Westchester County bounds
        """
        westchester_stops = []
        
        for stop in stops:
            try:
                lat = float(stop['stop_lat'])
                lon = float(stop['stop_lon'])
                
                # Check if within Westchester bounds
                if (self.WESTCHESTER_BOUNDS['min_lat'] <= lat <= self.WESTCHESTER_BOUNDS['max_lat'] and
                    self.WESTCHESTER_BOUNDS['min_lon'] <= lon <= self.WESTCHESTER_BOUNDS['max_lon']):
                    westchester_stops.append(stop)
                    
            except (ValueError, KeyError) as e:
                print(f"[WARNING] Invalid coordinates for stop: {stop.get('stop_name', 'unknown')}")
                continue
        
        print(f"[SUCCESS] Found {len(westchester_stops)} stations in Westchester County")
        return westchester_stops
    
    def identify_metro_north_lines(self, routes: List[Dict], trips: List[Dict]) -> Dict[str, str]:
        """
        Identify Metro-North lines (Harlem, Hudson, New Haven)
        
        Args:
            routes: GTFS routes data
            trips: GTFS trips data
            
        Returns:
            Dictionary mapping route_id to line name
        """
        line_mapping = {}
        
        for route in routes:
            route_id = route.get('route_id', '')
            route_name = route.get('route_long_name', '').lower()
            
            # Identify line based on route name
            if 'harlem' in route_name:
                line_mapping[route_id] = 'Harlem Line'
            elif 'hudson' in route_name:
                line_mapping[route_id] = 'Hudson Line'
            elif 'new haven' in route_name or 'newhaven' in route_name:
                line_mapping[route_id] = 'New Haven Line'
            else:
                line_mapping[route_id] = 'Other'
        
        return line_mapping
    
    def create_station_geojson(self, stations: List[Dict], routes: List[Dict], trips: List[Dict]) -> Dict:
        """
        Create GeoJSON of Westchester County Metro-North stations
        
        Args:
            stations: Filtered Westchester stations
            routes: GTFS routes data
            trips: GTFS trips data
            
        Returns:
            GeoJSON FeatureCollection
        """
        line_mapping = self.identify_metro_north_lines(routes, trips)
        
        features = []
        for station in stations:
            try:
                feature = {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [float(station['stop_lon']), float(station['stop_lat'])]
                    },
                    "properties": {
                        "name": station.get('stop_name', ''),
                        "id": station.get('stop_id', ''),
                        "code": station.get('stop_code', ''),
                        "description": station.get('stop_desc', ''),
                        "wheelchair_accessible": station.get('wheelchair_boarding', '0') == '1',
                        "county": "Westchester",
                        "state": "NY"
                    }
                }
                features.append(feature)
            except (ValueError, KeyError) as e:
                print(f"[WARNING] Error processing station {station.get('stop_name', 'unknown')}: {e}")
                continue
        
        geojson = {
            "type": "FeatureCollection",
            "metadata": {
                "generated": datetime.now().isoformat(),
                "source": "Metro-North Railroad GTFS",
                "source_url": self.GTFS_URL,
                "county": "Westchester County, NY",
                "feature_count": len(features)
            },
            "features": features
        }
        
        return geojson
    
    def save_westchester_data(self, stations: List[Dict], routes: List[Dict], trips: List[Dict]):
        """
        Save Westchester-specific station data in multiple formats
        
        Args:
            stations: Filtered Westchester stations
            routes: GTFS routes data
            trips: GTFS trips data
        """
        # Save as JSON
        json_path = self.output_dir / "westchester_metro_north_stations.json"
        with open(json_path, 'w') as f:
            json.dump(stations, f, indent=2)
        print(f"[SUCCESS] Saved station data to {json_path}")
        
        # Save as GeoJSON
        geojson = self.create_station_geojson(stations, routes, trips)
        geojson_path = self.output_dir / "westchester_metro_north_stations.geojson"
        with open(geojson_path, 'w') as f:
            json.dump(geojson, f, indent=2)
        print(f"[SUCCESS] Saved GeoJSON to {geojson_path}")
        
        # Save metadata
        metadata = {
            "source": "Metro-North Railroad GTFS",
            "source_url": self.GTFS_URL,
            "download_date": datetime.now().isoformat(),
            "county": "Westchester County, NY",
            "station_count": len(stations),
            "bounds": self.WESTCHESTER_BOUNDS,
            "files": {
                "json": str(json_path.name),
                "geojson": str(geojson_path.name),
                "gtfs_zip": "metro_north_gtfs.zip"
            }
        }
        
        metadata_path = self.output_dir / "westchester_metro_north_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"[SUCCESS] Saved metadata to {metadata_path}")
    
    def run_import(self) -> Tuple[bool, str]:
        """
        Run complete import process
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Download GTFS data
            zip_path = self.download_gtfs()
            
            # Extract and parse
            gtfs_data = self.extract_gtfs(zip_path)
            
            # Filter to Westchester County
            westchester_stations = self.filter_westchester_stations(gtfs_data['stops'])
            
            if not westchester_stations:
                return False, "No stations found in Westchester County"
            
            # Save Westchester-specific data
            self.save_westchester_data(
                westchester_stations,
                gtfs_data.get('routes', []),
                gtfs_data.get('trips', [])
            )
            
            return True, f"Successfully imported {len(westchester_stations)} Metro-North stations"
            
        except Exception as e:
            return False, f"Import failed: {str(e)}"


def main():
    """Command-line interface for the importer"""
    print("="*60)
    print("Metro-North GTFS Data Importer - Westchester County")
    print("="*60)
    print()
    
    importer = MetroNorthGTFSImporter()
    success, message = importer.run_import()
    
    print()
    print("="*60)
    if success:
        print(f"[SUCCESS]: {message}")
    else:
        print(f"[FAILED]: {message}")
    print("="*60)


if __name__ == "__main__":
    main()

