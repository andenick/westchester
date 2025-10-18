/**
 * Export Button Component
 * Reusable button for exporting data as CSV or JSON
 */

import { useState } from 'react';
import { downloadCSV, downloadJSON, downloadGeoJSONAsCSV, downloadGeoJSON } from '../utils/exportUtils';

interface ExportButtonProps {
    data: any;
    filename: string;
    label?: string;
    formats?: ('csv' | 'json' | 'geojson')[];
    isGeoJSON?: boolean;
    className?: string;
}

export default function ExportButton({
    data,
    filename,
    label = 'Export Data',
    formats = ['csv', 'json'],
    isGeoJSON = false,
    className = ''
}: ExportButtonProps) {
    const [showMenu, setShowMenu] = useState(false);

    const handleExport = (format: string) => {
        if (!data) {
            alert('No data available to export');
            return;
        }

        try {
            if (isGeoJSON) {
                if (format === 'csv') {
                    downloadGeoJSONAsCSV(data, filename);
                } else if (format === 'geojson') {
                    downloadGeoJSON(data, filename);
                }
            } else {
                if (format === 'csv') {
                    downloadCSV(data, filename);
                } else if (format === 'json') {
                    downloadJSON(data, filename);
                }
            }

            setShowMenu(false);
        } catch (error) {
            console.error('Export error:', error);
            alert('Error exporting data. See console for details.');
        }
    };

    if (formats.length === 1) {
        // Single format - direct button
        return (
            <button
                onClick={() => handleExport(formats[0])}
                className={`inline-flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors ${className}`}
                title={`Export as ${formats[0].toUpperCase()}`}
            >
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                {label}
            </button>
        );
    }

    // Multiple formats - dropdown menu
    return (
        <div className="relative inline-block">
            <button
                onClick={() => setShowMenu(!showMenu)}
                className={`inline-flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors ${className}`}
                title="Export data in various formats"
            >
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                {label}
                <svg className="w-4 h-4 ml-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
            </button>

            {showMenu && (
                <>
                    {/* Backdrop to close menu */}
                    <div
                        className="fixed inset-0 z-10"
                        onClick={() => setShowMenu(false)}
                    />

                    {/* Dropdown menu */}
                    <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-xl z-20 border border-gray-200">
                        {formats.map(format => (
                            <button
                                key={format}
                                onClick={() => handleExport(format)}
                                className="w-full text-left px-4 py-3 hover:bg-gray-100 transition-colors first:rounded-t-lg last:rounded-b-lg flex items-center justify-between"
                            >
                                <span className="font-medium text-gray-900">
                                    Export as {format.toUpperCase()}
                                </span>
                                <span className="text-xs text-gray-500">
                                    {format === 'csv' && '.csv'}
                                    {format === 'json' && '.json'}
                                    {format === 'geojson' && '.geojson'}
                                </span>
                            </button>
                        ))}
                    </div>
                </>
            )}
        </div>
    );
}
