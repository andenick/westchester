#!/usr/bin/env python3
"""
NYC Open Data Collector
Collects data from NYC Open Data Portal for regional context
Provides comparative data for Westchester County analysis
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

class NYCOpenDataCollector:
    """Collects data from NYC Open Data Portal"""

    def __init__(self, output_dir: str = None):
        self.output_dir = Path(output_dir or "data/raw/nyc_opendata")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # NYC Open Data API configuration
        self.app_token = os.getenv('NYC_OPEN_DATA_APP_TOKEN')
        self.base_url = "https://data.cityofnewyork.us/resource"
        self.search_url = "https://data.cityofnewyork.us/api/views"

        # Relevant datasets for Westchester County comparison
        self.relevant_datasets = {
            # Education
            "school-attendance-and-enrollment-statistics-2023-24": {
                "name": "School Attendance and Enrollment Statistics",
                "category": "education",
                "description": "NYC school enrollment and attendance data for comparison"
            },
            "school-safety-report": {
                "name": "School Safety Report",
                "category": "education",
                "description": "School safety statistics for regional comparison"
            },
            "doe-high-school-directory-2023-2024": {
                "name": "DOE High School Directory",
                "category": "education",
                "description": "High school information for educational comparison"
            },

            # Housing and Real Estate
            "dob-jobs-now-issued": {
                "name": "DOB Jobs Now Issued",
                "category": "housing",
                "description": "Building permits for construction activity comparison"
            },
            "nyc-dob-permit-issuance": {
                "name": "NYC DOB Permit Issuance",
                "category": "housing",
                "description": "Department of Buildings permit data"
            },
            "hpd-building-registration": {
                "name": "HPD Building Registration",
                "category": "housing",
                "description": "Housing building registration data"
            },
            "hnycc-2a2k": {
                "name": "NYC Housing Database",
                "category": "housing",
                "description": "Comprehensive housing database for comparison"
            },

            # Public Health
            "nc7y-ek9j": {
                "name": "NYC Leading Causes of Death",
                "category": "health",
                "description": "Health statistics for regional comparison"
            },
            "uq7m-59z2": {
                "name": "Epiquery Restaurant Inspection Results",
                "category": "health",
                "description": "Restaurant inspection data"
            },
            "swpk-hqdp": {
                "name": "NYC 311 Service Requests",
                "category": "health",
                "description": "Public service requests for quality of life metrics"
            },

            # Transportation
            "7up4-nza9": {
                "name": "Citi Bike Trip Histories",
                "category": "transportation",
                "description": "Bike share data for transportation analysis"
            },
            "unsg-d27r": {
                "name": "NYC Ferry Ridership",
                "category": "transportation",
                "description": "Ferry ridership data"
            },
            "kavf-qfyz": {
                "name": "Traffic Volume Counts",
                "category": "transportation",
                "description": "Traffic volume data for transportation planning"
            },

            # Economic Development
            "tqy6-5w8h": {
                "name": "NYC Business Acceleration",
                "category": "economic",
                "description": "Business development data"
            },
            "5uva-wxga": {
                "name": "NYC Open Businesses",
                "category": "economic",
                "description": "Current business licenses and permits"
            },
            "iy8u-9trd": {
                "name": "NYC Workforce1 Career Center Events",
                "category": "economic",
                "description": "Workforce development activities"
            },

            # Public Safety
            "uip8-fykc": {
                "name": "NYPD Arrest Data",
                "category": "safety",
                "description": "Arrest data for crime comparison"
            },
            "833y-fsy8": {
                "name": "NYPD Complaint Data",
                "category": "safety",
                "description": "Police complaint data"
            },
            "bq5a-3yan": {
                "name": "FDNY Incidents",
                "category": "safety",
                "description": "Fire department incident data"
            },

            # Environment
            "c3uy-2p5v": {
                "name": "Air Quality Surveillance Data",
                "category": "environment",
                "description": "Air quality measurements"
            },
            "ebb7-jp6j": {
                "name": "NYC Greenhouse Gas Emissions",
                "category": "environment",
                "description": "Environmental impact data"
            },
            "kgn6-ecg8": {
                "name": "Tree Census",
                "category": "environment",
                "description": "Urban forestry data"
            },

            # Demographics
            "sw77-hjdz": {
                "name": "NYC Population Projections",
                "category": "demographics",
                "description": "Population projections for comparison"
            },
            "xywu-7bv9": {
                "name": "NYC Community District Profiles",
                "category": "demographics",
                "description": "Community-level demographic data"
            },
            "kku6-nxdu": {
                "name": "NYC Housing and Vacancy Survey",
                "category": "demographics",
                "description": "Housing characteristics and vacancy rates"
            },

            # Government Services
            "erm2-nwe9": {
                "name": "NYC 311 Service Requests",
                "category": "government",
                "description": "Public service requests for comparative analysis"
            },
            "p9r-w-7hj": {
                "name": "NYC Open Data",
                "category": "government",
                "description": "General open data catalog"
            },

            # Finance and Budget
            "k397-673e": {
                "name": "NYC Budget",
                "category": "finance",
                "description": "Budget data for fiscal comparison"
            },
            "rc79-m6h5": {
                "name": "NYC Spending",
                "category": "finance",
                "description": "City spending data"
            }
        }

        # Rate limiting (NYC Open Data allows ~1000 requests/hour)
        self.request_delay = 0.1  # 0.1 seconds between requests
        self.last_request_time = 0

        # Session for persistent connections
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Westchester Data Platform/1.0 (Regional Data Collection)'
        })

        # Add app token if available
        if self.app_token:
            self.session.headers.update({'X-App-Token': self.app_token})

    def _rate_limit(self):
        """Implement rate limiting for requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.request_delay:
            sleep_time = self.request_delay - time_since_last
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def make_socrata_request(self, dataset_id: str, params: Dict[str, Any] = None) -> Optional[pd.DataFrame]:
        """Make a request to Socrata Open Data API"""
        if params is None:
            params = {}

        # Default parameters
        default_params = {
            '$limit': 50000,  # Maximum records per request
            '$order': ':created_at',  # Order by creation date
        }
        params = {**default_params, **params}

        try:
            url = f"{self.base_url}/{dataset_id}.json"
            self._rate_limit()

            response = self.session.get(url, params=params)
            response.raise_for_status()

            data = response.json()

            if not data:
                logger.warning(f"No data returned for dataset {dataset_id}")
                return None

            df = pd.DataFrame(data)

            # Convert date columns if present
            date_columns = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
            for col in date_columns:
                try:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                except:
                    pass

            logger.info(f"Retrieved {len(df)} records from {dataset_id}")
            return df

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {dataset_id}: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error for {dataset_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error processing {dataset_id}: {e}")
            return None

    def get_dataset_metadata(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a specific dataset"""
        try:
            url = f"{self.search_url}/{dataset_id}.json"
            self._rate_limit()

            response = self.session.get(url)
            response.raise_for_status()

            data = response.json()

            return {
                'id': data.get('id'),
                'name': data.get('name'),
                'description': data.get('description'),
                'category': data.get('category'),
                'columns': data.get('columns', []),
                'rows_count': data.get('rowsCount', 0),
                'created_at': data.get('createdAt'),
                'updated_at': data.get('updatedAt')
            }

        except Exception as e:
            logger.error(f"Failed to get metadata for {dataset_id}: {e}")
            return None

    def collect_dataset(self, dataset_id: str, config: Dict[str, Any],
                       date_range: int = None) -> Optional[Dict[str, Any]]:
        """Collect data from a specific NYC Open Data dataset"""

        logger.info(f"Collecting dataset: {config['name']}")

        try:
            # Get dataset metadata
            metadata = self.get_dataset_metadata(dataset_id)
            if not metadata:
                logger.warning(f"Could not get metadata for {dataset_id}")

            # Build query parameters
            params = {}

            # Add date filtering if requested
            if date_range and metadata:
                date_columns = [col for col in metadata.get('columns', [])
                              if col.get('dataTypeName') in ['date', 'datetime', 'timestamp']]

                if date_columns:
                    # Use first date column found
                    date_col = date_columns[0]['fieldName']
                    start_date = (datetime.now() - timedelta(days=date_range)).strftime('%Y-%m-%d')
                    params[f'${date_col}_after'] = start_date

            # Get data
            df = self.make_socrata_request(dataset_id, params)

            if df is None or df.empty:
                logger.warning(f"No data available for {config['name']}")
                return None

            # Add metadata to dataframe
            df['dataset_id'] = dataset_id
            df['dataset_name'] = config['name']
            df['category'] = config['category']
            df['download_date'] = datetime.now().isoformat()

            return {
                'dataset_id': dataset_id,
                'name': config['name'],
                'category': config['category'],
                'description': config['description'],
                'records_count': len(df),
                'columns': list(df.columns),
                'dataframe': df,
                'metadata': metadata
            }

        except Exception as e:
            logger.error(f"Error collecting dataset {config['name']}: {e}")
            return None

    def collect_all_relevant_data(self, date_range: int = None) -> Dict[str, Any]:
        """Collect all relevant NYC Open Data for Westchester comparison"""

        logger.info("Starting NYC Open Data collection for regional context...")
        logger.info(f"Output directory: {self.output_dir}")

        results = {
            'collection_time': datetime.now().isoformat(),
            'date_range_days': date_range,
            'datasets': {},
            'summary': {
                'total_datasets': len(self.relevant_datasets),
                'successful_downloads': 0,
                'failed_downloads': 0,
                'total_records': 0
            },
            'saved_files': {},
            'categories': {}
        }

        # Collect data from each dataset
        for i, (dataset_id, config) in enumerate(self.relevant_datasets.items(), 1):
            logger.info(f"Processing dataset {i}/{len(self.relevant_datasets)}: {config['name']}")

            try:
                dataset_result = self.collect_dataset(dataset_id, config, date_range)

                if dataset_result:
                    results['datasets'][dataset_id] = dataset_result
                    results['summary']['successful_downloads'] += 1
                    results['summary']['total_records'] += dataset_result['records_count']

                    # Track by category
                    category = config['category']
                    if category not in results['categories']:
                        results['categories'][category] = {
                            'datasets': [],
                            'total_records': 0
                        }
                    results['categories'][category]['datasets'].append(dataset_id)
                    results['categories'][category]['total_records'] += dataset_result['records_count']

                    logger.info(f"✅ Successfully collected {dataset_result['records_count']:,} records")
                else:
                    results['summary']['failed_downloads'] += 1
                    logger.error(f"❌ Failed to collect {config['name']}")

            except Exception as e:
                results['summary']['failed_downloads'] += 1
                logger.error(f"❌ Error processing {config['name']}: {e}")

            # Brief pause between datasets
            time.sleep(0.2)

        # Save datasets to files
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        for dataset_id, dataset_result in results['datasets'].items():
            try:
                df = dataset_result['dataframe']

                # Save as CSV
                csv_filename = f"{timestamp}_nyc_{dataset_id}.csv"
                csv_path = self.output_dir / csv_filename
                df.to_csv(csv_path, index=False)

                # Save as JSON
                json_filename = f"{timestamp}_nyc_{dataset_id}.json"
                json_path = self.output_dir / json_filename
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(df.to_dict('records'), f, indent=2, ensure_ascii=False, default=str)

                # Update result with file paths
                dataset_result['csv_file'] = str(csv_path)
                dataset_result['json_file'] = str(json_path)

                logger.info(f"Saved {dataset_id} to {csv_path}")

            except Exception as e:
                logger.error(f"Error saving dataset {dataset_id}: {e}")

        # Create combined datasets by category
        for category, category_info in results['categories'].items():
            try:
                category_dfs = []
                for dataset_id in category_info['datasets']:
                    if dataset_id in results['datasets']:
                        df = results['datasets'][dataset_id]['dataframe']
                        # Add a source column to identify the dataset
                        df = df.copy()
                        df['source_dataset'] = results['datasets'][dataset_id]['name']
                        category_dfs.append(df)

                if category_dfs:
                    combined_df = pd.concat(category_dfs, ignore_index=True)

                    # Save combined category data
                    combined_csv = self.output_dir / f"{timestamp}_nyc_category_{category}.csv"
                    combined_df.to_csv(combined_csv, index=False)

                    results['saved_files'][f'category_{category}'] = str(combined_csv)
                    logger.info(f"Created combined {category} dataset: {len(combined_df)} records")

            except Exception as e:
                logger.error(f"Error creating combined dataset for {category}: {e}")

        # Save collection summary
        summary_file = self.output_dir / f"nyc_collection_summary_{timestamp}.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)

        results['saved_files']['summary'] = str(summary_file)

        logger.info(f"\n🎉 NYC Open Data Collection Complete!")
        logger.info(f"✅ Successfully downloaded: {results['summary']['successful_downloads']}/{results['summary']['total_datasets']} datasets")
        logger.info(f"📊 Total records: {results['summary']['total_records']:,}")
        logger.info(f"📁 Summary saved to: {summary_file}")

        return results

    def generate_comparison_summary(self, results: Dict[str, Any]) -> str:
        """Generate a summary comparison between NYC and Westchester contexts"""

        summary = []
        summary.append("# NYC Open Data Collection Summary")
        summary.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        summary.append("Purpose: Provide regional context for Westchester County analysis")
        summary.append("")

        # Overall summary
        summary.append("## Collection Summary")
        summary.append(f"- **Datasets Collected**: {results['summary']['successful_downloads']}")
        summary.append(f"- **Total Records**: {results['summary']['total_records']:,}")
        summary.append(f"- **Date Range**: Last {results.get('date_range_days', 'all')} days")
        summary.append("")

        # Data by category
        summary.append("## Data Categories")
        for category, info in results['categories'].items():
            summary.append(f"### {category.title()}")
            summary.append(f"- **Datasets**: {len(info['datasets'])}")
            summary.append(f"- **Records**: {info['total_records']:,}")

            # List datasets in this category
            for dataset_id in info['datasets']:
                if dataset_id in results['datasets']:
                    dataset_name = results['datasets'][dataset_id]['name']
                    record_count = results['datasets'][dataset_id]['records_count']
                    summary.append(f"  - {dataset_name}: {record_count:,} records")
            summary.append("")

        # Potential use cases for Westchester
        summary.append("## Potential Uses for Westchester Analysis")
        use_cases = {
            "Education": "Compare school performance, enrollment trends, and educational outcomes",
            "Housing": "Analyze housing market trends, construction activity, and affordability patterns",
            "Transportation": "Study transit usage, traffic patterns, and mobility trends",
            "Public Health": "Compare health outcomes, disease patterns, and healthcare access",
            "Economic Development": "Analyze business activity, employment trends, and economic indicators",
            "Public Safety": "Compare crime patterns, emergency response, and safety metrics",
            "Environment": "Study air quality, environmental impacts, and sustainability metrics"
        }

        for category, description in use_cases.items():
            if category.lower() in results['categories']:
                summary.append(f"- **{category}**: {description}")

        summary.append("")
        summary.append("## Data Quality Notes")
        summary.append("- Data is provided as-is from NYC Open Data Portal")
        summary.append("- Some datasets may have different update frequencies")
        summary.append("- Geographic boundaries differ between NYC and Westchester County")
        summary.append("- Use data for comparative analysis rather than direct substitution")

        return "\n".join(summary)

def main():
    """Main function for command line usage"""
    import argparse

    parser = argparse.ArgumentParser(description='Collect NYC Open Data for Regional Context')
    parser.add_argument('--output-dir', help='Output directory for data files')
    parser.add_argument('--date-range', type=int,
                       help='Only collect data from last N days')
    parser.add_argument('--category', help='Only collect specific category of data')
    parser.add_argument('--generate-summary', action='store_true',
                       help='Generate comparison summary')

    args = parser.parse_args()

    # Initialize collector
    collector = NYCOpenDataCollector(output_dir=args.output_dir)

    # Filter by category if specified
    if args.category:
        original_datasets = collector.relevant_datasets.copy()
        collector.relevant_datasets = {
            k: v for k, v in original_datasets.items()
            if v['category'] == args.category.lower()
        }
        logger.info(f"Filtered to {len(collector.relevant_datasets)} datasets in category: {args.category}")

    # Collect data
    results = collector.collect_all_relevant_data(date_range=args.date_range)

    if results['summary']['successful_downloads'] > 0:
        print(f"\n📊 Collection Summary:")
        print(f"  ✅ Datasets Downloaded: {results['summary']['successful_downloads']}")
        print(f"  📈 Total Records: {results['summary']['total_records']:,}")

        # Print category breakdown
        print(f"  📂 Data Categories:")
        for category, info in results['categories'].items():
            print(f"    - {category.title()}: {len(info['datasets'])} datasets, {info['total_records']:,} records")

        # Generate summary if requested
        if args.generate_summary:
            summary = collector.generate_comparison_summary(results)
            summary_file = collector.output_dir / f"nyc_comparison_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(summary)
            print(f"  📄 Comparison summary saved to: {summary_file}")
    else:
        print("❌ No data collected successfully")

if __name__ == "__main__":
    main()