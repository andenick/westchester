/**
 * Footer Component
 * 
 * Footer with project information and links
 */

export default function Footer() {
    return (
        <footer className="bg-gray-800 text-white mt-auto">
            <div className="container mx-auto px-4 py-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {/* About */}
                    <div>
                        <h3 className="text-lg font-bold mb-2">Westchester County Data Platform</h3>
                        <p className="text-sm text-gray-300">
                            Comprehensive government data analysis, interactive mapping, and visualization tools
                            for Westchester County, New York.
                        </p>
                    </div>

                    {/* Data Sources */}
                    <div>
                        <h3 className="text-lg font-bold mb-2">Data Sources</h3>
                        <ul className="text-sm text-gray-300 space-y-1">
                            <li>• Metro-North Railroad</li>
                            <li>• U.S. Census Bureau</li>
                            <li>• NY State Open Data</li>
                            <li>• Westchester County GIS</li>
                        </ul>
                    </div>

                    {/* Links */}
                    <div>
                        <h3 className="text-lg font-bold mb-2">Quick Links</h3>
                        <ul className="text-sm text-gray-300 space-y-1">
                            <li>
                                <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer" className="hover:text-westchester-green-300">
                                    API Documentation
                                </a>
                            </li>
                            <li>
                                <a href="https://data.westchestergov.com/" target="_blank" rel="noopener noreferrer" className="hover:text-westchester-green-300">
                                    Westchester Open Data
                                </a>
                            </li>
                            <li>
                                <a href="https://www.census.gov/" target="_blank" rel="noopener noreferrer" className="hover:text-westchester-green-300">
                                    Census Bureau
                                </a>
                            </li>
                        </ul>
                    </div>
                </div>

                <div className="border-t border-gray-700 mt-6 pt-4 text-center text-sm text-gray-400">
                    <p>
                        &copy; {new Date().getFullYear()} Westchester County Data Platform. Part of the Arcanum Projects ecosystem.
                    </p>
                    <p className="mt-1">
                        Follows Druck organizational standards.
                    </p>
                </div>
            </div>
        </footer>
    );
}

