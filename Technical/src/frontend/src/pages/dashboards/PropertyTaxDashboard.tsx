/**
 * Property Tax Dashboard
 * 
 * Tax assessment data and geographic analysis
 */

import { TaxAssessmentChart } from '../../components/charts';

export default function PropertyTaxDashboard() {
    // const [loading, setLoading] = useState(false);

    // ⚠️ SAMPLE DATA - REAL DATA REQUIRES MANUAL PDF DOWNLOADS & GIS RE-DOWNLOAD  
    // See: Projects/Westchester/MANUAL_DOWNLOAD_WISHLIST.md
    // Real sources: tax.ny.gov municipal profiles + WCGIS tax parcels (currently corrupted)
    const sampleTaxData = [
        { year: '2018', average_assessment: 450000, median_assessment: 385000 },
        { year: '2019', average_assessment: 465000, median_assessment: 398000 },
        { year: '2020', average_assessment: 482000, median_assessment: 412000 },
        { year: '2021', average_assessment: 510000, median_assessment: 435000 },
        { year: '2022', average_assessment: 548000, median_assessment: 465000 },
    ];

    return (
        <div className="container mx-auto px-4 py-8">
            {/* CRITICAL WARNING - SAMPLE DATA */}
            <div className="bg-red-100 border-4 border-red-600 rounded-lg p-8 mb-8 shadow-2xl">
                <div className="flex items-start">
                    <div className="flex-shrink-0">
                        <span className="text-6xl">⚠️</span>
                    </div>
                    <div className="ml-6 flex-1">
                        <h2 className="text-3xl font-black text-red-900 mb-4">⚠️ SAMPLE DATA ONLY - NOT REAL ⚠️</h2>
                        <p className="text-xl font-bold text-red-800 mb-4">
                            ALL PROPERTY TAX DATA ON THIS PAGE IS DEMONSTRATION/SAMPLE DATA.
                            This is NOT real Westchester County tax information.
                        </p>
                        <div className="bg-white rounded-lg p-4 mb-4">
                            <p className="text-sm font-semibold text-gray-900 mb-2">To get real property tax data:</p>
                            <ul className="list-disc ml-6 text-sm text-gray-800 space-y-1">
                                <li>Re-download Westchester GIS tax parcels (current file corrupted)</li>
                                <li>Download 50 PDF municipal tax profiles from <a href="https://www.tax.ny.gov/research/property/reports.htm" target="_blank" rel="noopener noreferrer" className="text-blue-600 underline font-semibold">tax.ny.gov</a></li>
                                <li>See MANUAL_DOWNLOAD_WISHLIST.md for complete instructions</li>
                            </ul>
                        </div>
                        <p className="text-lg font-bold text-red-900">
                            ⚠️ DO NOT USE THIS DATA FOR DECISION MAKING ⚠️
                        </p>
                    </div>
                </div>
            </div>

            {/* Header */}
            <div className="mb-8">
                <h1 className="text-4xl font-bold text-gray-900 mb-2">Property Tax Dashboard (SAMPLE DATA)</h1>
                <p className="text-gray-600">Tax assessment data and geographic analysis for Westchester County</p>
                <p className="text-red-600 font-bold text-sm mt-2">⚠️ All data below is sample/demonstration data only</p>
            </div>

            {/* Summary Cards */}
            <div className="grid md:grid-cols-4 gap-6 mb-8">
                <StatCard
                    label="Total Parcels"
                    value="350,000+"
                    icon="🏘️"
                />
                <StatCard
                    label="Average Assessment"
                    value="$548,000"
                    icon="💵"
                    trend="+7.4%"
                />
                <StatCard
                    label="Tax Rate (avg)"
                    value="2.85%"
                    icon="📊"
                />
                <StatCard
                    label="Assessment Year"
                    value="2022"
                    icon="📅"
                />
            </div>

            {/* Assessment Trends */}
            <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
                <h2 className="text-2xl font-bold mb-4">Assessment Value Trends (2018-2022)</h2>
                <TaxAssessmentChart data={sampleTaxData} height={400} chartType="area" />
            </div>

            {/* Geographic Distribution */}
            <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
                <h2 className="text-2xl font-bold mb-4">Assessment by Municipality</h2>
                <div className="grid md:grid-cols-3 gap-4">
                    <MunicipalityCard name="Yonkers" avgAssessment={425000} parcels={85000} />
                    <MunicipalityCard name="New Rochelle" avgAssessment={585000} parcels={32000} />
                    <MunicipalityCard name="White Plains" avgAssessment={620000} parcels={28000} />
                    <MunicipalityCard name="Mount Vernon" avgAssessment={395000} parcels={24000} />
                    <MunicipalityCard name="Scarsdale" avgAssessment={1250000} parcels={6500} />
                    <MunicipalityCard name="Rye" avgAssessment={985000} parcels={7200} />
                </div>
            </div>

            {/* Tax Analysis */}
            <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
                <h2 className="text-2xl font-bold mb-4">Tax Rate Analysis</h2>
                <div className="space-y-4">
                    <TaxRateBar municipality="Scarsdale" rate={2.12} isHighlight={false} />
                    <TaxRateBar municipality="Bronxville" rate={2.24} isHighlight={false} />
                    <TaxRateBar municipality="Rye" rate={2.45} isHighlight={false} />
                    <TaxRateBar municipality="White Plains" rate={2.78} isHighlight={true} />
                    <TaxRateBar municipality="New Rochelle" rate={3.12} isHighlight={false} />
                    <TaxRateBar municipality="Yonkers" rate={3.45} isHighlight={false} />
                    <TaxRateBar municipality="Mount Vernon" rate={3.89} isHighlight={false} />
                </div>
            </div>

            {/* Data Source */}
            <div className="mt-4 text-sm text-red-600 font-bold text-center py-4 bg-red-50 rounded">
                ⚠️ REMINDER: ALL DATA ON THIS PAGE IS SAMPLE/DEMONSTRATION DATA - NOT REAL ⚠️
            </div>
        </div>
    );
}

// Helper Components
function StatCard({ label, value, icon, trend }: {
    label: string;
    value: string;
    icon: string;
    trend?: string;
}) {
    return (
        <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center justify-between mb-2">
                <p className="text-sm text-gray-600">{label}</p>
                <span className="text-2xl">{icon}</span>
            </div>
            <p className="text-2xl font-bold">{value}</p>
            {trend && (
                <p className="text-xs text-green-600 mt-1">↗ {trend} from last year</p>
            )}
        </div>
    );
}

function MunicipalityCard({ name, avgAssessment, parcels }: {
    name: string;
    avgAssessment: number;
    parcels: number;
}) {
    return (
        <div className="p-4 bg-gray-50 rounded-lg">
            <h3 className="font-semibold mb-2">{name}</h3>
            <p className="text-sm text-gray-600">Avg Assessment</p>
            <p className="text-xl font-bold text-green-600">${(avgAssessment / 1000).toFixed(0)}k</p>
            <p className="text-xs text-gray-500 mt-2">{parcels.toLocaleString()} parcels</p>
        </div>
    );
}

function TaxRateBar({ municipality, rate, isHighlight }: {
    municipality: string;
    rate: number;
    isHighlight: boolean;
}) {
    const maxRate = 4.0;
    const percentage = (rate / maxRate) * 100;

    return (
        <div>
            <div className="flex justify-between items-center mb-1">
                <span className={`text-sm ${isHighlight ? 'font-semibold' : ''}`}>{municipality}</span>
                <span className="text-sm font-semibold">{rate.toFixed(2)}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                    className={`h-2 rounded-full ${isHighlight ? 'bg-green-600' : 'bg-blue-500'}`}
                    style={{ width: `${percentage}%` }}
                />
            </div>
        </div>
    );
}

