/**
 * Header Component
 * 
 * Main navigation header for Westchester County Data Platform
 */

import { Link } from 'react-router-dom';
import { useState } from 'react';

export default function Header() {
    const [showDashboardMenu, setShowDashboardMenu] = useState(false);

    return (
        <header className="bg-westchester-green-700 text-white shadow-lg">
            <div className="container mx-auto px-4">
                <div className="flex items-center justify-between h-16">
                    {/* Logo and Title */}
                    <Link to="/" className="flex items-center space-x-3 hover:opacity-80 transition-opacity">
                        <div className="text-2xl font-bold">
                            🏛️
                        </div>
                        <div>
                            <h1 className="text-xl font-bold">Westchester County</h1>
                            <p className="text-xs text-westchester-green-100">Data Platform</p>
                        </div>
                    </Link>

                    {/* Navigation */}
                    <nav className="hidden md:flex space-x-6 items-center">
                        <Link
                            to="/"
                            className="hover:text-westchester-green-200 transition-colors font-medium"
                        >
                            Home
                        </Link>

                        <Link
                            to="/data-catalog"
                            className="hover:text-westchester-green-200 transition-colors font-medium flex items-center gap-1"
                        >
                            📦 Data Catalog
                        </Link>

                        {/* Dashboards Dropdown */}
                        <div 
                            className="relative"
                            onMouseEnter={() => setShowDashboardMenu(true)}
                            onMouseLeave={() => setShowDashboardMenu(false)}
                        >
                            <button className="hover:text-westchester-green-200 transition-colors font-medium flex items-center gap-1">
                                Dashboards
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                                </svg>
                            </button>
                            
                            {showDashboardMenu && (
                                <div className="absolute top-full left-0 mt-0 w-64 bg-white text-gray-800 rounded-lg shadow-xl py-2 z-50">
                                    <Link to="/overview" className="block px-4 py-2 hover:bg-gray-100 transition-colors">
                                        📊 Overview
                                    </Link>
                                    <Link to="/demographics" className="block px-4 py-2 hover:bg-gray-100 transition-colors">
                                        👥 Demographics
                                    </Link>
                                    <Link to="/transit" className="block px-4 py-2 hover:bg-gray-100 transition-colors">
                                        🚂 Transit Access
                                    </Link>
                                    <Link to="/property-tax" className="block px-4 py-2 hover:bg-gray-100 transition-colors">
                                        🏘️ Property Tax
                                    </Link>
                                    <Link to="/budget" className="block px-4 py-2 hover:bg-gray-100 transition-colors">
                                        💰 County Budget
                                    </Link>
                                    <Link to="/municipal-services" className="block px-4 py-2 hover:bg-gray-100 transition-colors">
                                        🚒 Municipal Services
                                    </Link>
                                    <Link to="/municipality-comparison" className="block px-4 py-2 hover:bg-gray-100 transition-colors">
                                        ⚖️ Municipality Comparison
                                    </Link>
                                    <Link to="/infrastructure" className="block px-4 py-2 hover:bg-gray-100 transition-colors">
                                        🏗️ Infrastructure
                                    </Link>
                                    <Link to="/historical-trends" className="block px-4 py-2 hover:bg-gray-100 transition-colors">
                                        📈 Historical Trends
                                    </Link>
                                    <Link to="/regional-comparison" className="block px-4 py-2 hover:bg-gray-100 transition-colors">
                                        🗺️ Regional Comparison
                                    </Link>
                                </div>
                            )}
                        </div>
                    </nav>

                    {/* Mobile menu button (TODO: implement mobile menu) */}
                    <button className="md:hidden p-2 hover:bg-westchester-green-600 rounded">
                        <svg
                            className="w-6 h-6"
                            fill="none"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth="2"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                        >
                            <path d="M4 6h16M4 12h16M4 18h16"></path>
                        </svg>
                    </button>
                </div>
            </div>
        </header>
    );
}

