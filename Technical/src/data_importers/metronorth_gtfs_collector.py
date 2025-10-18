#!/usr/bin/env python3
"""
Metro-North GTFS Transit Data Collector
Collects real-time and schedule data for Metro-North Railroad
Provides comprehensive transit information for Westchester County
"""

import os
import sys
import json
import time
import requests
import logging
import zipfile
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import gtfs_kit as gk
from urllib.parse import urljoin

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MetroNorthGTFSCollector:
    """Collects Metro-North Railroad GTFS and real-time data"""

    def __init__(self, output_dir: str = None):
        self.output_dir = Path(output_dir or "data/raw/transit/metronorth")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Metro-North GTFS data sources
        self.gtfs_url = "http://web.mta.info/developers/data/nyct/gtfs/mnr.zip"
        self.realtime_url = "https://api.mta.info/mta_esi?key={key}&feed_id=21"  # Metro-North feed ID

        # Westchester County Metro-North stations (major ones)
        self.westchester_stations = {
            "CROTON-HARMON": "Croton-Harmon",
            "CORTLANDT": "Cortlandt",
            "GARRISON": "Garrison",
            "GOLDENS BRIDGE": "Goldens Bridge",
            "HARRIMAN": "Harriman",
            "HASTINGS-ON-HUDSON": "Hastings-on-Hudson",
            "HAWTHORNE": "Hawthorne",
            "KATONAH": "Katonah",
            "LAKESIDE": "Lakeside",
            "MAMARONECK": "Mamaroneck",
            "MOHEGAN LAKE": "Mohegan Lake",
            "MOUNT PLEASANT": "Mount Pleasant",
            "MOUNT KISCO": "Mount Kisco",
            "MOUNT VERNON EAST": "Mount Vernon East",
            "MOUNT VERNON WEST": "Mount Vernon West",
            "NEW ROCHELLE": "New Rochelle",
            "NORTH WHITE PLAINS": "North White Plains",
            "OSSINING": "Ossining",
            "PEEKSKILL": "Peekskill",
            "PLEASANTVILLE": "Pleasantville",
            "PORT CHESTER": "Port Chester",
            "PURCHASE": "Purchase",
            "RENSSELAER": "Rensselaer",
            "RYE": "Rye",
            "SCARSDALE": "Scarsdale",
            "TARRYTOWN": "Tarrytown",
            "TUCKAHOE": "Tuckahoe",
            "VALHALLA": "Valhalla",
            "WAPPINGERS FALLS": "Wappingers Falls",
            "WHITE PLAINS": "White Plains",
            "YONKERS": "Yonkers",
            "YORKER HEIGHTS": "Yorker Heights"
        }

        # Rate limiting
        self.request_delay = 1.0
        self.last_request_time = 0

        # Session for persistent connections
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Westchester Data Platform/1.0 (Transit Data Collection)'
        })

        # MTA API key (should be in environment)
        self.mta_api_key = os.getenv('MTA_API_KEY')

    def _rate_limit(self):
        """Implement rate limiting for requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.request_delay:
            sleep_time = self.request_delay - time_since_last
            logger.info(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def download_gtfs_data(self) -> Optional[Dict[str, Any]]:
        """Download static GTFS schedule data"""
        logger.info("Downloading Metro-North GTFS schedule data...")

        try:
            self._rate_limit()
            response = self.session.get(self.gtfs_url)
            response.raise_for_status()

            # Save ZIP file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            zip_filename = f"{timestamp}_metronorth_gtfs.zip"
            zip_path = self.output_dir / zip_filename

            with open(zip_path, 'wb') as f:
                f.write(response.content)

            logger.info(f"Downloaded GTFS data to {zip_path}")

            # Extract and process GTFS data
            extract_dir = self.output_dir / f"gtfs_extract_{timestamp}"
            extract_dir.mkdir(exist_ok=True)

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)

            logger.info(f"Extracted GTFS data to {extract_dir}")

            # Load GTFS data
            feed = gk.read_feed(zip_path, dist_units='km')

            # Get basic statistics
            stats = {
                'feed_date': timestamp,
                'agencies': len(feed.agencies) if hasattr(feed, 'agencies') else 0,
                'routes': len(feed.routes) if hasattr(feed, 'routes') else 0,
                'stops': len(feed.stops) if hasattr(feed, 'stops') else 0,
                'trips': len(feed.trips) if hasattr(feed, 'trips') else 0,
                'stop_times': len(feed.stop_times) if hasattr(feed, 'stop_times') else 0,
                'zip_file': str(zip_path),
                'extract_dir': str(extract_dir)
            }

            logger.info(f"GTFS data loaded: {stats['routes']} routes, {stats['stops']} stops, {stats['trips']} trips")

            return {
                'stats': stats,
                'feed': feed,
                'zip_path': zip_path,
                'extract_dir': extract_dir
            }

        except Exception as e:
            logger.error(f"Failed to download GTFS data: {e}")
            return None

    def extract_westchester_data(self, gtfs_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract Westchester County specific data from GTFS feed"""

        logger.info("Extracting Westchester County transit data...")

        feed = gtfs_data['feed']
        westchester_data = {
            'stations': [],
            'routes': [],
            'trips': [],
            'stop_times': []
        }

        try:
            # Get Westchester stations
            if hasattr(feed, 'stops') and feed.stops is not None:
                for _, stop in feed.stops.iterrows():
                    stop_name = stop.get('stop_name', '').upper()

                    # Check if this is a Westchester station
                    is_westchester = any(
                        station_name in stop_name or stop_name in station_name
                        for station_name in self.westchester_stations.keys()
                    )

                    if is_westchester:
                        station_info = {
                            'stop_id': stop.get('stop_id'),
                            'stop_name': stop.get('stop_name'),
                            'stop_lat': stop.get('stop_lat'),
                            'stop_lon': stop.get('stop_lon'),
                            'municipality': self._identify_municipality(stop.get('stop_name', '')),
                            'is_westchester': True
                        }
                        westchester_data['stations'].append(station_info)

                logger.info(f"Found {len(westchester_data['stations'])} Westchester stations")

            # Get routes serving Westchester
            if hasattr(feed, 'trips') and feed.trips is not None and hasattr(feed, 'stop_times') and feed.stop_times is not None:
                westchester_stop_ids = {station['stop_id'] for station in westchester_data['stations']}

                # Find trips that stop at Westchester stations
                westchester_trip_ids = set()
                for _, stop_time in feed.stop_times.iterrows():
                    if stop_time.get('stop_id') in westchester_stop_ids:
                        westchester_trip_ids.add(stop_time.get('trip_id'))

                # Get routes for these trips
                if hasattr(feed, 'trips') and feed.trips is not None:
                    westchester_trips = feed.trips[feed.trips['trip_id'].isin(westchester_trip_ids)]
                    westchester_route_ids = set(westchester_trips['route_id'])

                    if hasattr(feed, 'routes') and feed.routes is not None:
                        westchester_routes = feed.routes[feed.routes['route_id'].isin(westchester_route_ids)]

                        for _, route in westchester_routes.iterrows():
                            route_info = {
                                'route_id': route.get('route_id'),
                                'route_short_name': route.get('route_short_name'),
                                'route_long_name': route.get('route_long_name'),
                                'route_desc': route.get('route_desc'),
                                'route_type': route.get('route_type'),
                                'route_color': route.get('route_color'),
                                'route_text_color': route.get('route_text_color')
                            }
                            westchester_data['routes'].append(route_info)

                        logger.info(f"Found {len(westchester_data['routes'])} routes serving Westchester")

                # Get Westchester-specific stop times
                westchester_stop_times = feed.stop_times[
                    feed.stop_times['stop_id'].isin(westchester_stop_ids)
                ]

                # Convert to list of dictionaries
                for _, stop_time in westchester_stop_times.iterrows():
                    stop_time_info = {
                        'trip_id': stop_time.get('trip_id'),
                        'arrival_time': stop_time.get('arrival_time'),
                        'departure_time': stop_time.get('departure_time'),
                        'stop_id': stop_time.get('stop_id'),
                        'stop_sequence': stop_time.get('stop_sequence'),
                        'pickup_type': stop_time.get('pickup_type'),
                        'drop_off_type': stop_time.get('drop_off_type')
                    }
                    westchester_data['stop_times'].append(stop_time_info)

                logger.info(f"Found {len(westchester_data['stop_times'])} stop times for Westchester stations")

        except Exception as e:
            logger.error(f"Error extracting Westchester data: {e}")

        return westchester_data

    def _identify_municipality(self, stop_name: str) -> str:
        """Identify municipality based on station name"""
        stop_name_upper = stop_name.upper()

        for municipality, station in self.westchester_stations.items():
            if municipality in stop_name_upper or stop_name_upper in municipality:
                return station

        # Try to extract from station name
        if "WHITE PLAINS" in stop_name_upper:
            return "White Plains"
        elif "NEW ROCHELLE" in stop_name_upper:
            return "New Rochelle"
        elif "YONKERS" in stop_name_upper:
            return "Yonkers"
        elif "MOUNT VERNON" in stop_name_upper:
            return "Mount Vernon"

        return "Unknown"

    def download_realtime_data(self) -> Optional[Dict[str, Any]]:
        """Download real-time transit data if API key is available"""
        if not self.mta_api_key:
            logger.warning("No MTA API key found. Skipping real-time data.")
            logger.info("Set MTA_API_KEY environment variable to enable real-time data.")
            return None

        logger.info("Downloading Metro-North real-time data...")

        try:
            url = self.realtime_url.format(key=self.mta_api_key)
            self._rate_limit()
            response = self.session.get(url)
            response.raise_for_status()

            # Save real-time data
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            rt_filename = f"{timestamp}_metronorth_realtime.json"
            rt_path = self.output_dir / rt_filename

            # Parse and save the GTFS-RT data
            from google.transit import gtfs_realtime_pb2
            feed = gtfs_realtime_pb2.FeedMessage()
            feed.ParseFromString(response.content)

            # Convert to JSON for easier processing
            rt_data = {
                'timestamp': feed.header.timestamp,
                'gtfs_realtime': feed,
                'download_time': datetime.now().isoformat(),
                'entity_count': len(feed.entity)
            }

            # Process entities
            entities = []
            for entity in feed.entity:
                entity_data = {
                    'id': entity.id,
                    'vehicle': None,
                    'trip_update': None,
                    'alert': None
                }

                if entity.HasField('vehicle'):
                    entity_data['vehicle'] = {
                        'trip_id': entity.vehicle.trip.trip_id if entity.vehicle.trip else None,
                        'route_id': entity.vehicle.trip.route_id if entity.vehicle.trip else None,
                        'current_stop_sequence': entity.vehicle.current_stop_sequence,
                        'current_status': entity.vehicle.current_status,
                        'timestamp': entity.vehicle.timestamp,
                        'position': {
                            'latitude': entity.vehicle.position.latitude,
                            'longitude': entity.vehicle.position.longitude,
                            'bearing': entity.vehicle.position.bearing,
                            'speed': entity.vehicle.position.speed
                        }
                    }

                if entity.HasField('trip_update'):
                    stop_time_updates = []
                    for stu in entity.trip_update.stop_time_update:
                        stop_time_updates.append({
                            'stop_id': stu.stop_id,
                            'arrival_delay': stu.arrival.delay if stu.HasField('arrival') else None,
                            'departure_delay': stu.departure.delay if stu.HasField('departure') else None
                        })

                    entity_data['trip_update'] = {
                        'trip_id': entity.trip_update.trip.trip_id if entity.trip_update.trip else None,
                        'route_id': entity.trip_update.trip.route_id if entity.trip_update.trip else None,
                        'stop_time_updates': stop_time_updates
                    }

                entities.append(entity_data)

            rt_data['entities'] = entities

            with open(rt_path, 'w', encoding='utf-8') as f:
                json.dump(rt_data, f, indent=2, default=str, ensure_ascii=False)

            logger.info(f"Downloaded real-time data: {len(entities)} entities")
            logger.info(f"Saved to: {rt_path}")

            return rt_data

        except Exception as e:
            logger.error(f"Failed to download real-time data: {e}")
            return None

    def save_westchester_data(self, westchester_data: Dict[str, Any]) -> Dict[str, str]:
        """Save Westchester-specific data to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        saved_files = {}

        try:
            # Save stations
            if westchester_data['stations']:
                stations_file = self.output_dir / f"{timestamp}_westchester_stations.json"
                with open(stations_file, 'w', encoding='utf-8') as f:
                    json.dump(westchester_data['stations'], f, indent=2, ensure_ascii=False)
                saved_files['stations'] = str(stations_file)

                # Also save as CSV for easy viewing
                stations_df = pd.DataFrame(westchester_data['stations'])
                stations_csv = self.output_dir / f"{timestamp}_westchester_stations.csv"
                stations_df.to_csv(stations_csv, index=False)
                saved_files['stations_csv'] = str(stations_csv)

            # Save routes
            if westchester_data['routes']:
                routes_file = self.output_dir / f"{timestamp}_westchester_routes.json"
                with open(routes_file, 'w', encoding='utf-8') as f:
                    json.dump(westchester_data['routes'], f, indent=2, ensure_ascii=False)
                saved_files['routes'] = str(routes_file)

            # Save stop times (might be large, save as CSV)
            if westchester_data['stop_times']:
                stop_times_df = pd.DataFrame(westchester_data['stop_times'])
                stop_times_csv = self.output_dir / f"{timestamp}_westchester_stop_times.csv"
                stop_times_df.to_csv(stop_times_csv, index=False)
                saved_files['stop_times_csv'] = str(stop_times_csv)

            logger.info(f"Saved Westchester transit data to {len(saved_files)} files")

        except Exception as e:
            logger.error(f"Error saving Westchester data: {e}")

        return saved_files

    def collect_all_data(self, include_realtime: bool = False) -> Dict[str, Any]:
        """Collect all Metro-North data for Westchester County"""

        logger.info("Starting Metro-North transit data collection for Westchester County...")
        logger.info(f"Output directory: {self.output_dir}")

        results = {
            'collection_time': datetime.now().isoformat(),
            'gtfs_data': None,
            'westchester_data': None,
            'realtime_data': None,
            'saved_files': {},
            'summary': {}
        }

        # Download static GTFS data
        gtfs_data = self.download_gtfs_data()
        if gtfs_data:
            results['gtfs_data'] = gtfs_data['stats']
            results['summary']['gtfs_download'] = 'success'

            # Extract Westchester-specific data
            westchester_data = self.extract_westchester_data(gtfs_data)
            results['westchester_data'] = {
                'stations_count': len(westchester_data['stations']),
                'routes_count': len(westchester_data['routes']),
                'stop_times_count': len(westchester_data['stop_times'])
            }

            # Save Westchester data
            saved_files = self.save_westchester_data(westchester_data)
            results['saved_files'] = saved_files
            results['summary']['westchester_extraction'] = 'success'

        else:
            results['summary']['gtfs_download'] = 'failed'
            logger.error("Failed to download GTFS data")

        # Download real-time data if requested and API key is available
        if include_realtime:
            realtime_data = self.download_realtime_data()
            if realtime_data:
                results['realtime_data'] = {
                    'entity_count': realtime_data['entity_count'],
                    'timestamp': realtime_data['timestamp']
                }
                results['summary']['realtime_download'] = 'success'
            else:
                results['summary']['realtime_download'] = 'skipped'

        # Save collection summary
        summary_file = self.output_dir / f"metronorth_collection_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        logger.info(f"\n🎉 Metro-North Data Collection Complete!")
        logger.info(f"📊 Westchester stations: {results['westchester_data']['stations_count'] if results['westchester_data'] else 0}")
        logger.info(f"🚊 Routes serving Westchester: {results['westchester_data']['routes_count'] if results['westchester_data'] else 0}")
        logger.info(f"📝 Stop times: {results['westchester_data']['stop_times_count'] if results['westchester_data'] else 0:,}")
        if include_realtime and results.get('realtime_data'):
            logger.info(f"🚇 Real-time entities: {results['realtime_data']['entity_count']}")
        logger.info(f"📁 Summary saved to: {summary_file}")

        return results

def main():
    """Main function for command line usage"""
    import argparse

    parser = argparse.ArgumentParser(description='Collect Metro-North GTFS Transit Data')
    parser.add_argument('--output-dir', help='Output directory for data files')
    parser.add_argument('--include-realtime', action='store_true',
                       help='Include real-time data (requires MTA_API_KEY)')
    parser.add_argument('--gtfs-only', action='store_true',
                       help='Download GTFS data only')

    args = parser.parse_args()

    # Initialize collector
    collector = MetroNorthGTFSCollector(output_dir=args.output_dir)

    # Collect data
    results = collector.collect_all_data(include_realtime=args.include_realtime)

    # Print summary
    if results['gtfs_data']:
        print(f"\n📊 Collection Summary:")
        print(f"  ✅ GTFS Routes: {results['gtfs_data']['routes']}")
        print(f"  ✅ GTFS Stops: {results['gtfs_data']['stops']}")
        print(f"  ✅ GTFS Trips: {results['gtfs_data']['trips']:,}")

        if results['westchester_data']:
            print(f"  🏘️ Westchester Stations: {results['westchester_data']['stations_count']}")
            print(f"  🚊 Westchester Routes: {results['westchester_data']['routes_count']}")
            print(f"  📝 Westchester Stop Times: {results['westchester_data']['stop_times_count']:,}")

        if args.include_realtime and results.get('realtime_data'):
            print(f"  🚇 Real-time Entities: {results['realtime_data']['entity_count']}")

if __name__ == "__main__":
    main()