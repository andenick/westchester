/**
 * Overview Dashboard
 * 
 * High-level county metrics and statistics
 */

import { useEffect, useState } from 'react';
import apiService from '../../services/api';
import EnhancedMapComponent from '../../components/map/EnhancedMapComponent';
import type { DemographicsData, APIStats } from '../../types';

export default function OverviewDashboard() {
    const [stats, setStats] = useState<APIStats | null>(null);
    const [demographics, setDemographics] = useState<DemographicsData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        loadDashboardData();
    }, []);

    const loadDashboardData = async () => {
        try {
            setLoading(true);

            // Load API stats
            const statsData = await apiService.getStats();
            setStats(statsData);

            // Try to load demographics (may fail if data not downloaded yet)
            try {
                const demoData = await apiService.getCountyDemographics();
                setDemographics(demoData);
            } catch (err) {
                console.log('Demographics data not yet available');
            }

            setError(null);
        } catch (err) {
            console.error('Error loading dashboard data:', err);
            setError('Failed to load dashboard data. Make sure the API is running.');
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-westchester-green-600 mx-auto mb-4"></div>
                    <p className="text-gray-600">Loading dashboard...</p>
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

    return (
        <div className="container mx-auto px-4 py-8">
            {/* Header */}
            <div className="mb-8">
                <h1 className="text-4xl font-bold text-gray-900 mb-2">Overview Dashboard</h1>
                <p className="text-gray-600">High-level metrics for Westchester County, New York</p>
            </div>

            {/* Status Cards */}
            <div className="grid md:grid-cols-3 gap-6 mb-8">
                <StatusCard
                    title="County"
                    value="Westchester County, NY"
                    status="active"
                    description="Lower Hudson Valley region"
                />
                <StatusCard
                    title="Data Sources"
                    value={stats ? Object.keys(stats.data_sources).length.toString() : '0'}
                    status={stats && Object.values(stats.data_availability).some(v => v) ? 'active' : 'warning'}
                    description="Integrated data sources"
                />
                <StatusCard
                    title="API Status"
                    value="Connected"
                    status="active"
                    description="Backend API operational"
                />
            </div>

            {/* Demographics Summary (if available) */}
            {demographics && (
                <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
                    <h2 className="text-2xl font-bold mb-4">County Demographics</h2>
                    <div className="grid md:grid-cols-4 gap-6">
                        <DemoCard
                            label="Total Population"
                            value={demographics.total_population?.toLocaleString() || 'N/A'}
                        />
                        <DemoCard
                            label="Median Household Income"
                            value={demographics.median_household_income ? `$${demographics.median_household_income.toLocaleString()}` : 'N/A'}
                        />
                        <DemoCard
                            label="Median Home Value"
                            value={demographics.median_home_value ? `$${demographics.median_home_value.toLocaleString()}` : 'N/A'}
                        />
                        <DemoCard
                            label="Unemployment Rate"
                            value={demographics.unemployed && demographics.civilian_labor_force
                                ? `${((demographics.unemployed / demographics.civilian_labor_force) * 100).toFixed(1)}%`
                                : 'N/A'
                            }
                        />
                    </div>
                    <p className="text-sm text-gray-500 mt-4">
                        Data Year: {demographics.year} | Source: {demographics.dataset}
                    </p>
                </div>
            )}

            {/* Map */}
            <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
                <h2 className="text-2xl font-bold mb-4">Westchester County Interactive Map</h2>
                <p className="text-gray-600 mb-4">
                    Explore Metro-North stations, parks, trails, and amenities. Use the layer control (top right) to toggle different data layers.
                </p>
                <EnhancedMapComponent height="600px" defaultLayers={['stations', 'parks']} />
            </div>

            {/* Data Availability */}
            {stats && (
                <div className="bg-white rounded-lg shadow-lg p-6">
                    <h2 className="text-2xl font-bold mb-4">Data Availability</h2>
                    <div className="space-y-2">
                        {Object.entries(stats.data_availability).map(([key, available]) => (
                            <div key={key} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                                <span className="font-medium capitalize">{key.replace(/_/g, ' ')}</span>
                                <span className={`px-3 py-1 rounded text-sm font-semibold ${available ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                                    }`}>
                                    {available ? '✓ Available' : '⚠ Not Downloaded'}
                                </span>
                            </div>
                        ))}
                    </div>
                    {!Object.values(stats.data_availability).every(v => v) && (
                        <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded">
                            <p className="text-sm text-blue-800">
                                <strong>Note:</strong> Some data has not been downloaded yet. Run the data import scripts to fetch all available data.
                            </p>
                            <pre className="mt-2 text-xs bg-blue-100 p-2 rounded overflow-x-auto">
                                cd Technical{'\n'}
                                python scripts/download_all_data.py
                            </pre>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}

// Helper Components
function StatusCard({ title, value, status, description }: {
    title: string;
    value: string;
    status: 'active' | 'warning' | 'error';
    description: string;
}) {
    const statusColors = {
        active: 'bg-green-100 text-green-800',
        warning: 'bg-yellow-100 text-yellow-800',
        error: 'bg-red-100 text-red-800',
    };

    return (
        <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-sm font-semibold text-gray-600 mb-2">{title}</h3>
            <p className="text-2xl font-bold mb-1">{value}</p>
            <p className="text-sm text-gray-500">{description}</p>
            <span className={`inline-block mt-3 px-2 py-1 rounded text-xs font-semibold ${statusColors[status]}`}>
                {status.toUpperCase()}
            </span>
        </div>
    );
}

function DemoCard({ label, value }: { label: string; value: string }) {
    return (
        <div>
            <p className="text-sm text-gray-600 mb-1">{label}</p>
            <p className="text-2xl font-bold">{value}</p>
        </div>
    );
}

