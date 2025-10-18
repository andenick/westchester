import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import EnhancedMapComponent from '../../components/map/EnhancedMapComponent';
import ExportButton from '../../components/ExportButton';
import apiService from '../../services/api';

interface SidewalkStats {
    tod_statistics: {
        total_roads: number;
        no_coverage: number;
        one_side: number;
        both_sides: number;
        any_coverage_pct: number;
    };
    non_tod_statistics: {
        total_roads: number;
        no_coverage: number;
        one_side: number;
        both_sides: number;
        any_coverage_pct: number;
    };
}

interface PlanningData {
    roadsNoCoverage: any | null;
    roadsOneSide: any | null;
    roadsBothSides: any | null;
    todAreaRoads: any | null;
    todBuffers: any | null;
}

const SidewalkPlanningDashboard: React.FC = () => {
    const [stats, setStats] = useState<SidewalkStats | null>(null);
    const [data, setData] = useState<PlanningData>({
        roadsNoCoverage: null,
        roadsOneSide: null,
        roadsBothSides: null,
        todAreaRoads: null,
        todBuffers: null
    });
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        loadPlanningData();
    }, []);

    const loadPlanningData = async () => {
        try {
            setLoading(true);

            // Load statistics and all coverage layers in parallel
            const [statsData, noCoverageData, oneSideData, bothSidesData, todRoadsData, todBuffersData] = await Promise.allSettled([
                apiService.getSidewalkStatistics(),
                apiService.getRoadsNoCoverage(),
                apiService.getRoadsOneSide(),
                apiService.getRoadsBothSides(),
                apiService.getTODAreaRoads(),
                apiService.getTODBuffers()
            ]);

            if (statsData.status === 'fulfilled') {
                setStats(statsData.value);
            }

            const newData: PlanningData = {
                roadsNoCoverage: null,
                roadsOneSide: null,
                roadsBothSides: null,
                todAreaRoads: null,
                todBuffers: null
            };

            if (noCoverageData.status === 'fulfilled') newData.roadsNoCoverage = noCoverageData.value;
            if (oneSideData.status === 'fulfilled') newData.roadsOneSide = oneSideData.value;
            if (bothSidesData.status === 'fulfilled') newData.roadsBothSides = bothSidesData.value;
            if (todRoadsData.status === 'fulfilled') newData.todAreaRoads = todRoadsData.value;
            if (todBuffersData.status === 'fulfilled') newData.todBuffers = todBuffersData.value;

            setData(newData);
            setError(null);
        } catch (err) {
            console.error('Error loading planning data:', err);
            setError('Failed to load sidewalk planning data');
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-amber-600 mx-auto mb-4"></div>
                    <p className="text-gray-600">Loading sidewalk planning data...</p>
                </div>
            </div>
        );
    }

    if (error || !stats) {
        return (
            <div className="container mx-auto px-4 py-8">
                <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
                    <p className="font-bold">Error</p>
                    <p>{error || 'Failed to load statistics'}</p>
                </div>
            </div>
        );
    }

    const todStats = stats.tod_statistics;
    const nonTodStats = stats.non_tod_statistics;

    // Calculate percentages for traffic light display
    const noCoveragePct = ((todStats.no_coverage / todStats.total_roads) * 100).toFixed(1);
    const oneSidePct = ((todStats.one_side / todStats.total_roads) * 100).toFixed(1);
    const bothSidesPct = ((todStats.both_sides / todStats.total_roads) * 100).toFixed(1);

    return (
        <div className="container mx-auto px-4 py-8">
            {/* Header */}
            <div className="mb-8">
                <div className="flex justify-between items-start mb-4">
                    <div className="flex-1">
                        <h1 className="text-4xl font-bold text-gray-900 mb-2">Sidewalk Planning Dashboard</h1>
                        <p className="text-gray-600">
                            Transit-Oriented Development (TOD) Sidewalk Coverage Analysis & Investment Prioritization
                        </p>
                        <p className="text-sm text-gray-500 mt-2">
                            Analysis Methodology: DVRPC Sidewalk-to-Road Ratio | TOD Definition: 0.5 miles from Metro-North stations
                        </p>
                    </div>

                    {/* Export Buttons */}
                    <div className="flex gap-3 flex-wrap justify-end">
                        {data.roadsNoCoverage && (
                            <ExportButton
                                data={data.roadsNoCoverage}
                                filename="tod_roads_no_coverage"
                                label="Export Priority Tier 1"
                                formats={['csv', 'geojson']}
                                isGeoJSON={true}
                            />
                        )}
                        {data.roadsOneSide && (
                            <ExportButton
                                data={data.roadsOneSide}
                                filename="tod_roads_one_side"
                                label="Export Priority Tier 2"
                                formats={['csv', 'geojson']}
                                isGeoJSON={true}
                            />
                        )}
                        {data.roadsBothSides && (
                            <ExportButton
                                data={data.roadsBothSides}
                                filename="tod_roads_both_sides"
                                label="Export Adequate Coverage"
                                formats={['csv', 'geojson']}
                                isGeoJSON={true}
                            />
                        )}
                    </div>
                </div>

                {/* Planning Context Banner */}
                <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mt-4">
                    <div className="flex items-start">
                        <svg className="w-6 h-6 text-amber-600 mr-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                        </svg>
                        <div>
                            <p className="text-sm font-semibold text-amber-900 mb-1">For City Planners:</p>
                            <p className="text-sm text-amber-800">
                                This dashboard provides a comprehensive assessment of sidewalk coverage near Metro-North stations.
                                Use the 3-tier investment framework below to prioritize capital improvements. Export data for GIS analysis,
                                grant applications, and stakeholder presentations.
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Traffic Light Assessment Display */}
            <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
                <h2 className="text-2xl font-bold mb-6 text-center">TOD Sidewalk Coverage Assessment</h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {/* No Coverage - Red */}
                    <div className="bg-red-50 border-2 border-red-300 rounded-lg p-6 text-center">
                        <div className="w-16 h-16 bg-red-500 rounded-full flex items-center justify-center mx-auto mb-4 shadow-lg">
                            <span className="text-3xl text-white font-bold">!</span>
                        </div>
                        <h3 className="text-lg font-bold text-red-900 mb-2">No Coverage</h3>
                        <p className="text-4xl font-bold text-red-600 mb-2">{noCoveragePct}%</p>
                        <p className="text-sm text-red-700 font-semibold">{todStats.no_coverage.toLocaleString()} roads</p>
                        <p className="text-xs text-red-600 mt-2">HIGH PRIORITY - Investment Focus</p>
                    </div>

                    {/* One-Side Coverage - Orange/Yellow */}
                    <div className="bg-orange-50 border-2 border-orange-300 rounded-lg p-6 text-center">
                        <div className="w-16 h-16 bg-orange-500 rounded-full flex items-center justify-center mx-auto mb-4 shadow-lg">
                            <span className="text-3xl text-white font-bold">△</span>
                        </div>
                        <h3 className="text-lg font-bold text-orange-900 mb-2">One-Side Coverage</h3>
                        <p className="text-4xl font-bold text-orange-600 mb-2">{oneSidePct}%</p>
                        <p className="text-sm text-orange-700 font-semibold">{todStats.one_side.toLocaleString()} roads</p>
                        <p className="text-xs text-orange-600 mt-2">MEDIUM PRIORITY - Quick Wins</p>
                    </div>

                    {/* Both-Sides Coverage - Green */}
                    <div className="bg-green-50 border-2 border-green-300 rounded-lg p-6 text-center">
                        <div className="w-16 h-16 bg-green-500 rounded-full flex items-center justify-center mx-auto mb-4 shadow-lg">
                            <span className="text-3xl text-white font-bold">✓</span>
                        </div>
                        <h3 className="text-lg font-bold text-green-900 mb-2">Both-Sides Coverage</h3>
                        <p className="text-4xl font-bold text-green-600 mb-2">{bothSidesPct}%</p>
                        <p className="text-sm text-green-700 font-semibold">{todStats.both_sides.toLocaleString()} roads</p>
                        <p className="text-xs text-green-600 mt-2">ADEQUATE - Maintain</p>
                    </div>
                </div>
            </div>

            {/* Key Metrics Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-8">
                <div className="bg-white rounded-lg shadow-lg p-6 text-center">
                    <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                        <span className="text-2xl">📊</span>
                    </div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">TOD Coverage</h3>
                    <p className="text-3xl font-bold text-blue-600">{todStats.any_coverage_pct.toFixed(1)}%</p>
                    <p className="text-sm text-gray-500">Any sidewalk coverage</p>
                </div>

                <div className="bg-white rounded-lg shadow-lg p-6 text-center">
                    <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                        <span className="text-2xl">🎯</span>
                    </div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">Priority Roads</h3>
                    <p className="text-3xl font-bold text-red-600">{todStats.no_coverage.toLocaleString()}</p>
                    <p className="text-sm text-gray-500">Tier 1 investment focus</p>
                </div>

                <div className="bg-white rounded-lg shadow-lg p-6 text-center">
                    <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                        <span className="text-2xl">⚡</span>
                    </div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">Quick Wins</h3>
                    <p className="text-3xl font-bold text-orange-600">{todStats.one_side.toLocaleString()}</p>
                    <p className="text-sm text-gray-500">Tier 2 completions</p>
                </div>

                <div className="bg-white rounded-lg shadow-lg p-6 text-center">
                    <div className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                        <span className="text-2xl">🗺️</span>
                    </div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">Total Analyzed</h3>
                    <p className="text-3xl font-bold text-gray-900">{todStats.total_roads.toLocaleString()}</p>
                    <p className="text-sm text-gray-500">TOD area roads</p>
                </div>
            </div>

            {/* Interactive Map */}
            <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
                <h2 className="text-2xl font-bold mb-4">Interactive Sidewalk Coverage Map</h2>
                <p className="text-gray-600 mb-4">
                    Toggle layers to view TOD buffer zones (purple), priority roads (red), completion opportunities (orange),
                    and adequate coverage (green). Click on roads for detailed information.
                </p>
                <EnhancedMapComponent
                    height="700px"
                    defaultLayers={['todBuffers', 'roadsNoCoverage', 'roadsOneSide', 'roadsBothSides', 'stations']}
                />
            </div>

            {/* Three-Tier Investment Prioritization */}
            <div className="mb-8">
                <h2 className="text-3xl font-bold mb-6 text-center">Three-Tier Investment Prioritization Framework</h2>
                <div className="grid md:grid-cols-3 gap-6">
                    {/* Tier 1 */}
                    <div className="bg-white rounded-lg shadow-lg p-6 border-l-4 border-red-500">
                        <div className="flex items-center mb-4">
                            <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center mr-3">
                                <span className="text-2xl font-bold text-red-600">1</span>
                            </div>
                            <h3 className="text-xl font-bold text-gray-900">Transit Connectivity</h3>
                        </div>
                        <div className="space-y-3">
                            <div>
                                <p className="text-sm font-semibold text-gray-700">Target</p>
                                <p className="text-gray-900">{todStats.no_coverage.toLocaleString()} TOD roads with NO coverage</p>
                            </div>
                            <div>
                                <p className="text-sm font-semibold text-gray-700">Priority</p>
                                <p className="text-red-600 font-bold">HIGH - Essential for walkable TOD</p>
                            </div>
                            <div>
                                <p className="text-sm font-semibold text-gray-700">Timeline</p>
                                <p className="text-gray-900">5-7 years</p>
                            </div>
                            <div>
                                <p className="text-sm font-semibold text-gray-700">Impact</p>
                                <p className="text-gray-900">Maximize pedestrian access to Metro-North stations</p>
                            </div>
                        </div>
                    </div>

                    {/* Tier 2 */}
                    <div className="bg-white rounded-lg shadow-lg p-6 border-l-4 border-orange-500">
                        <div className="flex items-center mb-4">
                            <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center mr-3">
                                <span className="text-2xl font-bold text-orange-600">2</span>
                            </div>
                            <h3 className="text-xl font-bold text-gray-900">Completion Opportunities</h3>
                        </div>
                        <div className="space-y-3">
                            <div>
                                <p className="text-sm font-semibold text-gray-700">Target</p>
                                <p className="text-gray-900">{todStats.one_side.toLocaleString()} TOD roads with ONE-SIDE coverage</p>
                            </div>
                            <div>
                                <p className="text-sm font-semibold text-gray-700">Priority</p>
                                <p className="text-orange-600 font-bold">MEDIUM - Cost-effective</p>
                            </div>
                            <div>
                                <p className="text-sm font-semibold text-gray-700">Timeline</p>
                                <p className="text-gray-900">3-5 years</p>
                            </div>
                            <div>
                                <p className="text-sm font-semibold text-gray-700">Impact</p>
                                <p className="text-gray-900">Quick wins, improved pedestrian safety</p>
                            </div>
                        </div>
                    </div>

                    {/* Tier 3 */}
                    <div className="bg-white rounded-lg shadow-lg p-6 border-l-4 border-purple-500">
                        <div className="flex items-center mb-4">
                            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mr-3">
                                <span className="text-2xl font-bold text-purple-600">3</span>
                            </div>
                            <h3 className="text-xl font-bold text-gray-900">Equity & Expansion</h3>
                        </div>
                        <div className="space-y-3">
                            <div>
                                <p className="text-sm font-semibold text-gray-700">Target</p>
                                <p className="text-gray-900">{nonTodStats.no_coverage.toLocaleString()} non-TOD roads lacking coverage</p>
                            </div>
                            <div>
                                <p className="text-sm font-semibold text-gray-700">Priority</p>
                                <p className="text-purple-600 font-bold">LONG-TERM - Environmental justice</p>
                            </div>
                            <div>
                                <p className="text-sm font-semibold text-gray-700">Timeline</p>
                                <p className="text-gray-900">10-15 years</p>
                            </div>
                            <div>
                                <p className="text-sm font-semibold text-gray-700">Impact</p>
                                <p className="text-gray-900">Address {((nonTodStats.no_coverage / nonTodStats.total_roads) * 100).toFixed(1)}% no-coverage rate</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Comparative Benchmarks */}
            <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
                <h2 className="text-2xl font-bold mb-6">Comparative Benchmarks</h2>
                <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                            <tr>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Metric</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Current TOD</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Best Practice</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Gap to Target</th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            <tr>
                                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">Any Coverage</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{todStats.any_coverage_pct.toFixed(1)}%</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">75-85%</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-red-600 font-semibold">
                                    -{(75 - todStats.any_coverage_pct).toFixed(1)} to -{(85 - todStats.any_coverage_pct).toFixed(1)} percentage points
                                </td>
                            </tr>
                            <tr className="bg-gray-50">
                                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">Non-TOD Coverage</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{nonTodStats.any_coverage_pct.toFixed(1)}%</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">50-65%</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-red-600 font-semibold">Significant equity gap</td>
                            </tr>
                            <tr>
                                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">County-Wide Average</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                    {(((todStats.no_coverage + todStats.one_side + todStats.both_sides + nonTodStats.no_coverage + nonTodStats.one_side + nonTodStats.both_sides - (todStats.no_coverage + nonTodStats.no_coverage)) / (todStats.total_roads + nonTodStats.total_roads)) * 100).toFixed(1)}%
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">60-70%</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">Below target</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                <div className="mt-4 text-sm text-gray-600">
                    <p className="font-semibold mb-2">Key Planning Questions:</p>
                    <ol className="list-decimal ml-6 space-y-1">
                        <li>Which TOD roads should be addressed first based on ridership and connectivity?</li>
                        <li>What is the ROI of Tier 2 completions vs Tier 1 new construction?</li>
                        <li>What timeline and phasing is realistic given budget constraints?</li>
                        <li>Which projects qualify for federal/state TOD, ADA, or Complete Streets funding?</li>
                        <li>How do we compare to peer counties with similar transit infrastructure?</li>
                    </ol>
                </div>
            </div>

            {/* Municipality Interactive Maps */}
            <div className="bg-gradient-to-r from-amber-50 to-amber-100 rounded-lg shadow-lg p-6 mb-8">
                <h2 className="text-2xl font-bold mb-4 text-gray-900">Municipality Interactive Maps</h2>
                <p className="text-gray-700 mb-6">
                    Explore detailed interactive maps for major municipalities with Metro-North stations. These maps show TOD zones (0.5-mile buffers), sidewalk coverage by priority tier, and specific road segments.
                </p>
                <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
                    {/* White Plains */}
                    <a
                        href="/MAPPING_DELIVERABLES/Interactive_Maps/white_plains_sidewalk_tod_analysis.html"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="group bg-white rounded-lg p-4 shadow hover:shadow-xl transition-all duration-300 border-l-4 border-blue-500 hover:border-blue-600"
                    >
                        <div className="flex items-center mb-3">
                            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center mr-3 group-hover:bg-blue-200 transition-colors">
                                <span className="text-xl">🗺️</span>
                            </div>
                            <h3 className="text-lg font-bold text-gray-900 group-hover:text-blue-600 transition-colors">
                                White Plains
                            </h3>
                        </div>
                        <p className="text-sm text-gray-600 mb-2">2 Metro-North stations</p>
                        <div className="space-y-1 text-xs">
                            <div className="flex justify-between">
                                <span className="text-red-600">No Coverage:</span>
                                <span className="font-semibold">24 roads</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-orange-600">One-Side:</span>
                                <span className="font-semibold">24 roads</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-green-600">Both-Sides:</span>
                                <span className="font-semibold">9 roads</span>
                            </div>
                        </div>
                        <div className="mt-3 text-xs text-blue-600 font-semibold group-hover:underline">
                            View Interactive Map →
                        </div>
                    </a>

                    {/* Yonkers */}
                    <a
                        href="/MAPPING_DELIVERABLES/Interactive_Maps/yonkers_sidewalk_tod_analysis.html"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="group bg-white rounded-lg p-4 shadow hover:shadow-xl transition-all duration-300 border-l-4 border-green-500 hover:border-green-600"
                    >
                        <div className="flex items-center mb-3">
                            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center mr-3 group-hover:bg-green-200 transition-colors">
                                <span className="text-xl">🗺️</span>
                            </div>
                            <h3 className="text-lg font-bold text-gray-900 group-hover:text-green-600 transition-colors">
                                Yonkers
                            </h3>
                        </div>
                        <p className="text-sm text-gray-600 mb-2">4 Metro-North stations</p>
                        <div className="space-y-1 text-xs">
                            <div className="flex justify-between">
                                <span className="text-red-600">No Coverage:</span>
                                <span className="font-semibold">8 roads</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-orange-600">One-Side:</span>
                                <span className="font-semibold">15 roads</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-green-600">Both-Sides:</span>
                                <span className="font-semibold">12 roads</span>
                            </div>
                        </div>
                        <div className="mt-3 text-xs text-green-600 font-semibold group-hover:underline">
                            View Interactive Map →
                        </div>
                    </a>

                    {/* New Rochelle */}
                    <a
                        href="/MAPPING_DELIVERABLES/Interactive_Maps/new_rochelle_sidewalk_tod_analysis.html"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="group bg-white rounded-lg p-4 shadow hover:shadow-xl transition-all duration-300 border-l-4 border-purple-500 hover:border-purple-600"
                    >
                        <div className="flex items-center mb-3">
                            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center mr-3 group-hover:bg-purple-200 transition-colors">
                                <span className="text-xl">🗺️</span>
                            </div>
                            <h3 className="text-lg font-bold text-gray-900 group-hover:text-purple-600 transition-colors">
                                New Rochelle
                            </h3>
                        </div>
                        <p className="text-sm text-gray-600 mb-2">1 Metro-North station</p>
                        <div className="space-y-1 text-xs">
                            <div className="flex justify-between">
                                <span className="text-red-600">No Coverage:</span>
                                <span className="font-semibold">11 roads</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-orange-600">One-Side:</span>
                                <span className="font-semibold">25 roads</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-green-600">Both-Sides:</span>
                                <span className="font-semibold">22 roads</span>
                            </div>
                        </div>
                        <div className="mt-3 text-xs text-purple-600 font-semibold group-hover:underline">
                            View Interactive Map →
                        </div>
                    </a>

                    {/* Mount Vernon */}
                    <a
                        href="/MAPPING_DELIVERABLES/Interactive_Maps/mount_vernon_sidewalk_tod_analysis.html"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="group bg-white rounded-lg p-4 shadow hover:shadow-xl transition-all duration-300 border-l-4 border-orange-500 hover:border-orange-600"
                    >
                        <div className="flex items-center mb-3">
                            <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center mr-3 group-hover:bg-orange-200 transition-colors">
                                <span className="text-xl">🗺️</span>
                            </div>
                            <h3 className="text-lg font-bold text-gray-900 group-hover:text-orange-600 transition-colors">
                                Mount Vernon
                            </h3>
                        </div>
                        <p className="text-sm text-gray-600 mb-2">3 Metro-North stations</p>
                        <div className="space-y-1 text-xs">
                            <div className="flex justify-between">
                                <span className="text-red-600">No Coverage:</span>
                                <span className="font-semibold">56 roads</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-orange-600">One-Side:</span>
                                <span className="font-semibold">25 roads</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-green-600">Both-Sides:</span>
                                <span className="font-semibold">13 roads</span>
                            </div>
                        </div>
                        <div className="mt-3 text-xs text-orange-600 font-semibold group-hover:underline">
                            View Interactive Map →
                        </div>
                    </a>
                </div>

                {/* County-Wide Overview */}
                <div className="mt-6">
                    <a
                        href="/MAPPING_DELIVERABLES/Interactive_Maps/county_wide_tod_overview.html"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="group bg-white rounded-lg p-6 shadow-lg hover:shadow-xl transition-all duration-300 border-l-4 border-indigo-500 hover:border-indigo-600 block"
                    >
                        <div className="flex items-center justify-between">
                            <div className="flex items-center">
                                <div className="w-12 h-12 bg-indigo-100 rounded-lg flex items-center justify-center mr-4 group-hover:bg-indigo-200 transition-colors">
                                    <span className="text-2xl">🗺️</span>
                                </div>
                                <div>
                                    <h3 className="text-xl font-bold text-gray-900 group-hover:text-indigo-600 transition-colors mb-1">
                                        County-Wide TOD Overview Map
                                    </h3>
                                    <p className="text-sm text-gray-600">
                                        All 56 Metro-North stations with sampled TOD coverage data
                                    </p>
                                </div>
                            </div>
                            <div className="text-indigo-600 font-semibold group-hover:underline">
                                View Map →
                            </div>
                        </div>
                    </a>
                </div>

                <div className="mt-4 text-sm text-gray-600 bg-white rounded-lg p-4">
                    <p className="font-semibold mb-2">Map Features:</p>
                    <ul className="list-disc ml-6 space-y-1">
                        <li>Interactive panning and zooming with OpenStreetMap base layer</li>
                        <li>Color-coded roads by coverage priority (RED = Tier 1, ORANGE = Tier 2, GREEN = Adequate)</li>
                        <li>0.5-mile TOD buffer zones shown as dashed circles around stations</li>
                        <li>Click on roads to view road type and other attributes</li>
                        <li>Toggle layers on/off for custom views</li>
                    </ul>
                </div>
            </div>

            {/* Download Resources */}
            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg shadow-lg p-6">
                <h2 className="text-2xl font-bold mb-4 text-gray-900">Download Planning Resources</h2>
                <p className="text-gray-700 mb-6">
                    Access comprehensive Excel spreadsheets and PDF reports for offline analysis, grant applications, and stakeholder presentations.
                </p>
                <div className="grid md:grid-cols-2 gap-6">
                    <div className="bg-white rounded-lg p-4 shadow">
                        <h3 className="font-bold text-lg mb-2 text-gray-900">Excel Spreadsheets</h3>
                        <ul className="space-y-2 text-sm text-gray-700">
                            <li className="flex items-center">
                                <span className="mr-2">📊</span>
                                <span>1_EXECUTIVE_SUMMARY.xlsx - Complete coverage breakdown</span>
                            </li>
                            <li className="flex items-center">
                                <span className="mr-2">📊</span>
                                <span>2_TOD_COMPARISON.xlsx - TOD vs Non-TOD analysis</span>
                            </li>
                            <li className="flex items-center">
                                <span className="mr-2">📊</span>
                                <span>3_ROAD_TYPE_ANALYSIS.xlsx - Coverage by road classification</span>
                            </li>
                            <li className="flex items-center">
                                <span className="mr-2">📊</span>
                                <span>4_AREA_ANALYSIS.xlsx - Coverage by area (acres)</span>
                            </li>
                        </ul>
                        <p className="mt-3 text-xs text-gray-500">
                            Location: D:\Arcanum\Projects\Westchester\Output\DELIVERABLES_FOR_TAYLOR\Excel\
                        </p>
                    </div>

                    <div className="bg-white rounded-lg p-4 shadow">
                        <h3 className="font-bold text-lg mb-2 text-gray-900">PDF Reports</h3>
                        <ul className="space-y-2 text-sm text-gray-700">
                            <li className="flex items-center">
                                <span className="mr-2">📄</span>
                                <span>START_HERE.pdf - Planning framework & 3-tier prioritization</span>
                            </li>
                            <li className="flex items-center">
                                <span className="mr-2">📄</span>
                                <span>Executive_Summary.pdf - 5-page overview for presentations</span>
                            </li>
                            <li className="flex items-center">
                                <span className="mr-2">📄</span>
                                <span>Technical_Analysis.pdf - 12-page methodology report</span>
                            </li>
                        </ul>
                        <p className="mt-3 text-xs text-gray-500">
                            Location: D:\Arcanum\Projects\Westchester\Output\DELIVERABLES_FOR_TAYLOR\Reports\
                        </p>
                    </div>
                </div>

                <div className="mt-6 flex justify-center">
                    <Link
                        to="/data-catalog"
                        className="inline-flex items-center px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors shadow-md"
                    >
                        <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
                        </svg>
                        Browse All Datasets
                    </Link>
                </div>
            </div>
        </div>
    );
};

export default SidewalkPlanningDashboard;
