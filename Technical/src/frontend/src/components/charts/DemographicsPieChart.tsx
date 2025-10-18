/**
 * Demographics Pie Chart Component
 * 
 * Displays race/ethnicity breakdown
 */

import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

interface DemographicsData {
    white_alone?: number;
    black_alone?: number;
    asian_alone?: number;
    hispanic_or_latino?: number;
    other?: number;
}

interface DemographicsPieChartProps {
    data: DemographicsData;
    height?: number;
}

const COLORS = {
    'White': '#3B82F6',
    'Black or African American': '#EF4444',
    'Asian': '#10B981',
    'Hispanic or Latino': '#F59E0B',
    'Other': '#8B5CF6',
};

export default function DemographicsPieChart({ data, height = 400 }: DemographicsPieChartProps) {
    // Transform data into chart format
    const chartData = [
        { name: 'White', value: data.white_alone || 0, color: COLORS['White'] },
        { name: 'Black or African American', value: data.black_alone || 0, color: COLORS['Black or African American'] },
        { name: 'Asian', value: data.asian_alone || 0, color: COLORS['Asian'] },
        { name: 'Hispanic or Latino', value: data.hispanic_or_latino || 0, color: COLORS['Hispanic or Latino'] },
    ].filter(item => item.value > 0);

    // Calculate total for percentage
    const total = chartData.reduce((sum, item) => sum + item.value, 0);

    const renderLabel = (entry: any) => {
        const percentage = ((entry.value / total) * 100).toFixed(1);
        return `${percentage}%`;
    };

    return (
        <ResponsiveContainer width="100%" height={height}>
            <PieChart>
                <Pie
                    data={chartData}
                    cx="50%"
                    cy="50%"
                    labelLine={true}
                    label={renderLabel}
                    outerRadius={120}
                    fill="#8884d8"
                    dataKey="value"
                >
                    {chartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                </Pie>
                <Tooltip 
                    formatter={(value: number) => [
                        `${value.toLocaleString()} (${((value / total) * 100).toFixed(1)}%)`,
                        'Population'
                    ]}
                    contentStyle={{ backgroundColor: 'white', border: '1px solid #ccc' }}
                />
                <Legend 
                    verticalAlign="bottom" 
                    height={36}
                    formatter={(value, entry: any) => {
                        const percentage = ((entry.payload.value / total) * 100).toFixed(1);
                        return `${value}: ${percentage}%`;
                    }}
                />
            </PieChart>
        </ResponsiveContainer>
    );
}

