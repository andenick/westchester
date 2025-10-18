"""
Westchester County Budget PDF Extractor

Uses DALM (Direct Agent LLM Method) via Robert to extract budget data from
Westchester County adopted operating budget PDFs.

This script processes budget PDFs and extracts:
- Total operating budget by year
- Department budget allocations
- Planning Department budget (critical for analysis)
- Year-over-year growth rates

Input: PDFs in Technical/data/raw/manual_downloads/budgets/
Output: JSON files in Technical/data/processed/budget/
"""

import os
import sys
from pathlib import Path
import json
from datetime import datetime
from typing import Dict, List, Optional

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

# DALM Integration
# For PDFs > 5 MB, use: Council/Robert/Reference/pdf_processing/dalm_orchestrator.py
# For PDFs <= 5 MB, use Claude's Read tool directly


class BudgetPDFExtractor:
    """Extract budget data from Westchester County PDF documents"""

    def __init__(self, input_dir: str, output_dir: str):
        """
        Initialize the budget PDF extractor.

        Args:
            input_dir: Directory containing budget PDFs
            output_dir: Directory to save extracted JSON data
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Create extraction log
        self.log_file = self.output_dir / "extraction_log.json"
        self.extraction_log = {
            "extraction_date": datetime.now().isoformat(),
            "files_processed": [],
            "errors": [],
            "summary": {}
        }

    def extract_budget_data(self, pdf_path: Path) -> Optional[Dict]:
        """
        Extract budget data from a single PDF file.

        This function uses DALM (Direct Agent LLM Method) to extract structured
        budget data. For PDFs <= 5 MB, Claude Read tool is sufficient.
        For larger PDFs, use dalm_orchestrator.py

        Args:
            pdf_path: Path to budget PDF file

        Returns:
            Dictionary with extracted budget data, or None if extraction fails
        """
        print(f"\n🔍 Processing: {pdf_path.name}")

        # Check file size
        file_size_mb = pdf_path.stat().st_size / (1024 * 1024)
        print(f"   File size: {file_size_mb:.2f} MB")

        # Extract year from filename (e.g., "2024_Adopted_Operating_Budget.pdf" → 2024)
        try:
            year = int(pdf_path.stem.split('_')[0])
        except (ValueError, IndexError):
            print(f"   ❌ Could not extract year from filename: {pdf_path.name}")
            self.extraction_log["errors"].append({
                "file": str(pdf_path),
                "error": "Invalid filename format"
            })
            return None

        # TODO: Implement DALM extraction
        # For now, return template structure
        # ACTUAL IMPLEMENTATION: Use Robert/DALM to read PDF and extract tables

        budget_data = {
            "year": year,
            "file_source": str(pdf_path.name),
            "extraction_date": datetime.now().isoformat(),
            "extraction_method": "DALM" if file_size_mb > 5 else "Claude Read",
            "total_budget": None,  # To be extracted from PDF
            "departments": {
                # Department name: budget amount
                # To be extracted from PDF
                "Education": None,
                "Public Safety": None,
                "Health & Human Services": None,
                "Public Works": None,
                "Parks & Recreation": None,
                "Planning": None,  # CRITICAL for analysis
                "Administration": None,
                "Other": None
            },
            "metadata": {
                "currency": "USD",
                "fiscal_year": year,
                "document_type": "Adopted Operating Budget"
            }
        }

        print(f"""
   📋 MANUAL EXTRACTION REQUIRED:

   To extract budget data, use one of these methods:

   1. AUTOMATED (Recommended): Use Robert/DALM
      - For PDFs <= 5 MB: Use Claude Read tool directly
      - For PDFs > 5 MB: Use Council/Robert/Reference/pdf_processing/dalm_orchestrator.py

   2. SEMI-AUTOMATED: Use this Python script with pdfplumber
      - Install: pip install pdfplumber
      - Extract tables automatically
      - Validate and clean data

   3. MANUAL: Extract from PDF manually
      - Open PDF: {pdf_path}
      - Find budget summary table
      - Extract total budget and department allocations
      - Update: {self.output_dir / f"budget_{year}.json"}

   EXPECTED DATA TO EXTRACT:
   - Total Operating Budget (FY {year})
   - Department Allocations:
     * Education
     * Public Safety
     * Health & Human Services
     * Public Works
     * Parks & Recreation
     * Planning (CRITICAL - for city planning analysis)
     * Administration
     * Other departments

   SAVE TO: {self.output_dir / f"budget_{year}.json"}
        """)

        # Save template for manual population
        output_file = self.output_dir / f"budget_{year}.json"
        with open(output_file, 'w') as f:
            json.dump(budget_data, f, indent=2)

        print(f"   ✅ Template saved: {output_file}")
        print(f"   ⚠️  Requires manual data population")

        # Log extraction attempt
        self.extraction_log["files_processed"].append({
            "file": str(pdf_path),
            "year": year,
            "status": "template_created",
            "output": str(output_file)
        })

        return budget_data

    def process_all_budgets(self) -> Dict:
        """
        Process all budget PDFs in input directory.

        Returns:
            Dictionary with extraction summary
        """
        print("\n" + "=" * 70)
        print("WESTCHESTER COUNTY BUDGET PDF EXTRACTOR")
        print("=" * 70)
        print(f"\nInput directory:  {self.input_dir}")
        print(f"Output directory: {self.output_dir}")

        # Find all PDF files
        pdf_files = sorted(self.input_dir.glob("*.pdf"))

        if not pdf_files:
            print(f"\n❌ No PDF files found in {self.input_dir}")
            print(f"\nExpected files:")
            print(f"  - 2025_Adopted_Operating_Budget.pdf")
            print(f"  - 2024_Adopted_Operating_Budget.pdf")
            print(f"  - 2023_Adopted_Operating_Budget.pdf")
            print(f"  - 2022_Adopted_Operating_Budget.pdf")
            print(f"  - 2021_Adopted_Operating_Budget.pdf")
            print(f"  - 2020_Adopted_Operating_Budget.pdf")
            return {"status": "error", "message": "No PDF files found"}

        print(f"\nFound {len(pdf_files)} PDF file(s):")
        for pdf in pdf_files:
            print(f"  - {pdf.name}")

        # Process each PDF
        extracted_budgets = []
        for pdf_path in pdf_files:
            budget_data = self.extract_budget_data(pdf_path)
            if budget_data:
                extracted_budgets.append(budget_data)

        # Create consolidated budget time series
        time_series = self._create_time_series(extracted_budgets)

        # Save consolidated data
        consolidated_file = self.output_dir / "budgets_time_series.json"
        with open(consolidated_file, 'w') as f:
            json.dump(time_series, f, indent=2)

        print(f"\n✅ Consolidated time series saved: {consolidated_file}")

        # Update summary
        self.extraction_log["summary"] = {
            "total_files": len(pdf_files),
            "successful": len(extracted_budgets),
            "failed": len(pdf_files) - len(extracted_budgets),
            "years_covered": [b["year"] for b in extracted_budgets],
            "output_files": {
                "individual": [str(self.output_dir / f"budget_{b['year']}.json")
                             for b in extracted_budgets],
                "consolidated": str(consolidated_file)
            }
        }

        # Save extraction log
        with open(self.log_file, 'w') as f:
            json.dump(self.extraction_log, f, indent=2)

        print(f"\n📊 Extraction log saved: {self.log_file}")

        # Print summary
        print("\n" + "=" * 70)
        print("EXTRACTION SUMMARY")
        print("=" * 70)
        print(f"Total PDFs found:     {len(pdf_files)}")
        print(f"Templates created:    {len(extracted_budgets)}")
        print(f"Years covered:        {min(b['year'] for b in extracted_budgets) if extracted_budgets else 'N/A'}-"
              f"{max(b['year'] for b in extracted_budgets) if extracted_budgets else 'N/A'}")
        print(f"\n⚠️  NEXT STEPS:")
        print(f"   1. Use Robert/DALM to extract data from PDFs")
        print(f"   2. Populate JSON templates in: {self.output_dir}")
        print(f"   3. Run validation script: python validate_extracted_data.py")
        print("=" * 70 + "\n")

        return self.extraction_log["summary"]

    def _create_time_series(self, budgets: List[Dict]) -> Dict:
        """
        Create consolidated time series from individual budget data.

        Args:
            budgets: List of budget dictionaries

        Returns:
            Dictionary with time series data
        """
        # Sort by year
        budgets_sorted = sorted(budgets, key=lambda x: x["year"])

        time_series = {
            "dataset": "Westchester County Operating Budgets",
            "years": [b["year"] for b in budgets_sorted],
            "data_source": "Westchester County Budget Office",
            "url": "https://www.westchestergov.com/county-budgets",
            "extraction_date": datetime.now().isoformat(),
            "budgets_by_year": {
                str(b["year"]): b for b in budgets_sorted
            },
            "metadata": {
                "currency": "USD",
                "fiscal_year_basis": "Calendar year",
                "department_categories": list(budgets_sorted[0]["departments"].keys()) if budgets_sorted else []
            }
        }

        return time_series


def main():
    """Main execution function"""

    # Set up paths
    PROJECT_ROOT = Path(__file__).parent.parent.parent
    INPUT_DIR = PROJECT_ROOT / "data" / "raw" / "manual_downloads" / "budgets"
    OUTPUT_DIR = PROJECT_ROOT / "data" / "processed" / "budget"

    # Create extractor
    extractor = BudgetPDFExtractor(
        input_dir=str(INPUT_DIR),
        output_dir=str(OUTPUT_DIR)
    )

    # Process all budgets
    summary = extractor.process_all_budgets()

    return summary


if __name__ == "__main__":
    summary = main()
