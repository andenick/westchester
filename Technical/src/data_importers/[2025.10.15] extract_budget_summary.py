#!/usr/bin/env python3
"""
Extract budget summary data from Westchester County budget PDFs
"""

import pdfplumber
from pathlib import Path
import re
import json

def find_summary_pages(pdf):
    """Find pages containing budget summary tables"""
    summary_pages = []

    for i, page in enumerate(pdf.pages):
        text = page.extract_text()
        if text and ('SUMMARIES OF COUNTY OPERATING BUDGETS' in text or
                     'SUMMARY OF APPROPRIATIONS' in text or
                     'B-' in text[:100]):  # Section B pages
            summary_pages.append(i)
            if len(summary_pages) > 20:  # Limit to first 20 summary pages
                break

    return summary_pages

def extract_budget_data(pdf_path):
    """Extract department budget data from PDF"""
    print(f"\nExtracting from: {pdf_path.name}")

    with pdfplumber.open(pdf_path) as pdf:
        print(f"Total pages: {len(pdf.pages)}")

        # Find summary pages
        summary_pages = find_summary_pages(pdf)
        print(f"Found {len(summary_pages)} potential summary pages: {summary_pages[:10]}")

        # Extract text and tables from summary pages
        for page_num in summary_pages[:10]:
            page = pdf.pages[page_num]
            print(f"\n{'='*80}")
            print(f"PAGE {page_num + 1}")
            print(f"{'='*80}")

            text = page.extract_text()
            print(text[:2000] if text else "(No text)")

            tables = page.extract_tables()
            if tables:
                print(f"\nFound {len(tables)} table(s)")
                for j, table in enumerate(tables):
                    print(f"\nTable {j+1} (first 10 rows):")
                    for row in table[:10]:
                        print(row)

# Run for each downloaded budget PDF
budgets_dir = Path(__file__).parent.parent.parent / "data" / "raw" / "manual_downloads" / "budgets"

pdf_files = sorted(budgets_dir.glob("*.pdf"))
print(f"Found {len(pdf_files)} PDF files")

# Start with 2025 operating budget
for pdf_file in pdf_files:
    if '2025' in pdf_file.name and 'operating' in pdf_file.name.lower():
        extract_budget_data(pdf_file)
        break
