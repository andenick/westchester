/**
 * Budget Dashboard
 *
 * County spending by department and year
 * Includes detailed Planning Department budget analysis
 */

import { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line } from 'recharts';

interface BudgetCategory {
    category: string;
    amount: number;
    percentage: number;
    description?: string;
}

interface YearBudget {
    year: number;
    total_budget: number;
    categories: BudgetCategory[];
    source: string;
    extraction_date: string;
}

interface BudgetData {
    westchester_county_budgets: {
        [year: string]: YearBudget;
    };
    metadata: {
        extracted_from: string;
        extraction_date: string;
        years_available: string[];
        data_quality: string;
        notes: string;
    };
}

interface PlanningBudgetTrends {
    department: {
        name: string;
        number: number;
        mission: string;
    };
    trends: {
        expenditures_change_2022_to_2025: any;
        revenues_change_2022_to_2025: any;
        tax_levy_change_2022_to_2025: any;
    };
    year_summary: Array<{
        year: number;
        total_expenditures: number;
        total_revenues: number;
        tax_levy: number;
        total_positions: number;
    }>;
    key_programs: any;
    service_indicators: any;
    metadata: any;
}

export default function BudgetDashboard() {
    const [budgetData, setBudgetData] = useState<BudgetData | null>(null);
    const [planningData, setPlanningData] = useState<PlanningBudgetTrends | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        Promise.all([
            fetch('/data/westchester_budget_data.json').then(res => res.json()),
            fetch('http://localhost:8000/api/budget/planning/trends').then(res => res.json())
        ])
            .then(([countyData, planningTrendsData]) => {
                setBudgetData(countyData);
                setPlanningData(planningTrendsData);
                setLoading(false);
            })
            .catch(err => {
                console.error('Error loading budget data:', err);
                setError('Failed to load budget data');
                setLoading(false);
            });
    }, []);

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-green-600 mx-auto mb-4"></div>
                    <p className="text-gray-600">Loading budget data...</p>
                </div>
            </div>
        );
    }

    if (error || !budgetData) {
        return (
            <div className="container mx-auto px-4 py-8">
                <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
                    <p className="font-bold">Error</p>
                    <p>{error || 'Budget data not available'}</p>
                </div>
            </div>
        );
    }

    // Get 2025 data (most recent)
    const currentYear = budgetData.westchester_county_budgets['2025'];
    const totalBudget = currentYear.total_budget;

    // Prepare department data for charts (sorted by amount)
    const departmentBudgets = currentYear.categories
        .map(cat => ({
            department: cat.category,
            amount: cat.amount,
            percentage: cat.percentage,
            description: cat.description
        }))
        .sort((a, b) => b.amount - a.amount);

    // Prepare yearly trend data
    const yearlyBudgets = Object.keys(budgetData.westchester_county_budgets)
        .sort()
        .map(year => ({
            year,
            total: budgetData.westchester_county_budgets[year].total_budget
        }));

    // Calculate growth rate
    const prevYear = budgetData.westchester_county_budgets['2024'];
    const growthRate = prevYear
        ? ((currentYear.total_budget - prevYear.total_budget) / prevYear.total_budget * 100).toFixed(1)
        : '0.0';

    // Estimate population for per capita (Westchester County ~997,904)
    const population = 997904;
    const perCapita = (totalBudget / population).toFixed(0);

    const COLORS = ['#059669', '#3B82F6', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#6B7280'];

    return (
        <div className="container mx-auto px-4 py-8">
            {/* Header */}
            <div className="mb-8">
                <h1 className="text-4xl font-bold text-gray-900 mb-2">County Budget Dashboard</h1>
                <p className="text-gray-600">Westchester County spending analysis by department and fiscal year</p>
                <div className="mt-4 bg-green-50 border border-green-200 rounded-lg p-4">
                    <p className="text-sm text-green-800">
                        <strong>Data Source:</strong> {currentYear.source} | <strong>Official adopted budgets</strong> | Extracted {budgetData.metadata.extraction_date}
                    </p>
                </div>
            </div>

            {/* Summary Cards */}
            <div className="grid md:grid-cols-4 gap-6 mb-8">
                <StatCard
                    label="Total Budget FY2025"
                    value={`$${(totalBudget / 1000000000).toFixed(2)}B`}
                    icon="💰"
                />
                <StatCard
                    label="Per Capita Spending"
                    value={`$${perCapita}`}
                    icon="👤"
                />
                <StatCard
                    label="Year-over-Year Growth"
                    value={`+${growthRate}%`}
                    icon="📈"
                />
                <StatCard
                    label="Budget Categories"
                    value={departmentBudgets.length.toString()}
                    icon="🏛️"
                />
            </div>

            {/* Budget by Department - Pie Chart */}
            <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
                <h2 className="text-2xl font-bold mb-4">Budget Allocation by Category (FY2025)</h2>
                <div className="grid md:grid-cols-2 gap-8">
                    <div>
                        <ResponsiveContainer width="100%" height={400}>
                            <PieChart>
                                <Pie
                                    data={departmentBudgets}
                                    dataKey="amount"
                                    nameKey="department"
                                    cx="50%"
                                    cy="50%"
                                    outerRadius={120}
                                    label={(entry: any) => `${entry.percentage}%`}
                                >
                                    {departmentBudgets.map((_entry, index) => (
                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                    ))}
                                </Pie>
                                <Tooltip formatter={(value: number) => `$${(value / 1000000).toFixed(1)}M`} />
                                <Legend />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                    <div className="space-y-3">
                        {departmentBudgets.map((dept, idx) => (
                            <DepartmentRow
                                key={dept.department}
                                department={dept.department}
                                amount={dept.amount}
                                percentage={dept.percentage}
                                color={COLORS[idx % COLORS.length]}
                            />
                        ))}
                    </div>
                </div>
            </div>

            {/* Yearly Budget Trends */}
            <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
                <h2 className="text-2xl font-bold mb-4">Budget Trends (2023-2025)</h2>
                <ResponsiveContainer width="100%" height={400}>
                    <BarChart data={yearlyBudgets} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="year" />
                        <YAxis
                            label={{ value: 'Budget ($)', angle: -90, position: 'insideLeft' }}
                            tickFormatter={(value) => `$${(value / 1000000000).toFixed(2)}B`}
                        />
                        <Tooltip formatter={(value: number) => `$${(value / 1000000000).toFixed(2)}B`} />
                        <Legend />
                        <Bar dataKey="total" fill="#059669" name="Total Budget" />
                    </BarChart>
                </ResponsiveContainer>
            </div>

            {/* Top Spending Categories */}
            <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
                <h2 className="text-2xl font-bold mb-4">Top Spending Priorities (FY2025)</h2>
                <div className="grid md:grid-cols-3 gap-6">
                    {departmentBudgets.slice(0, 3).map((dept, idx) => (
                        <PriorityCard
                            key={dept.department}
                            rank={idx + 1}
                            category={dept.department}
                            amount={dept.amount}
                            description={dept.description || ''}
                        />
                    ))}
                </div>
            </div>

            {/* Planning Department Budget Analysis */}
            {planningData && (
                <div className="mt-12">
                    <div className="mb-6">
                        <h2 className="text-3xl font-bold text-gray-900 mb-2">Planning Department Budget Analysis</h2>
                        <p className="text-gray-600">{planningData.department.mission}</p>
                    </div>

                    {/* Planning Department Summary Cards */}
                    <div className="grid md:grid-cols-4 gap-6 mb-8">
                        <StatCard
                            label="FY2025 Budget"
                            value={`$${(planningData.year_summary.find(y => y.year === 2025)?.total_expenditures! / 1000000).toFixed(2)}M`}
                            icon="🏛️"
                        />
                        <StatCard
                            label="Total Staff"
                            value={planningData.year_summary.find(y => y.year === 2025)?.total_positions.toString() || '0'}
                            icon="👥"
                        />
                        <StatCard
                            label="3-Year Change"
                            value={`${planningData.trends.expenditures_change_2022_to_2025.total_expenditures.percent.toFixed(1)}%`}
                            icon="📉"
                        />
                        <StatCard
                            label="FY2025 Tax Levy"
                            value={`$${(planningData.year_summary.find(y => y.year === 2025)?.tax_levy! / 1000000).toFixed(2)}M`}
                            icon="💰"
                        />
                    </div>

                    {/* Planning Department Trends */}
                    <div className="grid md:grid-cols-2 gap-8 mb-8">
                        <div className="bg-white rounded-lg shadow-lg p-6">
                            <h3 className="text-xl font-bold mb-4">Budget Trend (2022-2025)</h3>
                            <ResponsiveContainer width="100%" height={300}>
                                <LineChart data={planningData.year_summary}>
                                    <CartesianGrid strokeDasharray="3 3" />
                                    <XAxis dataKey="year" />
                                    <YAxis tickFormatter={(value) => `$${(value / 1000000).toFixed(0)}M`} />
                                    <Tooltip formatter={(value: number) => `$${(value / 1000000).toFixed(2)}M`} />
                                    <Legend />
                                    <Line type="monotone" dataKey="total_expenditures" stroke="#059669" name="Total Expenditures" strokeWidth={2} />
                                    <Line type="monotone" dataKey="total_revenues" stroke="#3B82F6" name="Total Revenues" strokeWidth={2} />
                                    <Line type="monotone" dataKey="tax_levy" stroke="#EF4444" name="Tax Levy" strokeWidth={2} />
                                </LineChart>
                            </ResponsiveContainer>
                        </div>

                        <div className="bg-white rounded-lg shadow-lg p-6">
                            <h3 className="text-xl font-bold mb-4">Multi-Year Comparison</h3>
                            <ResponsiveContainer width="100%" height={300}>
                                <BarChart data={planningData.year_summary}>
                                    <CartesianGrid strokeDasharray="3 3" />
                                    <XAxis dataKey="year" />
                                    <YAxis tickFormatter={(value) => `$${(value / 1000000).toFixed(0)}M`} />
                                    <Tooltip formatter={(value: number) => `$${(value / 1000000).toFixed(2)}M`} />
                                    <Legend />
                                    <Bar dataKey="total_expenditures" fill="#059669" name="Expenditures" />
                                    <Bar dataKey="total_revenues" fill="#3B82F6" name="Revenues" />
                                </BarChart>
                            </ResponsiveContainer>
                        </div>
                    </div>

                    {/* Key Insights */}
                    <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
                        <h3 className="text-xl font-bold mb-4">Key Insights</h3>
                        <div className="grid md:grid-cols-3 gap-4">
                            <div className="p-4 bg-red-50 rounded-lg">
                                <p className="text-sm text-gray-600 mb-1">Budget Change (2022-2025)</p>
                                <p className="text-2xl font-bold text-red-600">
                                    {planningData.trends.expenditures_change_2022_to_2025.total_expenditures.percent.toFixed(1)}%
                                </p>
                                <p className="text-xs text-gray-500 mt-1">
                                    ${(planningData.trends.expenditures_change_2022_to_2025.total_expenditures.amount / 1000000).toFixed(1)}M decrease
                                </p>
                            </div>
                            <div className="p-4 bg-green-50 rounded-lg">
                                <p className="text-sm text-gray-600 mb-1">Personnel Costs</p>
                                <p className="text-2xl font-bold text-green-600">
                                    +{planningData.trends.expenditures_change_2022_to_2025.personal_services.percent.toFixed(1)}%
                                </p>
                                <p className="text-xs text-gray-500 mt-1">Stable workforce of 42 positions</p>
                            </div>
                            <div className="p-4 bg-blue-50 rounded-lg">
                                <p className="text-sm text-gray-600 mb-1">Tax Levy Change</p>
                                <p className="text-2xl font-bold text-blue-600">
                                    {planningData.trends.tax_levy_change_2022_to_2025.percent.toFixed(1)}%
                                </p>
                                <p className="text-xs text-gray-500 mt-1">
                                    ${Math.abs(planningData.trends.tax_levy_change_2022_to_2025.amount / 1000000).toFixed(1)}M reduction
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Data Source */}
            <div className="mt-4 text-sm text-gray-600 text-center py-4 bg-gray-50 rounded">
                Data extracted from official Westchester County adopted budget documents | Last updated: {budgetData.metadata.extraction_date}
                {planningData && <span> | Planning Department data from FY2022, 2023, 2025</span>}
            </div>
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

function DepartmentRow({ department, amount, percentage, color }: {
    department: string;
    amount: number;
    percentage: number;
    color: string;
}) {
    return (
        <div className="flex items-center justify-between p-3 bg-gray-50 rounded">
            <div className="flex items-center gap-3">
                <div className="w-4 h-4 rounded" style={{ backgroundColor: color }} />
                <span className="font-medium">{department}</span>
            </div>
            <div className="text-right">
                <p className="font-semibold">${(amount / 1000000).toFixed(1)}M</p>
                <p className="text-xs text-gray-500">{percentage}%</p>
            </div>
        </div>
    );
}

function PriorityCard({ rank, category, amount, description }: {
    rank: number;
    category: string;
    amount: number;
    description: string;
}) {
    return (
        <div className="p-4 bg-gradient-to-br from-green-50 to-blue-50 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
                <span className="bg-green-600 text-white w-8 h-8 rounded-full flex items-center justify-center font-bold">
                    {rank}
                </span>
                <h3 className="text-lg font-semibold">{category}</h3>
            </div>
            <p className="text-2xl font-bold text-green-600 mb-2">
                ${(amount / 1000000).toFixed(0)}M
            </p>
            <p className="text-sm text-gray-600">{description}</p>
        </div>
    );
}

