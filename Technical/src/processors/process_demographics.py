"""
Process Demographics Data

Cleans and aggregates census data for Excel output generation.
"""

import pandas as pd
import json
from pathlib import Path
from typing import Dict, List
from excel_generator import DruckExcelGenerator


class DemographicsProcessor:
    """Process and prepare demographics data for Excel export"""
    
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            self.data_dir = Path(__file__).parent.parent.parent / "data" / "raw" / "demographics"
        else:
            self.data_dir = Path(data_dir)
    
    def load_county_data(self, year: int = 2022) -> pd.DataFrame:
        """Load county-level demographics"""
        json_path = self.data_dir / f"westchester_county_demographics_{year}.json"
        
        if not json_path.exists():
            print(f"[WARNING] County data not found: {json_path}")
            return pd.DataFrame()
        
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        # Convert single dict to DataFrame
        return pd.DataFrame([data])
    
    def load_tract_data(self, year: int = 2022) -> pd.DataFrame:
        """Load census tract-level demographics"""
        csv_path = self.data_dir / f"westchester_tracts_demographics_{year}.csv"
        
        if not csv_path.exists():
            print(f"[WARNING] Tract data not found: {csv_path}")
            return pd.DataFrame()
        
        return pd.read_csv(csv_path)
    
    def load_municipality_data(self, year: int = 2022) -> pd.DataFrame:
        """Load municipality-level demographics"""
        csv_path = self.data_dir / f"westchester_municipalities_demographics_{year}.csv"
        
        if not csv_path.exists():
            print(f"[WARNING] Municipality data not found: {csv_path}")
            return pd.DataFrame()
        
        df = pd.read_csv(csv_path)
        
        # Filter to actual Westchester municipalities (simple filtering)
        # Remove state-level or county aggregates
        df = df[~df['location_name'].str.contains('New York', case=False, na=False)]
        df = df[~df['location_name'].str.contains('County', case=False, na=False)]
        
        return df
    
    def create_county_excel(self, year: int = 2022) -> Path:
        """Create county-level demographics Excel file"""
        df = self.load_county_data(year)
        
        if df.empty:
            print("[FAILED] No county data available")
            return None
        
        # Select and rename key columns for readability
        columns_to_keep = {
            'location_name': 'Location',
            'total_population': 'Total Population',
            'male_population': 'Male Population',
            'female_population': 'Female Population',
            'median_age': 'Median Age',
            'white_alone': 'White Alone',
            'black_alone': 'Black or African American',
            'asian_alone': 'Asian Alone',
            'hispanic_or_latino': 'Hispanic or Latino',
            'total_housing_units': 'Total Housing Units',
            'occupied_housing_units': 'Occupied Housing Units',
            'median_home_value': 'Median Home Value',
            'median_gross_rent': 'Median Gross Rent',
            'median_household_income': 'Median Household Income',
            'per_capita_income': 'Per Capita Income',
            'in_labor_force': 'In Labor Force',
            'employed': 'Employed',
            'unemployed': 'Unemployed',
            'year': 'Data Year',
        }
        
        # Filter to existing columns
        available_cols = {k: v for k, v in columns_to_keep.items() if k in df.columns}
        df_clean = df[list(available_cols.keys())].rename(columns=available_cols)
        
        # Generate Excel
        generator = DruckExcelGenerator()
        filepath = generator.create_excel_file(
            df_clean,
            "westchester_county_demographics",
            sheet_name="County Demographics",
            add_timestamp=True
        )
        
        print(f"[SUCCESS] Created county demographics Excel: {filepath}")
        return filepath
    
    def create_tract_excel(self, year: int = 2022, top_n: int = None) -> Path:
        """Create census tract demographics Excel file"""
        df = self.load_tract_data(year)
        
        if df.empty:
            print("[FAILED] No tract data available")
            return None
        
        # Select key columns
        columns_to_keep = {
            'location_name': 'Census Tract',
            'tract': 'Tract Code',
            'total_population': 'Population',
            'median_household_income': 'Median Household Income',
            'median_home_value': 'Median Home Value',
            'median_age': 'Median Age',
            'total_housing_units': 'Housing Units',
        }
        
        available_cols = {k: v for k, v in columns_to_keep.items() if k in df.columns}
        df_clean = df[list(available_cols.keys())].rename(columns=available_cols)
        
        # Sort by population
        if 'Population' in df_clean.columns:
            df_clean = df_clean.sort_values('Population', ascending=False)
        
        # Limit rows if specified
        if top_n:
            df_clean = df_clean.head(top_n)
        
        generator = DruckExcelGenerator()
        filepath = generator.create_excel_file(
            df_clean,
            "westchester_census_tracts",
            sheet_name="Census Tracts",
            add_timestamp=True
        )
        
        print(f"[SUCCESS] Created tract demographics Excel: {filepath}")
        return filepath
    
    def create_municipality_excel(self, year: int = 2022) -> Path:
        """Create municipality comparison Excel file"""
        df = self.load_municipality_data(year)
        
        if df.empty:
            print("[FAILED] No municipality data available")
            return None
        
        # Select key columns
        columns_to_keep = {
            'location_name': 'Municipality',
            'total_population': 'Population',
            'median_household_income': 'Median Household Income',
            'per_capita_income': 'Per Capita Income',
            'median_home_value': 'Median Home Value',
            'median_gross_rent': 'Median Gross Rent',
            'median_age': 'Median Age',
            'total_housing_units': 'Housing Units',
            'occupied_housing_units': 'Occupied Units',
            'in_labor_force': 'Labor Force',
            'unemployed': 'Unemployed',
        }
        
        available_cols = {k: v for k, v in columns_to_keep.items() if k in df.columns}
        df_clean = df[list(available_cols.keys())].rename(columns=available_cols)
        
        # Sort by population
        if 'Population' in df_clean.columns:
            df_clean = df_clean.sort_values('Population', ascending=False)
        
        # Calculate unemployment rate if possible
        if 'Unemployed' in df_clean.columns and 'Labor Force' in df_clean.columns:
            df_clean['Unemployment Rate (%)'] = (
                df_clean['Unemployed'] / df_clean['Labor Force'] * 100
            ).round(2)
        
        generator = DruckExcelGenerator()
        filepath = generator.create_excel_file(
            df_clean,
            "westchester_municipalities",
            sheet_name="Municipalities",
            add_timestamp=True
        )
        
        print(f"[SUCCESS] Created municipality Excel: {filepath}")
        return filepath


def main():
    """Run all demographics processing"""
    print("="*70)
    print(" Westchester Demographics - Excel Generation")
    print("="*70)
    print()
    
    processor = DemographicsProcessor()
    
    # Generate all Excel files
    results = []
    
    print("[1/3] Processing county-level data...")
    county_file = processor.create_county_excel(2022)
    if county_file:
        results.append(("County Demographics", county_file))
    
    print("\n[2/3] Processing census tract data...")
    tract_file = processor.create_tract_excel(2022)
    if tract_file:
        results.append(("Census Tracts", tract_file))
    
    print("\n[3/3] Processing municipality data...")
    muni_file = processor.create_municipality_excel(2022)
    if muni_file:
        results.append(("Municipalities", muni_file))
    
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

