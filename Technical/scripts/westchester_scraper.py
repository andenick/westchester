#!/usr/bin/env python3
"""
Westchester County Data Platform - Web Scraping Framework

Westchester County website data scraper.

Target Sites:
- westchestergov.com (Budget Office)
- finance.westchestergov.com (Tax data)
- westchestergov.com/transportation (Transit data)
- planning.westchestergov.com (Planning documents)

Features:
- Rate limiting and respectful scraping
- PDF download and processing
- Data structure normalization
- Error handling and retries

Target: 25% of files (17 documents) automated scraping
Dependencies: requests, beautifulsoup4, selenium, pandas
"""

import os
import sys
import json
import time
import logging
import random
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from urllib.parse import urljoin, urlparse
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Web scraping libraries
import requests
from bs4 import BeautifulSoup
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.action_chains import ActionChains
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    logging.warning("Selenium not available - JavaScript-heavy sites may not scrape well")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('westchester_scraping.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WestchesterWebScraper:
    """
    Specialized web scraper for Westchester County government websites.
    Respects robots.txt, implements rate limiting, and handles various data formats.
    """

    def __init__(self, output_dir: str = None, respect_robots: bool = True):
        self.output_dir = Path(output_dir or "data/processed/web_scraping")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.respect_robots = respect_robots

        # User agent to identify the scraper
        self.user_agent = (
            "Westchester-Data-Platform/1.0 (Educational/Research Purpose; "
            "Data collection for public analytics; +info@westchester-data.org)"
        )

        # Session for HTTP requests
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })

        # Rate limiting: respectful delays between requests
        self.min_delay = 2.0  # seconds
        self.max_delay = 5.0  # seconds
        self.last_request_time = {}

        # Westchester-specific target sites and data patterns
        self.target_sites = {
            'budget_office': {
                'base_url': 'https://www.westchestergov.com',
                'search_paths': [
                    '/budget',
                    '/departments/budget',
                    '/finance/budget',
                    '/county-executive/budget'
                ],
                'file_patterns': [
                    'budget', 'adopted', 'proposed', 'capital', 'financial'
                ],
                'data_types': ['budget_reports'],
                'priority': 1
            },
            'tax_finance': {
                'base_url': 'https://finance.westchestergov.com',
                'search_paths': [
                    '/tax-levy',
                    '/property-tax',
                    '/assessment',
                    '/tax-rates'
                ],
                'file_patterns': [
                    'tax', 'levy', 'assessment', 'rate', 'property'
                ],
                'data_types': ['tax_levy'],
                'priority': 1
            },
            'transportation': {
                'base_url': 'https://www.westchestergov.com',
                'search_paths': [
                    '/transportation',
                    '/public-works/transportation',
                    '/metro-north',
                    '/bus'
                ],
                'file_patterns': [
                    'transit', 'transportation', 'metro', 'bus', 'ridership'
                ],
                'data_types': ['transit'],
                'priority': 2
            },
            'planning': {
                'base_url': 'https://planning.westchestergov.com',
                'search_paths': [
                    '/infrastructure',
                    '/capital-improvement',
                    '/development',
                    '/projects'
                ],
                'file_patterns': [
                    'infrastructure', 'capital', 'improvement', 'project', 'development'
                ],
                'data_types': ['infrastructure'],
                'priority': 2
            },
            'historical': {
                'base_url': 'https://www.westchestergov.com',
                'search_paths': [
                    '/demographics',
                    '/economic-development',
                    '/statistics',
                    '/research'
                ],
                'file_patterns': [
                    'historical', 'trend', 'demographic', 'economic', 'statistics'
                ],
                'data_types': ['historical'],
                'priority': 3
            }
        }

        # File type priorities (PDFs preferred, but also accept Excel, CSV)
        self.file_priorities = {
            '.pdf': 10,
            '.xlsx': 8,
            '.xls': 7,
            '.csv': 6,
            '.doc': 4,
            '.docx': 4,
            '.html': 2,
            '.htm': 2
        }

        # Scraping statistics
        self.scraping_stats = {
            'total_urls_visited': 0,
            'files_downloaded': 0,
            'failed_downloads': 0,
            'pages_scraped': 0,
            'sites_scraped': 0,
            'processing_time': 0,
            'files_by_type': {},
            'files_by_category': {cat: 0 for cat in self.target_sites.keys()},
            'robots_txt_respected': 0
        }

    def check_robots_txt(self, domain: str) -> Dict[str, Any]:
        """
        Check and parse robots.txt for the given domain.
        """
        robots_url = f"https://{domain}/robots.txt"

        try:
            response = self.session.get(robots_url, timeout=10)
            if response.status_code == 200:
                content = response.text
                # Parse robots.txt (basic implementation)
                disallowed_paths = []
                for line in content.split('\n'):
                    if line.startswith('Disallow:'):
                        path = line.replace('Disallow:', '').strip()
                        if path:
                            disallowed_paths.append(path)

                logger.info(f"Found robots.txt for {domain} with {len(disallowed_paths)} disallow rules")
                self.scraping_stats['robots_txt_respected'] += 1

                return {
                    'allowed': True,
                    'disallowed_paths': disallowed_paths,
                    'content': content
                }
            else:
                logger.info(f"No robots.txt found for {domain}")
                return {'allowed': True, 'disallowed_paths': [], 'content': None}

        except Exception as e:
            logger.warning(f"Error checking robots.txt for {domain}: {str(e)}")
            return {'allowed': True, 'disallowed_paths': [], 'content': None}

    def is_url_allowed(self, url: str, robots_info: Dict[str, Any]) -> bool:
        """
        Check if URL is allowed according to robots.txt rules.
        """
        if not self.respect_robots or not robots_info.get('disallowed_paths'):
            return True

        parsed_url = urlparse(url)
        path = parsed_url.path

        for disallowed in robots_info['disallowed_paths']:
            if path.startswith(disallowed):
                logger.warning(f"URL disallowed by robots.txt: {url}")
                return False

        return True

    def respect_rate_limit(self, domain: str):
        """
        Implement rate limiting to be respectful to web servers.
        """
        current_time = time.time()

        if domain in self.last_request_time:
            elapsed = current_time - self.last_request_time[domain]
            delay = random.uniform(self.min_delay, self.max_delay)

            if elapsed < delay:
                sleep_time = delay - elapsed
                logger.debug(f"Rate limiting: waiting {sleep_time:.2f}s for {domain}")
                time.sleep(sleep_time)

        self.last_request_time[domain] = time.time()

    def make_request(self, url: str, timeout: int = 30) -> Optional[requests.Response]:
        """
        Make HTTP request with proper error handling and rate limiting.
        """
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc

            # Respect rate limiting
            self.respect_rate_limit(domain)

            logger.info(f"Requesting: {url}")
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()

            self.scraping_stats['total_urls_visited'] += 1
            return response

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {url}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error requesting {url}: {str(e)}")
            return None

    def extract_links(self, response: requests.Response, base_url: str) -> List[Dict[str, Any]]:
        """
        Extract relevant links from HTML response.
        """
        links = []

        try:
            soup = BeautifulSoup(response.content, 'html.parser')

            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(base_url, href)

                # Clean up URL
                full_url = full_url.split('#')[0]  # Remove fragments

                # Get link text
                link_text = link.get_text(strip=True)

                # Get file extension if any
                parsed = urlparse(full_url)
                file_ext = Path(parsed.path).suffix.lower()

                links.append({
                    'url': full_url,
                    'text': link_text,
                    'file_extension': file_ext,
                    'is_file': bool(file_ext)
                })

        except Exception as e:
            logger.error(f"Error extracting links from {base_url}: {str(e)}")

        return links

    def filter_relevant_links(self, links: List[Dict[str, Any]], site_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Filter links based on relevance to target data types.
        """
        relevant_links = []
        file_patterns = [pattern.lower() for pattern in site_config['file_patterns']]

        for link in links:
            # Check if link text or URL contains relevant keywords
            text_lower = link['text'].lower()
            url_lower = link['url'].lower()

            # Calculate relevance score
            score = 0

            # Check file patterns
            for pattern in file_patterns:
                if pattern in text_lower or pattern in url_lower:
                    score += 10

            # Bonus for file downloads
            if link['is_file']:
                file_priority = self.file_priorities.get(link['file_extension'], 0)
                if file_priority > 0:
                    score += file_priority

            # Only include links with some relevance
            if score > 0:
                link['relevance_score'] = score
                relevant_links.append(link)

        # Sort by relevance score
        relevant_links.sort(key=lambda x: x['relevance_score'], reverse=True)

        return relevant_links

    def download_file(self, link_info: Dict[str, Any], category: str) -> Optional[Path]:
        """
        Download file from link and save to appropriate directory.
        """
        url = link_info['url']

        try:
            response = self.make_request(url)
            if not response:
                return None

            # Determine filename
            content_disposition = response.headers.get('content-disposition', '')
            if 'filename=' in content_disposition:
                filename = content_disposition.split('filename=')[-1].strip('"')
            else:
                # Extract filename from URL
                parsed_url = urlparse(url)
                filename = Path(parsed_url.path).name

            if not filename:
                # Generate filename from link text
                safe_text = "".join(c for c in link_info['text'][:50] if c.isalnum() or c in (' ', '-', '_')).rstrip()
                filename = f"{safe_text}{link_info['file_extension']}"

            # Create category directory
            category_dir = self.output_dir / category
            category_dir.mkdir(exist_ok=True)

            # Save file
            filepath = category_dir / filename
            with open(filepath, 'wb') as f:
                f.write(response.content)

            logger.info(f"Downloaded: {filename} ({len(response.content)} bytes)")
            self.scraping_stats['files_downloaded'] += 1
            self.scraping_stats['files_by_type'][link_info['file_extension']] = \
                self.scraping_stats['files_by_type'].get(link_info['file_extension'], 0) + 1
            self.scraping_stats['files_by_category'][category] += 1

            return filepath

        except Exception as e:
            logger.error(f"Error downloading file from {url}: {str(e)}")
            self.scraping_stats['failed_downloads'] += 1
            return None

    def scrape_page_content(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Scrape text content from a page for data extraction.
        """
        try:
            response = self.make_request(url)
            if not response:
                return None

            soup = BeautifulSoup(response.content, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Extract text content
            text = soup.get_text()

            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)

            # Extract tables
            tables = []
            for table in soup.find_all('table'):
                try:
                    df = pd.read_html(str(table))[0]
                    tables.append({
                        'html': str(table),
                        'data': df.to_dict('records'),
                        'columns': list(df.columns)
                    })
                except:
                    continue

            return {
                'url': url,
                'title': soup.title.string if soup.title else '',
                'text_content': text,
                'tables': tables,
                'content_length': len(text)
            }

        except Exception as e:
            logger.error(f"Error scraping page content from {url}: {str(e)}")
            return None

    def scrape_site(self, site_key: str, site_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Scrape a complete Westchester County website section.
        """
        start_time = time.time()
        base_url = site_config['base_url']

        logger.info(f"\n{'='*60}")
        logger.info(f"Scraping site: {site_key}")
        logger.info(f"Base URL: {base_url}")
        logger.info(f"{'='*60}")

        # Check robots.txt
        domain = urlparse(base_url).netloc
        robots_info = self.check_robots_txt(domain)

        results = {
            'site_key': site_key,
            'base_url': base_url,
            'start_time': start_time,
            'pages_visited': [],
            'files_downloaded': [],
            'content_extracted': [],
            'errors': [],
            'summary': {
                'total_pages': 0,
                'total_files': 0,
                'total_content_items': 0,
                'processing_time': 0
            }
        }

        try:
            # Visit each search path
            for search_path in site_config['search_paths']:
                search_url = urljoin(base_url, search_path)

                if not self.is_url_allowed(search_url, robots_info):
                    logger.warning(f"Skipping disallowed URL: {search_url}")
                    continue

                logger.info(f"Searching path: {search_url}")

                response = self.make_request(search_url)
                if not response:
                    results['errors'].append(f"Failed to access {search_url}")
                    continue

                # Extract links from page
                links = self.extract_links(response, search_url)
                logger.info(f"Found {len(links)} links on {search_url}")

                # Filter relevant links
                relevant_links = self.filter_relevant_links(links, site_config)
                logger.info(f"Found {len(relevant_links)} relevant links")

                # Download top relevant files
                max_downloads = 10  # Limit per page to be respectful
                for link in relevant_links[:max_downloads]:
                    if link['is_file']:
                        filepath = self.download_file(link, site_key)
                        if filepath:
                            results['files_downloaded'].append({
                                'url': link['url'],
                                'filename': filepath.name,
                                'size': filepath.stat().st_size,
                                'type': link['file_extension']
                            })
                    else:
                        # Scrape page content for non-file links
                        content = self.scrape_page_content(link['url'])
                        if content and content['content_length'] > 500:  # Only keep substantial content
                            results['content_extracted'].append(content)

                results['pages_visited'].append(search_url)
                self.scraping_stats['pages_scraped'] += 1

                # Respect rate limiting between pages
                time.sleep(random.uniform(2, 4))

        except Exception as e:
            logger.error(f"Error scraping site {site_key}: {str(e)}")
            results['errors'].append(str(e))

        finally:
            # Calculate summary
            end_time = time.time()
            results['end_time'] = end_time
            results['summary']['total_pages'] = len(results['pages_visited'])
            results['summary']['total_files'] = len(results['files_downloaded'])
            results['summary']['total_content_items'] = len(results['content_extracted'])
            results['summary']['processing_time'] = end_time - start_time

            self.scraping_stats['sites_scraped'] += 1

            logger.info(f"Completed scraping {site_key}: "
                       f"{results['summary']['total_files']} files, "
                       f"{results['summary']['total_pages']} pages")

        return results

    def save_scraping_results(self, results: Dict[str, Any]) -> None:
        """
        Save scraping results to files.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        try:
            # Save detailed JSON results
            results_file = self.output_dir / f"scraping_results_{timestamp}.json"
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False, default=str)

            # Save summary statistics
            summary_file = self.output_dir / f"scraping_summary_{timestamp}.json"
            summary_data = {
                'timestamp': timestamp,
                'statistics': self.scraping_stats,
                'summary': self.generate_summary_stats(results)
            }

            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary_data, f, indent=2, ensure_ascii=False, default=str)

            # Generate human-readable report
            report_file = self.output_dir / f"scraping_report_{timestamp}.md"
            report_content = self.generate_human_readable_report(results)

            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report_content)

            logger.info(f"Scraping results saved:")
            logger.info(f"  - Detailed results: {results_file}")
            logger.info(f"  - Summary statistics: {summary_file}")
            logger.info(f"  - Human-readable report: {report_file}")

        except Exception as e:
            logger.error(f"Error saving scraping results: {str(e)}")

    def generate_summary_stats(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary statistics from scraping results"""

        summary = {
            'total_sites_scraped': len(results.get('site_results', [])),
            'total_files_downloaded': 0,
            'total_pages_scraped': 0,
            'total_content_extracted': 0,
            'file_types': {},
            'categories': {},
            'processing_time': 0,
            'success_rate': 0
        }

        # Aggregate statistics from all sites
        for site_result in results.get('site_results', []):
            site_summary = site_result.get('summary', {})
            summary['total_files_downloaded'] += site_summary.get('total_files', 0)
            summary['total_pages_scraped'] += site_summary.get('total_pages', 0)
            summary['total_content_extracted'] += site_summary.get('total_content_items', 0)
            summary['processing_time'] += site_summary.get('processing_time', 0)

            # Count file types
            for file_info in site_result.get('files_downloaded', []):
                file_type = file_info.get('type', 'unknown')
                summary['file_types'][file_type] = summary['file_types'].get(file_type, 0) + 1

            # Count by site category
            site_key = site_result.get('site_key', 'unknown')
            summary['categories'][site_key] = summary['categories'].get(site_key, 0) + 1

        # Calculate success rate (files downloaded per page visited)
        if summary['total_pages_scraped'] > 0:
            summary['success_rate'] = summary['total_files_downloaded'] / summary['total_pages_scraped']

        return summary

    def generate_human_readable_report(self, results: Dict[str, Any]) -> str:
        """Generate human-readable scraping report"""

        summary_stats = self.generate_summary_stats(results)

        report = []
        report.append("# Westchester County Web Scraping Report")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        # Executive Summary
        report.append("## Executive Summary")
        report.append(f"**Total Sites Scraped**: {summary_stats['total_sites_scraped']}")
        report.append(f"**Total Files Downloaded**: {summary_stats['total_files_downloaded']}")
        report.append(f"**Total Pages Scraped**: {summary_stats['total_pages_scraped']}")
        report.append(f"**Total Content Items Extracted**: {summary_stats['total_content_extracted']}")
        report.append(f"**Total Processing Time**: {summary_stats['processing_time']:.2f} seconds")
        report.append(f"**Overall Success Rate**: {summary_stats['success_rate']:.2f} files per page")
        report.append("")

        # Results by Site
        report.append("## Results by Site")
        for site_result in results.get('site_results', []):
            site_key = site_result.get('site_key', 'unknown')
            site_summary = site_result.get('summary', {})

            report.append(f"### {site_key.replace('_', ' ').title()}")
            report.append(f"- **Files Downloaded**: {site_summary.get('total_files', 0)}")
            report.append(f"- **Pages Visited**: {site_summary.get('total_pages', 0)}")
            report.append(f"- **Content Items**: {site_summary.get('total_content_items', 0)}")
            report.append(f"- **Processing Time**: {site_summary.get('processing_time', 0):.2f}s")

            # List downloaded files
            files = site_result.get('files_downloaded', [])
            if files:
                report.append("**Downloaded Files:**")
                for file_info in files[:5]:  # Show first 5 files
                    report.append(f"  - {file_info['filename']} ({file_info['size']:,} bytes)")
                if len(files) > 5:
                    report.append(f"  - ... and {len(files) - 5} more files")

            report.append("")

        # File Type Distribution
        report.append("## File Type Distribution")
        for file_type, count in summary_stats['file_types'].items():
            report.append(f"- **{file_type.upper()}**: {count} files")
        report.append("")

        # Scraping Statistics
        report.append("## Scraping Statistics")
        report.append(f"- **Total URLs Visited**: {self.scraping_stats['total_urls_visited']}")
        report.append(f"- **Failed Downloads**: {self.scraping_stats['failed_downloads']}")
        report.append(f"- **Robots.txt Files Respected**: {self.scraping_stats['robots_txt_respected']}")
        report.append(f"- **Average Delay Between Requests**: {self.scraping_stats.get('avg_delay', 0):.2f}s")
        report.append("")

        # Recommendations
        report.append("## Recommendations")

        success_rate = summary_stats['success_rate']
        if success_rate >= 2.0:
            report.append("✅ **Excellent scraping results!** Found plenty of relevant files.")
        elif success_rate >= 1.0:
            report.append("⚠️ **Good results.** Consider expanding search patterns for more files.")
        elif success_rate >= 0.5:
            report.append("⚠️ **Moderate results.** Review site structure for better file discovery.")
        else:
            report.append("❌ **Low success rate.** Manual review of sites may be needed.")

        report.append("")
        report.append("## Next Steps")
        report.append("1. Review downloaded files for relevance and quality")
        report.append("2. Process PDF files through the PDF extraction pipeline")
        report.append("3. Extract and clean tabular data from downloaded files")
        report.append("4. Integrate scraped data into main data processing pipeline")
        report.append("5. Schedule regular scraping cycles for updated data")

        return "\n".join(report)

    def run_full_scraping(self, max_sites: int = None) -> Dict[str, Any]:
        """
        Run complete scraping of all target Westchester County sites.
        """
        start_time = time.time()

        logger.info("Starting comprehensive Westchester County web scraping")
        logger.info(f"Target sites: {len(self.target_sites)}")

        # Sort sites by priority
        sorted_sites = sorted(
            self.target_sites.items(),
            key=lambda x: x[1]['priority']
        )

        # Limit sites if specified
        if max_sites:
            sorted_sites = sorted_sites[:max_sites]

        results = {
            'start_time': start_time,
            'scraping_config': {
                'respect_robots': self.respect_robots,
                'min_delay': self.min_delay,
                'max_delay': self.max_delay,
                'user_agent': self.user_agent
            },
            'site_results': [],
            'statistics': {},
            'errors': []
        }

        try:
            # Scrape each site
            for site_key, site_config in sorted_sites:
                try:
                    site_result = self.scrape_site(site_key, site_config)
                    results['site_results'].append(site_result)

                except Exception as e:
                    logger.error(f"Failed to scrape site {site_key}: {str(e)}")
                    results['errors'].append(f"Site {site_key}: {str(e)}")
                    continue

            # Calculate final statistics
            end_time = time.time()
            results['end_time'] = end_time
            results['total_processing_time'] = end_time - start_time
            results['statistics'] = self.scraping_stats
            results['statistics']['processing_time'] = end_time - start_time

            # Save results
            self.save_scraping_results(results)

            # Print summary
            logger.info(f"\n{'='*60}")
            logger.info("SCRAPING SUMMARY")
            logger.info(f"{'='*60}")
            logger.info(f"Sites scraped: {len(results['site_results'])}")
            logger.info(f"Files downloaded: {self.scraping_stats['files_downloaded']}")
            logger.info(f"Pages scraped: {self.scraping_stats['pages_scraped']}")
            logger.info(f"Processing time: {end_time - start_time:.2f}s")

            return results

        except Exception as e:
            logger.error(f"Critical error during scraping: {str(e)}")
            results['errors'].append(f"Critical error: {str(e)}")
            return results

def main():
    """Main function for command line usage"""
    import argparse

    parser = argparse.ArgumentParser(description='Westchester County Web Scraper')
    parser.add_argument('--output-dir', help='Output directory for scraped data')
    parser.add_argument('--max-sites', type=int, help='Maximum number of sites to scrape')
    parser.add_argument('--site', help='Scrape specific site only')
    parser.add_argument('--test-mode', action='store_true', help='Test mode: limited scraping')
    parser.add_argument('--no-robots', action='store_true', help='Ignore robots.txt (not recommended)')

    args = parser.parse_args()

    # Initialize scraper
    scraper = WestchesterWebScraper(
        output_dir=args.output_dir,
        respect_robots=not args.no_robots
    )

    if args.site:
        # Scrape single site
        if args.site not in scraper.target_sites:
            print(f"Error: Unknown site '{args.site}'")
            print(f"Available sites: {list(scraper.target_sites.keys())}")
            sys.exit(1)

        print(f"Scraping single site: {args.site}")
        site_config = scraper.target_sites[args.site]
        result = scraper.scrape_site(args.site, site_config)

        print(f"\nResults for {args.site}:")
        print(f"  Files downloaded: {result['summary']['total_files']}")
        print(f"  Pages scraped: {result['summary']['total_pages']}")
        print(f"  Processing time: {result['summary']['processing_time']:.2f}s")

    else:
        # Run full scraping
        print("Starting comprehensive Westchester County web scraping...")

        # Adjust for test mode
        max_sites = 2 if args.test_mode else args.max_sites

        results = scraper.run_full_scraping(max_sites=max_sites)

        # Print final summary
        stats = results['statistics']
        print(f"\n{'='*60}")
        print("FINAL SCRAPPING SUMMARY")
        print(f"{'='*60}")
        print(f"Sites processed: {stats['sites_scraped']}")
        print(f"Files downloaded: {stats['files_downloaded']}")
        print(f"Pages scraped: {stats['pages_scraped']}")
        print(f"Processing time: {stats['processing_time']:.2f}s")

        if stats['files_downloaded'] > 0:
            print(f"Files by type:")
            for file_type, count in stats['files_by_type'].items():
                print(f"  - {file_type}: {count}")

        print(f"\n📁 Results saved to: {scraper.output_dir}")

if __name__ == "__main__":
    main()