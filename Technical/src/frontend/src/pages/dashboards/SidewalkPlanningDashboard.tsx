import { useState, useEffect } from 'react';
import SidewalkCoverageMap from '../../components/map/SidewalkCoverageMap';

interface SidewalkStats {
  version: string;
  validation_accuracy: string;
  total_roads: number;
  total_road_miles: number;
  coverage_counts: { none: number; one_side: number; both_sides: number };
  coverage_percentages: { none: number; one_side: number; both_sides: number };
  coverage_miles: { none: number; one_side: number; both_sides: number };
  methodology: {
    buffer_distance_ft: number;
    detection_threshold_pct: number;
    sampling_interval_ft: number;
    source_roads: string;
    source_sidewalks: string;
    approach: string;
  };
}

interface CoverageFilters {
  none: boolean;
  one_side: boolean;
  both_sides: boolean;
}

const SidewalkPlanningDashboard = () => {
  const [stats, setStats] = useState<SidewalkStats | null>(null);
  const [filters, setFilters] = useState<CoverageFilters>({
    none: true,
    one_side: true,
    both_sides: true,
  });
  const [methodologyOpen, setMethodologyOpen] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  useEffect(() => {
    fetch('/data/sidewalk_stats_v5.3.json')
      .then((r) => r.json())
      .then(setStats)
      .catch((err) => console.error('Failed to load stats:', err));
  }, []);

  const toggleFilter = (key: keyof CoverageFilters) => {
    setFilters((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  return (
    <div className="flex flex-col" style={{ height: 'calc(100vh - 64px)' }}>
      {/* Top Bar */}
      <div className="bg-white border-b px-4 py-3 flex items-center justify-between flex-shrink-0">
        <div>
          <h1 className="text-xl font-bold text-gray-900">
            Westchester County Sidewalk Coverage
          </h1>
          <p className="text-sm text-gray-500">
            DVRPC-Inspired Analysis &middot; v5.3 &middot; 100% Validation Accuracy (17/17)
          </p>
        </div>
        <div className="flex items-center gap-3">
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
            v5.3 Validated
          </span>
          <button
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
            className="text-gray-500 hover:text-gray-700 p-1.5 rounded hover:bg-gray-100"
            title={sidebarCollapsed ? 'Show sidebar' : 'Hide sidebar'}
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d={sidebarCollapsed ? 'M4 6h16M4 12h16M4 18h16' : 'M11 19l-7-7 7-7m8 14l-7-7 7-7'}
              />
            </svg>
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        {!sidebarCollapsed && (
          <div className="w-72 bg-white border-r overflow-y-auto flex-shrink-0">
            {/* Stats */}
            {stats && (
              <div className="p-4 space-y-4">
                {/* Summary */}
                <div>
                  <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">
                    Summary
                  </h2>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Total Roads</span>
                      <span className="font-semibold">{stats.total_roads.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Total Miles</span>
                      <span className="font-semibold">{stats.total_road_miles.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Any Coverage</span>
                      <span className="font-semibold text-green-700">
                        {(stats.coverage_percentages.one_side + stats.coverage_percentages.both_sides).toFixed(1)}%
                      </span>
                    </div>
                  </div>
                </div>

                <hr />

                {/* Coverage Breakdown */}
                <div>
                  <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">
                    Coverage
                  </h2>

                  {/* No Coverage */}
                  <div className="mb-3">
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-sm" style={{ backgroundColor: '#DC2626' }} />
                        <span className="text-sm font-medium">No Sidewalk</span>
                      </div>
                      <span className="text-sm font-bold text-red-600">
                        {stats.coverage_percentages.none}%
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-red-500 h-2 rounded-full"
                        style={{ width: `${stats.coverage_percentages.none}%` }}
                      />
                    </div>
                    <div className="flex justify-between text-xs text-gray-500 mt-1">
                      <span>{stats.coverage_counts.none.toLocaleString()} roads</span>
                      <span>{stats.coverage_miles.none.toLocaleString()} mi</span>
                    </div>
                  </div>

                  {/* One Side */}
                  <div className="mb-3">
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-sm" style={{ backgroundColor: '#F59E0B' }} />
                        <span className="text-sm font-medium">One Side</span>
                      </div>
                      <span className="text-sm font-bold text-amber-600">
                        {stats.coverage_percentages.one_side}%
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-amber-500 h-2 rounded-full"
                        style={{ width: `${stats.coverage_percentages.one_side}%` }}
                      />
                    </div>
                    <div className="flex justify-between text-xs text-gray-500 mt-1">
                      <span>{stats.coverage_counts.one_side.toLocaleString()} roads</span>
                      <span>{stats.coverage_miles.one_side.toLocaleString()} mi</span>
                    </div>
                  </div>

                  {/* Both Sides */}
                  <div className="mb-3">
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-sm" style={{ backgroundColor: '#10B981' }} />
                        <span className="text-sm font-medium">Both Sides</span>
                      </div>
                      <span className="text-sm font-bold text-green-600">
                        {stats.coverage_percentages.both_sides}%
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-green-500 h-2 rounded-full"
                        style={{ width: `${stats.coverage_percentages.both_sides}%` }}
                      />
                    </div>
                    <div className="flex justify-between text-xs text-gray-500 mt-1">
                      <span>{stats.coverage_counts.both_sides.toLocaleString()} roads</span>
                      <span>{stats.coverage_miles.both_sides.toLocaleString()} mi</span>
                    </div>
                  </div>
                </div>

                <hr />

                {/* Filters */}
                <div>
                  <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">
                    Filters
                  </h2>
                  <div className="space-y-2">
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={filters.none}
                        onChange={() => toggleFilter('none')}
                        className="rounded border-gray-300 text-red-600 focus:ring-red-500"
                      />
                      <div className="w-3 h-0.5" style={{ backgroundColor: '#DC2626' }} />
                      <span className="text-sm">No Sidewalk</span>
                    </label>
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={filters.one_side}
                        onChange={() => toggleFilter('one_side')}
                        className="rounded border-gray-300 text-amber-600 focus:ring-amber-500"
                      />
                      <div className="w-3 h-0.5" style={{ backgroundColor: '#F59E0B' }} />
                      <span className="text-sm">One Side</span>
                    </label>
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={filters.both_sides}
                        onChange={() => toggleFilter('both_sides')}
                        className="rounded border-gray-300 text-green-600 focus:ring-green-500"
                      />
                      <div className="w-3 h-0.5" style={{ backgroundColor: '#10B981' }} />
                      <span className="text-sm">Both Sides</span>
                    </label>
                  </div>
                </div>

                <hr />

                {/* Methodology */}
                <div>
                  <button
                    onClick={() => setMethodologyOpen(!methodologyOpen)}
                    className="flex items-center justify-between w-full text-sm font-semibold text-gray-500 uppercase tracking-wider"
                  >
                    <span>Methodology</span>
                    <svg
                      className={`w-4 h-4 transform transition-transform ${methodologyOpen ? 'rotate-180' : ''}`}
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>
                  {methodologyOpen && (
                    <div className="mt-3 space-y-2 text-xs text-gray-600">
                      <p>
                        <span className="font-semibold text-gray-700">Approach:</span>{' '}
                        {stats.methodology.approach}
                      </p>
                      <p>
                        <span className="font-semibold text-gray-700">Buffer:</span>{' '}
                        {stats.methodology.buffer_distance_ft} ft perpendicular
                      </p>
                      <p>
                        <span className="font-semibold text-gray-700">Threshold:</span>{' '}
                        {(stats.methodology.detection_threshold_pct * 100).toFixed(0)}% detection
                      </p>
                      <p>
                        <span className="font-semibold text-gray-700">Sampling:</span> Every{' '}
                        {stats.methodology.sampling_interval_ft} ft along centerline
                      </p>
                      <p>
                        <span className="font-semibold text-gray-700">Roads:</span>{' '}
                        {stats.methodology.source_roads}
                      </p>
                      <p>
                        <span className="font-semibold text-gray-700">Sidewalks:</span>{' '}
                        {stats.methodology.source_sidewalks}
                      </p>
                      <p>
                        <span className="font-semibold text-gray-700">Validation:</span>{' '}
                        {stats.validation_accuracy}
                      </p>
                    </div>
                  )}
                </div>

                <hr />

                {/* Download */}
                <div>
                  <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">
                    Download
                  </h2>
                  <a
                    href="/data/sidewalk_coverage_v5.3.geojson"
                    download
                    className="block w-full text-center text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium py-2 px-3 rounded transition-colors"
                  >
                    GeoJSON (18 MB)
                  </a>
                </div>
              </div>
            )}

            {!stats && (
              <div className="p-4 text-sm text-gray-500">Loading statistics...</div>
            )}
          </div>
        )}

        {/* Map Area */}
        <div className="flex-1 relative">
          <SidewalkCoverageMap height="100%" filters={filters} />

          {/* Legend (bottom-left, on top of map) */}
          <div
            className="absolute bottom-4 left-4 bg-white rounded-lg shadow-lg px-3 py-2 z-[1000] text-xs"
            style={{ pointerEvents: 'auto' }}
          >
            <div className="font-semibold mb-1.5 text-gray-700">Legend</div>
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <div className="w-5 h-0.5" style={{ backgroundColor: '#DC2626' }} />
                <span>No Sidewalk ({stats?.coverage_percentages.none ?? '...'}%)</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-5 h-0.5" style={{ backgroundColor: '#F59E0B' }} />
                <span>One Side ({stats?.coverage_percentages.one_side ?? '...'}%)</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-5 h-0.5" style={{ backgroundColor: '#10B981' }} />
                <span>Both Sides ({stats?.coverage_percentages.both_sides ?? '...'}%)</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SidewalkPlanningDashboard;
