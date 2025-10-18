#!/usr/bin/env python3
"""
Extract Planning Department budget from Westchester County budget PDFs
Search for planning-related entries in budget documents
"""

import pdfplumber
from pathlib import Path
import re
import json

pdf_path = Path(__file__).parent.parent.parent / "data" / "raw" / "manual_downloads" / "budgets" / "westchester_county_2025_operating_budget.pdf"

print(f"Searching for Planning Department budget in: {pdf_path.name}\n")

planning_references = []

with pdfplumber.open(pdf_path) as pdf:
    print(f"Total pages: {len(pdf.pages)}\n")

    # Search for "Planning" or "planning" in all pages
    for i, page in enumerate(pdf.pages):
        text = page.extract_text()

        if text and ('planning' in text.lower() or 'plann' in text.lower()):
            # Extract context around "planning"
            lines = text.split('\n')
            for j, line in enumerate(lines):
                if 'planning' in line.lower() or 'plann' in line.lower():
                    # Get surrounding context (3 lines before and after)
                    start_idx = max(0, j - 3)
                    end_idx = min(len(lines), j + 4)
                    context = '\n'.join(lines[start_idx:end_idx])

                    planning_references.append({
                        'page': i + 1,
                        'line': line.strip(),
                        'context': context
                    })

# Display findings
print("="*80)
print("PLANNING DEPARTMENT REFERENCES FOUND")
print("="*80)

if planning_references:
    print(f"\nFound {len(planning_references)} references to Planning\n")

    # Group by page for clarity
    pages_with_planning = {}
    for ref in planning_references:
        page = ref['page']
        if page not in pages_with_planning:
            pages_with_planning[page] = []
        pages_with_planning[page].append(ref)

    # Show unique pages
    for page_num in sorted(pages_with_planning.keys())[:20]:  # Limit to first 20 pages with planning
        print(f"\n{'='*80}")
        print(f"PAGE {page_num}")
        print(f"{'='*80}")

        # Show first few references from this page
        for ref in pages_with_planning[page_num][:3]:
            print(f"\nLine: {ref['line']}")
            if '$' in ref['context'] or ',' in ref['context']:  # Likely contains budget numbers
                print(f"\nContext (likely budget data):\n{ref['context']}\n")
                print("-"*60)
else:
    print("\nNo planning references found. Budget may use different terminology.")
    print("Try searching for: Development, Land Use, Zoning, Community Development")

# Now let's also check the index for Planning
print("\n\n" + "="*80)
print("CHECKING INDEX FOR PLANNING DEPARTMENT")
print("="*80)

with pdfplumber.open(pdf_path) as pdf:
    # Index is typically in first 10-20 pages
    for i in range(min(20, len(pdf.pages))):
        page = pdf.pages[i]
        text = page.extract_text()

        if text and ('index' in text.lower() or 'table of contents' in text.lower()):
            if 'planning' in text.lower():
                print(f"\nFound Planning in INDEX on page {i+1}:\n")
                print(text[:2000])
                break
