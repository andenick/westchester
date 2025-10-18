"""
Comprehensive Westchester County Web Scraper
Collects data from Westchester County government websites and related sources

This advanced scraper respects robots.txt, implements rate limiting,
and extracts structured data from multiple county sources.
"""

import requests
import json
import time
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
import csv


class WestchesterWebScraper:
    """Comprehensive Westchester County web scraper"""

    def __init__(self, output_dir: Path = None, delay: float = 2.0):
        """
        Initialize Westchester web scraper

        Args:
            output_dir: Directory to save scraped data
            delay: Delay between requests (seconds)
        """
        if output_dir is None:
            output_dir = Path(__file__).parent.parent.parent / "data" / "raw" / "web_scraped"

        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })

        # Westchester County websites to scrape
        self.target_websites = {
            "county_main": {
                "name": "Westchester County Main Website",
                "base_url": "https://www.westchestergov.com",
                "priority": 1
            },
            "planning_department": {
                "name": "Westchester Planning Department",
                "base_url": "https://planning.westchestergov.com",
                "priority": 1
            },
            "budget_finance": {
                "name": "Westchester Budget and Finance",
                "base_url": "https://finance.westchestergov.com",
                "priority": 1
            },
            "health_department": {
                "name": "Westchester Health Department",
                "base_url": "https://health.westchestergov.com",
                "priority": 2
            },
            "public_safety": {
                "name": "Westchester Public Safety",
                "base_url": "https://publicsafety.westchestergov.com",
                "priority": 2
            },
            "parks_recreation": {
                "name": "Westchester Parks and Recreation",
                "base_url": "https://parks.westchestergov.com",
                "priority": 2
            },
            "public_works": {
                "name": "Westchester Public Works",
                "base_url": "https://publicworks.westchestergov.com",
                "priority": 3
            },
            "gis": {
                "name": "Westchester GIS Open Data",
                "base_url": "https://gis.westchestergov.com",
                "priority": 1
            }
        }

        # Data patterns to look for
        self.data_patterns = {
            "demographics": [
                r"population",
                r"census",
                r"demographic",
                r"population\s+density",
                r"age\s+distribution",
                r"race\s+and\s+ethnicity"
            ],
            "housing": [
                r"housing",
                r"real\s+estate",
                r"property\s+values?",
                r"median\s+home",
                r"rental\s+rates?",
                r"housing\s+units"
            ],
            "economic": [
                r"employment",
                r"unemployment",
                r"income",
                r"business",
                r"economic",
                r"industry",
                r"wage"
            ],
            "transportation": [
                r"transit",
                r"traffic",
                r"commuting",
                r"transportation",
                r"metro[-\s]?north",
                r"bus",
                r"rail"
            ],
            "environmental": [
                r"environment",
                r"air\s+quality",
                r"water\s+quality",
                r"brownfield",
                r"hazardous",
                r"sustainability"
            ],
            "education": [
                r"school",
                r"education",
                r"student",
                r"graduation",
                r"enrollment"
            ],
            "health": [
                r"health",
                r"hospital",
                r"clinic",
                r"disease",
                r"vaccination",
                r"mortality"
            ],
            "public_safety": [
                r"crime",
                r"police",
                r"fire",
                r"emergency",
                r"safety",
                r"arrest"
            ]
        }

        # File types to look for
        self.target_file_types = [
            ".pdf", ".csv", ".xlsx", ".xls", ".json", ".xml", ".txt", ".doc", ".docx"
        ]

        # Track scraped URLs to avoid duplicates
        self.scraped_urls = set()
        self.robots_cache = {}

    def check_robots_txt(self, url: str) -> bool:
        """
        Check if scraping is allowed by robots.txt

        Args:
            url: URL to check

        Returns:
            True if scraping is allowed
        """
        try:
            parsed = urlparse(url)
            robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"

            if robots_url in self.robots_cache:
                return self.robots_cache[robots_url]

            rp = RobotFileParser()
            rp.set_url(robots_url)

            try:
                rp.read()
                can_fetch = rp.can_fetch(self.session.headers['User-Agent'], url)
                self.robots_cache[robots_url] = can_fetch
                return can_fetch
            except:
                # If robots.txt can't be read, assume it's okay
                self.robots_cache[robots_url] = True
                return True

        except Exception as e:
            print(f"[WARNING] Could not check robots.txt for {url}: {e}")
            return True

    def make_request(self, url: str, timeout: int = 30) -> Optional[requests.Response]:
        """
        Make HTTP request with rate limiting and error handling

        Args:
            url: URL to request
            timeout: Request timeout in seconds

        Returns:
            Response object or None if failed
        """
        if not self.check_robots_txt(url):
            print(f"[BLOCKED] robots.txt disallows scraping: {url}")
            return None

        if url in self.scraped_urls:
            print(f"[SKIP] Already scraped: {url}")
            return None

        try:
            # Rate limiting
            time.sleep(self.delay)

            print(f"[REQUESTING] {url}")
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()

            self.scraped_urls.add(url)
            return response

        except requests.RequestException as e:
            print(f"[ERROR] Failed to fetch {url}: {e}")
            return None

    def extract_links(self, response: requests.Response, base_url: str) -> List[str]:
        """
        Extract relevant links from HTML response

        Args:
            response: HTTP response
            base_url: Base URL for resolving relative links

        Returns:
            List of relevant links
        """
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            links = []

            # Extract all links
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(base_url, href)

                # Filter for relevant links
                if self.is_relevant_link(full_url, link.get_text(), base_url):
                    links.append(full_url)

            return links

        except ImportError:
            print("[WARNING] BeautifulSoup not available. Install with: pip install beautifulsoup4")
            return []
        except Exception as e:
            print(f"[ERROR] Failed to extract links: {e}")
            return []

    def is_relevant_link(self, url: str, link_text: str, base_url: str) -> bool:
        """
        Check if a link is relevant to our data collection goals

        Args:
            url: Full URL
            link_text: Link text
            base_url: Base URL

        Returns:
            True if link is relevant
        """
        url_lower = url.lower()
        text_lower = link_text.lower()

        # Skip external links and common non-data pages
        external_domains = ["facebook.com", "twitter.com", "instagram.com", "youtube.com", "linkedin.com"]
        if any(domain in url_lower for domain in external_domains):
            return False

        # Skip common non-data pages
        skip_patterns = [
            r"contact", r"about", r"help", r"faq", r"login", r"register",
            r"privacy", r"terms", r"careers", r"jobs", r"news", r"events"
        ]

        for pattern in skip_patterns:
            if re.search(pattern, url_lower) or re.search(pattern, text_lower):
                return False

        # Prioritize links that match our data patterns
        for category, patterns in self.data_patterns.items():
            for pattern in patterns:
                if re.search(pattern, url_lower) or re.search(pattern, text_lower):
                    return True

        # Prioritize file downloads
        if any(url_lower.endswith(ext) for ext in self.target_file_types):
            return True

        # Prioritize department pages
        dept_keywords = ["department", "dept", "division", "office", "bureau"]
        if any(keyword in url_lower for keyword in dept_keywords):
            return True

        # Prioritize data and reports
        data_keywords = ["data", "reports", "statistics", "analytics", "metrics"]
        if any(keyword in url_lower for keyword in data_keywords):
            return True

        return False

    def scrape_website(self, website_key: str, website_info: Dict, max_pages: int = 50) -> Dict:
        """
        Scrape a specific website for data

        Args:
            website_key: Website identifier
            website_info: Website configuration
            max_pages: Maximum pages to scrape

        Returns:
            Scraping results
        """
        print(f"\n{'='*60}")
        print(f"SCRAPING: {website_info['name']}")
        print(f"URL: {website_info['base_url']}")
        print(f"{'='*60}")

        results = {
            "website_key": website_key,
            "website_name": website_info["name"],
            "base_url": website_info["base_url"],
            "scraped_pages": [],
            "downloaded_files": [],
            "extracted_data": {},
            "errors": [],
            "scraping_timestamp": datetime.now().isoformat()
        }

        try:
            # Start with the main page
            main_response = self.make_request(website_info["base_url"])
            if not main_response:
                results["errors"].append("Failed to fetch main page")
                return results

            # Extract links from main page
            links = self.extract_links(main_response, website_info["base_url"])
            print(f"[INFO] Found {len(links)} relevant links")

            # Add the main page to the queue
            queue = [(website_info["base_url"], "main_page", 0)]
            processed_urls = set()

            # BFS scraping with priority
            page_count = 0
            while queue and page_count < max_pages:
                url, context, depth = queue.pop(0)

                if url in processed_urls:
                    continue

                processed_urls.add(url)
                page_count += 1

                print(f"\n[PAGE {page_count}/{max_pages}] Scraping: {url}")
                print(f"Context: {context}, Depth: {depth}")

                # Scrape the page
                page_result = self.scrape_page(url, context, website_info["base_url"])
                results["scraped_pages"].append(page_result)

                # Extract new links (limit depth)
                if depth < 3 and page_count < max_pages - 10:  # Leave room for prioritized links
                    response = self.make_request(url)
                    if response:
                        new_links = self.extract_links(response, website_info["base_url"])

                        # Prioritize file downloads
                        file_links = [link for link in new_links
                                    if any(link.lower().endswith(ext) for ext in self.target_file_types)]
                        other_links = [link for link in new_links if link not in file_links]

                        # Add file links first
                        for link in file_links[:5]:  # Limit file links per page
                            if link not in processed_urls:
                                queue.append((link, f"file_download", depth + 1))

                        # Add other links
                        for link in other_links[:10]:  # Limit other links per page
                            if link not in processed_urls:
                                queue.append((link, "linked_page", depth + 1))

                # Rate limiting
                time.sleep(self.delay)

        except Exception as e:
            error_msg = f"Scraping failed: {str(e)}"
            results["errors"].append(error_msg)
            print(f"[ERROR] {error_msg}")

        # Create summary
        results["summary"] = {
            "total_pages_scraped": len(results["scraped_pages"]),
            "total_files_downloaded": len(results["downloaded_files"]),
            "data_categories_found": list(results["extracted_data"].keys()),
            "errors_count": len(results["errors"])
        }

        print(f"\n[COMPLETE] {website_info['name']}")
        print(f"Pages scraped: {results['summary']['total_pages_scraped']}")
        print(f"Files downloaded: {results['summary']['total_files_downloaded']}")
        print(f"Data categories: {results['summary']['data_categories_found']}")
        print(f"Errors: {results['summary']['errors_count']}")

        return results

    def scrape_page(self, url: str, context: str, base_url: str) -> Dict:
        """
        Scrape individual page for data

        Args:
            url: Page URL
            context: Page context
            base_url: Base URL

        Returns:
            Page scraping results
        """
        response = self.make_request(url)
        if not response:
            return {"url": url, "error": "Failed to fetch page"}

        page_result = {
            "url": url,
            "context": context,
            "status_code": response.status_code,
            "content_type": response.headers.get('content-type', ''),
            "content_length": len(response.content),
            "extracted_data": {},
            "downloaded_files": [],
            "scraped_timestamp": datetime.now().isoformat()
        }

        try:
            content_type = response.headers.get('content-type', '').lower()

            if 'pdf' in content_type:
                # Handle PDF files
                file_result = self.save_downloaded_file(response, url, "pdf")
                page_result["downloaded_files"].append(file_result)
                print(f"     [PDF] Downloaded: {file_result['filename']}")

            elif any(x in content_type for x in ['excel', 'spreadsheet', 'xls']):
                # Handle Excel files
                file_result = self.save_downloaded_file(response, url, "excel")
                page_result["downloaded_files"].append(file_result)
                print(f"     [EXCEL] Downloaded: {file_result['filename']}")

            elif 'csv' in content_type:
                # Handle CSV files
                file_result = self.save_downloaded_file(response, url, "csv")
                page_result["downloaded_files"].append(file_result)
                print(f"     [CSV] Downloaded: {file_result['filename']}")

            elif 'json' in content_type:
                # Handle JSON files
                try:
                    data = response.json()
                    json_result = self.process_json_data(data, url)
                    page_result["extracted_data"].update(json_result)
                    print(f"     [JSON] Processed {len(data)} records")
                except:
                    # Save as file if can't parse
                    file_result = self.save_downloaded_file(response, url, "json")
                    page_result["downloaded_files"].append(file_result)
                    print(f"     [JSON] Downloaded: {file_result['filename']}")

            elif 'html' in content_type or 'text' in content_type:
                # Handle HTML/text pages
                page_data = self.extract_text_data(response.text, url)
                page_result["extracted_data"].update(page_data)

                # Look for data tables
                tables = self.extract_tables(response.text, url)
                if tables:
                    page_result["extracted_data"]["tables"] = tables
                    print(f"     [HTML] Found {len(tables)} data tables")

            else:
                # Save unknown file types
                file_result = self.save_downloaded_file(response, url, "binary")
                page_result["downloaded_files"].append(file_result)
                print(f"     [FILE] Downloaded: {file_result['filename']}")

        except Exception as e:
            error_msg = f"Failed to process page content: {str(e)}"
            page_result["error"] = error_msg
            print(f"     [ERROR] {error_msg}")

        return page_result

    def save_downloaded_file(self, response: requests.Response, url: str, file_type: str) -> Dict:
        """
        Save downloaded file to disk

        Args:
            response: HTTP response
            url: Source URL
            file_type: Type of file

        Returns:
            File metadata
        """
        try:
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            parsed_url = urlparse(url)
            path_part = parsed_url.path.strip('/').replace('/', '_')[:50]

            if not path_part:
                path_part = "downloaded"

            # Get file extension
            if '.' in parsed_url.path:
                extension = '.' + parsed_url.path.split('.')[-1].lower()
            else:
                extension = self._get_extension_from_content_type(response.headers.get('content-type', ''))

            filename = f"{timestamp}_{path_part}{extension}"
            filepath = self.output_dir / filename

            # Save file
            with open(filepath, 'wb') as f:
                f.write(response.content)

            return {
                "filename": filename,
                "filepath": str(filepath),
                "file_type": file_type,
                "size_bytes": len(response.content),
                "content_type": response.headers.get('content-type', ''),
                "source_url": url,
                "download_timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "error": f"Failed to save file: {str(e)}",
                "source_url": url,
                "file_type": file_type
            }

    def _get_extension_from_content_type(self, content_type: str) -> str:
        """Get file extension from content type"""
        content_type = content_type.lower()

        if 'pdf' in content_type:
            return '.pdf'
        elif 'excel' in content_type or 'spreadsheet' in content_type:
            return '.xlsx'
        elif 'csv' in content_type:
            return '.csv'
        elif 'json' in content_type:
            return '.json'
        elif 'xml' in content_type:
            return '.xml'
        elif 'text' in content_type:
            return '.txt'
        elif 'word' in content_type:
            return '.docx'
        else:
            return '.bin'

    def process_json_data(self, data: List[Dict], url: str) -> Dict:
        """
        Process JSON data for Westchester information

        Args:
            data: JSON data
            url: Source URL

        Returns:
            Processed data
        """
        processed = {
            "record_count": len(data) if isinstance(data, list) else 1,
            "source_url": url,
            "data_type": "json",
            "westchester_records": [],
            "metadata": {}
        }

        if isinstance(data, list):
            # Filter for Westchester records
            westchester_records = self._filter_westchester_records(data)
            processed["westchester_records"] = westchester_records
            processed["westchester_count"] = len(westchester_records)

        return processed

    def _filter_westchester_records(self, data: List[Dict]) -> List[Dict]:
        """Filter records for Westchester County"""
        westchester_records = []
        westchester_keywords = ["westchester", "yonkers", "white plains", "new rochelle", "mount vernon"]

        for record in data:
            # Check various fields for Westchester
            record_text = ' '.join(str(v) for v in record.values()).lower()

            if any(keyword in record_text for keyword in westchester_keywords):
                westchester_records.append(record)

        return westchester_records

    def extract_text_data(self, html_text: str, url: str) -> Dict:
        """
        Extract structured data from HTML text

        Args:
            html_text: HTML content
            url: Source URL

        Returns:
            Extracted data
        """
        extracted = {
            "source_url": url,
            "data_type": "html_text",
            "extracted_numbers": [],
            "extracted_dates": [],
            "data_indicators": {}
        }

        try:
            # Extract numbers (potential data values)
            number_pattern = r'\$?[0-9,]+(?:\.[0-9]+)?(?:\s*(?:million|billion|thousand|percent|%)|%)?'
            numbers = re.findall(number_pattern, html_text)
            extracted["extracted_numbers"] = numbers[:20]  # Limit to first 20

            # Extract dates
            date_pattern = r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b'
            dates = re.findall(date_pattern, html_text)
            extracted["extracted_dates"] = dates[:10]  # Limit to first 10

            # Look for data indicators
            for category, patterns in self.data_patterns.items():
                matches = 0
                for pattern in patterns:
                    matches += len(re.findall(pattern, html_text, re.IGNORECASE))

                if matches > 0:
                    extracted["data_indicators"][category] = matches

        except Exception as e:
            extracted["error"] = f"Failed to extract text data: {str(e)}"

        return extracted

    def extract_tables(self, html_text: str, url: str) -> List[Dict]:
        """
        Extract data tables from HTML

        Args:
            html_text: HTML content
            url: Source URL

        Returns:
            List of extracted tables
        """
        tables = []

        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_text, 'html.parser')

            for i, table in enumerate(soup.find_all('table')):
                table_data = {
                    "table_index": i,
                    "source_url": url,
                    "rows": [],
                    "headers": []
                }

                # Extract headers
                header_row = table.find('tr')
                if header_row:
                    headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
                    table_data["headers"] = headers

                # Extract data rows
                for row in table.find_all('tr')[1:]:  # Skip header row
                    cells = [td.get_text(strip=True) for td in row.find_all(['td', 'th'])]
                    if cells:
                        table_data["rows"].append(cells)

                if table_data["rows"]:
                    tables.append(table_data)

        except ImportError:
            print("[WARNING] BeautifulSoup not available for table extraction")
        except Exception as e:
            print(f"[ERROR] Failed to extract tables: {e}")

        return tables

    def run_comprehensive_scraping(self, max_pages_per_site: int = 30) -> Dict:
        """
        Run comprehensive scraping of all target websites

        Args:
            max_pages_per_site: Maximum pages to scrape per website

        Returns:
            Comprehensive scraping results
        """
        print("=" * 80)
        print("COMPREHENSIVE WESTCHESTER COUNTY WEB SCRAPING")
        print("=" * 80)
        print(f"Websites to scrape: {len(self.target_websites)}")
        print(f"Max pages per site: {max_pages_per_site}")
        print(f"Output directory: {self.output_dir}")
        print()

        all_results = {
            "scraping_session": {
                "start_time": datetime.now().isoformat(),
                "max_pages_per_site": max_pages_per_site,
                "total_websites": len(self.target_websites)
            },
            "website_results": {},
            "summary": {},
            "all_downloaded_files": [],
            "errors": []
        }

        total_files = 0
        total_pages = 0

        # Sort websites by priority
        sorted_websites = sorted(self.target_websites.items(),
                               key=lambda x: x[1]['priority'])

        for website_key, website_info in sorted_websites:
            print(f"\n{'='*60}")
            print(f"SCRAPING WEBSITE {list(sorted_websites).index((website_key, website_info)) + 1}/{len(sorted_websites)}")
            print(f"{'='*60}")

            try:
                result = self.scrape_website(website_key, website_info, max_pages_per_site)
                all_results["website_results"][website_key] = result

                total_pages += result["summary"]["total_pages_scraped"]
                total_files += result["summary"]["total_files_downloaded"]

                # Add downloaded files to master list
                for page in result["scraped_pages"]:
                    all_results["all_downloaded_files"].extend(page.get("downloaded_files", []))

                # Add errors
                all_results["errors"].extend(result.get("errors", []))

            except Exception as e:
                error_msg = f"Failed to scrape {website_info['name']}: {str(e)}"
                all_results["errors"].append(error_msg)
                print(f"[ERROR] {error_msg}")

        # Create comprehensive summary
        all_results["summary"] = {
            "end_time": datetime.now().isoformat(),
            "total_pages_scraped": total_pages,
            "total_files_downloaded": total_files,
            "websites_scraped": len(all_results["website_results"]),
            "total_errors": len(all_results["errors"]),
            "data_categories_found": set()
        }

        # Collect all data categories
        for website_result in all_results["website_results"].values():
            categories = website_result.get("summary", {}).get("data_categories_found", [])
            all_results["summary"]["data_categories_found"].update(categories)

        all_results["summary"]["data_categories_found"] = list(all_results["summary"]["data_categories_found"])

        # Save comprehensive results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = self.output_dir / f"comprehensive_scraping_results_{timestamp}.json"

        with open(results_file, 'w') as f:
            json.dump(all_results, f, indent=2)

        print("\n" + "=" * 80)
        print("COMPREHENSIVE SCRAPING COMPLETE!")
        print("=" * 80)
        print(f"Websites scraped: {all_results['summary']['websites_scraped']}")
        print(f"Total pages: {all_results['summary']['total_pages_scraped']}")
        print(f"Total files downloaded: {all_results['summary']['total_files_downloaded']}")
        print(f"Data categories found: {all_results['summary']['data_categories_found']}")
        print(f"Total errors: {all_results['summary']['total_errors']}")
        print(f"Results saved to: {results_file}")
        print(f"Files saved to: {self.output_dir}")

        return all_results


def main():
    """Command-line interface for web scraping"""
    import os

    print("=" * 80)
    print("WESTCHESTER COUNTY COMPREHENSIVE WEB SCRAPER")
    print("Collects data from Westchester County government websites")
    print("=" * 80)
    print()

    # Get configuration
    delay_input = input("Delay between requests in seconds (default 2.0): ").strip()
    try:
        delay = float(delay_input) if delay_input else 2.0
        if delay < 0.5:
            print("Delay too short. Using 2.0 seconds.")
            delay = 2.0
    except ValueError:
        print("Invalid input. Using 2.0 seconds.")
        delay = 2.0

    max_pages_input = input("Maximum pages per website (default 30): ").strip()
    try:
        max_pages = int(max_pages_input) if max_pages_input else 30
        if max_pages < 1:
            print("Invalid input. Using 30 pages.")
            max_pages = 30
    except ValueError:
        print("Invalid input. Using 30 pages.")
        max_pages = 30

    # Run scraper
    scraper = WestchesterWebScraper(delay=delay)
    results = scraper.run_comprehensive_scraping(max_pages_per_site=max_pages)

    print()
    if results["summary"]["total_errors"] == 0:
        print("[SUCCESS] Scraping completed without errors!")
    else:
        print(f"[COMPLETED] Scraping completed with {results['summary']['total_errors']} errors.")
        print("Check the results file for error details.")


if __name__ == "__main__":
    main()