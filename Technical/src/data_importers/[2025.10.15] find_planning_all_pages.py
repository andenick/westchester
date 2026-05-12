#!/usr/bin/env python3
"""
Search ALL pages for Planning Department (19) section headers
"""

import pdfplumber
from pathlib import Path
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

budget_dir = Path(__file__).resolve().parent.parent / 'data' / 'raw' / 'manual_downloads' / 'budgets'

for year, filename in [('2022', 'westchester_county_2022_operating_budget.pdf'),
                       ('2023', 'westchester_county_2023_operating_budget.pdf')]:
    print(f'{'='*80}')
    print(f'Searching {year} for Planning Department section')
    print(f'='*80 + '\n')

    pdf_path = budget_dir / filename
    matches = []

    with pdfplumber.open(pdf_path) as pdf:
        for i in range(len(pdf.pages)):
            text = pdf.pages[i].extract_text()
            if not text:
                continue

            # Look for actual department header (not just index)
            if 'Department Of Planning (19)' in text:
                # Check if this is the actual department section (not index)
                lines = text.split('\n')
                for j, line in enumerate(lines[:10]):
                    if 'Department Of Planning (19)' in line:
                        matches.append((i+1, line[:100]))
                        break

    print(f'Found {len(matches)} matches in {year}:')
    for page_num, line in matches:
        print(f'  Page {page_num}: {line}')
    print()
