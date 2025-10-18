#!/usr/bin/env python3
"""
Data Validation Pipeline for Westchester County Data Collection
Validates collected data against JSON schemas and quality standards
Provides comprehensive data quality assessment and reporting
"""

import os
import sys
import json
import logging
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
import jsonschema
from jsonschema import validate, ValidationError, Draft7Validator
import geopandas as gpd
from shapely.geometry import Point, Polygon

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataValidationPipeline:
    """Comprehensive data validation pipeline for Westchester County data"""

    def __init__(self, data_dir: str = None):
        self.data_dir = Path(data_dir or "data")
        self.validation_dir = self.data_dir / "validation"
        self.validation_dir.mkdir(parents=True, exist_ok=True)

        # Validation results
        self.validation_results = {
            'validation_time': datetime.now().isoformat(),
            'datasets_validated': 0,
            'datasets_passed': 0,
            'datasets_failed': 0,
            'total_records_validated': 0,
            'validation_errors': [],
            'validation_warnings': [],
            'quality_scores': {}
        }

        # JSON schemas for different data types
        self.schemas = self._define_schemas()

    def _define_schemas(self) -> Dict[str, Dict]:
        """Define JSON schemas for different data types"""

        schemas = {}

        # Census Data Schema
        schemas['census_data'] = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "Census Data Schema",
            "description": "Schema for U.S. Census demographic data",
            "type": "object",
            "required": ["geography", "year", "variables"],
            "properties": {
                "geography": {
                    "type": "string",
                    "enum": ["county", "tract", "place", "block_group"]
                },
                "year": {
                    "type": "integer",
                    "minimum": 2000,
                    "maximum": 2030
                },
                "variables": {
                    "type": "object",
                    "patternProperties": {
                        "^B[0-9]+": {
                            "type": "object",
                            "required": ["value", "margin_of_error"],
                            "properties": {
                                "value": {"type": "number"},
                                "margin_of_error": {"type": "number", "minimum": 0}
                            }
                        }
                    }
                }
            }
        }

        # Municipal Services Schema
        schemas['municipal_services'] = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "Municipal Services Schema",
            "description": "Schema for municipal services and facilities",
            "type": "object",
            "required": ["type", "geometry", "properties"],
            "properties": {
                "type": {"type": "string", "enum": ["Feature"]},
                "geometry": {
                    "type": "object",
                    "required": ["type", "coordinates"],
                    "properties": {
                        "type": {"type": "string", "enum": ["Point", "Polygon", "MultiPolygon"]},
                        "coordinates": {
                            "type": "array",
                            "items": {"type": "number"}
                        }
                    }
                },
                "properties": {
                    "type": "object",
                    "required": ["name", "amenity", "municipality"],
                    "properties": {
                        "name": {"type": "string", "minLength": 1},
                        "amenity": {"type": "string", "minLength": 1},
                        "municipality": {"type": "string", "minLength": 1},
                        "address": {"type": "string"},
                        "phone": {"type": "string"},
                        "website": {"type": "string", "format": "uri"}
                    }
                }
            }
        }

        # GIS Data Schema
        schemas['gis_data'] = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "GIS Data Schema",
            "description": "Schema for geographic information system data",
            "type": "object",
            "required": ["type", "crs", "features"],
            "properties": {
                "type": {"type": "string", "enum": ["FeatureCollection"]},
                "crs": {
                    "type": "object",
                    "required": ["type", "properties"],
                    "properties": {
                        "type": {"type": "string", "enum": ["name"]},
                        "properties": {
                            "type": "object",
                            "required": ["name"],
                            "properties": {
                                "name": {"type": "string", "pattern": "^EPSG:[0-9]+$"}
                            }
                        }
                    }
                },
                "features": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["type", "geometry", "properties"],
                        "properties": {
                            "type": {"type": "string", "enum": ["Feature"]},
                            "geometry": {"type": "object"},
                            "properties": {"type": "object"}
                        }
                    }
                }
            }
        }

        # Economic Data Schema
        schemas['economic_data'] = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "Economic Data Schema",
            "description": "Schema for economic indicators data",
            "type": "object",
            "required": ["series_id", "observations"],
            "properties": {
                "series_id": {"type": "string", "minLength": 1},
                "title": {"type": "string", "minLength": 1},
                "units": {"type": "string", "minLength": 1},
                "frequency": {"type": "string", "enum": ["D", "W", "M", "Q", "A"]},
                "observations": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["date", "value"],
                        "properties": {
                            "date": {
                                "type": "string",
                                "format": "date",
                                "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}$"
                            },
                            "value": {"type": "number"},
                            "realtime_start": {"type": "string"},
                            "realtime_end": {"type": "string"}
                        }
                    }
                }
            }
        }

        # Transit Data Schema
        schemas['transit_data'] = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "Transit Data Schema",
            "description": "Schema for public transit data",
            "type": "object",
            "required": ["stops", "routes", "trips"],
            "properties": {
                "stops": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["stop_id", "stop_name", "stop_lat", "stop_lon"],
                        "properties": {
                            "stop_id": {"type": "string", "minLength": 1},
                            "stop_name": {"type": "string", "minLength": 1},
                            "stop_lat": {"type": "number", "minimum": -90, "maximum": 90},
                            "stop_lon": {"type": "number", "minimum": -180, "maximum": 180}
                        }
                    }
                },
                "routes": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["route_id", "route_short_name"],
                        "properties": {
                            "route_id": {"type": "string", "minLength": 1},
                            "route_short_name": {"type": "string", "minLength": 1},
                            "route_long_name": {"type": "string"},
                            "route_type": {"type": "integer", "minimum": 0, "maximum": 7}
                        }
                    }
                }
            }
        }

        # Housing Data Schema
        schemas['housing_data'] = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "Housing Data Schema",
            "description": "Schema for housing and urban development data",
            "type": "object",
            "required": ["year", "county_fips", "data_type"],
            "properties": {
                "year": {"type": "integer", "minimum": 2000, "maximum": 2030},
                "county_fips": {"type": "string", "pattern": "^[0-9]{5}$"},
                "state_fips": {"type": "string", "pattern": "^[0-9]{2}$"},
                "data_type": {
                    "type": "string",
                    "enum": ["fair_market_rent", "income_limits", "section8", "multifamily"]
                },
                "values": {
                    "type": "object",
                    "patternProperties": {
                        "^[0-9]BR$": {
                            "type": "object",
                            "required": ["value"],
                            "properties": {
                                "value": {"type": "number", "minimum": 0},
                                "efficiency": {"type": "number", "minimum": 0},
                                "one_bedroom": {"type": "number", "minimum": 0},
                                "two_bedroom": {"type": "number", "minimum": 0},
                                "three_bedroom": {"type": "number", "minimum": 0},
                                "four_bedroom": {"type": "number", "minimum": 0}
                            }
                        }
                    }
                }
            }
        }

        return schemas

    def validate_json_schema(self, data: Dict, schema_name: str) -> Dict[str, Any]:
        """Validate data against JSON schema"""
        if schema_name not in self.schemas:
            return {
                'valid': False,
                'error': f'Schema "{schema_name}" not found',
                'warnings': [],
                'errors': []
            }

        schema = self.schemas[schema_name]
        validator = Draft7Validator(schema)

        errors = list(validator.iter_errors(data))
        warnings = []

        # Convert errors to readable format
        formatted_errors = []
        for error in errors:
            error_path = " -> ".join(str(p) for p in error.absolute_path) if error.absolute_path else "root"
            formatted_errors.append(f"Path: {error_path}, Error: {error.message}")

        # Additional quality checks
        if schema_name == 'municipal_services':
            warnings.extend(self._validate_municipal_services_quality(data))
        elif schema_name == 'census_data':
            warnings.extend(self._validate_census_data_quality(data))
        elif schema_name == 'gis_data':
            warnings.extend(self._validate_gis_data_quality(data))

        return {
            'valid': len(errors) == 0,
            'schema_used': schema_name,
            'errors': formatted_errors,
            'warnings': warnings,
            'error_count': len(errors),
            'warning_count': len(warnings)
        }

    def _validate_municipal_services_quality(self, data: Dict) -> List[str]:
        """Additional quality checks for municipal services data"""
        warnings = []

        if isinstance(data, dict) and 'features' in data:
            for i, feature in enumerate(data['features'][:10]):  # Check first 10 features
                if isinstance(feature, dict) and 'properties' in feature:
                    props = feature['properties']

                    # Check for missing important fields
                    if not props.get('municipality'):
                        warnings.append(f"Feature {i}: Missing municipality")

                    if not props.get('amenity'):
                        warnings.append(f"Feature {i}: Missing amenity type")

                    # Check for Westchester County specific validation
                    if props.get('municipality'):
                        if not self._is_westchester_municipality(props['municipality']):
                            warnings.append(f"Feature {i}: Municipality '{props['municipality']}' may not be in Westchester County")

        return warnings

    def _validate_census_data_quality(self, data: Dict) -> List[str]:
        """Additional quality checks for census data"""
        warnings = []

        if isinstance(data, dict) and 'variables' in data:
            for var_name, var_data in data['variables'].items():
                if isinstance(var_data, dict):
                    # Check for negative population values
                    if var_name.startswith(('B01001', 'B02001')):  # Population variables
                        if var_data.get('value', 0) < 0:
                            warnings.append(f"Variable {var_name}: Negative population value")

                    # Check for unreasonable margin of error
                    value = var_data.get('value', 0)
                    moe = var_data.get('margin_of_error', 0)
                    if value > 0 and moe > value * 2:  # MOE more than 2x the value
                        warnings.append(f"Variable {var_name}: Margin of error seems too large")

        return warnings

    def _validate_gis_data_quality(self, data: Dict) -> List[str]:
        """Additional quality checks for GIS data"""
        warnings = []

        if isinstance(data, dict) and 'features' in data:
            # Check coordinate reference system
            if 'crs' not in data:
                warnings.append("Missing CRS information")

            # Validate geometries
            for i, feature in enumerate(data['features'][:10]):  # Check first 10 features
                if isinstance(feature, dict) and 'geometry' in feature:
                    geom = feature['geometry']
                    if not geom:
                        warnings.append(f"Feature {i}: Missing geometry")
                        continue

                    # Check coordinate validity
                    if geom.get('type') == 'Point' and 'coordinates' in geom:
                        coords = geom['coordinates']
                        if len(coords) >= 2:
                            lon, lat = coords[0], coords[1]
                            if not (-180 <= lon <= 180 and -90 <= lat <= 90):
                                warnings.append(f"Feature {i}: Invalid coordinates ({lon}, {lat})")

                            # Check if coordinates are in Westchester County area
                            if not self._is_westchester_coordinates(lat, lon):
                                warnings.append(f"Feature {i}: Coordinates may not be in Westchester County area")

        return warnings

    def _is_westchester_municipality(self, municipality: str) -> bool:
        """Check if municipality is in Westchester County"""
        westchester_municipalities = {
            'Yonkers', 'New Rochelle', 'Mount Vernon', 'White Plains', 'Peekskill',
            'Rye', 'Hastings-on-Hudson', 'Dobbs Ferry', 'Irvington', 'Tarrytown',
            'Sleepy Hollow', 'Ossining', 'Croton-on-Hudson', 'Yorktown', 'Cortlandt',
            'New Castle', 'Chappaqua', 'Bedford', 'Mount Kisco', 'North Castle',
            'Armonk', 'Greenburgh', 'Scarsdale', 'Eastchester', 'Tuckahoe',
            'Bronxville', 'Pelham', 'Pelham Manor', 'Mamaroneck', 'Larchmont',
            'Rye Brook', 'Port Chester', 'Rye City', 'Harrison', 'Purchase',
            'Rye Neck', 'Blauvelt', 'Grand View', 'Nyack', 'Piermont',
            'Upper Grand View', 'South Nyack', 'Upper Nyack'
        }
        return municipality.strip() in westchester_municipalities

    def _is_westchester_coordinates(self, lat: float, lon: float) -> bool:
        """Check if coordinates are within Westchester County bounds"""
        # Westchester County approximate bounds
        # Northern bound: ~41.3°N
        # Southern bound: ~40.8°N
        # Eastern bound: ~-73.5°W
        # Western bound: ~-74.0°W
        return (40.8 <= lat <= 41.3) and (-74.0 <= lon <= -73.5)

    def validate_dataframe(self, df: pd.DataFrame, dataset_name: str) -> Dict[str, Any]:
        """Validate pandas DataFrame for quality and completeness"""
        validation_result = {
            'dataset_name': dataset_name,
            'total_records': len(df),
            'total_columns': len(df.columns),
            'validation_passed': True,
            'quality_score': 100.0,
            'issues': [],
            'warnings': [],
            'statistics': {}
        }

        try:
            # Basic quality checks
            # 1. Check for empty dataset
            if df.empty:
                validation_result['validation_passed'] = False
                validation_result['issues'].append("Dataset is empty")
                validation_result['quality_score'] = 0.0
                return validation_result

            # 2. Check for duplicate rows
            duplicate_count = df.duplicated().sum()
            if duplicate_count > 0:
                duplicate_pct = (duplicate_count / len(df)) * 100
                if duplicate_pct > 5:  # More than 5% duplicates
                    validation_result['validation_passed'] = False
                    validation_result['issues'].append(f"High duplicate rate: {duplicate_pct:.1f}% ({duplicate_count} rows)")
                    validation_result['quality_score'] -= 20
                else:
                    validation_result['warnings'].append(f"Low duplicate rate: {duplicate_pct:.1f}% ({duplicate_count} rows)")
                    validation_result['quality_score'] -= 5

            # 3. Check for missing values
            missing_analysis = df.isnull().sum()
            total_cells = len(df) * len(df.columns)
            missing_cells = missing_analysis.sum()
            missing_pct = (missing_cells / total_cells) * 100

            if missing_pct > 20:  # More than 20% missing data
                validation_result['validation_passed'] = False
                validation_result['issues'].append(f"High missing data rate: {missing_pct:.1f}%")
                validation_result['quality_score'] -= 30
            elif missing_pct > 5:
                validation_result['warnings'].append(f"Moderate missing data rate: {missing_pct:.1f}%")
                validation_result['quality_score'] -= 10

            # 4. Column-specific validation based on dataset type
            if 'census' in dataset_name.lower():
                validation_result = self._validate_census_dataframe(df, validation_result)
            elif 'transit' in dataset_name.lower():
                validation_result = self._validate_transit_dataframe(df, validation_result)
            elif 'economic' in dataset_name.lower() or 'fred' in dataset_name.lower():
                validation_result = self._validate_economic_dataframe(df, validation_result)
            elif 'gis' in dataset_name.lower() or 'geographic' in dataset_name.lower():
                validation_result = self._validate_gis_dataframe(df, validation_result)

            # 5. Generate basic statistics
            validation_result['statistics'] = {
                'numeric_columns': df.select_dtypes(include=[np.number]).shape[1],
                'text_columns': df.select_dtypes(include=['object']).shape[1],
                'date_columns': df.select_dtypes(include=['datetime']).shape[1],
                'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024 / 1024,
                'missing_data_percentage': missing_pct
            }

        except Exception as e:
            validation_result['validation_passed'] = False
            validation_result['issues'].append(f"Validation error: {str(e)}")
            validation_result['quality_score'] = 0.0

        return validation_result

    def _validate_census_dataframe(self, df: pd.DataFrame, result: Dict) -> Dict:
        """Validate census-specific DataFrame"""
        # Check for required census columns
        required_columns = ['geography', 'year']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            result['validation_passed'] = False
            result['issues'].append(f"Missing required census columns: {missing_columns}")
            result['quality_score'] -= 25

        # Check year range
        if 'year' in df.columns:
            invalid_years = df[~df['year'].between(2000, 2030)]
            if not invalid_years.empty:
                result['warnings'].append(f"Found {len(invalid_years)} records with invalid years")

        # Check for negative population values
        pop_columns = [col for col in df.columns if 'population' in col.lower() or col.startswith(('B01001', 'B02001'))]
        for col in pop_columns:
            if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
                negative_count = (df[col] < 0).sum()
                if negative_count > 0:
                    result['warnings'].append(f"Found {negative_count} negative values in {col}")

        return result

    def _validate_transit_dataframe(self, df: pd.DataFrame, result: Dict) -> Dict:
        """Validate transit-specific DataFrame"""
        # Check for coordinate validity
        if 'stop_lat' in df.columns and 'stop_lon' in df.columns:
            invalid_lat = df[~df['stop_lat'].between(-90, 90)]
            invalid_lon = df[~df['stop_lon'].between(-180, 180)]

            if not invalid_lat.empty:
                result['issues'].append(f"Found {len(invalid_lat)} records with invalid latitude")
                result['quality_score'] -= 15

            if not invalid_lon.empty:
                result['issues'].append(f"Found {len(invalid_lon)} records with invalid longitude")
                result['quality_score'] -= 15

        # Check for required transit fields
        if 'stop_id' in df.columns:
            null_stop_ids = df['stop_id'].isnull().sum()
            if null_stop_ids > 0:
                result['warnings'].append(f"Found {null_stop_ids} records with null stop IDs")

        return result

    def _validate_economic_dataframe(self, df: pd.DataFrame, result: Dict) -> Dict:
        """Validate economic data DataFrame"""
        # Check for date column
        date_columns = [col for col in df.columns if 'date' in col.lower()]
        if date_columns:
            for col in date_columns:
                try:
                    pd.to_datetime(df[col], errors='coerce')
                except:
                    result['warnings'].append(f"Could not parse {col} as dates")

        # Check for value columns
        value_columns = [col for col in df.columns if 'value' in col.lower() or 'amount' in col.lower()]
        for col in value_columns:
            if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
                # Check for extreme outliers (using IQR method)
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR

                outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
                outlier_pct = len(outliers) / len(df) * 100

                if outlier_pct > 10:  # More than 10% outliers
                    result['warnings'].append(f"High outlier rate in {col}: {outlier_pct:.1f}%")

        return result

    def _validate_gis_dataframe(self, df: pd.DataFrame, result: Dict) -> Dict:
        """Validate GIS DataFrame"""
        # Check for coordinate columns
        coord_columns = []
        for col in df.columns:
            if any(coord in col.lower() for coord in ['lat', 'latitude', 'lon', 'longitude', 'x', 'y']):
                coord_columns.append(col)

        if len(coord_columns) >= 2:
            # Assume first two are lat/lon or x/y
            coord1, coord2 = coord_columns[0], coord_columns[1]

            # Check for valid coordinate ranges
            if 'lat' in coord1.lower() or 'latitude' in coord1.lower():
                invalid_count = df[~df[coord1].between(-90, 90)].sum()
                if invalid_count > 0:
                    result['warnings'].append(f"Found {invalid_count} invalid latitude values")

            if 'lon' in coord2.lower() or 'longitude' in coord2.lower():
                invalid_count = df[~df[coord2].between(-180, 180)].sum()
                if invalid_count > 0:
                    result['warnings'].append(f"Found {invalid_count} invalid longitude values")

        return result

    def validate_dataset_file(self, file_path: Path, dataset_type: str = None) -> Dict[str, Any]:
        """Validate a single dataset file"""
        try:
            logger.info(f"Validating dataset: {file_path}")

            # Determine file type and schema
            if file_path.suffix.lower() == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Auto-detect schema if not provided
                if not dataset_type:
                    dataset_type = self._detect_dataset_type(data, file_path.name)

                # Validate against schema
                schema_result = self.validate_json_schema(data, dataset_type)

                result = {
                    'file_path': str(file_path),
                    'dataset_type': dataset_type,
                    'file_size_bytes': file_path.stat().st_size,
                    'validation_method': 'json_schema',
                    'validation_passed': schema_result['valid'],
                    'schema_validation': schema_result
                }

            elif file_path.suffix.lower() in ['.csv', '.xlsx']:
                # Load as DataFrame
                if file_path.suffix.lower() == '.csv':
                    df = pd.read_csv(file_path)
                else:
                    df = pd.read_excel(file_path)

                # Determine dataset type from filename
                if not dataset_type:
                    dataset_type = self._detect_dataset_type_from_filename(file_path.name)

                # Validate DataFrame
                df_validation = self.validate_dataframe(df, dataset_type)

                result = {
                    'file_path': str(file_path),
                    'dataset_type': dataset_type,
                    'file_size_bytes': file_path.stat().st_size,
                    'validation_method': 'dataframe',
                    'validation_passed': df_validation['validation_passed'],
                    'dataframe_validation': df_validation
                }

            elif file_path.suffix.lower() == '.geojson':
                # Load as GeoDataFrame
                gdf = gpd.read_file(file_path)

                # Convert to dict for JSON schema validation
                data = gdf.__geo_interface__

                if not dataset_type:
                    dataset_type = 'gis_data'

                # Validate against GIS schema
                schema_result = self.validate_json_schema(data, dataset_type)

                result = {
                    'file_path': str(file_path),
                    'dataset_type': dataset_type,
                    'file_size_bytes': file_path.stat().st_size,
                    'validation_method': 'geojson_schema',
                    'validation_passed': schema_result['valid'],
                    'schema_validation': schema_result,
                    'feature_count': len(gdf),
                    'geometry_types': gdf.geometry.geom_type.unique().tolist() if not gdf.empty else []
                }

            else:
                result = {
                    'file_path': str(file_path),
                    'validation_passed': False,
                    'error': f"Unsupported file type: {file_path.suffix}"
                }

            return result

        except Exception as e:
            logger.error(f"Error validating {file_path}: {str(e)}")
            return {
                'file_path': str(file_path),
                'validation_passed': False,
                'error': str(e)
            }

    def _detect_dataset_type(self, data: Dict, filename: str) -> str:
        """Auto-detect dataset type from data structure"""
        filename_lower = filename.lower()

        # Check filename for clues
        if 'census' in filename_lower:
            return 'census_data'
        elif 'municipal' in filename_lower or 'services' in filename_lower:
            return 'municipal_services'
        elif 'gis' in filename_lower or 'geographic' in filename_lower:
            return 'gis_data'
        elif 'transit' in filename_lower or 'gtfs' in filename_lower or 'metronorth' in filename_lower:
            return 'transit_data'
        elif 'economic' in filename_lower or 'fred' in filename_lower:
            return 'economic_data'
        elif 'housing' in filename_lower or 'hud' in filename_lower:
            return 'housing_data'

        # Check data structure
        if isinstance(data, dict):
            if 'type' in data and data['type'] == 'FeatureCollection':
                if 'crs' in data:
                    return 'gis_data'
                else:
                    return 'municipal_services'
            elif 'variables' in data and 'geography' in data:
                return 'census_data'
            elif 'series_id' in data and 'observations' in data:
                return 'economic_data'
            elif 'stops' in data and 'routes' in data:
                return 'transit_data'

        # Default to generic validation
        return 'municipal_services'

    def _detect_dataset_type_from_filename(self, filename: str) -> str:
        """Detect dataset type from filename"""
        filename_lower = filename.lower()

        if 'census' in filename_lower:
            return 'census'
        elif 'transit' in filename_lower or 'gtfs' in filename_lower:
            return 'transit'
        elif 'economic' in filename_lower or 'fred' in filename_lower:
            return 'economic'
        elif 'housing' in filename_lower or 'hud' in filename_lower:
            return 'housing'
        elif 'gis' in filename_lower or 'geographic' in filename_lower:
            return 'gis'
        else:
            return 'general'

    def validate_all_datasets(self, scan_directory: str = None) -> Dict[str, Any]:
        """Validate all datasets in the data directory"""
        if scan_directory:
            scan_path = Path(scan_directory)
        else:
            scan_path = self.data_dir

        logger.info(f"Starting comprehensive validation of datasets in: {scan_path}")

        validation_results = {
            'validation_start_time': datetime.now().isoformat(),
            'scan_directory': str(scan_path),
            'datasets_validated': 0,
            'datasets_passed': 0,
            'datasets_failed': 0,
            'total_records_validated': 0,
            'validation_errors': [],
            'validation_warnings': [],
            'quality_scores': {},
            'dataset_results': [],
            'summary_by_type': {}
        }

        # Find all data files
        data_files = []
        for pattern in ['**/*.json', '**/*.csv', '**/*.xlsx', '**/*.geojson']:
            data_files.extend(scan_path.glob(pattern))

        logger.info(f"Found {len(data_files)} data files to validate")

        # Validate each file
        for file_path in data_files:
            result = self.validate_dataset_file(file_path)
            validation_results['dataset_results'].append(result)

            validation_results['datasets_validated'] += 1

            if result.get('validation_passed', False):
                validation_results['datasets_passed'] += 1
            else:
                validation_results['datasets_failed'] += 1

            # Collect errors and warnings
            if 'schema_validation' in result:
                sv = result['schema_validation']
                validation_results['validation_errors'].extend(sv.get('errors', []))
                validation_results['validation_warnings'].extend(sv.get('warnings', []))
            elif 'dataframe_validation' in result:
                dv = result['dataframe_validation']
                validation_results['validation_errors'].extend(dv.get('issues', []))
                validation_results['validation_warnings'].extend(dv.get('warnings', []))

            # Track quality scores
            dataset_type = result.get('dataset_type', 'unknown')
            if dataset_type not in validation_results['summary_by_type']:
                validation_results['summary_by_type'][dataset_type] = {
                    'count': 0,
                    'passed': 0,
                    'failed': 0
                }

            validation_results['summary_by_type'][dataset_type]['count'] += 1
            if result.get('validation_passed', False):
                validation_results['summary_by_type'][dataset_type]['passed'] += 1
            else:
                validation_results['summary_by_type'][dataset_type]['failed'] += 1

        # Calculate overall quality score
        if validation_results['datasets_validated'] > 0:
            pass_rate = (validation_results['datasets_passed'] / validation_results['datasets_validated']) * 100
            validation_results['overall_quality_score'] = pass_rate
        else:
            validation_results['overall_quality_score'] = 0.0

        validation_results['validation_end_time'] = datetime.now().isoformat()

        # Save validation report
        self.save_validation_report(validation_results)

        logger.info(f"Validation complete: {validation_results['datasets_passed']}/{validation_results['datasets_validated']} datasets passed")
        logger.info(f"Overall quality score: {validation_results['overall_quality_score']:.1f}%")

        return validation_results

    def save_validation_report(self, results: Dict[str, Any]) -> None:
        """Save comprehensive validation report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save detailed JSON report
        json_report_path = self.validation_dir / f"validation_report_{timestamp}.json"
        with open(json_report_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)

        # Save human-readable summary
        summary_path = self.validation_dir / f"validation_summary_{timestamp}.md"
        summary_content = self.generate_validation_summary(results)

        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(summary_content)

        logger.info(f"Validation report saved to: {json_report_path}")
        logger.info(f"Validation summary saved to: {summary_path}")

    def generate_validation_summary(self, results: Dict[str, Any]) -> str:
        """Generate human-readable validation summary"""
        summary = []
        summary.append("# Westchester Data Validation Report")
        summary.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        summary.append(f"Scan Directory: {results['scan_directory']}")
        summary.append("")

        # Overall Summary
        summary.append("## Validation Summary")
        summary.append(f"- **Datasets Validated**: {results['datasets_validated']}")
        summary.append(f"- **Datasets Passed**: {results['datasets_passed']}")
        summary.append(f"- **Datasets Failed**: {results['datasets_failed']}")
        summary.append(f"- **Pass Rate**: {results['overall_quality_score']:.1f}%")
        summary.append(f"- **Total Errors**: {len(results['validation_errors'])}")
        summary.append(f"- **Total Warnings**: {len(results['validation_warnings'])}")
        summary.append("")

        # Results by Type
        summary.append("## Results by Dataset Type")
        for dataset_type, type_summary in results['summary_by_type'].items():
            pass_rate = (type_summary['passed'] / type_summary['count']) * 100 if type_summary['count'] > 0 else 0
            summary.append(f"### {dataset_type.title()}")
            summary.append(f"- **Total**: {type_summary['count']}")
            summary.append(f"- **Passed**: {type_summary['passed']}")
            summary.append(f"- **Failed**: {type_summary['failed']}")
            summary.append(f"- **Pass Rate**: {pass_rate:.1f}%")
            summary.append("")

        # Top Issues
        if results['validation_errors']:
            summary.append("## Top Validation Errors")
            for error in results['validation_errors'][:10]:
                summary.append(f"- ❌ {error}")
            if len(results['validation_errors']) > 10:
                summary.append(f"- ... and {len(results['validation_errors']) - 10} more errors")
            summary.append("")

        if results['validation_warnings']:
            summary.append("## Validation Warnings")
            for warning in results['validation_warnings'][:15]:
                summary.append(f"- ⚠️ {warning}")
            if len(results['validation_warnings']) > 15:
                summary.append(f"- ... and {len(results['validation_warnings']) - 15} more warnings")
            summary.append("")

        # Recommendations
        summary.append("## Recommendations")
        if results['overall_quality_score'] >= 90:
            summary.append("✅ **Excellent Data Quality**: Data collection is performing very well")
        elif results['overall_quality_score'] >= 75:
            summary.append("⚠️ **Good Data Quality**: Minor issues should be addressed")
        elif results['overall_quality_score'] >= 50:
            summary.append("❌ **Moderate Data Quality**: Significant issues need attention")
        else:
            summary.append("🚨 **Poor Data Quality**: Major issues require immediate attention")

        summary.append("")
        summary.append("### Next Steps")
        if results['datasets_failed'] > 0:
            summary.append("1. Review and fix failed datasets")
        if len(results['validation_errors']) > 0:
            summary.append("2. Address validation errors systematically")
        if len(results['validation_warnings']) > 0:
            summary.append("3. Review warnings for potential improvements")
        summary.append("4. Re-run validation after fixes")
        summary.append("5. Schedule regular validation checks")

        return "\n".join(summary)

def main():
    """Main function for command line usage"""
    import argparse

    parser = argparse.ArgumentParser(description='Westchester Data Validation Pipeline')
    parser.add_argument('--data-dir', help='Data directory to validate')
    parser.add_argument('--file', help='Validate specific file')
    parser.add_argument('--dataset-type', help='Dataset type for validation')
    parser.add_argument('--output-dir', help='Output directory for validation reports')

    args = parser.parse_args()

    # Initialize validator
    validator = DataValidationPipeline(data_dir=args.data_dir)

    if args.file:
        # Validate single file
        file_path = Path(args.file)
        result = validator.validate_dataset_file(file_path, args.dataset_type)

        print(f"\nValidation Results for {file_path.name}:")
        print(f"Status: {'✅ PASSED' if result.get('validation_passed', False) else '❌ FAILED'}")

        if 'schema_validation' in result:
            sv = result['schema_validation']
            print(f"Errors: {sv['error_count']}")
            print(f"Warnings: {sv['warning_count']}")

            if sv['errors']:
                print("\nErrors:")
                for error in sv['errors']:
                    print(f"  - {error}")

            if sv['warnings']:
                print("\nWarnings:")
                for warning in sv['warnings']:
                    print(f"  - {warning}")

    else:
        # Validate all datasets
        results = validator.validate_all_datasets(args.data_dir)

        print(f"\n📊 Validation Summary:")
        print(f"  Datasets: {results['datasets_validated']}")
        print(f"  Passed: {results['datasets_passed']}")
        print(f"  Failed: {results['datasets_failed']}")
        print(f"  Quality Score: {results['overall_quality_score']:.1f}%")

        if results['validation_errors']:
            print(f"  Errors: {len(results['validation_errors'])}")

        if results['validation_warnings']:
            print(f"  Warnings: {len(results['validation_warnings'])}")

if __name__ == "__main__":
    main()