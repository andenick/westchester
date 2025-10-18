#!/usr/bin/env python3
"""
HUD (Housing and Urban Development) Data Collector
Collects housing and urban development data relevant to Westchester County
Provides comprehensive housing data for municipal planning and analysis
"""

import os
import sys
import json
import time
import requests
import logging
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlencode

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class HUDDataCollector:
    """Collects housing and urban development data from HUD APIs"""

    def __init__(self, output_dir: str = None):
        self.output_dir = Path(output_dir or "data/raw/housing/hud")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # HUD API configuration
        self.api_key = os.getenv('HUD_API_KEY')
        self.base_url = "https://www.huduser.gov/hudapi/public"

        # Westchester County FIPS codes and geographic identifiers
        self.westchester_geo = {
            "county_fips": "36119",  # Westchester County, NY
            "state_fips": "36",       # New York State
            "place_fips": {
                "Yonkers": "3680000",
                "New Rochelle": "3654000",
                "Mount Vernon": "3648000",
                "White Plains": "3682000",
                "Peekskill": "3657000"
            },
            "metro_area": "35620",  # New York-Newark-Jersey City, NY-NJ-PA MSA
            "zip_codes": [
                # Major Westchester ZIP codes
                "10501", "10502", "10503", "10504", "10506", "10510", "10512",
                "10514", "10516", "10517", "10518", "10520", "10521", "10522",
                "10523", "10526", "10527", "10528", "10530", "10532", "10533",
                "10535", "10536", "10537", "10538", "10540", "10541", "10543",
                "10545", "10546", "10547", "10548", "10549", "10552", "10553",
                "10560", "10562", "10566", "10567", "10570", "10573", "10575",
                "10576", "10577", "10578", "10579", "10580", "10583", "10587",
                "10588", "10589", "10590", "10591", "10592", "10594", "10595",
                "10596", "10598", "10601", "10603", "10604", "10605", "10606",
                "10607", "10610"
            ]
        }

        # HUD data endpoints and datasets
        self.hud_datasets = {
            # Fair Market Rents
            "fair_market_rents": {
                "endpoint": "/fmr",
                "description": "Fair Market Rents for housing units",
                "frequency": "Annual",
                "geography": ["county", "metro"]
            },

            # Income Limits
            "income_limits": {
                "endpoint": "/il",
                "description": "HUD Income Limits for different household sizes",
                "frequency": "Annual",
                "geography": ["county", "metro", "state"]
            },

            # Section 8 Data
            "section8": {
                "endpoint": "/hudsection8",
                "description": "Section 8 housing choice voucher program data",
                "frequency": "Annual",
                "geography": ["county", "state"]
            },

            # Public Housing
            "public_housing": {
                "endpoint": "/hudpublichousing",
                "description": "Public housing authority and program data",
                "frequency": "Annual",
                "geography": ["county", "state"]
            },

            # Multifamily Properties
            "multifamily": {
                "endpoint": "/hudmultifamily",
                "description": "Multifamily housing properties data",
                "frequency": "Quarterly",
                "geography": ["county", "state"]
            },

            # Comprehensive Housing Affordability Strategy (CHAS)
            "chas": {
                "endpoint": "/chas",
                "description": "Comprehensive Housing Affordability Strategy data",
                "frequency": "Annual (based on ACS)",
                "geography": ["county", "census_tract", "place"]
            },

            # Housing Market Data
            "housing_market": {
                "endpoint": "/hudmarket",
                "description": "Housing market conditions and trends",
                "frequency": "Monthly",
                "geography": ["metro", "state"]
            },

            # Emergency Solutions Grants
            "emergency_solutions": {
                "endpoint": "/hudemergencysolutions",
                "description": "Emergency Solutions Grants program data",
                "frequency": "Annual",
                "geography": ["county", "state"]
            },

            # Homeless Management Information System
            "homeless": {
                "endpoint": "/hudhomeless",
                "description": "Homeless populations and services data",
                "frequency": "Annual",
                "geography": ["county", "state"]
            },

            # Community Development Block Grants
            "cdbb": {
                "endpoint": "/hudcdbg",
                "description": "Community Development Block Grant program data",
                "frequency": "Annual",
                "geography": ["county", "state"]
            },

            # Housing Counseling
            "housing_counseling": {
                "endpoint": "/hudhousingcounseling",
                "description": "HUD-approved housing counseling agencies",
                "frequency": "Monthly",
                "geography": ["national", "state", "county"]
            },

            # Lead Hazard Control
            "lead_hazard": {
                "endpoint": "/hudlead",
                "description": "Lead hazard control grant data",
                "frequency": "Annual",
                "geography": ["county", "state"]
            }
        }

        # Rate limiting (HUD API allows ~1000 requests/hour)
        self.request_delay = 0.5  # 0.5 seconds between requests
        self.last_request_time = 0

        # Session for persistent connections
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Westchester Data Platform/1.0 (Housing Data Collection)',
            'Content-Type': 'application/json'
        })

    def _rate_limit(self):
        """Implement rate limiting for requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.request_delay:
            sleep_time = self.request_delay - time_since_last
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def check_api_key(self) -> bool:
        """Check if HUD API key is available"""
        if not self.api_key:
            logger.error("HUD_API_KEY environment variable not found")
            logger.info("Get a free API key at: https://www.huduser.gov/portal/datasets/pdrdatas.html")
            return False
        return True

    def make_hud_request(self, endpoint: str, params: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Make a request to HUD API with proper error handling"""
        if not self.check_api_key():
            return None

        if params is None:
            params = {}

        # Add API key to parameters
        params['key'] = self.api_key

        try:
            url = f"{self.base_url}{endpoint}"
            self._rate_limit()

            response = self.session.post(url, json=params)
            response.raise_for_status()

            data = response.json()

            # Check for API errors
            if 'error_code' in data or 'error' in data:
                error_msg = data.get('error_message', data.get('error', 'Unknown error'))
                logger.error(f"HUD API error: {error_msg}")
                return None

            return data

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {endpoint}: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error for {endpoint}: {e}")
            return None

    def collect_fair_market_rents(self, years: int = 5) -> Optional[pd.DataFrame]:
        """Collect Fair Market Rent data for Westchester County"""
        logger.info("Collecting Fair Market Rent data...")

        all_data = []
        current_year = datetime.now().year

        for year in range(current_year - years, current_year + 1):
            try:
                params = {
                    "year": year,
                    "geography": "county",
                    "state_code": self.westchester_geo["state_fips"],
                    "county_code": self.westchester_geo["county_fips"]
                }

                data = self.make_hud_request("/fmr", params)

                if data and 'data' in data:
                    for record in data['data']:
                        record['year'] = year
                        record['data_type'] = 'fair_market_rent'
                        all_data.append(record)

                    logger.info(f"✅ FMR data for {year}: {len(data['data'])} records")

            except Exception as e:
                logger.error(f"Error collecting FMR data for {year}: {e}")

        if all_data:
            return pd.DataFrame(all_data)
        return None

    def collect_income_limits(self, years: int = 5) -> Optional[pd.DataFrame]:
        """Collect HUD Income Limits data"""
        logger.info("Collecting Income Limits data...")

        all_data = []
        current_year = datetime.now().year

        for year in range(current_year - years, current_year + 1):
            try:
                params = {
                    "year": year,
                    "geography": "county",
                    "state_code": self.westchester_geo["state_fips"],
                    "county_code": self.westchester_geo["county_fips"]
                }

                data = self.make_hud_request("/il", params)

                if data and 'data' in data:
                    for record in data['data']:
                        record['year'] = year
                        record['data_type'] = 'income_limits'
                        all_data.append(record)

                    logger.info(f"✅ Income Limits data for {year}: {len(data['data'])} records")

            except Exception as e:
                logger.error(f"Error collecting Income Limits data for {year}: {e}")

        if all_data:
            return pd.DataFrame(all_data)
        return None

    def collect_section8_data(self, years: int = 5) -> Optional[pd.DataFrame]:
        """Collect Section 8 housing voucher data"""
        logger.info("Collecting Section 8 data...")

        all_data = []
        current_year = datetime.now().year

        for year in range(current_year - years, current_year + 1):
            try:
                params = {
                    "year": year,
                    "geography": "county",
                    "state_code": self.westchester_geo["state_fips"],
                    "county_code": self.westchester_geo["county_fips"]
                }

                data = self.make_hud_request("/hudsection8", params)

                if data and 'data' in data:
                    for record in data['data']:
                        record['year'] = year
                        record['data_type'] = 'section8'
                        all_data.append(record)

                    logger.info(f"✅ Section 8 data for {year}: {len(data['data'])} records")

            except Exception as e:
                logger.error(f"Error collecting Section 8 data for {year}: {e}")

        if all_data:
            return pd.DataFrame(all_data)
        return None

    def collect_chas_data(self) -> Optional[pd.DataFrame]:
        """Collect Comprehensive Housing Affordability Strategy data"""
        logger.info("Collecting CHAS data...")

        try:
            params = {
                "geography": "county",
                "state_code": self.westchester_geo["state_fips"],
                "county_code": self.westchester_geo["county_fips"]
            }

            data = self.make_hud_request("/chas", params)

            if data and 'data' in data:
                df = pd.DataFrame(data['data'])
                df['data_type'] = 'chas'
                df['collection_date'] = datetime.now().isoformat()

                logger.info(f"✅ CHAS data: {len(df)} records")
                return df

        except Exception as e:
            logger.error(f"Error collecting CHAS data: {e}")

        return None

    def collect_multifamily_data(self, years: int = 3) -> Optional[pd.DataFrame]:
        """Collect multifamily housing properties data"""
        logger.info("Collecting Multifamily Properties data...")

        all_data = []
        current_year = datetime.now().year

        for year in range(current_year - years, current_year + 1):
            try:
                params = {
                    "year": year,
                    "geography": "county",
                    "state_code": self.westchester_geo["state_fips"],
                    "county_code": self.westchester_geo["county_fips"]
                }

                data = self.make_hud_request("/hudmultifamily", params)

                if data and 'data' in data:
                    for record in data['data']:
                        record['year'] = year
                        record['data_type'] = 'multifamily'
                        all_data.append(record)

                    logger.info(f"✅ Multifamily data for {year}: {len(data['data'])} records")

            except Exception as e:
                logger.error(f"Error collecting Multifamily data for {year}: {e}")

        if all_data:
            return pd.DataFrame(all_data)
        return None

    def collect_housing_counseling_agencies(self) -> Optional[pd.DataFrame]:
        """Collect HUD-approved housing counseling agencies"""
        logger.info("Collecting Housing Counseling Agencies data...")

        try:
            # Collect agencies in New York State
            params = {
                "state_code": self.westchester_geo["state_fips"],
                "geography": "state"
            }

            data = self.make_hud_request("/hudhousingcounseling", params)

            if data and 'data' in data:
                df = pd.DataFrame(data['data'])

                # Filter for agencies near Westchester County
                # (This is a simple filter - you might want to add geographic proximity logic)
                westchester_agencies = df[
                    df['city'].str.contains('Yonkers|New Rochelle|Mount Vernon|White Plains|Peekskill', case=False, na=False) |
                    df['county'].str.contains('Westchester', case=False, na=False)
                ]

                westchester_agencies['data_type'] = 'housing_counseling'
                westchester_agencies['collection_date'] = datetime.now().isoformat()

                logger.info(f"✅ Housing Counseling Agencies: {len(westchester_agencies)} agencies in/near Westchester")
                return westchester_agencies

        except Exception as e:
            logger.error(f"Error collecting Housing Counseling data: {e}")

        return None

    def collect_all_hud_data(self, years_back: int = 5) -> Dict[str, Any]:
        """Collect all relevant HUD data for Westchester County"""

        if not self.check_api_key():
            return {
                'success': False,
                'error': 'HUD API key not available',
                'data': {}
            }

        logger.info("Starting comprehensive HUD housing data collection...")
        logger.info(f"Output directory: {self.output_dir}")

        results = {
            'collection_time': datetime.now().isoformat(),
            'years_collected': years_back,
            'datasets': {},
            'summary': {
                'total_datasets': len(self.hud_datasets),
                'successful_downloads': 0,
                'failed_downloads': 0,
                'total_records': 0
            },
            'saved_files': {},
            'geography': self.westchester_geo
        }

        # Collect data from each dataset
        data_collectors = {
            'fair_market_rents': lambda: self.collect_fair_market_rents(years_back),
            'income_limits': lambda: self.collect_income_limits(years_back),
            'section8': lambda: self.collect_section8_data(years_back),
            'chas': lambda: self.collect_chas_data(),
            'multifamily': lambda: self.collect_multifamily_data(years_back),
            'housing_counseling': lambda: self.collect_housing_counseling_agencies()
        }

        for dataset_name, collector_func in data_collectors.items():
            if dataset_name in self.hud_datasets:
                config = self.hud_datasets[dataset_name]
                logger.info(f"Collecting {config['description']}...")

                try:
                    df = collector_func()

                    if df is not None and not df.empty:
                        # Add metadata
                        df['collection_date'] = datetime.now().isoformat()
                        df['westchester_county'] = True
                        df['county_fips'] = self.westchester_geo['county_fips']
                        df['state_fips'] = self.westchester_geo['state_fips']

                        results['datasets'][dataset_name] = {
                            'description': config['description'],
                            'frequency': config['frequency'],
                            'records_count': len(df),
                            'columns': list(df.columns),
                            'dataframe': df
                        }

                        results['summary']['successful_downloads'] += 1
                        results['summary']['total_records'] += len(df)

                        logger.info(f"✅ Successfully collected {len(df)} records for {dataset_name}")
                    else:
                        results['summary']['failed_downloads'] += 1
                        logger.error(f"❌ No data available for {dataset_name}")

                except Exception as e:
                    results['summary']['failed_downloads'] += 1
                    logger.error(f"❌ Error collecting {dataset_name}: {e}")

                # Brief pause between datasets
                time.sleep(0.5)

        # Save datasets to files
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        for dataset_name, dataset_result in results['datasets'].items():
            try:
                df = dataset_result['dataframe']

                # Save as CSV
                csv_filename = f"{timestamp}_hud_{dataset_name}.csv"
                csv_path = self.output_dir / csv_filename
                df.to_csv(csv_path, index=False)

                # Save as JSON
                json_filename = f"{timestamp}_hud_{dataset_name}.json"
                json_path = self.output_dir / json_filename
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(df.to_dict('records'), f, indent=2, ensure_ascii=False, default=str)

                # Update result with file paths
                dataset_result['csv_file'] = str(csv_path)
                dataset_result['json_file'] = str(json_path)

                logger.info(f"Saved {dataset_name} to {csv_path}")

            except Exception as e:
                logger.error(f"Error saving dataset {dataset_name}: {e}")

        # Create combined housing affordability dataset
        try:
            housing_dfs = []
            for dataset_name in ['fair_market_rents', 'income_limits', 'section8']:
                if dataset_name in results['datasets']:
                    df = results['datasets'][dataset_name]['dataframe']
                    df = df.copy()
                    df['source_dataset'] = dataset_name
                    housing_dfs.append(df)

            if housing_dfs:
                combined_df = pd.concat(housing_dfs, ignore_index=True)

                # Save combined housing data
                combined_csv = self.output_dir / f"{timestamp}_hud_housing_affordability_combined.csv"
                combined_df.to_csv(combined_csv, index=False)

                results['saved_files']['housing_affordability_combined'] = str(combined_csv)
                logger.info(f"Created combined housing affordability dataset: {len(combined_df)} records")

        except Exception as e:
            logger.error(f"Error creating combined housing dataset: {e}")

        # Save collection summary
        summary_file = self.output_dir / f"hud_collection_summary_{timestamp}.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)

        results['saved_files']['summary'] = str(summary_file)

        logger.info(f"\n🎉 HUD Housing Data Collection Complete!")
        logger.info(f"✅ Successfully downloaded: {results['summary']['successful_downloads']}/{results['summary']['total_datasets']} datasets")
        logger.info(f"📊 Total records: {results['summary']['total_records']:,}")
        logger.info(f"📁 Summary saved to: {summary_file}")

        return results

    def generate_housing_report(self, results: Dict[str, Any]) -> str:
        """Generate a comprehensive housing data report"""

        report = []
        report.append("# Westchester County Housing Data Collection Report")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("Source: HUD (Housing and Urban Development) APIs")
        report.append("")

        # Summary
        report.append("## Collection Summary")
        report.append(f"- **Datasets Collected**: {results['summary']['successful_downloads']}")
        report.append(f"- **Total Records**: {results['summary']['total_records']:,}")
        report.append(f"- **Years of Data**: Up to {results['years_collected']} years")
        report.append(f"- **Geography**: Westchester County (FIPS: {results['geography']['county_fips']})")
        report.append("")

        # Housing affordability metrics
        report.append("## Key Housing Metrics Available")
        if 'fair_market_rents' in results['datasets']:
            fmr_data = results['datasets']['fair_market_rents']
            report.append(f"- **Fair Market Rents**: {fmr_data['records_count']} records spanning multiple years")
        if 'income_limits' in results['datasets']:
            il_data = results['datasets']['income_limits']
            report.append(f"- **Income Limits**: {il_data['records_count']} records for various household sizes")
        if 'section8' in results['datasets']:
            s8_data = results['datasets']['section8']
            report.append(f"- **Section 8 Vouchers**: {s8_data['records_count']} records of voucher program data")
        report.append("")

        # Data applications
        report.append("## Potential Applications for Westchester")
        applications = [
            "**Housing Affordability Analysis**: Compare income levels with housing costs",
            "**Policy Development**: Inform affordable housing policies and programs",
            "**Market Analysis**: Track housing market trends and changes",
            "**Grant Applications**: Support federal and state grant applications",
            "**Community Planning**: Guide comprehensive housing strategy development",
            "**Needs Assessment**: Identify housing needs across different income levels"
        ]
        for app in applications:
            report.append(f"- {app}")
        report.append("")

        # Data limitations
        report.append("## Data Limitations and Notes")
        limitations = [
            "Data is provided at county level, may not capture municipal variations",
            "Update frequencies vary by dataset (annual, quarterly, monthly)",
            "Some datasets may have reporting lags",
            "Geographic boundaries are based on official definitions",
            "Data should be used for comparative analysis and trend identification"
        ]
        for limitation in limitations:
            report.append(f"- {limitation}")

        return "\n".join(report)

def main():
    """Main function for command line usage"""
    import argparse

    parser = argparse.ArgumentParser(description='Collect HUD Housing and Urban Development Data')
    parser.add_argument('--output-dir', help='Output directory for data files')
    parser.add_argument('--years-back', type=int, default=5,
                       help='Number of years of historical data to collect (default: 5)')
    parser.add_argument('--generate-report', action='store_true',
                       help='Generate comprehensive housing report')

    args = parser.parse_args()

    # Check for API key
    if not os.getenv('HUD_API_KEY'):
        print("❌ Error: HUD_API_KEY environment variable not found")
        print("Get a free API key at: https://www.huduser.gov/portal/datasets/pdrdatas.html")
        print("Then set it: export HUD_API_KEY=your_api_key")
        return

    # Initialize collector
    collector = HUDDataCollector(output_dir=args.output_dir)

    # Collect data
    results = collector.collect_all_hud_data(years_back=args.years_back)

    if results.get('success', True) and results['summary']['successful_downloads'] > 0:
        print(f"\n📊 Collection Summary:")
        print(f"  ✅ Datasets Downloaded: {results['summary']['successful_downloads']}")
        print(f"  📈 Total Records: {results['summary']['total_records']:,}")
        print(f"  📅 Years of Data: Up to {results['years_collected']} years")

        # Print dataset details
        for dataset_name, dataset_info in results['datasets'].items():
            print(f"  🏠 {dataset_info['description']}: {dataset_info['records_count']:,} records")

        # Generate report if requested
        if args.generate_report:
            report = collector.generate_housing_report(results)
            report_file = collector.output_dir / f"hud_housing_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"  📄 Housing report saved to: {report_file}")
    else:
        print("❌ Data collection failed or no data retrieved")

if __name__ == "__main__":
    main()