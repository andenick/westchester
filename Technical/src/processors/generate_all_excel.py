"""
Generate All Excel Files

Master script to run all data processors and generate Druck-compliant Excel files.
"""

import sys
from pathlib import Path

# Add processors to path
sys.path.insert(0, str(Path(__file__).parent))

from process_demographics import DemographicsProcessor
from process_transit import TransitProcessor


def main():
    """Run all Excel generation"""
    print("="*80)
    print(" WESTCHESTER COUNTY DATA PLATFORM")
    print(" Druck-Compliant Excel File Generation")
    print("="*80)
    print()
    print("This script will generate all Excel files following Druck standards:")
    print("  - ONE sheet per file (no multi-tab workbooks)")
    print("  - Machine-readable columns with proper headers")
    print("  - Timestamped filenames [YYYY.MM.DD]")
    print("  - Professional black & white formatting")
    print()
    print("="*80)
    print()
    
    all_results = []
    
    # 1. Demographics
    print("\n" + "="*80)
    print(" SECTION 1: DEMOGRAPHICS DATA")
    print("="*80)
    
    demo_processor = DemographicsProcessor()
    
    print("\n[1.1] County-level demographics...")
    county_file = demo_processor.create_county_excel(2022)
    if county_file:
        all_results.append(("Demographics - County", county_file))
    
    print("\n[1.2] Census tract demographics...")
    tract_file = demo_processor.create_tract_excel(2022)
    if tract_file:
        all_results.append(("Demographics - Tracts", tract_file))
    
    print("\n[1.3] Municipality demographics...")
    muni_file = demo_processor.create_municipality_excel(2022)
    if muni_file:
        all_results.append(("Demographics - Municipalities", muni_file))
    
    # 2. Transit
    print("\n" + "="*80)
    print(" SECTION 2: TRANSIT DATA")
    print("="*80)
    
    transit_processor = TransitProcessor()
    
    print("\n[2.1] Metro-North stations...")
    stations_file = transit_processor.create_stations_excel()
    if stations_file:
        all_results.append(("Transit - Stations", stations_file))
    
    print("\n[2.2] Transit accessibility analysis...")
    access_file = transit_processor.create_accessibility_analysis_excel()
    if access_file:
        all_results.append(("Transit - Accessibility", access_file))
    
    # Final Summary
    print("\n" + "="*80)
    print(" FINAL SUMMARY - ALL EXCEL FILES GENERATED")
    print("="*80)
    print()
    
    if all_results:
        for i, (name, filepath) in enumerate(all_results, 1):
            print(f"{i}. {name}")
            print(f"   File: {filepath.name}")
            print(f"   Path: {filepath}")
            print()
        
        print("="*80)
        print(f" SUCCESS: {len(all_results)} Excel files created")
        print("="*80)
        print()
        print("All files saved to: Output/Data/Results/")
        print()
        print("Next Steps:")
        print("  1. Validate files: python Technical/scripts/validate_excel.py")
        print("  2. Review data in Excel application")
        print("  3. Confirm Druck compliance (one sheet per file)")
        print()
    else:
        print("[WARNING] No Excel files were generated.")
        print("Make sure data has been downloaded:")
        print("  python Technical/scripts/download_all_data.py")
        print()
    
    print("="*80)
    
    return len(all_results) > 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

