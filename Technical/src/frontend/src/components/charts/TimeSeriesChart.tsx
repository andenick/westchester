import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface TimeSeriesChartProps {
    data: any[];
    dataKey: string;
    title: string;
    xAxisKey: string;
    lineColor?: string;
}

const TimeSeriesChart: React.FC<TimeSeriesChartProps> = ({ data, dataKey, title, xAxisKey, lineColor = '#8884d8' }) => {
    if (!data || data.length === 0) {
        return <div className="text-center text-gray-500">No data available for {title}</div>;
    }

    return (
        <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
            <h3 className="text-xl font-bold mb-4">{title}</h3>
            <ResponsiveContainer width="100%" height={300}>
                <LineChart
                    data={data}
                    margin={{
                        top: 5,
                        right: 30,
                        left: 20,
                        bottom: 5,
                    }}
                >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey={xAxisKey} />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey={dataKey} stroke={lineColor} activeDot={{ r: 8 }} />
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
};

export default TimeSeriesChart;
