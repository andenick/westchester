import React from 'react';
import { Link } from 'react-router-dom';
import EnhancedMapComponent from '../../components/map/EnhancedMapComponent';

const LandingPage: React.FC = () => {
    return (
        <div className="min-h-screen bg-gray-50">
            <div className="container mx-auto px-4 py-8">
                {/* Header */}
                <div className="text-center mb-12">
                    <h1 className="text-5xl font-bold text-gray-900 mb-4">
                        Westchester County Data Platform
                    </h1>
                    <p className="text-xl text-gray-600 max-w-4xl mx-auto">
                        Interactive Data Visualization & Municipal Planning Tools
                    </p>
                </div>

                {/* Sidewalk Planning Tools Banner */}
                <div className="bg-gradient-to-r from-amber-50 to-amber-100 border-2 border-amber-300 rounded-xl shadow-lg p-8 mb-12 max-w-6xl mx-auto">
                    <div className="text-center mb-6">
                        <h2 className="text-3xl font-bold text-gray-900 mb-2">🚶 Sidewalk Planning Tools</h2>
                        <p className="text-lg text-gray-700">
                            Transit-Oriented Development (TOD) Sidewalk Coverage Analysis
                        </p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                        <div className="bg-white rounded-lg p-6 shadow-md text-center border-l-4 border-red-500">
                            <div className="text-3xl font-bold text-red-600 mb-2">502</div>
                            <div className="text-sm font-semibold text-gray-700 mb-1">Priority Roads</div>
                            <div className="text-xs text-gray-600">No sidewalk coverage</div>
                            <div className="text-xs text-red-600 font-semibold mt-2">TIER 1 - HIGH</div>
                        </div>

                        <div className="bg-white rounded-lg p-6 shadow-md text-center border-l-4 border-orange-500">
                            <div className="text-3xl font-bold text-orange-600 mb-2">352</div>
                            <div className="text-sm font-semibold text-gray-700 mb-1">Quick Wins</div>
                            <div className="text-xs text-gray-600">One-side coverage</div>
                            <div className="text-xs text-orange-600 font-semibold mt-2">TIER 2 - MEDIUM</div>
                        </div>

                        <div className="bg-white rounded-lg p-6 shadow-md text-center border-l-4 border-blue-500">
                            <div className="text-3xl font-bold text-blue-600 mb-2">1,117</div>
                            <div className="text-sm font-semibold text-gray-700 mb-1">Total TOD Roads</div>
                            <div className="text-xs text-gray-600">0.5 miles from stations</div>
                            <div className="text-xs text-blue-600 font-semibold mt-2">54.9% COVERAGE</div>
                        </div>
                    </div>

                    <div className="text-center">
                        <Link
                            to="/sidewalk-planning"
                            className="inline-flex items-center px-8 py-4 bg-amber-500 hover:bg-amber-600 text-white font-bold rounded-lg shadow-lg transition-all duration-300 text-lg"
                        >
                            Explore Sidewalk Planning Dashboard →
                        </Link>
                    </div>
                </div>

                {/* Overview Map - Centered and Prominent */}
                <div className="bg-white rounded-xl shadow-xl p-8 mb-12 max-w-6xl mx-auto">
                    <h2 className="text-3xl font-bold mb-6 text-center">🗺️ Interactive County Map</h2>
                    <EnhancedMapComponent
                        height="500px"
                        defaultLayers={['stations', 'parks', 'trails']}
                    />
                </div>

                {/* Dashboard Navigation Grid */}
                <div className="max-w-7xl mx-auto">
                    <h2 className="text-3xl font-bold text-center mb-8">📊 Dashboards & Tools</h2>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 mb-8">
                        {/* Demographics Dashboard */}
                        <Link
                            to="/demographics"
                            className="group bg-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 p-6 border-l-4 border-blue-500 hover:border-blue-600"
                        >
                            <div className="flex items-center mb-4">
                                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mr-4 group-hover:bg-blue-200 transition-colors">
                                    <span className="text-2xl">📈</span>
                                </div>
                                <div>
                                    <h3 className="text-xl font-bold text-gray-900 group-hover:text-blue-600 transition-colors">
                                        Demographics
                                    </h3>
                                    <p className="text-sm text-gray-500">Population & demographics</p>
                                </div>
                            </div>
                            <p className="text-gray-600 text-sm">
                                Population trends, age distribution, race/ethnicity, and demographic analysis
                            </p>
                        </Link>

                        {/* Transit Dashboard */}
                        <Link
                            to="/transit"
                            className="group bg-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 p-6 border-l-4 border-green-500 hover:border-green-600"
                        >
                            <div className="flex items-center mb-4">
                                <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mr-4 group-hover:bg-green-200 transition-colors">
                                    <span className="text-2xl">🚊</span>
                                </div>
                                <div>
                                    <h3 className="text-xl font-bold text-gray-900 group-hover:text-green-600 transition-colors">
                                        Transit & Transportation
                                    </h3>
                                    <p className="text-sm text-gray-500">Metro-North & Bee-Line</p>
                                </div>
                            </div>
                            <p className="text-gray-600 text-sm">
                                Transit stations, routes, ridership, and transportation infrastructure
                            </p>
                        </Link>

                        {/* Property Tax Dashboard */}
                        <Link
                            to="/property-tax"
                            className="group bg-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 p-6 border-l-4 border-purple-500 hover:border-purple-600"
                        >
                            <div className="flex items-center mb-4">
                                <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mr-4 group-hover:bg-purple-200 transition-colors">
                                    <span className="text-2xl">🏠</span>
                                </div>
                                <div>
                                    <h3 className="text-xl font-bold text-gray-900 group-hover:text-purple-600 transition-colors">
                                        Property Tax Analysis
                                    </h3>
                                    <p className="text-sm text-gray-500">Tax rates & assessments</p>
                                </div>
                            </div>
                            <p className="text-gray-600 text-sm">
                                Property tax rates, assessments, and tax burden analysis by municipality
                            </p>
                        </Link>

                        {/* Budget Dashboard */}
                        <Link
                            to="/budget"
                            className="group bg-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 p-6 border-l-4 border-orange-500 hover:border-orange-600"
                        >
                            <div className="flex items-center mb-4">
                                <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center mr-4 group-hover:bg-orange-200 transition-colors">
                                    <span className="text-2xl">💰</span>
                                </div>
                                <div>
                                    <h3 className="text-xl font-bold text-gray-900 group-hover:text-orange-600 transition-colors">
                                        County Budget
                                    </h3>
                                    <p className="text-sm text-gray-500">Financial planning</p>
                                </div>
                            </div>
                            <p className="text-gray-600 text-sm">
                                County budget analysis, expenditures, and financial planning tools
                            </p>
                        </Link>

                        {/* Municipal Services Dashboard */}
                        <Link
                            to="/municipal-services"
                            className="group bg-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 p-6 border-l-4 border-indigo-500 hover:border-indigo-600"
                        >
                            <div className="flex items-center mb-4">
                                <div className="w-12 h-12 bg-indigo-100 rounded-lg flex items-center justify-center mr-4 group-hover:bg-indigo-200 transition-colors">
                                    <span className="text-2xl">🏛️</span>
                                </div>
                                <div>
                                    <h3 className="text-xl font-bold text-gray-900 group-hover:text-indigo-600 transition-colors">
                                        Municipal Services
                                    </h3>
                                    <p className="text-sm text-gray-500">Services & infrastructure</p>
                                </div>
                            </div>
                            <p className="text-gray-600 text-sm">
                                Municipal services, infrastructure, and service delivery analysis
                            </p>
                        </Link>

                        {/* Municipality Comparison Dashboard */}
                        <Link
                            to="/municipality-comparison"
                            className="group bg-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 p-6 border-l-4 border-pink-500 hover:border-pink-600"
                        >
                            <div className="flex items-center mb-4">
                                <div className="w-12 h-12 bg-pink-100 rounded-lg flex items-center justify-center mr-4 group-hover:bg-pink-200 transition-colors">
                                    <span className="text-2xl">🏘️</span>
                                </div>
                                <div>
                                    <h3 className="text-xl font-bold text-gray-900 group-hover:text-pink-600 transition-colors">
                                        Municipality Comparison
                                    </h3>
                                    <p className="text-sm text-gray-500">Compare municipalities</p>
                                </div>
                            </div>
                            <p className="text-gray-600 text-sm">
                                Compare municipalities across demographics, taxes, services, and metrics
                            </p>
                        </Link>

                        {/* Historical Trends Dashboard */}
                        <Link
                            to="/historical-trends"
                            className="group bg-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 p-6 border-l-4 border-teal-500 hover:border-teal-600"
                        >
                            <div className="flex items-center mb-4">
                                <div className="w-12 h-12 bg-teal-100 rounded-lg flex items-center justify-center mr-4 group-hover:bg-teal-200 transition-colors">
                                    <span className="text-2xl">📈</span>
                                </div>
                                <div>
                                    <h3 className="text-xl font-bold text-gray-900 group-hover:text-teal-600 transition-colors">
                                        Historical Trends
                                    </h3>
                                    <p className="text-sm text-gray-500">35-year time series (1990-2024)</p>
                                </div>
                            </div>
                            <p className="text-gray-600 text-sm">
                                Historical trends in population, income, housing, and demographics
                            </p>
                        </Link>

                        {/* Infrastructure Map Dashboard */}
                        <Link
                            to="/infrastructure"
                            className="group bg-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 p-6 border-l-4 border-red-500 hover:border-red-600"
                        >
                            <div className="flex items-center mb-4">
                                <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center mr-4 group-hover:bg-red-200 transition-colors">
                                    <span className="text-2xl">📍</span>
                                </div>
                                <div>
                                    <h3 className="text-xl font-bold text-gray-900 group-hover:text-red-600 transition-colors">
                                        Infrastructure Map
                                    </h3>
                                    <p className="text-sm text-gray-500">Sidewalks, bike lanes, amenities</p>
                                </div>
                            </div>
                            <p className="text-gray-600 text-sm">
                                Infrastructure mapping including sidewalks, bike lanes, bus stops, and street lights
                            </p>
                        </Link>
                    </div>
                </div>

                {/* Footer Links */}
                <div className="max-w-4xl mx-auto text-center">
                    <div className="flex justify-center space-x-8 text-sm">
                        <a href="/data-sources" className="text-gray-600 hover:text-gray-900 transition-colors">
                            📄 Data Sources
                        </a>
                        <a href="/user-guide" className="text-gray-600 hover:text-gray-900 transition-colors">
                            📖 User Guide
                        </a>
                        <a href="/about" className="text-gray-600 hover:text-gray-900 transition-colors">
                            ℹ️ About
                        </a>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default LandingPage;
