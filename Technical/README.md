# Westchester County Project - Technical Implementation

## Architecture Overview

This project follows the **Shaikh Tonak Pattern** (95% success rate per Druck standards) with a modern full-stack architecture:

```
┌─────────────────┐      ┌──────────────────┐      ┌──────────────────┐
│   React 19      │      │   FastAPI        │      │  Data Sources    │
│   Frontend      │◄────►│   REST API       │◄────►│  - Census API    │
│   (Port 5173)   │      │   (Port 8000)    │      │  - GTFS Feeds    │
│                 │      │                  │      │  - NY State Data │
│  - TypeScript   │      │  - Python 3.11   │      │  - Robin DB      │
│  - Tailwind CSS │      │  - pandas        │      └──────────────────┘
│  - Leaflet Maps │      │  - geopandas     │               │
│  - Recharts     │      │  - FastAPI       │               ▼
└─────────────────┘      └──────────────────┘      ┌──────────────────┐
                                  │                 │  Excel Outputs   │
                                  └────────────────►│  (ONE SHEET ea.) │
                                                    │  LaTeX Reports   │
                                                    └──────────────────┘
```

**Key Design Principles**:
- **Separation of Concerns**: Frontend (presentation) ↔ Backend (logic) ↔ Data (storage)
- **RESTful API**: Clean endpoint design with OpenAPI documentation
- **Type Safety**: TypeScript frontend, Pydantic models backend
- **Mobile-First**: Responsive design from the start
- **Druck Compliance**: ONE SHEET Excel files, LaTeX reports, production quality

## Technology Stack

### Frontend
- **Framework**: React 19.1.1
- **Language**: TypeScript 5.9.3 (strict mode)
- **Build Tool**: Vite 7.1.7
- **Styling**: Tailwind CSS 4.1.14
- **Routing**: React Router DOM 7.9.4
- **Maps**: Leaflet 1.9.4 + React Leaflet 5.0.0
- **Charts**: Recharts 3.2.1
- **HTTP**: Axios 1.12.2

### Backend
- **Framework**: FastAPI 0.104.1
- **Server**: Uvicorn 0.24.0
- **Data Processing**: pandas 2.1.3, NumPy 1.26.2
- **Geographic**: GeoPandas 0.14.1, Shapely 2.0.2, PyProj 3.6.1
- **Excel**: openpyxl 3.1.2
- **HTTP**: requests 2.31.0
- **Scraping**: BeautifulSoup4 4.12.2 (if needed)

### Development Tools
- **Notebooks**: JupyterLab 4.0.9
- **Visualization**: Matplotlib 3.8.2, Seaborn 0.13.0
- **Linting**: ESLint 9.36.0 (frontend), Pylint/Flake8 (backend)

## Setup Instructions

### Prerequisites
1. **Python 3.11+**: Download from [python.org](https://www.python.org/)
2. **Node.js 18+**: Download from [nodejs.org](https://nodejs.org/)
3. **LaTeX Distribution** (for reports):
   - Windows: MiKTeX from [miktex.org](https://miktex.org/)
   - Mac: MacTeX from [tug.org/mactex](https://tug.org/mactex/)
   - Linux: `sudo apt install texlive-full`
4. **Git**: For version control

### Initial Setup (First Time)

#### 1. Clone and Navigate
```bash
cd D:\Arcanum\Projects\Westchester
```

#### 2. Backend Setup
```bash
# Create virtual environment
cd Technical
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Verify installation
python -c "import fastapi, pandas, geopandas; print('Backend dependencies OK')"
```

#### 3. Frontend Setup
```bash
# Navigate to frontend directory
cd src/frontend

# Install Node dependencies
npm install

# Verify installation
npm run --version
```

#### 4. Environment Variables (If Needed)
```bash
# Create .env file in Technical/ directory
# Add API keys (never commit to git):
CENSUS_API_KEY=your_census_api_key_here
NY_STATE_APP_TOKEN=your_ny_state_token_here
```

Get Census API key: [api.census.gov/data/key_signup.html](https://api.census.gov/data/key_signup.html)

### Quick Start Commands

#### Start Backend API
```bash
cd D:\Arcanum\Projects\Westchester\Technical
.\venv\Scripts\activate  # Windows
# or: source venv/bin/activate  # Mac/Linux

python src/api/main.py
```
**Result**: API running at http://localhost:8000
**Docs**: http://localhost:8000/docs (Swagger UI)

#### Start Frontend Development Server
```bash
cd D:\Arcanum\Projects\Westchester\Technical\src\frontend
npm run dev
```
**Result**: Frontend at http://localhost:5173

#### Run Data Collection
```bash
cd D:\Arcanum\Projects\Westchester\Technical
python scripts/download_all_data.py
```

#### Compile LaTeX Reports
```bash
cd D:\Arcanum\Projects\Westchester\Technical\docs
pdflatex westchester_methodology_report.tex
# Run twice for references
pdflatex westchester_methodology_report.tex
# Move to output directory
move *.pdf ..\..\Output\PDFs\
```

## Code Organization

```
Technical/
├── src/
│   ├── api/
│   │   ├── main.py              # FastAPI app with endpoints (175 lines)
│   │   └── __init__.py
│   │
│   ├── data_importers/
│   │   ├── census_api.py        # US Census Bureau integration
│   │   ├── gtfs_importer.py     # GTFS transit feed processing
│   │   ├── ny_state_data.py     # NY State Open Data Portal
│   │   └── __init__.py
│   │
│   ├── processors/
│   │   ├── excel_generator.py   # Excel export with ONE SHEET validation
│   │   └── __init__.py
│   │
│   ├── analysis/
│   │   └── __init__.py          # Analysis scripts
│   │
│   └── frontend/
│       ├── src/
│       │   ├── App.tsx          # Main app component with routing
│       │   ├── main.tsx         # React entry point
│       │   ├── components/
│       │   │   ├── common/      # Header, Footer
│       │   │   ├── charts/      # Recharts visualizations
│       │   │   └── map/         # Leaflet map components
│       │   ├── pages/
│       │   │   ├── HomePage.tsx
│       │   │   └── dashboards/
│       │   │       └── OverviewDashboard.tsx
│       │   ├── services/
│       │   │   └── api.ts       # Backend API client
│       │   ├── types/
│       │   │   └── index.ts     # TypeScript definitions
│       │   └── utils/           # Helper functions
│       ├── package.json
│       ├── vite.config.ts
│       ├── tailwind.config.js
│       └── tsconfig.json
│
├── data/
│   ├── raw/                     # Unprocessed source data
│   ├── processed/               # Cleaned data
│   ├── cache/                   # API response cache
│   └── robin_sourced/           # Data from Robin (read-only)
│
├── docs/
│   ├── methodology_report_template.tex
│   ├── analysis_report_template.tex
│   ├── executive_summary_template.tex
│   └── reporting_strategy_template.tex
│
├── scripts/
│   ├── download_all_data.py     # Master data acquisition script
│   ├── validate_excel.py        # ONE SHEET validation
│   └── validate_outputs.py      # Druck compliance check
│
├── configs/
│   └── data_sources.json        # Data source configuration
│
├── notebooks/                   # Jupyter notebooks for analysis
│
├── tests/                       # Unit and integration tests
│
├── requirements.txt             # Python dependencies
├── PROGRESS_LOG.md              # Hyper-detailed decision log
└── README.md                    # This file
```

## API Endpoints

### Base URL: http://localhost:8000

#### General
- `GET /` - API welcome and endpoint list
- `GET /docs` - Interactive Swagger UI documentation
- `GET /redoc` - ReDoc API documentation

#### Municipalities
- `GET /api/municipalities`
  - Returns: List of Westchester cities, towns, villages with population
  - Response: `{ county, municipality_count, municipalities: [...] }`

#### Demographics
- `GET /api/demographics/county?year=2022`
  - County-level demographic data
  - Parameters: `year` (default: 2022)
  
- `GET /api/demographics/tracts?year=2022`
  - Census tract-level demographics
  - Parameters: `year` (default: 2022)
  
- `GET /api/demographics/municipalities?year=2022`
  - Municipality-level demographics
  - Parameters: `year` (default: 2022)

#### Transit
- `GET /api/transit/stations`
  - GTFS transit station locations and info
  - Returns: Station data with coordinates

## Running the System

### Development Mode (Recommended)

**Terminal 1 - Backend**:
```bash
cd D:\Arcanum\Projects\Westchester\Technical
.\venv\Scripts\activate
python src/api/main.py
```
- Hot reload enabled
- Debug logging active
- CORS configured for localhost:5173

**Terminal 2 - Frontend**:
```bash
cd D:\Arcanum\Projects\Westchester\Technical\src\frontend
npm run dev
```
- Hot module replacement (HMR)
- Opens browser automatically
- Fast refresh on changes

## Data Processing Standards

### Excel Export (CRITICAL - Druck Mandatory)
**Rule**: ONE SHEET PER FILE - NO EXCEPTIONS

```python
# CORRECT:
import pandas as pd
df.to_excel('output.xlsx', index=False, sheet_name='Data')

# WRONG:
with pd.ExcelWriter('output.xlsx') as writer:
    df1.to_excel(writer, sheet_name='Sheet1')  # ❌
    df2.to_excel(writer, sheet_name='Sheet2')  # ❌
```

**Validation**:
```python
# Run before any handoff
import pandas as pd
xl = pd.ExcelFile('output.xlsx')
assert len(xl.sheet_names) == 1, f"FAILED: {len(xl.sheet_names)} sheets"
```

### Robin Data Integration
**Rule**: NEVER modify original Robin data

```python
# CORRECT workflow:
# 1. Copy from Robin
import shutil
shutil.copy('D:/Arcanum/Robin/data/dataset.xlsx', 
            'Technical/data/robin_sourced/dataset.xlsx')

# 2. Process local copy
df = pd.read_excel('Technical/data/robin_sourced/dataset.xlsx')
# ... processing ...

# 3. Export to Output
df.to_excel('../Output/Data/processed_results.xlsx', index=False)
```

## Troubleshooting

### Backend Won't Start
```bash
# Check Python version
python --version  # Should be 3.11+

# Check dependencies
pip list | grep fastapi

# Reinstall if needed
pip install -r requirements.txt --force-reinstall
```

### Frontend Build Errors
```bash
# Clear node_modules
rm -rf node_modules package-lock.json
npm install

# Check Node version
node --version  # Should be 18+
```

### CORS Errors
Check `src/api/main.py` CORS configuration:
```python
allow_origins=["http://localhost:5173"]  # Add your frontend URL
```

## Development Best Practices

### Druck Standards Compliance
- ✅ ONE SHEET per Excel file
- ✅ LaTeX for all final reports
- ✅ Hyper-detailed PROGRESS_LOG.md
- ✅ NO silent data processing decisions
- ✅ Production quality from day one
- ✅ Mobile-responsive design
- ✅ Fresh environment testing before handoff

## Resources

- **Druck Standards**: `D:/Arcanum/Council/Druck/`
- **Project Index**: `../PROJECT_INDEX.md`
- **Progress Log**: `PROGRESS_LOG.md`
- **API Documentation**: http://localhost:8000/docs

## Current Development Status

**Last Updated**: 2025-10-12
**Completion**: ~10-15% (Druck formula)

**Completed**:
- ✅ Project structure (Shaikh Tonak)
- ✅ Backend API framework
- ✅ Frontend scaffolding
- ✅ LaTeX templates
- ✅ .claude configuration
- ✅ Progress logging

**Next Priorities**:
1. Complete data collection scripts
2. Build frontend components
3. Generate Excel outputs (ONE SHEET)
4. Customize and compile LaTeX reports
5. Validation and testing

---

*This technical documentation follows Druck standards for comprehensive implementation guides.*
*All code follows production-ready standards per AGENT_STANDARDS_AND_BEST_PRACTICES.md Section 1.4.*
