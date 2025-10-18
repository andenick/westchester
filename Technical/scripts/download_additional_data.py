"""
Download Additional Data Script

Runs all additional data importers for Westchester County.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from data_importers.school_data_importer import SchoolDataImporter
from data_importers.infrastructure_importer import InfrastructureImporter

import os
from dotenv import load_dotenv


def main():
    """Run all additional data importers"""
    
    print("="*80)
    print(" Westchester County - Additional Data Download")
    print("="*80)
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
    
    # 1. School Data
    print("\n" + "="*80)
    print("1. School Directory Data")
    print("="*80)
    try:
        app_token = os.getenv('NY_STATE_APP_TOKEN')
        importer = SchoolDataImporter(app_token=app_token)
        success, message = importer.run_import()
        results.append(("Schools", success, message))
    except Exception as e:
        results.append(("Schools", False, str(e)))
    
    # 2. Infrastructure (OpenStreetMap)
    print("\n" + "="*80)
    print("2. Infrastructure Data (Parks, Trails, Amenities)")
    print("="*80)
    try:
        importer = InfrastructureImporter()
        success, message = importer.run_import()
        results.append(("Infrastructure", success, message))
    except Exception as e:
        results.append(("Infrastructure", False, str(e)))
    
    # Summary
    print("\n" + "="*80)
    print(" DOWNLOAD SUMMARY")
    print("="*80)
    print()
    
    for name, success, message in results:
        status = "[SUCCESS]" if success else "[FAILED]"
        print(f"{status}: {name}")
        print(f"         {message}")
        print()
    
    success_count = sum(1 for _, success, _ in results if success)
    total_count = len(results)
    
    print("="*80)
    print(f" {success_count}/{total_count} additional data sources downloaded successfully")
    print("="*80)
    print()
    
    if success_count < total_count:
        print("Note: Some data sources failed. Check error messages above.")
        print("You may need to manually download some datasets.")
        print("See MANUAL_DATA_IMPORT_GUIDE.md for instructions.")
    
    return success_count == total_count


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

