/**
 * Municipality Comparison Dashboard
 * 
 * Side-by-side comparison of towns and cities
 */

import { useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

// Sample municipality data
const municipalities = [
    { 
        name: 'Yonkers',
        population: 211569,
        medianIncome: 68976,
        medianHomeValue: 485000,
        area: 20.3,
        density: 10426,
        taxRate: 3.45,
    },
    { 
        name: 'New Rochelle',
        population: 79446,
        medianIncome: 88577,
        medianHomeValue: 625000,
        area: 13.2,
        density: 6018,
        taxRate: 3.12,
    },
    { 
        name: 'White Plains',
        population: 59559,
        medianIncome: 93171,
        medianHomeValue: 580000,
        area: 10.0,
        density: 5956,
        taxRate: 2.78,
    },
    { 
        name: 'Mount Vernon',
        population: 73893,
        medianIncome: 58482,
        medianHomeValue: 425000,
        area: 4.4,
        density: 16794,
        taxRate: 3.89,
    },
    { 
        name: 'Scarsdale',
        population: 17892,
        medianIncome: 250000,
        medianHomeValue: 1425000,
        area: 6.6,
        density: 2711,
        taxRate: 2.12,
    },
    { 
        name: 'Rye',
        population: 16630,
        medianIncome: 185000,
        medianHomeValue: 1150000,
        area: 6.3,
        density: 2640,
        taxRate: 2.45,
    },
];

export default function MunicipalityComparisonDashboard() {
    const [selectedMunicipalities, setSelectedMunicipalities] = useState<string[]>(['Yonkers', 'White Plains']);

    const handleToggle = (name: string) => {
        if (selectedMunicipalities.includes(name)) {
            setSelectedMunicipalities(selectedMunicipalities.filter(m => m !== name));
        } else if (selectedMunicipalities.length < 4) {
            setSelectedMunicipalities([...selectedMunicipalities, name]);
        }
    };

    const selectedData = municipalities.filter(m => selectedMunicipalities.includes(m.name));

    return (
        <div className="container mx-auto px-4 py-8">
            {/* Header */}
            <div className="mb-8">
                <h1 className="text-4xl font-bold text-gray-900 mb-2">Municipality Comparison</h1>
                <p className="text-gray-600">Compare demographics, economics, and services across Westchester municipalities</p>
            </div>

            {/* Municipality Selector */}
            <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
                <h2 className="text-xl font-bold mb-4">Select Municipalities to Compare (up to 4)</h2>
                <div className="grid md:grid-cols-3 gap-3">
                    {municipalities.map(muni => (
                        <button
                            key={muni.name}
                            onClick={() => handleToggle(muni.name)}
                            className={`p-3 rounded-lg border-2 transition-colors ${
                                selectedMunicipalities.includes(muni.name)
                                    ? 'border-green-500 bg-green-50'
                                    : 'border-gray-200 hover:border-gray-300'
                            }`}
                        >
                            <div className="flex items-center justify-between">
                                <span className="font-medium">{muni.name}</span>
                                {selectedMunicipalities.includes(muni.name) && (
                                    <span className="text-green-600">✓</span>
                                )}
                            </div>
                            <p className="text-xs text-gray-500 mt-1">Pop: {muni.population.toLocaleString()}</p>
                        </button>
                    ))}
                </div>
            </div>

            {/* Comparison Cards */}
            {selectedData.length > 0 && (
                <>
                    {/* Population Comparison */}
                    <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
                        <h2 className="text-2xl font-bold mb-4">Population Comparison</h2>
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={selectedData}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="name" />
                                <YAxis tickFormatter={(value) => (value / 1000).toFixed(0) + 'k'} />
                                <Tooltip formatter={(value: number) => value.toLocaleString()} />
                                <Legend />
                                <Bar dataKey="population" fill="#059669" name="Population" />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>

                    {/* Income Comparison */}
                    <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
                        <h2 className="text-2xl font-bold mb-4">Median Household Income Comparison</h2>
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={selectedData}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="name" />
                                <YAxis tickFormatter={(value) => '$' + (value / 1000).toFixed(0) + 'k'} />
                                <Tooltip formatter={(value: number) => '$' + value.toLocaleString()} />
                                <Legend />
                                <Bar dataKey="medianIncome" fill="#3B82F6" name="Median Income" />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>

                    {/* Home Value Comparison */}
                    <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
                        <h2 className="text-2xl font-bold mb-4">Median Home Value Comparison</h2>
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={selectedData}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="name" />
                                <YAxis tickFormatter={(value) => '$' + (value / 1000).toFixed(0) + 'k'} />
                                <Tooltip formatter={(value: number) => '$' + value.toLocaleString()} />
                                <Legend />
                                <Bar dataKey="medianHomeValue" fill="#F59E0B" name="Median Home Value" />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>

                    {/* Side-by-Side Comparison Table */}
                    <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
                        <h2 className="text-2xl font-bold mb-4">Detailed Comparison</h2>
                        <div className="overflow-x-auto">
                            <table className="min-w-full divide-y divide-gray-200">
                                <thead className="bg-gray-50">
                                    <tr>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Metric</th>
                                        {selectedData.map(muni => (
                                            <th key={muni.name} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                                {muni.name}
                                            </th>
                                        ))}
                                    </tr>
                                </thead>
                                <tbody className="bg-white divide-y divide-gray-200">
                                    <ComparisonRow 
                                        label="Population"
                                        data={selectedData}
                                        accessor={(m) => m.population.toLocaleString()}
                                    />
                                    <ComparisonRow 
                                        label="Median Income"
                                        data={selectedData}
                                        accessor={(m) => '$' + m.medianIncome.toLocaleString()}
                                    />
                                    <ComparisonRow 
                                        label="Median Home Value"
                                        data={selectedData}
                                        accessor={(m) => '$' + m.medianHomeValue.toLocaleString()}
                                    />
                                    <ComparisonRow 
                                        label="Area (sq mi)"
                                        data={selectedData}
                                        accessor={(m) => m.area.toFixed(1)}
                                    />
                                    <ComparisonRow 
                                        label="Population Density"
                                        data={selectedData}
                                        accessor={(m) => m.density.toLocaleString() + '/sq mi'}
                                    />
                                    <ComparisonRow 
                                        label="Tax Rate"
                                        data={selectedData}
                                        accessor={(m) => m.taxRate.toFixed(2) + '%'}
                                    />
                                </tbody>
                            </table>
                        </div>
                    </div>
                </>
            )}

            {selectedData.length === 0 && (
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
                    <p className="text-yellow-800">Please select at least one municipality to compare.</p>
                </div>
            )}

            {/* Data Source */}
            <div className="mt-4 text-sm text-gray-500">
                Data Source: U.S. Census Bureau ACS 5-Year Estimates, Local Tax Assessors
            </div>
        </div>
    );
}

// Helper Component
function ComparisonRow({ label, data, accessor }: {
    label: string;
    data: any[];
    accessor: (item: any) => string;
}) {
    return (
        <tr>
            <td className="px-6 py-4 whitespace-nowrap font-medium text-gray-900">{label}</td>
            {data.map((item, idx) => (
                <td key={idx} className="px-6 py-4 whitespace-nowrap text-gray-600">
                    {accessor(item)}
                </td>
            ))}
        </tr>
    );
}

