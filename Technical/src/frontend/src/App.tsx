/**
 * Main App Component
 * 
 * Root component with routing and layout
 */

import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/common/Header';
import Footer from './components/common/Footer';
import HomePage from './pages/HomePage';
import LandingPage from './pages/dashboards/LandingPage';
import OverviewDashboard from './pages/dashboards/OverviewDashboard';
import DemographicsDashboard from './pages/dashboards/DemographicsDashboard';
import TransitDashboard from './pages/dashboards/TransitDashboard';
import PropertyTaxDashboard from './pages/dashboards/PropertyTaxDashboard';
import BudgetDashboard from './pages/dashboards/BudgetDashboard';
import MunicipalServicesDashboard from './pages/dashboards/MunicipalServicesDashboard';
import MunicipalityComparisonDashboard from './pages/dashboards/MunicipalityComparisonDashboard';
import HistoricalTrendsDashboard from './pages/dashboards/HistoricalTrendsDashboard';
import InfrastructureDashboard from './pages/dashboards/InfrastructureDashboard';
import SidewalkPlanningDashboard from './pages/dashboards/SidewalkPlanningDashboard';
import DataCatalogPage from './pages/DataCatalogPage';
import AboutPage from './pages/AboutPage';
import UserGuidePage from './pages/UserGuidePage';
import DataSourcesPage from './pages/DataSourcesPage';

function App() {
  return (
    <Router>
      <div className="flex flex-col min-h-screen">
        <Header />
        <main className="flex-grow">
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/home" element={<HomePage />} />
            <Route path="/data-catalog" element={<DataCatalogPage />} />
            <Route path="/overview" element={<OverviewDashboard />} />
            <Route path="/demographics" element={<DemographicsDashboard />} />
            <Route path="/transit" element={<TransitDashboard />} />
            <Route path="/property-tax" element={<PropertyTaxDashboard />} />
            <Route path="/budget" element={<BudgetDashboard />} />
            <Route path="/municipal-services" element={<MunicipalServicesDashboard />} />
            <Route path="/municipality-comparison" element={<MunicipalityComparisonDashboard />} />
            <Route path="/historical-trends" element={<HistoricalTrendsDashboard />} />
            <Route path="/infrastructure" element={<InfrastructureDashboard />} />
            <Route path="/sidewalk-planning" element={<SidewalkPlanningDashboard />} />
            <Route path="/about" element={<AboutPage />} />
            <Route path="/user-guide" element={<UserGuidePage />} />
            <Route path="/data-sources" element={<DataSourcesPage />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </Router>
  );
}

// 404 Page
function NotFound() {
  return (
    <div className="container mx-auto px-4 py-16 text-center">
      <h1 className="text-4xl font-bold mb-4">404 - Page Not Found</h1>
      <p className="text-gray-600 mb-8">The page you're looking for doesn't exist.</p>
      <a href="/" className="bg-westchester-green-600 text-white px-6 py-3 rounded-lg hover:bg-westchester-green-700">
        Go Home
      </a>
    </div>
  );
}

export default App;
