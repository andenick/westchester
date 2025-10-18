"""
School Data Importer

Downloads school location and information data for Westchester County.
Uses NCES (National Center for Education Statistics) data and NY State School Directory.
"""

import requests
import json
import csv
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime


class SchoolDataImporter:
    """Import school data for Westchester County"""
    
    # Westchester County bounds
    WESTCHESTER_BOUNDS = {
        'min_lat': 40.9,
        'max_lat': 41.4,
        'min_lon': -74.0,
        'max_lon': -73.5
    }
    
    # NY State School Data API (Socrata)
    NY_SCHOOLS_API = "https://data.ny.gov/resource/mj4q-kq5y.json"
    
    def __init__(self, app_token: str = None, output_dir: str = None):
        """
        Initialize school data importer
        
        Args:
            app_token: NY State Open Data app token
            output_dir: Directory to save data
        """
        self.app_token = app_token
        
        if output_dir is None:
            base_path = Path(__file__).parent.parent.parent / "data" / "raw" / "schools"
        else:
            base_path = Path(output_dir)
        
        self.output_dir = base_path
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.headers = {}
        if app_token:
            self.headers['X-App-Token'] = app_token
    
    def fetch_ny_state_schools(self) -> List[Dict]:
        """
        Fetch school data from NY State Open Data
        
        Returns:
            List of school records
        """
        print("Fetching NY State school directory...")
        
        # Query for Westchester County schools
        params = {
            '$where': "county='Westchester'",
            '$limit': 10000
        }
        
        try:
            response = requests.get(
                self.NY_SCHOOLS_API,
                headers=self.headers,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            
            schools = response.json()
            print(f"[SUCCESS] Fetched {len(schools)} schools from NY State")
            return schools
            
        except requests.RequestException as e:
            print(f"[FAILED] Error fetching NY State schools: {e}")
            return []
    
    def filter_westchester_schools(self, schools: List[Dict]) -> List[Dict]:
        """
        Filter schools to Westchester County based on coordinates and county field
        
        Args:
            schools: List of all schools
            
        Returns:
            Filtered list of Westchester schools
        """
        westchester_schools = []
        
        for school in schools:
            # Check county field
            county = school.get('county', '').strip().lower()
            if 'westchester' in county:
                westchester_schools.append(school)
                continue
            
            # Check coordinates if available
            try:
                if 'latitude' in school and 'longitude' in school:
                    lat = float(school['latitude'])
                    lon = float(school['longitude'])
                    
                    if (self.WESTCHESTER_BOUNDS['min_lat'] <= lat <= self.WESTCHESTER_BOUNDS['max_lat'] and
                        self.WESTCHESTER_BOUNDS['min_lon'] <= lon <= self.WESTCHESTER_BOUNDS['max_lon']):
                        westchester_schools.append(school)
            except (ValueError, KeyError):
                pass
        
        print(f"[SUCCESS] Filtered to {len(westchester_schools)} Westchester schools")
        return westchester_schools
    
    def create_geojson(self, schools: List[Dict]) -> Dict:
        """
        Create GeoJSON of school locations
        
        Args:
            schools: List of schools with coordinates
            
        Returns:
            GeoJSON FeatureCollection
        """
        features = []
        
        for school in schools:
            try:
                if 'latitude' not in school or 'longitude' not in school:
                    continue
                
                lat = float(school['latitude'])
                lon = float(school['longitude'])
                
                feature = {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [lon, lat]
                    },
                    "properties": {
                        "name": school.get('school_name', ''),
                        "district": school.get('district_name', ''),
                        "type": school.get('school_type', ''),
                        "grade_level": school.get('grade_level', ''),
                        "address": school.get('location_address', ''),
                        "city": school.get('location_city', ''),
                        "zip": school.get('location_zip', ''),
                        "county": "Westchester"
                    }
                }
                features.append(feature)
            except (ValueError, KeyError) as e:
                continue
        
        geojson = {
            "type": "FeatureCollection",
            "metadata": {
                "generated": datetime.now().isoformat(),
                "source": "NY State School Directory",
                "county": "Westchester County, NY",
                "feature_count": len(features)
            },
            "features": features
        }
        
        return geojson
    
    def save_data(self, schools: List[Dict]):
        """
        Save school data in multiple formats
        
        Args:
            schools: List of school records
        """
        if not schools:
            print("[WARNING] No school data to save")
            return
        
        # Save as JSON
        json_path = self.output_dir / "westchester_schools.json"
        with open(json_path, 'w') as f:
            json.dump(schools, f, indent=2)
        print(f"[SUCCESS] Saved to {json_path}")
        
        # Save as CSV
        csv_path = self.output_dir / "westchester_schools.csv"
        if schools:
            # Get all unique fields
            all_fields = set()
            for school in schools:
                all_fields.update(school.keys())
            
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=sorted(all_fields))
                writer.writeheader()
                writer.writerows(schools)
            print(f"[SUCCESS] Saved to {csv_path}")
        
        # Save GeoJSON
        geojson = self.create_geojson(schools)
        if geojson['features']:
            geojson_path = self.output_dir / "westchester_schools.geojson"
            with open(geojson_path, 'w') as f:
                json.dump(geojson, f, indent=2)
            print(f"[SUCCESS] Saved GeoJSON to {geojson_path}")
    
    def run_import(self) -> Tuple[bool, str]:
        """
        Run complete school data import
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            if not self.app_token:
                print("[WARNING] No app token provided. Rate limits may apply.")
            
            # Fetch schools
            schools = self.fetch_ny_state_schools()
            
            if not schools:
                return False, "No school data retrieved"
            
            # Filter to Westchester
            westchester_schools = self.filter_westchester_schools(schools)
            
            if not westchester_schools:
                return False, "No Westchester schools found after filtering"
            
            # Save data
            self.save_data(westchester_schools)
            
            return True, f"Successfully imported {len(westchester_schools)} schools"
            
        except Exception as e:
            return False, f"Import failed: {str(e)}"


def main():
    """Command-line interface"""
    import os
    
    print("="*70)
    print(" Westchester County - School Data Importer")
    print("="*70)
    print()
    
    # Get app token from environment
    app_token = os.getenv('NY_STATE_APP_TOKEN')
    
    if not app_token:
        print("[WARNING] No NY_STATE_APP_TOKEN environment variable found")
        print("  You can still proceed, but rate limits may apply")
        print()
    
    importer = SchoolDataImporter(app_token=app_token)
    success, message = importer.run_import()
    
    print()
    print("="*70)
    if success:
        print(f"[SUCCESS]: {message}")
    else:
        print(f"[FAILED]: {message}")
    print("="*70)


if __name__ == "__main__":
    main()

