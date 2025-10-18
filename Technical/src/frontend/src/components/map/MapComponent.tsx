/**
 * Map Component
 * 
 * Interactive map displaying Westchester County data using Leaflet
 */

import { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import type { GeoJSONFeatureCollection, TransitStation } from '../../types';
import apiService from '../../services/api';

// Fix for default Leaflet marker icons
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

const DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41],
});

L.Marker.prototype.options.icon = DefaultIcon;

// Westchester County center coordinates
const WESTCHESTER_CENTER: [number, number] = [41.15, -73.75];
const DEFAULT_ZOOM = 10;

interface MapComponentProps {
    height?: string;
    showStations?: boolean;
}

export default function MapComponent({ height = '600px', showStations = true }: MapComponentProps) {
    const [stations, setStations] = useState<TransitStation[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (showStations) {
            loadStations();
        }
    }, [showStations]);

    const loadStations = async () => {
        try {
            setLoading(true);
            const data: GeoJSONFeatureCollection = await apiService.getTransitStations();

            // Convert GeoJSON features to TransitStation objects
            const stationData: TransitStation[] = data.features.map((feature) => {
                const coords = feature.geometry.coordinates;
                return {
                    name: feature.properties.name,
                    id: feature.properties.id,
                    code: feature.properties.code,
                    description: feature.properties.description,
                    wheelchair_accessible: feature.properties.wheelchair_accessible || false,
                    county: feature.properties.county,
                    state: feature.properties.state,
                    latitude: Array.isArray(coords) ? coords[1] as number : 0,
                    longitude: Array.isArray(coords) ? coords[0] as number : 0,
                };
            });

            setStations(stationData);
            setError(null);
        } catch (err) {
            console.error('Error loading stations:', err);
            setError('Failed to load Metro-North stations. Make sure the API is running and data has been downloaded.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="relative" style={{ height }}>
            {loading && (
                <div className="absolute inset-0 bg-gray-100 flex items-center justify-center z-10">
                    <div className="text-center">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-westchester-green-600 mx-auto mb-4"></div>
                        <p className="text-gray-600">Loading map data...</p>
                    </div>
                </div>
            )}

            {error && (
                <div className="absolute top-4 left-1/2 transform -translate-x-1/2 z-20 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded max-w-md">
                    <p className="font-bold">Error</p>
                    <p className="text-sm">{error}</p>
                </div>
            )}

            <MapContainer
                center={WESTCHESTER_CENTER}
                zoom={DEFAULT_ZOOM}
                style={{ height: '100%', width: '100%' }}
                className="rounded-lg shadow-lg"
            >
                <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />

                {showStations && stations.map((station) => (
                    <Marker
                        key={station.id}
                        position={[station.latitude, station.longitude]}
                    >
                        <Popup>
                            <div className="p-2">
                                <h3 className="font-bold text-lg mb-2">{station.name}</h3>
                                <div className="text-sm space-y-1">
                                    <p><strong>Station ID:</strong> {station.id}</p>
                                    {station.code && <p><strong>Code:</strong> {station.code}</p>}
                                    <p><strong>County:</strong> {station.county}</p>
                                    <p>
                                        <strong>Wheelchair Accessible:</strong>{' '}
                                        {station.wheelchair_accessible ? (
                                            <span className="text-green-600">✓ Yes</span>
                                        ) : (
                                            <span className="text-red-600">✗ No</span>
                                        )}
                                    </p>
                                    <p className="text-gray-600 text-xs mt-2">
                                        Lat: {station.latitude.toFixed(4)}, Lon: {station.longitude.toFixed(4)}
                                    </p>
                                </div>
                            </div>
                        </Popup>
                    </Marker>
                ))}
            </MapContainer>

            {!loading && showStations && (
                <div className="absolute bottom-4 right-4 bg-white px-3 py-2 rounded shadow-lg text-sm z-10">
                    <p className="font-semibold">Metro-North Stations: {stations.length}</p>
                </div>
            )}
        </div>
    );
}

