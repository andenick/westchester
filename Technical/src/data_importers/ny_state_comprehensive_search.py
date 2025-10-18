"""
Comprehensive NY State Open Data Search for Westchester County
Searches ALL available NY State datasets for Westchester-specific data

This advanced client searches the complete NY State Open Data portal
for any dataset containing Westchester County data.
"""

import requests
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import re


class NYStateComprehensiveSearch:
    """Comprehensive NY State Open Data portal searcher"""

    def __init__(self, api_token: str = None, output_dir: Path = None):
        """
        Initialize NY State Open Data searcher

        Args:
            api_token: Socrata app token for API access
            output_dir: Directory to save downloaded data
        """
        self.api_token = api_token
        self.base_url = "https://data.ny.gov/resource"

        if output_dir is None:
            base_path = Path(__file__).parent.parent.parent / "data" / "raw" / "ny_state_comprehensive"
        else:
            base_path = Path(output_dir)

        self.output_dir = base_path
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Westchester County keywords and variations
        self.westchester_keywords = [
            "Westchester", "westchester", "WESTCHESTER",
            "Westchester County", "westchester county", "WESTCHESTER COUNTY",
            "Westchester Co", "westchester co", "WESTCHESTER CO",
            "Yonkers", "yonkers", "YONKERS",  # Largest city
            "White Plains", "white plains", "WHITE PLAINS",  # County seat
            "New Rochelle", "new rochelle", "NEW ROCHELLE",
            "Mount Vernon", "mount vernon", "MOUNT VERNON",
            "Scarsdale", "scarsdale", "SCARSDALE",
            "Rye", "rye", "RYE",
            "Port Chester", "port chester", "PORT CHESTER",
            "Greenburgh", "greenburgh", "GREENBURGH",
            "Mamaroneck", "mamaroneck", "MAMARONECK",
            "Harrison", "harrison", "HARRISON",
            "Bedford", "bedford", "BEDFORD",
            "Ossining", "ossining", "OSSINING",
            "Peekskill", "peekskill", "PEEKSILL",
            "Cortlandt", "cortlandt", "CORTLANDT",
            "Yorktown", "yorktown", "YORKTOWN",
            "Somers", "somers", "SOMERS",
            "Mount Pleasant", "mount pleasant", "MOUNT PLEASANT",
            "New Castle", "new castle", "NEW CASTLE",
            "North Castle", "north castle", "NORTH CASTLE",
            "Lewisboro", "lewisboro", "LEWISBORO",
            "North Salem", "north salem", "NORTH SALEM",
            "Pound Ridge", "pound ridge", "POUND RIDGE",
            "Bronxville", "bronxville", "BRONXVILLE",
            "Tarrytown", "tarrytown", "TARRYTOWN",
            "Sleepy Hollow", "sleepy hollow", "SLEEPY HOLLOW",
            "Irvington", "irvington", "IRVINGTON",
            "Dobbs Ferry", "dobbs ferry", "DOBBS FERRY",
            "Hastings-on-Hudson", "hastings-on-hudson", "HASTINGS-ON-HUDSON",
            "Ardsley", "ardsley", "ARDSLEY",
            "Elmsford", "elmsford", "ELMSFORD",
            "Tuckahoe", "tuckahoe", "TUCKAHOE",
            "Pelham", "pelham", "PELHAM",
            "Larchmont", "larchmont", "LARCHMONT",
            "Rye Brook", "rye brook", "RYE BROOK",
            "Briarcliff Manor", "briarcliff manor", "BRIARCLIFF MANOR",
            "Croton-on-Hudson", "croton-on-hudson", "CROTON-ON-HUDSON",
            "Buchanan", "buchanan", "BUCHANAN"
        ]

        # FIPS codes for Westchester
        self.fips_codes = ["36119", "36-119"]  # State-County FIPS

        # Known NY State datasets for Westchester
        self.known_datasets = {
            "crime_statistics": {
                "endpoint": "ca8h-8gjq.json",
                "name": "Index Crimes by County",
                "description": "Annual crime statistics by county"
            },
            "health_facilities": {
                "endpoint": "vn5v-hh5r.json",
                "name": "Health Facility General Information",
                "description": "Licensed healthcare facilities"
            },
            "school_data": {
                "endpoint": "t4dw-s39s.json",
                "name": "School District Data",
                "description": "NY State school district information"
            },
            "municipal_finances": {
                "endpoint": "c6z4-3b9z.json",
                "name": "Annual Financial Data",
                "description": "Municipal financial information"
            },
            "elections": {
                "endpoint": "iisn-hrva.json",
                "name": "Election Results",
                "description": "NY State election data"
            },
            "environmental": {
                "endpoint": "i77j-ijqk.json",
                "name": "Environmental Facilities",
                "description": "Environmental monitoring sites"
            },
            "transportation": {
                "endpoint": "e9qj-95h8.json",
                "name": "Transportation Data",
                "description": "NY State transportation statistics"
            },
            "housing": {
                "endpoint": "c7y7-x8i9.json",
                "name": "Housing and Development",
                "description": "NY State housing data"
            },
            "business": {
                "endpoint": "786n-wkjj.json",
                "name": "Business and Employment",
                "description": "NY State business statistics"
            },
            "public_safety": {
                "endpoint": "jz6i-i4kg.json",
                "name": "Public Safety",
                "description": "NY State public safety data"
            }
        }

        # Search categories
        self.search_categories = [
            "demographics", "economics", "housing", "transportation",
            "education", "health", "public_safety", "environment",
            "government", "business", "infrastructure", "social_services"
        ]

        # Rate limiting
        self.request_delay = 1.0  # 1 second between requests
        self.last_request_time = 0

    def _rate_limit(self):
        """Implement rate limiting to respect API limits"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.request_delay:
            sleep_time = self.request_delay - time_since_last
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def search_datasets_by_keyword(self, keyword: str, limit: int = 100) -> List[Dict]:
        """
        Search NY State Open Data for datasets containing a specific keyword

        Args:
            keyword: Search keyword
            limit: Maximum number of results

        Returns:
            List of dataset metadata
        """
        self._rate_limit()

        # Socrata API for dataset search
        search_url = "https://data.ny.gov/api/catalog/v1"
        params = {
            "q": keyword,
            "limit": limit,
            "domains": "data.ny.gov"
        }

        headers = {}
        if self.api_token:
            headers["X-App-Token"] = self.api_token

        try:
            response = requests.get(search_url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()

            return data.get("results", [])

        except Exception as e:
            print(f"[ERROR] Failed to search for '{keyword}': {e}")
            return []

    def search_all_westchester_datasets(self) -> Dict[str, List[Dict]]:
        """
        Search for all datasets mentioning Westchester County

        Returns:
            Dictionary of search results by keyword
        """
        print("Starting comprehensive Westchester County dataset search...")
        print(f"Searching with {len(self.westchester_keywords)} Westchester keywords...")
        print(f"Searching {len(self.search_categories)} data categories...")
        print("=" * 80)

        all_results = {}
        found_datasets = set()

        # First, search by Westchester keywords
        print("\n[PHASE 1] Searching by Westchester keywords...")
        for keyword in self.westchester_keywords[:10]:  # Limit to top 10 for performance
            print(f"   Searching for: '{keyword}'...")
            results = self.search_datasets_by_keyword(keyword, limit=50)

            if results:
                all_results[keyword] = results
                print(f"     Found {len(results)} datasets")

                # Track unique datasets
                for result in results:
                    dataset_id = result.get("resource", {}).get("id", "")
                    if dataset_id:
                        found_datasets.add(dataset_id)
            else:
                print(f"     No results found")

            time.sleep(0.5)  # Brief pause between searches

        print(f"\n[SUMMARY] Found {len(found_datasets)} unique datasets mentioning Westchester")

        # Second, search by data categories with Westchester filter
        print("\n[PHASE 2] Searching by data categories...")
        category_results = {}

        for category in self.search_categories:
            print(f"   Searching {category} data...")
            search_term = f"Westchester {category}"
            results = self.search_datasets_by_keyword(search_term, limit=30)

            if results:
                category_results[category] = results
                print(f"     Found {len(results)} {category} datasets")
            else:
                print(f"     No {category} datasets found")

            time.sleep(0.5)

        # Combine results
        all_results.update(category_results)

        # Save search metadata
        search_metadata = {
            "search_timestamp": datetime.now().isoformat(),
            "westchester_keywords_used": len(self.westchester_keywords),
            "categories_searched": len(self.search_categories),
            "total_datasets_found": len(found_datasets),
            "results_by_keyword": {k: len(v) for k, v in all_results.items()},
            "unique_dataset_ids": list(found_datasets)
        }

        metadata_file = self.output_dir / f"search_metadata_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(metadata_file, 'w') as f:
            json.dump(search_metadata, f, indent=2)

        print(f"\n[SAVED] Search metadata saved to: {metadata_file}")

        return all_results

    def download_dataset_data(self, dataset_info: Dict) -> Optional[Dict]:
        """
        Download actual data from a NY State dataset

        Args:
            dataset_info: Dataset metadata

        Returns:
            Downloaded data or None if failed
        """
        try:
            # Extract dataset identifier
            resource = dataset_info.get("resource", {})
            dataset_id = resource.get("id", "")
            dataset_name = resource.get("name", "Unknown")

            if not dataset_id:
                print(f"[WARNING] No dataset ID found for: {dataset_name}")
                return None

            # Construct data URL
            data_url = f"https://data.ny.gov/resource/{dataset_id}.json"

            # Add Westchester County filter if possible
            params = {}
            if self.api_token:
                params["$limit"] = 50000  # Large limit for comprehensive data

            headers = {}
            if self.api_token:
                headers["X-App-Token"] = self.api_token

            print(f"   Downloading: {dataset_name}...")
            print(f"   URL: {data_url}")

            response = requests.get(data_url, params=params, headers=headers, timeout=120)
            response.raise_for_status()

            data = response.json()

            # Filter for Westchester County data if county field exists
            if isinstance(data, list) and data:
                filtered_data = self._filter_westchester_data(data)
                print(f"   Original records: {len(data)}, Westchester records: {len(filtered_data)}")
                return filtered_data
            else:
                print(f"   Downloaded {len(data) if isinstance(data, list) else 'single'} records")
                return data

        except Exception as e:
            print(f"[ERROR] Failed to download dataset {dataset_name}: {e}")
            return None

    def _filter_westchester_data(self, data: List[Dict]) -> List[Dict]:
        """
        Filter data to include only Westchester County records

        Args:
            data: List of data records

        Returns:
            Filtered data for Westchester County
        """
        westchester_data = []

        for record in data:
            # Check various fields that might contain county information
            county_fields = ["county", "County", "COUNTY", "county_name", "municipality", "location"]

            is_westchester = False

            # Check county fields
            for field in county_fields:
                if field in record:
                    county_value = str(record[field]).lower()
                    if any(keyword.lower() in county_value for keyword in self.westchester_keywords[:10]):
                        is_westchester = True
                        break

            # Check FIPS codes
            fips_fields = ["fips", "FIPS", "county_fips", "geoid", "geoid2"]
            for field in fips_fields:
                if field in record and str(record[field]) in self.fips_codes:
                    is_westchester = True
                    break

            # Check name fields for Westchester municipalities
            name_fields = ["name", "Name", "municipality", "city", "town", "village", "location"]
            for field in name_fields:
                if field in record:
                    name_value = str(record[field]).lower()
                    if any(keyword.lower() in name_value for keyword in self.westchester_keywords):
                        is_westchester = True
                        break

            if is_westchester:
                westchester_data.append(record)

        return westchester_data

    def download_known_datasets(self) -> Dict[str, Dict]:
        """
        Download data from known NY State datasets for Westchester

        Returns:
            Dictionary of downloaded datasets
        """
        print("\n[PHASE 3] Downloading known NY State datasets...")
        print("This includes crime statistics, health facilities, and other key datasets.")
        print("=" * 60)

        downloaded_data = {}

        for dataset_key, dataset_info in self.known_datasets.items():
            print(f"\n[DOWNLOADING] {dataset_info['name']}...")

            # Add metadata to dataset info
            enhanced_info = {
                **dataset_info,
                "dataset_key": dataset_key,
                "download_timestamp": datetime.now().isoformat()
            }

            # Download the data
            data = self.download_dataset_data(enhanced_info)

            if data:
                # Save the data
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{timestamp}_{dataset_key}_westchester.json"
                filepath = self.output_dir / filename

                with open(filepath, 'w') as f:
                    json.dump(data, f, indent=2)

                # Create metadata file
                metadata = {
                    "dataset_key": dataset_key,
                    "dataset_name": dataset_info["name"],
                    "dataset_description": dataset_info["description"],
                    "download_timestamp": datetime.now().isoformat(),
                    "record_count": len(data) if isinstance(data, list) else 1,
                    "data_file": filename,
                    "source": "NY State Open Data Portal",
                    "api_endpoint": dataset_info["endpoint"]
                }

                metadata_filename = f"{timestamp}_{dataset_key}_metadata.json"
                metadata_filepath = self.output_dir / metadata_filename

                with open(metadata_filepath, 'w') as f:
                    json.dump(metadata, f, indent=2)

                downloaded_data[dataset_key] = {
                    "data": data,
                    "metadata": metadata,
                    "filepath": str(filepath),
                    "metadata_filepath": str(metadata_filepath)
                }

                print(f"   [SUCCESS] {dataset_key}: {len(data) if isinstance(data, list) else 1} records saved")
            else:
                print(f"   [FAILED] {dataset_key}: No data downloaded")

            time.sleep(1)  # Rate limiting between downloads

        return downloaded_data

    def download_discovered_datasets(self, search_results: Dict[str, List[Dict]], max_datasets: int = 20) -> Dict[str, Dict]:
        """
        Download data from discovered datasets

        Args:
            search_results: Results from search_datasets_by_keyword
            max_datasets: Maximum number of datasets to download

        Returns:
            Dictionary of downloaded datasets
        """
        print(f"\n[PHASE 4] Downloading discovered datasets (max {max_datasets})...")

        # Flatten search results and remove duplicates
        all_datasets = []
        seen_ids = set()

        for keyword, datasets in search_results.items():
            for dataset in datasets:
                dataset_id = dataset.get("resource", {}).get("id", "")
                if dataset_id and dataset_id not in seen_ids:
                    all_datasets.append((keyword, dataset))
                    seen_ids.add(dataset_id)

        # Sort by relevance (simple heuristic - prioritize those with Westchester in name)
        def relevance_score(item):
            keyword, dataset = item
            name = dataset.get("resource", {}).get("name", "").lower()
            description = dataset.get("resource", {}).get("description", "").lower()

            score = 0
            if "westchester" in name:
                score += 10
            if "westchester" in description:
                score += 5
            if any(city in name for city in ["yonkers", "white plains", "new rochelle"]):
                score += 8

            return score

        all_datasets.sort(key=relevance_score, reverse=True)
        all_datasets = all_datasets[:max_datasets]

        downloaded_data = {}

        for i, (keyword, dataset) in enumerate(all_datasets):
            print(f"\n[{i+1}/{len(all_datasets)}] Downloading from '{keyword}' search...")
            print(f"   Dataset: {dataset.get('resource', {}).get('name', 'Unknown')}")

            # Download the data
            data = self.download_dataset_data(dataset)

            if data:
                # Save the data
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', dataset.get("resource", {}).get("name", "dataset"))[:50]
                filename = f"{timestamp}_discovered_{safe_name}.json"
                filepath = self.output_dir / filename

                with open(filepath, 'w') as f:
                    json.dump(data, f, indent=2)

                # Create metadata
                metadata = {
                    "search_keyword": keyword,
                    "dataset_name": dataset.get("resource", {}).get("name", "Unknown"),
                    "dataset_description": dataset.get("resource", {}).get("description", ""),
                    "download_timestamp": datetime.now().isoformat(),
                    "record_count": len(data) if isinstance(data, list) else 1,
                    "data_file": filename,
                    "source": "NY State Open Data Portal",
                    "original_endpoint": dataset.get("resource", {}).get("id", "")
                }

                metadata_filename = f"{timestamp}_discovered_{safe_name}_metadata.json"
                metadata_filepath = self.output_dir / metadata_filename

                with open(metadata_filepath, 'w') as f:
                    json.dump(metadata, f, indent=2)

                downloaded_data[safe_name] = {
                    "data": data,
                    "metadata": metadata,
                    "filepath": str(filepath),
                    "metadata_filepath": str(metadata_filepath)
                }

                print(f"   [SUCCESS] {len(data) if isinstance(data, list) else 1} records saved")
            else:
                print(f"   [FAILED] No data downloaded")

            time.sleep(1)  # Rate limiting

        return downloaded_data

    def create_comprehensive_summary(self, known_data: Dict, discovered_data: Dict) -> Dict:
        """Create comprehensive summary of all downloaded data"""
        summary = {
            "generation_timestamp": datetime.now().isoformat(),
            "data_source": "NY State Open Data Portal",
            "total_datasets_downloaded": len(known_data) + len(discovered_data),
            "known_datasets": {
                "count": len(known_data),
                "dataset_keys": list(known_data.keys())
            },
            "discovered_datasets": {
                "count": len(discovered_data),
                "dataset_names": list(discovered_data.keys())
            },
            "total_records": 0,
            "data_categories": {},
            "file_locations": {
                "data_directory": str(self.output_dir),
                "metadata_directory": str(self.output_dir)
            }
        }

        # Count total records and categorize
        all_data = {**known_data, **discovered_data}
        total_records = 0

        for dataset_key, dataset_info in all_data.items():
            metadata = dataset_info.get("metadata", {})
            record_count = metadata.get("record_count", 0)
            total_records += record_count

            # Extract category from dataset metadata
            dataset_name = metadata.get("dataset_name", "").lower()
            if "crime" in dataset_name:
                category = "crime_statistics"
            elif "health" in dataset_name or "medical" in dataset_name:
                category = "health"
            elif "school" in dataset_name or "education" in dataset_name:
                category = "education"
            elif "financial" in dataset_name or "budget" in dataset_name or "tax" in dataset_name:
                category = "finance"
            elif "environmental" in dataset_name:
                category = "environment"
            elif "transportation" in dataset_name:
                category = "transportation"
            elif "housing" in dataset_name:
                category = "housing"
            elif "business" in dataset_name or "employment" in dataset_name:
                category = "business"
            else:
                category = "other"

            if category not in summary["data_categories"]:
                summary["data_categories"][category] = {"count": 0, "datasets": []}

            summary["data_categories"][category]["count"] += 1
            summary["data_categories"][category]["datasets"].append(dataset_key)

        summary["total_records"] = total_records

        # Save summary
        summary_filename = f"comprehensive_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        summary_filepath = self.output_dir / summary_filename

        with open(summary_filepath, 'w') as f:
            json.dump(summary, f, indent=2)

        print(f"\n[SAVED] Comprehensive summary saved to: {summary_filepath}")

        return summary

    def run_comprehensive_search(self, max_discovered_datasets: int = 20) -> Tuple[bool, Dict]:
        """
        Run the complete comprehensive search process

        Args:
            max_discovered_datasets: Maximum number of discovered datasets to download

        Returns:
            Tuple of (success: bool, summary: dict)
        """
        try:
            print("=" * 80)
            print("COMPREHENSIVE NY STATE OPEN DATA SEARCH - WESTCHESTER COUNTY")
            print("=" * 80)
            print(f"API Token: {'Present' if self.api_token else 'Not present'}")
            print(f"Output Directory: {self.output_dir}")
            print(f"Max Discovered Datasets: {max_discovered_datasets}")
            print()

            # Phase 1: Search for datasets
            search_results = self.search_all_westchester_datasets()

            # Phase 2: Download known datasets
            known_data = self.download_known_datasets()

            # Phase 3: Download discovered datasets
            discovered_data = self.download_discovered_datasets(search_results, max_discovered_datasets)

            # Phase 4: Create comprehensive summary
            summary = self.create_comprehensive_summary(known_data, discovered_data)

            print("\n" + "=" * 80)
            print("COMPREHENSIVE SEARCH COMPLETE!")
            print("=" * 80)
            print(f"Known datasets downloaded: {len(known_data)}")
            print(f"Discovered datasets downloaded: {len(discovered_data)}")
            print(f"Total datasets: {len(known_data) + len(discovered_data)}")
            print(f"Total records: {summary.get('total_records', 0)}")
            print(f"Data categories: {list(summary.get('data_categories', {}).keys())}")
            print(f"All data saved to: {self.output_dir}")

            return True, summary

        except Exception as e:
            error_msg = f"Comprehensive search failed: {str(e)}"
            print(f"\n[ERROR] {error_msg}")
            return False, {"error": error_msg}


def main():
    """Command-line interface for comprehensive NY State data search"""
    import os

    print("=" * 80)
    print("COMPREHENSIVE NY STATE OPEN DATA SEARCH - WESTCHESTER COUNTY")
    print("Searches ALL available NY State datasets for Westchester-specific data")
    print("=" * 80)
    print()

    # Check for API token
    api_token = os.getenv('NY_STATE_API_TOKEN')

    if not api_token:
        print("No NY_STATE_API_TOKEN environment variable found.")
        print("Search will proceed without API token (rate limits may apply).")
        print()
        response = input("Enter your NY State Open Data API token (or press Enter to skip): ").strip()
        if response:
            api_token = response

    # Get max discovered datasets
    max_input = input("Maximum discovered datasets to download (default 20): ").strip()
    try:
        max_datasets = int(max_input) if max_input else 20
        if max_datasets < 1:
            print("Invalid input. Using default 20.")
            max_datasets = 20
    except ValueError:
        print("Invalid input. Using default 20.")
        max_datasets = 20

    searcher = NYStateComprehensiveSearch(api_token=api_token)
    success, summary = searcher.run_comprehensive_search(max_datasets)

    print()
    if success:
        print("[SUCCESS] Comprehensive search completed successfully!")
        print(f"Downloaded {summary.get('total_datasets_downloaded', 0)} datasets")
        print(f"Total records: {summary.get('total_records', 0)}")
        print(f"Data saved to: {searcher.output_dir}")
    else:
        print("[FAILED] Comprehensive search failed!")
        print(f"Error: {summary.get('error', 'Unknown error')}")


if __name__ == "__main__":
    main()