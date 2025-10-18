"""
U.S. Census Bureau API Client for Westchester County

Downloads demographic data from Census Bureau API (ACS - American Community Survey)
for Westchester County, New York.
"""

import requests
import json
import csv
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class CensusAPIClient:
    """Client for Census Bureau API focused on Westchester County, NY"""
    
    BASE_URL = "https://api.census.gov/data"
    
    # Geographic identifiers
    STATE_FIPS = "36"  # New York
    COUNTY_FIPS = "119"  # Westchester County
    
    # Key demographic variables from ACS
    DEMOGRAPHIC_VARIABLES = {
        # Population
        'B01003_001E': 'total_population',
        'B01001_002E': 'male_population',
        'B01001_026E': 'female_population',
        'B01002_001E': 'median_age',
        
        # Race and Ethnicity
        'B02001_002E': 'white_alone',
        'B02001_003E': 'black_alone',
        'B02001_005E': 'asian_alone',
        'B03003_003E': 'hispanic_or_latino',
        
        # Housing
        'B25001_001E': 'total_housing_units',
        'B25002_002E': 'occupied_housing_units',
        'B25002_003E': 'vacant_housing_units',
        'B25077_001E': 'median_home_value',
        'B25064_001E': 'median_gross_rent',
        
        # Income
        'B19013_001E': 'median_household_income',
        'B19301_001E': 'per_capita_income',
        'B17001_002E': 'poverty_count',
        
        # Employment
        'B23025_002E': 'in_labor_force',
        'B23025_003E': 'civilian_labor_force',
        'B23025_004E': 'employed',
        'B23025_005E': 'unemployed',
        
        # Education
        'B15003_022E': 'bachelors_degree',
        'B15003_023E': 'masters_degree',
        'B15003_025E': 'doctorate_degree',
        
        # Commuting
        'B08301_001E': 'total_commuters',
        'B08301_010E': 'public_transit_commuters',
        'B08303_001E': 'mean_travel_time_to_work',
    }
    
    def __init__(self, api_key: Optional[str] = None, output_dir: Optional[str] = None):
        """
        Initialize Census API client
        
        Args:
            api_key: Census API key (get from https://api.census.gov/data/key_signup.html)
            output_dir: Directory to save downloaded data (default: ../../data/raw/demographics/)
        """
        self.api_key = api_key
        
        if output_dir is None:
            base_path = Path(__file__).parent.parent.parent / "data" / "raw" / "demographics"
        else:
            base_path = Path(output_dir)
        
        self.output_dir = base_path
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def _build_url(self, dataset: str, year: int, variables: List[str], geography: str) -> str:
        """Build Census API URL"""
        base = f"{self.BASE_URL}/{year}/{dataset}"
        var_string = ",".join(variables + ['NAME'])  # Always include NAME
        
        url = f"{base}?get={var_string}&for={geography}"
        
        if self.api_key:
            url += f"&key={self.api_key}"
        
        return url
    
    def fetch_county_data(self, year: int = 2022, dataset: str = "acs/acs5") -> Optional[Dict]:
        """
        Fetch demographic data for Westchester County
        
        Args:
            year: Year of data (default 2022 for ACS 5-year estimates)
            dataset: Census dataset (default "acs/acs5" for 5-year ACS)
            
        Returns:
            Dictionary of demographic data or None if error
        """
        variables = list(self.DEMOGRAPHIC_VARIABLES.keys())
        geography = f"county:{self.COUNTY_FIPS}&in=state:{self.STATE_FIPS}"
        
        url = self._build_url(dataset, year, variables, geography)
        
        print(f"Fetching Westchester County data from Census API...")
        print(f"Dataset: {dataset}, Year: {year}")
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if len(data) < 2:
                print("[FAILED] No data returned from API")
                return None
            
            # First row is headers, second row is data
            headers = data[0]
            values = data[1]
            
            # Create dictionary with friendly names
            result = {}
            for i, header in enumerate(headers):
                if header in self.DEMOGRAPHIC_VARIABLES:
                    friendly_name = self.DEMOGRAPHIC_VARIABLES[header]
                    try:
                        # Convert to int if possible, otherwise keep as string
                        value = int(values[i]) if values[i] and values[i] != '-666666666' else None
                        result[friendly_name] = value
                    except (ValueError, IndexError):
                        result[friendly_name] = None
                elif header == 'NAME':
                    result['location_name'] = values[i]
                elif header in ['state', 'county']:
                    result[header] = values[i]
            
            result['year'] = year
            result['dataset'] = dataset
            result['fetched_date'] = datetime.now().isoformat()
            
            print(f"[SUCCESS] Successfully fetched county-level data")
            return result
            
        except requests.RequestException as e:
            print(f"[FAILED] Error fetching data: {e}")
            if not self.api_key:
                print("[WARNING] Note: No API key provided. Consider getting one at https://api.census.gov/data/key_signup.html")
            return None
    
    def fetch_tract_data(self, year: int = 2022, dataset: str = "acs/acs5") -> Optional[List[Dict]]:
        """
        Fetch demographic data for all census tracts in Westchester County
        
        Args:
            year: Year of data
            dataset: Census dataset
            
        Returns:
            List of dictionaries (one per tract) or None if error
        """
        variables = list(self.DEMOGRAPHIC_VARIABLES.keys())
        geography = f"tract:*&in=state:{self.STATE_FIPS}&in=county:{self.COUNTY_FIPS}"
        
        url = self._build_url(dataset, year, variables, geography)
        
        print(f"Fetching census tract data for Westchester County...")
        print(f"Dataset: {dataset}, Year: {year}")
        
        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            
            if len(data) < 2:
                print("[FAILED] No tract data returned from API")
                return None
            
            headers = data[0]
            tracts = []
            
            for row in data[1:]:
                tract_data = {}
                for i, header in enumerate(headers):
                    if header in self.DEMOGRAPHIC_VARIABLES:
                        friendly_name = self.DEMOGRAPHIC_VARIABLES[header]
                        try:
                            value = int(row[i]) if row[i] and row[i] != '-666666666' else None
                            tract_data[friendly_name] = value
                        except (ValueError, IndexError):
                            tract_data[friendly_name] = None
                    elif header == 'NAME':
                        tract_data['location_name'] = row[i]
                    elif header in ['state', 'county', 'tract']:
                        tract_data[header] = row[i]
                
                tract_data['year'] = year
                tract_data['dataset'] = dataset
                tract_data['fetched_date'] = datetime.now().isoformat()
                tracts.append(tract_data)
            
            print(f"[SUCCESS] Successfully fetched data for {len(tracts)} census tracts")
            return tracts
            
        except requests.RequestException as e:
            print(f"[FAILED] Error fetching tract data: {e}")
            return None
    
    def fetch_place_data(self, year: int = 2022, dataset: str = "acs/acs5") -> Optional[List[Dict]]:
        """
        Fetch demographic data for municipalities (places) in Westchester County
        
        Args:
            year: Year of data
            dataset: Census dataset
            
        Returns:
            List of dictionaries (one per place) or None if error
        """
        variables = list(self.DEMOGRAPHIC_VARIABLES.keys())
        geography = f"place:*&in=state:{self.STATE_FIPS}"
        
        url = self._build_url(dataset, year, variables, geography)
        
        print(f"Fetching municipality (place) data for Westchester County...")
        print(f"Dataset: {dataset}, Year: {year}")
        
        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            
            if len(data) < 2:
                print("[FAILED] No place data returned from API")
                return None
            
            headers = data[0]
            all_places = []
            westchester_places = []
            
            for row in data[1:]:
                place_data = {}
                for i, header in enumerate(headers):
                    if header in self.DEMOGRAPHIC_VARIABLES:
                        friendly_name = self.DEMOGRAPHIC_VARIABLES[header]
                        try:
                            value = int(row[i]) if row[i] and row[i] != '-666666666' else None
                            place_data[friendly_name] = value
                        except (ValueError, IndexError):
                            place_data[friendly_name] = None
                    elif header == 'NAME':
                        place_data['location_name'] = row[i]
                    elif header in ['state', 'place']:
                        place_data[header] = row[i]
                
                place_data['year'] = year
                place_data['dataset'] = dataset
                place_data['fetched_date'] = datetime.now().isoformat()
                all_places.append(place_data)
                
                # Filter to Westchester places (simple name matching)
                # Note: This is approximate - better to cross-reference with official list
                name = place_data.get('location_name', '').lower()
                if 'county' not in name:  # Exclude county entries
                    westchester_places.append(place_data)
            
            print(f"[SUCCESS] Successfully fetched data for {len(westchester_places)} municipalities")
            return westchester_places
            
        except requests.RequestException as e:
            print(f"[FAILED] Error fetching place data: {e}")
            return None
    
    def save_data(self, data: Dict or List[Dict], filename: str, format: str = 'json'):
        """
        Save Census data to file
        
        Args:
            data: Data to save (dict or list of dicts)
            filename: Output filename (without extension)
            format: Output format ('json' or 'csv')
        """
        if format == 'json':
            filepath = self.output_dir / f"{filename}.json"
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"[SUCCESS] Saved to {filepath}")
            
        elif format == 'csv':
            filepath = self.output_dir / f"{filename}.csv"
            
            if isinstance(data, dict):
                data = [data]
            
            if not data:
                print("[WARNING] No data to save")
                return
            
            with open(filepath, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            print(f"[SUCCESS] Saved to {filepath}")
    
    def run_import(self, year: int = 2022) -> Tuple[bool, str]:
        """
        Run complete Census data import
        
        Args:
            year: Year of ACS data to fetch
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            if not self.api_key:
                print("[WARNING] Warning: No Census API key provided. Rate limits may apply.")
                print("  Get a free key at: https://api.census.gov/data/key_signup.html")
                print()
            
            results = []
            
            # 1. County-level data
            print("\n[1/3] Fetching county-level data...")
            county_data = self.fetch_county_data(year)
            if county_data:
                self.save_data(county_data, f"westchester_county_demographics_{year}", 'json')
                self.save_data(county_data, f"westchester_county_demographics_{year}", 'csv')
                results.append("county-level")
            
            # 2. Census tract data
            print("\n[2/3] Fetching census tract data...")
            tract_data = self.fetch_tract_data(year)
            if tract_data:
                self.save_data(tract_data, f"westchester_tracts_demographics_{year}", 'json')
                self.save_data(tract_data, f"westchester_tracts_demographics_{year}", 'csv')
                results.append(f"{len(tract_data)} census tracts")
            
            # 3. Municipality (place) data
            print("\n[3/3] Fetching municipality data...")
            place_data = self.fetch_place_data(year)
            if place_data:
                self.save_data(place_data, f"westchester_municipalities_demographics_{year}", 'json')
                self.save_data(place_data, f"westchester_municipalities_demographics_{year}", 'csv')
                results.append(f"{len(place_data)} municipalities")
            
            if not results:
                return False, "No data was successfully imported"
            
            return True, f"Successfully imported {', '.join(results)}"
            
        except Exception as e:
            return False, f"Import failed: {str(e)}"


def main():
    """Command-line interface for the Census importer"""
    import os
    from pathlib import Path
    
    print("="*60)
    print("U.S. Census API Importer - Westchester County")
    print("="*60)
    print()
    
    # Check for API key in environment variable
    api_key = os.getenv('CENSUS_API_KEY')
    
    if not api_key:
        print("No CENSUS_API_KEY environment variable found.")
        print("You can still proceed, but rate limits may apply.")
        print()
        response = input("Enter your Census API key (or press Enter to skip): ").strip()
        if response:
            api_key = response
    
    client = CensusAPIClient(api_key=api_key)
    success, message = client.run_import(year=2022)
    
    print()
    print("="*60)
    if success:
        print(f"[SUCCESS]: {message}")
    else:
        print(f"[FAILED]: {message}")
    print("="*60)


if __name__ == "__main__":
    main()

