/**
 * Tax Assessment Chart Component
 * 
 * Displays property tax trends over time
 */

import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface TaxData {
    year: string | number;
    average_assessment?: number;
    median_assessment?: number;
    total_assessments?: number;
}

interface TaxAssessmentChartProps {
    data: TaxData[];
    height?: number;
    chartType?: 'line' | 'area';
}

export default function TaxAssessmentChart({ 
    data, 
    height = 400,
    chartType = 'line'
}: TaxAssessmentChartProps) {
    
    const formatCurrency = (value: number) => {
        if (value >= 1000000) {
            return `$${(value / 1000000).toFixed(1)}M`;
        }
        return `$${(value / 1000).toFixed(0)}k`;
    };

    const sortedData = [...data].sort((a, b) => 
        String(a.year).localeCompare(String(b.year))
    );

    if (chartType === 'area') {
        return (
            <ResponsiveContainer width="100%" height={height}>
                <AreaChart data={sortedData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="year" />
                    <YAxis 
                        label={{ value: 'Assessment Value ($)', angle: -90, position: 'insideLeft' }}
                        tickFormatter={formatCurrency}
                    />
                    <Tooltip 
                        formatter={(value: number) => `$${value.toLocaleString()}`}
                        contentStyle={{ backgroundColor: 'white', border: '1px solid #ccc' }}
                    />
                    <Legend />
                    <Area 
                        type="monotone" 
                        dataKey="average_assessment" 
                        stroke="#059669" 
                        fill="#059669" 
                        fillOpacity={0.3}
                        name="Average Assessment"
                    />
                    {sortedData.some(d => d.median_assessment) && (
                        <Area 
                            type="monotone" 
                            dataKey="median_assessment" 
                            stroke="#3B82F6" 
                            fill="#3B82F6" 
                            fillOpacity={0.3}
                            name="Median Assessment"
                        />
                    )}
                </AreaChart>
            </ResponsiveContainer>
        );
    }

    return (
        <ResponsiveContainer width="100%" height={height}>
            <LineChart data={sortedData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="year" />
                <YAxis 
                    label={{ value: 'Assessment Value ($)', angle: -90, position: 'insideLeft' }}
                    tickFormatter={formatCurrency}
                />
                <Tooltip 
                    formatter={(value: number) => `$${value.toLocaleString()}`}
                    contentStyle={{ backgroundColor: 'white', border: '1px solid #ccc' }}
                />
                <Legend />
                <Line 
                    type="monotone" 
                    dataKey="average_assessment" 
                    stroke="#059669" 
                    strokeWidth={2}
                    name="Average Assessment"
                    dot={{ r: 4 }}
                />
                {sortedData.some(d => d.median_assessment) && (
                    <Line 
                        type="monotone" 
                        dataKey="median_assessment" 
                        stroke="#3B82F6" 
                        strokeWidth={2}
                        name="Median Assessment"
                        dot={{ r: 4 }}
                    />
                )}
            </LineChart>
        </ResponsiveContainer>
    );
}

