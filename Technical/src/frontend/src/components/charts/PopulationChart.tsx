/**
 * Population Chart Component
 * 
 * Displays population trends by municipality
 */

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface PopulationData {
    name: string;
    population: number;
    male?: number;
    female?: number;
}

interface PopulationChartProps {
    data: PopulationData[];
    showGenderBreakdown?: boolean;
    height?: number;
}

export default function PopulationChart({ data, showGenderBreakdown = false, height = 400 }: PopulationChartProps) {
    // Sort data by population (descending)
    const sortedData = [...data].sort((a, b) => b.population - a.population);
    
    // Take top 15 for readability
    const displayData = sortedData.slice(0, 15);

    return (
        <ResponsiveContainer width="100%" height={height}>
            <BarChart data={displayData} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                    dataKey="name" 
                    angle={-45} 
                    textAnchor="end" 
                    height={100}
                    tick={{ fontSize: 12 }}
                />
                <YAxis 
                    label={{ value: 'Population', angle: -90, position: 'insideLeft' }}
                    tickFormatter={(value) => value.toLocaleString()}
                />
                <Tooltip 
                    formatter={(value: number) => value.toLocaleString()}
                    contentStyle={{ backgroundColor: 'white', border: '1px solid #ccc' }}
                />
                <Legend />
                
                {showGenderBreakdown ? (
                    <>
                        <Bar dataKey="male" fill="#3B82F6" name="Male" />
                        <Bar dataKey="female" fill="#EC4899" name="Female" />
                    </>
                ) : (
                    <Bar dataKey="population" fill="#059669" name="Total Population" />
                )}
            </BarChart>
        </ResponsiveContainer>
    );
}

