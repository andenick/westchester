import { useState, useEffect } from 'react';
import EnhancedMapComponent from '../../components/map/EnhancedMapComponent';
import ExportButton from '../../components/ExportButton';
import apiService from '../../services/api';

interface InfrastructureStats {
    sidewalks: number;
    bikeLanes: number;
    busStops: number;
    streetLights: number;
}

interface InfrastructureData {
    sidewalks: any | null;
    bikeLanes: any | null;
    busStops: any | null;
    streetLights: any | null;
}

const InfrastructureDashboard: React.FC = () => {
    const [stats, setStats] = useState<InfrastructureStats>({
        sidewalks: 0,
        bikeLanes: 0,
        busStops: 0,
        streetLights: 0
    });
    const [data, setData] = useState<InfrastructureData>({
        sidewalks: null,
        bikeLanes: null,
        busStops: null,
        streetLights: null
    });
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        loadInfrastructureData();
    }, []);

    const loadInfrastructureData = async () => {
        try {
            setLoading(true);

            // Load all infrastructure data in parallel
            const [sidewalksData, bikeLanesData, busStopsData, streetLightsData] = await Promise.allSettled([
                apiService.getSidewalks(),
                apiService.getBikeLanes(),
                apiService.getBusStops(),
                apiService.getStreetLights()
            ]);

            const newStats: InfrastructureStats = {
                sidewalks: 0,
                bikeLanes: 0,
                busStops: 0,
                streetLights: 0
            };

            const newData: InfrastructureData = {
                sidewalks: null,
                bikeLanes: null,
                busStops: null,
                streetLights: null
            };

            if (sidewalksData.status === 'fulfilled') {
                newStats.sidewalks = sidewalksData.value.features?.length || 0;
                newData.sidewalks = sidewalksData.value;
            }

            if (bikeLanesData.status === 'fulfilled') {
                newStats.bikeLanes = bikeLanesData.value.features?.length || 0;
                newData.bikeLanes = bikeLanesData.value;
            }

            if (busStopsData.status === 'fulfilled') {
                newStats.busStops = busStopsData.value.features?.length || 0;
                newData.busStops = busStopsData.value;
            }

            if (streetLightsData.status === 'fulfilled') {
                newStats.streetLights = streetLightsData.value.features?.length || 0;
                newData.streetLights = streetLightsData.value;
            }

            setStats(newStats);
            setData(newData);
            setError(null);
        } catch (err) {
            console.error('Error loading infrastructure data:', err);
            setError('Failed to load infrastructure data');
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
                    <p className="text-gray-600">Loading infrastructure data...</p>
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
                <div className="flex justify-between items-start mb-4">
                    <div className="flex-1">
                        <h1 className="text-4xl font-bold text-gray-900 mb-2">Infrastructure Dashboard</h1>
                        <p className="text-gray-600">
                            Sidewalks, bike lanes, bus stops, and street lights across Westchester County
                        </p>
                        <p className="text-sm text-gray-500 mt-2">
                            Data Source: OpenStreetMap | Last Updated: {new Date().toLocaleDateString()}
                        </p>
                    </div>

                    {/* Export Buttons */}
                    <div className="flex gap-3">
                        {data.sidewalks && (
                            <ExportButton
                                data={data.sidewalks}
                                filename="westchester_sidewalks"
                                label="Export Sidewalks"
                                formats={['csv', 'geojson']}
                                isGeoJSON={true}
                            />
                        )}
                        {data.bikeLanes && (
                            <ExportButton
                                data={data.bikeLanes}
                                filename="westchester_bike_lanes"
                                label="Export Bike Lanes"
                                formats={['csv', 'geojson']}
                                isGeoJSON={true}
                            />
                        )}
                        {data.busStops && (
                            <ExportButton
                                data={data.busStops}
                                filename="westchester_bus_stops"
                                label="Export Bus Stops"
                                formats={['csv', 'geojson']}
                                isGeoJSON={true}
                            />
                        )}
                        {data.streetLights && (
                            <ExportButton
                                data={data.streetLights}
                                filename="westchester_street_lights"
                                label="Export Street Lights"
                                formats={['csv', 'geojson']}
                                isGeoJSON={true}
                            />
                        )}
                    </div>
                </div>

                {/* Data Summary for City Planners */}
                <div className="bg-green-50 border border-green-200 rounded-lg p-4 mt-4">
                    <div className="flex items-start">
                        <svg className="w-6 h-6 text-green-600 mr-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                        </svg>
                        <div>
                            <p className="text-sm font-semibold text-green-900 mb-1">For City Planners:</p>
                            <p className="text-sm text-green-800">
                                {(stats.sidewalks + stats.bikeLanes + stats.busStops + stats.streetLights).toLocaleString()} infrastructure features available for analysis.
                                Use export buttons above to download data in CSV or GeoJSON format for GIS analysis, equity studies, or planning reports.
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Infrastructure Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-8">
                <div className="bg-white rounded-lg shadow-lg p-6 text-center">
                    <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                        <span className="text-2xl">🚶</span>
                    </div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">Sidewalks</h3>
                    <p className="text-3xl font-bold text-orange-600">{stats.sidewalks.toLocaleString()}</p>
                    <p className="text-sm text-gray-500">Pedestrian infrastructure</p>
                </div>

                <div className="bg-white rounded-lg shadow-lg p-6 text-center">
                    <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                        <span className="text-2xl">🚴</span>
                    </div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">Bike Lanes</h3>
                    <p className="text-3xl font-bold text-green-600">{stats.bikeLanes.toLocaleString()}</p>
                    <p className="text-sm text-gray-500">Cycling infrastructure</p>
                </div>

                <div className="bg-white rounded-lg shadow-lg p-6 text-center">
                    <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                        <span className="text-2xl">🚌</span>
                    </div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">Bus Stops</h3>
                    <p className="text-3xl font-bold text-blue-600">{stats.busStops.toLocaleString()}</p>
                    <p className="text-sm text-gray-500">Public transit stops</p>
                </div>

                <div className="bg-white rounded-lg shadow-lg p-6 text-center">
                    <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                        <span className="text-2xl">💡</span>
                    </div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">Street Lights</h3>
                    <p className="text-3xl font-bold text-yellow-600">{stats.streetLights.toLocaleString()}</p>
                    <p className="text-sm text-gray-500">Public lighting</p>
                </div>
            </div>

            {/* Interactive Map */}
            <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
                <h2 className="text-2xl font-bold mb-4">📍 Infrastructure Map</h2>
                <p className="text-gray-600 mb-4">
                    Interactive map showing sidewalks (orange), bike lanes (green), bus stops (blue), and street lights (yellow).
                    Use the layer control to toggle different infrastructure types.
                </p>
                <EnhancedMapComponent
                    height="600px"
                    defaultLayers={['sidewalks', 'bikeLanes', 'busStops', 'streetLights']}
                />
            </div>

            {/* Infrastructure Details */}
            <div className="grid md:grid-cols-2 gap-8 mb-8">
                {/* Sidewalks */}
                <div className="bg-white rounded-lg shadow-lg p-6">
                    <div className="flex items-center mb-4">
                        <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center mr-3">
                            <span className="text-xl">🚶</span>
                        </div>
                        <h3 className="text-xl font-bold text-gray-900">Sidewalks & Pedestrian Infrastructure</h3>
                    </div>
                    <p className="text-gray-600 mb-4">
                        Pedestrian walkways, footpaths, and pedestrian infrastructure throughout Westchester County.
                    </p>
                    <div className="space-y-2">
                        <div className="flex justify-between">
                            <span className="text-sm text-gray-600">Total Features:</span>
                            <span className="text-sm font-semibold">{stats.sidewalks.toLocaleString()}</span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-sm text-gray-600">Data Source:</span>
                            <span className="text-sm font-semibold">OpenStreetMap</span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-sm text-gray-600">Coverage:</span>
                            <span className="text-sm font-semibold">County-wide</span>
                        </div>
                    </div>
                </div>

                {/* Bike Lanes */}
                <div className="bg-white rounded-lg shadow-lg p-6">
                    <div className="flex items-center mb-4">
                        <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center mr-3">
                            <span className="text-xl">🚴</span>
                        </div>
                        <h3 className="text-xl font-bold text-gray-900">Bike Lanes & Cycling Infrastructure</h3>
                    </div>
                    <p className="text-gray-600 mb-4">
                        Dedicated bike lanes, cycleways, and cycling infrastructure for safe bicycle transportation.
                    </p>
                    <div className="space-y-2">
                        <div className="flex justify-between">
                            <span className="text-sm text-gray-600">Total Features:</span>
                            <span className="text-sm font-semibold">{stats.bikeLanes.toLocaleString()}</span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-sm text-gray-600">Data Source:</span>
                            <span className="text-sm font-semibold">OpenStreetMap</span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-sm text-gray-600">Coverage:</span>
                            <span className="text-sm font-semibold">County-wide</span>
                        </div>
                    </div>
                </div>

                {/* Bus Stops */}
                <div className="bg-white rounded-lg shadow-lg p-6">
                    <div className="flex items-center mb-4">
                        <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center mr-3">
                            <span className="text-xl">🚌</span>
                        </div>
                        <h3 className="text-xl font-bold text-gray-900">Bus Stops & Public Transit</h3>
                    </div>
                    <p className="text-gray-600 mb-4">
                        Bus stops and public transit infrastructure including Bee-Line and other transit services.
                    </p>
                    <div className="space-y-2">
                        <div className="flex justify-between">
                            <span className="text-sm text-gray-600">Total Features:</span>
                            <span className="text-sm font-semibold">{stats.busStops.toLocaleString()}</span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-sm text-gray-600">Data Source:</span>
                            <span className="text-sm font-semibold">OpenStreetMap</span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-sm text-gray-600">Coverage:</span>
                            <span className="text-sm font-semibold">County-wide</span>
                        </div>
                    </div>
                </div>

                {/* Street Lights */}
                <div className="bg-white rounded-lg shadow-lg p-6">
                    <div className="flex items-center mb-4">
                        <div className="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center mr-3">
                            <span className="text-xl">💡</span>
                        </div>
                        <h3 className="text-xl font-bold text-gray-900">Street Lights & Public Lighting</h3>
                    </div>
                    <p className="text-gray-600 mb-4">
                        Street lights and public lighting infrastructure for safety and visibility.
                    </p>
                    <div className="space-y-2">
                        <div className="flex justify-between">
                            <span className="text-sm text-gray-600">Total Features:</span>
                            <span className="text-sm font-semibold">{stats.streetLights.toLocaleString()}</span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-sm text-gray-600">Data Source:</span>
                            <span className="text-sm font-semibold">OpenStreetMap</span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-sm text-gray-600">Coverage:</span>
                            <span className="text-sm font-semibold">County-wide</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Data Quality Note */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-blue-900 mb-2">📊 Data Quality & Coverage</h3>
                <p className="text-blue-800 text-sm">
                    Infrastructure data is sourced from OpenStreetMap, a collaborative mapping project.
                    Coverage may vary by municipality and infrastructure type. Some features may be missing
                    or incomplete in areas with limited OpenStreetMap contributions. For the most accurate
                    and up-to-date infrastructure information, consult local municipal records.
                </p>
            </div>
        </div>
    );
};

export default InfrastructureDashboard;
