"""
Parse Westchester County Tax Parcels Data
Extracts real property tax statistics from existing GIS data
"""

import json
import csv
from pathlib import Path
import logging
from typing import Dict, Any, List
from collections import defaultdict

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

class TaxParcelParser:
    def __init__(self):
        # Use path relative to this script's location
        script_dir = Path(__file__).parent
        self.data_dir = script_dir.parent.parent / "data" / "raw"
        self.tax_parcels_csv = self.data_dir / "WCGIS.tax-parcels.csv"
        self.output_dir = self.data_dir / "tax"
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def parse_tax_parcels(self) -> Dict[str, Any]:
        """
        Parse tax parcels CSV to extract real assessment and tax data.
        """
        logger.info("\n" + "="*80)
        logger.info("PARSING WESTCHESTER COUNTY TAX PARCELS")
        logger.info("="*80)
        
        if not self.tax_parcels_csv.exists():
            logger.error(f"[ERROR] Tax parcels file not found: {self.tax_parcels_csv}")
            return None
        
        logger.info(f"[FILE] Reading: {self.tax_parcels_csv}")
        
        try:
            with open(self.tax_parcels_csv, 'r', encoding='utf-8', errors='ignore') as f:
                reader = csv.DictReader(f)
                parcels = list(reader)
            
            logger.info(f"[SUCCESS] Loaded {len(parcels):,} parcels")
            
            # Group parcels by municipality
            parcels_by_muni = defaultdict(list)
            
            for parcel in parcels:
                # Try to extract municipality name from various possible fields
                municipality = (
                    parcel.get('MUNICIPALITY') or 
                    parcel.get('CITY') or 
                    parcel.get('TOWN') or 
                    parcel.get('VILLAGE') or
                    'Unknown'
                )
                
                # Extract assessment value
                assessment_str = parcel.get('TOTAL_AV') or parcel.get('ASSESSMENT') or '0'
                try:
                    assessment = float(assessment_str.replace(',', '').replace('$', ''))
                except:
                    assessment = 0
                
                if assessment > 0:
                    parcels_by_muni[municipality].append({
                        'assessment': assessment,
                        'parcel_id': parcel.get('PARCEL_ID') or parcel.get('ID'),
                        'property_class': parcel.get('PROP_CLASS') or parcel.get('CLASS')
                    })
            
            logger.info(f"[ANALYSIS] Found {len(parcels_by_muni)} municipalities")
            
            # Calculate statistics by municipality
            municipality_stats = []
            
            for municipality, parcel_list in parcels_by_muni.items():
                if len(parcel_list) == 0:
                    continue
                
                assessments = [p['assessment'] for p in parcel_list]
                
                stats = {
                    'municipality': municipality,
                    'total_parcels': len(parcel_list),
                    'average_assessment': sum(assessments) / len(assessments),
                    'median_assessment': sorted(assessments)[len(assessments) // 2],
                    'min_assessment': min(assessments),
                    'max_assessment': max(assessments),
                    'total_assessed_value': sum(assessments)
                }
                
                municipality_stats.append(stats)
                
                logger.info(f"   [{municipality}] {len(parcel_list):,} parcels, avg ${stats['average_assessment']:,.0f}")
            
            # Sort by parcel count
            municipality_stats.sort(key=lambda x: x['total_parcels'], reverse=True)
            
            # Create overall statistics
            overall_stats = {
                'total_parcels': sum(m['total_parcels'] for m in municipality_stats),
                'total_assessed_value': sum(m['total_assessed_value'] for m in municipality_stats),
                'average_assessment_county': sum(
                    m['total_assessed_value'] for m in municipality_stats
                ) / sum(m['total_parcels'] for m in municipality_stats),
                'municipality_count': len(municipality_stats)
            }
            
            # Compile final dataset
            tax_data = {
                'metadata': {
                    'source': 'Westchester County GIS',
                    'dataset': 'Tax Parcels',
                    'parsed_date': json.dumps(defaultdict(str)),  # Will be replaced with actual date
                    'total_parcels': overall_stats['total_parcels']
                },
                'overall_statistics': overall_stats,
                'by_municipality': municipality_stats
            }
            
            # Save JSON
            output_file = self.output_dir / "westchester_property_tax_analysis.json"
            with open(output_file, 'w') as f:
                json.dump(tax_data, f, indent=2)
            
            logger.info(f"\n[SUCCESS] Tax analysis saved: {output_file}")
            logger.info(f"[SUMMARY] {overall_stats['total_parcels']:,} total parcels")
            logger.info(f"[SUMMARY] ${overall_stats['average_assessment_county']:,.0f} average assessment")
            
            return tax_data
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to parse tax parcels: {e}")
            return None


def main():
    """Parse tax parcels data"""
    
    parser = TaxParcelParser()
    
    logger.info("[START] Parsing Westchester County tax parcels...")
    logger.info("   This will extract real property tax statistics")
    logger.info("   from the existing GIS tax parcel dataset.")
    
    tax_data = parser.parse_tax_parcels()
    
    if tax_data:
        logger.info("\n" + "="*80)
        logger.info("TAX PARCEL PARSING COMPLETE!")
        logger.info("="*80)
        logger.info("[READY] Real property tax data ready for use!")
    else:
        logger.error("\n[FAILED] Could not parse tax parcels")


if __name__ == "__main__":
    main()

