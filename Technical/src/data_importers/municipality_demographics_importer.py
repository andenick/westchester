import requests
import json
from pathlib import Path
import logging
from typing import Dict, Any, List
import time

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

class MunicipalityDemographicsImporter:
    def __init__(self, data_dir: Path = Path("Projects/Westchester/Technical/data/raw/demographics")):
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Census API configuration
        self.census_api_key = "34698fc70a13bd2943ebbd4e720192030e5a824f"  # From Robin
        self.base_url = "https://api.census.gov/data"
        
        # Geographic identifiers
        self.state_fips = "36"  # New York
        self.county_fips = "119"  # Westchester County
        
        # Westchester municipalities with their place codes
        self.municipalities = {
            # Cities
            "Yonkers": {"type": "City", "place_code": "84000", "population": 211569},
            "New Rochelle": {"type": "City", "place_code": "50034", "population": 79446},
            "Mount Vernon": {"type": "City", "place_code": "49121", "population": 73893},
            "White Plains": {"type": "City", "place_code": "81677", "population": 59559},
            "Rye": {"type": "City", "place_code": "64203", "population": 16630},
            
            # Towns (with CDPs)
            "Greenburgh": {"type": "Town", "place_code": "30575", "population": 95397},
            "Mamaroneck": {"type": "Town", "place_code": "44789", "population": 31758},
            "Harrison": {"type": "Town", "place_code": "32548", "population": 28218},
            "Mount Pleasant": {"type": "Town", "place_code": "49000", "population": 44636},
            "New Castle": {"type": "Town", "place_code": "50000", "population": 18847},
            "North Castle": {"type": "Town", "place_code": "51375", "population": 12303},
            "Pound Ridge": {"type": "Town", "place_code": "59673", "population": 5199},
            "Lewisboro": {"type": "Town", "place_code": "42150", "population": 12539},
            "North Salem": {"type": "Town", "place_code": "53486", "population": 5093},
            "Somers": {"type": "Town", "place_code": "68320", "population": 21083},
            "Yorktown": {"type": "Town", "place_code": "83974", "population": 37072},
            "Cortlandt": {"type": "Town", "place_code": "18382", "population": 42334},
            "Peekskill": {"type": "City", "place_code": "56788", "population": 25431},
            "Ossining": {"type": "Town", "place_code": "55689", "population": 39531},
            "Bedford": {"type": "Town", "place_code": "05500", "population": 17489},
            
            # Villages
            "Port Chester": {"type": "Village", "place_code": "59438", "population": 30322},
            "Scarsdale": {"type": "Village", "place_code": "65508", "population": 17892},
            "Bronxville": {"type": "Village", "place_code": "08600", "population": 6542},
            "Tuckahoe": {"type": "Village", "place_code": "75850", "population": 6659},
            "Pelham": {"type": "Village", "place_code": "56775", "population": 6979},
            "Pelham Manor": {"type": "Village", "place_code": "56780", "population": 5736},
            "Larchmont": {"type": "Village", "place_code": "41375", "population": 6109},
            "Mamaroneck Village": {"type": "Village", "place_code": "44790", "population": 19219},
            "Rye Brook": {"type": "Village", "place_code": "64205", "population": 9608},
            "Ardsley": {"type": "Village", "place_code": "02675", "population": 4649},
            "Dobbs Ferry": {"type": "Village", "place_code": "20650", "population": 11254},
            "Hastings-on-Hudson": {"type": "Village", "place_code": "32675", "population": 8209},
            "Irvington": {"type": "Village", "place_code": "37800", "population": 6662},
            "Tarrytown": {"type": "Village", "place_code": "73250", "population": 11727},
            "Sleepy Hollow": {"type": "Village", "place_code": "67650", "population": 10077},
            "Briarcliff Manor": {"type": "Village", "place_code": "08250", "population": 7711},
            "Croton-on-Hudson": {"type": "Village", "place_code": "19250", "population": 8327},
            "Buchanan": {"type": "Village", "place_code": "10300", "population": 2259},
            "Elmsford": {"type": "Village", "place_code": "24075", "population": 5177}
        }
        
        # Key demographic variables from ACS
        self.demographic_variables = {
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
            
            # Education
            'B15003_022E': 'bachelors_degree',
            'B15003_023E': 'masters_degree',
            'B15003_024E': 'doctorate_degree',
            
            # Employment
            'B23025_003E': 'civilian_labor_force',
            'B23025_005E': 'unemployed',
            'B23025_004E': 'employed'
        }

    def fetch_municipality_data(self, municipality_name: str, year: int = 2022) -> Dict[str, Any]:
        """
        Fetch demographic data for a specific municipality.
        """
        if municipality_name not in self.municipalities:
            logger.warning(f"Unknown municipality: {municipality_name}")
            return None
        
        muni_info = self.municipalities[municipality_name]
        place_code = muni_info["place_code"]
        
        logger.info(f"   [FETCH] {municipality_name} (place: {place_code})")
        
        # Build API URL
        variables = list(self.demographic_variables.keys())
        variables_str = ','.join(variables)
        
        url = f"{self.base_url}/{year}/acs/acs5"
        params = {
            'get': f'NAME,{variables_str}',
            'for': f'place:{place_code}',
            'in': f'state:{self.state_fips}',
            'key': self.census_api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if len(data) < 2:
                logger.warning(f"   [WARNING] No data for {municipality_name}")
                return None
            
            # First row is headers, second row is data
            headers = data[0]
            values = data[1]
            
            # Create result dictionary
            result = {
                'municipality_name': municipality_name,
                'municipality_type': muni_info["type"],
                'place_code': place_code,
                'state_fips': self.state_fips,
                'county_fips': self.county_fips,
                'year': year,
                'dataset': 'acs/acs5',
                'fetched_date': time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Map Census variables to friendly names
            for i, header in enumerate(headers):
                if header in self.demographic_variables:
                    friendly_name = self.demographic_variables[header]
                    try:
                        # Convert to int if possible, otherwise keep as string
                        value = int(values[i]) if values[i] and values[i] != '-666666666' else None
                        result[friendly_name] = value
                    except (ValueError, IndexError):
                        result[friendly_name] = None
                elif header == 'NAME':
                    result['location_name'] = values[i]
            
            logger.info(f"   [SUCCESS] {municipality_name}: {result.get('total_population', 0):,} population")
            return result
            
        except Exception as e:
            logger.error(f"   [ERROR] Failed to fetch {municipality_name}: {e}")
            return None

    def download_all_municipalities(self, year: int = 2022) -> Dict[str, Any]:
        """
        Download demographic data for all Westchester municipalities.
        """
        logger.info("\n" + "="*80)
        logger.info("WESTCHESTER MUNICIPALITY DEMOGRAPHICS DOWNLOAD")
        logger.info("="*80)
        logger.info(f"Year: {year}")
        logger.info(f"Municipalities: {len(self.municipalities)}")
        
        all_municipality_data = []
        successful_downloads = 0
        
        for i, municipality_name in enumerate(self.municipalities.keys(), 1):
            logger.info(f"[{i}/{len(self.municipalities)}] Processing {municipality_name}...")
            
            muni_data = self.fetch_municipality_data(municipality_name, year)
            
            if muni_data:
                all_municipality_data.append(muni_data)
                successful_downloads += 1
            
            # Rate limiting - Census API has limits
            time.sleep(0.5)
        
        # Create consolidated dataset
        consolidated_data = {
            'metadata': {
                'generated': time.strftime("%Y-%m-%d %H:%M:%S"),
                'county': 'Westchester County, NY',
                'state': 'New York',
                'year': year,
                'dataset': 'acs/acs5',
                'total_municipalities': len(self.municipalities),
                'successful_downloads': successful_downloads,
                'source': 'U.S. Census Bureau American Community Survey'
            },
            'municipalities': all_municipality_data,
            'summary_statistics': self._calculate_summary_stats(all_municipality_data)
        }
        
        # Save consolidated data
        output_file = self.data_dir / f"westchester_municipalities_demographics_{year}.json"
        with open(output_file, 'w') as f:
            json.dump(consolidated_data, f, indent=2)
        
        logger.info(f"\n[SUCCESS] Municipality demographics saved: {output_file}")
        
        # Save individual municipality files
        for muni_data in all_municipality_data:
            muni_name = muni_data['municipality_name'].lower().replace(' ', '_').replace('-', '_')
            individual_file = self.data_dir / f"{muni_name}_demographics_{year}.json"
            with open(individual_file, 'w') as f:
                json.dump(muni_data, f, indent=2)
        
        return consolidated_data

    def _calculate_summary_stats(self, municipality_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate summary statistics across all municipalities.
        """
        if not municipality_data:
            return {}
        
        total_pop = sum(m.get('total_population', 0) or 0 for m in municipality_data)
        total_housing = sum(m.get('total_housing_units', 0) or 0 for m in municipality_data)
        
        # Calculate weighted averages for income (weighted by population)
        weighted_income = 0
        weighted_rent = 0
        weighted_home_value = 0
        pop_weight_total = 0
        
        for muni in municipality_data:
            pop = muni.get('total_population', 0) or 0
            if pop > 0:
                income = muni.get('median_household_income', 0) or 0
                rent = muni.get('median_gross_rent', 0) or 0
                home_value = muni.get('median_home_value', 0) or 0
                
                weighted_income += income * pop
                weighted_rent += rent * pop
                weighted_home_value += home_value * pop
                pop_weight_total += pop
        
        avg_income = weighted_income / pop_weight_total if pop_weight_total > 0 else 0
        avg_rent = weighted_rent / pop_weight_total if pop_weight_total > 0 else 0
        avg_home_value = weighted_home_value / pop_weight_total if pop_weight_total > 0 else 0
        
        return {
            'total_population': total_pop,
            'total_housing_units': total_housing,
            'municipality_count': len(municipality_data),
            'weighted_average_income': round(avg_income, 2),
            'weighted_average_rent': round(avg_rent, 2),
            'weighted_average_home_value': round(avg_home_value, 2),
            'population_range': {
                'min': min(m.get('total_population', 0) or 0 for m in municipality_data),
                'max': max(m.get('total_population', 0) or 0 for m in municipality_data)
            }
        }

    def create_municipality_comparison_data(self, year: int = 2022) -> Dict[str, Any]:
        """
        Create comparison data for municipality selector/dropdown.
        """
        logger.info("\n[COMPARISON] Creating municipality comparison data...")
        
        comparison_data = {
            'metadata': {
                'generated': time.strftime("%Y-%m-%d %H:%M:%S"),
                'purpose': 'Municipality selector and comparison tool',
                'year': year
            },
            'municipalities': []
        }
        
        # Read the consolidated data
        consolidated_file = self.data_dir / f"westchester_municipalities_demographics_{year}.json"
        
        if not consolidated_file.exists():
            logger.warning("   [WARNING] Consolidated data not found. Run download_all_municipalities first.")
            return comparison_data
        
        with open(consolidated_file, 'r') as f:
            consolidated_data = json.load(f)
        
        # Create simplified comparison records
        for muni_data in consolidated_data.get('municipalities', []):
            comparison_record = {
                'name': muni_data['municipality_name'],
                'type': muni_data['municipality_type'],
                'place_code': muni_data['place_code'],
                'population': muni_data.get('total_population', 0),
                'median_income': muni_data.get('median_household_income', 0),
                'median_home_value': muni_data.get('median_home_value', 0),
                'median_age': muni_data.get('median_age', 0),
                'white_pct': self._calculate_percentage(muni_data, 'white_alone', 'total_population'),
                'hispanic_pct': self._calculate_percentage(muni_data, 'hispanic_or_latino', 'total_population'),
                'bachelors_pct': self._calculate_percentage(muni_data, 'bachelors_degree', 'total_population')
            }
            comparison_data['municipalities'].append(comparison_record)
        
        # Sort by population (largest first)
        comparison_data['municipalities'].sort(key=lambda x: x['population'], reverse=True)
        
        # Save comparison data
        comparison_file = self.data_dir / f"municipality_comparison_{year}.json"
        with open(comparison_file, 'w') as f:
            json.dump(comparison_data, f, indent=2)
        
        logger.info(f"   [SUCCESS] Comparison data saved: {comparison_file}")
        
        return comparison_data

    def _calculate_percentage(self, data: Dict[str, Any], numerator_key: str, denominator_key: str) -> float:
        """Calculate percentage with error handling."""
        numerator = data.get(numerator_key, 0) or 0
        denominator = data.get(denominator_key, 0) or 0
        
        if denominator > 0:
            return round((numerator / denominator) * 100, 1)
        return 0.0


def main():
    """Download municipality-level demographics for all Westchester municipalities"""
    importer = MunicipalityDemographicsImporter()
    
    logger.info("[START] Starting municipality demographics download...")
    logger.info("   This will download demographic data for all 45+ municipalities")
    logger.info("   in Westchester County using the Census ACS API.")
    
    # Download all municipality data
    consolidated_data = importer.download_all_municipalities(2022)
    
    # Create comparison data
    comparison_data = importer.create_municipality_comparison_data(2022)
    
    logger.info("\n" + "="*80)
    logger.info("MUNICIPALITY DEMOGRAPHICS DOWNLOAD COMPLETE!")
    logger.info("="*80)
    
    summary = consolidated_data.get('summary_statistics', {})
    logger.info(f"[SUCCESS] Downloaded data for {summary.get('municipality_count', 0)} municipalities")
    logger.info(f"[SUCCESS] Total population: {summary.get('total_population', 0):,}")
    logger.info(f"[SUCCESS] Total housing units: {summary.get('total_housing_units', 0):,}")
    logger.info(f"[SUCCESS] Average income: ${summary.get('weighted_average_income', 0):,.0f}")
    
    logger.info(f"\n[FILES] All data saved to: {importer.data_dir}")
    logger.info("[READY] Municipality demographics ready for use!")


if __name__ == "__main__":
    main()
