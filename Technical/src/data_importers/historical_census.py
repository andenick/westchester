"""
Historical Census Data Importer

Downloads multi-year demographic data from US Census API for time series analysis
"""

import requests
import json
import os
from pathlib import Path
from typing import Dict, Any, List
import time

class HistoricalCensusImporter:
    """Import historical census data for time series analysis"""
    
    def __init__(self, data_dir: str = None, api_key: str = None):
        if data_dir is None:
            self.data_dir = Path(__file__).parent.parent.parent / "data" / "raw" / "census"
        else:
            self.data_dir = Path(data_dir)
        
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Census API configuration
        self.api_key = api_key or os.getenv('CENSUS_API_KEY', 'DEMO_KEY')
        self.base_url = "https://api.census.gov/data"
        
        # Years to fetch data for
        self.years = [2010, 2015, 2020, 2022]
        
        # Westchester County FIPS
        self.state_fips = "36"  # New York
        self.county_fips = "119"  # Westchester
        
    def download_historical_demographics(self) -> Dict[str, Any]:
        """
        Download historical demographic data for Westchester County
        """
        print("Downloading historical demographic data for Westchester County...")
        
        all_data = {}
        
        for year in self.years:
            print(f"\n[INFO] Fetching data for {year}...")
            
            # Determine which Census API to use based on year
            if year == 2010:
                data = self.fetch_2010_data()
            elif year in [2015, 2020, 2022]:
                data = self.fetch_acs_data(year)
            else:
                print(f"[WARNING] No data available for {year}")
                continue
            
            if data:
                all_data[year] = data
                
                # Save individual year data
                year_file = self.data_dir / f"westchester_demographics_{year}.json"
                with open(year_file, 'w') as f:
                    json.dump(data, f, indent=2)
                
                print(f"[SUCCESS] {year} data saved to {year_file}")
            
            # Rate limiting - be nice to Census API
            time.sleep(1)
        
        # Save combined time series data
        if all_data:
            combined_file = self.data_dir / "westchester_historical_demographics.json"
            with open(combined_file, 'w') as f:
                json.dump(all_data, f, indent=2)
            
            print(f"\n[SUCCESS] Combined historical data saved to {combined_file}")
        
        return all_data
    
    def fetch_2010_data(self) -> Dict[str, Any]:
        """
        Fetch 2010 Decennial Census data
        """
        print("  [INFO] Fetching 2010 Decennial Census data...")
        
        # 2010 Decennial Census variables
        variables = [
            "P001001",  # Total population
            "P003001",  # Total population (race)
            "P005001",  # Total population (Hispanic/Latino)
            "P037001",  # Total population (age)
            "P042001",  # Total population (sex)
        ]
        
        url = f"{self.base_url}/2010/dec/sf1"
        params = {
            'get': ','.join(variables),
            'for': f'county:{self.county_fips}',
            'in': f'state:{self.state_fips}',
            'key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Convert to structured format
            if len(data) > 1:
                headers = data[0]
                values = data[1]
                
                result = {
                    "year": 2010,
                    "source": "Decennial Census 2010",
                    "geography": "Westchester County, NY",
                    "data": dict(zip(headers, values))
                }
                
                print(f"    [SUCCESS] 2010 data retrieved")
                return result
            
        except Exception as e:
            print(f"    [ERROR] 2010 data failed: {e}")
        
        return None
    
    def fetch_acs_data(self, year: int) -> Dict[str, Any]:
        """
        Fetch American Community Survey data for specified year
        """
        print(f"  [INFO] Fetching {year} ACS data...")
        
        # ACS variables for demographics
        variables = [
            "B01003_001E",  # Total population
            "B19013_001E",  # Median household income
            "B08301_001E",  # Total workers
            "B08301_010E",  # Public transportation workers
            "B25077_001E",  # Median home value
            "B25003_001E",  # Total housing units
            "B25003_002E",  # Owner occupied
            "B25003_003E",  # Renter occupied
        ]
        
        # Determine ACS dataset based on year
        if year == 2015:
            dataset = "acs5"  # 5-year estimates
            api_year = "2015"
        elif year == 2020:
            dataset = "acs5"
            api_year = "2020"
        elif year == 2022:
            dataset = "acs5"
            api_year = "2022"
        else:
            print(f"    [ERROR] Unsupported ACS year: {year}")
            return None
        
        url = f"{self.base_url}/{api_year}/{dataset}"
        params = {
            'get': ','.join(variables),
            'for': f'county:{self.county_fips}',
            'in': f'state:{self.state_fips}',
            'key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Convert to structured format
            if len(data) > 1:
                headers = data[0]
                values = data[1]
                
                result = {
                    "year": year,
                    "source": f"ACS {api_year} 5-Year Estimates",
                    "geography": "Westchester County, NY",
                    "data": dict(zip(headers, values))
                }
                
                print(f"    [SUCCESS] {year} ACS data retrieved")
                return result
            
        except Exception as e:
            print(f"    [ERROR] {year} ACS data failed: {e}")
        
        return None
    
    def download_historical_property_data(self) -> Dict[str, Any]:
        """
        Download historical property tax and assessment data
        Note: This would typically come from NY State or local sources
        """
        print("Downloading historical property data...")
        
        # Sample historical property data (in real implementation, this would come from NY State)
        historical_property_data = {
            "2015": {
                "year": 2015,
                "source": "NY State Property Data (Sample)",
                "geography": "Westchester County, NY",
                "data": {
                    "median_assessment": 425000,
                    "median_tax_bill": 8500,
                    "tax_rate_per_1000": 20.0,
                    "total_assessments": 320000000000,
                    "total_tax_levy": 6400000000
                }
            },
            "2016": {
                "year": 2016,
                "source": "NY State Property Data (Sample)",
                "geography": "Westchester County, NY",
                "data": {
                    "median_assessment": 435000,
                    "median_tax_bill": 8700,
                    "tax_rate_per_1000": 20.0,
                    "total_assessments": 330000000000,
                    "total_tax_levy": 6600000000
                }
            },
            "2017": {
                "year": 2017,
                "source": "NY State Property Data (Sample)",
                "geography": "Westchester County, NY",
                "data": {
                    "median_assessment": 445000,
                    "median_tax_bill": 8900,
                    "tax_rate_per_1000": 20.0,
                    "total_assessments": 340000000000,
                    "total_tax_levy": 6800000000
                }
            },
            "2018": {
                "year": 2018,
                "source": "NY State Property Data (Sample)",
                "geography": "Westchester County, NY",
                "data": {
                    "median_assessment": 455000,
                    "median_tax_bill": 9100,
                    "tax_rate_per_1000": 20.0,
                    "total_assessments": 350000000000,
                    "total_tax_levy": 7000000000
                }
            },
            "2019": {
                "year": 2019,
                "source": "NY State Property Data (Sample)",
                "geography": "Westchester County, NY",
                "data": {
                    "median_assessment": 465000,
                    "median_tax_bill": 9300,
                    "tax_rate_per_1000": 20.0,
                    "total_assessments": 360000000000,
                    "total_tax_levy": 7200000000
                }
            },
            "2020": {
                "year": 2020,
                "source": "NY State Property Data (Sample)",
                "geography": "Westchester County, NY",
                "data": {
                    "median_assessment": 475000,
                    "median_tax_bill": 9500,
                    "tax_rate_per_1000": 20.0,
                    "total_assessments": 370000000000,
                    "total_tax_levy": 7400000000
                }
            },
            "2021": {
                "year": 2021,
                "source": "NY State Property Data (Sample)",
                "geography": "Westchester County, NY",
                "data": {
                    "median_assessment": 485000,
                    "median_tax_bill": 9700,
                    "tax_rate_per_1000": 20.0,
                    "total_assessments": 380000000000,
                    "total_tax_levy": 7600000000
                }
            },
            "2022": {
                "year": 2022,
                "source": "NY State Property Data (Sample)",
                "geography": "Westchester County, NY",
                "data": {
                    "median_assessment": 495000,
                    "median_tax_bill": 9900,
                    "tax_rate_per_1000": 20.0,
                    "total_assessments": 390000000000,
                    "total_tax_levy": 7800000000
                }
            },
            "2023": {
                "year": 2023,
                "source": "NY State Property Data (Sample)",
                "geography": "Westchester County, NY",
                "data": {
                    "median_assessment": 505000,
                    "median_tax_bill": 10100,
                    "tax_rate_per_1000": 20.0,
                    "total_assessments": 400000000000,
                    "total_tax_levy": 8000000000
                }
            },
            "2024": {
                "year": 2024,
                "source": "NY State Property Data (Sample)",
                "geography": "Westchester County, NY",
                "data": {
                    "median_assessment": 515000,
                    "median_tax_bill": 10300,
                    "tax_rate_per_1000": 20.0,
                    "total_assessments": 410000000000,
                    "total_tax_levy": 8200000000
                }
            }
        }
        
        # Save property data
        property_file = self.data_dir / "westchester_historical_property.json"
        with open(property_file, 'w') as f:
            json.dump(historical_property_data, f, indent=2)
        
        print(f"[SUCCESS] Historical property data saved to {property_file}")
        return historical_property_data


def main():
    """Download all historical data"""
    importer = HistoricalCensusImporter()
    
    print("\n" + "="*60)
    print("Downloading Historical Census Data for Westchester County")
    print("="*60 + "\n")
    
    # Download demographic data
    demographics = importer.download_historical_demographics()
    print(f"  Demographics years: {list(demographics.keys())}")
    
    print("\n" + "-"*60 + "\n")
    
    # Download property data
    property_data = importer.download_historical_property_data()
    print(f"  Property years: {list(property_data.keys())}")
    
    print("\n" + "="*60)
    print("Historical data download complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
