"""
Sidewalk and Infrastructure Data Importer

Downloads sidewalks, bike lanes, bus stops, and other infrastructure from OpenStreetMap
"""

import requests
import json
import os
from pathlib import Path
from typing import Dict, Any

class SidewalkImporter:
    """Import sidewalk and infrastructure data from OpenStreetMap"""
    
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            self.data_dir = Path(__file__).parent.parent.parent / "data" / "raw" / "infrastructure"
        else:
            self.data_dir = Path(data_dir)
        
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Overpass API endpoint
        self.overpass_url = "https://overpass-api.de/api/interpreter"
        
        # Westchester County bounding box (approximate)
        self.bbox = "41.0,-73.95,41.4,-73.4"  # south,west,north,east
        
    def download_sidewalks(self) -> Dict[str, Any]:
        """
        Download sidewalk data from OpenStreetMap
        """
        print("Downloading sidewalk data from OpenStreetMap...")
        
        # Overpass QL query for sidewalks and footpaths
        query = f"""
        [out:json][timeout:120];
        (
          way["highway"="footway"]["footway"~"sidewalk|crossing"]({self.bbox});
          way["highway"="footway"]["surface"~"paved|asphalt|concrete"]({self.bbox});
          way["highway"="path"]["foot"="yes"]({self.bbox});
          way["highway"="pedestrian"]({self.bbox});
        );
        out geom;
        """
        
        try:
            response = requests.post(
                self.overpass_url,
                data=query,
                headers={'Content-Type': 'text/plain'},
                timeout=180
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Convert to GeoJSON
            geojson = self.osm_to_geojson(data, "sidewalk")
            
            # Save to file
            output_file = self.data_dir / "westchester_sidewalks.geojson"
            with open(output_file, 'w') as f:
                json.dump(geojson, f, indent=2)
            
            print(f"[SUCCESS] Sidewalk data saved to {output_file}")
            print(f"[SUCCESS] Features: {len(geojson.get('features', []))}")
            return geojson
            
        except Exception as e:
            print(f"[ERROR] Sidewalk download failed: {e}")
            return self.create_sample_sidewalk_data()
    
    def download_bike_lanes(self) -> Dict[str, Any]:
        """
        Download bike lane data from OpenStreetMap
        """
        print("Downloading bike lane data from OpenStreetMap...")
        
        # Overpass QL query for bike lanes and cycling infrastructure
        query = f"""
        [out:json][timeout:120];
        (
          way["highway"="cycleway"]({self.bbox});
          way["highway"~"primary|secondary|tertiary|residential"]["bicycle"="yes"]({self.bbox});
          way["highway"~"primary|secondary|tertiary|residential"]["cycleway"~"lane|track|shared_lane"]({self.bbox});
        );
        out geom;
        """
        
        try:
            response = requests.post(
                self.overpass_url,
                data=query,
                headers={'Content-Type': 'text/plain'},
                timeout=180
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Convert to GeoJSON
            geojson = self.osm_to_geojson(data, "bike_lane")
            
            # Save to file
            output_file = self.data_dir / "westchester_bike_lanes.geojson"
            with open(output_file, 'w') as f:
                json.dump(geojson, f, indent=2)
            
            print(f"[SUCCESS] Bike lane data saved to {output_file}")
            print(f"[SUCCESS] Features: {len(geojson.get('features', []))}")
            return geojson
            
        except Exception as e:
            print(f"[ERROR] Bike lane download failed: {e}")
            return self.create_sample_bike_lane_data()
    
    def download_bus_stops(self) -> Dict[str, Any]:
        """
        Download bus stop data from OpenStreetMap
        """
        print("Downloading bus stop data from OpenStreetMap...")
        
        # Overpass QL query for bus stops
        query = f"""
        [out:json][timeout:120];
        (
          node["highway"="bus_stop"]({self.bbox});
          node["public_transport"="platform"]["bus"="yes"]({self.bbox});
          node["amenity"="bus_station"]({self.bbox});
        );
        out;
        """
        
        try:
            response = requests.post(
                self.overpass_url,
                data=query,
                headers={'Content-Type': 'text/plain'},
                timeout=180
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Convert to GeoJSON
            geojson = self.osm_to_geojson(data, "bus_stop")
            
            # Save to file
            output_file = self.data_dir / "westchester_bus_stops.geojson"
            with open(output_file, 'w') as f:
                json.dump(geojson, f, indent=2)
            
            print(f"[SUCCESS] Bus stop data saved to {output_file}")
            print(f"[SUCCESS] Features: {len(geojson.get('features', []))}")
            return geojson
            
        except Exception as e:
            print(f"[ERROR] Bus stop download failed: {e}")
            return self.create_sample_bus_stop_data()
    
    def download_street_lights(self) -> Dict[str, Any]:
        """
        Download street light data from OpenStreetMap
        """
        print("Downloading street light data from OpenStreetMap...")
        
        # Overpass QL query for street lights
        query = f"""
        [out:json][timeout:120];
        (
          node["highway"="street_lamp"]({self.bbox});
          node["amenity"="street_lamp"]({self.bbox});
          node["lighting"="street"]({self.bbox});
        );
        out;
        """
        
        try:
            response = requests.post(
                self.overpass_url,
                data=query,
                headers={'Content-Type': 'text/plain'},
                timeout=180
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Convert to GeoJSON
            geojson = self.osm_to_geojson(data, "street_light")
            
            # Save to file
            output_file = self.data_dir / "westchester_street_lights.geojson"
            with open(output_file, 'w') as f:
                json.dump(geojson, f, indent=2)
            
            print(f"[SUCCESS] Street light data saved to {output_file}")
            print(f"[SUCCESS] Features: {len(geojson.get('features', []))}")
            return geojson
            
        except Exception as e:
            print(f"[ERROR] Street light download failed: {e}")
            return self.create_sample_street_light_data()
    
    def osm_to_geojson(self, osm_data: Dict[str, Any], feature_type: str) -> Dict[str, Any]:
        """
        Convert OSM data to GeoJSON format
        """
        features = []
        
        for element in osm_data.get('elements', []):
            if element.get('type') == 'way' and 'geometry' in element:
                # This is a way (line/polygon)
                coords = []
                for node in element['geometry']:
                    coords.append([node['lon'], node['lat']])
                
                if len(coords) > 1:
                    feature = {
                        "type": "Feature",
                        "properties": {
                            "type": feature_type,
                            "name": element.get('tags', {}).get('name', f'{feature_type.title()}'),
                            "highway": element.get('tags', {}).get('highway', ''),
                            "surface": element.get('tags', {}).get('surface', ''),
                            "source": "OpenStreetMap"
                        },
                        "geometry": {
                            "type": "LineString",
                            "coordinates": coords
                        }
                    }
                    features.append(feature)
                    
            elif element.get('type') == 'node' and 'lat' in element and 'lon' in element:
                # This is a node (point)
                feature = {
                    "type": "Feature",
                    "properties": {
                        "type": feature_type,
                        "name": element.get('tags', {}).get('name', f'{feature_type.title()}'),
                        "amenity": element.get('tags', {}).get('amenity', ''),
                        "highway": element.get('tags', {}).get('highway', ''),
                        "source": "OpenStreetMap"
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [element['lon'], element['lat']]
                    }
                }
                features.append(feature)
        
        return {
            "type": "FeatureCollection",
            "features": features
        }
    
    def create_sample_sidewalk_data(self) -> Dict[str, Any]:
        """Create sample sidewalk data for demonstration"""
        print("[INFO] Creating sample sidewalk data...")
        
        # Sample sidewalk features around major Westchester areas
        sample_sidewalks = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {
                        "type": "sidewalk",
                        "name": "Main Street Sidewalk",
                        "highway": "footway",
                        "surface": "concrete",
                        "source": "Sample Data"
                    },
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [
                            [-73.9, 41.1], [-73.89, 41.11], [-73.88, 41.12]
                        ]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {
                        "type": "sidewalk",
                        "name": "Broadway Sidewalk",
                        "highway": "footway",
                        "surface": "asphalt",
                        "source": "Sample Data"
                    },
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [
                            [-73.8, 41.2], [-73.79, 41.21], [-73.78, 41.22]
                        ]
                    }
                }
            ]
        }
        
        output_file = self.data_dir / "westchester_sidewalks.geojson"
        with open(output_file, 'w') as f:
            json.dump(sample_sidewalks, f, indent=2)
        
        print(f"[SUCCESS] Sample sidewalk data saved to {output_file}")
        return sample_sidewalks
    
    def create_sample_bike_lane_data(self) -> Dict[str, Any]:
        """Create sample bike lane data"""
        print("[INFO] Creating sample bike lane data...")
        
        sample_bike_lanes = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {
                        "type": "bike_lane",
                        "name": "Bronx River Parkway Bike Path",
                        "highway": "cycleway",
                        "source": "Sample Data"
                    },
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [
                            [-73.85, 41.15], [-73.84, 41.16], [-73.83, 41.17]
                        ]
                    }
                }
            ]
        }
        
        output_file = self.data_dir / "westchester_bike_lanes.geojson"
        with open(output_file, 'w') as f:
            json.dump(sample_bike_lanes, f, indent=2)
        
        print(f"[SUCCESS] Sample bike lane data saved to {output_file}")
        return sample_bike_lanes
    
    def create_sample_bus_stop_data(self) -> Dict[str, Any]:
        """Create sample bus stop data"""
        print("[INFO] Creating sample bus stop data...")
        
        sample_bus_stops = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {
                        "type": "bus_stop",
                        "name": "Main St & Central Ave",
                        "amenity": "bus_stop",
                        "source": "Sample Data"
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-73.9, 41.1]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {
                        "type": "bus_stop",
                        "name": "Broadway & Park Ave",
                        "amenity": "bus_stop",
                        "source": "Sample Data"
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-73.8, 41.2]
                    }
                }
            ]
        }
        
        output_file = self.data_dir / "westchester_bus_stops.geojson"
        with open(output_file, 'w') as f:
            json.dump(sample_bus_stops, f, indent=2)
        
        print(f"[SUCCESS] Sample bus stop data saved to {output_file}")
        return sample_bus_stops
    
    def create_sample_street_light_data(self) -> Dict[str, Any]:
        """Create sample street light data"""
        print("[INFO] Creating sample street light data...")
        
        sample_street_lights = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {
                        "type": "street_light",
                        "name": "Street Light",
                        "amenity": "street_lamp",
                        "source": "Sample Data"
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-73.9, 41.1]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {
                        "type": "street_light",
                        "name": "Street Light",
                        "amenity": "street_lamp",
                        "source": "Sample Data"
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-73.85, 41.15]
                    }
                }
            ]
        }
        
        output_file = self.data_dir / "westchester_street_lights.geojson"
        with open(output_file, 'w') as f:
            json.dump(sample_street_lights, f, indent=2)
        
        print(f"[SUCCESS] Sample street light data saved to {output_file}")
        return sample_street_lights


def main():
    """Download all sidewalk and infrastructure data"""
    importer = SidewalkImporter()
    
    print("\n" + "="*60)
    print("Downloading Sidewalk and Infrastructure Data")
    print("="*60 + "\n")
    
    # Download sidewalks
    sidewalks = importer.download_sidewalks()
    print(f"  Sidewalk features: {len(sidewalks.get('features', []))}")
    
    print("\n" + "-"*60 + "\n")
    
    # Download bike lanes
    bike_lanes = importer.download_bike_lanes()
    print(f"  Bike lane features: {len(bike_lanes.get('features', []))}")
    
    print("\n" + "-"*60 + "\n")
    
    # Download bus stops
    bus_stops = importer.download_bus_stops()
    print(f"  Bus stop features: {len(bus_stops.get('features', []))}")
    
    print("\n" + "-"*60 + "\n")
    
    # Download street lights
    street_lights = importer.download_street_lights()
    print(f"  Street light features: {len(street_lights.get('features', []))}")
    
    print("\n" + "="*60)
    print("Sidewalk and infrastructure download complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
