#!/usr/bin/env python3
"""
Final Planning Department Budget Extraction
Uses index page numbers to find exact Planning Department sections
Creates comprehensive transcripts and structured data
"""

import pdfplumber
from pathlib import Path
import json
import csv
import sys
import io
import re

# Use UTF-8 for console output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Base paths
project_root = Path(__file__).parent.parent.parent
budget_dir = project_root / "data" / "raw" / "manual_downloads" / "budgets"
output_dir = project_root / "data" / "processed" / "planning_budget_final"
output_dir.mkdir(parents=True, exist_ok=True)

# Budget files with expected page numbers from index
budget_files = {
    "2022": {
        "file": budget_dir / "westchester_county_2022_operating_budget.pdf",
        "start_page": 202,  # Around C-173
        "end_page": 225
    },
    "2023": {
        "file": budget_dir / "westchester_county_2023_operating_budget.pdf",
        "start_page": 202,  # Around C-173
        "end_page": 225
    },
    "2025": {
        "file": budget_dir / "westchester_county_2025_operating_budget.pdf",
        "start_page": 212,  # Around C-183
        "end_page": 235
    }
}

def clean_text(text):
    """Clean text for safe output"""
    if not text:
        return ""
    replacements = {
        '\uf050': '•',
        '\uf0d8': '↑',
        '\uf0fc': '→',
        '\u2019': "'",
        '\u2013': '-',
        '\u2014': '--',
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text.encode('ascii', errors='replace').decode('ascii')

def extract_planning_department(pdf_path, year, start_page, end_page):
    """Extract Planning Department section"""
    print(f"\n{'='*80}")
    print(f"Extracting {year} Planning Department Budget")
    print(f"File: {pdf_path.name}")
    print(f"Searching pages {start_page} to {end_page}")
    print(f"{'='*80}\n")

    results = {
        'year': year,
        'file': pdf_path.name,
        'pages_found': [],
        'text_content': [],
        'tables': [],
        'budget_summary': {}
    }

    try:
        with pdfplumber.open(pdf_path) as pdf:
            found_section = False
            section_start_page = None

            for page_num in range(start_page - 1, min(end_page, len(pdf.pages))):
                page = pdf.pages[page_num]
                text = page.extract_text()

                if not text:
                    continue

                text_clean = clean_text(text)
                text_lower = text_clean.lower()

                # Look for Planning Department section header (Department 19)
                if not found_section:
                    if 'department of planning (19)' in text_lower or \
                       ('department of planning' in text_lower and '(19)' in text):
                        print(f"✓ Found Planning Department section header on page {page_num + 1}")
                        found_section = True
                        section_start_page = page_num
                    else:
                        continue  # Keep searching

                # Once we found the section, extract content
                if found_section:
                    # Check if we've moved to the next department
                    if section_start_page and (page_num > section_start_page):
                        # Look for next department header pattern
                        if re.search(r'department of \w+ \(\d+\)', text_lower) and \
                           'department of planning' not in text_lower:
                            print(f"  Reached end of Planning Department section at page {page_num + 1}")
                            break

                    print(f"  Extracting page {page_num + 1}")
                    results['pages_found'].append(page_num + 1)
                    results['text_content'].append({
                        'page': page_num + 1,
                        'text': text_clean
                    })

                    # Extract tables
                    tables = page.extract_tables()
                    if tables:
                        print(f"    Found {len(tables)} table(s)")
                        for table_idx, table in enumerate(tables):
                            results['tables'].append({
                                'page': page_num + 1,
                                'table_number': table_idx + 1,
                                'data': table
                            })

            if not found_section:
                print(f"⚠ Planning Department section not found")
            else:
                print(f"\n✓ Extracted {len(results['pages_found'])} pages")
                print(f"  Pages: {results['pages_found']}")

    except Exception as e:
        print(f"✗ ERROR: {str(e)}")
        results['error'] = str(e)

    return results

def extract_budget_numbers(results):
    """Extract budget dollar amounts from text"""
    budget_info = {
        'appropriations': [],
        'revenues': [],
        'personnel': []
    }

    for content in results['text_content']:
        text = content['text']
        lines = text.split('\n')

        for line in lines:
            # Look for dollar amounts
            dollar_matches = re.findall(r'\$[\d,]+', line)
            if dollar_matches:
                line_lower = line.lower()

                # Categorize by keywords
                if any(word in line_lower for word in ['appropriation', 'budget', 'total']):
                    budget_info['appropriations'].append({
                        'page': content['page'],
                        'line': line.strip(),
                        'amounts': dollar_matches
                    })
                elif any(word in line_lower for word in ['revenue', 'fee', 'charge']):
                    budget_info['revenues'].append({
                        'page': content['page'],
                        'line': line.strip(),
                        'amounts': dollar_matches
                    })
                elif any(word in line_lower for word in ['personnel', 'staff', 'position', 'fte']):
                    budget_info['personnel'].append({
                        'page': content['page'],
                        'line': line.strip(),
                        'amounts': dollar_matches
                    })

    return budget_info

def save_results(year, results):
    """Save results in multiple formats"""
    year_dir = output_dir / year
    year_dir.mkdir(exist_ok=True)

    # 1. Full JSON
    json_path = year_dir / f"planning_dept_{year}_complete.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n✓ Saved: {json_path}")

    # 2. Text transcript
    txt_path = year_dir / f"planning_dept_{year}_transcript.txt"
    with open(txt_path, 'w', encoding='utf-8', errors='replace') as f:
        f.write(f"WESTCHESTER COUNTY - DEPARTMENT OF PLANNING (19)\n")
        f.write(f"FISCAL YEAR {year} OPERATING BUDGET\n")
        f.write(f"{'='*80}\n\n")
        f.write(f"Source: {results['file']}\n")
        f.write(f"Pages Extracted: {', '.join(map(str, results['pages_found']))}\n")
        f.write(f"Total Pages: {len(results['pages_found'])}\n")
        f.write(f"Extraction Date: 2025-10-15\n")
        f.write(f"{'='*80}\n\n")

        for content in results['text_content']:
            f.write(f"\n{'─'*80}\n")
            f.write(f"PAGE {content['page']}\n")
            f.write(f"{'─'*80}\n\n")
            f.write(content['text'])
            f.write("\n\n")
    print(f"✓ Saved: {txt_path}")

    # 3. CSV tables
    if results['tables']:
        for table_info in results['tables']:
            csv_path = year_dir / f"planning_dept_{year}_p{table_info['page']}_t{table_info['table_number']}.csv"
            with open(csv_path, 'w', encoding='utf-8', newline='', errors='replace') as f:
                writer = csv.writer(f)
                for row in table_info['data']:
                    cleaned_row = [clean_text(str(cell)) if cell else '' for cell in row]
                    writer.writerow(cleaned_row)
        print(f"✓ Saved {len(results['tables'])} CSV table(s)")

    # 4. Budget summary
    summary_path = year_dir / f"planning_dept_{year}_summary.md"
    with open(summary_path, 'w', encoding='utf-8', errors='replace') as f:
        f.write(f"# Planning Department Budget Summary - {year}\n\n")
        f.write(f"**Source:** {results['file']}  \n")
        f.write(f"**Pages:** {', '.join(map(str, results['pages_found']))}  \n")
        f.write(f"**Total Pages Extracted:** {len(results['pages_found'])}  \n")
        f.write(f"**Tables Extracted:** {len(results['tables'])}  \n")
        f.write(f"**Extraction Date:** 2025-10-15  \n\n")

        if results.get('budget_summary'):
            f.write(f"## Budget Information\n\n")
            bs = results['budget_summary']
            if bs.get('appropriations'):
                f.write(f"### Appropriations\n\n")
                for item in bs['appropriations'][:10]:  # First 10
                    f.write(f"- (Page {item['page']}) {item['line']}\n")
                f.write("\n")

        f.write(f"## Files Generated\n\n")
        f.write(f"- **Full Data:** `planning_dept_{year}_complete.json`\n")
        f.write(f"- **Transcript:** `planning_dept_{year}_transcript.txt`\n")
        f.write(f"- **Tables:** {len(results['tables'])} CSV files\n")
    print(f"✓ Saved: {summary_path}")

def main():
    print("\n" + "="*80)
    print("PLANNING DEPARTMENT BUDGET EXTRACTION - FINAL")
    print("="*80)
    print(f"\nOutput: {output_dir}\n")

    all_results = {}

    for year, config in budget_files.items():
        pdf_path = config['file']
        if not pdf_path.exists():
            print(f"⚠ {year} budget not found: {pdf_path}")
            continue

        results = extract_planning_department(
            pdf_path, year, config['start_page'], config['end_page']
        )

        # Extract budget numbers
        results['budget_summary'] = extract_budget_numbers(results)

        save_results(year, results)
        all_results[year] = results

        print(f"\n{'='*80}\n")

    # Consolidated summary
    summary_path = output_dir / "planning_dept_all_years.json"
    summary = {}
    for year, results in all_results.items():
        summary[year] = {
            'pages': results['pages_found'],
            'total_pages': len(results['pages_found']),
            'total_tables': len(results['tables'])
        }

    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)

    print("\n" + "="*80)
    print("EXTRACTION COMPLETE!")
    print("="*80)
    print(f"\nProcessed {len(all_results)} years")
    print(f"Output directory: {output_dir}")
    print("\nGenerated for each year:")
    print("  • Complete JSON data")
    print("  • Full text transcript")
    print("  • CSV tables")
    print("  • Markdown summary")

if __name__ == '__main__':
    main()
