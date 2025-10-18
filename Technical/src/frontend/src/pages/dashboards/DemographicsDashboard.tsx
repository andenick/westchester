/**
 * Demographics Dashboard
 * 
 * Population, income, and housing statistics for Westchester County
 */

import { useEffect, useState } from 'react';
import apiService from '../../services/api';
import ExportButton from '../../components/ExportButton';
import { PopulationChart, IncomeDistributionChart, DemographicsPieChart } from '../../components/charts';
import type { DemographicsData } from '../../types';

export default function DemographicsDashboard() {
    const [countyData, setCountyData] = useState<DemographicsData | null>(null);
    const [municipalityData, setMunicipalityData] = useState<DemographicsData[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        loadDemographicsData();
    }, []);

    const loadDemographicsData = async () => {
        try {
            setLoading(true);

            // Load county-level demographics
            const county = await apiService.getCountyDemographics();
            setCountyData(county);

            // Load municipality demographics
            try {
                const municipalities = await apiService.getMunicipalityDemographics();
                setMunicipalityData(municipalities);
            } catch (err) {
                console.log('Municipality data not available');
            }

            setError(null);
        } catch (err) {
            console.error('Error loading demographics:', err);
            setError('Failed to load demographics data. Make sure the API is running and data is downloaded.');
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-green-600 mx-auto mb-4"></div>
                    <p className="text-gray-600">Loading demographics...</p>
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

    // Prepare population data for chart
    const populationChartData = municipalityData
        .filter(m => m.total_population && m.total_population > 0)
        .map(m => ({
            name: m.location_name || 'Unknown',
            population: m.total_population || 0,
            male: m.male_population,
            female: m.female_population,
        }));

    // Prepare income data for chart
    const incomeChartData = municipalityData
        .filter(m => m.median_household_income && m.median_household_income > 0)
        .map(m => ({
            name: m.location_name || 'Unknown',
            median_household_income: m.median_household_income,
            per_capita_income: m.per_capita_income,
        }));

    return (
        <div className="container mx-auto px-4 py-8">
            {/* Header */}
            <div className="mb-8">
                <div className="flex justify-between items-start mb-4">
                    <div className="flex-1">
                        <h1 className="text-4xl font-bold text-gray-900 mb-2">Demographics Dashboard</h1>
                        <p className="text-gray-600">Population, income, and housing statistics for Westchester County</p>
                    </div>

                    {/* Export Buttons */}
                    <div className="flex gap-3">
                        {countyData && (
                            <ExportButton
                                data={countyData}
                                filename="westchester_county_demographics"
                                label="Export County Data"
                                formats={['csv', 'json']}
                            />
                        )}
                        {municipalityData.length > 0 && (
                            <ExportButton
                                data={municipalityData}
                                filename="westchester_municipalities_demographics"
                                label="Export Municipalities"
                                formats={['csv', 'json']}
                            />
                        )}
                    </div>
                </div>

                {/* Data Summary for City Planners */}
                {countyData && (
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                        <div className="flex items-start">
                            <svg className="w-6 h-6 text-blue-600 mr-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                            </svg>
                            <div>
                                <p className="text-sm font-semibold text-blue-900 mb-1">For City Planners:</p>
                                <p className="text-sm text-blue-800">
                                    Complete demographic data from U.S. Census Bureau ({countyData.dataset}, {countyData.year}).
                                    Includes population, income, housing, and employment statistics for county and {municipalityData.length} municipalities.
                                    Use export buttons to download for demographic analysis and planning studies.
                                </p>
                            </div>
                        </div>
                    </div>
                )}
            </div>

            {/* County Summary Cards */}
            {countyData && (
                <div className="grid md:grid-cols-4 gap-6 mb-8">
                    <StatCard
                        label="Total Population"
                        value={countyData.total_population?.toLocaleString() || 'N/A'}
                        icon="👥"
                    />
                    <StatCard
                        label="Median Household Income"
                        value={countyData.median_household_income ? `$${countyData.median_household_income.toLocaleString()}` : 'N/A'}
                        icon="💰"
                    />
                    <StatCard
                        label="Median Home Value"
                        value={countyData.median_home_value ? `$${countyData.median_home_value.toLocaleString()}` : 'N/A'}
                        icon="🏠"
                    />
                    <StatCard
                        label="Median Age"
                        value={countyData.median_age ? `${countyData.median_age} years` : 'N/A'}
                        icon="📅"
                    />
                </div>
            )}

            {/* Population Distribution */}
            {populationChartData.length > 0 && (
                <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
                    <h2 className="text-2xl font-bold mb-4">Population by Municipality</h2>
                    <PopulationChart data={populationChartData} height={500} />
                </div>
            )}

            {/* Race/Ethnicity Breakdown */}
            {countyData && (
                <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
                    <h2 className="text-2xl font-bold mb-4">Race and Ethnicity Distribution</h2>
                    <DemographicsPieChart data={countyData} height={400} />
                </div>
            )}

            {/* Income Distribution */}
            {incomeChartData.length > 0 && (
                <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
                    <h2 className="text-2xl font-bold mb-4">Median Household Income by Municipality</h2>
                    <IncomeDistributionChart data={incomeChartData} height={500} />
                </div>
            )}

            {/* Housing Statistics */}
            {countyData && (
                <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
                    <h2 className="text-2xl font-bold mb-4">Housing Statistics</h2>
                    <div className="grid md:grid-cols-3 gap-6">
                        <HousingCard
                            label="Total Housing Units"
                            value={countyData.total_housing_units?.toLocaleString() || 'N/A'}
                        />
                        <HousingCard
                            label="Occupied Units"
                            value={countyData.occupied_housing_units?.toLocaleString() || 'N/A'}
                            subtext={countyData.total_housing_units && countyData.occupied_housing_units
                                ? `${((countyData.occupied_housing_units / countyData.total_housing_units) * 100).toFixed(1)}% occupancy`
                                : undefined
                            }
                        />
                        <HousingCard
                            label="Median Gross Rent"
                            value={countyData.median_gross_rent ? `$${countyData.median_gross_rent.toLocaleString()}/mo` : 'N/A'}
                        />
                    </div>
                </div>
            )}

            {/* Employment Statistics */}
            {countyData && (
                <div className="bg-white rounded-lg shadow-lg p-6">
                    <h2 className="text-2xl font-bold mb-4">Employment Statistics</h2>
                    <div className="grid md:grid-cols-3 gap-6">
                        <EmploymentCard
                            label="Labor Force"
                            value={countyData.civilian_labor_force?.toLocaleString() || 'N/A'}
                        />
                        <EmploymentCard
                            label="Employed"
                            value={countyData.employed?.toLocaleString() || 'N/A'}
                        />
                        <EmploymentCard
                            label="Unemployment Rate"
                            value={countyData.unemployed && countyData.civilian_labor_force
                                ? `${((countyData.unemployed / countyData.civilian_labor_force) * 100).toFixed(1)}%`
                                : 'N/A'
                            }
                        />
                    </div>
                </div>
            )}

            {/* Data Source Note */}
            {countyData && (
                <div className="mt-8 text-sm text-gray-500">
                    Data Source: U.S. Census Bureau, {countyData.dataset} ({countyData.year})
                </div>
            )}
        </div>
    );
}

// Helper Components
function StatCard({ label, value, icon }: { label: string; value: string; icon: string }) {
    return (
        <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center justify-between mb-2">
                <p className="text-sm text-gray-600">{label}</p>
                <span className="text-2xl">{icon}</span>
            </div>
            <p className="text-2xl font-bold">{value}</p>
        </div>
    );
}

function HousingCard({ label, value, subtext }: { label: string; value: string; subtext?: string }) {
    return (
        <div className="p-4 bg-gray-50 rounded">
            <p className="text-sm text-gray-600 mb-1">{label}</p>
            <p className="text-xl font-bold">{value}</p>
            {subtext && <p className="text-sm text-gray-500 mt-1">{subtext}</p>}
        </div>
    );
}

function EmploymentCard({ label, value }: { label: string; value: string }) {
    return (
        <div className="p-4 bg-gray-50 rounded">
            <p className="text-sm text-gray-600 mb-1">{label}</p>
            <p className="text-xl font-bold">{value}</p>
        </div>
    );
}

