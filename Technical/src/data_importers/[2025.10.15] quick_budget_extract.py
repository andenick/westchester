#!/usr/bin/env python3
"""
Quick budget summary extraction - focuses on likely summary pages (10-50)
"""

import pdfplumber
from pathlib import Path

pdf_path = Path(__file__).parent.parent.parent / "data" / "raw" / "manual_downloads" / "budgets" / "westchester_county_2025_operating_budget.pdf"

print(f"Examining: {pdf_path.name}")
print("Searching pages 10-50 for budget summaries...\n")

with pdfplumber.open(pdf_path) as pdf:
    # Check pages 10-50 only (where summary section B-1 likely is)
    for i in range(10, min(50, len(pdf.pages))):
        page = pdf.pages[i]
        text = page.extract_text()

        # Look for summary indicators
        if text and ('B-' in text[:200] or 'SUMMARY' in text[:500].upper()):
            print(f"{'='*80}")
            print(f"PAGE {i+1}")
            print(f"{'='*80}")
            print(text[:1500])

            # Extract tables
            tables = page.extract_tables()
            if tables:
                print(f"\nFOUND {len(tables)} TABLE(S):\n")
                for j, table in enumerate(tables[:2]):
                    print(f"Table {j+1} (first 5 rows):")
                    for row in table[:5]:
                        print(row)
                    print()

            print("\n" + "="*80 + "\n")
