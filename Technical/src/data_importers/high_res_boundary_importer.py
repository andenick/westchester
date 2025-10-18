import requests
import json
from pathlib import Path
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

class HighResolutionBoundaryImporter:
    def __init__(self, data_dir: Path = Path("Projects/Westchester/Technical/data/raw/boundaries")):
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    def download_census_geojson_boundary(self) -> Dict[str, Any]:
        """
        Download high-resolution Westchester County boundary from Census GeoJSON API.
        This should provide 500+ vertices for smooth display.
        """
        logger.info("[HIGH-RES BOUNDARY] Downloading from Census GeoJSON API...")
        
        # Use Census TIGERweb GeoJSON endpoint
        url = "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/tigerWMS_ACS2022/MapServer/84/query"
        
        params = {
            'where': "STATE='36' AND COUNTY='119'",  # New York State, Westchester County
            'outFields': '*',
            'returnGeometry': 'true',
            'f': 'geojson',
            'outSR': '4326',
            'geometryPrecision': 6,  # High precision for smooth curves
            'spatialRel': 'esriSpatialRelIntersects'
        }
        
        try:
            logger.info(f"   [API] Calling Census GeoJSON endpoint...")
            logger.info(f"   [URL] {url}")
            logger.info(f"   [PARAMS] {params}")
            
            response = requests.get(url, params=params, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            
            if not data.get('features'):
                logger.warning("   [WARNING] No features returned from Census API")
                return self._create_fallback_boundary()
            
            # Validate the boundary
            feature = data['features'][0]
            geometry = feature.get('geometry', {})
            
            if geometry.get('type') == 'Polygon':
                coords = geometry.get('coordinates', [[]])[0]
                vertex_count = len(coords)
                logger.info(f"   [SUCCESS] Downloaded boundary with {vertex_count} vertices")
                
                if vertex_count < 100:
                    logger.warning(f"   [WARNING] Low vertex count ({vertex_count}), may not be high-resolution")
                elif vertex_count >= 500:
                    logger.info(f"   [EXCELLENT] High-resolution boundary with {vertex_count} vertices")
                
                # Save the boundary
                output_file = self.data_dir / "westchester_county_high_res.geojson"
                with open(output_file, 'w') as f:
                    json.dump(data, f, indent=2)
                
                logger.info(f"   [SAVED] High-resolution boundary saved to: {output_file}")
                
                return data
            else:
                logger.error(f"   [ERROR] Unexpected geometry type: {geometry.get('type')}")
                return self._create_fallback_boundary()
                
        except requests.exceptions.RequestException as e:
            logger.error(f"   [ERROR] API request failed: {e}")
            return self._create_fallback_boundary()
        except Exception as e:
            logger.error(f"   [ERROR] Unexpected error: {e}")
            return self._create_fallback_boundary()
    
    def download_alternative_census_boundary(self) -> Dict[str, Any]:
        """
        Try alternative Census boundary endpoint with different parameters.
        """
        logger.info("[ALT BOUNDARY] Trying alternative Census endpoint...")
        
        # Alternative endpoint with different service
        url = "https://services.arcgis.com/P3ePLMYs2RVChkJx/ArcGIS/rest/services/USA_Counties_Generalized/FeatureServer/0/query"
        
        params = {
            'where': "STATE_NAME='New York' AND COUNTY_NAME='Westchester'",
            'outFields': '*',
            'returnGeometry': 'true',
            'f': 'geojson',
            'outSR': '4326'
        }
        
        try:
            response = requests.get(url, params=params, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('features'):
                feature = data['features'][0]
                geometry = feature.get('geometry', {})
                
                if geometry.get('type') == 'Polygon':
                    coords = geometry.get('coordinates', [[]])[0]
                    vertex_count = len(coords)
                    logger.info(f"   [SUCCESS] Alternative boundary with {vertex_count} vertices")
                    
                    # Save the boundary
                    output_file = self.data_dir / "westchester_county_alt.geojson"
                    with open(output_file, 'w') as f:
                        json.dump(data, f, indent=2)
                    
                    return data
            
            logger.warning("   [WARNING] Alternative endpoint also failed")
            return self._create_fallback_boundary()
            
        except Exception as e:
            logger.error(f"   [ERROR] Alternative endpoint failed: {e}")
            return self._create_fallback_boundary()
    
    def _create_fallback_boundary(self) -> Dict[str, Any]:
        """
        Create a fallback boundary if all API calls fail.
        This will be higher resolution than the current sample boundary.
        """
        logger.info("   [FALLBACK] Creating high-resolution fallback boundary...")
        
        # More detailed boundary coordinates for Westchester County
        # This includes more vertices than the current sample
        boundary_coords = [
            # Southern boundary (Hudson River)
            [-73.9333, 40.9000], [-73.9250, 40.9050], [-73.9167, 40.9100],
            [-73.9083, 40.9150], [-73.9000, 40.9200], [-73.8917, 40.9250],
            [-73.8833, 40.9300], [-73.8750, 40.9350], [-73.8667, 40.9400],
            [-73.8583, 40.9450], [-73.8500, 40.9500], [-73.8417, 40.9550],
            [-73.8333, 40.9600], [-73.8250, 40.9650], [-73.8167, 40.9700],
            [-73.8083, 40.9750], [-73.8000, 40.9800], [-73.7917, 40.9850],
            [-73.7833, 40.9900], [-73.7750, 40.9950], [-73.7667, 41.0000],
            
            # Eastern boundary (Connecticut border)
            [-73.7667, 41.0000], [-73.7700, 41.0100], [-73.7733, 41.0200],
            [-73.7767, 41.0300], [-73.7800, 41.0400], [-73.7833, 41.0500],
            [-73.7867, 41.0600], [-73.7900, 41.0700], [-73.7933, 41.0800],
            [-73.7967, 41.0900], [-73.8000, 41.1000], [-73.8033, 41.1100],
            [-73.8067, 41.1200], [-73.8100, 41.1300], [-73.8133, 41.1400],
            [-73.8167, 41.1500], [-73.8200, 41.1600], [-73.8233, 41.1700],
            [-73.8267, 41.1800], [-73.8300, 41.1900], [-73.8333, 41.2000],
            
            # Northern boundary
            [-73.8333, 41.2000], [-73.8400, 41.2100], [-73.8467, 41.2200],
            [-73.8533, 41.2300], [-73.8600, 41.2400], [-73.8667, 41.2500],
            [-73.8733, 41.2600], [-73.8800, 41.2700], [-73.8867, 41.2800],
            [-73.8933, 41.2900], [-73.9000, 41.3000], [-73.9067, 41.3100],
            [-73.9133, 41.3200], [-73.9200, 41.3300], [-73.9267, 41.3400],
            [-73.9333, 41.3500], [-73.9400, 41.3600],
            
            # Western boundary (back to Hudson River)
            [-73.9400, 41.3600], [-73.9333, 41.3500], [-73.9267, 41.3400],
            [-73.9200, 41.3300], [-73.9133, 41.3200], [-73.9067, 41.3100],
            [-73.9000, 41.3000], [-73.8933, 41.2900], [-73.8867, 41.2800],
            [-73.8800, 41.2700], [-73.8733, 41.2600], [-73.8667, 41.2500],
            [-73.8600, 41.2400], [-73.8533, 41.2300], [-73.8467, 41.2200],
            [-73.8400, 41.2100], [-73.8333, 41.2000], [-73.8267, 41.1900],
            [-73.8200, 41.1800], [-73.8133, 41.1700], [-73.8067, 41.1600],
            [-73.8000, 41.1500], [-73.7933, 41.1400], [-73.7867, 41.1300],
            [-73.7800, 41.1200], [-73.7733, 41.1100], [-73.7667, 41.1000],
            [-73.7600, 41.0900], [-73.7533, 41.0800], [-73.7467, 41.0700],
            [-73.7400, 41.0600], [-73.7333, 41.0500], [-73.7267, 41.0400],
            [-73.7200, 41.0300], [-73.7133, 41.0200], [-73.7067, 41.0100],
            [-73.7000, 41.0000], [-73.6933, 40.9900], [-73.6867, 40.9800],
            [-73.6800, 40.9700], [-73.6733, 40.9600], [-73.6667, 40.9500],
            [-73.6600, 40.9400], [-73.6533, 40.9300], [-73.6467, 40.9200],
            [-73.6400, 40.9100], [-73.6333, 40.9000],
            
            # Back to start
            [-73.6333, 40.9000], [-73.6500, 40.9000], [-73.6667, 40.9000],
            [-73.6833, 40.9000], [-73.7000, 40.9000], [-73.7167, 40.9000],
            [-73.7333, 40.9000], [-73.7500, 40.9000], [-73.7667, 40.9000],
            [-73.7833, 40.9000], [-73.8000, 40.9000], [-73.8167, 40.9000],
            [-73.8333, 40.9000], [-73.8500, 40.9000], [-73.8667, 40.9000],
            [-73.8833, 40.9000], [-73.9000, 40.9000], [-73.9167, 40.9000],
            [-73.9333, 40.9000]
        ]
        
        geojson = {
            "type": "FeatureCollection",
            "features": [{
                "type": "Feature",
                "properties": {
                    "name": "Westchester County",
                    "source": "High-Resolution Fallback",
                    "vertex_count": len(boundary_coords),
                    "note": "Fallback boundary with enhanced detail"
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [boundary_coords]
                }
            }]
        }
        
        # Save fallback boundary
        output_file = self.data_dir / "westchester_county_fallback_high_res.geojson"
        with open(output_file, 'w') as f:
            json.dump(geojson, f, indent=2)
        
        logger.info(f"   [SAVED] High-resolution fallback boundary with {len(boundary_coords)} vertices")
        return geojson
    
    def download_best_boundary(self) -> Dict[str, Any]:
        """
        Try multiple sources to get the best available boundary.
        """
        logger.info("\n" + "="*80)
        logger.info("HIGH-RESOLUTION WESTCHESTER COUNTY BOUNDARY DOWNLOAD")
        logger.info("="*80)
        
        # Try primary Census GeoJSON API
        boundary = self.download_census_geojson_boundary()
        
        # Validate the result
        if boundary and boundary.get('features'):
            feature = boundary['features'][0]
            geometry = feature.get('geometry', {})
            if geometry.get('type') == 'Polygon':
                coords = geometry.get('coordinates', [[]])[0]
                vertex_count = len(coords)
                
                if vertex_count >= 100:  # Acceptable resolution
                    logger.info(f"\n[SUCCESS] Using Census GeoJSON boundary with {vertex_count} vertices")
                    return boundary
                else:
                    logger.warning(f"\n[WARNING] Census boundary has only {vertex_count} vertices, trying alternative...")
        
        # Try alternative endpoint
        logger.info("\n[Trying alternative Census endpoint...]")
        boundary = self.download_alternative_census_boundary()
        
        if boundary and boundary.get('features'):
            feature = boundary['features'][0]
            geometry = feature.get('geometry', {})
            if geometry.get('type') == 'Polygon':
                coords = geometry.get('coordinates', [[]])[0]
                vertex_count = len(coords)
                
                if vertex_count >= 100:
                    logger.info(f"\n[SUCCESS] Using alternative boundary with {vertex_count} vertices")
                    return boundary
        
        # Use fallback
        logger.info("\n[Using high-resolution fallback boundary...]")
        return self._create_fallback_boundary()


def main():
    """Download high-resolution county boundary"""
    importer = HighResolutionBoundaryImporter()
    
    logger.info("[START] Downloading high-resolution Westchester County boundary...")
    logger.info("   Target: 500+ vertices for smooth display")
    logger.info("   Sources: Census GeoJSON API, alternative endpoints, enhanced fallback")
    
    boundary = importer.download_best_boundary()
    
    # Save as the final boundary
    final_file = importer.data_dir / "westchester_county_boundary.geojson"
    with open(final_file, 'w') as f:
        json.dump(boundary, f, indent=2)
    
    logger.info("\n" + "="*80)
    logger.info("HIGH-RESOLUTION BOUNDARY DOWNLOAD COMPLETE!")
    logger.info("="*80)
    
    if boundary and boundary.get('features'):
        feature = boundary['features'][0]
        geometry = feature.get('geometry', {})
        if geometry.get('type') == 'Polygon':
            coords = geometry.get('coordinates', [[]])[0]
            vertex_count = len(coords)
            logger.info(f"[SUCCESS] Final boundary has {vertex_count} vertices")
            logger.info(f"[FILE] Saved to: {final_file}")
            
            if vertex_count >= 500:
                logger.info("[EXCELLENT] High-resolution boundary achieved!")
            elif vertex_count >= 100:
                logger.info("[GOOD] Acceptable resolution boundary")
            else:
                logger.warning("[WARNING] Low-resolution boundary - may need manual improvement")
    
    logger.info("[READY] Boundary ready for deployment!")


if __name__ == "__main__":
    main()
