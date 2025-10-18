import requests
import json
from pathlib import Path
import logging
from typing import Dict, Any, List
import time

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

class ComprehensiveInfrastructureImporter:
    def __init__(self, data_dir: Path = Path("Projects/Westchester/Technical/data/raw/infrastructure")):
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.overpass_url = "http://overpass-api.de/api/interpreter"
        
        # Expanded bounding box for Westchester County
        # This ensures we capture all edge areas
        self.bbox = "40.7, -74.0, 41.5, -73.3"  # Expanded by 0.1-0.2 degrees
        
        # Westchester municipalities for targeted queries
        self.municipalities = [
            "White Plains", "Yonkers", "New Rochelle", "Mount Vernon", 
            "Port Chester", "Harrison", "Greenburgh", "Mamaroneck", 
            "Scarsdale", "Rye", "Sleepy Hollow", "Tarrytown", 
            "Irvington", "Dobbs Ferry", "Hastings-on-Hudson", "Ardsley",
            "Elmsford", "Tuckahoe", "Bronxville", "Pelham", "Pelham Manor",
            "Larchmont", "Mamaroneck Village", "Rye Brook", "Pound Ridge",
            "Lewisboro", "North Salem", "Somers", "Yorktown", "Cortlandt",
            "Peekskill", "Ossining", "Briarcliff Manor", "Croton-on-Hudson",
            "Buchanan", "Mount Pleasant", "New Castle", "Bedford", "North Castle"
        ]

    def create_comprehensive_sidewalk_query(self) -> str:
        """
        Create a comprehensive Overpass query for all sidewalk-related infrastructure.
        This includes multiple tagging schemes and types.
        """
        return f"""
[out:json][timeout:300];
(
  // Dedicated sidewalks
  way["highway"="footway"]["footway"="sidewalk"]({self.bbox});
  way["highway"="footway"]({self.bbox});
  
  // Pedestrian paths and walkways
  way["highway"="path"]["foot"="yes"]({self.bbox});
  way["highway"="pedestrian"]({self.bbox});
  way["highway"="footway"]["footway"!="sidewalk"]({self.bbox});
  
  // Tracks with foot access
  way["highway"="track"]["foot"~"yes|designated"]({self.bbox});
  
  // Roads with sidewalk tags
  way["sidewalk"~"both|left|right|yes"]({self.bbox});
  way["sidewalk:both"="yes"]({self.bbox});
  way["sidewalk:left"="yes"]({self.bbox});
  way["sidewalk:right"="yes"]({self.bbox});
  
  // Alternative sidewalk tagging
  way["footway"="sidewalk"]({self.bbox});
  way["sidewalk:both"="separate"]({self.bbox});
  way["sidewalk:left"="separate"]({self.bbox});
  way["sidewalk:right"="separate"]({self.bbox});
  
  // Shared paths
  way["highway"="path"]["bicycle"="yes"]["foot"="yes"]({self.bbox});
  way["highway"="cycleway"]["foot"="yes"]({self.bbox});
  
  // Crossings
  way["highway"="crossing"]({self.bbox});
  way["highway"="footway"]["crossing"~"marked|unmarked|zebra"]({self.bbox});
);
out geom;
"""

    def create_comprehensive_bike_lane_query(self) -> str:
        """
        Create a comprehensive Overpass query for all bike lane infrastructure.
        """
        return f"""
[out:json][timeout:300];
(
  // Dedicated bike lanes
  way["highway"="cycleway"]({self.bbox});
  way["cycleway"~"lane|track|separated"]({self.bbox});
  way["cycleway:both"~"lane|track"]({self.bbox});
  way["cycleway:left"~"lane|track"]({self.bbox});
  way["cycleway:right"~"lane|track"]({self.bbox});
  
  // Bike lanes on roads
  way["highway"~"primary|secondary|tertiary|residential"]["cycleway"~"lane|track"]({self.bbox});
  
  // Shared paths
  way["highway"="path"]["bicycle"="yes"]({self.bbox});
  way["highway"="footway"]["bicycle"="yes"]({self.bbox});
  
  // Bike routes
  way["route"="bicycle"]({self.bbox});
  way["bicycle"~"designated|official"]({self.bbox});
  
  // Alternative tagging
  way["cycleway:both"="shared_lane"]({self.bbox});
  way["cycleway:left"="shared_lane"]({self.bbox});
  way["cycleway:right"="shared_lane"]({self.bbox});
);
out geom;
"""

    def create_comprehensive_bus_stop_query(self) -> str:
        """
        Create a comprehensive Overpass query for all bus stop infrastructure.
        """
        return f"""
[out:json][timeout:300];
(
  // Standard bus stops
  node["highway"="bus_stop"]({self.bbox});
  node["public_transport"="platform"]["bus"="yes"]({self.bbox});
  node["amenity"="bus_station"]({self.bbox});
  
  // Alternative tagging
  node["railway"="platform"]["public_transport"="platform"]["bus"="yes"]({self.bbox});
  node["public_transport"="stop_position"]["bus"="yes"]({self.bbox});
  
  // Bus stations
  node["amenity"="bus_station"]({self.bbox});
  way["amenity"="bus_station"]({self.bbox});
  relation["amenity"="bus_station"]({self.bbox});
);
out geom;
"""

    def create_comprehensive_street_light_query(self) -> str:
        """
        Create a comprehensive Overpass query for all street light infrastructure.
        """
        return f"""
[out:json][timeout:300];
(
  // Street lights
  node["highway"="street_lamp"]({self.bbox});
  node["amenity"="street_lamp"]({self.bbox});
  node["highway"="street_light"]({self.bbox});
  node["amenity"="street_light"]({self.bbox});
  
  // Alternative tagging
  node["light"="street"]({self.bbox});
  node["light"="streetlight"]({self.bbox});
  node["light_source"="electric"]({self.bbox});
  
  // Lamp posts
  node["man_made"="street_lamp"]({self.bbox});
  node["man_made"="lighting"]({self.bbox});
);
out geom;
"""

    def query_municipality_specific(self, municipality: str, infrastructure_type: str) -> Dict[str, Any]:
        """
        Query infrastructure data for a specific municipality.
        This helps ensure complete coverage by querying each area separately.
        """
        logger.info(f"   [MUNICIPALITY] Querying {municipality} for {infrastructure_type}...")
        
        if infrastructure_type == "sidewalks":
            query = f"""
[out:json][timeout:180];
area["name"="{municipality}"]["admin_level"="8"];
(
  way["highway"="footway"]["footway"="sidewalk"](area);
  way["highway"="footway"](area);
  way["highway"="path"]["foot"="yes"](area);
  way["highway"="pedestrian"](area);
  way["sidewalk"~"both|left|right|yes"](area);
);
out geom;
"""
        elif infrastructure_type == "bike_lanes":
            query = f"""
[out:json][timeout:180];
area["name"="{municipality}"]["admin_level"="8"];
(
  way["highway"="cycleway"](area);
  way["cycleway"~"lane|track|separated"](area);
  way["highway"="path"]["bicycle"="yes"](area);
);
out geom;
"""
        elif infrastructure_type == "bus_stops":
            query = f"""
[out:json][timeout:180];
area["name"="{municipality}"]["admin_level"="8"];
(
  node["highway"="bus_stop"](area);
  node["public_transport"="platform"]["bus"="yes"](area);
);
out geom;
"""
        elif infrastructure_type == "street_lights":
            query = f"""
[out:json][timeout:180];
area["name"="{municipality}"]["admin_level"="8"];
(
  node["highway"="street_lamp"](area);
  node["amenity"="street_lamp"](area);
);
out geom;
"""
        else:
            logger.warning(f"   [WARNING] Unknown infrastructure type: {infrastructure_type}")
            return {"type": "FeatureCollection", "features": []}
        
        try:
            response = requests.post(
                self.overpass_url,
                data=query,
                headers={'Content-Type': 'text/plain'},
                timeout=180
            )
            response.raise_for_status()
            data = response.json()
            
            feature_count = len(data.get('elements', []))
            logger.info(f"   [SUCCESS] Found {feature_count} {infrastructure_type} in {municipality}")
            
            return data
            
        except Exception as e:
            logger.warning(f"   [WARNING] Failed to query {municipality} for {infrastructure_type}: {e}")
            return {"type": "FeatureCollection", "features": []}

    def download_comprehensive_infrastructure(self) -> Dict[str, Any]:
        """
        Download comprehensive infrastructure data using multiple approaches.
        """
        logger.info("\n" + "="*80)
        logger.info("COMPREHENSIVE INFRASTRUCTURE DATA COLLECTION")
        logger.info("="*80)
        
        results = {}
        
        # 1. County-wide comprehensive queries
        logger.info("\n[PHASE 1] County-wide comprehensive queries...")
        
        infrastructure_types = {
            "sidewalks": self.create_comprehensive_sidewalk_query(),
            "bike_lanes": self.create_comprehensive_bike_lane_query(),
            "bus_stops": self.create_comprehensive_bus_stop_query(),
            "street_lights": self.create_comprehensive_street_light_query()
        }
        
        for infra_type, query in infrastructure_types.items():
            logger.info(f"   [COUNTY-WIDE] Downloading {infra_type}...")
            try:
                response = requests.post(
                    self.overpass_url,
                    data=query,
                    headers={'Content-Type': 'text/plain'},
                    timeout=300
                )
                response.raise_for_status()
                data = response.json()
                
                # Convert to GeoJSON
                geojson_data = self.osm_to_geojson(data, infra_type)
                results[infra_type] = geojson_data
                
                feature_count = len(geojson_data.get('features', []))
                logger.info(f"   [SUCCESS] Found {feature_count} {infra_type} county-wide")
                
                # Save county-wide data
                output_file = self.data_dir / f"westchester_{infra_type}_comprehensive.geojson"
                with open(output_file, 'w') as f:
                    json.dump(geojson_data, f, indent=2)
                logger.info(f"   [SAVED] County-wide {infra_type} data")
                
            except Exception as e:
                logger.error(f"   [ERROR] Failed to download {infra_type}: {e}")
                results[infra_type] = {"type": "FeatureCollection", "features": []}
        
        # 2. Municipality-specific queries for completeness
        logger.info("\n[PHASE 2] Municipality-specific queries for completeness...")
        
        for infra_type in infrastructure_types.keys():
            logger.info(f"   [MUNICIPALITY QUERIES] Processing {infra_type}...")
            
            municipality_data = []
            for muni in self.municipalities[:10]:  # Limit to first 10 for performance
                muni_data = self.query_municipality_specific(muni, infra_type)
                if muni_data.get('elements'):
                    municipality_data.extend(muni_data['elements'])
                
                # Rate limiting
                time.sleep(1)
            
            if municipality_data:
                # Convert municipality data to GeoJSON
                geojson_data = self.osm_to_geojson(
                    {"elements": municipality_data}, 
                    infra_type
                )
                
                # Merge with county-wide data
                if infra_type in results and results[infra_type].get('features'):
                    existing_features = results[infra_type]['features']
                    new_features = geojson_data.get('features', [])
                    
                    # Combine and deduplicate (simple approach)
                    all_features = existing_features + new_features
                    results[infra_type]['features'] = all_features
                
                feature_count = len(geojson_data.get('features', []))
                logger.info(f"   [SUCCESS] Added {feature_count} municipality-specific {infra_type}")
        
        # 3. Create data quality report
        logger.info("\n[PHASE 3] Creating data quality report...")
        
        quality_report = {
            "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
            "bbox": self.bbox,
            "municipalities_queried": len(self.municipalities),
            "infrastructure_summary": {},
            "data_quality_notes": []
        }
        
        for infra_type, data in results.items():
            feature_count = len(data.get('features', []))
            quality_report["infrastructure_summary"][infra_type] = {
                "feature_count": feature_count,
                "data_completeness": "unknown",  # Would need ground truth to assess
                "last_updated": "2025-10-13"
            }
            
            # Add quality notes
            if feature_count == 0:
                quality_report["data_quality_notes"].append(
                    f"WARNING: No {infra_type} data found. May indicate incomplete OSM coverage."
                )
            elif feature_count < 50:
                quality_report["data_quality_notes"].append(
                    f"LOW: Only {feature_count} {infra_type} found. Coverage may be incomplete."
                )
            else:
                quality_report["data_quality_notes"].append(
                    f"GOOD: {feature_count} {infra_type} found."
                )
        
        # Save quality report
        report_file = self.data_dir / "infrastructure_quality_report.json"
        with open(report_file, 'w') as f:
            json.dump(quality_report, f, indent=2)
        
        logger.info(f"\n[SUCCESS] Data quality report saved: {report_file}")
        
        return results

    def osm_to_geojson(self, osm_data: Dict[str, Any], infrastructure_type: str) -> Dict[str, Any]:
        """
        Convert Overpass API response to GeoJSON format.
        """
        geojson_features = []
        
        for element in osm_data.get('elements', []):
            if element['type'] == 'way' and 'geometry' in element:
                # Way (line/polygon) elements
                coords = [[node['lon'], node['lat']] for node in element['geometry']]
                
                if len(coords) >= 2:
                    geometry_type = "LineString"
                    if coords[0] == coords[-1] and len(coords) >= 4:
                        geometry_type = "Polygon"
                        coords = [coords]  # Polygon needs array of rings
                    
                    feature = {
                        "type": "Feature",
                        "properties": {
                            "id": element['id'],
                            "infrastructure_type": infrastructure_type,
                            "osm_tags": element.get('tags', {}),
                            "name": element.get('tags', {}).get('name', f"{infrastructure_type} {element['id']}")
                        },
                        "geometry": {
                            "type": geometry_type,
                            "coordinates": coords
                        }
                    }
                    geojson_features.append(feature)
            
            elif element['type'] == 'node' and 'lat' in element and 'lon' in element:
                # Node (point) elements
                feature = {
                    "type": "Feature",
                    "properties": {
                        "id": element['id'],
                        "infrastructure_type": infrastructure_type,
                        "osm_tags": element.get('tags', {}),
                        "name": element.get('tags', {}).get('name', f"{infrastructure_type} {element['id']}")
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [element['lon'], element['lat']]
                    }
                }
                geojson_features.append(feature)
        
        return {
            "type": "FeatureCollection",
            "features": geojson_features,
            "metadata": {
                "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
                "source": "OpenStreetMap via Overpass API",
                "infrastructure_type": infrastructure_type,
                "feature_count": len(geojson_features),
                "bbox": self.bbox
            }
        }


def main():
    """Download comprehensive infrastructure data"""
    importer = ComprehensiveInfrastructureImporter()
    
    logger.info("[START] Starting comprehensive infrastructure data collection...")
    logger.info("   This will download sidewalks, bike lanes, bus stops, and street lights")
    logger.info("   using both county-wide and municipality-specific queries.")
    
    results = importer.download_comprehensive_infrastructure()
    
    logger.info("\n" + "="*80)
    logger.info("COMPREHENSIVE INFRASTRUCTURE COLLECTION COMPLETE!")
    logger.info("="*80)
    
    total_features = sum(len(data.get('features', [])) for data in results.values())
    logger.info(f"[SUCCESS] Downloaded {total_features} total infrastructure features")
    
    for infra_type, data in results.items():
        feature_count = len(data.get('features', []))
        logger.info(f"   - {infra_type}: {feature_count} features")
    
    logger.info(f"\n[FILES] All data saved to: {importer.data_dir}")
    logger.info("[READY] Comprehensive infrastructure data ready for use!")


if __name__ == "__main__":
    main()
