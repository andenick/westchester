#!/usr/bin/env python3
"""
Enhanced Master Data Collector for Westchester County
Coordinates all data collection systems including new specialized collectors
Provides comprehensive data orchestration with parallel processing and caching
"""

import os
import sys
import json
import time
import logging
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd

# Import all data collectors
from comprehensive_census_importer import ComprehensiveCensusClient
from municipal_services_importer import MunicipalServicesImporter
from ny_state_comprehensive_search import NYStateComprehensiveSearch
from westchester_web_scraper import WestchesterWebScraper
from pdf_data_extractor import PDFDataExtractor
from westchester_gis_collector import WestchesterGISCollector
from metronorth_gtfs_collector import MetroNorthGTFSCollector
from fred_economic_collector import FREDDataCollector
from nyc_opendata_collector import NYCOpenDataCollector
from hud_data_collector import HUDDataCollector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_collection.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EnhancedMasterDataCollector:
    """Enhanced master data collector with parallel processing and comprehensive data sources"""

    def __init__(self, output_dir: str = None):
        self.output_dir = Path(output_dir or "data/raw/enhanced_collection")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize all collectors
        self.collectors = {
            # Original collectors
            'comprehensive_census': ComprehensiveCensusClient,
            'municipal_services': MunicipalServicesImporter,
            'ny_state_search': NYStateComprehensiveSearch,
            'web_scraper': WestchesterWebScraper,
            'pdf_extractor': PDFDataExtractor,

            # New specialized collectors
            'westchester_gis': WestchesterGISCollector,
            'metronorth_gtfs': MetroNorthGTFSCollector,
            'fred_economic': FREDDataCollector,
            'nyc_opendata': NYCOpenDataCollector,
            'hud_housing': HUDDataCollector
        }

        # Enhanced collection phases with new sources
        self.collection_phases = [
            {
                "name": "Core Demographics & Infrastructure",
                "description": "Essential Census and infrastructure data",
                "collectors": ["comprehensive_census", "municipal_services"],
                "priority": 1,
                "parallel": True
            },
            {
                "name": "Geographic & Spatial Data",
                "description": "GIS datasets and geospatial information",
                "collectors": ["westchester_gis"],
                "priority": 2,
                "parallel": False
            },
            {
                "name": "Transportation & Transit",
                "description": "Metro-North and transportation data",
                "collectors": ["metronorth_gtfs"],
                "priority": 3,
                "parallel": False
            },
            {
                "name": "Economic & Housing Data",
                "description": "Economic indicators and housing information",
                "collectors": ["fred_economic", "hud_housing"],
                "priority": 4,
                "parallel": True
            },
            {
                "name": "Regional Context Data",
                "description": "NYC Open Data for regional comparison",
                "collectors": ["nyc_opendata"],
                "priority": 5,
                "parallel": False
            },
            {
                "name": "State-Level Data",
                "description": "NY State comprehensive search",
                "collectors": ["ny_state_search"],
                "priority": 6,
                "parallel": False
            },
            {
                "name": "Web & Document Data",
                "description": "Web scraping and PDF processing",
                "collectors": ["web_scraper", "pdf_extractor"],
                "priority": 7,
                "parallel": True
            }
        ]

        # Collection options
        self.collection_options = {
            'quick_collection': {
                'name': 'Quick Collection',
                'description': 'Essential data only (15-30 minutes)',
                'collectors': ['comprehensive_census', 'municipal_services', 'westchester_gis'],
                'max_workers': 2
            },
            'standard_collection': {
                'name': 'Standard Collection',
                'description': 'Comprehensive data collection (1-2 hours)',
                'collectors': ['comprehensive_census', 'municipal_services', 'westchester_gis',
                              'metronorth_gtfs', 'fred_economic', 'hud_housing'],
                'max_workers': 3
            },
            'complete_collection': {
                'name': 'Complete Collection',
                'description': 'All available data sources (2-4 hours)',
                'collectors': list(self.collectors.keys()),
                'max_workers': 4
            },
            'research_collection': {
                'name': 'Research Collection',
                'description': 'Comprehensive data with real-time feeds (3-6 hours)',
                'collectors': list(self.collectors.keys()),
                'max_workers': 4,
                'include_realtime': True
            }
        }

        # Results tracking
        self.current_collection = {
            'start_time': None,
            'end_time': None,
            'results': {},
            'summary': {
                'total_collectors': 0,
                'successful_collectors': 0,
                'failed_collectors': 0,
                'total_records': 0,
                'total_files_created': 0
            },
            'errors': [],
            'warnings': []
        }

    def run_collector(self, collector_name: str, **kwargs) -> Dict[str, Any]:
        """Run a single data collector with error handling"""
        start_time = time.time()
        logger.info(f"Starting collector: {collector_name}")

        try:
            # Initialize collector
            collector_class = self.collectors[collector_name]
            collector = collector_class(output_dir=str(self.output_dir / collector_name))

            # Determine the appropriate method to call
            if hasattr(collector, 'collect_all_data'):
                result = collector.collect_all_data(**kwargs)
            elif hasattr(collector, 'download_all_datasets'):
                result = collector.download_all_datasets(**kwargs)
            elif hasattr(collector, 'run_complete_collection'):
                result = collector.run_complete_collection(**kwargs)
            else:
                # Fallback to main method
                result = collector.main(**kwargs) if hasattr(collector, 'main') else None

            execution_time = time.time() - start_time

            # Normalize result structure
            if result is None:
                result = {'success': False, 'error': 'No result returned'}
            elif isinstance(result, dict):
                result['execution_time'] = execution_time
                result['collector_name'] = collector_name
                if 'success' not in result:
                    result['success'] = True
            else:
                result = {
                    'success': True,
                    'data': result,
                    'execution_time': execution_time,
                    'collector_name': collector_name
                }

            logger.info(f"✅ Collector {collector_name} completed successfully in {execution_time:.2f}s")
            return result

        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Collector {collector_name} failed: {str(e)}"
            logger.error(f"❌ {error_msg}")

            result = {
                'success': False,
                'error': error_msg,
                'execution_time': execution_time,
                'collector_name': collector_name
            }

            self.current_collection['errors'].append(error_msg)
            return result

    def run_collectors_parallel(self, collector_names: List[str], max_workers: int = 2, **kwargs) -> Dict[str, Any]:
        """Run multiple collectors in parallel"""
        logger.info(f"Running {len(collector_names)} collectors in parallel with {max_workers} workers")

        results = {}
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all collector tasks
            future_to_collector = {
                executor.submit(self.run_collector, name, **kwargs): name
                for name in collector_names
            }

            # Collect results as they complete
            for future in as_completed(future_to_collector):
                collector_name = future_to_collector[future]
                try:
                    result = future.result()
                    results[collector_name] = result

                    if result.get('success', False):
                        self.current_collection['summary']['successful_collectors'] += 1
                    else:
                        self.current_collection['summary']['failed_collectors'] += 1

                except Exception as e:
                    error_msg = f"Parallel execution error for {collector_name}: {str(e)}"
                    logger.error(f"❌ {error_msg}")
                    results[collector_name] = {
                        'success': False,
                        'error': error_msg,
                        'collector_name': collector_name
                    }
                    self.current_collection['errors'].append(error_msg)
                    self.current_collection['summary']['failed_collectors'] += 1

        return results

    def run_collection_phase(self, phase: Dict, **kwargs) -> Dict[str, Any]:
        """Run a complete collection phase"""
        logger.info(f"🚀 Starting Phase: {phase['name']}")
        logger.info(f"Description: {phase['description']}")

        phase_start_time = time.time()
        phase_results = {}

        if phase.get('parallel', False) and len(phase['collectors']) > 1:
            # Run collectors in parallel
            phase_results = self.run_collectors_parallel(
                phase['collectors'],
                max_workers=min(len(phase['collectors']), 3),
                **kwargs
            )
        else:
            # Run collectors sequentially
            for collector_name in phase['collectors']:
                if collector_name in self.collectors:
                    result = self.run_collector(collector_name, **kwargs)
                    phase_results[collector_name] = result

                    if result.get('success', False):
                        self.current_collection['summary']['successful_collectors'] += 1
                    else:
                        self.current_collection['summary']['failed_collectors'] += 1

                else:
                    warning_msg = f"Collector {collector_name} not available"
                    logger.warning(f"⚠️ {warning_msg}")
                    self.current_collection['warnings'].append(warning_msg)

        phase_execution_time = time.time() - phase_start_time

        phase_summary = {
            'phase_name': phase['name'],
            'description': phase['description'],
            'collectors_run': list(phase_results.keys()),
            'successful_collectors': sum(1 for r in phase_results.values() if r.get('success', False)),
            'failed_collectors': sum(1 for r in phase_results.values() if not r.get('success', False)),
            'execution_time': phase_execution_time,
            'results': phase_results
        }

        logger.info(f"✅ Phase '{phase['name']}' completed in {phase_execution_time:.2f}s")
        logger.info(f"   Successful: {phase_summary['successful_collectors']}, Failed: {phase_summary['failed_collectors']}")

        return phase_summary

    def run_enhanced_collection(self, collection_type: str = 'standard_collection', **kwargs) -> Dict[str, Any]:
        """Run enhanced data collection with specified type"""

        if collection_type not in self.collection_options:
            raise ValueError(f"Unknown collection type: {collection_type}")

        option = self.collection_options[collection_type]
        logger.info(f"🎯 Starting {option['name']}")
        logger.info(f"Description: {option['description']}")

        # Initialize collection tracking
        self.current_collection = {
            'start_time': datetime.now().isoformat(),
            'collection_type': collection_type,
            'description': option['description'],
            'results': {},
            'phases': [],
            'summary': {
                'total_collectors': len(option['collectors']),
                'successful_collectors': 0,
                'failed_collectors': 0,
                'total_records': 0,
                'total_files_created': 0,
                'total_execution_time': 0
            },
            'errors': [],
            'warnings': [],
            'environment': {
                'python_version': sys.version,
                'working_directory': os.getcwd(),
                'data_directory': str(self.output_dir)
            }
        }

        start_time = time.time()

        try:
            # Filter phases based on collectors to run
            relevant_phases = []
            for phase in self.collection_phases:
                phase_collectors = [c for c in phase['collectors'] if c in option['collectors']]
                if phase_collectors:
                    relevant_phase = phase.copy()
                    relevant_phase['collectors'] = phase_collectors
                    relevant_phases.append(relevant_phase)

            logger.info(f"Running {len(relevant_phases)} phases with {len(option['collectors'])} total collectors")

            # Run each phase
            for phase in relevant_phases:
                phase_result = self.run_collection_phase(phase, **kwargs)
                self.current_collection['phases'].append(phase_result)

            # Calculate final summary
            total_time = time.time() - start_time
            self.current_collection['end_time'] = datetime.now().isoformat()
            self.current_collection['summary']['total_execution_time'] = total_time

            # Calculate total records and files (if available in results)
            for phase_result in self.current_collection['phases']:
                for collector_result in phase_result['results'].values():
                    if isinstance(collector_result, dict):
                        # Try to extract record counts from different result formats
                        if 'summary' in collector_result:
                            summary = collector_result['summary']
                            if isinstance(summary, dict):
                                if 'total_records' in summary:
                                    self.current_collection['summary']['total_records'] += summary['total_records']
                                if 'total_datasets' in summary:
                                    self.current_collection['summary']['total_files_created'] += summary['total_datasets']
                                if 'successful_downloads' in summary:
                                    self.current_collection['summary']['total_files_created'] += summary['successful_downloads']

            # Generate and save comprehensive report
            self.generate_enhanced_collection_report()

            logger.info(f"\n🎉 Enhanced Data Collection Complete!")
            logger.info(f"✅ Successful collectors: {self.current_collection['summary']['successful_collectors']}/{self.current_collection['summary']['total_collectors']}")
            logger.info(f"📊 Total records: {self.current_collection['summary']['total_records']:,}")
            logger.info(f"📁 Total files: {self.current_collection['summary']['total_files_created']}")
            logger.info(f"⏱️ Total time: {total_time:.2f} seconds ({total_time/60:.1f} minutes)")

            return self.current_collection

        except Exception as e:
            error_msg = f"Enhanced collection failed: {str(e)}"
            logger.error(f"❌ {error_msg}")
            self.current_collection['errors'].append(error_msg)
            self.current_collection['end_time'] = datetime.now().isoformat()
            return self.current_collection

    def generate_enhanced_collection_report(self) -> None:
        """Generate comprehensive report of the enhanced collection"""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.output_dir / f"enhanced_collection_report_{timestamp}.json"

        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_collection, f, indent=2, ensure_ascii=False, default=str)

            logger.info(f"📄 Enhanced collection report saved to: {report_file}")

            # Generate human-readable summary
            summary_file = self.output_dir / f"enhanced_collection_summary_{timestamp}.md"
            summary_content = self.generate_human_readable_summary()

            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(summary_content)

            logger.info(f"📝 Human-readable summary saved to: {summary_file}")

        except Exception as e:
            logger.error(f"Error saving collection report: {e}")

    def generate_human_readable_summary(self) -> str:
        """Generate human-readable summary of collection results"""

        summary = []
        summary.append("# Enhanced Westchester Data Collection Report")
        summary.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        summary.append("")

        # Executive Summary
        summary.append("## Executive Summary")
        summary.append(f"**Collection Type**: {self.current_collection['collection_type'].replace('_', ' ').title()}")
        summary.append(f"**Description**: {self.current_collection['description']}")
        summary.append(f"**Duration**: {self.current_collection['summary']['total_execution_time']:.2f} seconds")
        summary.append(f"**Success Rate**: {self.current_collection['summary']['successful_collectors']}/{self.current_collection['summary']['total_collectors']} collectors")
        summary.append("")

        # Collection Phases
        summary.append("## Collection Phases")
        for phase in self.current_collection['phases']:
            summary.append(f"### {phase['phase_name']}")
            summary.append(f"**Description**: {phase['description']}")
            summary.append(f"**Duration**: {phase['execution_time']:.2f} seconds")
            summary.append(f"**Success Rate**: {phase['successful_collectors']}/{len(phase['collectors_run'])} collectors")

            for collector_name, result in phase['results'].items():
                status = "✅" if result.get('success', False) else "❌"
                summary.append(f"- {status} {collector_name}")

            summary.append("")

        # Data Categories Summary
        summary.append("## Data Categories Collected")
        data_categories = {
            'Demographics': ['comprehensive_census'],
            'Infrastructure': ['municipal_services', 'westchester_gis'],
            'Transportation': ['metronorth_gtfs'],
            'Economic': ['fred_economic'],
            'Housing': ['hud_housing'],
            'Regional Context': ['nyc_opendata'],
            'State Data': ['ny_state_search'],
            'Web Content': ['web_scraper', 'pdf_extractor']
        }

        for category, collectors in data_categories.items():
            successful = sum(1 for c in collectors if any(
                c in phase['results'] and phase['results'][c].get('success', False)
                for phase in self.current_collection['phases']
            ))
            total = len(collectors)
            status = "✅" if successful == total else "⚠️" if successful > 0 else "❌"
            summary.append(f"- {status} **{category}**: {successful}/{total} collectors")

        summary.append("")

        # Statistics
        summary.append("## Collection Statistics")
        summary.append(f"- **Total Records Collected**: {self.current_collection['summary']['total_records']:,}")
        summary.append(f"- **Total Files Created**: {self.current_collection['summary']['total_files_created']}")
        summary.append(f"- **Errors Encountered**: {len(self.current_collection['errors'])}")
        summary.append(f"- **Warnings Generated**: {len(self.current_collection['warnings'])}")
        summary.append("")

        # Errors and Warnings
        if self.current_collection['errors']:
            summary.append("## Errors")
            for error in self.current_collection['errors'][:10]:  # Limit to first 10
                summary.append(f"- ❌ {error}")
            if len(self.current_collection['errors']) > 10:
                summary.append(f"- ... and {len(self.current_collection['errors']) - 10} more errors")
            summary.append("")

        if self.current_collection['warnings']:
            summary.append("## Warnings")
            for warning in self.current_collection['warnings']:
                summary.append(f"- ⚠️ {warning}")
            summary.append("")

        # Next Steps
        summary.append("## Next Steps")
        summary.append("1. Review collected data for quality and completeness")
        summary.append("2. Validate data formats and structures")
        summary.append("3. Process and clean data as needed")
        summary.append("4. Update platform data sources")
        summary.append("5. Schedule regular data refresh cycles")

        return "\n".join(summary)

    def run_quick_collection(self) -> Dict[str, Any]:
        """Run quick collection with essential data only"""
        return self.run_enhanced_collection('quick_collection')

    def run_standard_collection(self) -> Dict[str, Any]:
        """Run standard comprehensive data collection"""
        return self.run_enhanced_collection('standard_collection')

    def run_complete_collection(self) -> Dict[str, Any]:
        """Run complete data collection with all sources"""
        return self.run_enhanced_collection('complete_collection')

    def run_research_collection(self) -> Dict[str, Any]:
        """Run research-level collection with real-time data"""
        return self.run_enhanced_collection('research_collection', include_realtime=True)

def main():
    """Main function for command line usage"""
    import argparse

    parser = argparse.ArgumentParser(description='Enhanced Westchester Data Collection System')
    parser.add_argument('--output-dir', help='Output directory for data files')
    parser.add_argument('--collection-type', choices=['quick_collection', 'standard_collection', 'complete_collection', 'research_collection'],
                       default='standard_collection', help='Type of collection to run')
    parser.add_argument('--list-collectors', action='store_true', help='List all available collectors')
    parser.add_argument('--run-collector', help='Run a specific collector')

    args = parser.parse_args()

    # Initialize enhanced collector
    collector = EnhancedMasterDataCollector(output_dir=args.output_dir)

    if args.list_collectors:
        print("\nAvailable Data Collectors:")
        for name, collector_class in collector.collectors.items():
            print(f"  [OK] {name}: {collector_class.__name__}")

        print(f"\nCollection Types:")
        for name, option in collector.collection_options.items():
            print(f"  -> {name}: {option['description']}")
        return

    if args.run_collector:
        if args.run_collector in collector.collectors:
            print(f"Running single collector: {args.run_collector}")
            result = collector.run_collector(args.run_collector)
            if result.get('success', False):
                print(f"[OK] Collector completed successfully")
            else:
                print(f"[ERROR] Collector failed: {result.get('error', 'Unknown error')}")
        else:
            print(f"[ERROR] Unknown collector: {args.run_collector}")
        return

    # Run collection
    print(f"Starting {collector.collection_options[args.collection_type]['name']}...")
    results = collector.run_enhanced_collection(args.collection_type)

    # Print final summary
    print(f"\nFinal Results:")
    print(f"  Successful: {results['summary']['successful_collectors']}/{results['summary']['total_collectors']} collectors")
    print(f"  Records: {results['summary']['total_records']:,}")
    print(f"  Files: {results['summary']['total_files_created']}")
    print(f"  Duration: {results['summary']['total_execution_time']:.2f}s")

    if results['errors']:
        print(f"  Errors: {len(results['errors'])}")

if __name__ == "__main__":
    main()