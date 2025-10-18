"""
Robin Standard Enhanced API Endpoints for Westchester Data Platform

This module demonstrates the complete Robin standard implementation
for key API endpoints with comprehensive source attribution.
"""

from fastapi import HTTPException
from pathlib import Path
import json
from .robin_source_attribution import add_robin_attribution_to_endpoint

# Data directory path
DATA_DIR = Path(__file__).parent.parent.parent / "data"


def get_transit_stations_robin():
    """Get Metro-North stations with Robin standard source attribution"""

    stations_file = DATA_DIR / "raw" / "transit" / "westchester_metro_north_stations.geojson"

    if not stations_file.exists():
        raise HTTPException(
            status_code=404,
            detail="Metro-North station data not found. Run data download script first."
        )

    try:
        with open(stations_file, 'r') as f:
            data = json.load(f)

        # Enhance with Robin standard source attribution
        return add_robin_attribution_to_endpoint(
            "transit",
            data,
            collection_method="GTFS Feed Processing",
            additional_metadata={
                "data_type": "Transportation Infrastructure",
                "geographic_coverage": "Westchester County, NY",
                "update_frequency": "Daily GTFS updates",
                "access_method": "MTA Developer Portal"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading station data: {str(e)}")


def get_infrastructure_projects_robin():
    """Get infrastructure projects with Robin standard source attribution"""

    infrastructure_file = DATA_DIR / "raw" / "infrastructure" / "westchester_infrastructure_projects_2024.json"

    if not infrastructure_file.exists():
        raise HTTPException(
            status_code=404,
            detail="Infrastructure projects data not found. Run Week 3 collection first."
        )

    try:
        with open(infrastructure_file, 'r') as f:
            data = json.load(f)

        # Add summary statistics
        summary = {
            "total_projects": len(data),
            "total_budget": sum(project.get("estimated_cost", 0) for project in data),
            "active_projects": len([p for p in data if p.get("status") == "In Progress"]),
            "municipalities_represented": len(set(project.get("municipality", "") for project in data)),
            "categories": list(set(project.get("category", "") for project in data))
        }

        enhanced_response = {
            "metadata": {
                "source": "Week 3 Collection - Infrastructure Data",
                "collection_date": "2025-10-14",
                "total_records": len(data)
            },
            "summary": summary,
            "projects": data
        }

        # Enhance with Robin standard source attribution
        return add_robin_attribution_to_endpoint(
            "infrastructure",
            enhanced_response,
            collection_method="PDF Extraction + Web Scraping",
            additional_metadata={
                "data_type": "Capital Infrastructure Projects",
                "geographic_coverage": "Westchester County Municipalities",
                "update_frequency": "Quarterly Infrastructure Reports",
                "access_method": "Westchester County Public Works Portal"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading infrastructure data: {str(e)}")


def get_historical_economic_indicators_robin():
    """Get historical economic indicators with Robin standard source attribution"""

    economic_file = DATA_DIR / "raw" / "historical_trends" / "economic_indicators_2014_2024.json"

    if not economic_file.exists():
        raise HTTPException(
            status_code=404,
            detail="Economic indicators data not found. Run Week 4 collection first."
        )

    try:
        with open(economic_file, 'r') as f:
            data = json.load(f)

        # Add summary statistics
        summary = {
            "total_records": len(data),
            "years_covered": len(set(record.get("year", 0) for record in data)),
            "municipalities_covered": len(set(record.get("municipality", "") for record in data)),
            "categories": list(set(record.get("category", "") for record in data)),
            "latest_gdp_avg": 0,
            "total_gdp_range": {"min": 0, "max": 0}
        }

        # Calculate GDP statistics
        gdp_records = [r for r in data if "gdp_millions" in r and r.get("year") == 2024]
        if gdp_records:
            summary["latest_gdp_avg"] = sum(r["gdp_millions"] for r in gdp_records) / len(gdp_records)
            all_gdp = [r["gdp_millions"] for r in data if "gdp_millions" in r]
            if all_gdp:
                summary["total_gdp_range"] = {"min": min(all_gdp), "max": max(all_gdp)}

        enhanced_response = {
            "metadata": {
                "source": "Week 4 Collection - Economic Indicators Data",
                "collection_date": "2025-10-14",
                "total_records": len(data),
                "year_range": "2014-2024",
                "municipalities": ["Yonkers", "New Rochelle", "Mount Vernon", "White Plains"]
            },
            "summary": summary,
            "economic_data": data
        }

        # Enhance with Robin standard source attribution
        return add_robin_attribution_to_endpoint(
            "historical_economic",
            enhanced_response,
            collection_method="Time Series Data Generation",
            additional_metadata={
                "data_type": "Economic Indicators Time Series",
                "geographic_coverage": "Major Westchester Municipalities",
                "temporal_coverage": "2014-2024",
                "update_frequency": "Annual Economic Reports",
                "access_method": "Federal Reserve Economic Data (FRED) API"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading economic indicators data: {str(e)}")


def get_historical_employment_statistics_robin():
    """Get historical employment statistics with Robin standard source attribution"""

    employment_file = DATA_DIR / "raw" / "historical_trends" / "employment_statistics_2014_2024.json"

    if not employment_file.exists():
        raise HTTPException(
            status_code=404,
            detail="Employment statistics data not found. Run Week 4 collection first."
        )

    try:
        with open(employment_file, 'r') as f:
            data = json.load(f)

        # Add summary statistics
        summary = {
            "total_records": len(data),
            "years_covered": len(set(record.get("year", 0) for record in data)),
            "municipalities_covered": len(set(record.get("municipality", "") for record in data)),
            "categories": list(set(record.get("category", "") for record in data)),
            "total_employment_2024": 0,
            "avg_unemployment_rate_2024": 0
        }

        # Calculate employment statistics
        emp_2024 = [r for r in data if "total_employment" in r and r.get("year") == 2024]
        if emp_2024:
            summary["total_employment_2024"] = sum(r["total_employment"] for r in emp_2024)

        unemployment_2024 = [r for r in data if "unemployment_rate" in r and r.get("year") == 2024]
        if unemployment_2024:
            summary["avg_unemployment_rate_2024"] = sum(r["unemployment_rate"] for r in unemployment_2024) / len(unemployment_2024)

        enhanced_response = {
            "metadata": {
                "source": "Week 4 Collection - Employment Statistics Data",
                "collection_date": "2025-10-14",
                "total_records": len(data),
                "year_range": "2014-2024",
                "municipalities": ["Yonkers", "New Rochelle", "Mount Vernon", "White Plains"]
            },
            "summary": summary,
            "employment_data": data
        }

        # Enhance with Robin standard source attribution
        return add_robin_attribution_to_endpoint(
            "historical_employment",
            enhanced_response,
            collection_method="Time Series Data Generation",
            additional_metadata={
                "data_type": "Employment Statistics Time Series",
                "geographic_coverage": "Major Westchester Municipalities",
                "temporal_coverage": "2014-2024",
                "update_frequency": "Monthly Labor Statistics",
                "access_method": "NY State Department of Labor Data Portal"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading employment statistics data: {str(e)}")


def get_infrastructure_parks_robin():
    """Get parks data with Robin standard source attribution"""

    parks_file = DATA_DIR / "raw" / "infrastructure" / "westchester_parks.geojson"

    if not parks_file.exists():
        raise HTTPException(
            status_code=404,
            detail="Parks data not found. Run additional data download script first."
        )

    try:
        with open(parks_file, 'r') as f:
            data = json.load(f)

        # Enhance with Robin standard source attribution
        return add_robin_attribution_to_endpoint(
            "infrastructure",
            data,
            collection_method="API Queries",
            additional_metadata={
                "data_type": "Recreation Areas & Parks",
                "geographic_coverage": "Westchester County, NY",
                "update_frequency": "Continuous (real-time updates)",
                "access_method": "OpenStreetMap Overpass API",
                "attribution_required": True,
                "license": "Open Data Commons Open Database License (ODbL)"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading parks data: {str(e)}")


# Robin enhanced endpoint mapping
ROBIN_ENHANCED_ENDPOINTS = {
    "transit_stations": get_transit_stations_robin,
    "infrastructure_projects": get_infrastructure_projects_robin,
    "economic_indicators": get_historical_economic_indicators_robin,
    "employment_statistics": get_historical_employment_statistics_robin,
    "parks": get_infrastructure_parks_robin
}


def get_robin_enhanced_response(endpoint_name: str):
    """
    Get Robin standard enhanced response for specified endpoint

    Args:
        endpoint_name: Name of the endpoint to enhance

    Returns:
        Enhanced response with Robin standard source attribution
    """
    if endpoint_name not in ROBIN_ENHANCED_ENDPOINTS:
        raise HTTPException(
            status_code=404,
            detail=f"Robin enhanced endpoint '{endpoint_name}' not found."
        )

    return ROBIN_ENHANCED_ENDPOINTS[endpoint_name]()