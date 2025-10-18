/**
 * User Guide Page - Instructions for using the platform
 */

import React from 'react';

const UserGuidePage: React.FC = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-gray-900 mb-6">
          User Guide
        </h1>

        <div className="bg-white rounded-lg shadow-md p-8">
          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-800 mb-4">
              Getting Started
            </h2>
            <p className="text-gray-700 leading-relaxed mb-4">
              Welcome to the Westchester County Data Platform! This guide will help you
              navigate the various dashboards and features available.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-800 mb-4">
              Available Dashboards
            </h2>

            <div className="space-y-4">
              <div className="border-l-4 border-blue-500 pl-4">
                <h3 className="font-semibold text-gray-800 mb-2">Overview Dashboard</h3>
                <p className="text-gray-700">
                  High-level summary of key metrics across all categories. Start here for
                  a quick snapshot of Westchester County data.
                </p>
              </div>

              <div className="border-l-4 border-blue-500 pl-4">
                <h3 className="font-semibold text-gray-800 mb-2">Demographics Dashboard</h3>
                <p className="text-gray-700">
                  Population, income, education, and housing statistics. View demographic
                  trends and distributions across the county.
                </p>
              </div>

              <div className="border-l-4 border-blue-500 pl-4">
                <h3 className="font-semibold text-gray-800 mb-2">Transit Dashboard</h3>
                <p className="text-gray-700">
                  Metro-North station locations, ridership data, and transit accessibility
                  metrics.
                </p>
              </div>

              <div className="border-l-4 border-blue-500 pl-4">
                <h3 className="font-semibold text-gray-800 mb-2">Infrastructure Dashboard</h3>
                <p className="text-gray-700">
                  Roads, sidewalks, bike lanes, bus stops, and other infrastructure data.
                  Includes GIS mapping and coverage statistics.
                </p>
              </div>

              <div className="border-l-4 border-blue-500 pl-4">
                <h3 className="font-semibold text-gray-800 mb-2">Historical Trends</h3>
                <p className="text-gray-700">
                  Time-series analysis of population, economic indicators, housing market,
                  and employment statistics over multiple years.
                </p>
              </div>

              <div className="border-l-4 border-blue-500 pl-4">
                <h3 className="font-semibold text-gray-800 mb-2">Municipality Comparison</h3>
                <p className="text-gray-700">
                  Compare demographics, services, and metrics across different municipalities
                  within Westchester County.
                </p>
              </div>

              <div className="border-l-4 border-blue-500 pl-4">
                <h3 className="font-semibold text-gray-800 mb-2">Budget Dashboard</h3>
                <p className="text-gray-700">
                  County budget information, departmental allocations, and financial trends.
                </p>
              </div>

              <div className="border-l-4 border-blue-500 pl-4">
                <h3 className="font-semibold text-gray-800 mb-2">Sidewalk Planning</h3>
                <p className="text-gray-700">
                  Transit-oriented development analysis, sidewalk coverage maps, and
                  infrastructure gap identification.
                </p>
              </div>
            </div>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-800 mb-4">
              Navigation Tips
            </h2>
            <ul className="list-disc list-inside space-y-2 text-gray-700">
              <li>Use the top navigation menu to switch between dashboards</li>
              <li>Most charts are interactive - hover for details</li>
              <li>Some dashboards include map views - click and drag to pan, scroll to zoom</li>
              <li>Data is refreshed periodically from official sources</li>
              <li>Export functionality available on select dashboards</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-800 mb-4">
              Data Sources
            </h2>
            <p className="text-gray-700 mb-4">
              Our data comes from trusted sources including:
            </p>
            <ul className="list-disc list-inside space-y-1 text-gray-700">
              <li>U.S. Census Bureau (demographics, population)</li>
              <li>New York State Open Data (municipal services, health facilities)</li>
              <li>Metro-North Railroad (transit schedules and stations)</li>
              <li>Westchester County Government (budget, planning documents)</li>
              <li>OpenStreetMap (infrastructure, roads, sidewalks)</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-800 mb-4">
              Need Help?
            </h2>
            <p className="text-gray-700">
              For questions or issues with the platform, please refer to the{' '}
              <a href="/data-catalog" className="text-blue-600 hover:underline">
                Data Catalog
              </a>{' '}
              for information about available datasets.
            </p>
          </section>
        </div>
      </div>
    </div>
  );
};

export default UserGuidePage;
