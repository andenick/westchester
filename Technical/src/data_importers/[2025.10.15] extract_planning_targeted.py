#!/usr/bin/env python3
"""
Extract Planning Department budget - targeted search around known page range
From index: Department Of Planning (19) appears around C-183
"""

import pdfplumber
from pathlib import Path
import json

pdf_path = Path(__file__).parent.parent.parent / "data" / "raw" / "manual_downloads" / "budgets" / "westchester_county_2025_operating_budget.pdf"

print(f"Extracting Planning Department budget from: {pdf_path.name}\n")

# Based on index showing "Department Of Planning (19)" around C-183
# C-1 starts around page 30, so C-183 is approximately page 30 + 183 = page 213
# Let's check pages 200-230 to be safe

start_page = 200
end_page = 230

with pdfplumber.open(pdf_path) as pdf:
    print(f"Searching pages {start_page} to {end_page} for Planning Department...")

    for i in range(start_page, min(end_page, len(pdf.pages))):
        page = pdf.pages[i]
        text = page.extract_text()

        if text and 'planning' in text.lower():
            print(f"\n{'='*80}")
            print(f"PAGE {i+1} - Contains 'Planning'")
            print(f"{'='*80}")
            print(text[:3000])  # First 3000 characters
            print("\n...")

            # Extract tables which likely contain budget numbers
            tables = page.extract_tables()
            if tables:
                print(f"\nFOUND {len(tables)} TABLE(S) ON THIS PAGE:")
                for j, table in enumerate(tables):
                    print(f"\nTable {j+1} (first 5 rows):")
                    for row in table[:5]:
                        print(row)

            # Stop after finding first substantial planning page
            if 'department of planning' in text.lower() or 'dept. of planning' in text.lower():
                print("\n\n" + "="*80)
                print("FOUND PLANNING DEPARTMENT SECTION")
                print("="*80)
                break
