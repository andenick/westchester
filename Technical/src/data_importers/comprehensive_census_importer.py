"""
Comprehensive U.S. Census Bureau API Client for Westchester County
Collects ALL available ACS variables for advanced municipal analysis

This expanded client collects comprehensive demographic, economic, housing,
social, and transportation data from the American Community Survey.
"""

import requests
import json
import csv
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class ComprehensiveCensusClient:
    """Comprehensive Census API client for advanced municipal analysis"""

    BASE_URL = "https://api.census.gov/data"

    # Geographic identifiers
    STATE_FIPS = "36"  # New York
    COUNTY_FIPS = "119"  # Westchester County

    # COMPREHENSIVE ACS VARIABLES - All available for municipal planning
    COMPREHENSIVE_VARIABLES = {
        # POPULATION CHARACTERISTICS
        # Age Distribution
        'B01001_001E': 'total_population',
        'B01001_002E': 'male_under_5', 'B01001_003E': 'male_5_to_9', 'B01001_004E': 'male_10_to_14',
        'B01001_005E': 'male_15_to_17', 'B01001_006E': 'male_18_to_19', 'B01001_007E': 'male_20',
        'B01001_008E': 'male_21', 'B01001_009E': 'male_22_to_24', 'B01001_010E': 'male_25_to_29',
        'B01001_011E': 'male_30_to_34', 'B01001_012E': 'male_35_to_39', 'B01001_013E': 'male_40_to_44',
        'B01001_014E': 'male_45_to_49', 'B01001_015E': 'male_50_to_54', 'B01001_016E': 'male_55_to_59',
        'B01001_017E': 'male_60_to_61', 'B01001_018E': 'male_62_to_64', 'B01001_019E': 'male_65_to_66',
        'B01001_020E': 'male_67_to_69', 'B01001_021E': 'male_70_to_74', 'B01001_022E': 'male_75_to_79',
        'B01001_023E': 'male_80_to_84', 'B01001_024E': 'male_85_and_over',
        'B01001_026E': 'female_under_5', 'B01001_027E': 'female_5_to_9', 'B01001_028E': 'female_10_to_14',
        'B01001_029E': 'female_15_to_17', 'B01001_030E': 'female_18_to_19', 'B01001_031E': 'female_20',
        'B01001_032E': 'female_21', 'B01001_033E': 'female_22_to_24', 'B01001_034E': 'female_25_to_29',
        'B01001_035E': 'female_30_to_34', 'B01001_036E': 'female_35_to_39', 'B01001_037E': 'female_40_to_44',
        'B01001_038E': 'female_45_to_49', 'B01001_039E': 'female_50_to_54', 'B01001_040E': 'female_55_to_59',
        'B01001_041E': 'female_60_to_61', 'B01001_042E': 'female_62_to_64', 'B01001_043E': 'female_65_to_66',
        'B01001_044E': 'female_67_to_69', 'B01001_045E': 'female_70_to_74', 'B01001_046E': 'female_75_to_79',
        'B01001_047E': 'female_80_to_84', 'B01001_048E': 'female_85_and_over',

        # Race and Ethnicity
        'B02001_001E': 'total_race_population',
        'B02001_002E': 'white_alone', 'B02001_003E': 'black_or_african_american_alone',
        'B02001_004E': 'american_indian_and_alaska_native_alone', 'B02001_005E': 'asian_alone',
        'B02001_006E': 'native_hawaiian_and_other_pacific_islander_alone', 'B02001_007E': 'some_other_race_alone',
        'B02001_008E': 'two_or_more_races',

        # Hispanic/Latino Origin
        'B03001_001E': 'total_hispanic_origin',
        'B03001_002E': 'not_hispanic_or_latino', 'B03001_003E': 'hispanic_or_latino',

        # HOUSING CHARACTERISTICS
        'B25001_001E': 'total_housing_units',
        'B25002_001E': 'total_occupancy_status', 'B25002_002E': 'occupied_housing_units',
        'B25002_003E': 'vacant_housing_units',

        # Housing Tenure
        'B25003_001E': 'total_tenure', 'B25003_002E': 'owner_occupied', 'B25003_003E': 'renter_occupied',

        # Housing Value
        'B25077_001E': 'median_home_value',
        'B25075_001E': 'aggregate_home_value',

        # Gross Rent
        'B25064_001E': 'median_gross_rent',
        'B25058_001E': 'aggregate_contract_rent',

        # Year Structure Built
        'B25035_001E': 'median_year_structure_built',
        'B25034_001E': 'year_structure_built_2014_or_later', 'B25034_002E': 'year_structure_built_2010_to_2013',
        'B25034_003E': 'year_structure_built_2000_to_2009', 'B25034_004E': 'year_structure_built_1980_to_1999',
        'B25034_005E': 'year_structure_built_1960_to_1979', 'B25034_006E': 'year_structure_built_1940_to_1959',
        'B25034_007E': 'year_structure_built_1939_or_earlier',

        # Rooms in Housing Unit
        'B25018_001E': 'median_number_of_rooms',
        'B25017_001E': 'housing_units_1_room', 'B25017_002E': 'housing_units_2_rooms',
        'B25017_003E': 'housing_units_3_rooms', 'B25017_004E': 'housing_units_4_rooms',
        'B25017_005E': 'housing_units_5_rooms', 'B25017_006E': 'housing_units_6_rooms',
        'B25017_007E': 'housing_units_7_rooms', 'B25017_008E': 'housing_units_8_rooms',
        'B25017_009E': 'housing_units_9_rooms_or_more',

        # ECONOMIC CHARACTERISTICS
        # Income
        'B19013_001E': 'median_household_income',
        'B19025_001E': 'aggregate_household_income',
        'B19113_001E': 'median_family_income',
        'B19301_001E': 'per_capita_income',
        'B19201_001E': 'aggregate_earnings',

        # Poverty Status
        'B17001_001E': 'total_poverty_status', 'B17001_002E': 'below_poverty_level',
        'B17001_003E': 'at_or_above_poverty_level',

        # Employment Status
        'B23025_001E': 'total_employment_status', 'B23025_002E': 'in_labor_force',
        'B23025_003E': 'civilian_labor_force', 'B23025_004E': 'employed',
        'B23025_005E': 'unemployed', 'B23025_006E': 'not_in_labor_force',

        # Industry and Occupation
        'B24010_001E': 'total_employment_industry',
        'B24010_002E': 'agriculture_forestry_fishing_hunting_mining',
        'B24010_003E': 'construction', 'B24010_004E': 'manufacturing',
        'B24010_005E': 'wholesale_trade', 'B24010_006E': 'retail_trade',
        'B24010_007E': 'transportation_warehousing', 'B24010_008E': 'utilities',
        'B24010_009E': 'information', 'B24010_010E': 'finance_insurance',
        'B24010_011E': 'real_estate_rental_leasing', 'B24010_012E': 'professional_scientific_technical',
        'B24010_013E': 'management', 'B24010_014E': 'administrative_support',
        'B24010_015E': 'educational_services', 'B24010_016E': 'healthcare_social_assistance',
        'B24010_017E': 'arts_entertainment_recreation', 'B24010_018E': 'accommodation_food_services',
        'B24010_019E': 'other_services', 'B24010_020E': 'public_administration',

        # Class of Worker
        'B24080_001E': 'total_class_worker', 'B24080_002E': 'private_wage_salary',
        'B24080_003E': 'private_not_for_profit', 'B24080_004E': 'local_government',
        'B24080_005E': 'state_government', 'B24080_006E': 'federal_government',
        'B24080_007E': 'selfemployed_not_incorporated', 'B24080_008E': 'selfemployed_incorporated',
        'B24080_009E': 'unpaid_family_worker',

        # Commuting and Transportation
        'B08006_001E': 'total_workers_16_over',
        'B08006_002E': 'car_truck_or_van', 'B08006_003E': 'drove_alone',
        'B08006_004E': 'carpooled', 'B08006_005E': 'public_transportation',
        'B08006_006E': 'bus', 'B08006_007E': 'subway_or_elevated',
        'B08006_008E': 'long_distance_train', 'B08006_009E': 'taxicab',
        'B08006_010E': 'motorcycle', 'B08006_011E': 'bicycle',
        'B08006_012E': 'walked', 'B08006_013E': 'other_means',
        'B08006_014E': 'worked_at_home',

        # Travel Time to Work
        'B08013_001E': 'aggregate_travel_time', 'B08013_002E': 'less_than_10_minutes',
        'B08013_003E': '10_to_19_minutes', 'B08013_004E': '20_to_29_minutes',
        'B08013_005E': '30_to_39_minutes', 'B08013_006E': '40_to_59_minutes',
        'B08013_007E': '60_to_89_minutes', 'B08013_008E': '90_or_more_minutes',

        # Time Leaving Home
        'B08012_001E': 'total_time_leaving_home', 'B08012_002E': '12_00_am_to_4_59_am',
        'B08012_003E': '5_00_am_to_5_29_am', 'B08012_004E': '5_30_am_to_5_59_am',
        'B08012_005E': '6_00_am_to_6_29_am', 'B08012_006E': '6_30_am_to_6_59_am',
        'B08012_007E': '7_00_am_to_7_29_am', 'B08012_008E': '7_30_am_to_7_59_am',
        'B08012_009E': '8_00_am_to_8_29_am', 'B08012_010E': '8_30_am_to_8_59_am',
        'B08012_011E': '9_00_am_to_9_59_am', 'B08012_012E': '10_00_am_to_10_59_am',
        'B08012_013E': '11_00_am_to_12_59_pm', 'B08012_014E': '1_00_pm_to_3_59_pm',
        'B08012_015E': '4_00_pm_to_4_59_pm', 'B08012_016E': '5_00_pm_to_5_29_pm',
        'B08012_017E': '5_30_pm_to_5_59_pm', 'B08012_018E': '6_00_pm_to_6_59_pm',
        'B08012_019E': '7_00_pm_to_11_59_pm',

        # EDUCATIONAL CHARACTERISTICS
        # Educational Attainment
        'B15003_001E': 'total_education_25_over',
        'B15003_002E': 'no_schooling_completed', 'B15003_003E': 'nursery_school',
        'B15003_004E': 'kindergarten', 'B15003_005E': '1st_grade', 'B15003_006E': '2nd_grade',
        'B15003_007E': '3rd_grade', 'B15003_008E': '4th_grade', 'B15003_009E': '5th_grade',
        'B15003_010E': '6th_grade', 'B15003_011E': '7th_grade', 'B15003_012E': '8th_grade',
        'B15003_013E': '9th_grade', 'B15003_014E': '10th_grade', 'B15003_015E': '11th_grade',
        'B15003_016E': '12th_grade_no_diploma', 'B15003_017E': 'regular_high_school_diploma',
        'B15003_018E': 'ged_or_alternative_credential', 'B15003_019E': 'some_college_less_than_1_year',
        'B15003_020E': 'some_college_1_or_more_years_no_degree', 'B15003_021E': 'associates_degree',
        'B15003_022E': 'bachelors_degree', 'B15003_023E': 'masters_degree',
        'B15003_024E': 'professional_school_degree', 'B15003_025E': 'doctorate_degree',

        # School Enrollment
        'B14001_001E': 'total_school_enrollment',
        'B14001_002E': 'public_school', 'B14001_003E': 'private_school',

        # SOCIAL CHARACTERISTICS
        # Household Relationships
        'B11001_001E': 'total_households', 'B11001_002E': 'family_households',
        'B11001_003E': 'married_couple_family', 'B11001_004E': 'other_family',
        'B11001_005E': 'male_householder_no_wife_present', 'B11001_006E': 'female_householder_no_husband_present',
        'B11001_007E': 'nonfamily_households',

        # Marital Status
        'B12001_001E': 'total_marital_status_15_over',
        'B12001_002E': 'never_married', 'B12001_003E': 'now_married',
        'B12001_004E': 'widowed', 'B12001_005E': 'divorced', 'B12001_006E': 'separated',

        # Grandparents as Caregivers
        'B10010_001E': 'total_grandparent_living_with_own_grandchildren',
        'B10010_002E': 'grandparent_responsible_for_grandchildren',

        # Veterans Status
        'B21001_001E': 'total_civilian_veterans', 'B21001_002E': 'civilian_veterans',

        # Language Spoken at Home
        'B16001_001E': 'total_language_5_over', 'B16001_002E': 'speak_only_english',
        'B16001_003E': 'spanish', 'B16001_004E': 'french', 'B16001_005E': 'german',
        'B16001_006E': 'russian', 'B16001_007E': 'chinese', 'B16001_008E': 'korean',
        'B16001_009E': 'vietnamese', 'B16001_010E': 'tagalog', 'B16001_011E': 'arabic',

        # Place of Birth
        'B05002_001E': 'total_place_of_birth', 'B05002_002E': 'native',
        'B05002_013E': 'foreign_born', 'B05002_014E': 'entered_us_before_2010',
        'B05002_015E': 'entered_us_2010_to_2014', 'B05002_016E': 'entered_us_2015_or_later',

        # Geographic Mobility
        'B07003_001E': 'total_geographic_mobility', 'B07003_002E': 'same_house_1_year_ago',
        'B07003_003E': 'moved_within_same_county', 'B07003_004E': 'moved_from_different_county',
        'B07003_005E': 'moved_from_different_state', 'B07003_006E': 'moved_from_abroad',
    }

    def __init__(self, api_key: Optional[str] = None, output_dir: Optional[str] = None):
        """
        Initialize comprehensive Census API client

        Args:
            api_key: Census API key
            output_dir: Directory to save downloaded data
        """
        self.api_key = api_key

        if output_dir is None:
            base_path = Path(__file__).parent.parent.parent / "data" / "raw" / "demographics" / "comprehensive"
        else:
            base_path = Path(output_dir)

        self.output_dir = base_path
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Rate limiting
        self.request_delay = 0.1  # 100ms between requests
        self.last_request_time = 0

    def _rate_limit(self):
        """Implement rate limiting to respect API limits"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.request_delay:
            sleep_time = self.request_delay - time_since_last
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def _build_url(self, dataset: str, year: int, variables: List[str], geography: str) -> str:
        """Build Census API URL with rate limiting"""
        self._rate_limit()

        base = f"{self.BASE_URL}/{year}/{dataset}"
        var_string = ",".join(variables + ['NAME'])  # Always include NAME

        url = f"{base}?get={var_string}&for={geography}"

        if self.api_key:
            url += f"&key={self.api_key}"

        return url

    def fetch_comprehensive_data(self, geography_type: str = "county", year: int = 2022, dataset: str = "acs/acs5") -> Optional[Dict or List[Dict]]:
        """
        Fetch comprehensive Census data for specified geography

        Args:
            geography_type: 'county', 'tract', or 'place'
            year: Year of data
            dataset: Census dataset

        Returns:
            Dictionary for county, list of dictionaries for tracts/places
        """
        variables = list(self.COMPREHENSIVE_VARIABLES.keys())

        if geography_type == "county":
            geography = f"county:{self.COUNTY_FIPS}&in=state:{self.STATE_FIPS}"
        elif geography_type == "tract":
            geography = f"tract:*&in=state:{self.STATE_FIPS}&in=county:{self.COUNTY_FIPS}"
        elif geography_type == "place":
            geography = f"place:*&in=state:{self.STATE_FIPS}"
        else:
            raise ValueError(f"Unsupported geography type: {geography_type}")

        url = self._build_url(dataset, year, variables, geography)

        print(f"Fetching comprehensive {geography_type} data...")
        print(f"Variables: {len(variables)} comprehensive indicators")
        print(f"Dataset: {dataset}, Year: {year}")

        try:
            response = requests.get(url, timeout=120)  # Longer timeout for comprehensive data
            response.raise_for_status()

            data = response.json()

            if len(data) < 2:
                print(f"[FAILED] No {geography_type} data returned from API")
                return None

            headers = data[0]

            if geography_type == "county":
                return self._process_county_data(data[1], headers, year, dataset)
            else:
                return self._process_multiple_geographies(data[1:], headers, year, dataset, geography_type)

        except requests.RequestException as e:
            print(f"[FAILED] Error fetching {geography_type} data: {e}")
            if not self.api_key:
                print("[WARNING] No API key provided. Rate limits may apply.")
            return None

    def _process_county_data(self, row: List[str], headers: List[str], year: int, dataset: str) -> Dict:
        """Process county-level data"""
        result = {}

        for i, header in enumerate(headers):
            if header in self.COMPREHENSIVE_VARIABLES:
                friendly_name = self.COMPREHENSIVE_VARIABLES[header]
                try:
                    value = int(row[i]) if row[i] and row[i] != '-666666666' else None
                    result[friendly_name] = value
                except (ValueError, IndexError):
                    result[friendly_name] = None
            elif header == 'NAME':
                result['location_name'] = row[i]
            elif header in ['state', 'county']:
                result[header] = row[i]

        result['year'] = year
        result['dataset'] = dataset
        result['fetched_date'] = datetime.now().isoformat()
        result['data_type'] = 'comprehensive'

        return result

    def _process_multiple_geographies(self, rows: List[List[str]], headers: List[str], year: int, dataset: str, geography_type: str) -> List[Dict]:
        """Process multiple geographic areas (tracts or places)"""
        results = []

        for row in rows:
            geo_data = {}

            for i, header in enumerate(headers):
                if header in self.COMPREHENSIVE_VARIABLES:
                    friendly_name = self.COMPREHENSIVE_VARIABLES[header]
                    try:
                        value = int(row[i]) if row[i] and row[i] != '-666666666' else None
                        geo_data[friendly_name] = value
                    except (ValueError, IndexError):
                        geo_data[friendly_name] = None
                elif header == 'NAME':
                    geo_data['location_name'] = row[i]
                elif header in ['state', 'county', 'tract', 'place']:
                    geo_data[header] = row[i]

            geo_data['year'] = year
            geo_data['dataset'] = dataset
            geo_data['fetched_date'] = datetime.now().isoformat()
            geo_data['data_type'] = 'comprehensive'

            # Filter places for Westchester County only (rough filtering by name)
            if geography_type == "place":
                name = geo_data.get('location_name', '').lower()
                if 'westchester' in name or any(city in name for city in ['yonkers', 'white plains', 'new rochelle', 'mount vernon', 'rye', 'scarsdale']):
                    results.append(geo_data)
            else:
                results.append(geo_data)

        return results

    def save_data(self, data: Dict or List[Dict], filename: str, format: str = 'json'):
        """Save comprehensive Census data to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if format == 'json':
            filepath = self.output_dir / f"{timestamp}_{filename}.json"
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"[SUCCESS] Saved comprehensive data to {filepath}")

        elif format == 'csv':
            filepath = self.output_dir / f"{timestamp}_{filename}.csv"

            if isinstance(data, dict):
                data = [data]

            if not data:
                print("[WARNING] No data to save")
                return

            with open(filepath, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            print(f"[SUCCESS] Saved comprehensive data to {filepath}")

    def run_comprehensive_import(self, year: int = 2022) -> Tuple[bool, str]:
        """
        Run comprehensive Census data import for all geographic levels

        Args:
            year: Year of ACS data to fetch

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            if not self.api_key:
                print("[WARNING] No Census API key provided. This comprehensive import requires an API key.")
                print("Get a free key at: https://api.census.gov/data/key_signup.html")
                print()

            results = []
            total_variables = len(self.COMPREHENSIVE_VARIABLES)

            print(f"Starting comprehensive Census data import...")
            print(f"Total variables to collect: {total_variables}")
            print("=" * 60)

            # 1. County-level comprehensive data
            print("\n[1/3] Fetching comprehensive county-level data...")
            county_data = self.fetch_comprehensive_data("county", year)
            if county_data:
                self.save_data(county_data, f"westchester_county_comprehensive_{year}", 'json')
                self.save_data(county_data, f"westchester_county_comprehensive_{year}", 'csv')
                results.append("comprehensive county-level data")

            # 2. Census tract comprehensive data
            print("\n[2/3] Fetching comprehensive census tract data...")
            tract_data = self.fetch_comprehensive_data("tract", year)
            if tract_data:
                self.save_data(tract_data, f"westchester_tracts_comprehensive_{year}", 'json')
                self.save_data(tract_data, f"westchester_tracts_comprehensive_{year}", 'csv')
                results.append(f"comprehensive data for {len(tract_data)} census tracts")

            # 3. Municipality comprehensive data
            print("\n[3/3] Fetching comprehensive municipality data...")
            place_data = self.fetch_comprehensive_data("place", year)
            if place_data:
                self.save_data(place_data, f"westchester_municipalities_comprehensive_{year}", 'json')
                self.save_data(place_data, f"westchester_municipalities_comprehensive_{year}", 'csv')
                results.append(f"comprehensive data for {len(place_data)} municipalities")

            if not results:
                return False, "No comprehensive data was successfully imported"

            return True, f"Successfully imported comprehensive data: {', '.join(results)}"

        except Exception as e:
            return False, f"Comprehensive import failed: {str(e)}"

    def generate_data_summary(self, data_file: str) -> Dict:
        """Generate summary statistics for comprehensive data"""
        try:
            filepath = self.output_dir / data_file
            with open(filepath, 'r') as f:
                data = json.load(f)

            if isinstance(data, dict):
                data = [data]

            summary = {
                'total_records': len(data),
                'variables_collected': len(self.COMPREHENSIVE_VARIABLES),
                'data_source': 'U.S. Census Bureau ACS 5-Year Estimates',
                'geographic_levels': list(set(d.get('tract', d.get('place', 'county')) for d in data)),
                'year_collected': data[0].get('year', 'unknown') if data else 'unknown',
                'key_demographics': {
                    'total_population': sum(d.get('total_population', 0) for d in data),
                    'median_household_income': next((d.get('median_household_income') for d in data if d.get('median_household_income')), None),
                    'median_home_value': next((d.get('median_home_value') for d in data if d.get('median_home_value')), None),
                }
            }

            return summary

        except Exception as e:
            return {'error': f'Failed to generate summary: {str(e)}'}


def main():
    """Command-line interface for comprehensive Census importer"""
    import os

    print("=" * 80)
    print("COMPREHENSIVE U.S. Census API Importer - Westchester County")
    print("Collects ALL available ACS variables for advanced municipal analysis")
    print("=" * 80)
    print()

    # Check for API key
    api_key = os.getenv('CENSUS_API_KEY')

    if not api_key:
        print("No CENSUS_API_KEY environment variable found.")
        print("This comprehensive importer requires an API key to avoid rate limits.")
        print("Get a free key at: https://api.census.gov/data/key_signup.html")
        print()
        response = input("Enter your Census API key (or press Enter to cancel): ").strip()
        if not response:
            print("Census API key required for comprehensive import. Exiting.")
            return
        api_key = response

    # Get year from user
    year_input = input("Enter year to fetch (2013-2022, default 2022): ").strip()
    try:
        year = int(year_input) if year_input else 2022
        if not (2013 <= year <= 2022):
            print("Year must be between 2013 and 2022. Using 2022.")
            year = 2022
    except ValueError:
        print("Invalid year input. Using 2022.")
        year = 2022

    client = ComprehensiveCensusClient(api_key=api_key)
    success, message = client.run_comprehensive_import(year)

    print()
    print("=" * 80)
    if success:
        print(f"[SUCCESS]: {message}")
        print(f"Data saved to: {client.output_dir}")
        print(f"Variables collected: {len(client.COMPREHENSIVE_VARIABLES)} comprehensive indicators")
    else:
        print(f"[FAILED]: {message}")
    print("=" * 80)


if __name__ == "__main__":
    main()