"""
Comprehensive Data.ny.gov Search and Download
Searches for all Westchester County datasets on data.ny.gov using Socrata API
"""

import requests
import json
from pathlib import Path
import logging
from typing import Dict, Any, List
import time

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

class DataNYGovSearcher:
    def __init__(self, data_dir: Path = Path("Projects/Westchester/Technical/data/raw/ny_state")):
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Socrata API configuration from Robin
        self.app_token = "4taH2WbrRfVE09RIthpfC0QMy"
        self.api_base = "https://data.ny.gov/api/catalog/v1"
        self.download_base = "https://data.ny.gov/resource"
        
        # Search queries
        self.search_queries = [
            "Westchester County budget",
            "Westchester municipal revenue",
            "Westchester expenditure",
            "Westchester property tax",
            "Westchester tax levy",
            "Westchester school district budget",
            "Westchester financial",
            "municipal budget New York",
            "county budget expenditures",
            "property assessment Westchester"
        ]
    
    def search_datasets(self, query: str) -> List[Dict[str, Any]]:
        """
        Search data.ny.gov catalog for datasets matching query.
        """
        logger.info(f"   [SEARCH] Querying: '{query}'")
        
        url = f"{self.api_base}"
        params = {
            'q': query,
            'only': 'datasets',
            'limit': 100
        }
        headers = {
            'X-App-Token': self.app_token
        }
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            results = data.get('results', [])
            
            logger.info(f"   [FOUND] {len(results)} datasets")
            return results
            
        except Exception as e:
            logger.error(f"   [ERROR] Search failed: {e}")
            return []
    
    def filter_westchester_datasets(self, datasets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter datasets to only include Westchester-related ones.
        """
        westchester_datasets = []
        
        for dataset in datasets:
            resource = dataset.get('resource', {})
            name = resource.get('name', '').lower()
            description = resource.get('description', '').lower()
            
            # Check if Westchester is mentioned
            if 'westchester' in name or 'westchester' in description:
                westchester_datasets.append(dataset)
                logger.info(f"      [MATCH] {resource.get('name', 'Unknown')}")
        
        return westchester_datasets
    
    def download_dataset(self, dataset_info: Dict[str, Any]) -> bool:
        """
        Download a dataset from data.ny.gov.
        """
        resource = dataset_info.get('resource', {})
        dataset_id = resource.get('id')
        name = resource.get('name', 'unknown')
        
        if not dataset_id:
            logger.warning(f"   [SKIP] No dataset ID for {name}")
            return False
        
        logger.info(f"   [DOWNLOAD] {name}")
        logger.info(f"      ID: {dataset_id}")
        
        # Try to download as JSON (limit to 50k rows for performance)
        download_url = f"{self.download_base}/{dataset_id}.json"
        params = {
            '$limit': 50000
        }
        headers = {
            'X-App-Token': self.app_token
        }
        
        try:
            response = requests.get(download_url, params=params, headers=headers, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            
            # Save as JSON
            safe_name = name.lower().replace(' ', '_').replace('/', '_')[:100]
            output_file = self.data_dir / f"{safe_name}_{dataset_id}.json"
            
            with open(output_file, 'w') as f:
                json.dump({
                    'metadata': {
                        'name': name,
                        'id': dataset_id,
                        'description': resource.get('description', ''),
                        'download_date': time.strftime("%Y-%m-%d %H:%M:%S"),
                        'source': 'data.ny.gov',
                        'record_count': len(data)
                    },
                    'data': data
                }, f, indent=2)
            
            logger.info(f"      [SUCCESS] Downloaded {len(data)} records")
            logger.info(f"      [SAVED] {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"      [ERROR] Failed to download: {e}")
            return False
    
    def comprehensive_search_and_download(self) -> Dict[str, Any]:
        """
        Search for all relevant datasets and download them.
        """
        logger.info("\n" + "="*80)
        logger.info("DATA.NY.GOV COMPREHENSIVE SEARCH")
        logger.info("="*80)
        logger.info(f"App Token: {self.app_token}")
        logger.info(f"Search Queries: {len(self.search_queries)}")
        
        all_datasets = []
        unique_dataset_ids = set()
        
        # Search with all queries
        logger.info("\n[PHASE 1] Searching data.ny.gov catalog...")
        for query in self.search_queries:
            results = self.search_datasets(query)
            
            # Filter for Westchester
            westchester_results = self.filter_westchester_datasets(results)
            
            # Add unique datasets
            for dataset in westchester_results:
                dataset_id = dataset.get('resource', {}).get('id')
                if dataset_id and dataset_id not in unique_dataset_ids:
                    all_datasets.append(dataset)
                    unique_dataset_ids.add(dataset_id)
            
            time.sleep(0.5)  # Rate limiting
        
        logger.info(f"\n[SUMMARY] Found {len(all_datasets)} unique Westchester datasets")
        
        # Download all datasets
        logger.info("\n[PHASE 2] Downloading datasets...")
        
        successful_downloads = 0
        failed_downloads = 0
        
        for i, dataset in enumerate(all_datasets, 1):
            logger.info(f"\n[{i}/{len(all_datasets)}] Processing dataset...")
            
            if self.download_dataset(dataset):
                successful_downloads += 1
            else:
                failed_downloads += 1
            
            time.sleep(1)  # Rate limiting
        
        # Create summary report
        summary = {
            'search_date': time.strftime("%Y-%m-%d %H:%M:%S"),
            'total_searches': len(self.search_queries),
            'datasets_found': len(all_datasets),
            'successful_downloads': successful_downloads,
            'failed_downloads': failed_downloads,
            'datasets': [
                {
                    'id': d.get('resource', {}).get('id'),
                    'name': d.get('resource', {}).get('name'),
                    'description': d.get('resource', {}).get('description', '')[:200]
                }
                for d in all_datasets
            ]
        }
        
        summary_file = self.data_dir / "data_ny_gov_search_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"\n[SUMMARY] Search summary saved: {summary_file}")
        
        return summary


def main():
    """Search and download all Westchester datasets from data.ny.gov"""
    
    searcher = DataNYGovSearcher()
    
    logger.info("[START] Starting comprehensive data.ny.gov search...")
    logger.info("   This will search for all Westchester County datasets")
    logger.info("   including budgets, taxes, financials, and more.")
    
    summary = searcher.comprehensive_search_and_download()
    
    logger.info("\n" + "="*80)
    logger.info("DATA.NY.GOV SEARCH COMPLETE!")
    logger.info("="*80)
    logger.info(f"[SUCCESS] Found {summary['datasets_found']} Westchester datasets")
    logger.info(f"[SUCCESS] Downloaded {summary['successful_downloads']} datasets")
    
    if summary['failed_downloads'] > 0:
        logger.warning(f"[WARNING] {summary['failed_downloads']} datasets failed to download")
    
    logger.info(f"\n[FILES] All data saved to: {searcher.data_dir}")
    logger.info("[READY] Data.ny.gov datasets ready for analysis!")


if __name__ == "__main__":
    main()

