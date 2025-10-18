/**
 * Transit Coverage Chart Component
 * 
 * Displays Metro-North station accessibility metrics
 */

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

interface TransitStation {
    name: string;
    line?: string;
    ridership?: number;
}

interface TransitCoverageChartProps {
    stations: TransitStation[];
    height?: number;
    chartType?: 'bar' | 'pie';
}

const LINE_COLORS: { [key: string]: string } = {
    'Harlem Line': '#0066CC',
    'Hudson Line': '#00AA00',
    'New Haven Line': '#CC0000',
    'Other': '#888888',
};

export default function TransitCoverageChart({ 
    stations, 
    height = 400,
    chartType = 'bar'
}: TransitCoverageChartProps) {
    
    // Count stations by line
    const lineData = stations.reduce((acc: { [key: string]: number }, station) => {
        const line = station.line || 'Other';
        acc[line] = (acc[line] || 0) + 1;
        return acc;
    }, {});

    const chartData = Object.entries(lineData).map(([name, value]) => ({
        name,
        stations: value,
        color: LINE_COLORS[name] || LINE_COLORS['Other']
    }));

    if (chartType === 'pie') {
        return (
            <ResponsiveContainer width="100%" height={height}>
                <PieChart>
                    <Pie
                        data={chartData}
                        dataKey="stations"
                        nameKey="name"
                        cx="50%"
                        cy="50%"
                        outerRadius={120}
                        label={(entry) => `${entry.name}: ${entry.stations}`}
                    >
                        {chartData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                </PieChart>
            </ResponsiveContainer>
        );
    }

    return (
        <ResponsiveContainer width="100%" height={height}>
            <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis label={{ value: 'Number of Stations', angle: -90, position: 'insideLeft' }} />
                <Tooltip contentStyle={{ backgroundColor: 'white', border: '1px solid #ccc' }} />
                <Legend />
                <Bar dataKey="stations" name="Stations" fill="#059669">
                    {chartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                </Bar>
            </BarChart>
        </ResponsiveContainer>
    );
}

