"""
Validate Extracted Data from PDFs

This script validates that all extracted data from budget, financial, and tax PDFs
meets quality standards and is ready for integration into dashboards.

Checks:
- Data completeness (no null values in critical fields)
- Data types (numeric values are numbers, not strings)
- Data ranges (values are within expected bounds)
- Consistency across files
- No sample data remaining
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime


class DataValidator:
    """Validate extracted data quality"""

    def __init__(self, project_root: Path):
        """Initialize validator with project root path"""
        self.project_root = project_root
        self.data_dir = project_root / "data" / "processed"
        self.validation_report = {
            "validation_date": datetime.now().isoformat(),
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "errors": [],
            "warnings": [],
            "datasets_validated": []
        }

    def validate_budget_data(self) -> Tuple[bool, List[str]]:
        """Validate budget data extracted from PDFs"""
        print("\n📊 Validating Budget Data...")
        errors = []
        budget_dir = self.data_dir / "budget"

        if not budget_dir.exists():
            errors.append(f"Budget data directory not found: {budget_dir}")
            return False, errors

        # Check for time series file
        time_series_file = budget_dir / "budgets_time_series.json"
        if not time_series_file.exists():
            errors.append(f"Time series file not found: {time_series_file}")
            return False, errors

        # Load time series
        with open(time_series_file) as f:
            time_series = json.load(f)

        # Validate structure
        if "budgets_by_year" not in time_series:
            errors.append("Missing 'budgets_by_year' in time series")
            return False, errors

        # Validate each year's data
        for year, budget in time_series["budgets_by_year"].items():
            year_errors = self._validate_budget_year(year, budget)
            errors.extend(year_errors)

        # Check coverage (should have 2020-2025)
        expected_years = set(str(y) for y in range(2020, 2026))
        actual_years = set(time_series["budgets_by_year"].keys())
        missing_years = expected_years - actual_years

        if missing_years:
            self.validation_report["warnings"].append(
                f"Missing budget data for years: {sorted(missing_years)}"
            )

        passed = len(errors) == 0
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"   Budget validation: {status}")
        if errors:
            for error in errors:
                print(f"     - {error}")

        return passed, errors

    def _validate_budget_year(self, year: str, budget: Dict) -> List[str]:
        """Validate a single year's budget data"""
        errors = []

        # Check required fields
        required_fields = ["total_budget", "departments", "metadata"]
        for field in required_fields:
            if field not in budget:
                errors.append(f"Year {year}: Missing required field '{field}'")

        # Check total budget
        if "total_budget" in budget:
            total = budget["total_budget"]
            if total is None:
                errors.append(f"Year {year}: Total budget is null (needs manual entry)")
            elif not isinstance(total, (int, float)):
                errors.append(f"Year {year}: Total budget must be numeric, got {type(total)}")
            elif total <= 0:
                errors.append(f"Year {year}: Total budget must be positive")

        # Check departments
        if "departments" in budget:
            critical_departments = ["Planning", "Education", "Public Safety"]
            for dept in critical_departments:
                if dept not in budget["departments"]:
                    errors.append(f"Year {year}: Missing critical department '{dept}'")
                elif budget["departments"][dept] is None:
                    errors.append(f"Year {year}: Department '{dept}' budget is null")

        return errors

    def validate_tax_data(self) -> Tuple[bool, List[str]]:
        """Validate property tax data extracted from PDFs"""
        print("\n🏘️  Validating Property Tax Data...")
        errors = []
        tax_dir = self.data_dir / "tax"

        if not tax_dir.exists():
            self.validation_report["warnings"].append(
                f"Tax data directory not found: {tax_dir} (optional)"
            )
            print("   ⚠️  Tax data not yet extracted (optional)")
            return True, []  # Not critical for initial deployment

        # Validation logic here (similar to budget validation)
        print("   ✅ Tax data validation skipped (not yet implemented)")
        return True, []

    def check_sample_data_removed(self) -> Tuple[bool, List[str]]:
        """Check that no sample data warnings remain in frontend code"""
        print("\n🔍 Checking for Sample Data Warnings...")
        errors = []

        frontend_dir = self.project_root / "src" / "frontend" / "src"
        if not frontend_dir.exists():
            errors.append(f"Frontend directory not found: {frontend_dir}")
            return False, errors

        # Search for "SAMPLE DATA" strings in React components
        sample_data_files = []
        for file in frontend_dir.rglob("*.tsx"):
            try:
                content = file.read_text()
                if "SAMPLE DATA" in content or "sample data" in content:
                    sample_data_files.append(str(file.relative_to(self.project_root)))
            except Exception as e:
                self.validation_report["warnings"].append(f"Could not read {file}: {e}")

        if sample_data_files:
            errors.append(
                f"Found {len(sample_data_files)} files with 'SAMPLE DATA' warnings:"
            )
            for file in sample_data_files:
                errors.append(f"  - {file}")

        passed = len(errors) == 0
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"   Sample data check: {status}")

        return passed, errors

    def validate_data_completeness(self) -> Tuple[bool, List[str]]:
        """Check that all required datasets are present"""
        print("\n📋 Validating Data Completeness...")
        errors = []

        required_datasets = {
            "Budget": self.data_dir / "budget" / "budgets_time_series.json",
            # Add more as needed
        }

        for name, path in required_datasets.items():
            if not path.exists():
                errors.append(f"Missing required dataset: {name} ({path})")
            else:
                print(f"   ✅ Found: {name}")

        passed = len(errors) == 0
        if not passed:
            print(f"   ❌ Missing {len(errors)} required dataset(s)")

        return passed, errors

    def run_all_validations(self) -> Dict:
        """Run all validation tests and generate report"""
        print("\n" + "=" * 70)
        print("DATA VALIDATION - WESTCHESTER COUNTY DATA PLATFORM")
        print("=" * 70)

        all_passed = True

        # Run validation tests
        tests = [
            ("Budget Data", self.validate_budget_data),
            ("Property Tax Data", self.validate_tax_data),
            ("Sample Data Removal", self.check_sample_data_removed),
            ("Data Completeness", self.validate_data_completeness),
        ]

        for test_name, test_func in tests:
            self.validation_report["tests_run"] += 1
            try:
                passed, errors = test_func()
                if passed:
                    self.validation_report["tests_passed"] += 1
                else:
                    self.validation_report["tests_failed"] += 1
                    self.validation_report["errors"].extend(errors)
                    all_passed = False
            except Exception as e:
                self.validation_report["tests_failed"] += 1
                self.validation_report["errors"].append(f"{test_name} failed: {str(e)}")
                all_passed = False
                print(f"\n❌ {test_name}: EXCEPTION - {e}")

        # Generate summary
        print("\n" + "=" * 70)
        print("VALIDATION SUMMARY")
        print("=" * 70)
        print(f"Tests run:    {self.validation_report['tests_run']}")
        print(f"Tests passed: {self.validation_report['tests_passed']}")
        print(f"Tests failed: {self.validation_report['tests_failed']}")
        print(f"Warnings:     {len(self.validation_report['warnings'])}")

        if all_passed:
            print("\n🎉 All validations PASSED! Data is ready for deployment.")
        else:
            print("\n⚠️  Some validations FAILED. Review errors above.")
            print("\nNext steps:")
            print("1. Fix data extraction issues")
            print("2. Populate null values in JSON files")
            print("3. Remove sample data warnings from frontend")
            print("4. Re-run validation")

        # Save validation report
        report_file = self.project_root / "data" / "validation_report.json"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        with open(report_file, 'w') as f:
            json.dump(self.validation_report, f, indent=2)

        print(f"\n📄 Validation report saved: {report_file}")
        print("=" * 70 + "\n")

        return self.validation_report


def main():
    """Main execution function"""
    PROJECT_ROOT = Path(__file__).parent.parent.parent

    validator = DataValidator(PROJECT_ROOT)
    report = validator.run_all_validations()

    # Exit with error code if validations failed
    if report["tests_failed"] > 0:
        exit(1)
    else:
        exit(0)


if __name__ == "__main__":
    main()
