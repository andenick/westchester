# Westchester Data Validation Report
Generated: 2025-10-14 11:51:10

## Executive Summary
**Total Files Validated**: 2
**Valid Files**: 1
**Invalid Files**: 1
**Files with Warnings**: 2
**Total Records Checked**: 22
**Total Errors Found**: 1
**Total Warnings Found**: 5
**Validation Time**: 0.30 seconds

**Overall Success Rate**: 50.0%

## Results by Data Category
- **Budget Reports**: 1 files, 0.0% success rate
- **Tax Levy**: 1 files, 100.0% success rate

## Quality Score Distribution
**Average Quality Score**: 87.5/100
- **Excellent (90-100)**: 1 files
- **Good (80-89)**: 1 files
- **Fair (70-79)**: 0 files
- **Poor (<70)**: 0 files

## Most Common Validation Issues
- **WARNING: data_types**: 3 occurrences
- **WARNING: column_names**: 2 occurrences
- **ERROR: column_names**: 1 occurrences

## Files That Failed Validation
### westchester_county_budget_2024_2025.xlsx
- **Quality Score**: 81/100
- **Errors**: 1
- **Warnings**: 3
**Top Issues:**
  - column_names: Missing required columns: ['budgeted']


## Recommendations
❌ **Data quality needs significant improvement.** Review failed files and address validation issues.

## Priority Actions
1. **Fix Druck violations** - Ensure all Excel files have exactly ONE sheet
2. **Address common errors** - Focus on the most frequent validation issues
3. **Improve data completeness** - Fill missing values in key columns
4. **Standardize data formats** - Ensure consistent data types and formats
5. **Validate data sources** - Verify data accuracy at the source