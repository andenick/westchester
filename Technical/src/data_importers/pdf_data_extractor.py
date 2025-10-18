"""
PDF Data Extractor for Westchester County
Processes downloaded PDF documents to extract structured data

This advanced extractor handles budget documents, financial reports,
tax profiles, and other PDFs containing Westchester data.
"""

import json
import re
import csv
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import os
import subprocess
import sys


class PDFDataExtractor:
    """Advanced PDF data extractor for municipal documents"""

    def __init__(self, pdf_dir: Path = None, output_dir: Path = None):
        """
        Initialize PDF data extractor

        Args:
            pdf_dir: Directory containing PDF files
            output_dir: Directory to save extracted data
        """
        if pdf_dir is None:
            pdf_dir = Path(__file__).parent.parent.parent / "data" / "raw" / "manual_downloads"

        if output_dir is None:
            output_dir = Path(__file__).parent.parent.parent / "data" / "processed" / "pdf_extracted"

        self.pdf_dir = pdf_dir
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.pdf_dir.mkdir(parents=True, exist_ok=True)

        # Check for required libraries
        self.pdfplumber_available = self._check_library('pdfplumber')
        self.pymupdf_available = self._check_library('fitz')  # PyMuPDF
        self.pypdf2_available = self._check_library('PyPDF2')

        print(f"PDF processing libraries available:")
        print(f"  - pdfplumber: {'Yes' if self.pdfplumber_available else 'No'}")
        print(f"  - PyMuPDF: {'Yes' if self.pymupdf_available else 'No'}")
        print(f"  - PyPDF2: {'Yes' if self.pypdf2_available else 'No'}")

        # PDF processing patterns for different document types
        self.extraction_patterns = {
            "budget_document": {
                "keywords": ["budget", "operating budget", "adopted budget", "fiscal year", "expenditures", "revenues"],
                "patterns": {
                    "total_budget": r"[$]?\s*([\d,]+(?:\.\d+)?)\s*(?:million|billion)?\s*(?:total budget|operating budget)",
                    "department_budget": r"([A-Za-z\s&]+)\s*[$]?\s*([\d,]+(?:\.\d+)?)\s*(?:million|billion)?",
                    "planning_budget": r"(planning|city planning|planning department)\s*[$]?\s*([\d,]+(?:\.\d+)?)",
                    "per_capita": r"per\s+capita\s*[$]?\s*([\d,]+(?:\.\d+)?)",
                    "year_comparison": r"(20\d{2})\s*[$]?\s*([\d,]+(?:\.\d+)?)\s*(?:million|billion)?"
                }
            },
            "financial_report": {
                "keywords": ["financial report", "annual report", "comprehensive annual financial report", "CAFR"],
                "patterns": {
                    "total_expenditures": r"total\s+expenditures\s*[$]?\s*([\d,]+(?:\.\d+)?)",
                    "total_revenues": r"total\s+revenues\s*[$]?\s*([\d,]+(?:\.\d+)?)",
                    "fund_balance": r"fund\s+balance\s*[$]?\s*([\d,]+(?:\.\d+)?)",
                    "capital_expenditures": r"capital\s+expenditures\s*[$]?\s*([\d,]+(?:\.\d+)?)"
                }
            },
            "tax_profile": {
                "keywords": ["tax profile", "municipal profile", "property tax", "effective tax rate"],
                "patterns": {
                    "effective_tax_rate": r"effective\s+tax\s+rate\s*([0-9.]+)%?",
                    "tax_levy": r"tax\s+levy\s*[$]?\s*([\d,]+(?:\.\d+)?)",
                    "assessed_value": r"assessed\s+value\s*[$]?\s*([\d,]+(?:\.\d+)?)",
                    "equalization_rate": r"equalization\s+rate\s*([0-9.]+)%?"
                }
            },
            "demographic_report": {
                "keywords": ["demographics", "population", "census", "community profile"],
                "patterns": {
                    "population": r"population\s*[:]?\s*([\d,]+)",
                    "median_income": r"median\s+(?:household\s+)?income\s*[$]?\s*([\d,]+)",
                    "median_age": r"median\s+age\s*[:]?\s*([\d.]+)",
                    "housing_units": r"housing\s+units\s*[:]?\s*([\d,]+)"
                }
            }
        }

    def _check_library(self, library_name: str) -> bool:
        """Check if a Python library is available"""
        try:
            if library_name == 'fitz':  # PyMuPDF
                import fitz
                return True
            else:
                __import__(library_name)
                return True
        except ImportError:
            return False

    def extract_pdf_text(self, pdf_path: Path) -> Optional[str]:
        """
        Extract text from PDF using available libraries

        Args:
            pdf_path: Path to PDF file

        Returns:
            Extracted text or None if failed
        """
        if not pdf_path.exists():
            print(f"[ERROR] PDF file not found: {pdf_path}")
            return None

        # Try different libraries in order of preference
        if self.pymupdf_available:
            text = self._extract_with_pymupdf(pdf_path)
            if text:
                return text

        if self.pdfplumber_available:
            text = self._extract_with_pdfplumber(pdf_path)
            if text:
                return text

        if self.pypdf2_available:
            text = self._extract_with_pypdf2(pdf_path)
            if text:
                return text

        print(f"[ERROR] No PDF processing libraries available for: {pdf_path}")
        return None

    def _extract_with_pymupdf(self, pdf_path: Path) -> Optional[str]:
        """Extract text using PyMuPDF (fitz)"""
        try:
            import fitz
            doc = fitz.open(str(pdf_path))
            text = ""

            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text += page.get_text()

            doc.close()
            return text

        except Exception as e:
            print(f"[ERROR] PyMuPDF extraction failed: {e}")
            return None

    def _extract_with_pdfplumber(self, pdf_path: Path) -> Optional[str]:
        """Extract text using pdfplumber"""
        try:
            import pdfplumber
            text = ""

            with pdfplumber.open(str(pdf_path)) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""

            return text

        except Exception as e:
            print(f"[ERROR] pdfplumber extraction failed: {e}")
            return None

    def _extract_with_pypdf2(self, pdf_path: Path) -> Optional[str]:
        """Extract text using PyPDF2"""
        try:
            from PyPDF2 import PdfReader
            text = ""

            with open(pdf_path, 'rb') as file:
                reader = PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text()

            return text

        except Exception as e:
            print(f"[ERROR] PyPDF2 extraction failed: {e}")
            return None

    def identify_document_type(self, pdf_path: Path, text: str) -> str:
        """
        Identify the type of document based on filename and content

        Args:
            pdf_path: Path to PDF file
            text: Extracted text

        Returns:
            Document type
        """
        filename_lower = pdf_path.name.lower()
        text_lower = text.lower()

        # Check filename first
        if "budget" in filename_lower:
            return "budget_document"
        elif "financial" in filename_lower or "cafr" in filename_lower:
            return "financial_report"
        elif "tax" in filename_lower and "profile" in filename_lower:
            return "tax_profile"
        elif "demographic" in filename_lower or "population" in filename_lower:
            return "demographic_report"

        # Check content
        for doc_type, config in self.extraction_patterns.items():
            keyword_count = sum(1 for keyword in config["keywords"] if keyword in text_lower)
            if keyword_count >= 2:  # Need at least 2 keywords to match
                return doc_type

        return "unknown"

    def extract_structured_data(self, text: str, document_type: str) -> Dict[str, Any]:
        """
        Extract structured data from text based on document type

        Args:
            text: Extracted PDF text
            document_type: Type of document

        Returns:
            Structured data
        """
        if document_type not in self.extraction_patterns:
            return {"document_type": document_type, "extracted_data": {}}

        patterns = self.extraction_patterns[document_type]["patterns"]
        extracted_data = {}

        for field_name, pattern in patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            if matches:
                # Convert numeric strings to actual numbers
                processed_matches = []
                for match in matches:
                    if isinstance(match, tuple):
                        # Handle groups
                        processed_match = []
                        for group in match:
                            processed_match.append(self._clean_numeric_string(group))
                        processed_matches.append(processed_match)
                    else:
                        processed_matches.append(self._clean_numeric_string(match))

                extracted_data[field_name] = processed_matches

        return {
            "document_type": document_type,
            "extracted_data": extracted_data,
            "extraction_timestamp": datetime.now().isoformat()
        }

    def _clean_numeric_string(self, value: str) -> Any:
        """
        Clean and convert numeric strings

        Args:
            value: String to clean

        Returns:
            Cleaned value (int, float, or string)
        """
        if not value:
            return value

        # Remove common formatting
        cleaned = re.sub(r'[$,%]', '', str(value).strip())

        # Check for millions/billions
        if re.search(r'\d+\s*(?:million|billion)', cleaned, re.IGNORECASE):
            return cleaned  # Keep as string for manual review

        # Try to convert to number
        try:
            if '.' in cleaned:
                return float(cleaned)
            else:
                return int(cleaned)
        except ValueError:
            return cleaned

    def extract_tables(self, pdf_path: Path) -> List[List[List[str]]]:
        """
        Extract tables from PDF using available libraries

        Args:
            pdf_path: Path to PDF file

        Returns:
            List of tables (each table is list of rows, each row is list of cells)
        """
        tables = []

        if self.pdfplumber_available:
            tables = self._extract_tables_pdfplumber(pdf_path)

        if not tables and self.pymupdf_available:
            tables = self._extract_tables_pymupdf(pdf_path)

        return tables

    def _extract_tables_pdfplumber(self, pdf_path: Path) -> List[List[List[str]]]:
        """Extract tables using pdfplumber"""
        try:
            import pdfplumber
            tables = []

            with pdfplumber.open(str(pdf_path)) as pdf:
                for page in pdf.pages:
                    page_tables = page.extract_tables()
                    for table in page_tables:
                        if table and len(table) > 1:  # At least header + 1 data row
                            tables.append(table)

            return tables

        except Exception as e:
            print(f"[ERROR] pdfplumber table extraction failed: {e}")
            return []

    def _extract_tables_pymupdf(self, pdf_path: Path) -> List[List[List[str]]]:
        """Extract tables using PyMuPDF"""
        try:
            import fitz
            tables = []

            doc = fitz.open(str(pdf_path))
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                # PyMuPDF table extraction is more complex, this is a basic implementation
                # In practice, you might want to use specialized table extraction
                tables_found = page.find_tables()
                for table in tables_found:
                    table_data = table.extract()
                    tables.append(table_data)

            doc.close()
            return tables

        except Exception as e:
            print(f"[ERROR] PyMuPDF table extraction failed: {e}")
            return []

    def process_single_pdf(self, pdf_path: Path) -> Dict[str, Any]:
        """
        Process a single PDF file

        Args:
            pdf_path: Path to PDF file

        Returns:
            Processing results
        """
        print(f"\n[PROCESSING] {pdf_path.name}")

        result = {
            "pdf_filename": pdf_path.name,
            "pdf_path": str(pdf_path),
            "processing_timestamp": datetime.now().isoformat(),
            "success": False,
            "text_extracted": False,
            "document_type": None,
            "extracted_data": {},
            "tables_extracted": [],
            "errors": []
        }

        try:
            # Extract text
            text = self.extract_pdf_text(pdf_path)
            if text:
                result["text_extracted"] = True
                result["text_length"] = len(text)

                # Identify document type
                result["document_type"] = self.identify_document_type(pdf_path, text)

                # Extract structured data
                structured_data = self.extract_structured_data(text, result["document_type"])
                result["extracted_data"] = structured_data

                print(f"   [SUCCESS] Text extracted ({len(text)} characters)")
                print(f"   [INFO] Document type: {result['document_type']}")
                print(f"   [INFO] Data fields extracted: {len(structured_data.get('extracted_data', {}))}")

            else:
                result["errors"].append("Failed to extract text from PDF")

            # Extract tables
            tables = self.extract_tables(pdf_path)
            if tables:
                result["tables_extracted"] = tables
                print(f"   [INFO] Tables extracted: {len(tables)}")

            result["success"] = True

        except Exception as e:
            error_msg = f"Processing failed: {str(e)}"
            result["errors"].append(error_msg)
            print(f"   [ERROR] {error_msg}")

        return result

    def save_extraction_results(self, result: Dict[str, Any]) -> Dict[str, str]:
        """
        Save extraction results in multiple formats

        Args:
            result: Processing results

        Returns:
            Dictionary of saved file paths
        """
        saved_files = {}
        base_filename = Path(result["pdf_filename"]).stem
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save structured data as JSON
        if result["extracted_data"]:
            json_filename = f"{timestamp}_{base_filename}_extracted.json"
            json_filepath = self.output_dir / json_filename

            with open(json_filepath, 'w') as f:
                json.dump(result["extracted_data"], f, indent=2)

            saved_files["json"] = str(json_filepath)
            print(f"   [SAVED] JSON data: {json_filename}")

        # Save tables as CSV
        if result["tables_extracted"]:
            for i, table in enumerate(result["tables_extracted"]):
                if table and len(table) > 1:  # Has data
                    csv_filename = f"{timestamp}_{base_filename}_table_{i+1}.csv"
                    csv_filepath = self.output_dir / csv_filename

                    with open(csv_filepath, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerows(table)

                    saved_files[f"csv_table_{i+1}"] = str(csv_filepath)
                    print(f"   [SAVED] Table {i+1} as CSV: {csv_filename}")

        # Save full processing results
        results_filename = f"{timestamp}_{base_filename}_processing_results.json"
        results_filepath = self.output_dir / results_filename

        with open(results_filepath, 'w') as f:
            json.dump(result, f, indent=2)

        saved_files["results"] = str(results_filepath)
        print(f"   [SAVED] Full results: {results_filename}")

        return saved_files

    def process_all_pdfs(self, pdf_directory: Path = None) -> Dict[str, Any]:
        """
        Process all PDF files in directory

        Args:
            pdf_directory: Directory containing PDFs (uses default if None)

        Returns:
            Comprehensive processing results
        """
        if pdf_directory is None:
            pdf_directory = self.pdf_dir

        if not pdf_directory.exists():
            print(f"[ERROR] PDF directory not found: {pdf_directory}")
            return {"error": "PDF directory not found"}

        # Find all PDF files
        pdf_files = list(pdf_directory.glob("*.pdf"))
        if not pdf_files:
            print(f"[INFO] No PDF files found in {pdf_directory}")
            return {"info": "No PDF files found"}

        print(f"\n{'='*80}")
        print(f"PROCESSING {len(pdf_files)} PDF FILES")
        print(f"Source directory: {pdf_directory}")
        print(f"Output directory: {self.output_dir}")
        print(f"{'='*80}")

        all_results = {
            "processing_session": {
                "start_time": datetime.now().isoformat(),
                "total_pdfs": len(pdf_files),
                "pdf_directory": str(pdf_directory),
                "output_directory": str(self.output_dir)
            },
            "pdf_results": {},
            "summary": {}
        }

        successful = 0
        failed = 0
        document_type_counts = {}
        total_data_fields = 0
        total_tables = 0

        for pdf_path in pdf_files:
            result = self.process_single_pdf(pdf_path)
            all_results["pdf_results"][pdf_path.name] = result

            if result["success"]:
                successful += 1

                # Count document types
                doc_type = result.get("document_type", "unknown")
                document_type_counts[doc_type] = document_type_counts.get(doc_type, 0) + 1

                # Count data fields
                data_fields = len(result.get("extracted_data", {}).get("extracted_data", {}))
                total_data_fields += data_fields

                # Count tables
                tables = len(result.get("tables_extracted", []))
                total_tables += tables

                # Save results
                saved_files = self.save_extraction_results(result)
                result["saved_files"] = saved_files

            else:
                failed += 1

        # Create summary
        all_results["summary"] = {
            "end_time": datetime.now().isoformat(),
            "successful": successful,
            "failed": failed,
            "success_rate": f"{(successful / len(pdf_files) * 100):.1f}%",
            "document_types": document_type_counts,
            "total_data_fields_extracted": total_data_fields,
            "total_tables_extracted": total_tables,
            "files_processed": len(pdf_files)
        }

        # Save comprehensive results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_filename = f"pdf_processing_summary_{timestamp}.json"
        summary_filepath = self.output_dir / summary_filename

        with open(summary_filepath, 'w') as f:
            json.dump(all_results, f, indent=2)

        print(f"\n{'='*80}")
        print(f"PDF PROCESSING COMPLETE!")
        print(f"{'='*80}")
        print(f"Files processed: {all_results['summary']['files_processed']}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        print(f"Success rate: {all_results['summary']['success_rate']}")
        print(f"Document types found: {list(document_type_counts.keys())}")
        print(f"Total data fields extracted: {total_data_fields}")
        print(f"Total tables extracted: {total_tables}")
        print(f"Results saved to: {summary_filepath}")
        print(f"Extracted data saved to: {self.output_dir}")

        return all_results

    def create_manual_download_guide(self) -> str:
        """
        Create a guide for manual PDF downloads

        Returns:
            Path to created guide file
        """
        guide_content = f"""# Westchester County PDF Download Guide

## Purpose
This guide provides instructions for downloading the PDF documents needed to complete the Westchester Municipal Administrator platform with real data.

## Priority Downloads

### 1. Budget Documents (HIGHEST PRIORITY)
**Source**: https://www.westchestergov.com/county-budgets

**Files Needed**:
- 2025 Adopted Operating Budget
- 2024 Adopted Operating Budget
- 2023 Adopted Operating Budget
- 2022 Adopted Operating Budget
- 2021 Adopted Operating Budget
- 2020 Adopted Operating Budget

**Instructions**:
1. Visit the URL above
2. Look for "Adopted Operating Budget" or similar links
3. Download PDF for each year (2020-2025)
4. Save to: `{self.pdf_dir}/budgets/`

**Data Expected**: Total budget amounts, department allocations, planning department budget

### 2. Annual Comprehensive Financial Reports (ACFRs)
**Source**: https://finance.westchestergov.com/?id=136&view=category

**Files Needed**:
- ACFR for each year 2015-2024 (if available)

**Instructions**:
1. Visit the URL above
2. Look for "Annual Comprehensive Financial Report" or "ACFR"
3. Download reports for available years
4. Save to: `{self.pdf_dir}/financial_reports/`

**Data Expected**: Historical expenditures, revenues, fund balances

### 3. NY State Tax Municipal Profiles
**Source**: https://www.tax.ny.gov/research/property/reports.htm

**Files Needed**:
- Tax profiles for major Westchester municipalities
- Focus on: Yonkers, White Plains, New Rochelle, Mount Vernon, Scarsdale
- Years: 2020-2024

**Instructions**:
1. Visit the NY State tax website
2. Navigate to "Municipal Profiles" or "Property Tax Reports"
3. Find Westchester municipalities
4. Download PDF profiles for recent years
5. Save to: `{self.pdf_dir}/tax_profiles/`

**Data Expected**: Effective tax rates, tax levies, assessed values

### 4. County Databook (Optional Enhancement)
**Source**: https://planning.westchestergov.com/census-and-statistics/databook

**Instructions**:
1. Visit the Planning Department website
2. Look for "County Databook" or "Data Book"
3. Download the latest edition
4. Save to: `{self.pdf_dir}/databook/`

## After Downloading

1. Organize files in the recommended directory structure
2. Run the PDF processor: `python pdf_data_extractor.py`
3. The processor will automatically:
   - Extract text from all PDFs
   - Identify document types
   - Extract structured data
   - Save results as JSON and CSV files

## Directory Structure

```
{self.pdf_dir}/
├── budgets/           # County budget documents
├── financial_reports/ # ACFR documents
├── tax_profiles/      # NY State tax profiles
├── databook/          # County databook
└── other/             # Additional documents

{self.output_dir}/      # Processed data (auto-generated)
├── *.json            # Extracted structured data
├── *.csv             # Extracted tables
└── *_processing_results.json  # Full processing results
```

## Troubleshooting

**If PDFs are password protected**:
- Look for "unprotected" or "public" versions
- Contact the department for public copies

**If downloads are slow**:
- Download one file at a time
- Use a wired internet connection if possible
- Try downloading during off-peak hours

**If processing fails**:
- Ensure PDFs are not corrupted (try opening them manually)
- Check that PDFs contain text (not scanned images only)
- Run the processor again after installing PDF libraries

## Processing Libraries Required

For best results, install these Python libraries:
```bash
pip install pdfplumber PyMuPDF PyPDF2
```

## Expected Output

After processing, you should have:
- JSON files with extracted budget and financial data
- CSV files with tabular data from PDFs
- Processing results showing what was extracted from each file

This data will be used to replace sample data in the Westchester Municipal Administrator platform.

---
*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

        guide_filename = "pdf_download_guide.md"
        guide_filepath = self.pdf_dir / guide_filename

        with open(guide_filepath, 'w') as f:
            f.write(guide_content)

        return str(guide_filepath)


def main():
    """Command-line interface for PDF processing"""
    print("=" * 80)
    print("WESTCHESTER COUNTY PDF DATA EXTRACTOR")
    print("Processes downloaded PDF documents to extract structured data")
    print("=" * 80)
    print()

    # Check for PDF directory
    pdf_dir = Path(__file__).parent.parent.parent / "data" / "raw" / "manual_downloads"

    if not pdf_dir.exists():
        print(f"PDF directory not found: {pdf_dir}")
        print("Creating directory and download guide...")
        pdf_dir.mkdir(parents=True, exist_ok=True)

        extractor = PDFDataExtractor(pdf_dir)
        guide_path = extractor.create_manual_download_guide()
        print(f"\nDownload guide created: {guide_path}")
        print(f"Please download PDFs according to the guide and run this script again.")
        return

    # Count PDFs
    pdf_files = list(pdf_dir.glob("**/*.pdf"))
    print(f"Found {len(pdf_files)} PDF files in {pdf_dir}")

    if not pdf_files:
        print("No PDF files found. Please download PDFs first.")
        extractor = PDFDataExtractor(pdf_dir)
        guide_path = extractor.create_manual_download_guide()
        print(f"Download guide created: {guide_path}")
        return

    # Process all PDFs
    extractor = PDFDataExtractor()
    results = extractor.process_all_pdfs()

    print()
    if results.get("summary", {}).get("success_rate", "0") == "100.0%":
        print("[SUCCESS] All PDFs processed successfully!")
    else:
        success_rate = results.get("summary", {}).get("success_rate", "0%")
        print(f"[COMPLETED] PDFs processed with {success_rate} success rate.")

    print(f"Extracted data saved to: {extractor.output_dir}")
    print("\nNext steps:")
    print("1. Review the extracted JSON and CSV files")
    print("2. Update the Westchester platform with real data")
    print("3. Validate data accuracy before deployment")


if __name__ == "__main__":
    main()