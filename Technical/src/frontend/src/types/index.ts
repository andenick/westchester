/**
 * TypeScript type definitions for Westchester County Data Platform
 */

// GeoJSON types
export interface GeoJSONFeature {
    type: 'Feature';
    geometry: {
        type: 'Point' | 'Polygon' | 'MultiPolygon' | 'LineString';
        coordinates: number[] | number[][] | number[][][];
    };
    properties: Record<string, any>;
}

export interface GeoJSONFeatureCollection {
    type: 'FeatureCollection';
    features: GeoJSONFeature[];
    metadata?: Record<string, any>;
}

// Transit types
export interface TransitStation {
    name: string;
    id: string;
    code?: string;
    description?: string;
    wheelchair_accessible: boolean;
    county: string;
    state: string;
    latitude: number;
    longitude: number;
}

// Demographics types
export interface DemographicsData {
    location_name: string;
    year: number;
    dataset: string;
    fetched_date: string;

    // Population
    total_population?: number;
    male_population?: number;
    female_population?: number;
    median_age?: number;

    // Race and Ethnicity
    white_alone?: number;
    black_alone?: number;
    asian_alone?: number;
    hispanic_or_latino?: number;

    // Housing
    total_housing_units?: number;
    occupied_housing_units?: number;
    vacant_housing_units?: number;
    median_home_value?: number;
    median_gross_rent?: number;

    // Income
    median_household_income?: number;
    per_capita_income?: number;
    poverty_count?: number;

    // Employment
    in_labor_force?: number;
    civilian_labor_force?: number;
    employed?: number;
    unemployed?: number;

    // Education
    bachelors_degree?: number;
    masters_degree?: number;
    doctorate_degree?: number;

    // Commuting
    total_commuters?: number;
    public_transit_commuters?: number;
    mean_travel_time_to_work?: number;
}

// Municipality types
export interface Municipality {
    name: string;
    type: 'City' | 'Town' | 'Village';
    population?: number;
    demographics?: DemographicsData;
}

// API Response types
export interface APIStats {
    county: string;
    data_sources: Record<string, string>;
    data_availability: Record<string, boolean>;
    generated: string;
}

export interface MunicipalitiesResponse {
    county: string;
    municipality_count: number;
    municipalities: Municipality[];
}

// Map types
export interface MapBounds {
    north: number;
    south: number;
    east: number;
    west: number;
}

// Dashboard types
export interface DashboardCard {
    title: string;
    value: string | number;
    description?: string;
    icon?: React.ReactNode;
    trend?: {
        value: number;
        direction: 'up' | 'down';
    };
}

