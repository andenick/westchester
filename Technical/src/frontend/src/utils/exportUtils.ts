/**
 * Data Export Utilities
 * CSV and JSON export functions for dashboards
 */

// Convert array of objects to CSV format
export function convertToCSV(data: any[], headers?: string[]): string {
    if (!data || data.length === 0) {
        return '';
    }

    // Get headers from first object if not provided
    const csvHeaders = headers || Object.keys(data[0]);

    // Create header row
    const headerRow = csvHeaders.join(',');

    // Create data rows
    const dataRows = data.map(row => {
        return csvHeaders.map(header => {
            const value = row[header];

            // Handle different data types
            if (value === null || value === undefined) {
                return '';
            }

            // Handle objects/arrays (stringify them)
            if (typeof value === 'object') {
                return `"${JSON.stringify(value).replace(/"/g, '""')}"`;
            }

            // Handle strings with commas or quotes
            const stringValue = String(value);
            if (stringValue.includes(',') || stringValue.includes('"') || stringValue.includes('\n')) {
                return `"${stringValue.replace(/"/g, '""')}"`;
            }

            return stringValue;
        }).join(',');
    });

    return [headerRow, ...dataRows].join('\n');
}

// Download CSV file
export function downloadCSV(data: any[], filename: string, headers?: string[]): void {
    const csv = convertToCSV(data, headers);
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');

    link.href = URL.createObjectURL(blob);
    link.download = `${filename}_${new Date().toISOString().split('T')[0]}.csv`;
    link.click();

    // Clean up
    URL.revokeObjectURL(link.href);
}

// Download JSON file
export function downloadJSON(data: any, filename: string): void {
    const json = JSON.stringify(data, null, 2);
    const blob = new Blob([json], { type: 'application/json;charset=utf-8;' });
    const link = document.createElement('a');

    link.href = URL.createObjectURL(blob);
    link.download = `${filename}_${new Date().toISOString().split('T')[0]}.json`;
    link.click();

    // Clean up
    URL.revokeObjectURL(link.href);
}

// Convert GeoJSON features to flat CSV format
export function convertGeoJSONToCSV(geojson: any): string {
    if (!geojson || !geojson.features || geojson.features.length === 0) {
        return '';
    }

    const features = geojson.features;

    // Flatten GeoJSON features into simple objects
    const flattened = features.map((feature: any) => {
        const props = feature.properties || {};
        const geometry = feature.geometry || {};

        // Extract coordinates if available
        let lat, lon;
        if (geometry.type === 'Point' && geometry.coordinates) {
            [lon, lat] = geometry.coordinates;
        }

        return {
            ...props,
            geometry_type: geometry.type,
            latitude: lat,
            longitude: lon,
        };
    });

    return convertToCSV(flattened);
}

// Download GeoJSON data as CSV
export function downloadGeoJSONAsCSV(geojson: any, filename: string): void {
    const csv = convertGeoJSONToCSV(geojson);
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');

    link.href = URL.createObjectURL(blob);
    link.download = `${filename}_${new Date().toISOString().split('T')[0]}.csv`;
    link.click();

    // Clean up
    URL.revokeObjectURL(link.href);
}

// Download GeoJSON as JSON
export function downloadGeoJSON(geojson: any, filename: string): void {
    const json = JSON.stringify(geojson, null, 2);
    const blob = new Blob([json], { type: 'application/geo+json;charset=utf-8;' });
    const link = document.createElement('a');

    link.href = URL.createObjectURL(blob);
    link.download = `${filename}_${new Date().toISOString().split('T')[0]}.geojson`;
    link.click();

    // Clean up
    URL.revokeObjectURL(link.href);
}
