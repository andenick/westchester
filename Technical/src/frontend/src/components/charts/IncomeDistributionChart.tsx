/**
 * Income Distribution Chart Component
 * 
 * Displays income distribution across municipalities
 */

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface IncomeData {
    name: string;
    median_household_income?: number;
    per_capita_income?: number;
}

interface IncomeDistributionChartProps {
    data: IncomeData[];
    height?: number;
    showBoth?: boolean;
}

export default function IncomeDistributionChart({ data, height = 400, showBoth = false }: IncomeDistributionChartProps) {
    // Filter out entries without income data and sort
    const validData = data
        .filter(d => d.median_household_income || d.per_capita_income)
        .sort((a, b) => (b.median_household_income || 0) - (a.median_household_income || 0))
        .slice(0, 15); // Top 15

    const formatCurrency = (value: number) => {
        return `$${(value / 1000).toFixed(0)}k`;
    };

    return (
        <ResponsiveContainer width="100%" height={height}>
            <BarChart data={validData} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                    dataKey="name" 
                    angle={-45} 
                    textAnchor="end" 
                    height={100}
                    tick={{ fontSize: 12 }}
                />
                <YAxis 
                    label={{ value: 'Income ($)', angle: -90, position: 'insideLeft' }}
                    tickFormatter={formatCurrency}
                />
                <Tooltip 
                    formatter={(value: number) => `$${value.toLocaleString()}`}
                    contentStyle={{ backgroundColor: 'white', border: '1px solid #ccc' }}
                />
                <Legend />
                
                {showBoth ? (
                    <>
                        <Bar dataKey="median_household_income" fill="#059669" name="Median Household Income" />
                        <Bar dataKey="per_capita_income" fill="#3B82F6" name="Per Capita Income" />
                    </>
                ) : (
                    <Bar dataKey="median_household_income" fill="#059669" name="Median Household Income" />
                )}
            </BarChart>
        </ResponsiveContainer>
    );
}

