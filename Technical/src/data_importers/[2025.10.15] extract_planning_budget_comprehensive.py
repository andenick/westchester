#!/usr/bin/env python3
"""
Comprehensive Planning Department Budget Extraction
Extracts Planning Department budgets from all available years (2022, 2023, 2025)
Creates structured data (JSON, CSV) and text transcripts for knowledge base
"""

import pdfplumber
from pathlib import Path
import json
import csv
import sys
import io

# Use UTF-8 for console output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Base paths
project_root = Path(__file__).parent.parent.parent
budget_dir = project_root / "data" / "raw" / "manual_downloads" / "budgets"
output_dir = project_root / "data" / "processed" / "planning_budget"
output_dir.mkdir(parents=True, exist_ok=True)

# Budget files to process
budget_files = {
    "2022": budget_dir / "westchester_county_2022_operating_budget.pdf",
    "2023": budget_dir / "westchester_county_2023_operating_budget.pdf",
    "2025": budget_dir / "westchester_county_2025_operating_budget.pdf",
}

def clean_text(text):
    """Clean text for safe output, replacing problematic characters"""
    if not text:
        return ""
    # Replace problematic Unicode characters
    replacements = {
        '\uf050': '•',  # Bullet point
        '\uf0d8': '↑',  # Up arrow
        '\uf0fc': '→',  # Right arrow
        '\u2019': "'",  # Right single quotation mark
        '\u2013': '-',  # En dash
        '\u2014': '--', # Em dash
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    # Remove any remaining problematic characters
    return text.encode('ascii', errors='replace').decode('ascii')

def extract_planning_section(pdf_path, year):
    """Extract Planning Department section from budget PDF"""
    print(f"\n{'='*80}")
    print(f"Processing {year} Operating Budget")
    print(f"File: {pdf_path.name}")
    print(f"{'='*80}\n")

    results = {
        'year': year,
        'file': pdf_path.name,
        'pages_found': [],
        'text_content': [],
        'tables': [],
        'budget_items': []
    }

    try:
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            print(f"Total pages in PDF: {total_pages}")

            # Based on previous search, Planning Department is around page 200-230
            # But we'll search a wider range to be safe
            search_start = 180
            search_end = min(250, total_pages)

            print(f"Searching pages {search_start} to {search_end} for Planning Department...\n")

            found_planning = False
            planning_pages = []

            for page_num in range(search_start, search_end):
                page = pdf.pages[page_num]
                text = page.extract_text()

                if not text:
                    continue

                text_lower = text.lower()

                # Look for Planning Department mentions
                if any(keyword in text_lower for keyword in [
                    'department of planning',
                    'dept. of planning',
                    'planning department',
                    'dept of planning'
                ]):
                    print(f"✓ Found Planning Department on page {page_num + 1}")
                    found_planning = True
                    planning_pages.append(page_num)

                    # Clean and store text
                    cleaned_text = clean_text(text)
                    results['pages_found'].append(page_num + 1)
                    results['text_content'].append({
                        'page': page_num + 1,
                        'text': cleaned_text
                    })

                    # Extract tables
                    tables = page.extract_tables()
                    if tables:
                        print(f"  Found {len(tables)} table(s) on page {page_num + 1}")
                        for table_idx, table in enumerate(tables):
                            results['tables'].append({
                                'page': page_num + 1,
                                'table_number': table_idx + 1,
                                'data': table
                            })

                    # Continue to next few pages after finding Planning
                    continue

                # If we found Planning Department, check next few pages too
                if found_planning and (page_num <= max(planning_pages) + 5):
                    if any(keyword in text_lower for keyword in [
                        'planning',
                        'budget',
                        'department',
                        'program'
                    ]):
                        print(f"  Checking continuation on page {page_num + 1}")
                        cleaned_text = clean_text(text)
                        results['pages_found'].append(page_num + 1)
                        results['text_content'].append({
                            'page': page_num + 1,
                            'text': cleaned_text
                        })

                        tables = page.extract_tables()
                        if tables:
                            for table_idx, table in enumerate(tables):
                                results['tables'].append({
                                    'page': page_num + 1,
                                    'table_number': table_idx + 1,
                                    'data': table
                                })

                # Stop if we've gone too far past Planning section
                if found_planning and (page_num > max(planning_pages) + 10):
                    break

            if not found_planning:
                print(f"⚠ WARNING: Planning Department section not found in {year} budget")
                print(f"Searched pages {search_start} to {search_end}")
            else:
                print(f"\n✓ Successfully extracted Planning Department data from {len(results['pages_found'])} pages")
                print(f"  Pages: {results['pages_found']}")

    except Exception as e:
        print(f"✗ ERROR processing {year} budget: {str(e)}")
        results['error'] = str(e)

    return results

def parse_budget_items(results):
    """Parse budget line items from extracted tables"""
    budget_items = []

    for table_info in results['tables']:
        table = table_info['data']
        page = table_info['page']

        # Skip empty tables
        if not table or len(table) < 2:
            continue

        # Try to identify budget tables by looking for dollar amounts
        for row_idx, row in enumerate(table):
            if not row:
                continue

            # Look for rows with amounts (containing $ or numeric values)
            row_str = ' '.join([str(cell) if cell else '' for cell in row])

            if '$' in row_str or any(cell and str(cell).replace(',', '').replace('.', '').isdigit() for cell in row):
                # This might be a budget line item
                budget_items.append({
                    'page': page,
                    'table': table_info['table_number'],
                    'row': row_idx + 1,
                    'data': row
                })

    return budget_items

def save_results(year, results):
    """Save extraction results in multiple formats"""
    year_dir = output_dir / year
    year_dir.mkdir(exist_ok=True)

    # 1. Save full JSON
    json_path = year_dir / f"planning_budget_{year}_full.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n✓ Saved JSON: {json_path}")

    # 2. Save text transcript
    txt_path = year_dir / f"planning_budget_{year}_transcript.txt"
    with open(txt_path, 'w', encoding='utf-8', errors='replace') as f:
        f.write(f"WESTCHESTER COUNTY PLANNING DEPARTMENT BUDGET - {year}\n")
        f.write(f"{'='*80}\n\n")
        f.write(f"Source: {results['file']}\n")
        f.write(f"Pages: {', '.join(map(str, results['pages_found']))}\n")
        f.write(f"{'='*80}\n\n")

        for content in results['text_content']:
            f.write(f"\n--- PAGE {content['page']} ---\n\n")
            f.write(content['text'])
            f.write("\n\n")
    print(f"✓ Saved transcript: {txt_path}")

    # 3. Save tables as CSV
    if results['tables']:
        for table_info in results['tables']:
            csv_path = year_dir / f"planning_budget_{year}_page{table_info['page']}_table{table_info['table_number']}.csv"
            with open(csv_path, 'w', encoding='utf-8', newline='', errors='replace') as f:
                writer = csv.writer(f)
                for row in table_info['data']:
                    # Clean each cell
                    cleaned_row = [clean_text(str(cell)) if cell else '' for cell in row]
                    writer.writerow(cleaned_row)
        print(f"✓ Saved {len(results['tables'])} CSV table(s)")

    # 4. Save summary
    summary_path = year_dir / f"planning_budget_{year}_summary.txt"
    with open(summary_path, 'w', encoding='utf-8', errors='replace') as f:
        f.write(f"PLANNING DEPARTMENT BUDGET SUMMARY - {year}\n")
        f.write(f"{'='*80}\n\n")
        f.write(f"Source File: {results['file']}\n")
        f.write(f"Pages Found: {len(results['pages_found'])}\n")
        f.write(f"Page Numbers: {', '.join(map(str, results['pages_found']))}\n")
        f.write(f"Tables Extracted: {len(results['tables'])}\n")
        f.write(f"\nExtraction Date: 2025-10-15\n")
    print(f"✓ Saved summary: {summary_path}")

def main():
    print("\n" + "="*80)
    print("WESTCHESTER COUNTY PLANNING DEPARTMENT BUDGET EXTRACTION")
    print("="*80)
    print(f"\nOutput directory: {output_dir}")
    print(f"Processing {len(budget_files)} budget years: {', '.join(budget_files.keys())}\n")

    all_results = {}

    for year, pdf_path in budget_files.items():
        if not pdf_path.exists():
            print(f"⚠ WARNING: {year} budget file not found: {pdf_path}")
            continue

        # Extract Planning Department section
        results = extract_planning_section(pdf_path, year)

        # Parse budget items
        results['budget_items'] = parse_budget_items(results)

        # Save results
        save_results(year, results)

        all_results[year] = results

        print(f"\n{'='*80}\n")

    # Create consolidated summary
    summary_path = output_dir / "planning_budget_all_years_summary.json"
    summary = {}
    for year, results in all_results.items():
        summary[year] = {
            'file': results['file'],
            'pages_found': results['pages_found'],
            'total_pages': len(results['pages_found']),
            'total_tables': len(results['tables']),
            'total_budget_items': len(results['budget_items'])
        }

    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)

    print("\n" + "="*80)
    print("EXTRACTION COMPLETE")
    print("="*80)
    print(f"\nProcessed {len(all_results)} years")
    print(f"Output directory: {output_dir}")
    print("\nFiles created:")
    print("  - Full JSON data for each year")
    print("  - Text transcripts for each year")
    print("  - CSV files for budget tables")
    print("  - Summary files")
    print(f"  - Consolidated summary: {summary_path}")
    print("\nYou can now use this data for:")
    print("  - Knowledge base integration")
    print("  - Budget trend analysis")
    print("  - Planning Department dashboard")
    print("  - Grant applications and reporting")

if __name__ == '__main__':
    main()
