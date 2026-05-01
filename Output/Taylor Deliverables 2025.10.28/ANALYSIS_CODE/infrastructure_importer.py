"""
Infrastructure Data Importer

Downloads parks, trails, and amenities data for Westchester County using OpenStreetMap.
"""

import requests
import json
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime
import time


class InfrastructureImporter:
    """Import infrastructure data from OpenStreetMap"""
    
    # Westchester County bounding box
    BBOX = "40.9,-74.0,41.4,-73.5"  # min_lat,min_lon,max_lat,max_lon
    
    # Overpass API endpoint
    OVERPASS_API = "https://overpass-api.de/api/interpreter"
    
    def __init__(self, output_dir: str = None):
        """
        Initialize infrastructure importer
        
        Args:
            output_dir: Directory to save data
        """
        if output_dir is None:
            base_path = Path(__file__).parent.parent.parent / "data" / "raw" / "infrastructure"
        else:
            base_path = Path(output_dir)
        
        self.output_dir = base_path
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def query_overpass(self, query: str) -> Dict:
        """
        Execute Overpass API query
        
        Args:
            query: Overpass QL query string
            
        Returns:
            GeoJSON result
        """
        try:
            response = requests.post(
                self.OVERPASS_API,
                data={'data': query},
                timeout=60
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"[FAILED] Overpass query error: {e}")
            return {"elements": []}
    
    def fetch_parks(self) -> List[Dict]:
        """Fetch parks and recreation areas"""
        print("Fetching parks and recreation areas...")
        
        query = f"""
        [out:json][bbox:{self.BBOX}];
        (
          way["leisure"="park"];
          way["leisure"="playground"];
          relation["leisure"="park"];
          way["landuse"="recreation_ground"];
        );
        out geom;
        """
        
        result = self.query_overpass(query)
        elements = result.get('elements', [])
        
        print(f"[SUCCESS] Fetched {len(elements)} parks")
        return elements
    
    def fetch_trails(self) -> List[Dict]:
        """Fetch trails and paths"""
        print("Fetching trails and bike paths...")
        
        query = f"""
        [out:json][bbox:{self.BBOX}];
        (
          way["highway"="cycleway"];
          way["highway"="path"]["bicycle"="yes"];
          way["route"="hiking"];
        );
        out geom;
        """
        
        result = self.query_overpass(query)
        elements = result.get('elements', [])
        
        print(f"[SUCCESS] Fetched {len(elements)} trails/paths")
        return elements
    
    def fetch_amenities(self) -> List[Dict]:
        """Fetch public amenities"""
        print("Fetching public amenities...")
        
        query = f"""
        [out:json][bbox:{self.BBOX}];
        (
          node["amenity"="parking"];
          node["amenity"="library"];
          node["amenity"="community_centre"];
          node["tourism"="attraction"];
        );
        out;
        """
        
        result = self.query_overpass(query)
        elements = result.get('elements', [])
        
        print(f"[SUCCESS] Fetched {len(elements)} amenities")
        return elements
    
    def osm_to_geojson(self, elements: List[Dict], category: str) -> Dict:
        """
        Convert OSM elements to GeoJSON
        
        Args:
            elements: OSM elements
            category: Data category name
            
        Returns:
            GeoJSON FeatureCollection
        """
        features = []
        
        for element in elements:
            try:
                # Handle different geometry types
                if element['type'] == 'node':
                    geometry = {
                        "type": "Point",
                        "coordinates": [element['lon'], element['lat']]
                    }
                elif element['type'] == 'way' and 'geometry' in element:
                    coords = [[p['lon'], p['lat']] for p in element['geometry']]
                    geometry = {
                        "type": "LineString" if len(coords) > 1 else "Point",
                        "coordinates": coords if len(coords) > 1 else coords[0]
                    }
                else:
                    continue
                
                # Extract properties
                properties = {
                    "osm_id": element.get('id'),
                    "osm_type": element.get('type'),
                    "name": element.get('tags', {}).get('name', 'Unnamed'),
                    "category": category
                }
                
                # Add all tags as properties
                if 'tags' in element:
                    properties.update(element['tags'])
                
                feature = {
                    "type": "Feature",
                    "geometry": geometry,
                    "properties": properties
                }
                features.append(feature)
            except (KeyError, IndexError) as e:
                continue
        
        geojson = {
            "type": "FeatureCollection",
            "metadata": {
                "generated": datetime.now().isoformat(),
                "source": "OpenStreetMap via Overpass API",
                "category": category,
                "county": "Westchester County, NY",
                "feature_count": len(features)
            },
            "features": features
        }
        
        return geojson
    
    def save_geojson(self, geojson: Dict, filename: str):
        """
        Save GeoJSON to file
        
        Args:
            geojson: GeoJSON data
            filename: Output filename
        """
        filepath = self.output_dir / filename
        with open(filepath, 'w') as f:
            json.dump(geojson, f, indent=2)
        print(f"[SUCCESS] Saved to {filepath}")
    
    def run_import(self) -> Tuple[bool, str]:
        """
        Run complete infrastructure import
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            results = []
            
            # Fetch parks
            print("\n[1/3] Fetching parks...")
            parks = self.fetch_parks()
            if parks:
                parks_geojson = self.osm_to_geojson(parks, "parks")
                self.save_geojson(parks_geojson, "westchester_parks.geojson")
                results.append(f"{len(parks)} parks")
            time.sleep(1)  # Be nice to Overpass API
            
            # Fetch trails
            print("\n[2/3] Fetching trails...")
            trails = self.fetch_trails()
            if trails:
                trails_geojson = self.osm_to_geojson(trails, "trails")
                self.save_geojson(trails_geojson, "westchester_trails.geojson")
                results.append(f"{len(trails)} trails")
            time.sleep(1)
            
            # Fetch amenities
            print("\n[3/3] Fetching amenities...")
            amenities = self.fetch_amenities()
            if amenities:
                amenities_geojson = self.osm_to_geojson(amenities, "amenities")
                self.save_geojson(amenities_geojson, "westchester_amenities.geojson")
                results.append(f"{len(amenities)} amenities")
            
            if results:
                return True, f"Successfully imported: {', '.join(results)}"
            else:
                return False, "No infrastructure data retrieved"
                
        except Exception as e:
            return False, f"Import failed: {str(e)}"


def main():
    """Command-line interface"""
    print("="*70)
    print(" Westchester County - Infrastructure Data Importer")
    print("="*70)
    print()
    print("Fetching data from OpenStreetMap via Overpass API...")
    print()
    
    importer = InfrastructureImporter()
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

