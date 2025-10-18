#!/usr/bin/env python3
"""
Parse budget data from extracted PDF summaries and create JSON
"""

import json
from pathlib import Path

# Real 2025 data extracted from PDF page 31
budget_2025 = {
    "year": 2025,
    "total_budget": 2484825864,
    "categories": [
        {
            "category": "Home and Community Services",
            "amount": 763728035,
            "percentage": 30.73,
            "description": "Housing, social services, community development"
        },
        {
            "category": "Miscellaneous and Fixed",
            "amount": 706932011,
            "percentage": 28.45,
            "description": "Fixed costs, reserves, and miscellaneous"
        },
        {
            "category": "Public Safety, Correction & Courts",
            "amount": 357001939,
            "percentage": 14.37,
            "description": "Police, courts, corrections, public safety"
        },
        {
            "category": "Roads, Transportation and Park Facilities",
            "amount": 318691263,
            "percentage": 12.83,
            "description": "Roads, transportation, parks and recreation"
        },
        {
            "category": "Health Services",
            "amount": 220248024,
            "percentage": 8.86,
            "description": "Public health and human services"
        },
        {
            "category": "General Government and Support",
            "amount": 92374593,
            "percentage": 3.72,
            "description": "General administration and government operations"
        },
        {
            "category": "Education",
            "amount": 25850000,
            "percentage": 1.04,
            "description": "Community college sponsorship"
        }
    ],
    "source": "2025 Adopted County Current Operating Budget, Page B-3",
    "extraction_date": "2025-10-15"
}

# Real 2024 data from PDF page 31 (previous year column)
budget_2024 = {
    "year": 2024,
    "total_budget": 2438304233,
    "categories": [
        {
            "category": "Home and Community Services",
            "amount": 720078990,
            "percentage": 29.53
        },
        {
            "category": "Miscellaneous and Fixed",
            "amount": 690628740,
            "percentage": 28.32
        },
        {
            "category": "Public Safety, Correction & Courts",
            "amount": 352292279,
            "percentage": 14.45
        },
        {
            "category": "Roads, Transportation and Park Facilities",
            "amount": 302102942,
            "percentage": 12.39
        },
        {
            "category": "Health Services",
            "amount": 247480260,
            "percentage": 10.15
        },
        {
            "category": "General Government and Support",
            "amount": 100371021,
            "percentage": 4.12
        },
        {
            "category": "Education",
            "amount": 25350000,
            "percentage": 1.04
        }
    ],
    "source": "2025 Adopted Budget (2024 comparison column), Page B-3",
    "extraction_date": "2025-10-15"
}

# Real 2023 data from PDF page 31
budget_2023 = {
    "year": 2023,
    "total_budget": 2369689638,
    "categories": [
        {
            "category": "Home and Community Services",
            "amount": 670092043,
            "percentage": 28.28
        },
        {
            "category": "Miscellaneous and Fixed",
            "amount": 698736298,
            "percentage": 29.49
        },
        {
            "category": "Public Safety, Correction & Courts",
            "amount": 327412947,
            "percentage": 13.82
        },
        {
            "category": "Roads, Transportation and Park Facilities",
            "amount": 292156180,
            "percentage": 12.33
        },
        {
            "category": "Health Services",
            "amount": 253622173,
            "percentage": 10.70
        },
        {
            "category": "General Government and Support",
            "amount": 102669998,
            "percentage": 4.33
        },
        {
            "category": "Education",
            "amount": 25000000,
            "percentage": 1.05
        }
    ],
    "source": "2025 Adopted Budget (2023 comparison column), Page B-3",
    "extraction_date": "2025-10-15"
}

# Combine all years
all_budgets = {
    "westchester_county_budgets": {
        "2023": budget_2023,
        "2024": budget_2024,
        "2025": budget_2025
    },
    "metadata": {
        "extracted_from": "Westchester County Adopted Operating Budget PDFs",
        "extraction_date": "2025-10-15",
        "years_available": ["2023", "2024", "2025"],
        "data_quality": "Official adopted budgets",
        "notes": "Data extracted from budget summary pages (Section B)"
    }
}

# Save to JSON
output_dir = Path(__file__).parent.parent.parent / "data" / "processed"
output_dir.mkdir(parents=True, exist_ok=True)

output_file = output_dir / "westchester_budget_data.json"

with open(output_file, 'w') as f:
    json.dump(all_budgets, f, indent=2)

print("="*80)
print("WESTCHESTER COUNTY BUDGET DATA EXTRACTION")
print("="*80)
print(f"\n✅ Successfully created: {output_file}")
print(f"\nData Summary:")
print(f"  Years: 2023-2025")
print(f"  2025 Total Budget: ${budget_2025['total_budget']:,.0f}")
print(f"  2024 Total Budget: ${budget_2024['total_budget']:,.0f}")
print(f"  2023 Total Budget: ${budget_2023['total_budget']:,.0f}")
print(f"\n2025 Budget Categories:")
for cat in sorted(budget_2025['categories'], key=lambda x: x['amount'], reverse=True):
    print(f"  - {cat['category']}: ${cat['amount']:,.0f} ({cat['percentage']}%)")

print(f"\n✅ Real budget data ready for dashboard integration!")
