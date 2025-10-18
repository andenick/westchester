/**
 * Data Sources Page - Information about data sources and attribution
 */

import React from 'react';

const DataSourcesPage: React.FC = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-gray-900 mb-6">
          Data Sources
        </h1>

        <div className="bg-white rounded-lg shadow-md p-8">
          <p className="text-gray-700 leading-relaxed mb-8">
            The Westchester County Data Platform aggregates data from multiple authoritative
            sources to provide comprehensive insights into county metrics. Below is a complete
            list of our data sources with attribution.
          </p>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-800 mb-4 border-b-2 border-gray-200 pb-2">
              Federal Sources
            </h2>

            <div className="space-y-6">
              <div>
                <h3 className="font-semibold text-gray-800 mb-2">
                  U.S. Census Bureau
                </h3>
                <p className="text-gray-700 mb-2">
                  Demographic data, population statistics, American Community Survey (ACS)
                </p>
                <p className="text-sm text-gray-600">
                  <strong>Website:</strong>{' '}
                  <a
                    href="https://www.census.gov"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline"
                  >
                    census.gov
                  </a>
                </p>
                <p className="text-sm text-gray-600">
                  <strong>API:</strong> Census API v2
                </p>
                <p className="text-sm text-gray-600">
                  <strong>Data Types:</strong> Population, income, education, housing, employment
                </p>
              </div>

              <div>
                <h3 className="font-semibold text-gray-800 mb-2">
                  Federal Reserve Economic Data (FRED)
                </h3>
                <p className="text-gray-700 mb-2">
                  Economic indicators and historical economic trends
                </p>
                <p className="text-sm text-gray-600">
                  <strong>Website:</strong>{' '}
                  <a
                    href="https://fred.stlouisfed.org"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline"
                  >
                    fred.stlouisfed.org
                  </a>
                </p>
              </div>
            </div>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-800 mb-4 border-b-2 border-gray-200 pb-2">
              State & Local Sources
            </h2>

            <div className="space-y-6">
              <div>
                <h3 className="font-semibold text-gray-800 mb-2">
                  New York State Open Data
                </h3>
                <p className="text-gray-700 mb-2">
                  Health facilities, public services, crime statistics
                </p>
                <p className="text-sm text-gray-600">
                  <strong>Website:</strong>{' '}
                  <a
                    href="https://data.ny.gov"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline"
                  >
                    data.ny.gov
                  </a>
                </p>
                <p className="text-sm text-gray-600">
                  <strong>Data Types:</strong> Healthcare, education, public safety
                </p>
              </div>

              <div>
                <h3 className="font-semibold text-gray-800 mb-2">
                  Westchester County Government
                </h3>
                <p className="text-gray-700 mb-2">
                  Budget documents, planning reports, municipal services
                </p>
                <p className="text-sm text-gray-600">
                  <strong>Website:</strong>{' '}
                  <a
                    href="https://www.westchestergov.com"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline"
                  >
                    westchestergov.com
                  </a>
                </p>
                <p className="text-sm text-gray-600">
                  <strong>Data Types:</strong> Budgets, planning, GIS data
                </p>
              </div>
            </div>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-800 mb-4 border-b-2 border-gray-200 pb-2">
              Transportation Sources
            </h2>

            <div className="space-y-6">
              <div>
                <h3 className="font-semibold text-gray-800 mb-2">
                  Metro-North Railroad (MTA)
                </h3>
                <p className="text-gray-700 mb-2">
                  Station locations, schedules, ridership data (GTFS format)
                </p>
                <p className="text-sm text-gray-600">
                  <strong>Website:</strong>{' '}
                  <a
                    href="https://new.mta.info/developers"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline"
                  >
                    MTA Open Data
                  </a>
                </p>
                <p className="text-sm text-gray-600">
                  <strong>Data Format:</strong> GTFS (General Transit Feed Specification)
                </p>
              </div>
            </div>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-800 mb-4 border-b-2 border-gray-200 pb-2">
              Geographic & Infrastructure Data
            </h2>

            <div className="space-y-6">
              <div>
                <h3 className="font-semibold text-gray-800 mb-2">
                  OpenStreetMap
                </h3>
                <p className="text-gray-700 mb-2">
                  Roads, sidewalks, bike lanes, points of interest
                </p>
                <p className="text-sm text-gray-600">
                  <strong>Website:</strong>{' '}
                  <a
                    href="https://www.openstreetmap.org"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline"
                  >
                    openstreetmap.org
                  </a>
                </p>
                <p className="text-sm text-gray-600">
                  <strong>License:</strong> ODbL (Open Database License)
                </p>
                <p className="text-sm text-gray-600">
                  <strong>Attribution:</strong> © OpenStreetMap contributors
                </p>
              </div>

              <div>
                <h3 className="font-semibold text-gray-800 mb-2">
                  U.S. Census TIGER/Line Shapefiles
                </h3>
                <p className="text-gray-700 mb-2">
                  County boundaries, census tract boundaries, road networks
                </p>
                <p className="text-sm text-gray-600">
                  <strong>Website:</strong>{' '}
                  <a
                    href="https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline"
                  >
                    Census TIGER/Line
                  </a>
                </p>
              </div>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-800 mb-4 border-b-2 border-gray-200 pb-2">
              Data Update Schedule
            </h2>
            <ul className="list-disc list-inside space-y-2 text-gray-700">
              <li><strong>Census data:</strong> Annual (ACS estimates)</li>
              <li><strong>Economic indicators:</strong> Monthly/Quarterly</li>
              <li><strong>Transit data:</strong> Updated as schedules change</li>
              <li><strong>Budget data:</strong> Annual (fiscal year)</li>
              <li><strong>Infrastructure data:</strong> Periodic updates from OSM</li>
            </ul>
          </section>
        </div>

        <div className="mt-8 bg-blue-50 border-l-4 border-blue-500 p-6 rounded">
          <h3 className="font-semibold text-gray-800 mb-2">
            Data Quality & Accuracy
          </h3>
          <p className="text-gray-700">
            All data is sourced from official government agencies and authoritative public
            datasets. While we strive for accuracy, users should verify critical information
            with original sources. Data may be subject to revisions and updates by source agencies.
          </p>
        </div>
      </div>
    </div>
  );
};

export default DataSourcesPage;
