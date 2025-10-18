#!/usr/bin/env python3
"""
Find the exact page numbers where Planning Department's own budget section starts
Searches for department header patterns like "Department Of Planning (##)"
"""

import pdfplumber
from pathlib import Path
import sys
import io

# Use UTF-8 for console output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Base paths
project_root = Path(__file__).parent.parent.parent
budget_dir = project_root / "data" / "raw" / "manual_downloads" / "budgets"

# Budget files to search
budget_files = {
    "2022": budget_dir / "westchester_county_2022_operating_budget.pdf",
    "2023": budget_dir / "westchester_county_2023_operating_budget.pdf",
    "2025": budget_dir / "westchester_county_2025_operating_budget.pdf",
}

def search_for_planning_header(pdf_path, year):
    """Search for Planning Department section header"""
    print(f"\n{'='*80}")
    print(f"Searching {year} Budget: {pdf_path.name}")
    print(f"{'='*80}\n")

    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)
        print(f"Total pages: {total_pages}\n")

        # Search entire document
        for page_num in range(total_pages):
            page = pdf.pages[page_num]
            text = page.extract_text()

            if not text:
                continue

            # Clean text for safe output
            text_clean = text.encode('ascii', errors='replace').decode('ascii')
            text_lower = text_clean.lower()

            # Look for department header patterns
            header_patterns = [
                'department of planning',
                'dept. of planning',
                'planning department (',
                'planning dept (',
            ]

            for pattern in header_patterns:
                if pattern in text_lower:
                    # Check if this looks like a department section header
                    lines = text_clean.split('\n')
                    for line in lines[:10]:  # Check first 10 lines of page
                        line_lower = line.lower()
                        if pattern in line_lower and '(' in line:
                            print(f"✓ FOUND on page {page_num + 1}:")
                            print(f"  Pattern: '{pattern}'")
                            print(f"  Line: {line.strip()}")
                            print(f"\n  First 500 characters of page:\n")
                            print(text_clean[:500])
                            print("\n" + "-"*80 + "\n")
                            return page_num + 1

        print(f"⚠ Planning Department section header NOT FOUND in {year} budget")
        print(f"Searched all {total_pages} pages\n")
        return None

def main():
    print("\n" + "="*80)
    print("SEARCHING FOR PLANNING DEPARTMENT SECTION HEADERS")
    print("="*80)

    results = {}

    for year, pdf_path in budget_files.items():
        if not pdf_path.exists():
            print(f"⚠ {year} budget file not found")
            continue

        page_num = search_for_planning_header(pdf_path, year)
        results[year] = page_num

    print("\n" + "="*80)
    print("SEARCH RESULTS SUMMARY")
    print("="*80 + "\n")

    for year, page_num in results.items():
        if page_num:
            print(f"{year}: Planning Department section starts on page {page_num}")
        else:
            print(f"{year}: Planning Department section NOT FOUND")

if __name__ == '__main__':
    main()
