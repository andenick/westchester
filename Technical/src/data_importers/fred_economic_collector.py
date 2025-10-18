#!/usr/bin/env python3
"""
Federal Reserve Economic Data (FRED) Collector
Collects economic indicators relevant to Westchester County
Provides comprehensive economic data for municipal planning and analysis
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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FREDDataCollector:
    """Collects economic data from Federal Reserve Economic Data (FRED)"""

    def __init__(self, output_dir: str = None):
        self.output_dir = Path(output_dir or "data/raw/economics/fred")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # FRED API configuration
        self.api_key = os.getenv('FRED_API_KEY')
        self.base_url = "https://api.stlouisfed.org/fred"

        # Westchester County and NY relevant economic series
        self.westchester_series = {
            # Employment and Labor
            "NYWESTPOP": "Westchester County, NY Population",
            "NYWEST6URN": "Westchester County, NY Unemployment Rate",
            "NYWEST5URN": "Westchester County, NY Unemployment Rate (5-year average)",
            "NYWESTEMP": "Westchester County, NY All Employees: Total Nonfarm",

            # New York State data (for comparison)
            "NYURN": "New York State Unemployment Rate",
            "NYPOP": "New York State Population",
            "NYEMP": "New York State All Employees: Total Nonfarm",

            # Housing Market Indicators
            "MORTGAGE30US": "30-Year Fixed Rate Mortgage Average",
            "MORTGAGE15US": "15-Year Fixed Rate Mortgage Average",
            "MSACSR": "Monthly Supply of Houses",
            "PERMIT": "New Private Housing Units Authorized by Building Permits",
            "HOUST": "New Private Housing Units Started",
            "TLRESCONS": "Total Construction Spending: Residential",

            # Economic Indicators
            "GDP": "Gross Domestic Product",
            "GDPC1": "Real Gross Domestic Product",
            "CPIAUCSL": "Consumer Price Index for All Urban Consumers",
            "UNRATE": "National Unemployment Rate",
            "PAYEMS": "All Employees: Total Nonfarm Payrolls",
            "INDPRO": "Industrial Production Index",
            "UMCSENT": "University of Michigan Consumer Sentiment",

            # Interest Rates and Credit
            "FEDFUNDS": "Federal Funds Effective Rate",
            "DGS10": "Market Yield on U.S. Treasury Securities at 10-Year Constant Maturity",
            "DGS2": "Market Yield on U.S. Treasury Securities at 2-Year Constant Maturity",
            "DPRIME": "Bank Prime Loan Rate",

            # Housing Price Indices
            "CSUSHPISA": "S&P/Case-Shiller U.S. National Home Price Index",
            "NYXRSA": "New York Home Price Index",
            "MSPUS": "Median Sales Price of Houses Sold",

            # Construction and Real Estate
            "PERMIT1": "New Private Housing Units Authorized by Building Permits: 1-Unit Structures",
            "PERMIT2": "New Private Housing Units Authorized by Building Permits: 2-4 Unit Structures",
            "PERMIT5": "New Private Housing Units Authorized by Building Permits: 5+ Unit Structures",

            # Income and Poverty
            "MEHOINUSA672N": "Median Household Income",
            "PCEPI": "Personal Consumption Expenditures: Chain-type Price Index",
            "DPCCRV1M225NBEA": "Personal Consumption Expenditures",

            # Business and Economic Activity
            "BUSINV": "Business Inventories",
            "RETAIL": "Retail Trade Sales",
            "ISRATIO": "Total Business Inventories to Sales Ratio",
            "DGORDER": "Manufacturers' New Orders: Durable Goods",

            # Financial Markets
            "SP500": "S&P 500",
            "DJIA": "Dow Jones Industrial Average",
            "DEXUSEU": "U.S. / Euro Exchange Rate",
            "DEXJPUS": "U.S. / Japan Exchange Rate",

            # Commodities
            "DHHNGSP": "Henry Hub Natural Gas Spot Price",
            "CO": "Commodity Research Bureau Index",
            "GASDESW": "U.S. All Grades All Formulations Retail Gasoline Prices"
        }

        # Additional economic series for regional context
        self.regional_series = {
            # Northeast Region
            "NORTURN": "Northeast Region Unemployment Rate",
            "NORTPOP": "Northeast Region Population",
            "NORTEMP": "Northeast Region All Employees: Total Nonfarm",

            # Metropolitan areas (closest to Westchester)
            "NYGSPA": "New York-Newark-Jersey City, NY-NJ-PA Gross Domestic Product",
            "NYC672URN": "New York City Unemployment Rate",
            "NYCPOP": "New York City Population",

            # County comparison data
            "NALAGALL": "Nonfarm Payrolls: All Employees, Government",
            "CES0000000001": "All Employees, Total Nonfarm",
            "CES2000000001": "All Employees, Construction",
            "LASST010000000000003": "State and Local Government Employees"
        }

        # Combine all series
        self.all_series = {**self.westchester_series, **self.regional_series}

        # Rate limiting (FRED allows 120 requests per minute)
        self.request_delay = 0.5  # 0.5 seconds between requests
        self.last_request_time = 0

        # Session for persistent connections
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Westchester Data Platform/1.0 (Economic Data Collection)'
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
        """Check if FRED API key is available"""
        if not self.api_key:
            logger.error("FRED_API_KEY environment variable not found")
            logger.info("Get a free API key at: https://fred.stlouisfed.org/docs/api/api_key.html")
            return False
        return True

    def make_fred_request(self, endpoint: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Make a request to FRED API with proper error handling"""
        if not self.check_api_key():
            return None

        params['api_key'] = self.api_key
        params['file_type'] = 'json'

        try:
            self._rate_limit()
            response = self.session.get(f"{self.base_url}/{endpoint}", params=params)
            response.raise_for_status()

            data = response.json()

            # Check for API errors
            if 'error_code' in data:
                logger.error(f"FRED API error: {data.get('error_message', 'Unknown error')}")
                return None

            return data

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return None

    def get_series_info(self, series_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific series"""
        data = self.make_fred_request('series', {
            'series_id': series_id
        })

        if data and 'seriess' in data and len(data['seriess']) > 0:
            return data['seriess'][0]

        return None

    def get_series_observations(self, series_id: str, start_date: str = None, end_date: str = None) -> Optional[pd.DataFrame]:
        """Get observations for a specific series"""
        params = {
            'series_id': series_id
        }

        if start_date:
            params['observation_start'] = start_date
        if end_date:
            params['observation_end'] = end_date

        data = self.make_fred_request('series/observations', params)

        if data and 'observations' in data:
            df = pd.DataFrame(data['observations'])

            # Convert date column and values
            df['date'] = pd.to_datetime(df['date'])
            df['value'] = pd.to_numeric(df['value'], errors='coerce')

            # Sort by date
            df = df.sort_values('date').reset_index(drop=True)

            return df

        return None

    def get_multiple_series(self, series_ids: List[str], start_date: str = None, end_date: str = None) -> Dict[str, pd.DataFrame]:
        """Get multiple series efficiently"""
        results = {}

        logger.info(f"Downloading {len(series_ids)} economic series from FRED...")

        for i, series_id in enumerate(series_ids, 1):
            logger.info(f"Downloading series {i}/{len(series_ids)}: {series_id}")

            # Get series observations
            df = self.get_series_observations(series_id, start_date, end_date)

            if df is not None and not df.empty:
                results[series_id] = df
                logger.info(f"✅ {series_id}: {len(df)} observations")
            else:
                logger.warning(f"❌ {series_id}: No data available")

            # Brief pause between series
            time.sleep(0.1)

        return results

    def collect_economic_data(self, years_back: int = 10) -> Dict[str, Any]:
        """Collect all economic data for Westchester County analysis"""

        if not self.check_api_key():
            return {
                'success': False,
                'error': 'FRED API key not available',
                'data': {}
            }

        logger.info("Starting comprehensive FRED economic data collection...")
        logger.info(f"Output directory: {self.output_dir}")

        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=years_back * 365)
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')

        logger.info(f"Date range: {start_date_str} to {end_date_str}")

        results = {
            'collection_time': datetime.now().isoformat(),
            'date_range': {
                'start': start_date_str,
                'end': end_date_str,
                'years_back': years_back
            },
            'series_data': {},
            'series_metadata': {},
            'summary': {
                'total_series': len(self.all_series),
                'successful_downloads': 0,
                'failed_downloads': 0,
                'total_observations': 0
            },
            'saved_files': {}
        }

        # Get series metadata first
        logger.info("Getting series metadata...")
        for series_id, series_name in self.all_series.items():
            series_info = self.get_series_info(series_id)
            if series_info:
                results['series_metadata'][series_id] = {
                    'id': series_info.get('id'),
                    'title': series_info.get('title'),
                    'units': series_info.get('units'),
                    'frequency': series_info.get('frequency_short'),
                    'seasonal_adjustment': series_info.get('seasonal_adjustment_short'),
                    'last_updated': series_info.get('last_updated'),
                    'observation_start': series_info.get('observation_start'),
                    'observation_end': series_info.get('observation_end'),
                    'description': series_name
                }

        logger.info(f"Retrieved metadata for {len(results['series_metadata'])} series")

        # Download all series data
        series_data = self.get_multiple_series(
            list(self.all_series.keys()),
            start_date_str,
            end_date_str
        )

        # Process and save each series
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        for series_id, df in series_data.items():
            try:
                # Add metadata to dataframe
                metadata = results['series_metadata'].get(series_id, {})
                df['series_id'] = series_id
                df['series_title'] = metadata.get('title', series_id)
                df['units'] = metadata.get('units', '')
                df['frequency'] = metadata.get('frequency', '')

                # Save as CSV
                csv_filename = f"{timestamp}_fred_{series_id.lower()}.csv"
                csv_path = self.output_dir / csv_filename
                df.to_csv(csv_path, index=False)

                # Save as JSON
                json_filename = f"{timestamp}_fred_{series_id.lower()}.json"
                json_path = self.output_dir / json_filename
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(df.to_dict('records'), f, indent=2, ensure_ascii=False, default=str)

                results['series_data'][series_id] = {
                    'observations': len(df),
                    'date_range': {
                        'start': df['date'].min().isoformat(),
                        'end': df['date'].max().isoformat()
                    },
                    'csv_file': str(csv_path),
                    'json_file': str(json_path)
                }

                results['summary']['successful_downloads'] += 1
                results['summary']['total_observations'] += len(df)

            except Exception as e:
                logger.error(f"Error processing series {series_id}: {e}")
                results['summary']['failed_downloads'] += 1

        # Create combined dataset
        try:
            combined_data = {}
            for series_id, df in series_data.items():
                if not df.empty:
                    # Rename value column to series_id
                    df_renamed = df[['date', 'value']].copy()
                    df_renamed = df_renamed.rename(columns={'value': series_id})
                    combined_data[series_id] = df_renamed.set_index('date')[series_id]

            if combined_data:
                combined_df = pd.DataFrame(combined_data)
                combined_df = combined_df.sort_index()

                # Save combined dataset
                combined_csv = self.output_dir / f"{timestamp}_fred_all_series.csv"
                combined_df.to_csv(combined_csv)

                combined_json = self.output_dir / f"{timestamp}_fred_all_series.json"
                with open(combined_json, 'w', encoding='utf-8') as f:
                    json.dump(combined_df.reset_index().to_dict('records'), f, indent=2, default=str)

                results['saved_files']['combined_csv'] = str(combined_csv)
                results['saved_files']['combined_json'] = str(combined_json)

                logger.info(f"Created combined dataset: {len(combined_df)} rows, {len(combined_df.columns)} series")

        except Exception as e:
            logger.error(f"Error creating combined dataset: {e}")

        # Save collection summary
        summary_file = self.output_dir / f"fred_collection_summary_{timestamp}.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)

        results['saved_files']['summary'] = str(summary_file)

        logger.info(f"\n🎉 FRED Economic Data Collection Complete!")
        logger.info(f"✅ Successfully downloaded: {results['summary']['successful_downloads']}/{results['summary']['total_series']} series")
        logger.info(f"📊 Total observations: {results['summary']['total_observations']:,}")
        logger.info(f"📁 Summary saved to: {summary_file}")

        return results

    def generate_economic_report(self, results: Dict[str, Any]) -> str:
        """Generate a summary report of the collected economic data"""

        report = []
        report.append("# Westchester County Economic Data Collection Report")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        # Summary
        report.append("## Collection Summary")
        report.append(f"- **Total Series Requested**: {results['summary']['total_series']}")
        report.append(f"- **Successful Downloads**: {results['summary']['successful_downloads']}")
        report.append(f"- **Failed Downloads**: {results['summary']['failed_downloads']}")
        report.append(f"- **Total Observations**: {results['summary']['total_observations']:,}")
        report.append(f"- **Date Range**: {results['date_range']['start']} to {results['date_range']['end']}")
        report.append("")

        # Key indicators
        report.append("## Key Economic Indicators Collected")
        key_indicators = [
            "NYWEST6URN", "MORTGAGE30US", "CSUSHPISA", "GDP", "UNRATE", "CPIAUCSL"
        ]

        for indicator in key_indicators:
            if indicator in results['series_data']:
                data = results['series_data'][indicator]
                metadata = results['series_metadata'].get(indicator, {})
                report.append(f"- **{metadata.get('title', indicator)}**: {data['observations']} observations")

        report.append("")

        # Data categories
        report.append("## Data Categories")
        categories = {
            "Employment & Labor": [s for s in self.westchester_series.keys() if 'EMP' in s or 'URN' in s or 'POP' in s],
            "Housing Market": [s for s in self.westchester_series.keys() if any(x in s for x in ['MORTGAGE', 'HOUSE', 'PERMIT', 'HOME', 'SP'])],
            "Economic Activity": [s for s in self.westchester_series.keys() if s in ['GDP', 'GDPC1', 'INDPRO', 'RETAIL', 'BUSINV']],
            "Financial Markets": [s for s in self.westchester_series.keys() if any(x in s for x in ['FEDFUNDS', 'DGS', 'SP', 'DJI'])],
            "Price Indices": [s for s in self.westchester_series.keys() if s in ['CPIAUCSL', 'PCEPI', 'CO']]
        }

        for category, series_list in categories.items():
            available_series = [s for s in series_list if s in results['series_data']]
            if available_series:
                report.append(f"### {category}")
                for series_id in available_series:
                    metadata = results['series_metadata'].get(series_id, {})
                    report.append(f"- {metadata.get('title', series_id)}")
                report.append("")

        return "\n".join(report)

def main():
    """Main function for command line usage"""
    import argparse

    parser = argparse.ArgumentParser(description='Collect FRED Economic Data')
    parser.add_argument('--output-dir', help='Output directory for data files')
    parser.add_argument('--years-back', type=int, default=10,
                       help='Number of years of historical data to collect (default: 10)')
    parser.add_argument('--generate-report', action='store_true',
                       help='Generate summary report')

    args = parser.parse_args()

    # Check for API key
    if not os.getenv('FRED_API_KEY'):
        print("❌ Error: FRED_API_KEY environment variable not found")
        print("Get a free API key at: https://fred.stlouisfed.org/docs/api/api_key.html")
        print("Then set it: export FRED_API_KEY=your_api_key")
        return

    # Initialize collector
    collector = FREDDataCollector(output_dir=args.output_dir)

    # Collect data
    results = collector.collect_economic_data(years_back=args.years_back)

    if results.get('success', True) and results['summary']['successful_downloads'] > 0:
        print(f"\n📊 Collection Summary:")
        print(f"  ✅ Series Downloaded: {results['summary']['successful_downloads']}")
        print(f"  📈 Total Observations: {results['summary']['total_observations']:,}")
        print(f"  📅 Date Range: {results['date_range']['start']} to {results['date_range']['end']}")

        # Generate report if requested
        if args.generate_report:
            report = collector.generate_economic_report(results)
            report_file = collector.output_dir / f"fred_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"  📄 Report saved to: {report_file}")
    else:
        print("❌ Data collection failed or no data retrieved")

if __name__ == "__main__":
    main()