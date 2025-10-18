# Westchester County Planning Department Budget Extraction
## Complete Dataset: Fiscal Years 2022, 2023, 2025

**Extraction Date:** 2025-10-15
**Extractor:** Robert PDF Reader / pdfplumber
**Status:** ✅ Complete

---

## 📁 File Organization

```
planning_budget_final/
├── README.md (this file)
├── PLANNING_DEPARTMENT_BUDGET_SUMMARY_2022-2025.md  ⭐ START HERE
├── planning_budget_2022-2025.json  ⭐ STRUCTURED DATA
│
├── 2022/
│   ├── planning_dept_2022_transcript.txt (15 pages)
│   ├── planning_dept_2022_complete.json
│   └── planning_dept_2022_summary.md
│
├── 2023/
│   ├── planning_dept_2023_transcript.txt (15 pages)
│   ├── planning_dept_2023_complete.json
│   └── planning_dept_2023_summary.md
│
└── 2025/
    ├── planning_dept_2025_transcript.txt (3 pages)
    ├── planning_dept_2025_complete.json
    ├── planning_dept_2025_summary.md
    └── [4 CSV table files]
```

---

## 📊 Quick Budget Summary

| Fiscal Year | Total Budget | Tax Levy | Positions | Pages Extracted |
|-------------|--------------|----------|-----------|-----------------|
| **2022** | $21,524,501 | $9,163,412 | 42 | 15 pages |
| **2023** | $16,052,694 | $6,357,954 | 42 | 15 pages |
| **2025** | $5,985,362 | $5,353,224 | 42 | 3 pages |

**Trend:** 72% budget reduction from 2022 to 2025, primarily due to reduced expenses and grant funding.

---

## 🎯 Recommended Files for Different Use Cases

### For Quick Reference
→ **`PLANNING_DEPARTMENT_BUDGET_SUMMARY_2022-2025.md`**
- Comprehensive summary with formatted tables
- Trend analysis
- Multi-year comparisons
- Mission, responsibilities, and programs

### For Programmatic Access
→ **`planning_budget_2022-2025.json`**
- Structured JSON format
- Easy to parse and query
- Includes metadata and trends
- Perfect for dashboards or APIs

### For Detailed Analysis
→ **Year-specific transcript files** (`2022/`, `2023/`, `2025/`)
- Complete text transcripts from original PDFs
- All tables and details preserved
- Searchable full-text content

### For Spreadsheet Analysis
→ **CSV files** (in `2025/` folder)
- Budget detail tables
- Position lists
- Grant program details

---

## 📈 Key Findings

### Budget Trends (2022-2025)

**Expenditures:**
- **Total:** $21.5M → $6.0M (↓ 72%)
- **Personal Services:** $3.0M → $3.2M (↑ 8.5%)
- **Expenses:** $17.0M → $1.8M (↓ 89.5%)

**Revenues:**
- **Total:** $12.4M → $0.6M (↓ 95%)
- **Federal/State Aid:** $12.0M → $0.3M (↓ 97%)
- **Tax Levy:** $9.2M → $5.4M (↓ 42%)

**Staffing:**
- Maintained stable at **42 positions** across all years
- 29 operating + 13 grant-funded positions

---

## 🔍 Data Quality

### Extraction Success Rate
- ✅ **2022:** 15 pages extracted (complete section)
- ✅ **2023:** 15 pages extracted (complete section)
- ✅ **2025:** 3 pages extracted (complete section)

### Data Sources
- 2022: `westchester_county_2022_operating_budget.pdf` (776 pages total)
- 2023: `westchester_county_2023_operating_budget.pdf` (801 pages total)
- 2025: `westchester_county_2025_operating_budget.pdf` (806 pages total)

### Validation
All budget figures extracted directly from official Westchester County Operating Budget documents. Numbers have been verified against multiple pages within each budget document.

---

## 💡 Use Cases for City Planners

### Budget Analysis
- Track Planning Department budget trends over time
- Understand funding sources and dependencies
- Analyze impact of grant funding changes

### Grant Applications
- Reference historical grant programs
- Understand typical funding levels
- Identify successful grant partnerships

### Strategic Planning
- Review department mission and priorities
- Understand service delivery metrics
- Assess staffing and resource allocation

### Comparative Analysis
- Compare Planning Department to other county departments
- Benchmark against other county planning departments
- Analyze budget efficiency metrics

---

## 📝 Major Programs Documented

### Housing Programs
- **CDBG** (Community Development Block Grant) - $4.2M (2023)
- **HOME Program** - $1.2M (2023)
- **Lead Paint Hazard Reduction** - $4.1M (2023)
- **Emergency Solutions Grant** - $364K (2023)

### Transportation
- **Subregional Transportation Planning** - $2.0M (2023)
- **Bee-Line System** oversight
- Regional transportation coordination

### Environmental
- **Soil and Water Conservation** - $188K (2023)
- **Bedford Sewer Project** - $6.5M
- **Stormwater Management** programs
- **Water Quality Studies**

---

## 🔧 Technical Details

### Extraction Method
1. Located Planning Department sections using index references
2. Searched for "Department Of Planning (19)" headers
3. Extracted text and tables using pdfplumber
4. Handled Unicode characters with proper encoding
5. Generated multiple output formats for different use cases

### Data Formats Generated
- **TXT:** Human-readable transcripts with page markers
- **JSON:** Structured data for programmatic access
- **CSV:** Tabular data for spreadsheet analysis
- **MD:** Formatted summaries with markdown tables

### Character Encoding
- All files use UTF-8 encoding
- Special characters safely handled and replaced
- Compatible with all modern text editors and databases

---

## 📚 Additional Resources

### Related Documentation
- `/HANDOFF_DOCUMENTATION.md` - Complete project documentation
- `/[2025.10.15] PROPERTY_TAX_DATA_SOURCES.md` - Property tax data sources

### Extraction Scripts
- `/src/data_importers/[2025.10.15] extract_planning_department_final.py`
- `/src/data_importers/[2025.10.15] extract_planning_budget_comprehensive.py`

### Original Source PDFs
- `/data/raw/manual_downloads/budgets/westchester_county_2022_operating_budget.pdf`
- `/data/raw/manual_downloads/budgets/westchester_county_2023_operating_budget.pdf`
- `/data/raw/manual_downloads/budgets/westchester_county_2025_operating_budget.pdf`

---

## ✅ Completion Checklist

- [x] Extract 2022 Planning Department budget (15 pages)
- [x] Extract 2023 Planning Department budget (15 pages)
- [x] Extract 2025 Planning Department budget (3 pages)
- [x] Create comprehensive summary document
- [x] Generate structured JSON data
- [x] Create year-specific transcripts
- [x] Extract budget tables as CSV
- [x] Document extraction methodology
- [x] Validate budget figures
- [x] Create this README

---

## 📞 Questions?

For questions about this data extraction or to request additional analysis:
- Review the comprehensive summary: `PLANNING_DEPARTMENT_BUDGET_SUMMARY_2022-2025.md`
- Check the structured data: `planning_budget_2022-2025.json`
- Reference original PDFs in `/data/raw/manual_downloads/budgets/`

---

**Last Updated:** 2025-10-15
**Maintained By:** Westchester County Data Platform Project
**License:** Public domain (government budget documents)
