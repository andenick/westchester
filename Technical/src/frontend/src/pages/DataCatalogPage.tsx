/**
 * Data Catalog Page
 *
 * Comprehensive listing of all downloadable datasets for city planners
 */

import { useState } from 'react';
import { Link } from 'react-router-dom';
import apiService from '../services/api';
import ExportButton from '../components/ExportButton';

interface DatasetInfo {
    id: string;
    title: string;
    description: string;
    category: string;
    source: string;
    lastUpdated: string;
    features?: number;
    status: 'ready' | 'loading' | 'error';
    useCases: string[];
    formats: ('csv' | 'json' | 'geojson')[];
    dashboardLink?: string;
}

export default function DataCatalogPage() {
    const datasets: DatasetInfo[] = [
        {
            id: 'sidewalks',
            title: 'Sidewalks',
            description: 'Pedestrian walkways, footpaths, and pedestrian infrastructure throughout Westchester County.',
            category: 'Infrastructure',
            source: 'OpenStreetMap',
            lastUpdated: '2025-10-15',
            features: 209000,
            status: 'ready',
            useCases: [
                'Pedestrian accessibility analysis',
                'Walkability scoring',
                'ADA compliance mapping',
                'Sidewalk gap analysis'
            ],
            formats: ['csv', 'geojson'],
            dashboardLink: '/infrastructure'
        },
        {
            id: 'bike_lanes',
            title: 'Bike Lanes',
            description: 'Dedicated bike lanes, cycleways, and cycling infrastructure for safe bicycle transportation.',
            category: 'Infrastructure',
            source: 'OpenStreetMap',
            lastUpdated: '2025-10-15',
            features: 11000,
            status: 'ready',
            useCases: [
                'Cycling network analysis',
                'Bike infrastructure planning',
                'Safe routes identification',
                'Active transportation studies'
            ],
            formats: ['csv', 'geojson'],
            dashboardLink: '/infrastructure'
        },
        {
            id: 'bus_stops',
            title: 'Bus Stops',
            description: 'Bus stops and public transit infrastructure including Bee-Line and other transit services.',
            category: 'Infrastructure',
            source: 'OpenStreetMap',
            lastUpdated: '2025-10-15',
            features: 11000,
            status: 'ready',
            useCases: [
                'Transit coverage analysis',
                'Service gap identification',
                'Transit equity studies',
                'Multi-modal planning'
            ],
            formats: ['csv', 'geojson'],
            dashboardLink: '/infrastructure'
        },
        {
            id: 'street_lights',
            title: 'Street Lights',
            description: 'Street lights and public lighting infrastructure for safety and visibility.',
            category: 'Infrastructure',
            source: 'OpenStreetMap',
            lastUpdated: '2025-10-15',
            features: 7000,
            status: 'ready',
            useCases: [
                'Public safety planning',
                'Lighting coverage analysis',
                'Crime prevention studies',
                'Energy efficiency planning'
            ],
            formats: ['csv', 'geojson'],
            dashboardLink: '/infrastructure'
        },
        {
            id: 'transit_stations',
            title: 'Metro-North Stations',
            description: 'Metro-North Railroad stations with accessibility information and coverage data.',
            category: 'Transit',
            source: 'Metro-North Railroad GTFS',
            lastUpdated: '2025-10-15',
            features: 56,
            status: 'ready',
            useCases: [
                'Transit-oriented development',
                'Accessibility compliance',
                'Walkability to transit',
                'Transit equity analysis'
            ],
            formats: ['csv', 'json'],
            dashboardLink: '/transit'
        },
        {
            id: 'county_demographics',
            title: 'County Demographics',
            description: 'Population, income, housing, and employment statistics for Westchester County.',
            category: 'Demographics',
            source: 'U.S. Census Bureau (ACS 2022)',
            lastUpdated: '2025-10-15',
            status: 'ready',
            useCases: [
                'Demographic trend analysis',
                'Housing needs assessment',
                'Economic development',
                'Service demand forecasting'
            ],
            formats: ['csv', 'json'],
            dashboardLink: '/demographics'
        },
        {
            id: 'municipality_demographics',
            title: 'Municipality Demographics',
            description: 'Detailed demographic data for 6 municipalities including population, income, and housing.',
            category: 'Demographics',
            source: 'U.S. Census Bureau (ACS 2022)',
            lastUpdated: '2025-10-15',
            features: 6,
            status: 'ready',
            useCases: [
                'Comparative analysis',
                'Regional planning',
                'Equity assessments',
                'Grant applications'
            ],
            formats: ['csv', 'json'],
            dashboardLink: '/demographics'
        },
        {
            id: 'budget',
            title: 'County Budget (2023-2025)',
            description: 'Operating and capital budget data for Westchester County departments.',
            category: 'Finance',
            source: 'Westchester County Budget Office',
            lastUpdated: '2025-10-15',
            status: 'ready',
            useCases: [
                'Budget trend analysis',
                'Resource allocation planning',
                'Fiscal impact studies',
                'Departmental comparisons'
            ],
            formats: ['csv', 'json'],
            dashboardLink: '/budget'
        },
        {
            id: 'planning_budget',
            title: 'Planning Department Budget (2022-2025)',
            description: 'Detailed budget data for the Westchester County Planning Department including expenditures, revenues, tax levy, staffing, and major grant programs across FY2022, 2023, and 2025.',
            category: 'Finance',
            source: 'Westchester County Operating Budget PDFs',
            lastUpdated: '2025-10-15',
            status: 'ready',
            useCases: [
                'Planning Department trend analysis',
                'Grant funding assessment',
                'Staffing and resource planning',
                'Multi-year budget comparisons'
            ],
            formats: ['json'],
            dashboardLink: '/budget'
        },
        {
            id: 'regional_comparison',
            title: 'Regional Comparison (NYC Neighboring Counties)',
            description: 'Comparative demographic data for Westchester, Rockland, Putnam, and Nassau counties for regional benchmarking and analysis.',
            category: 'Demographics',
            source: 'U.S. Census Bureau (ACS 2022)',
            lastUpdated: '2025-10-15',
            features: 4,
            status: 'ready',
            useCases: [
                'Regional benchmarking',
                'Comparative demographic analysis',
                'Grant applications',
                'Economic development planning'
            ],
            formats: ['json'],
            dashboardLink: '/demographics'
        }
    ];

    const [dataCache, setDataCache] = useState<Record<string, any>>({});
    const [loading, setLoading] = useState<Record<string, boolean>>({});

    // Pre-load data when user hovers over export button
    const handlePreload = async (datasetId: string) => {
        if (dataCache[datasetId] || loading[datasetId]) {
            return; // Already loaded or loading
        }

        setLoading({ ...loading, [datasetId]: true });

        try {
            let data;
            switch (datasetId) {
                case 'sidewalks':
                    data = await apiService.getSidewalks();
                    break;
                case 'bike_lanes':
                    data = await apiService.getBikeLanes();
                    break;
                case 'bus_stops':
                    data = await apiService.getBusStops();
                    break;
                case 'street_lights':
                    data = await apiService.getStreetLights();
                    break;
                case 'transit_stations':
                    data = await apiService.getTransitStations();
                    break;
                case 'county_demographics':
                    data = await apiService.getCountyDemographics();
                    break;
                case 'municipality_demographics':
                    data = await apiService.getMunicipalityDemographics();
                    break;
                case 'budget':
                    data = await fetch('http://localhost:8000/api/budget').then(res => res.json());
                    break;
                case 'planning_budget':
                    data = await fetch('http://localhost:8000/api/budget/planning').then(res => res.json());
                    break;
                case 'regional_comparison':
                    data = await fetch('http://localhost:8000/api/regional/comparison').then(res => res.json());
                    break;
            }

            setDataCache({ ...dataCache, [datasetId]: data });
        } catch (error) {
            console.error(`Error preloading ${datasetId}:`, error);
        } finally {
            setLoading({ ...loading, [datasetId]: false });
        }
    };

    // Group datasets by category
    const groupedDatasets = datasets.reduce((acc, dataset) => {
        if (!acc[dataset.category]) {
            acc[dataset.category] = [];
        }
        acc[dataset.category].push(dataset);
        return acc;
    }, {} as Record<string, DatasetInfo[]>);

    const totalFeatures = datasets.reduce((sum, ds) => sum + (ds.features || 0), 0);

    return (
        <div className="container mx-auto px-4 py-8">
            {/* Header */}
            <div className="mb-8">
                <h1 className="text-4xl font-bold text-gray-900 mb-2">Data Catalog</h1>
                <p className="text-gray-600 mb-4">
                    Comprehensive listing of all downloadable datasets for planning and analysis
                </p>

                {/* Summary Stats */}
                <div className="grid md:grid-cols-4 gap-4 mb-6">
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                        <p className="text-sm text-blue-800 font-semibold">Total Datasets</p>
                        <p className="text-3xl font-bold text-blue-900">{datasets.length}</p>
                    </div>
                    <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                        <p className="text-sm text-green-800 font-semibold">Total Features</p>
                        <p className="text-3xl font-bold text-green-900">{totalFeatures.toLocaleString()}+</p>
                    </div>
                    <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                        <p className="text-sm text-purple-800 font-semibold">Categories</p>
                        <p className="text-3xl font-bold text-purple-900">{Object.keys(groupedDatasets).length}</p>
                    </div>
                    <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
                        <p className="text-sm text-orange-800 font-semibold">Data Quality</p>
                        <p className="text-3xl font-bold text-orange-900">100%</p>
                        <p className="text-xs text-orange-700">Real Data</p>
                    </div>
                </div>

                {/* Info Banner */}
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <div className="flex items-start">
                        <svg className="w-6 h-6 text-blue-600 mr-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                        </svg>
                        <div>
                            <p className="text-sm font-semibold text-blue-900 mb-1">For City Planners:</p>
                            <p className="text-sm text-blue-800">
                                All datasets are available for immediate download in multiple formats. Data is sourced from
                                official government agencies and open data sources. Use these datasets for GIS analysis,
                                planning studies, equity assessments, grant applications, and policy development.
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Datasets by Category */}
            {Object.entries(groupedDatasets).map(([category, categoryDatasets]) => (
                <div key={category} className="mb-8">
                    <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center">
                        {category === 'Infrastructure' && '🏗️'}
                        {category === 'Transit' && '🚊'}
                        {category === 'Demographics' && '👥'}
                        {category === 'Finance' && '💰'}
                        <span className="ml-2">{category}</span>
                        <span className="ml-3 text-sm font-normal text-gray-500">
                            ({categoryDatasets.length} dataset{categoryDatasets.length !== 1 ? 's' : ''})
                        </span>
                    </h2>

                    <div className="grid md:grid-cols-1 gap-4">
                        {categoryDatasets.map(dataset => (
                            <div
                                key={dataset.id}
                                className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-lg transition-shadow"
                            >
                                <div className="flex justify-between items-start mb-4">
                                    <div className="flex-1">
                                        <div className="flex items-center mb-2">
                                            <h3 className="text-xl font-bold text-gray-900">
                                                {dataset.title}
                                            </h3>
                                            <span className="ml-3 px-2 py-1 text-xs font-semibold bg-green-100 text-green-800 rounded">
                                                {dataset.status === 'ready' && '✓ Ready'}
                                            </span>
                                            {dataset.features && (
                                                <span className="ml-2 text-sm text-gray-500">
                                                    {dataset.features.toLocaleString()} features
                                                </span>
                                            )}
                                        </div>
                                        <p className="text-gray-600 mb-3">{dataset.description}</p>

                                        <div className="flex flex-wrap gap-4 text-sm text-gray-500 mb-3">
                                            <div className="flex items-center">
                                                <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                                                    <path fillRule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clipRule="evenodd" />
                                                </svg>
                                                {dataset.lastUpdated}
                                            </div>
                                            <div className="flex items-center">
                                                <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                                                    <path fillRule="evenodd" d="M4 4a2 2 0 012-2h8a2 2 0 012 2v12a1 1 0 110 2h-3a1 1 0 01-1-1v-2a1 1 0 00-1-1H9a1 1 0 00-1 1v2a1 1 0 01-1 1H4a1 1 0 110-2V4zm3 1h2v2H7V5zm2 4H7v2h2V9zm2-4h2v2h-2V5zm2 4h-2v2h2V9z" clipRule="evenodd" />
                                                </svg>
                                                {dataset.source}
                                            </div>
                                        </div>

                                        {/* Use Cases */}
                                        <div className="mb-3">
                                            <p className="text-sm font-semibold text-gray-700 mb-1">Use Cases:</p>
                                            <div className="flex flex-wrap gap-2">
                                                {dataset.useCases.map((useCase, idx) => (
                                                    <span
                                                        key={idx}
                                                        className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded"
                                                    >
                                                        {useCase}
                                                    </span>
                                                ))}
                                            </div>
                                        </div>
                                    </div>

                                    {/* Export & Dashboard Link */}
                                    <div className="flex flex-col gap-2 ml-4">
                                        {dataCache[dataset.id] ? (
                                            <ExportButton
                                                data={dataCache[dataset.id]}
                                                filename={`westchester_${dataset.id}`}
                                                label="Export"
                                                formats={dataset.formats}
                                                isGeoJSON={dataset.formats.includes('geojson')}
                                            />
                                        ) : (
                                            <button
                                                onClick={() => handlePreload(dataset.id)}
                                                onMouseEnter={() => handlePreload(dataset.id)}
                                                disabled={loading[dataset.id]}
                                                className="inline-flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:bg-gray-400"
                                            >
                                                {loading[dataset.id] ? (
                                                    <>
                                                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                                                        Loading...
                                                    </>
                                                ) : (
                                                    <>
                                                        <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                                        </svg>
                                                        Load & Export
                                                    </>
                                                )}
                                            </button>
                                        )}

                                        {dataset.dashboardLink && (
                                            <Link
                                                to={dataset.dashboardLink}
                                                className="inline-flex items-center justify-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
                                            >
                                                <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                                                    <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
                                                    <path fillRule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clipRule="evenodd" />
                                                </svg>
                                                View Dashboard
                                            </Link>
                                        )}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            ))}

            {/* Usage Guide */}
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-6 mt-8">
                <h3 className="text-lg font-semibold text-gray-900 mb-3">📚 How to Use This Data</h3>
                <div className="grid md:grid-cols-2 gap-4 text-sm text-gray-700">
                    <div>
                        <h4 className="font-semibold mb-2">CSV Format</h4>
                        <p>Best for spreadsheet analysis in Excel, Google Sheets, or statistical software. Includes all attributes in tabular format.</p>
                    </div>
                    <div>
                        <h4 className="font-semibold mb-2">JSON Format</h4>
                        <p>Ideal for developers and programmatic access. Preserves hierarchical data structures and nested attributes.</p>
                    </div>
                    <div>
                        <h4 className="font-semibold mb-2">GeoJSON Format</h4>
                        <p>Compatible with GIS software (QGIS, ArcGIS) and web mapping libraries. Includes spatial coordinates and geometries.</p>
                    </div>
                    <div>
                        <h4 className="font-semibold mb-2">Data Attribution</h4>
                        <p>All datasets include source attribution. Please cite the original data sources when using in reports or publications.</p>
                    </div>
                </div>
            </div>

            {/* Contact Info */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mt-6">
                <p className="text-sm text-blue-800">
                    <strong>Need help?</strong> For questions about data quality, coverage, or specific use cases,
                    please contact the Westchester County Planning Department or refer to individual dashboard pages
                    for detailed information.
                </p>
            </div>
        </div>
    );
}
