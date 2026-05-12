import { useEffect, useState, useCallback, useRef } from 'react';
import { MapContainer, TileLayer, GeoJSON, LayersControl, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

const WESTCHESTER_CENTER: [number, number] = [41.15, -73.75];
const DEFAULT_ZOOM = 11;

interface CoverageFilters {
  none: boolean;
  one_side: boolean;
  both_sides: boolean;
}

interface SidewalkCoverageMapProps {
  height?: string;
  filters: CoverageFilters;
  onFeatureCount?: (counts: { none: number; one_side: number; both_sides: number }) => void;
}

const COVERAGE_STYLES: Record<string, L.PathOptions> = {
  none: { color: '#DC2626', weight: 2, opacity: 0.8 },
  one_side: { color: '#F59E0B', weight: 2, opacity: 0.8 },
  both_sides: { color: '#10B981', weight: 2, opacity: 0.8 },
};

function formatPct(val: number): string {
  return `${(val * 100).toFixed(0)}%`;
}

function CanvasRendererSetter() {
  const map = useMap();
  useEffect(() => {
    (map.options as any).preferCanvas = true;
  }, [map]);
  return null;
}

export default function SidewalkCoverageMap({
  height = '100%',
  filters,
  onFeatureCount,
}: SidewalkCoverageMapProps) {
  const [geojsonData, setGeojsonData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const geoJsonRef = useRef<L.GeoJSON | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const resp = await fetch('/data/sidewalk_coverage_v5.3.geojson');
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const data = await resp.json();
      setGeojsonData(data);

      if (onFeatureCount && data.features) {
        const counts = { none: 0, one_side: 0, both_sides: 0 };
        for (const f of data.features) {
          const ct = f.properties?.coverage_type as keyof typeof counts;
          if (ct in counts) counts[ct]++;
        }
        onFeatureCount(counts);
      }

      setError(null);
    } catch (err) {
      console.error('Failed to load sidewalk data:', err);
      setError('Failed to load sidewalk coverage data.');
    } finally {
      setLoading(false);
    }
  };

  const featureFilter = useCallback(
    (feature: any): boolean => {
      const ct = feature.properties?.coverage_type;
      if (ct === 'none') return filters.none;
      if (ct === 'one_side') return filters.one_side;
      if (ct === 'both_sides') return filters.both_sides;
      return false;
    },
    [filters]
  );

  const style = useCallback((feature: any): L.PathOptions => {
    const ct = feature?.properties?.coverage_type || 'none';
    return COVERAGE_STYLES[ct] || COVERAGE_STYLES.none;
  }, []);

  const onEachFeature = useCallback((feature: any, layer: L.Layer) => {
    if (!feature.properties) return;
    const p = feature.properties;
    const coverageLabel =
      p.coverage_type === 'both_sides'
        ? 'Both Sides'
        : p.coverage_type === 'one_side'
          ? 'One Side'
          : 'No Sidewalk';
    const color = COVERAGE_STYLES[p.coverage_type]?.color || '#666';
    const lengthFt = typeof p.road_length_ft === 'number' ? p.road_length_ft.toFixed(0) : 'N/A';

    layer.bindPopup(
      `<div style="font-family: system-ui, sans-serif; min-width: 200px;">
        <div style="font-weight: 700; font-size: 14px; color: ${color}; margin-bottom: 8px; border-bottom: 2px solid ${color}; padding-bottom: 4px;">
          ${coverageLabel}
        </div>
        <table style="font-size: 13px; width: 100%; border-collapse: collapse;">
          <tr><td style="padding: 2px 8px 2px 0; color: #6B7280;">Road ID</td><td style="font-weight: 600;">${p.road_id}</td></tr>
          <tr><td style="padding: 2px 8px 2px 0; color: #6B7280;">Left Side</td><td style="font-weight: 600;">${formatPct(p.left_pct)}</td></tr>
          <tr><td style="padding: 2px 8px 2px 0; color: #6B7280;">Right Side</td><td style="font-weight: 600;">${formatPct(p.right_pct)}</td></tr>
          <tr><td style="padding: 2px 8px 2px 0; color: #6B7280;">Length</td><td style="font-weight: 600;">${lengthFt} ft</td></tr>
        </table>
      </div>`,
      { maxWidth: 280 }
    );
  }, []);

  if (loading) {
    return (
      <div
        style={{ height, display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: '#f9fafb' }}
      >
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto mb-4"></div>
          <p className="text-gray-600 text-sm">Loading 60,000+ road segments...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div
        style={{ height, display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: '#fef2f2' }}
      >
        <div className="text-center text-red-700 max-w-md px-4">
          <p className="font-bold text-lg mb-2">Map Data Error</p>
          <p className="text-sm">{error}</p>
          <p className="text-xs mt-2 text-red-500">
            Ensure sidewalk_coverage_v5.3.geojson is in public/data/
          </p>
        </div>
      </div>
    );
  }

  return (
    <div style={{ height, position: 'relative' }}>
      <MapContainer
        center={WESTCHESTER_CENTER}
        zoom={DEFAULT_ZOOM}
        style={{ height: '100%', width: '100%' }}
        scrollWheelZoom={true}
        preferCanvas={true}
      >
        <CanvasRendererSetter />

        <LayersControl position="topright">
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
          <LayersControl.BaseLayer name="Light Gray">
            <TileLayer
              attribution='&copy; <a href="https://cartodb.com/">CartoDB</a>'
              url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
            />
          </LayersControl.BaseLayer>
        </LayersControl>

        {geojsonData && (
          <GeoJSON
            key={`${filters.none}-${filters.one_side}-${filters.both_sides}`}
            data={geojsonData}
            filter={featureFilter}
            style={style}
            onEachFeature={onEachFeature}
            ref={(el) => {
              geoJsonRef.current = el as unknown as L.GeoJSON;
            }}
          />
        )}
      </MapContainer>
    </div>
  );
}
