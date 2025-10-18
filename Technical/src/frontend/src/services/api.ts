/**
 * API Service for Westchester County Data Platform
 * 
 * Handles all HTTP requests to the FastAPI backend
 */

import axios from 'axios';
import type { AxiosInstance } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class APIService {
    private client: AxiosInstance;

    constructor() {
        this.client = axios.create({
            baseURL: API_BASE_URL,
            headers: {
                'Content-Type': 'application/json',
            },
            timeout: 30000, // 30 seconds
        });
    }

    /**
     * Get API health status
     */
    async getHealth() {
        const response = await this.client.get('/api/health');
        return response.data;
    }

    /**
     * Get summary statistics
     */
    async getStats() {
        const response = await this.client.get('/api/stats');
        return response.data;
    }

    /**
     * Get Metro-North stations in Westchester County
     */
    async getTransitStations() {
        const response = await this.client.get('/api/transit/stations');
        return response.data;
    }

    /**
     * Get county-level demographic data
     */
    async getCountyDemographics(year: number = 2022) {
        const response = await this.client.get('/api/demographics/county', {
            params: { year },
        });
        return response.data;
    }

    /**
     * Get census tract demographic data
     */
    async getTractDemographics(year: number = 2022) {
        const response = await this.client.get('/api/demographics/tracts', {
            params: { year },
        });
        return response.data;
    }

    /**
     * Get municipality demographic data
     */
    async getMunicipalityDemographics(year: number = 2022) {
        const response = await this.client.get('/api/demographics/municipalities', {
            params: { year },
        });
        return response.data;
    }

    /**
     * Get list of municipalities
     */
    async getMunicipalities() {
        const response = await this.client.get('/api/municipalities');
        return response.data;
    }

    /**
     * Get parks and recreation areas
     */
    async getParks() {
        const response = await this.client.get('/api/infrastructure/parks');
        return response.data;
    }

    /**
     * Get trails and bike paths
     */
    async getTrails() {
        const response = await this.client.get('/api/infrastructure/trails');
        return response.data;
    }

    /**
     * Get public amenities
     */
    async getAmenities() {
        const response = await this.client.get('/api/infrastructure/amenities');
        return response.data;
    }

    /**
     * Get platform metadata
     */
    async getMetadata() {
        const response = await this.client.get('/api/metadata');
        return response.data;
    }

    /**
     * Get Westchester County boundary
     */
    async getCountyBoundary() {
        const response = await this.client.get('/api/boundaries/county');
        return response.data;
    }

    /**
     * Get sidewalks and pedestrian infrastructure
     */
    async getSidewalks() {
        const response = await this.client.get('/api/infrastructure/sidewalks');
        return response.data;
    }

    /**
     * Get bike lanes and cycling infrastructure
     */
    async getBikeLanes() {
        const response = await this.client.get('/api/infrastructure/bike-lanes');
        return response.data;
    }

    /**
     * Get bus stops
     */
    async getBusStops() {
        const response = await this.client.get('/api/infrastructure/bus-stops');
        return response.data;
    }

    /**
     * Get street lights
     */
    async getStreetLights() {
        const response = await this.client.get('/api/infrastructure/street-lights');
        return response.data;
    }

    /**
     * Get municipal services (real data from OSM)
     */
    async getMunicipalServices() {
        const response = await this.client.get('/api/services/municipal');
        return response.data;
    }

    /**
     * Get roads with no sidewalk coverage (Priority Tier 1)
     */
    async getRoadsNoCoverage() {
        const response = await this.client.get('/api/planning/roads-no-coverage');
        return response.data;
    }

    /**
     * Get roads with one-side sidewalk coverage (Priority Tier 2)
     */
    async getRoadsOneSide() {
        const response = await this.client.get('/api/planning/roads-one-side');
        return response.data;
    }

    /**
     * Get roads with both-sides sidewalk coverage (Adequate)
     */
    async getRoadsBothSides() {
        const response = await this.client.get('/api/planning/roads-both-sides');
        return response.data;
    }

    /**
     * Get all roads in TOD areas (0.5 miles from Metro-North)
     */
    async getTODAreaRoads() {
        const response = await this.client.get('/api/planning/tod-area-roads');
        return response.data;
    }

    /**
     * Get Metro-North 0.5-mile buffer zones
     */
    async getTODBuffers() {
        const response = await this.client.get('/api/planning/tod-buffers');
        return response.data;
    }

    /**
     * Get comprehensive sidewalk coverage statistics for planning
     */
    async getSidewalkStatistics() {
        const response = await this.client.get('/api/planning/sidewalk-statistics');
        return response.data;
    }
}

// Export singleton instance
const apiService = new APIService();
export default apiService;

