/**
 * Transit Dashboard
 * 
 * Metro-North accessibility analysis for Westchester County
 */

import React, { useEffect, useState } from 'react';
import apiService from '../../services/api';
import MapComponent from '../../components/map/MapComponent';
import { TransitCoverageChart } from '../../components/charts';
import ExportButton from '../../components/ExportButton';

// Error Boundary Component
class TransitErrorBoundary extends React.Component<
    { children: React.ReactNode },
    { hasError: boolean; error?: Error }
> {
    constructor(props: { children: React.ReactNode }) {
        super(props);
        this.state = { hasError: false };
    }

    static getDerivedStateFromError(error: Error) {
        return { hasError: true, error };
    }

    componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
        console.error('Transit Dashboard Error:', error, errorInfo);
    }

    render() {
        if (this.state.hasError) {
            return (
                <div className="container mx-auto px-4 py-8">
                    <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
                        <p className="font-bold">Transit Dashboard Error</p>
                        <p>Something went wrong loading the transit dashboard.</p>
                        <button
                            onClick={() => this.setState({ hasError: false })}
                            className="mt-2 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
                        >
                            Try Again
                        </button>
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}

interface Station {
    name: string;
    id: string;
    code?: string;
    wheelchair_accessible?: boolean;
    coordinates: [number, number];
}

function TransitDashboardContent() {
    const [stations, setStations] = useState<Station[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        loadTransitData();
    }, []);

    const loadTransitData = async () => {
        try {
            setLoading(true);
            const data = await apiService.getTransitStations();
            setStations(data);
            setError(null);
        } catch (err) {
            console.error('Error loading transit data:', err);
            setError('Failed to load transit data. Make sure the API is running and data is downloaded.');
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-green-600 mx-auto mb-4"></div>
                    <p className="text-gray-600">Loading transit data...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="container mx-auto px-4 py-8">
                <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
                    <p className="font-bold">Error</p>
                    <p>{error}</p>
                </div>
            </div>
        );
    }

    // Calculate statistics
    const totalStations = stations.length;
    const accessibleStations = stations.filter(s => s.wheelchair_accessible).length;

    // Prepare chart data (mock line data for now)
    const chartStations = stations.map(s => ({
        name: s.name,
        line: 'Metro-North', // TODO: Extract from actual data
    }));

    return (
        <div className="container mx-auto px-4 py-8">
            {/* Header */}
            <div className="mb-8">
                <div className="flex justify-between items-start mb-4">
                    <div className="flex-1">
                        <h1 className="text-4xl font-bold text-gray-900 mb-2">Transit Accessibility Dashboard</h1>
                        <p className="text-gray-600">
                            Metro-North Railroad coverage analysis for Westchester County
                        </p>
                        <p className="text-sm text-gray-500 mt-2">
                            Data Source: Metro-North Railroad GTFS | {totalStations} stations
                        </p>
                    </div>

                    {/* Export Button */}
                    <div className="flex gap-3">
                        {stations.length > 0 && (
                            <ExportButton
                                data={stations}
                                filename="westchester_transit_stations"
                                label="Export Stations"
                                formats={['csv', 'json']}
                            />
                        )}
                    </div>
                </div>

                {/* Data Summary for City Planners */}
                <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                    <div className="flex items-start">
                        <svg className="w-6 h-6 text-purple-600 mr-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                        </svg>
                        <div>
                            <p className="text-sm font-semibold text-purple-900 mb-1">For City Planners:</p>
                            <p className="text-sm text-purple-800">
                                {totalStations} Metro-North stations with accessibility data available for analysis.
                                Use export button to download station locations, accessibility status, and coverage data for transit equity studies,
                                walkability analysis, or transit-oriented development planning.
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Summary Cards */}
            <div className="grid md:grid-cols-4 gap-6 mb-8">
                <StatCard
                    label="Total Stations"
                    value={totalStations.toString()}
                    icon="🚂"
                />
                <StatCard
                    label="Wheelchair Accessible"
                    value={accessibleStations.toString()}
                    icon="♿"
                    subtext={`${((accessibleStations / totalStations) * 100).toFixed(0)}% of stations`}
                />
                <StatCard
                    label="Coverage Area"
                    value="1-mile radius"
                    icon="📍"
                    subtext="Per station walkability"
                />
                <StatCard
                    label="Transit Lines"
                    value="3 Lines"
                    icon="🛤️"
                    subtext="Harlem, Hudson, New Haven"
                />
            </div>

            {/* Interactive Map */}
            <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
                <h2 className="text-2xl font-bold mb-4">Station Locations Map</h2>
                <p className="text-gray-600 mb-4">
                    Interactive map showing all {totalStations} Metro-North stations in Westchester County.
                    Click on markers for station details.
                </p>
                <MapComponent height="600px" showStations={true} />
            </div>

            {/* Coverage Chart */}
            <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
                <h2 className="text-2xl font-bold mb-4">Stations by Line</h2>
                <TransitCoverageChart stations={chartStations} height={350} chartType="bar" />
            </div>

            {/* Station List */}
            <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
                <h2 className="text-2xl font-bold mb-4">Station Directory</h2>
                <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                            <tr>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Station Name
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Station Code
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Accessibility
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Coordinates
                                </th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {stations.slice(0, 20).map((station, idx) => (
                                <tr key={station.id || idx}>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                        {station.name}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                        {station.code || 'N/A'}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                        {station.wheelchair_accessible ? (
                                            <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                                                ♿ Accessible
                                            </span>
                                        ) : (
                                            <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-gray-100 text-gray-800">
                                                Not Accessible
                                            </span>
                                        )}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 font-mono">
                                        {station.coordinates[1].toFixed(4)}, {station.coordinates[0].toFixed(4)}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                    {stations.length > 20 && (
                        <p className="text-sm text-gray-500 mt-4 text-center">
                            Showing 20 of {stations.length} stations
                        </p>
                    )}
                </div>
            </div>

            {/* Accessibility Analysis */}
            <div className="bg-white rounded-lg shadow-lg p-6">
                <h2 className="text-2xl font-bold mb-4">Transit Accessibility Insights</h2>
                <div className="grid md:grid-cols-2 gap-6">
                    <InsightCard
                        title="1-Mile Walkability"
                        description="Each station provides transit access within a 1-mile walking radius, covering significant portions of residential areas."
                        metric={`${totalStations} stations`}
                    />
                    <InsightCard
                        title="Accessibility Compliance"
                        description={`${accessibleStations} out of ${totalStations} stations are wheelchair accessible, meeting ADA requirements.`}
                        metric={`${((accessibleStations / totalStations) * 100).toFixed(0)}% compliant`}
                    />
                </div>
            </div>
        </div>
    );
}

// Helper Components
function StatCard({ label, value, icon, subtext }: {
    label: string;
    value: string;
    icon: string;
    subtext?: string;
}) {
    return (
        <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center justify-between mb-2">
                <p className="text-sm text-gray-600">{label}</p>
                <span className="text-2xl">{icon}</span>
            </div>
            <p className="text-2xl font-bold">{value}</p>
            {subtext && <p className="text-xs text-gray-500 mt-1">{subtext}</p>}
        </div>
    );
}

function InsightCard({ title, description, metric }: {
    title: string;
    description: string;
    metric: string;
}) {
    return (
        <div className="p-4 bg-blue-50 rounded-lg">
            <h3 className="text-lg font-semibold mb-2">{title}</h3>
            <p className="text-sm text-gray-700 mb-3">{description}</p>
            <p className="text-xl font-bold text-blue-600">{metric}</p>
        </div>
    );
}

// Export with error boundary
export default function TransitDashboard() {
    return (
        <TransitErrorBoundary>
            <TransitDashboardContent />
        </TransitErrorBoundary>
    );
}

