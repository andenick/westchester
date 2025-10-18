#!/usr/bin/env python3
"""
Westchester County Data Platform - Data Validation Pipeline

Validate extracted Westchester data against expected patterns.

Validation Rules:
- Data type consistency
- Value range validation
- Format compliance
- Completeness checks
- Cross-source validation

Dependencies: pandas, numpy, pytest
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_validation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WestchesterDataValidator:
    """
    Comprehensive data validation system for Westchester County data.
    Ensures data quality, consistency, and compliance with expected patterns.
    """

    def __init__(self, data_dir: str = None, output_dir: str = None):
        self.data_dir = Path(data_dir or "data/processed")
        self.output_dir = Path(output_dir or "data/validation_reports")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Westchester-specific validation rules
        self.validation_rules = {
            'budget_reports': {
                'required_columns': ['department', 'budgeted', 'actual', 'variance'],
                'optional_columns': ['fund', 'category', 'year', 'division'],
                'data_types': {
                    'department': 'object',
                    'budgeted': 'float64',
                    'actual': 'float64',
                    'variance': 'float64'
                },
                'value_ranges': {
                    'budgeted': {'min': 0, 'max': 1e10},
                    'actual': {'min': -1e9, 'max': 1e10},
                    'variance': {'min': -1e9, 'max': 1e9}
                },
                'completeness_threshold': 0.95,
                'duplicate_threshold': 0.1
            },
            'tax_levy': {
                'required_columns': ['municipality', 'levy_amount', 'tax_rate'],
                'optional_columns': ['assessment_value', 'year', 'tax_class', 'exemptions'],
                'data_types': {
                    'municipality': 'object',
                    'levy_amount': 'float64',
                    'tax_rate': 'float64'
                },
                'value_ranges': {
                    'levy_amount': {'min': 0, 'max': 1e10},
                    'tax_rate': {'min': 0, 'max': 100}
                },
                'completeness_threshold': 0.95,
                'duplicate_threshold': 0.05
            },
            'infrastructure': {
                'required_columns': ['project', 'cost', 'status'],
                'optional_columns': ['funding_source', 'timeline', 'department', 'location'],
                'data_types': {
                    'project': 'object',
                    'cost': 'float64',
                    'status': 'object'
                },
                'value_ranges': {
                    'cost': {'min': 0, 'max': 1e9}
                },
                'allowed_values': {
                    'status': ['planned', 'in_progress', 'completed', 'on_hold', 'cancelled']
                },
                'completeness_threshold': 0.90,
                'duplicate_threshold': 0.1
            },
            'transit': {
                'required_columns': ['route', 'ridership'],
                'optional_columns': ['station', 'line', 'year', 'month', 'frequency'],
                'data_types': {
                    'route': 'object',
                    'ridership': 'int64'
                },
                'value_ranges': {
                    'ridership': {'min': 0, 'max': 1e8}
                },
                'completeness_threshold': 0.90,
                'duplicate_threshold': 0.05
            },
            'historical': {
                'required_columns': ['year'],
                'optional_columns': ['population', 'employment', 'growth_rate', 'indicator'],
                'data_types': {
                    'year': 'int64',
                    'population': 'float64',
                    'employment': 'float64',
                    'growth_rate': 'float64'
                },
                'value_ranges': {
                    'year': {'min': 1900, 'max': 2030},
                    'population': {'min': 0, 'max': 1e8},
                    'employment': {'min': 0, 'max': 1e8},
                    'growth_rate': {'min': -1, 'max': 1}
                },
                'completeness_threshold': 0.85,
                'duplicate_threshold': 0.1
            }
        }

        # Validation statistics
        self.validation_stats = {
            'total_files': 0,
            'valid_files': 0,
            'invalid_files': 0,
            'warning_files': 0,
            'total_records': 0,
            'total_errors': 0,
            'total_warnings': 0,
            'files_by_category': {cat: 0 for cat in self.validation_rules.keys()},
            'validation_time': 0
        }

    def detect_data_category(self, df: pd.DataFrame, filename: str) -> Tuple[str, float]:
        """
        Detect the data category based on column names and filename.
        """
        filename_lower = filename.lower()
        columns_lower = [col.lower() for col in df.columns]

        category_scores = {}

        for category, rules in self.validation_rules.items():
            score = 0

            # Check filename
            category_keywords = category.split('_')
            for keyword in category_keywords:
                if keyword in filename_lower:
                    score += 0.3

            # Check required columns
            required_columns = rules['required_columns']
            matched_columns = 0
            for req_col in required_columns:
                if any(req_col in col for col in columns_lower):
                    matched_columns += 1

            if required_columns:
                column_score = matched_columns / len(required_columns)
                score += column_score * 0.7

            category_scores[category] = score

        # Return best match
        best_category = max(category_scores, key=category_scores.get)
        confidence = category_scores[best_category]

        return best_category, confidence

    def validate_column_names(self, df: pd.DataFrame, category: str) -> Tuple[bool, List[str]]:
        """
        Validate that required columns are present and properly named.
        """
        errors = []
        warnings = []

        rules = self.validation_rules.get(category, {})
        required_columns = rules.get('required_columns', [])
        optional_columns = rules.get('optional_columns', [])

        df_columns_lower = [col.lower() for col in df.columns]

        # Check required columns
        missing_required = []
        for req_col in required_columns:
            if not any(req_col in col for col in df_columns_lower):
                missing_required.append(req_col)

        if missing_required:
            errors.append(f"Missing required columns: {missing_required}")

        # Check for unexpected columns
        expected_columns = set(required_columns + optional_columns)
        found_columns = set(df.columns)

        # This is just a warning, not an error
        unexpected_columns = found_columns - expected_columns
        if unexpected_columns:
            warnings.append(f"Unexpected columns found: {list(unexpected_columns)[:5]}")

        is_valid = len(errors) == 0
        return is_valid, errors + warnings

    def validate_data_types(self, df: pd.DataFrame, category: str) -> Tuple[bool, List[str]]:
        """
        Validate that columns have appropriate data types.
        """
        errors = []
        warnings = []

        rules = self.validation_rules.get(category, {})
        expected_types = rules.get('data_types', {})

        for column, expected_type in expected_types.items():
            # Find matching column (case-insensitive)
            matching_col = None
            for df_col in df.columns:
                if column.lower() in df_col.lower():
                    matching_col = df_col
                    break

            if matching_col:
                actual_type = str(df[matching_col].dtype)

                # Check if types are compatible
                if expected_type == 'object' and actual_type != 'object':
                    warnings.append(f"Column '{matching_col}' is {actual_type}, expected object")
                elif 'int' in expected_type and 'int' not in actual_type:
                    try:
                        # Try to convert
                        pd.to_numeric(df[matching_col], errors='raise')
                        warnings.append(f"Column '{matching_col}' could be converted to integer")
                    except:
                        errors.append(f"Column '{matching_col}' is {actual_type}, expected integer")
                elif 'float' in expected_type and 'float' not in actual_type:
                    try:
                        # Try to convert
                        pd.to_numeric(df[matching_col], errors='raise')
                        warnings.append(f"Column '{matching_col}' could be converted to float")
                    except:
                        errors.append(f"Column '{matching_col}' is {actual_type}, expected numeric")

        is_valid = len(errors) == 0
        return is_valid, errors + warnings

    def validate_value_ranges(self, df: pd.DataFrame, category: str) -> Tuple[bool, List[str]]:
        """
        Validate that values fall within expected ranges.
        """
        errors = []
        warnings = []

        rules = self.validation_rules.get(category, {})
        value_ranges = rules.get('value_ranges', {})

        for column, range_config in value_ranges.items():
            # Find matching column
            matching_col = None
            for df_col in df.columns:
                if column.lower() in df_col.lower():
                    matching_col = df_col
                    break

            if matching_col and matching_col in df.columns:
                try:
                    # Convert to numeric if needed
                    numeric_series = pd.to_numeric(df[matching_col], errors='coerce')

                    # Check for values outside range
                    min_val = range_config.get('min')
                    max_val = range_config.get('max')

                    if min_val is not None:
                        below_min = (numeric_series < min_val).sum()
                        if below_min > 0:
                            errors.append(f"Column '{matching_col}' has {below_min} values below minimum {min_val}")

                    if max_val is not None:
                        above_max = (numeric_series > max_val).sum()
                        if above_max > 0:
                            errors.append(f"Column '{matching_col}' has {above_max} values above maximum {max_val}")

                except Exception as e:
                    warnings.append(f"Could not validate range for column '{matching_col}': {str(e)}")

        is_valid = len(errors) == 0
        return is_valid, errors + warnings

    def validate_allowed_values(self, df: pd.DataFrame, category: str) -> Tuple[bool, List[str]]:
        """
        Validate that categorical columns contain only allowed values.
        """
        errors = []
        warnings = []

        rules = self.validation_rules.get(category, {})
        allowed_values = rules.get('allowed_values', {})

        for column, allowed in allowed_values.items():
            # Find matching column
            matching_col = None
            for df_col in df.columns:
                if column.lower() in df_col.lower():
                    matching_col = df_col
                    break

            if matching_col and matching_col in df.columns:
                try:
                    unique_values = set(df[matching_col].dropna().astype(str).str.lower().str.strip())
                    allowed_lower = set(val.lower() for val in allowed)

                    invalid_values = unique_values - allowed_lower

                    if invalid_values:
                        errors.append(f"Column '{matching_col}' has invalid values: {list(invalid_values)[:5]}")

                except Exception as e:
                    warnings.append(f"Could not validate allowed values for column '{matching_col}': {str(e)}")

        is_valid = len(errors) == 0
        return is_valid, errors + warnings

    def validate_completeness(self, df: pd.DataFrame, category: str) -> Tuple[bool, List[str]]:
        """
        Validate data completeness (missing values).
        """
        errors = []
        warnings = []

        rules = self.validation_rules.get(category, {})
        completeness_threshold = rules.get('completeness_threshold', 0.95)
        required_columns = rules.get('required_columns', [])

        # Check overall completeness
        total_cells = len(df) * len(df.columns)
        missing_cells = df.isnull().sum().sum()
        completeness = 1 - (missing_cells / total_cells)

        if completeness < completeness_threshold:
            errors.append(f"Overall completeness {completeness:.2%} below threshold {completeness_threshold:.2%}")

        # Check required columns for completeness
        for req_col in required_columns:
            # Find matching column
            matching_col = None
            for df_col in df.columns:
                if req_col.lower() in df_col.lower():
                    matching_col = df_col
                    break

            if matching_col and matching_col in df.columns:
                missing_count = df[matching_col].isnull().sum()
                missing_rate = missing_count / len(df)

                if missing_rate > (1 - completeness_threshold):
                    errors.append(f"Required column '{matching_col}' has {missing_rate:.1%} missing values")

        is_valid = len(errors) == 0
        return is_valid, errors + warnings

    def validate_duplicates(self, df: pd.DataFrame, category: str) -> Tuple[bool, List[str]]:
        """
        Check for duplicate records.
        """
        errors = []
        warnings = []

        rules = self.validation_rules.get(category, {})
        duplicate_threshold = rules.get('duplicate_threshold', 0.1)
        required_columns = rules.get('required_columns', [])

        # Check for exact duplicates
        exact_duplicates = df.duplicated().sum()
        duplicate_rate = exact_duplicates / len(df)

        if duplicate_rate > duplicate_threshold:
            errors.append(f"High duplicate rate: {duplicate_rate:.1%} ({exact_duplicates} rows)")

        # Check for duplicates in key columns
        if required_columns:
            key_cols = []
            for req_col in required_columns:
                for df_col in df.columns:
                    if req_col.lower() in df_col.lower():
                        key_cols.append(df_col)
                        break

            if key_cols:
                key_duplicates = df.duplicated(subset=key_cols).sum()
                key_duplicate_rate = key_duplicates / len(df)

                if key_duplicate_rate > duplicate_threshold:
                    warnings.append(f"High key column duplicate rate: {key_duplicate_rate:.1%}")

        is_valid = len(errors) == 0
        return is_valid, errors + warnings

    def validate_data_consistency(self, df: pd.DataFrame, category: str) -> Tuple[bool, List[str]]:
        """
        Validate logical consistency within the data.
        """
        errors = []
        warnings = []

        # Category-specific consistency checks
        if category == 'budget_reports':
            errors.extend(self._validate_budget_consistency(df))
        elif category == 'tax_levy':
            errors.extend(self._validate_tax_consistency(df))
        elif category == 'infrastructure':
            errors.extend(self._validate_infrastructure_consistency(df))
        elif category == 'transit':
            errors.extend(self._validate_transit_consistency(df))
        elif category == 'historical':
            errors.extend(self._validate_historical_consistency(df))

        is_valid = len(errors) == 0
        return is_valid, errors + warnings

    def _validate_budget_consistency(self, df: pd.DataFrame) -> List[str]:
        """Validate budget-specific consistency"""
        errors = []

        # Find budget, actual, and variance columns
        budget_col = None
        actual_col = None
        variance_col = None

        for col in df.columns:
            col_lower = col.lower()
            if 'budget' in col_lower and budget_col is None:
                budget_col = col
            elif 'actual' in col_lower and actual_col is None:
                actual_col = col
            elif 'variance' in col_lower and variance_col is None:
                variance_col = col

        # Check if variance = actual - budget (approximately)
        if budget_col and actual_col and variance_col:
            try:
                budget_vals = pd.to_numeric(df[budget_col], errors='coerce')
                actual_vals = pd.to_numeric(df[actual_col], errors='coerce')
                variance_vals = pd.to_numeric(df[variance_col], errors='coerce')

                # Calculate expected variance
                expected_variance = actual_vals - budget_vals
                difference = abs(variance_vals - expected_variance)

                # Check for large discrepancies (more than 1% or $1000)
                large_discrepancies = (difference > (0.01 * abs(budget_vals) + 1000)).sum()

                if large_discrepancies > 0:
                    errors.append(f"Found {large_discrepancies} rows with variance calculation discrepancies")

            except Exception as e:
                errors.append(f"Could not validate variance calculations: {str(e)}")

        return errors

    def _validate_tax_consistency(self, df: pd.DataFrame) -> List[str]:
        """Validate tax levy-specific consistency"""
        errors = []

        # Find levy and rate columns
        levy_col = None
        rate_col = None
        assessment_col = None

        for col in df.columns:
            col_lower = col.lower()
            if 'levy' in col_lower and 'amount' in col_lower and levy_col is None:
                levy_col = col
            elif 'rate' in col_lower and rate_col is None:
                rate_col = col
            elif 'assessment' in col_lower and assessment_col is None:
                assessment_col = col

        # Check if levy ≈ assessment * rate (for consistent data)
        if levy_col and rate_col and assessment_col:
            try:
                levy_vals = pd.to_numeric(df[levy_col], errors='coerce')
                rate_vals = pd.to_numeric(df[rate_col], errors='coerce')
                assessment_vals = pd.to_numeric(df[assessment_col], errors='coerce')

                # Convert rate from percentage to decimal if needed
                if rate_vals.max() > 1:
                    rate_vals = rate_vals / 100

                # Calculate expected levy
                expected_levy = assessment_vals * rate_vals
                difference = abs(levy_vals - expected_levy)

                # Check for large discrepancies (more than 5%)
                large_discrepancies = (difference > 0.05 * levy_vals).sum()

                if large_discrepancies > 0:
                    errors.append(f"Found {large_discrepancies} rows with levy calculation inconsistencies")

            except Exception as e:
                errors.append(f"Could not validate levy calculations: {str(e)}")

        return errors

    def _validate_infrastructure_consistency(self, df: pd.DataFrame) -> List[str]:
        """Validate infrastructure-specific consistency"""
        errors = []

        # Check for valid status values
        status_col = None
        cost_col = None

        for col in df.columns:
            col_lower = col.lower()
            if 'status' in col_lower and status_col is None:
                status_col = col
            elif 'cost' in col_lower and cost_col is None:
                cost_col = col

        # Check if completed projects have valid costs
        if status_col and cost_col:
            try:
                cost_vals = pd.to_numeric(df[cost_col], errors='coerce')
                completed_mask = df[status_col].str.lower() == 'completed'

                if completed_mask.any():
                    completed_zero_cost = ((cost_vals == 0) & completed_mask).sum()
                    if completed_zero_cost > 0:
                        errors.append(f"Found {completed_zero_cost} completed projects with zero cost")

            except Exception as e:
                errors.append(f"Could not validate infrastructure consistency: {str(e)}")

        return errors

    def _validate_transit_consistency(self, df: pd.DataFrame) -> List[str]:
        """Validate transit-specific consistency"""
        errors = []

        # Check for reasonable ridership numbers
        ridership_col = None

        for col in df.columns:
            if 'ridership' in col.lower():
                ridership_col = col
                break

        if ridership_col:
            try:
                ridership_vals = pd.to_numeric(df[ridership_col], errors='coerce')

                # Check for negative ridership
                negative_ridership = (ridership_vals < 0).sum()
                if negative_ridership > 0:
                    errors.append(f"Found {negative_ridership} rows with negative ridership")

                # Check for extremely high ridership (likely data errors)
                extreme_high = (ridership_vals > 1e7).sum()  # More than 10 million riders
                if extreme_high > 0:
                    errors.append(f"Found {extreme_high} rows with extremely high ridership (>10M)")

            except Exception as e:
                errors.append(f"Could not validate transit consistency: {str(e)}")

        return errors

    def _validate_historical_consistency(self, df: pd.DataFrame) -> List[str]:
        """Validate historical data-specific consistency"""
        errors = []

        # Find year column
        year_col = None

        for col in df.columns:
            if 'year' in col.lower():
                year_col = col
                break

        if year_col:
            try:
                year_vals = pd.to_numeric(df[year_col], errors='coerce')

                # Check for reasonable year range
                invalid_years = ((year_vals < 1900) | (year_vals > 2030)).sum()
                if invalid_years > 0:
                    errors.append(f"Found {invalid_years} rows with invalid year values")

                # Check for duplicate years (should be unique for time series)
                duplicate_years = year_vals.duplicated().sum()
                if duplicate_years > 0:
                    errors.append(f"Found {duplicate_years} duplicate year values")

            except Exception as e:
                errors.append(f"Could not validate historical consistency: {str(e)}")

        return errors

    def validate_dataframe(self, df: pd.DataFrame, category: str, filename: str) -> Dict[str, Any]:
        """
        Comprehensive validation of a single DataFrame.
        """
        start_time = datetime.now()

        validation_result = {
            'filename': filename,
            'category': category,
            'timestamp': start_time.isoformat(),
            'shape': df.shape,
            'columns': list(df.columns),
            'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
            'validation_results': {},
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'validation_time': 0,
            'quality_score': 0
        }

        # Run all validation checks
        validation_checks = [
            ('column_names', self.validate_column_names),
            ('data_types', self.validate_data_types),
            ('value_ranges', self.validate_value_ranges),
            ('allowed_values', self.validate_allowed_values),
            ('completeness', self.validate_completeness),
            ('duplicates', self.validate_duplicates),
            ('consistency', self.validate_data_consistency)
        ]

        total_errors = 0
        total_warnings = 0

        for check_name, check_func in validation_checks:
            try:
                is_valid, messages = check_func(df, category)

                validation_result['validation_results'][check_name] = {
                    'passed': is_valid,
                    'messages': messages
                }

                if not is_valid:
                    validation_result['is_valid'] = False

                # Categorize messages
                for message in messages:
                    if message.startswith('Missing') or message.startswith('Invalid') or message.startswith('High'):
                        validation_result['errors'].append(f"{check_name}: {message}")
                        total_errors += 1
                    else:
                        validation_result['warnings'].append(f"{check_name}: {message}")
                        total_warnings += 1

            except Exception as e:
                error_msg = f"Validation check '{check_name}' failed: {str(e)}"
                validation_result['errors'].append(error_msg)
                validation_result['validation_results'][check_name] = {
                    'passed': False,
                    'messages': [error_msg]
                }
                validation_result['is_valid'] = False
                total_errors += 1

        # Calculate quality score (0-100)
        max_score = 100
        error_penalty = 10
        warning_penalty = 3

        validation_result['quality_score'] = max(0, max_score - (total_errors * error_penalty) - (total_warnings * warning_penalty))

        # Calculate validation time
        validation_result['validation_time'] = (datetime.now() - start_time).total_seconds()

        # Update statistics
        self.validation_stats['total_records'] += len(df)
        self.validation_stats['total_errors'] += total_errors
        self.validation_stats['total_warnings'] += total_warnings
        self.validation_stats['files_by_category'][category] += 1

        if validation_result['is_valid']:
            self.validation_stats['valid_files'] += 1
        else:
            self.validation_stats['invalid_files'] += 1

        if total_warnings > 0:
            self.validation_stats['warning_files'] += 1

        return validation_result

    def load_and_validate_file(self, filepath: Path) -> Optional[Dict[str, Any]]:
        """
        Load a data file and run validation.
        """
        try:
            # Load file based on extension
            if filepath.suffix.lower() in ['.xlsx', '.xls']:
                # Excel file - validate one sheet rule
                excel_file = pd.ExcelFile(filepath)
                if len(excel_file.sheet_names) > 1:
                    logger.error(f"DRUCK VIOLATION: {filepath.name} has {len(excel_file.sheet_names)} sheets (must have exactly ONE)")
                    return {
                        'filename': filepath.name,
                        'is_valid': False,
                        'errors': [f"DRUCK VIOLATION: Multiple sheets found ({len(excel_file.sheet_names)}). Must have exactly ONE sheet."],
                        'warnings': [],
                        'quality_score': 0
                    }

                df = pd.read_excel(filepath)
            elif filepath.suffix.lower() == '.csv':
                df = pd.read_csv(filepath)
            else:
                logger.warning(f"Unsupported file type: {filepath.suffix}")
                return None

            if df.empty:
                logger.warning(f"Empty file: {filepath.name}")
                return None

            # Detect category
            category, confidence = self.detect_data_category(df, filepath.name)

            # Run validation
            result = self.validate_dataframe(df, category, filepath.name)
            result['file_path'] = str(filepath)
            result['file_size'] = filepath.stat().st_size
            result['category_confidence'] = confidence

            return result

        except Exception as e:
            logger.error(f"Error loading/validating {filepath.name}: {str(e)}")
            return {
                'filename': filepath.name,
                'is_valid': False,
                'errors': [f"File loading error: {str(e)}"],
                'warnings': [],
                'quality_score': 0
            }

    def validate_all_files(self) -> Dict[str, Any]:
        """
        Validate all data files in the data directory.
        """
        start_time = datetime.now()

        logger.info("Starting comprehensive data validation")
        logger.info(f"Data directory: {self.data_dir}")

        # Find all data files
        file_patterns = ['**/*.xlsx', '**/*.xls', '**/*.csv']
        all_files = []

        for pattern in file_patterns:
            all_files.extend(self.data_dir.glob(pattern))

        if not all_files:
            logger.warning("No data files found for validation")
            return {'error': 'No data files found'}

        logger.info(f"Found {len(all_files)} files to validate")

        results = {
            'start_time': start_time.isoformat(),
            'total_files': len(all_files),
            'validation_results': [],
            'summary': self.validation_stats.copy(),
            'files_processed': [],
            'files_failed': []
        }

        # Validate each file
        for filepath in all_files:
            logger.info(f"Validating: {filepath.name}")

            result = self.load_and_validate_file(filepath)
            if result:
                results['validation_results'].append(result)

                if result['is_valid']:
                    results['files_processed'].append(filepath.name)
                else:
                    results['files_failed'].append(filepath.name)

            self.validation_stats['total_files'] += 1

        # Calculate final statistics
        end_time = datetime.now()
        self.validation_stats['validation_time'] = (end_time - start_time).total_seconds()

        results['end_time'] = end_time.isoformat()
        results['summary'] = self.validation_stats

        # Generate validation report
        self.generate_validation_report(results)

        return results

    def generate_validation_report(self, results: Dict[str, Any]) -> None:
        """
        Generate comprehensive validation report.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.output_dir / f"validation_report_{timestamp}.json"

        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False, default=str)

            logger.info(f"Validation report saved to: {report_file}")

            # Generate human-readable summary
            summary_file = self.output_dir / f"validation_summary_{timestamp}.md"
            summary_content = self.generate_human_readable_summary(results)

            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(summary_content)

            logger.info(f"Human-readable summary saved to: {summary_file}")

        except Exception as e:
            logger.error(f"Error saving validation report: {str(e)}")

    def generate_human_readable_summary(self, results: Dict[str, Any]) -> str:
        """Generate human-readable summary of validation results"""

        summary = []
        summary.append("# Westchester Data Validation Report")
        summary.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        summary.append("")

        # Executive Summary
        summary.append("## Executive Summary")
        summary.append(f"**Total Files Validated**: {results['summary']['total_files']}")
        summary.append(f"**Valid Files**: {results['summary']['valid_files']}")
        summary.append(f"**Invalid Files**: {results['summary']['invalid_files']}")
        summary.append(f"**Files with Warnings**: {results['summary']['warning_files']}")
        summary.append(f"**Total Records Checked**: {results['summary']['total_records']:,}")
        summary.append(f"**Total Errors Found**: {results['summary']['total_errors']}")
        summary.append(f"**Total Warnings Found**: {results['summary']['total_warnings']}")
        summary.append(f"**Validation Time**: {results['summary']['validation_time']:.2f} seconds")
        summary.append("")

        # Success Rate
        if results['summary']['total_files'] > 0:
            success_rate = results['summary']['valid_files'] / results['summary']['total_files']
            summary.append(f"**Overall Success Rate**: {success_rate:.1%}")
            summary.append("")

        # Results by Data Category
        summary.append("## Results by Data Category")
        for category, count in results['summary']['files_by_category'].items():
            if count > 0:
                # Calculate success rate for this category
                category_results = [r for r in results['validation_results'] if r['category'] == category]
                if category_results:
                    valid_count = sum(1 for r in category_results if r['is_valid'])
                    category_success_rate = valid_count / len(category_results)
                    summary.append(f"- **{category.replace('_', ' ').title()}**: {count} files, {category_success_rate:.1%} success rate")
        summary.append("")

        # Quality Score Distribution
        summary.append("## Quality Score Distribution")
        quality_scores = [r.get('quality_score', 0) for r in results['validation_results']]

        if quality_scores:
            avg_score = np.mean(quality_scores)
            summary.append(f"**Average Quality Score**: {avg_score:.1f}/100")

            # Score ranges
            excellent = sum(1 for score in quality_scores if score >= 90)
            good = sum(1 for score in quality_scores if 80 <= score < 90)
            fair = sum(1 for score in quality_scores if 70 <= score < 80)
            poor = sum(1 for score in quality_scores if score < 70)

            summary.append(f"- **Excellent (90-100)**: {excellent} files")
            summary.append(f"- **Good (80-89)**: {good} files")
            summary.append(f"- **Fair (70-79)**: {fair} files")
            summary.append(f"- **Poor (<70)**: {poor} files")
        summary.append("")

        # Most Common Issues
        summary.append("## Most Common Validation Issues")

        # Collect all error and warning messages
        all_issues = []
        for result in results['validation_results']:
            for error in result.get('errors', []):
                all_issues.append(('ERROR', error))
            for warning in result.get('warnings', []):
                all_issues.append(('WARNING', warning))

        # Count issue types
        issue_counts = {}
        for issue_type, message in all_issues:
            # Extract issue type (first word before colon)
            issue_category = message.split(':')[0] if ':' in message else message
            key = f"{issue_type}: {issue_category}"
            issue_counts[key] = issue_counts.get(key, 0) + 1

        # Sort and show top issues
        top_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        for (issue_type, count) in top_issues:
            summary.append(f"- **{issue_type}**: {count} occurrences")
        summary.append("")

        # Failed Files (if any)
        if results['files_failed']:
            summary.append("## Files That Failed Validation")
            for filename in results['files_failed'][:20]:  # Show first 20
                result = next((r for r in results['validation_results'] if r['filename'] == filename), None)
                if result:
                    summary.append(f"### {filename}")
                    summary.append(f"- **Quality Score**: {result.get('quality_score', 0)}/100")
                    summary.append(f"- **Errors**: {len(result.get('errors', []))}")
                    summary.append(f"- **Warnings**: {len(result.get('warnings', []))}")

                    # Show top errors
                    errors = result.get('errors', [])[:3]
                    if errors:
                        summary.append("**Top Issues:**")
                        for error in errors:
                            summary.append(f"  - {error}")
                    summary.append("")

            if len(results['files_failed']) > 20:
                summary.append(f"... and {len(results['files_failed']) - 20} more failed files")
            summary.append("")

        # Recommendations
        summary.append("## Recommendations")

        success_rate = results['summary']['valid_files'] / max(results['summary']['total_files'], 1)
        avg_score = np.mean(quality_scores) if quality_scores else 0

        if success_rate >= 0.9 and avg_score >= 85:
            summary.append("✅ **Excellent data quality!** Validation shows high compliance with standards.")
        elif success_rate >= 0.7 and avg_score >= 70:
            summary.append("⚠️ **Good data quality with room for improvement.** Address the common issues identified above.")
        else:
            summary.append("❌ **Data quality needs significant improvement.** Review failed files and address validation issues.")

        summary.append("")
        summary.append("## Priority Actions")
        summary.append("1. **Fix Druck violations** - Ensure all Excel files have exactly ONE sheet")
        summary.append("2. **Address common errors** - Focus on the most frequent validation issues")
        summary.append("3. **Improve data completeness** - Fill missing values in key columns")
        summary.append("4. **Standardize data formats** - Ensure consistent data types and formats")
        summary.append("5. **Validate data sources** - Verify data accuracy at the source")

        return "\n".join(summary)

def main():
    """Main function for command line usage"""
    import argparse

    parser = argparse.ArgumentParser(description='Westchester Data Validation System')
    parser.add_argument('--data-dir', help='Directory containing data files to validate')
    parser.add_argument('--output-dir', help='Output directory for validation reports')
    parser.add_argument('--single-file', help='Validate a single file')
    parser.add_argument('--category', help='Force data category (overrides auto-detection)')
    parser.add_argument('--quality-threshold', type=float, default=70, help='Minimum quality score threshold')

    args = parser.parse_args()

    # Initialize validator
    validator = WestchesterDataValidator(
        data_dir=args.data_dir,
        output_dir=args.output_dir
    )

    if args.single_file:
        # Validate single file
        filepath = Path(args.single_file)
        if not filepath.exists():
            print(f"Error: File {args.single_file} not found")
            sys.exit(1)

        print(f"Validating single file: {filepath.name}")
        result = validator.load_and_validate_file(filepath)

        if result:
            print(f"\n{'='*60}")
            print("VALIDATION RESULTS")
            print(f"{'='*60}")
            print(f"File: {result['filename']}")
            print(f"Category: {result['category']}")
            print(f"Valid: {'✅' if result['is_valid'] else '❌'}")
            print(f"Quality Score: {result.get('quality_score', 0)}/100")
            print(f"Errors: {len(result.get('errors', []))}")
            print(f"Warnings: {len(result.get('warnings', []))}")

            if result.get('errors'):
                print(f"\n**Errors:**")
                for error in result['errors']:
                    print(f"  ❌ {error}")

            if result.get('warnings'):
                print(f"\n**Warnings:**")
                for warning in result['warnings']:
                    print(f"  ⚠️ {warning}")

            # Quality assessment
            quality_score = result.get('quality_score', 0)
            if quality_score >= args.quality_threshold:
                print(f"\n✅ **PASSED** - Quality score {quality_score} meets threshold {args.quality_threshold}")
            else:
                print(f"\n❌ **FAILED** - Quality score {quality_score} below threshold {args.quality_threshold}")
        else:
            print("❌ Validation failed - could not process file")

    else:
        # Validate all files
        print("Starting comprehensive data validation...")

        results = validator.validate_all_files()

        # Print summary
        stats = results['summary']
        print(f"\n{'='*60}")
        print("VALIDATION SUMMARY")
        print(f"{'='*60}")
        print(f"Total files: {stats['total_files']}")
        print(f"Valid files: {stats['valid_files']}")
        print(f"Invalid files: {stats['invalid_files']}")
        print(f"Total errors: {stats['total_errors']}")
        print(f"Total warnings: {stats['total_warnings']}")
        print(f"Validation time: {stats['validation_time']:.2f}s")

        if stats['total_files'] > 0:
            success_rate = stats['valid_files'] / stats['total_files']
            print(f"Success rate: {success_rate:.1%}")

        print(f"\n📁 Validation reports saved to: {validator.output_dir}")

if __name__ == "__main__":
    main()