/**
 * About Page - Information about the Westchester County Data Platform
 */

import React from 'react';

const AboutPage: React.FC = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-gray-900 mb-6">
          About Westchester County Data Platform
        </h1>

        <div className="bg-white rounded-lg shadow-md p-8">
          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-800 mb-4">
              Project Overview
            </h2>
            <p className="text-gray-700 leading-relaxed mb-4">
              The Westchester County Data Platform is a comprehensive data visualization
              and analytics tool designed to provide insights into Westchester County's
              demographics, infrastructure, transit systems, and municipal services.
            </p>
            <p className="text-gray-700 leading-relaxed">
              This platform aggregates data from multiple sources including the U.S. Census
              Bureau, New York State open data, Metro-North Railroad, and Westchester County
              government sources to provide a unified view of the county's key metrics.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-800 mb-4">
              Features
            </h2>
            <ul className="list-disc list-inside space-y-2 text-gray-700">
              <li>Interactive dashboards for demographics, transit, and infrastructure</li>
              <li>Historical trend analysis</li>
              <li>Municipality comparison tools</li>
              <li>Budget and financial data visualization</li>
              <li>Sidewalk coverage and transit-oriented development planning</li>
              <li>Municipal services mapping</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-800 mb-4">
              Technology Stack
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h3 className="font-semibold text-gray-800 mb-2">Frontend</h3>
                <ul className="list-disc list-inside text-gray-700 space-y-1">
                  <li>React 19</li>
                  <li>TypeScript</li>
                  <li>Vite</li>
                  <li>Tailwind CSS</li>
                  <li>Recharts (data visualization)</li>
                  <li>Leaflet (mapping)</li>
                </ul>
              </div>
              <div>
                <h3 className="font-semibold text-gray-800 mb-2">Backend</h3>
                <ul className="list-disc list-inside text-gray-700 space-y-1">
                  <li>FastAPI (Python)</li>
                  <li>Pandas (data processing)</li>
                  <li>GeoPandas (geospatial data)</li>
                  <li>Uvicorn (server)</li>
                </ul>
              </div>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-800 mb-4">
              Version Information
            </h2>
            <p className="text-gray-700">
              <strong>Version:</strong> 1.0.0<br />
              <strong>Last Updated:</strong> October 2025<br />
              <strong>Status:</strong> Production
            </p>
          </section>
        </div>
      </div>
    </div>
  );
};

export default AboutPage;
