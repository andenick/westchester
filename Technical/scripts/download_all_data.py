"""
Download All Data Script

Runs all data importers to download Westchester County data from various sources.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from data_importers.gtfs_importer import MetroNorthGTFSImporter
from data_importers.census_api import CensusAPIClient
from data_importers.ny_state_data import NYStateDataClient

import os
from dotenv import load_dotenv


def main():
    """Run all data importers"""
    
    print("="*70)
    print(" Westchester County Data Platform - Download All Data")
    print("="*70)
    print()
    
    # Load environment variables
    env_path = Path(__file__).parent.parent / "configs" / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        print("[SUCCESS] Loaded environment variables from .env")
    else:
        print("[WARNING] No .env file found - using environment variables only")
    print()
    
    results = []
    
    # 1. Metro-North GTFS Data
    print("\n" + "="*70)
    print("1. Metro-North GTFS Data (Transit)")
    print("="*70)
    try:
        importer = MetroNorthGTFSImporter()
        success, message = importer.run_import()
        results.append(("Metro-North GTFS", success, message))
    except Exception as e:
        results.append(("Metro-North GTFS", False, str(e)))
    
    # 2. Census Bureau Data
    print("\n" + "="*70)
    print("2. U.S. Census Bureau Data (Demographics)")
    print("="*70)
    try:
        api_key = os.getenv('CENSUS_API_KEY')
        client = CensusAPIClient(api_key=api_key)
        success, message = client.run_import(year=2022)
        results.append(("Census Demographics", success, message))
    except Exception as e:
        results.append(("Census Demographics", False, str(e)))
    
    # 3. NY State Open Data
    print("\n" + "="*70)
    print("3. NY State Open Data (Government Records)")
    print("="*70)
    try:
        app_token = os.getenv('NY_STATE_APP_TOKEN')
        client = NYStateDataClient(app_token=app_token)
        
        # Import key datasets (not all, as some may not exist)
        priority_datasets = ['crime_data', 'health_facilities']
        success, message = client.run_import(datasets=priority_datasets)
        results.append(("NY State Data", success, message))
    except Exception as e:
        results.append(("NY State Data", False, str(e)))
    
    # Summary
    print("\n" + "="*70)
    print(" DOWNLOAD SUMMARY")
    print("="*70)
    print()
    
    for name, success, message in results:
        status = "[SUCCESS]" if success else "[FAILED]"
        print(f"{status}: {name}")
        print(f"         {message}")
        print()
    
    success_count = sum(1 for _, success, _ in results if success)
    total_count = len(results)
    
    print("="*70)
    print(f" {success_count}/{total_count} data sources downloaded successfully")
    print("="*70)
    
    return success_count == total_count


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

