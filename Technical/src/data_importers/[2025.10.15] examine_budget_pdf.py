#!/usr/bin/env python3
"""
Quick script to examine budget PDF structure
"""

import pdfplumber
from pathlib import Path

pdf_path = Path(__file__).parent.parent.parent / "data" / "raw" / "manual_downloads" / "budgets" / "westchester_county_2025_operating_budget.pdf"

print(f"Examining: {pdf_path.name}\n")

with pdfplumber.open(pdf_path) as pdf:
    print(f"Total pages: {len(pdf.pages)}\n")

    # Examine first 10 pages
    for i in range(min(10, len(pdf.pages))):
        page = pdf.pages[i]
        text = page.extract_text()

        print(f"=" * 80)
        print(f"PAGE {i+1}")
        print(f"=" * 80)
        print(text[:1000] if text else "(No text)")
        print("\n")

        # Also extract tables
        tables = page.extract_tables()
        if tables:
            print(f"Found {len(tables)} table(s) on page {i+1}")
            for j, table in enumerate(tables):
                print(f"\nTable {j+1} preview (first 3 rows):")
                for row in table[:3]:
                    print(row)
        print("\n")
