/**
 * Enhanced Map Component
 * 
 * Interactive map with multiple data layers, controls, and beautiful styling
 */

import { useEffect, useState } from 'react';
import { MapContainer, TileLayer, GeoJSON, LayersControl } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import apiService from '../../services/api';

// Fix Leaflet default icon issue
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41]
});

L.Marker.prototype.options.icon = DefaultIcon;

interface EnhancedMapComponentProps {
    height?: string;
    defaultLayers?: string[];
}

// Custom markers for different features
const createCustomIcon = (color: string, icon: string) => {
    return L.divIcon({
        className: 'custom-div-icon',
        html: `<div style="background-color: ${color}; width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center; justify-content: center; border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3);">
            <span style="font-size: 16px;">${icon}</span>
        </div>`,
        iconSize: [30, 30],
        iconAnchor: [15, 15]
    });
};

const stationIcon = createCustomIcon('#059669', '🚂');
const amenityIcon = createCustomIcon('#F59E0B', '📍');

export default function EnhancedMapComponent({
    height = '600px',
    defaultLayers = ['stations', 'parks', 'sidewalks', 'bikeLanes', 'busStops']
}: EnhancedMapComponentProps) {
    const [stations, setStations] = useState<any>(null);
    const [parks, setParks] = useState<any>(null);
    const [trails, setTrails] = useState<any>(null);
    const [amenities, setAmenities] = useState<any>(null);
    const [countyBoundary, setCountyBoundary] = useState<any>(null);
    const [sidewalks, setSidewalks] = useState<any>(null);
    const [bikeLanes, setBikeLanes] = useState<any>(null);
    const [busStops, setBusStops] = useState<any>(null);
    const [streetLights, setStreetLights] = useState<any>(null);

    // Sidewalk Coverage Planning Layers
    const [roadsNoCoverage, setRoadsNoCoverage] = useState<any>(null);
    const [roadsOneSide, setRoadsOneSide] = useState<any>(null);
    const [roadsBothSides, setRoadsBothSides] = useState<any>(null);
    const [todBuffers, setTodBuffers] = useState<any>(null);

    const [loading, setLoading] = useState(true);

    // Westchester County center coordinates
    const center: [number, number] = [41.15, -73.75];

    useEffect(() => {
        loadMapData();
    }, []);

    const loadMapData = async () => {
        try {
            setLoading(true);

            // Build list of data to load based on defaultLayers
            const dataPromises: Promise<any>[] = [];
            const dataKeys: string[] = [];

            // Always load boundary
            dataPromises.push(apiService.getCountyBoundary());
            dataKeys.push('boundary');

            // Load standard infrastructure layers
            if (defaultLayers.includes('stations')) {
                dataPromises.push(apiService.getTransitStations());
                dataKeys.push('stations');
            }
            if (defaultLayers.includes('parks')) {
                dataPromises.push(apiService.getParks());
                dataKeys.push('parks');
            }
            if (defaultLayers.includes('trails')) {
                dataPromises.push(apiService.getTrails());
                dataKeys.push('trails');
            }
            if (defaultLayers.includes('amenities')) {
                dataPromises.push(apiService.getAmenities());
                dataKeys.push('amenities');
            }
            if (defaultLayers.includes('sidewalks')) {
                dataPromises.push(apiService.getSidewalks());
                dataKeys.push('sidewalks');
            }
            if (defaultLayers.includes('bikeLanes')) {
                dataPromises.push(apiService.getBikeLanes());
                dataKeys.push('bikeLanes');
            }
            if (defaultLayers.includes('busStops')) {
                dataPromises.push(apiService.getBusStops());
                dataKeys.push('busStops');
            }
            if (defaultLayers.includes('streetLights')) {
                dataPromises.push(apiService.getStreetLights());
                dataKeys.push('streetLights');
            }

            // Load sidewalk planning layers if requested
            if (defaultLayers.includes('roadsNoCoverage')) {
                dataPromises.push(apiService.getRoadsNoCoverage());
                dataKeys.push('roadsNoCoverage');
            }
            if (defaultLayers.includes('roadsOneSide')) {
                dataPromises.push(apiService.getRoadsOneSide());
                dataKeys.push('roadsOneSide');
            }
            if (defaultLayers.includes('roadsBothSides')) {
                dataPromises.push(apiService.getRoadsBothSides());
                dataKeys.push('roadsBothSides');
            }
            if (defaultLayers.includes('todBuffers')) {
                dataPromises.push(apiService.getTODBuffers());
                dataKeys.push('todBuffers');
            }

            // Load all data in parallel
            const results = await Promise.allSettled(dataPromises);

            // Set state for each loaded layer
            results.forEach((result, index) => {
                if (result.status === 'fulfilled') {
                    const key = dataKeys[index];
                    switch (key) {
                        case 'boundary': setCountyBoundary(result.value); break;
                        case 'stations': setStations(result.value); break;
                        case 'parks': setParks(result.value); break;
                        case 'trails': setTrails(result.value); break;
                        case 'amenities': setAmenities(result.value); break;
                        case 'sidewalks': setSidewalks(result.value); break;
                        case 'bikeLanes': setBikeLanes(result.value); break;
                        case 'busStops': setBusStops(result.value); break;
                        case 'streetLights': setStreetLights(result.value); break;
                        case 'roadsNoCoverage': setRoadsNoCoverage(result.value); break;
                        case 'roadsOneSide': setRoadsOneSide(result.value); break;
                        case 'roadsBothSides': setRoadsBothSides(result.value); break;
                        case 'todBuffers': setTodBuffers(result.value); break;
                    }
                }
            });

        } catch (error) {
            console.error('Error loading map data:', error);
        } finally {
            setLoading(false);
        }
    };

    // Style functions for different layers
    const parkStyle = {
        fillColor: '#10B981',
        fillOpacity: 0.3,
        color: '#059669',
        weight: 2
    };

    const trailStyle = {
        color: '#3B82F6',
        weight: 3,
        opacity: 0.7
    };

    // County boundary style - prominent outline
    const countyBoundaryStyle = {
        color: '#059669',        // Green
        weight: 4,               // Bold line
        opacity: 1,
        fillColor: '#059669',
        fillOpacity: 0.05,       // Very transparent fill
        dashArray: '10, 5'       // Dashed pattern
    };

    // Infrastructure styles
    const sidewalkStyle = {
        color: '#D97706',        // Orange/brown
        weight: 2,
        opacity: 0.6
    };

    const bikeLaneStyle = {
        color: '#10B981',        // Green
        weight: 3,
        opacity: 0.8
    };

    const busStopStyle = {
        color: '#3B82F6',        // Blue
        weight: 2,
        opacity: 0.8,
        radius: 4
    };

    const streetLightStyle = {
        color: '#F59E0B',        // Amber/yellow
        weight: 2,
        opacity: 0.7,
        radius: 3
    };

    // Sidewalk Coverage Planning Layer Styles
    const noCoverageStyle = {
        color: '#DC2626',        // Red - HIGH priority
        weight: 3,
        opacity: 0.8
    };

    const oneSideStyle = {
        color: '#F59E0B',        // Orange - MEDIUM priority
        weight: 3,
        opacity: 0.8
    };

    const bothSidesStyle = {
        color: '#10B981',        // Green - Adequate coverage
        weight: 3,
        opacity: 0.8
    };

    const todBufferStyle = {
        fillColor: '#9333EA',    // Purple
        fillOpacity: 0.1,
        color: '#9333EA',
        weight: 2,
        opacity: 0.6
    };

    if (loading) {
        return (
            <div style={{ height, display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: '#f3f4f6' }}>
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto mb-4"></div>
                    <p className="text-gray-600">Loading map data...</p>
                </div>
            </div>
        );
    }

    return (
        <div style={{ height, position: 'relative' }}>
            <MapContainer
                center={center}
                zoom={11}
                style={{ height: '100%', width: '100%' }}
                scrollWheelZoom={true}
            >
                <LayersControl position="topright">
                    {/* Base Map Options */}
                    <LayersControl.BaseLayer checked name="Street Map">
                        <TileLayer
                            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                        />
                    </LayersControl.BaseLayer>

                    <LayersControl.BaseLayer name="Satellite">
                        <TileLayer
                            attribution='&copy; <a href="https://www.esri.com/">Esri</a>'
                            url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
                        />
                    </LayersControl.BaseLayer>

                    <LayersControl.BaseLayer name="Terrain">
                        <TileLayer
                            attribution='&copy; <a href="https://www.opentopomap.org/">OpenTopoMap</a>'
                            url="https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png"
                        />
                    </LayersControl.BaseLayer>
                </LayersControl>

                {/* County Boundary - Always visible, not in layer control, NON-INTERACTIVE */}
                {countyBoundary && (
                    <GeoJSON
                        data={countyBoundary}
                        style={countyBoundaryStyle}
                        interactive={false}
                        bubblingMouseEvents={false}
                    />
                )}

                <LayersControl position="topright">
                    {/* Data Layers */}
                    {stations && (
                        <LayersControl.Overlay checked={defaultLayers.includes('stations')} name="🚂 Metro-North Stations">
                            <GeoJSON
                                data={stations}
                                pointToLayer={(_feature, latlng) => {
                                    return L.marker(latlng, { icon: stationIcon });
                                }}
                                onEachFeature={(_feature, layer) => {
                                    if (_feature.properties) {
                                        const props = _feature.properties;
                                        layer.bindPopup(`
                                            <div style="font-family: system-ui;">
                                                <h3 style="font-weight: bold; margin-bottom: 8px; color: #059669;">🚂 ${props.name || 'Station'}</h3>
                                                <p style="margin: 4px 0;"><strong>ID:</strong> ${props.id || 'N/A'}</p>
                                                <p style="margin: 4px 0;"><strong>Code:</strong> ${props.code || 'N/A'}</p>
                                                <p style="margin: 4px 0;"><strong>Accessible:</strong> ${props.wheelchair_accessible ? '✓ Yes' : '✗ No'}</p>
                                            </div>
                                        `);
                                    }
                                }}
                            />
                        </LayersControl.Overlay>
                    )}

                    {parks && (
                        <LayersControl.Overlay checked={defaultLayers.includes('parks')} name="🏞️ Parks & Recreation">
                            <GeoJSON
                                data={parks}
                                style={parkStyle}
                                onEachFeature={(feature, layer) => {
                                    if (feature.properties) {
                                        const props = feature.properties;
                                        layer.bindPopup(`
                                            <div style="font-family: system-ui;">
                                                <h3 style="font-weight: bold; margin-bottom: 8px; color: #10B981;">🏞️ ${props.name || 'Park'}</h3>
                                                <p style="margin: 4px 0;"><strong>Type:</strong> ${props.leisure || props.landuse || 'Park'}</p>
                                                <p style="margin: 4px 0; font-size: 12px; color: #6B7280;">Source: OpenStreetMap</p>
                                            </div>
                                        `);
                                    }
                                }}
                            />
                        </LayersControl.Overlay>
                    )}

                    {trails && (
                        <LayersControl.Overlay checked={defaultLayers.includes('trails')} name="🚶 Trails & Bike Paths">
                            <GeoJSON
                                data={trails}
                                style={trailStyle}
                                onEachFeature={(feature, layer) => {
                                    if (feature.properties) {
                                        const props = feature.properties;
                                        layer.bindPopup(`
                                            <div style="font-family: system-ui;">
                                                <h3 style="font-weight: bold; margin-bottom: 8px; color: #3B82F6;">🚶 ${props.name || 'Trail'}</h3>
                                                <p style="margin: 4px 0;"><strong>Type:</strong> ${props.highway || 'Trail'}</p>
                                                ${props.surface ? `<p style="margin: 4px 0;"><strong>Surface:</strong> ${props.surface}</p>` : ''}
                                                <p style="margin: 4px 0; font-size: 12px; color: #6B7280;">Source: OpenStreetMap</p>
                                            </div>
                                        `);
                                    }
                                }}
                            />
                        </LayersControl.Overlay>
                    )}

                    {amenities && (
                        <LayersControl.Overlay checked={defaultLayers.includes('amenities')} name="📍 Public Amenities">
                            <GeoJSON
                                data={amenities}
                                pointToLayer={(_feature, latlng) => {
                                    return L.marker(latlng, { icon: amenityIcon });
                                }}
                                onEachFeature={(_feature, layer) => {
                                    if (_feature.properties) {
                                        const props = _feature.properties;
                                        layer.bindPopup(`
                                            <div style="font-family: system-ui;">
                                                <h3 style="font-weight: bold; margin-bottom: 8px; color: #F59E0B;">📍 ${props.name || 'Amenity'}</h3>
                                                <p style="margin: 4px 0;"><strong>Type:</strong> ${props.amenity || props.tourism || 'Amenity'}</p>
                                                <p style="margin: 4px 0; font-size: 12px; color: #6B7280;">Source: OpenStreetMap</p>
                                            </div>
                                        `);
                                    }
                                }}
                            />
                        </LayersControl.Overlay>
                    )}

                    {/* Infrastructure Layers */}
                    {sidewalks && (
                        <LayersControl.Overlay checked={defaultLayers.includes('sidewalks')} name="🚶 Sidewalks">
                            <GeoJSON
                                data={sidewalks}
                                style={sidewalkStyle}
                                onEachFeature={(_feature, layer) => {
                                    if (_feature.properties) {
                                        const props = _feature.properties;
                                        layer.bindPopup(`
                                            <div style="font-family: system-ui;">
                                                <h3 style="font-weight: bold; margin-bottom: 8px; color: #D97706;">🚶 ${props.name || 'Sidewalk'}</h3>
                                                <p style="margin: 4px 0;"><strong>Type:</strong> ${props.highway || 'Sidewalk'}</p>
                                                ${props.surface ? `<p style="margin: 4px 0;"><strong>Surface:</strong> ${props.surface}</p>` : ''}
                                                <p style="margin: 4px 0; font-size: 12px; color: #6B7280;">Source: OpenStreetMap</p>
                                            </div>
                                        `);
                                    }
                                }}
                            />
                        </LayersControl.Overlay>
                    )}

                    {bikeLanes && (
                        <LayersControl.Overlay checked={defaultLayers.includes('bikeLanes')} name="🚴 Bike Lanes">
                            <GeoJSON
                                data={bikeLanes}
                                style={bikeLaneStyle}
                                onEachFeature={(_feature, layer) => {
                                    if (_feature.properties) {
                                        const props = _feature.properties;
                                        layer.bindPopup(`
                                            <div style="font-family: system-ui;">
                                                <h3 style="font-weight: bold; margin-bottom: 8px; color: #10B981;">🚴 ${props.name || 'Bike Lane'}</h3>
                                                <p style="margin: 4px 0;"><strong>Type:</strong> ${props.highway || 'Bike Lane'}</p>
                                                ${props.cycleway ? `<p style="margin: 4px 0;"><strong>Cycleway:</strong> ${props.cycleway}</p>` : ''}
                                                <p style="margin: 4px 0; font-size: 12px; color: #6B7280;">Source: OpenStreetMap</p>
                                            </div>
                                        `);
                                    }
                                }}
                            />
                        </LayersControl.Overlay>
                    )}

                    {busStops && (
                        <LayersControl.Overlay checked={defaultLayers.includes('busStops')} name="🚌 Bus Stops">
                            <GeoJSON
                                data={busStops}
                                pointToLayer={(_feature, latlng) => {
                                    return L.circleMarker(latlng, {
                                        radius: busStopStyle.radius,
                                        fillColor: busStopStyle.color,
                                        color: busStopStyle.color,
                                        weight: busStopStyle.weight,
                                        opacity: busStopStyle.opacity,
                                        fillOpacity: 0.7
                                    });
                                }}
                                onEachFeature={(_feature, layer) => {
                                    if (_feature.properties) {
                                        const props = _feature.properties;
                                        layer.bindPopup(`
                                            <div style="font-family: system-ui;">
                                                <h3 style="font-weight: bold; margin-bottom: 8px; color: #3B82F6;">🚌 ${props.name || 'Bus Stop'}</h3>
                                                <p style="margin: 4px 0;"><strong>Type:</strong> ${props.amenity || props.highway || 'Bus Stop'}</p>
                                                <p style="margin: 4px 0; font-size: 12px; color: #6B7280;">Source: OpenStreetMap</p>
                                            </div>
                                        `);
                                    }
                                }}
                            />
                        </LayersControl.Overlay>
                    )}

                    {streetLights && (
                        <LayersControl.Overlay checked={defaultLayers.includes('streetLights')} name="💡 Street Lights">
                            <GeoJSON
                                data={streetLights}
                                pointToLayer={(_feature, latlng) => {
                                    return L.circleMarker(latlng, {
                                        radius: streetLightStyle.radius,
                                        fillColor: streetLightStyle.color,
                                        color: streetLightStyle.color,
                                        weight: streetLightStyle.weight,
                                        opacity: streetLightStyle.opacity,
                                        fillOpacity: 0.7
                                    });
                                }}
                                onEachFeature={(_feature, layer) => {
                                    if (_feature.properties) {
                                        const props = _feature.properties;
                                        layer.bindPopup(`
                                            <div style="font-family: system-ui;">
                                                <h3 style="font-weight: bold; margin-bottom: 8px; color: #F59E0B;">💡 ${props.name || 'Street Light'}</h3>
                                                <p style="margin: 4px 0;"><strong>Type:</strong> ${props.amenity || props.highway || 'Street Light'}</p>
                                                <p style="margin: 4px 0; font-size: 12px; color: #6B7280;">Source: OpenStreetMap</p>
                                            </div>
                                        `);
                                    }
                                }}
                            />
                        </LayersControl.Overlay>
                    )}

                    {/* Sidewalk Coverage Planning Layers */}
                    {todBuffers && (
                        <LayersControl.Overlay checked={defaultLayers.includes('todBuffers')} name="🟣 TOD Buffer Zones">
                            <GeoJSON
                                data={todBuffers}
                                style={todBufferStyle}
                                onEachFeature={(_feature, layer) => {
                                    if (_feature.properties) {
                                        const props = _feature.properties;
                                        layer.bindPopup(`
                                            <div style="font-family: system-ui;">
                                                <h3 style="font-weight: bold; margin-bottom: 8px; color: #9333EA;">🟣 TOD Buffer Zone</h3>
                                                <p style="margin: 4px 0;"><strong>Station:</strong> ${props.station_name || 'N/A'}</p>
                                                <p style="margin: 4px 0;"><strong>Buffer:</strong> 0.5 miles (2,640 feet)</p>
                                                <p style="margin: 4px 0; font-size: 12px; color: #6B7280;">Transit-Oriented Development Area</p>
                                            </div>
                                        `);
                                    }
                                }}
                            />
                        </LayersControl.Overlay>
                    )}

                    {roadsNoCoverage && (
                        <LayersControl.Overlay checked={defaultLayers.includes('roadsNoCoverage')} name="🔴 No Sidewalk Coverage">
                            <GeoJSON
                                data={roadsNoCoverage}
                                style={noCoverageStyle}
                                onEachFeature={(_feature, layer) => {
                                    if (_feature.properties) {
                                        const props = _feature.properties;
                                        layer.bindPopup(`
                                            <div style="font-family: system-ui;">
                                                <h3 style="font-weight: bold; margin-bottom: 8px; color: #DC2626;">🔴 ${props.STREETNAME || 'Road'}</h3>
                                                <p style="margin: 4px 0;"><strong>Coverage:</strong> No sidewalks</p>
                                                <p style="margin: 4px 0;"><strong>Priority:</strong> <span style="color: #DC2626; font-weight: bold;">TIER 1 - HIGH</span></p>
                                                <p style="margin: 4px 0;"><strong>Road Type:</strong> ${props.TYPE || 'N/A'}</p>
                                                ${props.in_tod_area ? '<p style="margin: 4px 0;"><strong>Location:</strong> Within TOD area</p>' : ''}
                                                <p style="margin: 4px 0; font-size: 12px; color: #6B7280;">DVRPC Analysis - Westchester County</p>
                                            </div>
                                        `);
                                    }
                                }}
                            />
                        </LayersControl.Overlay>
                    )}

                    {roadsOneSide && (
                        <LayersControl.Overlay checked={defaultLayers.includes('roadsOneSide')} name="🟠 One-Side Coverage">
                            <GeoJSON
                                data={roadsOneSide}
                                style={oneSideStyle}
                                onEachFeature={(_feature, layer) => {
                                    if (_feature.properties) {
                                        const props = _feature.properties;
                                        layer.bindPopup(`
                                            <div style="font-family: system-ui;">
                                                <h3 style="font-weight: bold; margin-bottom: 8px; color: #F59E0B;">🟠 ${props.STREETNAME || 'Road'}</h3>
                                                <p style="margin: 4px 0;"><strong>Coverage:</strong> One side only</p>
                                                <p style="margin: 4px 0;"><strong>Priority:</strong> <span style="color: #F59E0B; font-weight: bold;">TIER 2 - MEDIUM</span></p>
                                                <p style="margin: 4px 0;"><strong>Road Type:</strong> ${props.TYPE || 'N/A'}</p>
                                                ${props.in_tod_area ? '<p style="margin: 4px 0;"><strong>Location:</strong> Within TOD area</p>' : ''}
                                                <p style="margin: 4px 0; font-size: 12px; color: #6B7280;">DVRPC Analysis - Westchester County</p>
                                            </div>
                                        `);
                                    }
                                }}
                            />
                        </LayersControl.Overlay>
                    )}

                    {roadsBothSides && (
                        <LayersControl.Overlay checked={defaultLayers.includes('roadsBothSides')} name="🟢 Both-Sides Coverage">
                            <GeoJSON
                                data={roadsBothSides}
                                style={bothSidesStyle}
                                onEachFeature={(_feature, layer) => {
                                    if (_feature.properties) {
                                        const props = _feature.properties;
                                        layer.bindPopup(`
                                            <div style="font-family: system-ui;">
                                                <h3 style="font-weight: bold; margin-bottom: 8px; color: #10B981;">🟢 ${props.STREETNAME || 'Road'}</h3>
                                                <p style="margin: 4px 0;"><strong>Coverage:</strong> Both sides</p>
                                                <p style="margin: 4px 0;"><strong>Status:</strong> <span style="color: #10B981; font-weight: bold;">ADEQUATE</span></p>
                                                <p style="margin: 4px 0;"><strong>Road Type:</strong> ${props.TYPE || 'N/A'}</p>
                                                ${props.in_tod_area ? '<p style="margin: 4px 0;"><strong>Location:</strong> Within TOD area</p>' : ''}
                                                <p style="margin: 4px 0; font-size: 12px; color: #6B7280;">DVRPC Analysis - Westchester County</p>
                                            </div>
                                        `);
                                    }
                                }}
                            />
                        </LayersControl.Overlay>
                    )}
                </LayersControl>

                {/* Map Legend */}
                <div style={{
                    position: 'absolute',
                    bottom: '20px',
                    left: '10px',
                    backgroundColor: 'white',
                    padding: '12px',
                    borderRadius: '8px',
                    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
                    zIndex: 1000,
                    fontSize: '12px'
                }}>
                    <div style={{ fontWeight: 'bold', marginBottom: '8px' }}>Legend</div>
                    <div style={{ display: 'flex', alignItems: 'center', marginBottom: '4px' }}>
                        <span style={{ marginRight: '8px' }}>🚂</span>
                        <span>Metro-North Stations ({stations?.features?.length || 0})</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', marginBottom: '4px' }}>
                        <span style={{ marginRight: '8px' }}>🏞️</span>
                        <span>Parks ({parks?.features?.length || 0})</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', marginBottom: '4px' }}>
                        <span style={{ marginRight: '8px' }}>🚶</span>
                        <span>Trails ({trails?.features?.length || 0})</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', marginBottom: '4px' }}>
                        <span style={{ marginRight: '8px' }}>📍</span>
                        <span>Amenities ({amenities?.features?.length || 0})</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', marginBottom: '4px' }}>
                        <span style={{ marginRight: '8px', color: '#D97706' }}>━</span>
                        <span>Sidewalks ({sidewalks?.features?.length?.toLocaleString() || 0})</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', marginBottom: '4px' }}>
                        <span style={{ marginRight: '8px', color: '#10B981' }}>━</span>
                        <span>Bike Lanes ({bikeLanes?.features?.length?.toLocaleString() || 0})</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', marginBottom: '4px' }}>
                        <span style={{ marginRight: '8px', color: '#3B82F6' }}>●</span>
                        <span>Bus Stops ({busStops?.features?.length?.toLocaleString() || 0})</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center' }}>
                        <span style={{ marginRight: '8px', color: '#F59E0B' }}>●</span>
                        <span>Street Lights ({streetLights?.features?.length?.toLocaleString() || 0})</span>
                    </div>
                    <div style={{ marginTop: '8px', paddingTop: '8px', borderTop: '1px solid #E5E7EB', fontSize: '10px', color: '#6B7280' }}>
                        <em>Note: Infrastructure data from OpenStreetMap may vary by municipality</em>
                    </div>
                </div>
            </MapContainer>
        </div>
    );
}

