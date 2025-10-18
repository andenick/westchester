"""
Regional Comparison Data Importer
Collects county-level demographics for NYC neighboring counties comparable to Westchester
"""

import requests
import json
from pathlib import Path
import logging
from typing import Dict, Any, List
import time

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


class RegionalComparisonImporter:
    def __init__(self, data_dir: Path = None):
        if data_dir is None:
            data_dir = Path("Projects/Westchester/Technical/data/raw/regional_comparison")
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Census API configuration
        self.census_api_key = "34698fc70a13bd2943ebbd4e720192030e5a824f"
        self.base_url = "https://api.census.gov/data"

        # Comparable NYC neighboring counties
        self.counties = {
            "Westchester County, NY": {
                "state_fips": "36",  # New York
                "county_fips": "119",
                "description": "Base county for comparison",
                "characteristics": "Suburban NYC, affluent, diverse economy"
            },
            "Rockland County, NY": {
                "state_fips": "36",  # New York
                "county_fips": "087",
                "description": "South of Westchester, shares Hudson River border",
                "characteristics": "Similar suburban profile, slightly less affluent"
            },
            "Putnam County, NY": {
                "state_fips": "36",  # New York
                "county_fips": "079",
                "description": "North of Westchester, more rural character",
                "characteristics": "More rural/exurban, lower density"
            },
            "Nassau County, NY": {
                "state_fips": "36",  # New York
                "county_fips": "059",
                "description": "Long Island, comparable affluence",
                "characteristics": "Similar affluence, more suburban sprawl"
            }
        }

        # Key demographic variables for county comparison
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
            'B25003_002E': 'owner_occupied_housing',
            'B25003_003E': 'renter_occupied_housing',

            # Income
            'B19013_001E': 'median_household_income',
            'B19301_001E': 'per_capita_income',
            'B17001_002E': 'poverty_count',
            'B19001_014E': 'households_100k_to_150k',
            'B19001_015E': 'households_150k_to_200k',
            'B19001_016E': 'households_200k_plus',

            # Education
            'B15003_022E': 'bachelors_degree',
            'B15003_023E': 'masters_degree',
            'B15003_024E': 'doctorate_degree',
            'B15003_025E': 'professional_degree',

            # Employment
            'B23025_003E': 'civilian_labor_force',
            'B23025_005E': 'unemployed',
            'B23025_004E': 'employed',

            # Commuting
            'B08301_010E': 'commute_by_transit',
            'B08303_001E': 'mean_travel_time_to_work'
        }

    def fetch_county_data(self, county_name: str, year: int = 2022) -> Dict[str, Any]:
        """
        Fetch demographic data for a specific county.
        """
        if county_name not in self.counties:
            logger.warning(f"Unknown county: {county_name}")
            return None

        county_info = self.counties[county_name]
        state_fips = county_info["state_fips"]
        county_fips = county_info["county_fips"]

        logger.info(f"   [FETCH] {county_name} (state: {state_fips}, county: {county_fips})")

        # Build API URL
        variables = list(self.demographic_variables.keys())
        variables_str = ','.join(variables)

        url = f"{self.base_url}/{year}/acs/acs5"
        params = {
            'get': f'NAME,{variables_str}',
            'for': f'county:{county_fips}',
            'in': f'state:{state_fips}',
            'key': self.census_api_key
        }

        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            if len(data) < 2:
                logger.warning(f"   [WARNING] No data for {county_name}")
                return None

            # First row is headers, second row is data
            headers = data[0]
            values = data[1]

            # Create result dictionary
            result = {
                'county_name': county_name,
                'state_fips': state_fips,
                'county_fips': county_fips,
                'year': year,
                'dataset': 'acs/acs5',
                'description': county_info["description"],
                'characteristics': county_info["characteristics"],
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

            # Calculate derived metrics
            result['poverty_rate'] = self._calculate_percentage(
                result.get('poverty_count', 0),
                result.get('total_population', 0)
            )
            result['unemployment_rate'] = self._calculate_percentage(
                result.get('unemployed', 0),
                result.get('civilian_labor_force', 0)
            )
            result['homeownership_rate'] = self._calculate_percentage(
                result.get('owner_occupied_housing', 0),
                result.get('occupied_housing_units', 0)
            )

            logger.info(f"   [SUCCESS] {county_name}: {result.get('total_population', 0):,} population")
            return result

        except Exception as e:
            logger.error(f"   [ERROR] Failed to fetch {county_name}: {e}")
            return None

    def download_all_counties(self, year: int = 2022) -> Dict[str, Any]:
        """
        Download demographic data for all comparison counties.
        """
        logger.info("\n" + "="*80)
        logger.info("REGIONAL COMPARISON COUNTIES DATA DOWNLOAD")
        logger.info("="*80)
        logger.info(f"Year: {year}")
        logger.info(f"Counties: {len(self.counties)}")

        all_county_data = []
        successful_downloads = 0

        for i, county_name in enumerate(self.counties.keys(), 1):
            logger.info(f"[{i}/{len(self.counties)}] Processing {county_name}...")

            county_data = self.fetch_county_data(county_name, year)

            if county_data:
                all_county_data.append(county_data)
                successful_downloads += 1

            # Rate limiting
            time.sleep(0.5)

        # Create comparison dataset
        comparison_data = {
            'metadata': {
                'generated': time.strftime("%Y-%m-%d %H:%M:%S"),
                'title': 'NYC Neighboring Counties Comparison',
                'year': year,
                'dataset': 'acs/acs5',
                'total_counties': len(self.counties),
                'successful_downloads': successful_downloads,
                'source': 'U.S. Census Bureau American Community Survey',
                'purpose': 'Regional comparison for Westchester County planning analysis'
            },
            'counties': all_county_data,
            'comparison_metrics': self._create_comparison_metrics(all_county_data)
        }

        # Save consolidated data
        output_file = self.data_dir / f"regional_comparison_{year}.json"
        with open(output_file, 'w') as f:
            json.dump(comparison_data, f, indent=2)

        logger.info(f"\n[SUCCESS] Regional comparison data saved: {output_file}")

        # Save individual county files
        for county_data in all_county_data:
            county_name_clean = county_data['county_name'].lower().replace(' ', '_').replace(',', '').replace('.', '')
            individual_file = self.data_dir / f"{county_name_clean}_demographics_{year}.json"
            with open(individual_file, 'w') as f:
                json.dump(county_data, f, indent=2)

        return comparison_data

    def _create_comparison_metrics(self, county_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create comparison metrics across all counties.
        """
        if not county_data:
            return {}

        # Find Westchester as baseline
        westchester = next((c for c in county_data if 'Westchester' in c['county_name']), None)

        if not westchester:
            return {}

        comparison = {
            'baseline_county': westchester['county_name'],
            'comparisons': []
        }

        for county in county_data:
            if county['county_name'] == westchester['county_name']:
                continue

            comp = {
                'county_name': county['county_name'],
                'population_vs_westchester': self._calculate_percentage_change(
                    westchester.get('total_population', 0),
                    county.get('total_population', 0)
                ),
                'income_vs_westchester': self._calculate_percentage_change(
                    westchester.get('median_household_income', 0),
                    county.get('median_household_income', 0)
                ),
                'home_value_vs_westchester': self._calculate_percentage_change(
                    westchester.get('median_home_value', 0),
                    county.get('median_home_value', 0)
                ),
                'density_comparison': self._compare_density(westchester, county)
            }
            comparison['comparisons'].append(comp)

        return comparison

    def _calculate_percentage(self, numerator: int, denominator: int) -> float:
        """Calculate percentage with error handling."""
        if not numerator or not denominator or denominator == 0:
            return 0.0
        return round((numerator / denominator) * 100, 2)

    def _calculate_percentage_change(self, baseline: int, comparison: int) -> float:
        """Calculate percentage change from baseline."""
        if not baseline or baseline == 0:
            return 0.0
        return round(((comparison - baseline) / baseline) * 100, 1)

    def _compare_density(self, county1: Dict, county2: Dict) -> str:
        """Compare population density (simplified)."""
        pop1 = county1.get('total_population', 0)
        pop2 = county2.get('total_population', 0)

        if pop1 > pop2:
            return f"{county2['county_name']} is less dense"
        elif pop2 > pop1:
            return f"{county2['county_name']} is more dense"
        else:
            return "Similar density"


def main():
    """Download regional comparison data for NYC neighboring counties"""
    importer = RegionalComparisonImporter()

    logger.info("[START] Starting regional comparison data download...")
    logger.info("   Counties: Westchester, Rockland, Putnam, Nassau")
    logger.info("   Purpose: Regional benchmarking and comparative analysis")

    # Download all county data
    comparison_data = importer.download_all_counties(2022)

    logger.info("\n" + "="*80)
    logger.info("REGIONAL COMPARISON DATA DOWNLOAD COMPLETE!")
    logger.info("="*80)

    logger.info(f"[SUCCESS] Downloaded data for {len(comparison_data.get('counties', []))} counties")

    for county in comparison_data.get('counties', []):
        logger.info(f"   - {county['county_name']}: {county.get('total_population', 0):,} population")

    logger.info(f"\n[FILES] All data saved to: {importer.data_dir}")
    logger.info("[READY] Regional comparison data ready for use!")


if __name__ == "__main__":
    main()
