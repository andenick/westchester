# Westchester — County Data Platform

**A full-stack web application for Westchester County, NY open data — demographic analysis, sidewalk infrastructure planning, transit accessibility, and interactive mapping. React frontend + FastAPI backend.**

---

## Why This Exists

Westchester County publishes open data across dozens of portals (county GIS, census, MTA, municipal budgets) but there's no unified platform for analysis. This project combines demographic, infrastructure, transit, and property data into interactive dashboards designed for municipal planners, researchers, and residents.

---

## Quick Start

```bash
git clone https://github.com/andenick/westchester.git
cd westchester

# Backend
cd Technical/src/backend
pip install -r requirements.txt
python main.py                     # Starts on http://localhost:8000

# Frontend (new terminal)
cd Technical/src/frontend
npm install
npm run dev                        # Starts on http://localhost:5173
```

---

## Features

- **Demographic Dashboard**: Population, income, housing, and education data by municipality
- **Sidewalk Planning Dashboard**: Infrastructure coverage analysis with interactive mapping
- **Transit Accessibility**: Metro-North station analysis and commute patterns
- **Property Tax Explorer**: Assessment and tax rate comparisons across municipalities
- **Interactive Maps**: Leaflet-based geospatial visualization with layer controls

---

## Data Sources

| Source | Content | Access |
|--------|---------|--------|
| Westchester County GIS | Tax parcels, sidewalks, municipal boundaries | [GIS Portal](https://gis.westchestergov.com/) |
| US Census / ACS | Population, income, housing, education (2020 + 5-year ACS) | [data.census.gov](https://data.census.gov/) |
| MTA / Metro-North | Station locations, ridership, schedules | [MTA Open Data](https://new.mta.info/open-data) |
| Westchester County Budget | Municipal budget documents | County website |
| USDA SNAP | Food access indicators | [USDA ERS](https://www.ers.usda.gov/) |

---

## Repository Structure

```
westchester/
├── README.md
├── Inputs/                         Raw data files (shapefiles, CSVs)
├── Technical/
│   └── src/
│       ├── backend/                FastAPI server
│       ├── frontend/               React app (Vite + Tailwind)
│       │   └── src/pages/          Dashboard pages
│       ├── data_importers/         Data ingestion scripts
│       └── data_pipeline/          Data processing pipeline
└── Output/                         Deliverables (maps, reports, packages)
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React, TypeScript, Vite, Tailwind CSS, Leaflet, Recharts |
| Backend | FastAPI, Python |
| Database | SQLite |
| Maps | Leaflet + GeoJSON |
| Deployment | Netlify (frontend) + Render (backend) |

---

## Requirements

- **Python 3.11+** — backend and data processing
- **Node.js 18+** — frontend
- **No API keys required** — all data is from public open data portals

---

## Citation

```bibtex
@software{westchester2026,
  title = {Westchester County Data Platform},
  author = {Anderson, Nicholas},
  year = {2026},
  url = {https://github.com/andenick/westchester}
}
```

---

## License

MIT
