"""
Westchester County Data Platform - Output Validation Script

Comprehensive validation of all project outputs against Druck standards:
- LaTeX PDFs in Output/PDFs/
- Excel files in Output/Data/ (ONE SHEET each)
- Directory structure compliance (Shaikh Tonak pattern)
- Documentation completeness

Per AGENT_STANDARDS_AND_BEST_PRACTICES.md
"""

import sys
from pathlib import Path
import pandas as pd


class DruckValidator:
    """Validate project outputs against Druck standards."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.output_dir = project_root / "Output"
        self.technical_dir = project_root / "Technical"
        self.results = {
            'total_checks': 0,
            'passed': 0,
            'failed': 0,
            'warnings': 0,
            'checks': []
        }
    
    def add_check(self, name: str, status: str, message: str, is_critical: bool = False):
        """Add validation check result."""
        self.results['total_checks'] += 1
        
        if status == 'PASS':
            self.results['passed'] += 1
            symbol = '[PASS]'
        elif status == 'FAIL':
            self.results['failed'] += 1
            symbol = '[FAIL]'
        elif status == 'WARNING':
            self.results['warnings'] += 1
            symbol = '[WARN]'
        else:
            symbol = '[????]'
        
        self.results['checks'].append({
            'name': name,
            'status': status,
            'message': message,
            'is_critical': is_critical,
            'symbol': symbol
        })
        
        print(f"{symbol} {name}: {message}")
    
    def validate_directory_structure(self):
        """Validate Shaikh Tonak directory structure."""
        print("\n" + "="*80)
        print("DIRECTORY STRUCTURE VALIDATION (Shaikh Tonak Pattern)")
        print("="*80 + "\n")
        
        required_dirs = [
            (self.output_dir, "Output/", True),
            (self.output_dir / "Data", "Output/Data/", True),
            (self.output_dir / "PDFs", "Output/PDFs/", True),
            (self.technical_dir, "Technical/", True),
            (self.technical_dir / "src", "Technical/src/", True),
            (self.technical_dir / "docs", "Technical/docs/", True),
            (self.technical_dir / "scripts", "Technical/scripts/", True),
            (self.technical_dir / "data", "Technical/data/", False),
        ]
        
        for dir_path, dir_name, is_critical in required_dirs:
            if dir_path.exists():
                self.add_check(
                    f"Directory: {dir_name}",
                    "PASS",
                    "Exists",
                    is_critical
                )
            else:
                self.add_check(
                    f"Directory: {dir_name}",
                    "FAIL" if is_critical else "WARNING",
                    "Missing",
                    is_critical
                )
    
    def validate_latex_pdfs(self):
        """Validate LaTeX PDF outputs."""
        print("\n" + "="*80)
        print("LATEX PDF VALIDATION (Mandatory per Druck)")
        print("="*80 + "\n")
        
        pdf_dir = self.output_dir / "PDFs"
        
        if not pdf_dir.exists():
            self.add_check(
                "LaTeX PDFs Directory",
                "FAIL",
                "Output/PDFs/ directory missing",
                is_critical=True
            )
            return
        
        pdf_files = list(pdf_dir.glob("*.pdf"))
        
        if not pdf_files:
            self.add_check(
                "LaTeX PDFs",
                "FAIL",
                "No PDF files found in Output/PDFs/ (LaTeX reports required)",
                is_critical=True
            )
        else:
            self.add_check(
                "LaTeX PDFs",
                "PASS",
                f"{len(pdf_files)} PDF file(s) found",
                is_critical=True
            )
            
            for pdf in pdf_files:
                size_kb = pdf.stat().st_size / 1024
                self.add_check(
                    f"  PDF: {pdf.name}",
                    "PASS",
                    f"{size_kb:.1f} KB",
                    is_critical=False
                )
        
        # Check for expected report types
        expected_reports = [
            ("methodology_report", "Methodology Report"),
            ("analysis_report", "Analysis Report"),
            ("executive_summary", "Executive Summary"),
            ("reporting_strategy", "Reporting Strategy")
        ]
        
        for report_key, report_name in expected_reports:
            matching_pdfs = [p for p in pdf_files if report_key in p.name.lower()]
            if matching_pdfs:
                self.add_check(
                    f"  {report_name}",
                    "PASS",
                    f"Found: {matching_pdfs[0].name}",
                    is_critical=False
                )
            else:
                self.add_check(
                    f"  {report_name}",
                    "WARNING",
                    "Not found (expected per Druck standards)",
                    is_critical=False
                )
    
    def validate_latex_sources(self):
        """Validate LaTeX source files."""
        print("\n" + "="*80)
        print("LATEX SOURCE FILES VALIDATION")
        print("="*80 + "\n")
        
        docs_dir = self.technical_dir / "docs"
        
        if not docs_dir.exists():
            self.add_check(
                "LaTeX Sources Directory",
                "FAIL",
                "Technical/docs/ directory missing",
                is_critical=True
            )
            return
        
        tex_files = list(docs_dir.glob("*.tex"))
        
        if not tex_files:
            self.add_check(
                "LaTeX Sources",
                "FAIL",
                "No .tex files found in Technical/docs/",
                is_critical=True
            )
        else:
            self.add_check(
                "LaTeX Sources",
                "PASS",
                f"{len(tex_files)} .tex file(s) found",
                is_critical=True
            )
            
            for tex in tex_files:
                self.add_check(
                    f"  TEX: {tex.name}",
                    "PASS",
                    "Source file exists",
                    is_critical=False
                )
    
    def validate_excel_files(self):
        """Validate Excel files (ONE SHEET rule)."""
        print("\n" + "="*80)
        print("EXCEL FILES VALIDATION (ONE SHEET per file - Mandatory)")
        print("="*80 + "\n")
        
        data_dir = self.output_dir / "Data"
        
        if not data_dir.exists():
            self.add_check(
                "Excel Data Directory",
                "FAIL",
                "Output/Data/ directory missing",
                is_critical=True
            )
            return
        
        excel_files = list(data_dir.glob("**/*.xlsx"))
        # Filter out temp files
        excel_files = [f for f in excel_files if not f.name.startswith('~$')]
        
        if not excel_files:
            self.add_check(
                "Excel Files",
                "WARNING",
                "No Excel files found (will be created as data processing progresses)",
                is_critical=False
            )
            return
        
        self.add_check(
            "Excel Files Found",
            "PASS",
            f"{len(excel_files)} Excel file(s) to validate",
            is_critical=False
        )
        
        violations = 0
        for excel_file in excel_files:
            try:
                xl = pd.ExcelFile(excel_file)
                sheet_count = len(xl.sheet_names)
                
                if sheet_count == 1:
                    self.add_check(
                        f"  {excel_file.name}",
                        "PASS",
                        "ONE sheet (compliant)",
                        is_critical=True
                    )
                else:
                    self.add_check(
                        f"  {excel_file.name}",
                        "FAIL",
                        f"{sheet_count} sheets (VIOLATION - must be ONE)",
                        is_critical=True
                    )
                    violations += 1
            except Exception as e:
                self.add_check(
                    f"  {excel_file.name}",
                    "FAIL",
                    f"Error reading: {str(e)}",
                    is_critical=True
                )
                violations += 1
        
        if violations > 0:
            self.add_check(
                "ONE SHEET Rule Compliance",
                "FAIL",
                f"{violations} violation(s) found - FIX BEFORE HANDOFF",
                is_critical=True
            )
    
    def validate_documentation(self):
        """Validate documentation files."""
        print("\n" + "="*80)
        print("DOCUMENTATION VALIDATION")
        print("="*80 + "\n")
        
        required_docs = [
            (self.project_root / "README.md", "README.md", False),
            (self.project_root / "PROJECT_INDEX.md", "PROJECT_INDEX.md", True),
            (self.project_root / "HANDOFF_DOCUMENTATION.md", "HANDOFF_DOCUMENTATION.md", True),
            (self.output_dir / "README.md", "Output/README.md", True),
            (self.technical_dir / "README.md", "Technical/README.md", True),
            (self.technical_dir / "PROGRESS_LOG.md", "Technical/PROGRESS_LOG.md", True),
        ]
        
        for doc_path, doc_name, is_critical in required_docs:
            if doc_path.exists():
                size = doc_path.stat().st_size
                if size > 100:  # More than 100 bytes (not empty)
                    self.add_check(
                        f"Documentation: {doc_name}",
                        "PASS",
                        f"Exists ({size} bytes)",
                        is_critical
                    )
                else:
                    self.add_check(
                        f"Documentation: {doc_name}",
                        "WARNING",
                        "Exists but appears empty or minimal",
                        is_critical
                    )
            else:
                self.add_check(
                    f"Documentation: {doc_name}",
                    "FAIL" if is_critical else "WARNING",
                    "Missing",
                    is_critical
                )
    
    def validate_claude_config(self):
        """Validate Claude configuration."""
        print("\n" + "="*80)
        print("CLAUDE CONFIGURATION VALIDATION")
        print("="*80 + "\n")
        
        claude_dir = self.project_root / ".claude"
        
        if not claude_dir.exists():
            self.add_check(
                ".claude/ directory",
                "WARNING",
                "Missing (recommended for project-specific configuration)",
                is_critical=False
            )
            return
        
        config_files = [
            ("settings.local.json", True),
            ("instructions.md", True),
        ]
        
        for config_file, is_critical in config_files:
            config_path = claude_dir / config_file
            if config_path.exists():
                self.add_check(
                    f".claude/{config_file}",
                    "PASS",
                    "Exists",
                    is_critical
                )
            else:
                self.add_check(
                    f".claude/{config_file}",
                    "WARNING",
                    "Missing",
                    is_critical
                )
        
        commands_dir = claude_dir / "commands"
        if commands_dir.exists():
            command_files = list(commands_dir.glob("*.md"))
            self.add_check(
                ".claude/commands/",
                "PASS",
                f"{len(command_files)} command(s) defined",
                is_critical=False
            )
        else:
            self.add_check(
                ".claude/commands/",
                "WARNING",
                "Missing (custom commands recommended)",
                is_critical=False
            )
    
    def validate_data_structure(self):
        """Validate data directory structure."""
        print("\n" + "="*80)
        print("DATA STRUCTURE VALIDATION")
        print("="*80 + "\n")
        
        data_root = self.technical_dir / "data"
        
        if not data_root.exists():
            self.add_check(
                "Technical/data/",
                "WARNING",
                "Directory missing (will be created when data processing begins)",
                is_critical=False
            )
            return
        
        expected_subdirs = ["raw", "processed", "cache"]
        for subdir in expected_subdirs:
            subdir_path = data_root / subdir
            if subdir_path.exists():
                file_count = len(list(subdir_path.glob("*")))
                self.add_check(
                    f"data/{subdir}/",
                    "PASS",
                    f"Exists ({file_count} items)",
                    is_critical=False
                )
            else:
                self.add_check(
                    f"data/{subdir}/",
                    "WARNING",
                    "Missing (will be created as needed)",
                    is_critical=False
                )
    
    def print_summary(self):
        """Print validation summary."""
        print("\n" + "="*80)
        print("VALIDATION SUMMARY")
        print("="*80 + "\n")
        
        print(f"Total checks: {self.results['total_checks']}")
        print(f"[PASS] Passed: {self.results['passed']}")
        print(f"[WARN] Warnings: {self.results['warnings']}")
        print(f"[FAIL] Failed: {self.results['failed']}\n")
        
        # Critical failures
        critical_failures = [c for c in self.results['checks'] if c['is_critical'] and c['status'] == 'FAIL']
        
        if critical_failures:
            print(">>> CRITICAL FAILURES <<<")
            for check in critical_failures:
                print(f"  [FAIL] {check['name']}: {check['message']}")
            print("\n>>> FIX THESE ISSUES BEFORE HANDOFF")
            print(">>> Completion rating cannot exceed 75% with critical failures\n")
            return False
        
        elif self.results['failed'] > 0:
            print("[FAIL] Some non-critical failures found")
            print("[PASS] No critical violations - can proceed with caution\n")
            return True
        
        elif self.results['warnings'] > 0:
            print("[WARN] Some warnings found - review recommended")
            print("[PASS] No failures - Druck compliant\n")
            return True
        
        else:
            print("[PASS] ALL CHECKS PASSED")
            print("[PASS] Project is Druck compliant\n")
            return True
    
    def run_all_validations(self):
        """Run all validation checks."""
        print("\n" + "="*80)
        print("WESTCHESTER COUNTY - DRUCK COMPLIANCE VALIDATION")
        print("="*80)
        print(f"\nProject Root: {self.project_root}\n")
        
        self.validate_directory_structure()
        self.validate_latex_sources()
        self.validate_latex_pdfs()
        self.validate_excel_files()
        self.validate_documentation()
        self.validate_claude_config()
        self.validate_data_structure()
        
        is_compliant = self.print_summary()
        
        return is_compliant


def main():
    """Main validation function."""
    # Determine project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    
    # Run validation
    validator = DruckValidator(project_root)
    is_compliant = validator.run_all_validations()
    
    # Exit code
    sys.exit(0 if is_compliant else 1)


if __name__ == "__main__":
    main()

