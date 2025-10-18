"""
Process Transit Data

Processes Metro-North GTFS data and calculates station coverage metrics.
"""

import pandas as pd
import json
from pathlib import Path
from typing import Dict, List
from excel_generator import DruckExcelGenerator


class TransitProcessor:
    """Process Metro-North transit data for Excel export"""
    
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            self.data_dir = Path(__file__).parent.parent.parent / "data" / "raw" / "transit"
        else:
            self.data_dir = Path(data_dir)
    
    def load_stations(self) -> List[Dict]:
        """Load Metro-North station data"""
        json_path = self.data_dir / "westchester_metro_north_stations.json"
        
        if not json_path.exists():
            print(f"[WARNING] Station data not found: {json_path}")
            return []
        
        with open(json_path, 'r') as f:
            return json.load(f)
    
    def create_stations_excel(self) -> Path:
        """Create Metro-North stations Excel file"""
        stations = self.load_stations()
        
        if not stations:
            print("[FAILED] No station data available")
            return None
        
        df = pd.DataFrame(stations)
        
        # Select and rename columns
        columns_to_keep = {
            'stop_name': 'Station Name',
            'stop_id': 'Station ID',
            'stop_code': 'Station Code',
            'stop_lat': 'Latitude',
            'stop_lon': 'Longitude',
            'wheelchair_boarding': 'Wheelchair Accessible',
        }
        
        available_cols = {k: v for k, v in columns_to_keep.items() if k in df.columns}
        df_clean = df[list(available_cols.keys())].rename(columns=available_cols)
        
        # Convert wheelchair boarding to readable format
        if 'Wheelchair Accessible' in df_clean.columns:
            df_clean['Wheelchair Accessible'] = df_clean['Wheelchair Accessible'].map({
                '0': 'No',
                '1': 'Yes',
                '2': 'Unknown'
            }).fillna('Unknown')
        
        # Sort by station name
        df_clean = df_clean.sort_values('Station Name')
        
        generator = DruckExcelGenerator()
        filepath = generator.create_excel_file(
            df_clean,
            "westchester_metro_north_stations",
            sheet_name="Stations",
            add_timestamp=True
        )
        
        print(f"[SUCCESS] Created stations Excel: {filepath}")
        return filepath
    
    def create_accessibility_analysis_excel(self) -> Path:
        """Create transit accessibility analysis Excel"""
        stations = self.load_stations()
        
        if not stations:
            print("[FAILED] No station data available")
            return None
        
        # Calculate accessibility metrics
        total_stations = len(stations)
        accessible_count = sum(1 for s in stations if s.get('wheelchair_boarding') == '1')
        
        # Create summary dataframe
        analysis_data = {
            'Metric': [
                'Total Stations',
                'Wheelchair Accessible Stations',
                'Non-Accessible Stations',
                'Accessibility Rate (%)',
                'Coverage Area (1-mile radius)',
                'Estimated Population Served'
            ],
            'Value': [
                total_stations,
                accessible_count,
                total_stations - accessible_count,
                round((accessible_count / total_stations * 100), 1) if total_stations > 0 else 0,
                f"{total_stations} sq mi (approx)",
                "Data pending"
            ],
            'Notes': [
                'All Metro-North stations in Westchester County',
                'Stations with full ADA compliance',
                'Stations requiring accessibility improvements',
                'Percentage of ADA-compliant stations',
                'Approximate walkable area (1-mile radius per station)',
                'Requires census tract overlay analysis'
            ]
        }
        
        df = pd.DataFrame(analysis_data)
        
        generator = DruckExcelGenerator()
        filepath = generator.create_excel_file(
            df,
            "westchester_transit_accessibility",
            sheet_name="Accessibility Analysis",
            add_timestamp=True
        )
        
        print(f"[SUCCESS] Created accessibility analysis Excel: {filepath}")
        return filepath


def main():
    """Run all transit processing"""
    print("="*70)
    print(" Westchester Transit - Excel Generation")
    print("="*70)
    print()
    
    processor = TransitProcessor()
    
    # Generate all Excel files
    results = []
    
    print("[1/2] Processing station data...")
    stations_file = processor.create_stations_excel()
    if stations_file:
        results.append(("Metro-North Stations", stations_file))
    
    print("\n[2/2] Processing accessibility analysis...")
    access_file = processor.create_accessibility_analysis_excel()
    if access_file:
        results.append(("Transit Accessibility", access_file))
    
    # Summary
    print("\n" + "="*70)
    print(" SUMMARY")
    print("="*70)
    for name, filepath in results:
        print(f"[SUCCESS] {name}: {filepath.name}")
    print(f"\nTotal files generated: {len(results)}")
    print("="*70)


if __name__ == "__main__":
    main()

