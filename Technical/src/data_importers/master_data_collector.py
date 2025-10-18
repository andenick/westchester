"""
Master Data Collection Orchestrator for Westchester County
Coordinates all data collection systems for comprehensive municipal data gathering

This master orchestrator runs all data collectors in the optimal order,
manages dependencies, and provides a unified interface for complete data collection.
"""

import json
import time
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import traceback


class MasterDataCollector:
    """Master orchestrator for all Westchester data collection systems"""

    def __init__(self, base_dir: Path = None):
        """
        Initialize master data collector

        Args:
            base_dir: Base directory for all data operations
        """
        if base_dir is None:
            base_dir = Path(__file__).parent.parent.parent

        self.base_dir = base_dir
        self.data_dir = base_dir / "data"
        self.raw_dir = self.data_dir / "raw"
        self.processed_dir = self.data_dir / "processed"

        # Create directories
        for directory in [self.data_dir, self.raw_dir, self.processed_dir]:
            directory.mkdir(parents=True, exist_ok=True)

        # Import all collector modules
        self.collectors = {}
        self._import_collectors()

        # Collection phases in optimal order
        self.collection_phases = [
            {
                "name": "Census Data Collection",
                "description": "Comprehensive demographics and social data",
                "collectors": ["comprehensive_census"],
                "priority": 1,
                "estimated_time": "5-10 minutes",
                "dependencies": [],
                "data_types": ["demographics", "economics", "housing", "education", "transportation"]
            },
            {
                "name": "OpenStreetMap Infrastructure",
                "description": "Comprehensive infrastructure and municipal services",
                "collectors": ["comprehensive_infrastructure", "municipal_services"],
                "priority": 2,
                "estimated_time": "10-20 minutes",
                "dependencies": [],
                "data_types": ["infrastructure", "transportation", "healthcare", "education", "government"]
            },
            {
                "name": "NY State Open Data Search",
                "description": "State-level datasets for Westchester County",
                "collectors": ["ny_state_comprehensive"],
                "priority": 3,
                "estimated_time": "15-30 minutes",
                "dependencies": [],
                "data_types": ["crime", "health", "education", "finance", "environmental"]
            },
            {
                "name": "Web Scraping",
                "description": "County website and online document collection",
                "collectors": ["westchester_web_scraper"],
                "priority": 4,
                "estimated_time": "20-45 minutes",
                "dependencies": [],
                "data_types": ["government", "planning", "budgets", "reports"]
            },
            {
                "name": "PDF Processing",
                "description": "Process manually downloaded PDF documents",
                "collectors": ["pdf_data_extractor"],
                "priority": 5,
                "estimated_time": "5-15 minutes",
                "dependencies": [],
                "data_types": ["budgets", "financial", "tax", "demographics"]
            }
        ]

        # Results storage
        self.session_results = {
            "session_info": {
                "start_time": datetime.now().isoformat(),
                "base_directory": str(self.base_dir),
                "collection_phases": len(self.collection_phases),
                "python_version": sys.version
            },
            "phase_results": {},
            "collector_results": {},
            "summary": {},
            "errors": []
        }

    def _import_collectors(self):
        """Import all collector modules"""
        try:
            # Import Comprehensive Census Collector
            from .comprehensive_census_importer import ComprehensiveCensusClient
            self.collectors["comprehensive_census"] = ComprehensiveCensusClient
        except ImportError as e:
            self.session_results["errors"].append(f"Failed to import comprehensive_census_importer: {e}")

        try:
            # Import Infrastructure Collector
            from .comprehensive_infrastructure_importer import ComprehensiveInfrastructureImporter
            self.collectors["comprehensive_infrastructure"] = ComprehensiveInfrastructureImporter
        except ImportError as e:
            self.session_results["errors"].append(f"Failed to import comprehensive_infrastructure_importer: {e}")

        try:
            # Import Municipal Services Collector
            from .municipal_services_importer import MunicipalServicesImporter
            self.collectors["municipal_services"] = MunicipalServicesImporter
        except ImportError as e:
            self.session_results["errors"].append(f"Failed to import municipal_services_importer: {e}")

        try:
            # Import NY State Comprehensive Search
            from .ny_state_comprehensive_search import NYStateComprehensiveSearch
            self.collectors["ny_state_comprehensive"] = NYStateComprehensiveSearch
        except ImportError as e:
            self.session_results["errors"].append(f"Failed to import ny_state_comprehensive_search: {e}")

        try:
            # Import Web Scraper
            from .westchester_web_scraper import WestchesterWebScraper
            self.collectors["westchester_web_scraper"] = WestchesterWebScraper
        except ImportError as e:
            self.session_results["errors"].append(f"Failed to import westchester_web_scraper: {e}")

        try:
            # Import PDF Data Extractor
            from .pdf_data_extractor import PDFDataExtractor
            self.collectors["pdf_data_extractor"] = PDFDataExtractor
        except ImportError as e:
            self.session_results["errors"].append(f"Failed to import pdf_data_extractor: {e}")

    def run_collector(self, collector_name: str, **kwargs) -> Dict[str, Any]:
        """
        Run a specific data collector

        Args:
            collector_name: Name of collector to run
            **kwargs: Arguments to pass to collector

        Returns:
            Collector results
        """
        if collector_name not in self.collectors:
            error_msg = f"Unknown collector: {collector_name}"
            self.session_results["errors"].append(error_msg)
            return {"error": error_msg, "collector": collector_name}

        try:
            print(f"\n{'='*60}")
            print(f"RUNNING COLLECTOR: {collector_name}")
            print(f"{'='*60}")

            # Initialize collector
            CollectorClass = self.collectors[collector_name]
            collector = CollectorClass(**kwargs)

            # Run collector based on type
            if collector_name == "comprehensive_census":
                year = kwargs.get("year", 2022)
                result = collector.run_comprehensive_import(year)

            elif collector_name in ["comprehensive_infrastructure", "municipal_services"]:
                result = collector.download_comprehensive_infrastructure() if collector_name == "comprehensive_infrastructure" else collector.download_all_services()

            elif collector_name == "ny_state_comprehensive":
                max_datasets = kwargs.get("max_datasets", 20)
                result = collector.run_comprehensive_search(max_datasets)

            elif collector_name == "westchester_web_scraper":
                max_pages = kwargs.get("max_pages", 30)
                result = collector.run_comprehensive_scraping(max_pages_per_site=max_pages)

            elif collector_name == "pdf_data_extractor":
                pdf_dir = kwargs.get("pdf_dir")
                result = collector.process_all_pdfs(pdf_dir)

            else:
                # Generic run method
                if hasattr(collector, "run_import"):
                    result = collector.run_import()
                elif hasattr(collector, "download_data"):
                    result = collector.download_data()
                elif hasattr(collector, "run_comprehensive_search"):
                    result = collector.run_comprehensive_search()
                else:
                    error_msg = f"Collector {collector_name} has no runnable method"
                    result = {"error": error_msg}

            # Add metadata
            if isinstance(result, tuple):
                success, data = result
                result = {"success": success, "data": data}

            result["collector"] = collector_name
            result["run_timestamp"] = datetime.now().isoformat()
            result["kwargs"] = kwargs

            print(f"\n[COMPLETE] {collector_name}")
            if result.get("success"):
                print(f"[SUCCESS] Collector completed successfully")
            else:
                print(f"[WARNING] Collector completed with issues")

            return result

        except Exception as e:
            error_msg = f"Collector {collector_name} failed: {str(e)}"
            traceback_str = traceback.format_exc()
            print(f"[ERROR] {error_msg}")

            self.session_results["errors"].append(error_msg)
            return {
                "error": error_msg,
                "collector": collector_name,
                "traceback": traceback_str,
                "run_timestamp": datetime.now().isoformat(),
                "kwargs": kwargs
            }

    def run_collection_phase(self, phase: Dict) -> Dict[str, Any]:
        """
        Run a complete collection phase

        Args:
            phase: Phase configuration

        Returns:
            Phase results
        """
        print(f"\n{'='*80}")
        print(f"COLLECTION PHASE: {phase['name']}")
        print(f"Description: {phase['description']}")
        print(f"Priority: {phase['priority']}")
        print(f"Estimated time: {phase['estimated_time']}")
        print(f"Data types: {', '.join(phase['data_types'])}")
        print(f"{'='*80}")

        phase_result = {
            "phase_name": phase["name"],
            "phase_priority": phase["priority"],
            "start_time": datetime.now().isoformat(),
            "collectors_run": [],
            "success": True,
            "errors": [],
            "summary": {}
        }

        collector_results = {}
        total_collectors = len(phase["collectors"])
        successful_collectors = 0

        for i, collector_name in enumerate(phase["collectors"], 1):
            print(f"\n[COLLECTOR {i}/{total_collectors}] {collector_name}")

            # Prepare collector-specific arguments
            kwargs = {}
            if collector_name == "comprehensive_census":
                kwargs["year"] = 2022
            elif collector_name == "ny_state_comprehensive":
                kwargs["max_datasets"] = 20
            elif collector_name == "westchester_web_scraper":
                kwargs["max_pages"] = 30
            elif collector_name == "pdf_data_extractor":
                pdf_dir = self.base_dir / "data" / "raw" / "manual_downloads"
                kwargs["pdf_dir"] = pdf_dir

            # Run collector
            result = self.run_collector(collector_name, **kwargs)
            collector_results[collector_name] = result

            phase_result["collectors_run"].append(collector_name)

            # Check success
            if result.get("success", False):
                successful_collectors += 1
                print(f"[SUCCESS] {collector_name} completed successfully")
            else:
                phase_result["success"] = False
                phase_result["errors"].append(f"{collector_name}: {result.get('error', 'Unknown error')}")
                print(f"[FAILED] {collector_name} failed")

        # Create phase summary
        phase_result.update({
            "end_time": datetime.now().isoformat(),
            "collectors_attempted": total_collectors,
            "collectors_successful": successful_collectors,
            "collectors_failed": total_collectors - successful_collectors,
            "success_rate": f"{(successful_collectors / total_collectors * 100):.1f}%" if total_collectors > 0 else "0%"
        })

        # Add data summary if available
        total_records = 0
        total_files = 0
        data_categories = set()

        for collector_result in collector_results.values():
            if collector_result.get("success"):
                # Try to extract common metrics
                if "total_records" in collector_result:
                    total_records += collector_result["total_records"]
                if "total_files" in collector_result:
                    total_files += collector_result["total_files"]
                if "data_categories" in collector_result:
                    data_categories.update(collector_result["data_categories"])

        phase_result["summary"] = {
            "total_records": total_records,
            "total_files": total_files,
            "data_categories": list(data_categories)
        }

        print(f"\n[PHASE COMPLETE] {phase['name']}")
        print(f"Collectors successful: {successful_collectors}/{total_collectors}")
        print(f"Success rate: {phase_result['success_rate']}")
        if total_records > 0:
            print(f"Records collected: {total_records}")
        if total_files > 0:
            print(f"Files downloaded: {total_files}")

        return phase_result

    def run_complete_collection(self, phases: List[Dict] = None) -> Dict[str, Any]:
        """
        Run the complete data collection process

        Args:
            phases: List of phases to run (uses default if None)

        Returns:
            Complete collection results
        """
        if phases is None:
            phases = self.collection_phases

        print(f"\n{'='*100}")
        print(f"MASTER DATA COLLECTION SESSION")
        print(f"Westchester County Municipal Administrator Platform")
        print(f"{'='*100}")
        print(f"Starting at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Base directory: {self.base_dir}")
        print(f"Phases to run: {len(phases)}")
        print(f"Collectors available: {len(self.collectors)}")
        print()

        # Check collectors
        if not self.collectors:
            print("[ERROR] No collectors available. Check imports.")
            return {"error": "No collectors available"}

        print(f"Available collectors: {', '.join(self.collectors.keys())}")

        # Run each phase
        phase_results = {}
        total_phases = len(phases)
        successful_phases = 0

        for i, phase in enumerate(phases, 1):
            print(f"\n{'='*80}")
            print(f"PHASE {i}/{total_phases}")
            print(f"{'='*80}")

            phase_result = self.run_collection_phase(phase)
            phase_results[phase["name"]] = phase_result

            self.session_results["phase_results"][phase["name"]] = phase_result

            if phase_result["success"]:
                successful_phases += 1
            else:
                print(f"[WARNING] Phase {phase['name']} had issues")

        # Create final summary
        end_time = datetime.now()

        total_records = sum(
            phase.get("summary", {}).get("total_records", 0)
            for phase in phase_results.values()
        )

        total_files = sum(
            phase.get("summary", {}).get("total_files", 0)
            for phase in phase_results.values()
        )

        all_data_categories = set()
        for phase in phase_results.values():
            all_data_categories.update(phase.get("summary", {}).get("data_categories", []))

        final_summary = {
            "session_completed": True,
            "end_time": end_time.isoformat(),
            "duration_minutes": (end_time - datetime.fromisoformat(self.session_results["session_info"]["start_time"])).total_seconds() / 60,
            "total_phases": total_phases,
            "successful_phases": successful_phases,
            "failed_phases": total_phases - successful_phases,
            "overall_success_rate": f"{(successful_phases / total_phases * 100):.1f}%" if total_phases > 0 else "0%",
            "total_records_collected": total_records,
            "total_files_downloaded": total_files,
            "data_categories_collected": list(all_data_categories),
            "collectors_used": list(self.collectors.keys()),
            "errors_count": len(self.session_results["errors"])
        }

        self.session_results["summary"] = final_summary

        # Save comprehensive results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = self.data_dir / f"master_collection_results_{timestamp}.json"

        with open(results_file, 'w') as f:
            json.dump(self.session_results, f, indent=2)

        print(f"\n{'='*100}")
        print(f"MASTER DATA COLLECTION COMPLETE!")
        print(f"{'='*100}")
        print(f"Duration: {final_summary['duration_minutes']:.1f} minutes")
        print(f"Phases completed: {successful_phases}/{total_phases}")
        print(f"Success rate: {final_summary['overall_success_rate']}")
        print(f"Records collected: {total_records:,}")
        print(f"Files downloaded: {total_files}")
        print(f"Data categories: {len(all_data_categories)}")
        print(f"Errors encountered: {len(self.session_results['errors'])}")
        print(f"Results saved to: {results_file}")
        print(f"Data directory: {self.data_dir}")

        if self.session_results["errors"]:
            print(f"\n[ERRORS ENCOUNTERED]")
            for error in self.session_results["errors"]:
                print(f"  - {error}")

        return self.session_results

    def run_quick_collection(self) -> Dict[str, Any]:
        """
        Run a quick collection with high-priority collectors only

        Returns:
            Collection results
        """
        # Select high-priority phases and collectors
        quick_phases = [
            {
                "name": "Quick Census Collection",
                "description": "Essential demographics and social data",
                "collectors": ["comprehensive_census"],
                "priority": 1,
                "estimated_time": "3-5 minutes",
                "dependencies": [],
                "data_types": ["demographics", "economics", "housing"]
            },
            {
                "name": "Quick Infrastructure Collection",
                "description": "Essential infrastructure and services",
                "collectors": ["comprehensive_infrastructure"],
                "priority": 2,
                "estimated_time": "5-10 minutes",
                "dependencies": [],
                "data_types": ["infrastructure", "transportation"]
            }
        ]

        print("\n" + "="*80)
        print("QUICK DATA COLLECTION MODE")
        print("Collecting essential data for immediate use")
        print("="*80)

        return self.run_complete_collection(quick_phases)

    def create_status_report(self) -> str:
        """
        Create a comprehensive status report

        Returns:
            Path to created report file
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        report_content = f"""# Westchester County Data Collection Status Report

**Generated**: {timestamp}
**Base Directory**: {self.base_dir}
**Data Directory**: {self.data_dir}

## Available Collectors

"""
        for name, CollectorClass in self.collectors.items():
            report_content += f"### {name}\n"
            report_content += f"- Module: {CollectorClass.__module__}\n"
            report_content += f"- Class: {CollectorClass.__name__}\n"
            report_content += f"- Status: Available\n\n"

        report_content += f"""## Collection Phases

Total phases configured: {len(self.collection_phases)}

"""
        for i, phase in enumerate(self.collection_phases, 1):
            report_content += f"### Phase {i}: {phase['name']}\n"
            report_content += f"- **Priority**: {phase['priority']}\n"
            report_content += f"- **Description**: {phase['description']}\n"
            report_content += f"- **Collectors**: {', '.join(phase['collectors'])}\n"
            report_content += f"- **Estimated Time**: {phase['estimated_time']}\n"
            report_content += f"- **Data Types**: {', '.join(phase['data_types'])}\n\n"

        report_content += f"""## Usage Instructions

### Complete Collection
```bash
python master_data_collector.py
```

### Quick Collection
```python
from master_data_collector import MasterDataCollector

collector = MasterDataCollector()
results = collector.run_quick_collection()
```

### Run Specific Phase
```python
from master_data_collector import MasterDataCollector

collector = MasterDataCollector()
phase = collector.collection_phases[0]  # First phase
results = collector.run_collection_phase(phase)
```

### Run Specific Collector
```python
from master_data_collector import MasterDataCollector

collector = MasterDataCollector()
results = collector.run_collector("comprehensive_census", year=2022)
```

## Data Directory Structure

```
{self.data_dir}/
├── raw/                    # Raw downloaded data
│   ├── demographics/        # Census data
│   ├── infrastructure/       # OpenStreetMap data
│   ├── ny_state_comprehensive/ # NY State data
│   ├── web_scraped/          # Web scraped data
│   └── manual_downloads/    # Manually downloaded PDFs
├── processed/              # Processed and cleaned data
│   ├── pdf_extracted/       # Extracted PDF data
│   └── [other formats]/
└── [collection_results]   # Session results
```

## Requirements

Install required Python packages:

```bash
pip install requests beautifulsoup4 pdfplumber PyMuPDF PyPDF2
pip install openpyxl pandas geopandas
```

## Next Steps

1. **Run Complete Collection**: Execute the master collector to gather all data
2. **Review Results**: Check the generated JSON files for extracted data
3. **Validate Data**: Verify data quality and completeness
4. **Update Platform**: Integrate new data into the Westchester platform
5. **Schedule Updates**: Set up regular data refresh schedules

---
*Report generated by Master Data Collector*
*Last updated: {timestamp}*
"""

        # Save report
        report_filename = f"data_collection_status_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        report_filepath = self.base_dir / report_filename

        with open(report_filepath, 'w') as f:
            f.write(report_content)

        return str(report_filepath)


def main():
    """Command-line interface for master data collector"""
    print("=" * 100)
    print("WESTCHESTER COUNTY MASTER DATA COLLECTOR")
    print("Comprehensive municipal data gathering system")
    print("=" * 100)
    print()

    # Initialize collector
    collector = MasterDataCollector()

    # Show status
    print(f"Available collectors: {len(collector.collectors)}")
    print(f"Collection phases: {len(collector.collection_phases)}")
    print()

    # Get user choice
    print("Collection Options:")
    print("1. Complete Collection (all phases)")
    print("2. Quick Collection (essential data only)")
    print("3. Status Report Only")
    print("4. Exit")

    choice = input("\nSelect option (1-4): ").strip()

    if choice == "1":
        print("\nStarting complete data collection...")
        print("This may take 30-90 minutes depending on data availability.")
        confirm = input("Continue? (y/N): ").strip().lower()

        if confirm == 'y':
            results = collector.run_complete_collection()
        else:
            print("Collection cancelled.")
            return

    elif choice == "2":
        print("\nStarting quick data collection...")
        print("This will collect essential data in 5-15 minutes.")
        confirm = input("Continue? (y/N): ").strip().lower()

        if confirm == 'y':
            results = collector.run_quick_collection()
        else:
            print("Collection cancelled.")
            return

    elif choice == "3":
        print("\nGenerating status report...")
        report_path = collector.create_status_report()
        print(f"Status report saved to: {report_path}")
        return

    elif choice == "4":
        print("Exiting.")
        return

    else:
        print("Invalid choice. Exiting.")
        return

    # Show final results
    if 'results' in locals():
        summary = results.get("summary", {})
        print("\n" + "=" * 100)
        print("COLLECTION COMPLETE!")
        print("=" * 100)

        if summary:
            print(f"Success rate: {summary.get('overall_success_rate', 'Unknown')}")
            print(f"Records collected: {summary.get('total_records_collected', 0):,}")
            print(f"Files downloaded: {summary.get('total_files_downloaded', 0):,}")
            print(f"Data categories: {len(summary.get('data_categories_collected', []))}")
            print(f"Duration: {summary.get('duration_minutes', 0):.1f} minutes")

        print(f"\nNext steps:")
        print("1. Review the collected data in: {collector.data_dir}")
        print("2. Check for any errors in the results files")
        print("3. Validate data quality before integration")
        print("4. Update the Westchester platform with new data")


if __name__ == "__main__":
    main()