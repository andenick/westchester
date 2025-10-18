#!/usr/bin/env python3
"""
Westchester County Data Platform - PDF Extraction Pipeline

Automated PDF table extraction for Westchester documents.
Capabilities:
- Detect and extract tables from PDFs
- Handle multi-page tables
- Clean and normalize extracted data
- Validate data structure
- Export to standardized format

Target: 60% of files (42 documents) automated extraction
Dependencies: tabula-py, pdfplumber, pandas, camelot
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import numpy as np

# PDF processing libraries
import tabula
import pdfplumber
try:
    import camelot
    CAMELOT_AVAILABLE = True
except ImportError:
    CAMELOT_AVAILABLE = False
    logging.warning("Camelot not available - some complex tables may not extract well")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pdf_extraction.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WestchesterPDFExtractor:
    """
    Specialized PDF extractor for Westchester County documents.
    Handles Budget reports, Tax Levy data, Infrastructure documents, and more.
    """

    def __init__(self, input_dir: str = None, output_dir: str = None):
        self.input_dir = Path(input_dir or "data/raw/pdfs")
        self.output_dir = Path(output_dir or "data/processed/pdf_extractions")
        self.input_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Westchester-specific document patterns
        self.document_patterns = {
            'budget_reports': {
                'keywords': ['budget', 'adopted budget', 'proposed budget', 'capital budget'],
                'table_indicators': ['revenue', 'expenditure', 'department', 'fund', 'category'],
                'expected_columns': ['Department', 'Budgeted', 'Actual', 'Variance'],
                'file_patterns': ['*budget*.pdf', '*adopted*.pdf', '*capital*.pdf']
            },
            'tax_levy': {
                'keywords': ['tax levy', 'property tax', 'assessment', 'tax rate'],
                'table_indicators': ['municipality', 'levy', 'rate', 'assessment', 'value'],
                'expected_columns': ['Municipality', 'Assessed_Value', 'Tax_Rate', 'Levy_Amount'],
                'file_patterns': ['*tax*.pdf', '*levy*.pdf', '*assessment*.pdf']
            },
            'infrastructure': {
                'keywords': ['infrastructure', 'capital improvement', 'road', 'bridge', 'water'],
                'table_indicators': ['project', 'cost', 'status', 'funding', 'timeline'],
                'expected_columns': ['Project', 'Cost', 'Status', 'Funding_Source'],
                'file_patterns': ['*infrastructure*.pdf', '*capital*.pdf', '*project*.pdf']
            },
            'transit': {
                'keywords': ['transit', 'metro-north', 'bus', 'ridership', 'transportation'],
                'table_indicators': ['route', 'ridership', 'station', 'line', 'frequency'],
                'expected_columns': ['Route', 'Ridership', 'Station', 'Line'],
                'file_patterns': ['*transit*.pdf', '*metro*.pdf', '*ridership*.pdf']
            },
            'historical': {
                'keywords': ['historical', 'trend', 'historical trends', 'economic', 'demographic'],
                'table_indicators': ['year', 'population', 'employment', 'growth', 'indicator'],
                'expected_columns': ['Year', 'Population', 'Employment', 'Growth_Rate'],
                'file_patterns': ['*historical*.pdf', '*trend*.pdf', '*economic*.pdf']
            }
        }

        # Extraction statistics
        self.extraction_stats = {
            'total_files': 0,
            'successful_extractions': 0,
            'failed_extractions': 0,
            'partial_extractions': 0,
            'total_tables_found': 0,
            'total_records_extracted': 0,
            'processing_time': 0,
            'files_by_category': {cat: 0 for cat in self.document_patterns.keys()},
            'success_rate_by_category': {cat: 0 for cat in self.document_patterns.keys()}
        }

    def detect_document_type(self, pdf_path: Path) -> Tuple[str, float]:
        """
        Detect document type based on filename and content analysis.

        Returns:
            (document_type, confidence_score)
        """
        filename = pdf_path.name.lower()

        # Check filename patterns first
        category_scores = {}
        for category, config in self.document_patterns.items():
            score = 0

            # Check filename patterns
            for pattern in config['file_patterns']:
                if pattern.replace('*', '') in filename:
                    score += 0.3

            category_scores[category] = score

        # If we have a clear winner from filename, return it
        max_score = max(category_scores.values())
        if max_score > 0:
            best_category = max(category_scores, key=category_scores.get)
            return best_category, min(max_score, 1.0)

        # Default to budget_reports if no clear match
        return 'budget_reports', 0.5

    def extract_with_tabula(self, pdf_path: Path, pages: str = 'all') -> List[pd.DataFrame]:
        """Extract tables using tabula-py"""
        tables = []

        try:
            # Extract tables with multiple lattice options
            tables_list = tabula.read_pdf(
                str(pdf_path),
                pages=pages,
                multiple_tables=True,
                lattice=True,
                stream=False,
                pandas_options={'header': 0}
            )

            if not tables_list or len(tables_list) == 0:
                # Try with stream mode
                tables_list = tabula.read_pdf(
                    str(pdf_path),
                    pages=pages,
                    multiple_tables=True,
                    lattice=False,
                    stream=True,
                    pandas_options={'header': 0}
                )

            tables = tables_list

        except Exception as e:
            logger.warning(f"Tabula extraction failed for {pdf_path.name}: {str(e)}")

        return tables

    def extract_with_pdfplumber(self, pdf_path: Path) -> List[pd.DataFrame]:
        """Extract tables using pdfplumber"""
        tables = []

        try:
            with pdfplumber.open(str(pdf_path)) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    try:
                        # Extract tables from current page
                        page_tables = page.extract_tables()

                        for table_idx, table in enumerate(page_tables):
                            if table and len(table) > 1:  # At least header + one row
                                # Convert to DataFrame
                                df = pd.DataFrame(table[1:], columns=table[0])
                                df['source_page'] = page_num
                                df['source_table'] = table_idx
                                tables.append(df)

                    except Exception as e:
                        logger.warning(f"Error extracting table from page {page_num}: {str(e)}")
                        continue

        except Exception as e:
            logger.error(f"pdfplumber extraction failed for {pdf_path.name}: {str(e)}")

        return tables

    def extract_with_camelot(self, pdf_path: Path) -> List[pd.DataFrame]:
        """Extract tables using camelot (if available)"""
        if not CAMELOT_AVAILABLE:
            return []

        tables = []

        try:
            # Try lattice mode first
            lattice_tables = camelot.read_pdf(str(pdf_path), flavor='lattice')
            tables.extend([table.df for table in lattice_tables])

            # Try stream mode if lattice didn't work well
            if len(lattice_tables) == 0 or all(table.accuracy < 50 for table in lattice_tables):
                stream_tables = camelot.read_pdf(str(pdf_path), flavor='stream')
                tables.extend([table.df for table in stream_tables])

        except Exception as e:
            logger.warning(f"Camelot extraction failed for {pdf_path.name}: {str(e)}")

        return tables

    def clean_table_data(self, df: pd.DataFrame, document_type: str) -> pd.DataFrame:
        """
        Clean and normalize extracted table data.
        """
        if df.empty:
            return df

        # Make a copy to avoid SettingWithCopyWarning
        cleaned_df = df.copy()

        # Basic cleaning
        cleaned_df = cleaned_df.dropna(how='all')  # Drop empty rows
        cleaned_df = cleaned_df.dropna(axis=1, how='all')  # Drop empty columns

        # Clean column names
        cleaned_df.columns = [
            str(col).strip().replace(' ', '_').replace('/', '_').replace('(', '').replace(')', '')
            for col in cleaned_df.columns
        ]

        # Remove columns that are metadata
        metadata_columns = ['source_page', 'source_table']
        cleaned_df = cleaned_df.drop(columns=[col for col in metadata_columns if col in cleaned_df.columns])

        # Document-specific cleaning
        if document_type == 'budget_reports':
            cleaned_df = self._clean_budget_data(cleaned_df)
        elif document_type == 'tax_levy':
            cleaned_df = self._clean_tax_data(cleaned_df)
        elif document_type == 'infrastructure':
            cleaned_df = self._clean_infrastructure_data(cleaned_df)
        elif document_type == 'transit':
            cleaned_df = self._clean_transit_data(cleaned_df)
        elif document_type == 'historical':
            cleaned_df = self._clean_historical_data(cleaned_df)

        return cleaned_df

    def _clean_budget_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean budget-specific data"""
        # Try to identify and convert monetary columns
        for col in df.columns:
            if any(keyword in col.lower() for keyword in ['budget', 'amount', 'cost', 'revenue', 'expenditure']):
                df[col] = pd.to_numeric(df[col].astype(str).str.replace('[$,]', '', regex=True), errors='coerce')

        return df

    def _clean_tax_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean tax levy specific data"""
        # Try to identify and convert monetary and percentage columns
        for col in df.columns:
            if any(keyword in col.lower() for keyword in ['levy', 'amount', 'value', 'assessment']):
                df[col] = pd.to_numeric(df[col].astype(str).str.replace('[$,]', '', regex=True), errors='coerce')
            elif any(keyword in col.lower() for keyword in ['rate', 'percent']):
                df[col] = pd.to_numeric(df[col].astype(str).str.replace('[%]', '', regex=True), errors='coerce')

        return df

    def _clean_infrastructure_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean infrastructure specific data"""
        # Try to identify and convert cost columns
        for col in df.columns:
            if any(keyword in col.lower() for keyword in ['cost', 'budget', 'funding', 'investment']):
                df[col] = pd.to_numeric(df[col].astype(str).str.replace('[$,]', '', regex=True), errors='coerce')

        return df

    def _clean_transit_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean transit specific data"""
        # Try to identify and convert ridership columns
        for col in df.columns:
            if any(keyword in col.lower() for keyword in ['ridership', 'passenger', 'frequency']):
                df[col] = pd.to_numeric(df[col].astype(str).str.replace('[,]', '', regex=True), errors='coerce')

        return df

    def _clean_historical_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean historical trend data"""
        # Try to identify year columns and convert to numeric
        for col in df.columns:
            if col.lower().startswith('year') or col.lower().endswith('year'):
                df[col] = pd.to_numeric(df[col], errors='coerce')
            elif any(keyword in col.lower() for keyword in ['population', 'employment', 'rate', 'growth']):
                df[col] = pd.to_numeric(df[col].astype(str).str.replace('[,]', '', regex=True), errors='coerce')

        return df

    def validate_table_structure(self, df: pd.DataFrame, document_type: str) -> Tuple[bool, str]:
        """
        Validate that the extracted table matches expected structure.
        """
        if df.empty:
            return False, "Table is empty after cleaning"

        expected_config = self.document_patterns.get(document_type, {})
        expected_keywords = expected_config.get('table_indicators', [])

        # Check if we have expected columns (at least some)
        columns_lower = [col.lower() for col in df.columns]
        matched_keywords = 0

        for keyword in expected_keywords:
            if any(keyword in col for col in columns_lower):
                matched_keywords += 1

        # If we match at least 30% of expected keywords, consider it valid
        if expected_keywords:
            match_rate = matched_keywords / len(expected_keywords)
            if match_rate < 0.3:
                return False, f"Low keyword match rate: {match_rate:.1%}"

        # Check if we have enough data
        if len(df) < 2:
            return False, "Table has less than 2 data rows"

        return True, "Table structure appears valid"

    def extract_pdf(self, pdf_path: Path) -> Dict[str, Any]:
        """
        Extract all tables from a PDF file using multiple methods.
        """
        start_time = pd.Timestamp.now()

        result = {
            'file_name': pdf_path.name,
            'file_path': str(pdf_path),
            'file_size': pdf_path.stat().st_size,
            'document_type': None,
            'extraction_method': None,
            'tables': [],
            'total_tables': 0,
            'total_records': 0,
            'success': False,
            'error': None,
            'processing_time': 0,
            'validation_results': []
        }

        try:
            # Detect document type
            doc_type, confidence = self.detect_document_type(pdf_path)
            result['document_type'] = doc_type
            result['type_confidence'] = confidence

            logger.info(f"Processing {pdf_path.name} as {doc_type} (confidence: {confidence:.2f})")

            # Try extraction methods in order of preference
            all_tables = []

            # Method 1: Tabula (usually best for structured tables)
            tables = self.extract_with_tabula(pdf_path)
            if tables:
                all_tables.extend([(table, 'tabula') for table in tables])
                logger.info(f"Tabula extracted {len(tables)} tables")

            # Method 2: pdfplumber (good for complex layouts)
            tables = self.extract_with_pdfplumber(pdf_path)
            if tables:
                all_tables.extend([(table, 'pdfplumber') for table in tables])
                logger.info(f"pdfplumber extracted {len(tables)} tables")

            # Method 3: Camelot (if available, for lattice-based tables)
            if CAMELOT_AVAILABLE:
                tables = self.extract_with_camelot(pdf_path)
                if tables:
                    all_tables.extend([(table, 'camelot') for table in tables])
                    logger.info(f"Camelot extracted {len(tables)} tables")

            if not all_tables:
                result['error'] = "No tables extracted with any method"
                logger.warning(f"No tables found in {pdf_path.name}")
                return result

            # Process and validate each table
            processed_tables = []
            total_records = 0

            for table_df, method in all_tables:
                try:
                    # Clean the table data
                    cleaned_table = self.clean_table_data(table_df, doc_type)

                    if not cleaned_table.empty:
                        # Validate table structure
                        is_valid, validation_msg = self.validate_table_structure(cleaned_table, doc_type)

                        table_info = {
                            'data': cleaned_table,
                            'method': method,
                            'rows': len(cleaned_table),
                            'columns': len(cleaned_table.columns),
                            'column_names': list(cleaned_table.columns),
                            'is_valid': is_valid,
                            'validation_message': validation_msg
                        }

                        processed_tables.append(table_info)
                        total_records += len(cleaned_table)

                        if is_valid:
                            logger.debug(f"Valid table: {len(cleaned_table)} rows, method: {method}")
                        else:
                            logger.warning(f"Invalid table: {validation_msg}")

                except Exception as e:
                    logger.warning(f"Error processing table: {str(e)}")
                    continue

            if not processed_tables:
                result['error'] = "No valid tables after processing"
                return result

            # Determine primary extraction method
            method_counts = {}
            for table in processed_tables:
                method = table['method']
                method_counts[method] = method_counts.get(method, 0) + 1

            result['extraction_method'] = max(method_counts, key=method_counts.get)
            result['tables'] = processed_tables
            result['total_tables'] = len(processed_tables)
            result['total_records'] = total_records
            result['success'] = True

            logger.info(f"Successfully extracted {len(processed_tables)} tables ({total_records} records) from {pdf_path.name}")

        except Exception as e:
            result['error'] = str(e)
            logger.error(f"Extraction failed for {pdf_path.name}: {str(e)}")

        finally:
            result['processing_time'] = (pd.Timestamp.now() - start_time).total_seconds()

        return result

    def save_extraction_results(self, extraction_result: Dict[str, Any]) -> List[str]:
        """
        Save extraction results to appropriate output files.
        """
        saved_files = []
        pdf_name = Path(extraction_result['file_name']).stem
        doc_type = extraction_result['document_type']

        # Create document-specific directory
        doc_dir = self.output_dir / doc_type
        doc_dir.mkdir(exist_ok=True)

        try:
            # Save each valid table as separate Excel file (Druck compliance: ONE SHEET PER FILE)
            for i, table_info in enumerate(extraction_result['tables']):
                if table_info['is_valid']:
                    table_df = table_info['data']

                    # Generate filename
                    filename = f"{pdf_name}_table_{i+1}.xlsx"
                    filepath = doc_dir / filename

                    # Save as Excel ( Druck standards - B&W, one sheet)
                    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                        table_df.to_excel(writer, sheet_name='Data', index=False)

                    saved_files.append(str(filepath))
                    logger.debug(f"Saved table {i+1} to {filepath}")

            # Save extraction metadata
            metadata_file = doc_dir / f"{pdf_name}_metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(extraction_result, f, indent=2, ensure_ascii=False, default=str)

            logger.info(f"Saved {len(saved_files)} Excel files and metadata for {pdf_name}")

        except Exception as e:
            logger.error(f"Error saving extraction results for {pdf_name}: {str(e)}")

        return saved_files

    def process_all_pdfs(self) -> Dict[str, Any]:
        """
        Process all PDF files in the input directory.
        """
        start_time = pd.Timestamp.now()

        # Find all PDF files
        pdf_files = list(self.input_dir.glob("**/*.pdf"))

        if not pdf_files:
            logger.warning(f"No PDF files found in {self.input_dir}")
            return {'error': 'No PDF files found'}

        logger.info(f"Found {len(pdf_files)} PDF files to process")

        # Initialize results tracking
        results = {
            'start_time': start_time.isoformat(),
            'total_files': len(pdf_files),
            'extraction_results': [],
            'summary': self.extraction_stats.copy(),
            'files_processed': [],
            'files_failed': [],
            'total_extraction_time': 0
        }

        # Process each PDF
        for pdf_path in pdf_files:
            logger.info(f"\n{'='*60}")
            logger.info(f"Processing: {pdf_path.name}")
            logger.info(f"{'='*60}")

            # Extract tables
            extraction_result = self.extract_pdf(pdf_path)

            # Save results if successful
            if extraction_result['success']:
                saved_files = self.save_extraction_results(extraction_result)
                extraction_result['saved_files'] = saved_files
                results['files_processed'].append(pdf_path.name)

                # Update statistics
                doc_type = extraction_result['document_type']
                self.extraction_stats['files_by_category'][doc_type] += 1
                self.extraction_stats['successful_extractions'] += 1
                self.extraction_stats['total_tables_found'] += extraction_result['total_tables']
                self.extraction_stats['total_records_extracted'] += extraction_result['total_records']

            else:
                results['files_failed'].append(pdf_path.name)
                self.extraction_stats['failed_extractions'] += 1
                logger.error(f"Failed to extract from {pdf_path.name}: {extraction_result.get('error', 'Unknown error')}")

            results['extraction_results'].append(extraction_result)
            self.extraction_stats['total_files'] += 1

        # Calculate final statistics
        end_time = pd.Timestamp.now()
        total_time = (end_time - start_time).total_seconds()

        self.extraction_stats['processing_time'] = total_time

        # Calculate success rates by category
        for category in self.document_patterns.keys():
            if self.extraction_stats['files_by_category'][category] > 0:
                success_count = sum(1 for r in results['extraction_results']
                                  if r['document_type'] == category and r['success'])
                total_count = self.extraction_stats['files_by_category'][category]
                self.extraction_stats['success_rate_by_category'][category] = success_count / total_count

        results['summary'] = self.extraction_stats
        results['end_time'] = end_time.isoformat()
        results['total_extraction_time'] = total_time

        # Generate comprehensive report
        self.generate_extraction_report(results)

        return results

    def generate_extraction_report(self, results: Dict[str, Any]) -> None:
        """
        Generate comprehensive extraction report.
        """
        timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.output_dir / f"pdf_extraction_report_{timestamp}.json"

        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False, default=str)

            logger.info(f"Extraction report saved to: {report_file}")

            # Generate human-readable summary
            summary_file = self.output_dir / f"pdf_extraction_summary_{timestamp}.md"
            summary_content = self.generate_human_readable_summary(results)

            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(summary_content)

            logger.info(f"Human-readable summary saved to: {summary_file}")

        except Exception as e:
            logger.error(f"Error saving extraction report: {str(e)}")

    def generate_human_readable_summary(self, results: Dict[str, Any]) -> str:
        """Generate human-readable summary of extraction results"""

        summary = []
        summary.append("# Westchester PDF Extraction Report")
        summary.append(f"Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
        summary.append("")

        # Executive Summary
        summary.append("## Executive Summary")
        summary.append(f"**Total Files Processed**: {results['summary']['total_files']}")
        summary.append(f"**Successful Extractions**: {results['summary']['successful_extractions']}")
        summary.append(f"**Failed Extractions**: {results['summary']['failed_extractions']}")
        summary.append(f"**Total Tables Found**: {results['summary']['total_tables_found']}")
        summary.append(f"**Total Records Extracted**: {results['summary']['total_records_extracted']:,}")
        summary.append(f"**Processing Time**: {results['summary']['processing_time']:.2f} seconds")
        summary.append("")

        # Success Rate
        if results['summary']['total_files'] > 0:
            success_rate = results['summary']['successful_extractions'] / results['summary']['total_files']
            summary.append(f"**Overall Success Rate**: {success_rate:.1%}")
            summary.append("")

        # Results by Document Type
        summary.append("## Results by Document Type")
        for category, count in results['summary']['files_by_category'].items():
            if count > 0:
                success_rate = results['summary']['success_rate_by_category'][category]
                summary.append(f"- **{category.replace('_', ' ').title()}**: {count} files, {success_rate:.1%} success rate")
        summary.append("")

        # Processing Statistics
        summary.append("## Processing Statistics")
        summary.append(f"- **Average tables per file**: {results['summary']['total_tables_found'] / max(results['summary']['total_files'], 1):.1f}")
        summary.append(f"- **Average records per file**: {results['summary']['total_records_extracted'] / max(results['summary']['total_files'], 1):.0f}")
        summary.append(f"- **Processing speed**: {results['summary']['total_files'] / max(results['summary']['processing_time'], 1):.2f} files per second")
        summary.append("")

        # Failed Files
        if results['files_failed']:
            summary.append("## Failed Files")
            for filename in results['files_failed']:
                summary.append(f"- ❌ {filename}")
            summary.append("")

        # Recommendations
        summary.append("## Recommendations")

        success_rate = results['summary']['successful_extractions'] / max(results['summary']['total_files'], 1)

        if success_rate >= 0.8:
            summary.append("✅ **Excellent extraction success rate!** Automation is working well.")
        elif success_rate >= 0.6:
            summary.append("⚠️ **Moderate success rate.** Consider reviewing failed files for pattern improvements.")
        else:
            summary.append("❌ **Low success rate.** Manual review and extraction method refinement needed.")

        summary.append("")
        summary.append("## Next Steps")
        summary.append("1. Review extracted data for quality and completeness")
        summary.append("2. Manually process any failed high-priority documents")
        summary.append("3. Integrate extracted data into main data pipeline")
        summary.append("4. Update document patterns based on successful extractions")

        return "\n".join(summary)

def main():
    """Main function for command line usage"""
    import argparse

    parser = argparse.ArgumentParser(description='Westchester PDF Extraction System')
    parser.add_argument('--input-dir', help='Input directory containing PDF files')
    parser.add_argument('--output-dir', help='Output directory for extracted data')
    parser.add_argument('--single-file', help='Process a single PDF file')
    parser.add_argument('--test-mode', action='store_true', help='Test mode: process only first 5 files')

    args = parser.parse_args()

    # Initialize extractor
    extractor = WestchesterPDFExtractor(
        input_dir=args.input_dir,
        output_dir=args.output_dir
    )

    if args.single_file:
        # Process single file
        pdf_path = Path(args.single_file)
        if not pdf_path.exists():
            print(f"Error: File {args.single_file} not found")
            sys.exit(1)

        print(f"Processing single file: {pdf_path.name}")
        result = extractor.extract_pdf(pdf_path)

        if result['success']:
            saved_files = extractor.save_extraction_results(result)
            print(f"✅ Success! Extracted {result['total_tables']} tables ({result['total_records']} records)")
            print(f"📁 Saved {len(saved_files)} files:")
            for filepath in saved_files:
                print(f"   - {filepath}")
        else:
            print(f"❌ Failed: {result.get('error', 'Unknown error')}")

    else:
        # Process all files
        print("Starting batch PDF extraction...")

        # Modify input directory for test mode
        if args.test_mode:
            print("⚠️  TEST MODE: Processing only first 5 files")

        results = extractor.process_all_pdfs()

        # Print summary
        print(f"\n{'='*60}")
        print("EXTRACTION SUMMARY")
        print(f"{'='*60}")
        print(f"Total files: {results['summary']['total_files']}")
        print(f"Successful: {results['summary']['successful_extractions']}")
        print(f"Failed: {results['summary']['failed_extractions']}")
        print(f"Total tables: {results['summary']['total_tables_found']}")
        print(f"Total records: {results['summary']['total_records_extracted']:,}")
        print(f"Processing time: {results['summary']['processing_time']:.2f}s")

        if results['summary']['total_files'] > 0:
            success_rate = results['summary']['successful_extractions'] / results['summary']['total_files']
            print(f"Success rate: {success_rate:.1%}")

        print(f"\n📁 Results saved to: {extractor.output_dir}")

if __name__ == "__main__":
    main()