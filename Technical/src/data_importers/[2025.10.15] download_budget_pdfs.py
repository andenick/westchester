#!/usr/bin/env python3
"""
[2025.10.15] Westchester County Budget PDF Downloader

Automatically downloads budget PDF documents from Westchester County website
for years 2020-2025 to replace sample data in Budget dashboard.

Sources: westchestergov.com/county-budget
"""

import requests
from pathlib import Path
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class BudgetPDFDownloader:
    def __init__(self, output_dir: Path = None):
        if output_dir is None:
            base_dir = Path(__file__).parent.parent.parent
            self.output_dir = base_dir / "data" / "raw" / "manual_downloads" / "budgets"
        else:
            self.output_dir = output_dir

        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Budget PDF URLs (verified for 2025, pattern-based for 2020-2024)
        self.budget_urls = {
            '2025': {
                'operating': 'https://www.westchestergov.com/images/stories/budget/2025/2025-adopted-operating-budget---web-version.pdf',
                'special_districts': 'https://www.westchestergov.com/images/stories/budget/2025/2025-special-districts-adopted-budget.pdf',
                'capital': 'https://www.westchestergov.com/images/stories/budget/2025/westchester-county-2025-adopted-capital-budget.pdf',
            },
            '2024': {
                'operating': 'https://www.westchestergov.com/images/stories/budget/2024/2024-adopted-operating-budget.pdf',
                'special_districts': 'https://www.westchestergov.com/images/stories/budget/2024/2024-special-districts-adopted-budget.pdf',
                'capital': 'https://www.westchestergov.com/images/stories/budget/2024/westchester-county-2024-adopted-capital-budget.pdf',
            },
            '2023': {
                'operating': 'https://www.westchestergov.com/images/stories/budget/2023/2023-adopted-operating-budget.pdf',
                'special_districts': 'https://www.westchestergov.com/images/stories/budget/2023/2023-special-districts-adopted-budget.pdf',
                'capital': 'https://www.westchestergov.com/images/stories/budget/2023/westchester-county-2023-adopted-capital-budget.pdf',
            },
            '2022': {
                'operating': 'https://www.westchestergov.com/images/stories/budget/2022/2022-adopted-operating-budget.pdf',
                'special_districts': 'https://www.westchestergov.com/images/stories/budget/2022/2022-special-districts-adopted-budget.pdf',
                'capital': 'https://www.westchestergov.com/images/stories/budget/2022/westchester-county-2022-adopted-capital-budget.pdf',
            },
            '2021': {
                'operating': 'https://www.westchestergov.com/images/stories/budget/2021/2021-adopted-operating-budget.pdf',
                'special_districts': 'https://www.westchestergov.com/images/stories/budget/2021/2021-special-districts-adopted-budget.pdf',
                'capital': 'https://www.westchestergov.com/images/stories/budget/2021/westchester-county-2021-adopted-capital-budget.pdf',
            },
            '2020': {
                'operating': 'https://www.westchestergov.com/images/stories/budget/2020/2020-adopted-operating-budget.pdf',
                'special_districts': 'https://www.westchestergov.com/images/stories/budget/2020/2020-special-districts-adopted-budget.pdf',
                'capital': 'https://www.westchestergov.com/images/stories/budget/2020/westchester-county-2020-adopted-capital-budget.pdf',
            },
        }

    def download_pdf(self, url: str, filename: str) -> bool:
        """Download a single PDF file"""
        try:
            logger.info(f"   Downloading: {filename}")
            logger.info(f"   URL: {url}")

            response = requests.get(url, timeout=120, allow_redirects=True)

            # Check if we got a PDF
            content_type = response.headers.get('content-type', '')

            if response.status_code == 200:
                if 'pdf' in content_type.lower() or url.endswith('.pdf'):
                    output_path = self.output_dir / filename
                    with open(output_path, 'wb') as f:
                        f.write(response.content)

                    file_size = len(response.content) / (1024 * 1024)  # MB
                    logger.info(f"   ✅ Downloaded: {filename} ({file_size:.2f} MB)")
                    return True
                else:
                    logger.warning(f"   ⚠️ Not a PDF file (Content-Type: {content_type})")
                    return False
            elif response.status_code == 404:
                logger.warning(f"   ❌ Not Found (404): {filename}")
                return False
            else:
                logger.warning(f"   ❌ HTTP {response.status_code}: {filename}")
                return False

        except requests.exceptions.Timeout:
            logger.error(f"   ❌ Timeout: {filename}")
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"   ❌ Request failed: {e}")
            return False
        except Exception as e:
            logger.error(f"   ❌ Unexpected error: {e}")
            return False

    def download_all(self):
        """Download all budget PDFs"""
        logger.info("="*80)
        logger.info("WESTCHESTER COUNTY BUDGET PDF DOWNLOADER")
        logger.info("="*80)
        logger.info(f"Output Directory: {self.output_dir}")
        logger.info(f"Years: 2020-2025 (6 years)")
        logger.info(f"Types: Operating, Special Districts, Capital")
        logger.info("")

        stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'by_year': {}
        }

        for year, documents in sorted(self.budget_urls.items(), reverse=True):
            logger.info(f"\n📅 Downloading {year} Budget Documents...")
            year_stats = {'success': 0, 'failed': 0}

            for doc_type, url in documents.items():
                stats['total'] += 1
                filename = f"westchester_county_{year}_{doc_type}_budget.pdf"

                if self.download_pdf(url, filename):
                    stats['success'] += 1
                    year_stats['success'] += 1
                else:
                    stats['failed'] += 1
                    year_stats['failed'] += 1

            stats['by_year'][year] = year_stats
            logger.info(f"   Year {year}: {year_stats['success']}/{year_stats['success'] + year_stats['failed']} downloaded")

        # Summary
        logger.info("\n" + "="*80)
        logger.info("DOWNLOAD SUMMARY")
        logger.info("="*80)
        logger.info(f"Total PDFs Attempted: {stats['total']}")
        logger.info(f"✅ Successfully Downloaded: {stats['success']}")
        logger.info(f"❌ Failed: {stats['failed']}")
        logger.info(f"Success Rate: {(stats['success']/stats['total']*100):.1f}%")

        logger.info("\nBreakdown by Year:")
        for year in sorted(stats['by_year'].keys(), reverse=True):
            year_data = stats['by_year'][year]
            logger.info(f"  {year}: {year_data['success']} downloaded, {year_data['failed']} failed")

        logger.info(f"\n📁 Files saved to: {self.output_dir}")

        if stats['failed'] > 0:
            logger.info("\n⚠️ Some downloads failed. This may be due to:")
            logger.info("   - Incorrect URL patterns for older years")
            logger.info("   - Files moved or renamed on the website")
            logger.info("   - Network issues")
            logger.info("\n💡 Recommendation: Visit https://www.westchestergov.com/county-budget")
            logger.info("   to manually locate and download missing files.")

        if stats['success'] > 0:
            logger.info(f"\n✅ Successfully downloaded {stats['success']} PDF files!")
            logger.info("   Next step: Extract budget data from PDFs")

        return stats


def main():
    """Main execution function"""
    downloader = BudgetPDFDownloader()
    stats = downloader.download_all()

    return 0 if stats['success'] > 0 else 1


if __name__ == "__main__":
    exit(main())
