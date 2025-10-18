/**
 * Home Page
 * 
 * Landing page for Westchester County Data Platform
 */

import { Link } from 'react-router-dom';

export default function HomePage() {
    return (
        <div className="min-h-screen bg-gradient-to-br from-westchester-green-50 to-white">
            {/* Hero Section */}
            <section className="container mx-auto px-4 py-16">
                <div className="text-center max-w-4xl mx-auto">
                    <h1 className="text-5xl font-bold text-gray-900 mb-6">
                        Westchester County Data Platform
                    </h1>
                    <p className="text-xl text-gray-600 mb-8">
                        Comprehensive government data analysis, interactive mapping, and visualization tools
                        for Westchester County, New York
                    </p>
                    <div className="flex gap-4 justify-center">
                        <Link
                            to="/dashboards/overview"
                            className="bg-westchester-green-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-westchester-green-700 transition-colors"
                        >
                            View Dashboards
                        </Link>
                        <Link
                            to="/map"
                            className="bg-white text-westchester-green-600 px-8 py-3 rounded-lg font-semibold border-2 border-westchester-green-600 hover:bg-westchester-green-50 transition-colors"
                        >
                            Explore Map
                        </Link>
                    </div>
                </div>
            </section>

            {/* Features Grid */}
            <section className="container mx-auto px-4 py-16">
                <h2 className="text-3xl font-bold text-center mb-12">Key Features</h2>
                <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
                    <FeatureCard
                        icon="🏛️"
                        title="Government Data"
                        description="Property tax, county budget, and municipal services data"
                    />
                    <FeatureCard
                        icon="🚉"
                        title="Transit Analysis"
                        description="Metro-North stations, accessibility, and coverage analysis"
                    />
                    <FeatureCard
                        icon="📊"
                        title="Demographics"
                        description="Population, income, housing, and employment statistics"
                    />
                    <FeatureCard
                        icon="🗺️"
                        title="Interactive Maps"
                        description="Multi-layer geographic visualization with click-to-inspect"
                    />
                </div>
            </section>

            {/* Data Sources */}
            <section className="container mx-auto px-4 py-16">
                <h2 className="text-3xl font-bold text-center mb-12">Data Sources</h2>
                <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-5xl mx-auto">
                    <DataSourceCard
                        title="Metro-North Railroad"
                        description="GTFS schedule and station data"
                    />
                    <DataSourceCard
                        title="U.S. Census Bureau"
                        description="ACS demographic data"
                    />
                    <DataSourceCard
                        title="NY State Open Data"
                        description="Government records and statistics"
                    />
                    <DataSourceCard
                        title="Westchester County GIS"
                        description="Geographic boundaries and mapping"
                    />
                </div>
            </section>

            {/* Statistics */}
            <section className="bg-westchester-green-700 text-white py-16">
                <div className="container mx-auto px-4">
                    <div className="grid md:grid-cols-4 gap-8 text-center">
                        <StatCard number="56+" label="Metro-North Stations" />
                        <StatCard number="6" label="Cities & Towns" />
                        <StatCard number="1M+" label="County Population" />
                        <StatCard number="8+" label="Interactive Dashboards" />
                    </div>
                </div>
            </section>

            {/* Call to Action */}
            <section className="container mx-auto px-4 py-16 text-center">
                <h2 className="text-3xl font-bold mb-6">Ready to Explore?</h2>
                <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
                    Dive into the data and discover insights about Westchester County through
                    our comprehensive analysis tools and interactive visualizations.
                </p>
                <Link
                    to="/dashboards/overview"
                    className="inline-block bg-westchester-green-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-westchester-green-700 transition-colors"
                >
                    Get Started
                </Link>
            </section>
        </div>
    );
}

// Helper Components
function FeatureCard({ icon, title, description }: { icon: string; title: string; description: string }) {
    return (
        <div className="bg-white p-6 rounded-lg shadow-lg text-center hover:shadow-xl transition-shadow">
            <div className="text-4xl mb-4">{icon}</div>
            <h3 className="text-xl font-bold mb-2">{title}</h3>
            <p className="text-gray-600">{description}</p>
        </div>
    );
}

function DataSourceCard({ title, description }: { title: string; description: string }) {
    return (
        <div className="bg-white p-4 rounded-lg shadow text-center">
            <h4 className="font-bold mb-1">{title}</h4>
            <p className="text-sm text-gray-600">{description}</p>
        </div>
    );
}

function StatCard({ number, label }: { number: string; label: string }) {
    return (
        <div>
            <div className="text-4xl font-bold mb-2">{number}</div>
            <div className="text-westchester-green-100">{label}</div>
        </div>
    );
}

