# Best Practices Guide: Data Visualization Platforms

## Code Architecture Standards for All Projects

This document outlines coding standards, architecture patterns, and best practices for building interactive data visualization platforms.

---

## 🏗️ Project Structure

### Monorepo Organization
```
project-root/
├── Technical/
│   ├── src/
│   │   ├── api/                    # Backend
│   │   │   ├── main.py
│   │   │   ├── requirements.txt
│   │   │   └── data/
│   │   ├── frontend/               # Frontend
│   │   │   ├── src/
│   │   │   ├── public/
│   │   │   └── package.json
│   │   ├── data_importers/         # Data fetching
│   │   └── processors/             # Data processing
│   ├── scripts/                    # Automation scripts
│   └── docs/                       # LaTeX reports
├── Output/                         # Generated outputs
│   ├── Excel/
│   └── PDFs/
├── DEPLOYMENT_GUIDE.md
├── BEST_PRACTICES.md
└── README.md
```

---

## 💻 Code Standards

### TypeScript/React

**Component Structure:**
```typescript
/**
 * Component Name
 * 
 * Brief description of what this component does
 */

import { useState, useEffect } from 'react';
import type { ComponentProps } from '../types';

interface Props {
    data: DataType;
    onUpdate?: (value: string) => void;
}

export default function ComponentName({ data, onUpdate }: Props) {
    const [state, setState] = useState<StateType>(initialValue);

    useEffect(() => {
        // Side effects
    }, [dependencies]);

    return (
        <div className="container">
            {/* JSX */}
        </div>
    );
}
```

**Type Safety:**
- Define interfaces for all props
- Use `type` for type aliases
- Avoid `any` - use `unknown` if needed
- Export types for reuse across files

**Naming Conventions:**
- Components: PascalCase (`DashboardCard.tsx`)
- Functions: camelCase (`fetchData()`)
- Constants: UPPER_SNAKE_CASE (`API_BASE_URL`)
- Files: Match component name (`DashboardCard.tsx`)

### Python/FastAPI

**API Endpoint Structure:**
```python
@app.get("/api/resource/{id}", 
    response_model=ResourceResponse,
    summary="Get resource by ID",
    description="Detailed description of what this endpoint does"
)
async def get_resource(id: str) -> ResourceResponse:
    """
    Get a specific resource by its unique identifier.
    
    Args:
        id: Unique resource identifier
        
    Returns:
        ResourceResponse with resource data
        
    Raises:
        HTTPException: 404 if resource not found
    """
    try:
        data = await fetch_resource(id)
        return ResourceResponse(**data)
    except ResourceNotFound:
        raise HTTPException(status_code=404, detail="Resource not found")
```

**Code Organization:**
- One endpoint per function
- Type hints for all parameters
- Docstrings for all functions
- Error handling with appropriate HTTP status codes

---

## 🎨 UI/UX Standards

### Color Palette (Accessible)

**Primary Colors:**
```css
--primary-green: #059669;      /* Main brand color */
--primary-blue: #3B82F6;       /* Accent color */
--primary-amber: #F59E0B;      /* Warning/highlight */
```

**Semantic Colors:**
```css
--success: #10B981;
--warning: #F59E0B;
--error: #EF4444;
--info: #3B82F6;
```

**Neutrals:**
```css
--gray-50: #F9FAFB;
--gray-100: #F3F4F6;
--gray-600: #4B5563;
--gray-900: #111827;
```

**Contrast Requirements:**
- Text on white: ≥4.5:1 contrast ratio
- Interactive elements: ≥3:1 contrast ratio
- Test with tools like WebAIM Contrast Checker

### Responsive Design

**Breakpoints (Tailwind):**
```javascript
sm: '640px',   // Mobile landscape
md: '768px',   // Tablet
lg: '1024px',  // Desktop
xl: '1280px',  // Large desktop
2xl: '1536px'  // Extra large
```

**Mobile-First Approach:**
```tsx
// Base styles for mobile, add responsive classes
<div className="p-4 md:p-6 lg:p-8">
    <h1 className="text-2xl md:text-3xl lg:text-4xl">Title</h1>
</div>
```

### Loading States

**Always show loading states:**
```tsx
{loading ? (
    <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
    </div>
) : (
    <DataDisplay data={data} />
)}
```

### Error Handling

**User-friendly error messages:**
```tsx
{error && (
    <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <h3 className="text-red-800 font-semibold">Error Loading Data</h3>
        <p className="text-red-600 text-sm mt-1">{error.message}</p>
        <button onClick={retry} className="mt-3 text-red-700 underline">
            Try Again
        </button>
    </div>
)}
```

---

## 📊 Data Visualization Best Practices

### Chart Design

**1. Always Include:**
- Clear title
- Axis labels with units
- Legend (if multiple series)
- Tooltips for detailed data
- Responsive sizing

**2. Color Usage:**
- Max 7 colors per chart
- Use colorblind-safe palettes
- Consistent colors across dashboards
- Semantic colors (green=positive, red=negative)

**3. Chart Selection:**
- **Line charts:** Time series, trends
- **Bar charts:** Comparisons, categories
- **Pie charts:** Proportions (max 5 slices)
- **Scatter plots:** Correlations, distributions
- **Maps:** Geographic data

**Example Implementation:**
```tsx
<ResponsiveContainer width="100%" height={400}>
    <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
        <XAxis 
            dataKey="year" 
            label={{ value: 'Year', position: 'bottom' }}
        />
        <YAxis 
            label={{ value: 'Population', angle: -90, position: 'left' }}
        />
        <Tooltip 
            formatter={(value: number) => value.toLocaleString()}
        />
        <Legend />
        <Line 
            type="monotone" 
            dataKey="population" 
            stroke="#059669" 
            strokeWidth={2}
        />
    </LineChart>
</ResponsiveContainer>
```

### Map Design

**1. Base Map Selection:**
- Light theme for data overlay
- OpenStreetMap for detailed streets
- CartoDB Positron for minimal base
- Dark theme only with light data

**2. Layer Organization:**
- Base layers (boundaries, geography)
- Data layers (points, lines, polygons)
- Labels on top
- Max 5 visible layers at once

**3. Marker Design:**
- Consistent icon system
- Size based on importance
- Color coded by category
- Hover states for interactivity

**4. Performance:**
- Cluster markers if >100 points
- Simplify geometries for large polygons
- Lazy load layers
- Use GeoJSON for efficiency

---

## 🔌 API Design Patterns

### RESTful Endpoints

**Structure:**
```
GET    /api/resource           # List all
GET    /api/resource/{id}      # Get one
POST   /api/resource           # Create
PUT    /api/resource/{id}      # Update
DELETE /api/resource/{id}      # Delete
```

**Naming:**
- Use nouns, not verbs
- Plural for collections
- Hierarchical for relationships: `/api/county/{id}/municipalities`

### Response Format

**Consistent structure:**
```json
{
    "success": true,
    "data": {
        "id": "123",
        "name": "Resource"
    },
    "metadata": {
        "timestamp": "2025-10-13T12:00:00Z",
        "source": "Census API"
    }
}
```

**Error format:**
```json
{
    "success": false,
    "error": {
        "code": "NOT_FOUND",
        "message": "Resource not found",
        "details": "No resource with ID 123"
    }
}
```

### Pagination

**For large datasets:**
```python
@app.get("/api/resource")
async def list_resources(
    skip: int = 0, 
    limit: int = 100
):
    total = await count_resources()
    items = await get_resources(skip, limit)
    
    return {
        "items": items,
        "total": total,
        "skip": skip,
        "limit": limit
    }
```

---

## 🚀 Performance Optimization

### Frontend

**1. Code Splitting:**
```tsx
import { lazy, Suspense } from 'react';

const DashboardPage = lazy(() => import('./pages/DashboardPage'));

function App() {
    return (
        <Suspense fallback={<Loading />}>
            <DashboardPage />
        </Suspense>
    );
}
```

**2. Memoization:**
```tsx
import { useMemo, memo } from 'react';

const ExpensiveComponent = memo(function ExpensiveComponent({ data }) {
    const processedData = useMemo(() => 
        expensiveCalculation(data),
        [data]
    );
    
    return <Chart data={processedData} />;
});
```

**3. Image Optimization:**
- Use WebP format
- Lazy load images: `loading="lazy"`
- Responsive images with `srcset`
- Compress images (<200KB)

### Backend

**1. Caching:**
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_census_data(year: int):
    # Expensive API call
    return fetch_from_census(year)
```

**2. Async Operations:**
```python
import asyncio

async def fetch_all_data():
    results = await asyncio.gather(
        fetch_census_data(),
        fetch_transit_data(),
        fetch_property_data()
    )
    return combine_results(results)
```

**3. Database Optimization:**
- Index frequently queried fields
- Use connection pooling
- Limit query result size

---

## 🧪 Testing Standards

### Frontend Tests

**Component Testing:**
```tsx
import { render, screen } from '@testing-library/react';
import DashboardCard from './DashboardCard';

test('displays title correctly', () => {
    render(<DashboardCard title="Test" value={100} />);
    expect(screen.getByText('Test')).toBeInTheDocument();
});
```

**Integration Testing:**
```tsx
import { renderWithRouter } from './test-utils';

test('navigation works', async () => {
    const { user } = renderWithRouter(<App />);
    await user.click(screen.getByText('Demographics'));
    expect(screen.getByRole('heading', { name: /demographics/i })).toBeInTheDocument();
});
```

### Backend Tests

**API Testing:**
```python
from fastapi.testclient import TestClient

def test_get_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

---

## 📝 Documentation Standards

### Code Comments

**When to comment:**
- Complex algorithms
- Non-obvious business logic
- Workarounds or hacks
- Public API functions

**When NOT to comment:**
- Obvious code (let code be self-documenting)
- Redundant descriptions

**Good example:**
```typescript
// Calculate median income excluding outliers (>99th percentile)
// to prevent skewing from ultra-wealthy households
const medianIncome = calculateMedian(
    incomes.filter(i => i < percentile99)
);
```

### README Files

**Each major component should have a README:**
```markdown
# Component Name

## Purpose
What this component does and why it exists

## Usage
How to use this component with examples

## Props/Parameters
List of all configuration options

## Dependencies
What this component depends on

## Examples
Code examples showing common use cases
```

---

## 🔐 Security Best Practices

### Environment Variables

**Never commit:**
- API keys
- Passwords
- Database credentials
- Secret tokens

**Use .env files:**
```env
# .env.local (not in git)
CENSUS_API_KEY=your_key_here
DATABASE_URL=postgresql://...
```

### Input Validation

**Frontend:**
```tsx
const validateEmail = (email: string): boolean => {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
};
```

**Backend:**
```python
from pydantic import BaseModel, validator

class UserInput(BaseModel):
    email: str
    age: int
    
    @validator('age')
    def age_must_be_positive(cls, v):
        if v < 0:
            raise ValueError('Age must be positive')
        return v
```

### CORS Configuration

**Be specific with origins:**
```python
# Don't use "*" in production
allow_origins=[
    "https://yourdomain.com",
    "https://app.yourdomain.com"
]
```

---

## 📦 Dependency Management

### Frontend (package.json)

**Use exact versions for critical deps:**
```json
{
    "dependencies": {
        "react": "19.1.1",              // Exact version
        "axios": "^1.12.2"              // Minor updates OK
    }
}
```

**Regular updates:**
```bash
npm outdated
npm update
```

### Backend (requirements.txt)

**Pin major versions:**
```txt
fastapi>=0.104.0,<0.105.0
uvicorn[standard]>=0.24.0,<0.25.0
```

---

## 🎯 Accessibility (a11y)

### Semantic HTML

```tsx
// Good - semantic elements
<nav>
    <ul>
        <li><a href="/home">Home</a></li>
    </ul>
</nav>

// Bad - div soup
<div className="nav">
    <div onClick={goHome}>Home</div>
</div>
```

### ARIA Labels

```tsx
<button 
    onClick={handleDelete}
    aria-label="Delete user John Doe"
>
    <TrashIcon />
</button>
```

### Keyboard Navigation

- All interactive elements accessible via Tab
- Enter/Space activates buttons
- Escape closes modals
- Arrow keys navigate lists

---

## 🔄 Git Workflow

### Commit Messages

**Format:**
```
type(scope): short description

Longer description if needed

Fixes #123
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance

**Examples:**
```
feat(dashboard): add population trend chart

fix(api): resolve CORS issue for Netlify domain

docs(readme): update deployment instructions
```

### Branch Strategy

```
main           # Production-ready code
└── develop    # Integration branch
    ├── feature/add-sidewalk-data
    ├── feature/county-boundary
    └── fix/map-loading-error
```

---

## 🎉 Summary Checklist

Before deploying any project, ensure:

- [ ] Code follows TypeScript/Python standards
- [ ] All components have proper TypeScript types
- [ ] API endpoints have proper error handling
- [ ] Loading and error states implemented
- [ ] Responsive design tested (mobile, tablet, desktop)
- [ ] Colors meet accessibility contrast requirements
- [ ] No API keys or secrets in code
- [ ] Environment variables properly configured
- [ ] Build succeeds without errors
- [ ] Documentation is up to date
- [ ] Git commits are clear and descriptive

---

**Remember: Consistency across projects makes maintenance easier. When in doubt, refer back to this guide!**

