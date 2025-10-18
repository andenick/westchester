"""
NY State Comptroller Municipal Financial Data Importer
Downloads real financial data for Westchester County municipalities
"""

import requests
import json
import csv
from pathlib import Path
import logging
from typing import Dict, Any, List
import time
import io

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

class NYComptrollerFinancialImporter:
    def __init__(self, data_dir: Path = Path("Projects/Westchester/Technical/data/raw/budget")):
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # NY State Comptroller base URLs
        self.base_url = "https://www.osc.state.ny.us/files/local-government/csv"
        
        # Westchester County code
        self.county_code = "60"  # Westchester
        
        # Available years for municipal profiles
        self.available_years = list(range(2015, 2023))  # 2015-2022
        
    def download_municipal_profiles(self, year: int) -> Dict[str, Any]:
        """
        Download municipal financial profiles for a specific year.
        """
        logger.info(f"   [YEAR] Downloading {year} municipal profiles...")
        
        url = f"{self.base_url}/municipal-profiles-{year}.csv"
        
        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            
            # Parse CSV
            csv_text = response.text
            csv_reader = csv.DictReader(io.StringIO(csv_text))
            
            all_records = list(csv_reader)
            logger.info(f"      [TOTAL] Downloaded {len(all_records)} municipal records")
            
            # Filter for Westchester County
            westchester_records = [
                record for record in all_records
                if record.get('County Code', '') == self.county_code
                or record.get('County Name', '').lower() == 'westchester'
            ]
            
            logger.info(f"      [WESTCHESTER] Found {len(westchester_records)} Westchester municipalities")
            
            if len(westchester_records) > 0:
                # Save raw CSV data
                csv_file = self.data_dir / f"westchester_municipal_profiles_{year}.csv"
                with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                    if westchester_records:
                        writer = csv.DictWriter(f, fieldnames=westchester_records[0].keys())
                        writer.writeheader()
                        writer.writerows(westchester_records)
                
                # Convert to structured JSON
                structured_data = self._structure_financial_data(westchester_records, year)
                
                # Save JSON
                json_file = self.data_dir / f"westchester_municipal_financials_{year}.json"
                with open(json_file, 'w') as f:
                    json.dump(structured_data, f, indent=2)
                
                logger.info(f"      [SUCCESS] Saved {year} data")
                return structured_data
            else:
                logger.warning(f"      [WARNING] No Westchester data found for {year}")
                return None
                
        except Exception as e:
            logger.error(f"      [ERROR] Failed to download {year}: {e}")
            return None
    
    def _structure_financial_data(self, records: List[Dict[str, Any]], year: int) -> Dict[str, Any]:
        """
        Structure raw CSV data into organized JSON format.
        """
        municipalities = []
        
        for record in records:
            # Extract key financial metrics
            muni_data = {
                'municipality_name': record.get('Municipality Name', ''),
                'municipality_type': record.get('Type of Government', ''),
                'county': 'Westchester',
                'year': year,
                'financials': {
                    'total_revenues': self._safe_float(record.get('Total Revenues', 0)),
                    'total_expenditures': self._safe_float(record.get('Total Expenditures', 0)),
                    'total_debt': self._safe_float(record.get('Total Debt', 0)),
                    'fund_balance': self._safe_float(record.get('Fund Balance', 0)),
                    'property_tax_levy': self._safe_float(record.get('Property Tax Levy', 0)),
                }
            }
            
            # Add expenditure breakdown if available
            expenditure_categories = {
                'general_government': record.get('General Government Support', 0),
                'public_safety': record.get('Public Safety', 0),
                'health': record.get('Health', 0),
                'transportation': record.get('Transportation', 0),
                'economic_development': record.get('Economic Assistance and Opportunity', 0),
                'culture_recreation': record.get('Culture and Recreation', 0),
                'home_community': record.get('Home and Community Services', 0),
                'employee_benefits': record.get('Employee Benefits', 0),
                'debt_service': record.get('Debt Service', 0)
            }
            
            muni_data['expenditures_by_category'] = {
                k: self._safe_float(v) for k, v in expenditure_categories.items()
            }
            
            municipalities.append(muni_data)
        
        # Calculate county-wide totals
        county_totals = {
            'total_revenues': sum(m['financials']['total_revenues'] for m in municipalities),
            'total_expenditures': sum(m['financials']['total_expenditures'] for m in municipalities),
            'total_debt': sum(m['financials']['total_debt'] for m in municipalities),
            'municipality_count': len(municipalities)
        }
        
        return {
            'metadata': {
                'year': year,
                'county': 'Westchester County, NY',
                'source': 'NY State Comptroller Office',
                'download_date': time.strftime("%Y-%m-%d %H:%M:%S"),
                'municipality_count': len(municipalities)
            },
            'county_totals': county_totals,
            'municipalities': municipalities
        }
    
    def _safe_float(self, value: Any) -> float:
        """Convert string/numeric value to float, handling errors."""
        if value is None or value == '':
            return 0.0
        
        try:
            # Remove commas and dollar signs
            if isinstance(value, str):
                value = value.replace(',', '').replace('$', '').strip()
            return float(value)
        except (ValueError, TypeError):
            return 0.0
    
    def download_all_years(self) -> Dict[str, Any]:
        """
        Download municipal financial data for all available years.
        """
        logger.info("\n" + "="*80)
        logger.info("NY STATE COMPTROLLER MUNICIPAL FINANCIAL DATA DOWNLOAD")
        logger.info("="*80)
        logger.info(f"Years: {self.available_years[0]}-{self.available_years[-1]}")
        
        all_year_data = {}
        successful_years = []
        
        for year in self.available_years:
            logger.info(f"\n[{year}] Processing...")
            
            data = self.download_municipal_profiles(year)
            
            if data:
                all_year_data[str(year)] = data
                successful_years.append(year)
            
            time.sleep(1)  # Rate limiting
        
        # Create time series data
        logger.info("\n[TIME SERIES] Creating historical trends...")
        time_series = self._create_time_series(all_year_data)
        
        # Save time series
        time_series_file = self.data_dir / "westchester_budget_time_series.json"
        with open(time_series_file, 'w') as f:
            json.dump(time_series, f, indent=2)
        
        logger.info(f"   [SAVED] Time series data: {time_series_file}")
        
        return {
            'summary': {
                'years_downloaded': successful_years,
                'total_years': len(successful_years)
            },
            'time_series': time_series
        }
    
    def _create_time_series(self, all_year_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create time series from multiple years of data.
        """
        years = sorted([int(y) for y in all_year_data.keys()])
        
        county_time_series = []
        for year in years:
            year_data = all_year_data[str(year)]
            county_time_series.append({
                'year': year,
                'total_revenues': year_data['county_totals']['total_revenues'],
                'total_expenditures': year_data['county_totals']['total_expenditures'],
                'total_debt': year_data['county_totals']['total_debt'],
                'municipality_count': year_data['county_totals']['municipality_count']
            })
        
        # Extract planning/development spending if available
        planning_time_series = []
        for year in years:
            year_data = all_year_data[str(year)]
            municipalities = year_data.get('municipalities', [])
            
            # Sum planning/development spending across municipalities
            total_economic_dev = sum(
                m.get('expenditures_by_category', {}).get('economic_development', 0)
                for m in municipalities
            )
            
            planning_time_series.append({
                'year': year,
                'economic_development_spending': total_economic_dev
            })
        
        return {
            'metadata': {
                'created': time.strftime("%Y-%m-%d %H:%M:%S"),
                'years_included': years,
                'source': 'NY State Comptroller'
            },
            'county_totals_time_series': county_time_series,
            'planning_development_time_series': planning_time_series
        }


def main():
    """Download municipal financial data from NY State Comptroller"""
    
    importer = NYComptrollerFinancialImporter()
    
    logger.info("[START] Downloading NY State Comptroller financial data...")
    logger.info("   This will download real municipal budget data")
    logger.info("   for all Westchester County municipalities.")
    
    results = importer.download_all_years()
    
    logger.info("\n" + "="*80)
    logger.info("NY STATE COMPTROLLER DOWNLOAD COMPLETE!")
    logger.info("="*80)
    logger.info(f"[SUCCESS] Downloaded {results['summary']['total_years']} years of data")
    logger.info(f"[SUCCESS] Years: {results['summary']['years_downloaded']}")
    logger.info(f"\n[FILES] All data saved to: {importer.data_dir}")
    logger.info("[READY] Real budget data ready for use!")


if __name__ == "__main__":
    main()

