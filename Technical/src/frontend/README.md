# Westchester County Data Platform - Frontend

React + TypeScript + Vite web application for visualizing and exploring Westchester County data.

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

The application will be available at **http://localhost:3000**

## 🛠️ Technology Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool & dev server
- **Tailwind CSS** - Utility-first CSS
- **React Router** - Client-side routing
- **Leaflet** - Interactive maps
- **Recharts** - Data visualizations
- **Axios** - HTTP client

## 📁 Project Structure

```
src/
├── components/
│   ├── common/         # Reusable UI components (Header, Footer)
│   ├── map/            # Map components (MapComponent)
│   └── charts/         # Chart components
├── pages/
│   ├── HomePage.tsx    # Landing page
│   └── dashboards/     # Dashboard pages
│       └── OverviewDashboard.tsx
├── services/
│   └── api.ts          # API service for backend calls
├── types/
│   └── index.ts        # TypeScript type definitions
├── utils/              # Utility functions
├── App.tsx             # Main app with routing
└── main.tsx            # Entry point
```

## 🔗 API Integration

The frontend connects to the FastAPI backend running on `http://localhost:8000`.

API calls are handled through the `apiService` singleton in `src/services/api.ts`.

### Available Endpoints

- `GET /api/health` - Health check
- `GET /api/stats` - Summary statistics
- `GET /api/transit/stations` - Metro-North stations
- `GET /api/demographics/county` - County demographics
- `GET /api/demographics/tracts` - Census tract data
- `GET /api/demographics/municipalities` - Municipality data
- `GET /api/municipalities` - Municipality list

## 🎨 Styling

### Tailwind CSS

The project uses Tailwind CSS for styling. Configuration in `tailwind.config.js`.

### Custom Colors

- Westchester Green palette: `westchester-green-{50-900}`

### Responsive Design

All components are mobile-responsive using Tailwind's responsive utilities.

## 🗺️ Map Features

The map component uses **Leaflet** with OpenStreetMap tiles (free, no API key required).

To use Mapbox instead:
1. Get a Mapbox access token
2. Add to `.env`: `VITE_MAPBOX_TOKEN=your_token`
3. Update MapComponent to use Mapbox tiles

## 📊 Dashboards

### Implemented
- ✅ HomePage - Landing page
- ✅ Overview Dashboard - County metrics and map

### Planned
- Transit Dashboard - Metro-North analysis
- Demographics Dashboard - Population & housing
- Property Tax Dashboard - Assessment data
- Budget Dashboard - County spending
- Municipal Services Dashboard - Services coverage
- Geographic Explorer - Interactive multi-layer map
- Municipality Comparison - Side-by-side comparisons

## 🧪 Development

### Hot Module Replacement (HMR)

Vite provides instant HMR - changes appear immediately without full page reload.

### TypeScript

All components use TypeScript for type safety. Type definitions in `src/types/`.

### Linting

```bash
npm run lint
```

## 🏗️ Building for Production

```bash
# Create production build
npm run build

# Output will be in dist/
# Deploy dist/ folder to your hosting service
```

### Deployment Options

- **Vercel** - `vercel deploy`
- **Netlify** - `netlify deploy --prod`
- **GitHub Pages** - Configure in vite.config.ts
- **Static hosting** - Upload dist/ folder

## 🔧 Configuration

### Environment Variables

Copy `.env.template` to `.env` and configure:

```bash
VITE_API_URL=http://localhost:8000
```

### Vite Configuration

`vite.config.ts` includes:
- Port: 3000
- API proxy to localhost:8000
- React plugin

## 📝 Adding New Features

### New Dashboard

1. Create component in `src/pages/dashboards/`
2. Add route in `App.tsx`
3. Add navigation link in `Header.tsx`

### New API Endpoint

1. Add method to `src/services/api.ts`
2. Add TypeScript types to `src/types/index.ts`
3. Use in component with `apiService.methodName()`

### New Component

1. Create in appropriate `src/components/` subdirectory
2. Use TypeScript for props
3. Style with Tailwind CSS classes

## 🐛 Troubleshooting

### Port Already in Use

Change port in `vite.config.ts`:
```ts
server: { port: 3001 }
```

### API Connection Error

1. Ensure backend is running on port 8000
2. Check `VITE_API_URL` in .env
3. Verify proxy configuration in vite.config.ts

### Map Not Loading

1. Check Leaflet CSS is imported in index.css
2. Verify map container has height set
3. Check browser console for errors

### Type Errors

Run TypeScript check:
```bash
npx tsc --noEmit
```

## 📚 Documentation

- [React Documentation](https://react.dev/)
- [Vite Documentation](https://vite.dev/)
- [Tailwind CSS](https://tailwindcss.com/)
- [React Router](https://reactrouter.com/)
- [Leaflet](https://leafletjs.com/)
- [Recharts](https://recharts.org/)

## 🤝 Contributing

Follow Druck standards:
- Component-based architecture
- TypeScript for type safety
- Tailwind for styling
- Professional UI/UX
- Mobile-responsive design

---

*Part of the Westchester County Data Platform - Arcanum Projects*
