"""
New York State Open Data API Client for Westchester County

Downloads data from NY State Open Data portal (data.ny.gov) filtering for
Westchester County records.
"""

import requests
import json
import csv
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class NYStateDataClient:
    """Client for NY State Open Data portal (Socrata platform)"""
    
    BASE_URL = "https://data.ny.gov/resource"
    
    # Key datasets relevant to Westchester County
    DATASETS = {
        # Real Property Tax Services
        'property_assessments': {
            'id': 'iq85-sdzs',  # Real Property Tax Parcel Data
            'description': 'Property assessment data',
            'filter': "county_name='Westchester'",
        },
        
        # Building & Construction
        'building_permits': {
            'id': '8y4t-faws',  # Building Permits (if available)
            'description': 'Building permits and construction data',
            'filter': "county='Westchester'",
        },
        
        # Crime Statistics
        'crime_data': {
            'id': 'ca8h-8gjq',  # Index Crimes by County
            'description': 'Crime statistics by county',
            'filter': "county='Westchester'",
        },
        
        # Education
        'school_data': {
            'id': '3bkp-49pg',  # School District Data
            'description': 'School enrollment and performance',
            'filter': "county_name='Westchester'",
        },
        
        # Health
        'health_facilities': {
            'id': 'vn5v-hh5r',  # Health Facility General Information
            'description': 'Licensed health facilities',
            'filter': "county='Westchester'",
        },
        
        # Environment
        'water_quality': {
            'id': 'qw3f-8rqp',  # Water Quality Data
            'description': 'Water quality monitoring',
            'filter': "county='Westchester'",
        },
    }
    
    def __init__(self, app_token: Optional[str] = None, output_dir: Optional[str] = None):
        """
        Initialize NY State Data client
        
        Args:
            app_token: Socrata app token (optional but recommended)
            output_dir: Directory to save downloaded data
        """
        self.app_token = app_token
        
        if output_dir is None:
            base_path = Path(__file__).parent.parent.parent / "data" / "raw" / "ny_state"
        else:
            base_path = Path(output_dir)
        
        self.output_dir = base_path
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.headers = {}
        if app_token:
            self.headers['X-App-Token'] = app_token
    
    def fetch_dataset(self, dataset_id: str, filter_clause: Optional[str] = None, 
                      limit: int = 10000) -> Optional[List[Dict]]:
        """
        Fetch dataset from NY State Open Data
        
        Args:
            dataset_id: Socrata dataset ID (e.g., 'iq85-sdzs')
            filter_clause: SoQL WHERE clause for filtering
            limit: Maximum number of records to fetch
            
        Returns:
            List of records or None if error
        """
        url = f"{self.BASE_URL}/{dataset_id}.json"
        
        params = {
            '$limit': limit,
            '$offset': 0,
        }
        
        if filter_clause:
            params['$where'] = filter_clause
        
        print(f"Fetching dataset {dataset_id}...")
        print(f"Filter: {filter_clause}")
        
        all_records = []
        
        try:
            while True:
                response = requests.get(url, headers=self.headers, params=params, timeout=30)
                response.raise_for_status()
                
                records = response.json()
                
                if not records:
                    break
                
                all_records.extend(records)
                print(f"  Fetched {len(all_records)} records so far...")
                
                if len(records) < limit:
                    # No more records to fetch
                    break
                
                # Move to next page
                params['$offset'] += limit
            
            print(f"[SUCCESS] Total records fetched: {len(all_records)}")
            return all_records
            
        except requests.RequestException as e:
            print(f"[FAILED] Error fetching dataset: {e}")
            if not self.app_token:
                print("[WARNING] Note: No app token provided. Consider registering at https://data.ny.gov/")
            return None
    
    def fetch_westchester_dataset(self, dataset_name: str) -> Optional[List[Dict]]:
        """
        Fetch a predefined dataset filtered for Westchester County
        
        Args:
            dataset_name: Name from DATASETS dictionary
            
        Returns:
            List of records or None if error
        """
        if dataset_name not in self.DATASETS:
            print(f"[FAILED] Unknown dataset: {dataset_name}")
            print(f"Available datasets: {', '.join(self.DATASETS.keys())}")
            return None
        
        dataset = self.DATASETS[dataset_name]
        print(f"\nFetching: {dataset['description']}")
        
        return self.fetch_dataset(
            dataset_id=dataset['id'],
            filter_clause=dataset.get('filter')
        )
    
    def save_data(self, data: List[Dict], filename: str, format: str = 'json'):
        """
        Save data to file
        
        Args:
            data: List of records
            filename: Output filename (without extension)
            format: Output format ('json' or 'csv')
        """
        if not data:
            print("[WARNING] No data to save")
            return
        
        if format == 'json':
            filepath = self.output_dir / f"{filename}.json"
            
            # Add metadata
            output = {
                'metadata': {
                    'source': 'NY State Open Data',
                    'source_url': 'https://data.ny.gov',
                    'fetched_date': datetime.now().isoformat(),
                    'record_count': len(data),
                    'county': 'Westchester'
                },
                'data': data
            }
            
            with open(filepath, 'w') as f:
                json.dump(output, f, indent=2)
            print(f"[SUCCESS] Saved to {filepath}")
            
        elif format == 'csv':
            filepath = self.output_dir / f"{filename}.csv"
            
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                if data:
                    # Collect all possible fields from all records
                    all_fields = set()
                    for record in data:
                        all_fields.update(record.keys())
                    
                    writer = csv.DictWriter(f, fieldnames=sorted(all_fields))
                    writer.writeheader()
                    writer.writerows(data)
                    print(f"[SUCCESS] Saved to {filepath}")
    
    def fetch_available_datasets(self) -> List[Dict]:
        """
        Fetch list of available datasets from NY State Open Data catalog
        
        Returns:
            List of dataset metadata
        """
        url = "https://data.ny.gov/api/views/metadata/v1"
        
        print("Fetching available datasets from catalog...")
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"[FAILED] Error fetching catalog: {e}")
            return []
    
    def run_import(self, datasets: Optional[List[str]] = None) -> Tuple[bool, str]:
        """
        Run complete import of NY State data
        
        Args:
            datasets: List of dataset names to import (default: all)
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            if not self.app_token:
                print("[WARNING] Warning: No app token provided. Rate limits may apply.")
                print("  Register at: https://data.ny.gov/profile/app_tokens")
                print()
            
            if datasets is None:
                datasets = list(self.DATASETS.keys())
            
            results = []
            
            for i, dataset_name in enumerate(datasets, 1):
                print(f"\n[{i}/{len(datasets)}] Processing {dataset_name}...")
                
                data = self.fetch_westchester_dataset(dataset_name)
                
                if data:
                    filename = f"westchester_{dataset_name}"
                    self.save_data(data, filename, 'json')
                    self.save_data(data, filename, 'csv')
                    results.append(f"{dataset_name} ({len(data)} records)")
                else:
                    print(f"[WARNING] No data fetched for {dataset_name}")
            
            if not results:
                return False, "No data was successfully imported"
            
            return True, f"Successfully imported: {', '.join(results)}"
            
        except Exception as e:
            return False, f"Import failed: {str(e)}"


def main():
    """Command-line interface for the NY State data importer"""
    import os
    
    print("="*60)
    print("NY State Open Data Importer - Westchester County")
    print("="*60)
    print()
    
    # Check for app token in environment variable
    app_token = os.getenv('NY_STATE_APP_TOKEN')
    
    if not app_token:
        print("No NY_STATE_APP_TOKEN environment variable found.")
        print("You can still proceed, but rate limits may apply.")
        print()
        response = input("Enter your Socrata app token (or press Enter to skip): ").strip()
        if response:
            app_token = response
    
    client = NYStateDataClient(app_token=app_token)
    
    # List available datasets
    print("\nAvailable datasets:")
    for name, info in client.DATASETS.items():
        print(f"  - {name}: {info['description']}")
    print()
    
    # Import all datasets
    success, message = client.run_import()
    
    print()
    print("="*60)
    if success:
        print(f"✓ SUCCESS: {message}")
    else:
        print(f"✗ FAILED: {message}")
    print("="*60)


if __name__ == "__main__":
    main()

