"""
Comprehensive Municipal Services Importer for Westchester County
Collects ALL municipal services and facilities from OpenStreetMap

This advanced importer captures healthcare, education, emergency services,
government buildings, community facilities, and commercial services.
"""

import requests
import json
from pathlib import Path
import logging
from typing import Dict, Any, List
import time

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


class MunicipalServicesImporter:
    """Comprehensive municipal services and facilities importer"""

    def __init__(self, data_dir: Path = None):
        if data_dir is None:
            data_dir = Path("Projects/Westchester/Technical/data/raw/municipal_services")

        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.overpass_url = "http://overpass-api.de/api/interpreter"

        # Westchester County bounding box (expanded for edge coverage)
        self.bbox = "40.7, -74.0, 41.5, -73.3"

        # Service categories with comprehensive queries
        self.service_categories = {
            "healthcare": self.create_healthcare_query,
            "education": self.create_education_query,
            "emergency_services": self.create_emergency_services_query,
            "government": self.create_government_query,
            "community": self.create_community_query,
            "commercial": self.create_commercial_query,
            "transportation": self.create_transportation_query,
            "utilities": self.create_utilities_query,
            "financial": self.create_financial_query,
            "professional": self.create_professional_query
        }

    def create_healthcare_query(self) -> str:
        """Comprehensive healthcare facilities query"""
        return f"""
[out:json][timeout:300];
(
  // Hospitals and medical centers
  node["amenity"="hospital"]({self.bbox});
  node["amenity"="clinic"]({self.bbox});
  node["building"="hospital"]({self.bbox});

  // Emergency services
  node["emergency"="yes"]({self.bbox});
  node["amenity"="doctors"]({self.bbox});
  node["amenity"="dentist"]({self.bbox});
  node["amenity"="pharmacy"]({self.bbox});
  node["shop"="pharmacy"]({self.bbox});

  // Specialized care
  node["amenity"="nursing_home"]({self.bbox});
  node["social_facility"="nursing_home"]({self.bbox});
  node["amenity"="doctors"]["speciality"~"pediatrics|obstetrics|cardiology"]({self.bbox});

  // Mental health
  node["amenity"="social_facility"]({self.bbox});
  node["social_facility"="group_home"]({self.bbox});
  node["amenity"="clinic"]["healthcare"="mental"]({self.bbox});

  // Urgent care
  node["amenity"="urgent_care"]({self.bbox});
  node["healthcare"="urgent"]({self.bbox});

  // Alternative medicine
  node["shop"="herbalist"]({self.bbox});
  node["amenity"="alternative"]({self.bbox});

  // Medical labs
  node["healthcare"="laboratory"]({self.bbox});
  node["shop"="medical_supply"]({self.bbox});

  // Veterinary
  node["amenity"="veterinary"]({self.bbox});

  // Physical therapy
  node["healthcare"="physiotherapy"]({self.bbox});
  node["amenity"="physiotherapy"]({self.bbox});

  // Optometry
  node["shop"="optician"]({self.bbox});
  node["amenity"="optician"]({self.bbox});

  // Blood donation
  node["amenity"="blood_donation"]({self.bbox});

  // Medical imaging
  node["healthcare"="diagnostic_radiology"]({self.bbox});
  node["healthcare"="medical_imaging"]({self.bbox});
);
out geom;
"""

    def create_education_query(self) -> str:
        """Comprehensive educational institutions query"""
        return f"""
[out:json][timeout:300];
(
  // Schools by level
  node["amenity"="school"]({self.bbox});
  node["building"="school"]({self.bbox});
  node["amenity"="kindergarten"]({self.bbox});
  node["amenity"="college"]({self.bbox});
  node["amenity"="university"]({self.bbox});

  // Education levels
  node["education"="primary"]({self.bbox});
  node["education"="secondary"]({self.bbox});
  node["education"="higher"]({self.bbox});
  node["education"="special"]({self.bbox});

  // Private schools
  node["school:type"="private"]({self.bbox});
  node["operator:type"="private"]({self.bbox});

  // Specialized education
  node["amenity"="music_school"]({self.bbox});
  node["amenity"="driving_school"]({self.bbox});
  node["amenity"="language_school"]({self.bbox});
  node["amenity"="cooking_school"]({self.bbox});
  node["amenity"="art_school"]({self.bbox});

  // Libraries
  node["amenity"="library"]({self.bbox});
  node["building"="library"]({self.bbox});

  // Museums and cultural education
  node["tourism"="museum"]({self.bbox});
  node["building"="museum"]({self.bbox});

  // Research centers
  node["amenity"="research_institute"]({self.bbox});
  node["office"="research"]({self.bbox});

  // Tutoring centers
  node["shop"="books"]({self.bbox});
  node["amenity"="prep_school"]({self.bbox});

  // Daycare and preschool
  node["amenity"="childcare"]({self.bbox});
  node["amenity"="daycare"]({self.bbox});
  node["social_facility"="daycare"]({self.bbox});

  // Vocational training
  node["amenity"="training"]({self.bbox});
  node["amenity"="vocational_school"]({self.bbox});

  // Educational support
  node["office"="educational_institution"]({self.bbox});

  // Religious schools
  node["building"="religious_school"]({self.bbox});
  node["amenity"="place_of_worship"]["school"="yes"]({self.bbox});
);
out geom;
"""

    def create_emergency_services_query(self) -> str:
        """Comprehensive emergency services query"""
        return f"""
[out:json][timeout:300];
(
  // Police stations
  node["amenity"="police"]({self.bbox});
  node["building"="police"]({self.bbox});
  node["office"="police"]({self.bbox});

  // Fire stations
  node["amenity"="fire_station"]({self.bbox});
  node["building"="fire_station"]({self.bbox});

  // Emergency medical services
  node["emergency"="ambulance_station"]({self.bbox});
  node["amenity"="ambulance_station"]({self.bbox});
  node["building"="ambulance_station"]({self.bbox});

  // Emergency call boxes
  node["emergency"="phone"]({self.bbox});
  node["amenity"="emergency_phone"]({self.bbox});

  // Rescue services
  node["emergency"="rescue_service"]({self.bbox});
  node["amenity"="rescue_service"]({self.bbox});

  // Coast guard
  node["emergency"="coast_guard"]({self.bbox});
  node["amenity"="coast_guard"]({self.bbox});

  // Civil defense
  node["emergency"="civil_defence"]({self.bbox});
  node["amenity"="civil_defence"]({self.bbox});

  // Lifeguard stations
  node["emergency"="lifeguard"]({self.bbox});
  node["amenity"="lifeguard"]({self.bbox});

  // Mountain rescue
  node["emergency"="mountain_rescue"]({self.bbox});

  // Emergency shelters
  node["emergency"="shelter"]({self.bbox});
  node["amenity"="shelter"]["emergency"="yes"]({self.bbox});

  // Disaster response
  node["emergency"="disaster_response"]({self.bbox});
  node["office"="emergency_management"]({self.bbox});

  // First aid stations
  node["emergency"="first_aid"]({self.bbox});
  node["amenity"="first_aid"]({self.bbox});

  // Search and rescue
  node["emergency"="search_and_rescue"]({self.bbox});

  // Emergency access roads
  way["emergency"="access"]({self.bbox});

  // Emergency vehicle access
  way["emergency"="vehicle"]({self.bbox});

  // Emergency communication
  node["emergency"="communication"]({self.bbox});
  node["communication"="emergency"]({self.bbox});
);
out geom;
"""

    def create_government_query(self) -> str:
        """Comprehensive government facilities query"""
        return f"""
[out:json][timeout:300];
(
  // Government offices
  node["amenity"="townhall"]({self.bbox});
  node["building"="government"]({self.bbox});
  node["office"="government"]({self.bbox});
  node["government"="yes"]({self.bbox});

  // City halls and municipal buildings
  node["building"="civic"]({self.bbox});
  node["amenity"="public_building"]({self.bbox});

  // Courthouses
  node["amenity"="courthouse"]({self.bbox});
  node["building"="courthouse"]({self.bbox});

  // Post offices
  node["amenity"="post_office"]({self.bbox});
  node["building"="post_office"]({self.bbox});

  // Police departments (detailed)
  node["police"="station"]({self.bbox});
  node["building"="police"]({self.bbox});

  // Fire departments (detailed)
  node["fire"="station"]({self.bbox});
  node["building"="fire_station"]({self.bbox});

  // Public works
  node["office"="public_works"]({self.bbox});
  node["building"="public_works"]({self.bbox});

  // DMV and motor vehicle services
  node["office"="motor_vehicle"]({self.bbox});
  node["shop"="car"]({self.bbox});

  // Tax offices
  node["office"="tax"]({self.bbox});
  node["government"="tax"]({self.bbox});

  // Social services
  node["office"="social_services"]({self.bbox});
  node["government"="social_services"]({self.bbox});

  // Voting locations
  node["amenity"="voting_station"]({self.bbox});
  node["office"="voting"]({self.bbox});

  // Public meeting places
  node["amenity"="community_centre"]["public"="yes"]({self.bbox});

  // Public records
  node["office"="public_records"]({self.bbox});

  // Building permits
  node["office"="building_permits"]({self.bbox});
  node["office"="permit"]({self.bbox});

  // Health department
  node["office"="health_department"]({self.bbox});
  node["government"="health"]({self.bbox});

  // Education department
  node["office"="education"]({self.bbox});
  node["government"="education"]({self.bbox});

  // Public safety
  node["office"="public_safety"]({self.bbox});
  node["government"="public_safety"]({self.bbox});

  // City planning
  node["office"="planning"]({self.bbox});
  node["office"="urban_planning"]({self.bbox});

  // Public utilities
  node["office"="utility"]({self.bbox});
  node["building"="utility"]({self.bbox});
);
out geom;
"""

    def create_community_query(self) -> str:
        """Comprehensive community facilities query"""
        return f"""
[out:json][timeout:300];
(
  // Community centers
  node["amenity"="community_centre"]({self.bbox});
  node["building"="community_centre"]({self.bbox});

  // Senior centers
  node["amenity"="senior_centre"]({self.bbox});
  node["social_facility"="senior_centre"]({self.bbox});

  // Youth centers
  node["amenity"="youth_centre"]({self.bbox});
  node["social_facility"="youth_centre"]({self.bbox});

  // Recreation centers
  node["leisure"="recreation_centre"]({self.bbox});
  node["building"="recreation_centre"]({self.bbox});

  // Religious institutions
  node["amenity"="place_of_worship"]({self.bbox});
  node["building"="church"]({self.bbox});
  node["building"="mosque"]({self.bbox});
  node["building"="synagogue"]({self.bbox});
  node["building"="temple"]({self.bbox});
  node["building"="hindu_temple"]({self.bbox});

  // Parks and recreation
  node["leisure"="park"]({self.bbox});
  node["leisure"="garden"]({self.bbox});
  node["leisure"="playground"]({self.bbox});
  node["leisure"="sports_centre"]({self.bbox});
  node["leisure"="fitness_centre"]({self.bbox});

  // Sports facilities
  node["sport"="swimming"]({self.bbox});
  node["sport"="soccer"]({self.bbox});
  node["sport"="basketball"]({self.bbox});
  node["sport"="tennis"]({self.bbox});
  node["sport"="baseball"]({self.bbox});
  node["sport"="football"]({self.bbox});

  // Theaters and entertainment
  node["amenity"="theatre"]({self.bbox});
  node["amenity"="cinema"]({self.bbox});
  node["building"="theatre"]({self.bbox});

  // Markets
  node["amenity"="marketplace"]({self.bbox});
  node["shop"="market"]({self.bbox});

  // Animal services
  node["amenity"="animal_shelter"]({self.bbox});
  node["shop"="pet"]({self.bbox});

  // Public spaces
  node["leisure"="common"]({self.bbox});
  node["leisure"="square"]({self.bbox});

  // Community gardens
  node["leisure"="garden"]["community"="yes"]({self.bbox});

  // Food banks
  node["amenity"="food_bank"]({self.bbox});
  node["social_facility"="food_bank"]({self.bbox});

  // Homeless shelters
  node["amenity"="shelter"]({self.bbox});
  node["social_facility"="shelter"]({self.bbox});

  // Community halls
  node["amenity"="hall"]({self.bbox});
  node["building"="hall"]({self.bbox});

  // Meeting rooms
  node["amenity"="meeting_room"]({self.bbox});
);
out geom;
"""

    def create_commercial_query(self) -> str:
        """Comprehensive commercial services query"""
        return f"""
[out:json][timeout:300];
(
  // Retail centers
  node["shop"="mall"]({self.bbox});
  node["shop"="department_store"]({self.bbox});
  node["shop"="supermarket"]({self.bbox});
  node["shop"="grocery"]({self.bbox});

  // Food and dining
  node["amenity"="restaurant"]({self.bbox});
  node["amenity"="fast_food"]({self.bbox});
  node["amenity"="cafe"]({self.bbox});
  node["amenity"="bar"]({self.bbox});
  node["amenity"="pub"]({self.bbox});

  // Convenience stores
  node["shop"="convenience"]({self.bbox});
  node["shop"="kiosk"]({self.bbox});

  // Gas stations
  node["amenity"="fuel"]({self.bbox});
  node["shop"="gas"]({self.bbox});

  // Banks and financial services
  node["amenity"="bank"]({self.bbox});
  node["amenity"="atm"]({self.bbox});
  node["shop"="money_transfer"]({self.bbox});

  // Hotels and lodging
  node["tourism"="hotel"]({self.bbox});
  node["tourism"="motel"]({self.bbox});
  node["tourism"="guest_house"]({self.bbox});

  // Auto services
  node["shop"="car"]({self.bbox});
  node["shop"="car_repair"]({self.bbox});
  node["shop"="car_parts"]({self.bbox});
  node["shop"="tyres"]({self.bbox});

  // Hardware and home improvement
  node["shop"="hardware"]({self.bbox});
  node["shop"="doityourself"]({self.bbox});
  node["shop"="garden_centre"]({self.bbox});

  // Electronics and technology
  node["shop"="electronics"]({self.bbox});
  node["shop"="mobile_phone"]({self.bbox});
  node["shop"="computer"]({self.bbox});

  // Clothing and apparel
  node["shop"="clothes"]({self.bbox});
  node["shop"="shoes"]({self.bbox});
  node["shop"="jewelry"]({self.bbox});

  // Personal care
  node["shop"="hairdresser"]({self.bbox});
  node["shop"="beauty"]({self.bbox});
  node["shop"="perfumery"]({self.bbox});

  // Books and media
  node["shop"="books"]({self.bbox});
  node["shop"="music"]({self.bbox});
  node["shop"="video"]({self.bbox});

  // Home goods
  node["shop"="furniture"]({self.bbox});
  node["shop"="home_improvement"]({self.bbox});
  node["shop"="household_linen"]({self.bbox});

  // Specialty stores
  node["shop"="gift"]({self.bbox});
  node["shop"="toy"]({self.bbox});
  node["shop"="sports"]({self.bbox});
  node["shop"="outdoor"]({self.bbox});

  // Wholesale
  node["shop"="wholesale"]({self.bbox});

  // Storage facilities
  node["amenity"="storage"]({self.bbox});

  // Business services
  node["office"="company"]({self.bbox});
  node["shop"="copyshop"]({self.bbox});
  node["amenity"="post_box"]({self.bbox});

  // Pet services
  node["shop"="pet"]({self.bbox});
  node["shop"="pet_grooming"]({self.bbox});

  // Dry cleaning
  node["shop"="dry_cleaning"]({self.bbox});

  // Laundry services
  node["shop"="laundry"]({self.bbox});
);
out geom;
"""

    def create_transportation_query(self) -> str:
        """Comprehensive transportation infrastructure query"""
        return f"""
[out:json][timeout:300];
(
  // Transit hubs
  node["amenity"="bus_station"]({self.bbox});
  node["station"="subway"]({self.bbox});
  node["station"="light_rail"]({self.bbox});
  node["station"="train"]({self.bbox});

  // Bus stops
  node["highway"="bus_stop"]({self.bbox});
  node["public_transport"="platform"]["bus"="yes"]({self.bbox});

  // Taxi stands
  node["amenity"="taxi"]({self.bbox});
  node["highway"="bus_stop"]["taxi"="yes"]({self.bbox});

  // Parking facilities
  node["amenity"="parking"]({self.bbox});
  node["parking"="surface"]({self.bbox});
  node["parking"="multi-storey"]({self.bbox});
  node["parking"="underground"]({self.bbox});

  // Bike parking
  node["amenity"="bicycle_parking"]({self.bbox});
  node["parking"="bicycle"]({self.bbox});

  // Car rental
  node["amenity"="car_rental"]({self.bbox});
  node["shop"="car_rental"]({self.bbox});

  // Bike rental
  node["amenity"="bicycle_rental"]({self.bbox});
  node["shop"="bicycle_rental"]({self.bbox});

  // Car sharing
  node["amenity"="car_sharing"]({self.bbox});
  node["car_sharing"="yes"]({self.bbox});

  // Charging stations
  node["amenity"="charging_station"]({self.bbox});
  node["charging_station"="yes"]({self.bbox});

  // Fuel stations (detailed)
  node["amenity"="fuel"]({self.bbox});
  node["fuel"="diesel"]({self.bbox});
  node["fuel"="octane_91"]({self.bbox});
  node["fuel"="octane_95"]({self.bbox});
  node["fuel"="octane_98"]({self.bbox});
  node["fuel"="e10"]({self.bbox});
  node["fuel"="e85"]({self.bbox});
  node["fuel"="lpg"]({self.bbox});
  node["fuel"="cng"]({self.bbox});
  node["fuel"="electric"]({self.bbox});
  node["fuel"="hydrogen"]({self.bbox});
  node["fuel"="adhoc"]({self.bbox});

  // Ferry terminals
  node["amenity"="ferry_terminal"]({self.bbox});
  node["route"="ferry"]({self.bbox});

  // Airport facilities
  node["aeroway"="terminal"]({self.bbox});
  node["aeroway"="helipad"]({self.bbox});
  node["aeroway"="aerodrome"]({self.bbox});

  // Port facilities
  node["landuse"="port"]({self.bbox});
  node["waterway"="port"]({self.bbox});

  // Transit information
  node["public_transport"="information"]({self.bbox});
  node["information"="terminal"]({self.bbox});

  // Transport offices
  node["office"="transport"]({self.bbox});
  node["office"="taxi"]({self.bbox});

  // Traffic signals
  node["highway"="traffic_signals"]({self.bbox});

  // Street lighting (transport related)
  node["highway"="street_lamp"]({self.bbox});

  // Speed cameras
  node["highway"="speed_camera"]({self.bbox});

  // Weigh stations
  node["highway"="weigh_bridge"]({self.bbox});
  node["amenity"="weigh_bridge"]({self.bbox});

  // Rest areas
  node["highway"="rest_area"]({self.bbox});
  node["amenity"="rest_area"]({self.bbox});

  // Service areas
  node["highway"="services"]({self.bbox});
  node["amenity"="services"]({self.bbox});

  // Toll booths
  node["highway"="toll_booth"]({self.bbox});
  node["barrier"="toll_booth"]({self.bbox});
);
out geom;
"""

    def create_utilities_query(self) -> str:
        """Comprehensive utilities infrastructure query"""
        return f"""
[out:json][timeout:300];
(
  // Power infrastructure
  node["power"="substation"]({self.bbox});
  node["power"="tower"]({self.bbox});
  node["power"="pole"]({self.bbox});
  node["power"="generator"]({self.bbox});
  node["power"="plant"]({self.bbox});

  // Water infrastructure
  node["amenity"="water_tower"]({self.bbox});
  node["man_made"="water_tower"]({self.bbox});
  node["man_made"="reservoir_covered"]({self.bbox});
  node["landuse"="reservoir"]({self.bbox});
  node["waterway"="dam"]({self.bbox});

  // Wastewater treatment
  node["man_made"="wastewater_plant"]({self.bbox});
  node["amenity"="wastewater_plant"]({self.bbox});

  // Water treatment
  node["man_made"="water_treatment_plant"]({self.bbox});
  node["amenity"="water_treatment_plant"]({self.bbox});

  // Pumping stations
  node["man_made"="pumping_station"]({self.bbox});
  node["amenity"="pumping_station"]({self.bbox});

  // Communication infrastructure
  node["communication"="tower"]({self.bbox});
  node["man_made"="tower"]({self.bbox});
  node["man_made"="mast"]({self.bbox});
  node["communication"="antenna"]({self.bbox});
  node["man_made"="antenna"]({self.bbbox});

  // Cell towers
  node["communication"="mobile_phone"]({self.bbox});
  node["communication"="cell_tower"]({self.bbox});

  // Broadcasting
  node["communication"="radio"]({self.bbox});
  node["communication"="television"]({self.bbox});
  node["man_made"="broadcast_transmitter"]({self.bbox});

  // Internet infrastructure
  node["communication"="internet"]({self.bbox});
  node["telecom"="data_center"]({self.bbox});
  node["building"="data_center"]({self.bbox});

  // Postal infrastructure
  node["amenity"="post_box"]({self.bbox});
  node["amenity"="post_office"]({self.bbox});
  node["amenity"="post_depot"]({self.bbox});

  // Waste management
  node["amenity"="recycling"]({self.bbox});
  node["amenity"="waste_basket"]({self.bbox});
  node["amenity"="waste_disposal"]({self.bbox});
  node["amenity"="waste_transfer_station"]({self.bbox});
  node["landuse"="landfill"]({self.bbox});

  // Gas infrastructure
  node["man_made"="gasometer"]({self.bbox});
  node["man_made"="gas_cylinder_holder"]({self.bbox});
  node["man_made"="gas_holder"]({self.bbox});

  // Street lighting
  node["highway"="street_lamp"]({self.bbox});
  node["amenity"="street_lamp"]({self.bbox});
  node["light"="street"]({self.bbox});

  // Traffic signals
  node["highway"="traffic_signals"]({self.bbox});

  // Surveillance
  node["man_made"="surveillance"]({self.bbox});
  node["surveillance"="camera"]({self.bbox});
  node["man_made"="camera"]({self.bbox});

  // Emergency services infrastructure
  node["emergency"="siren"]({self.bbox});
  node["man_made"="siren"]({self.bbox});

  // Weather stations
  node["man_made"="weather_station"]({self.bbox});
  node["amenity"="weather_station"]({self.bbox});

  // Storage tanks
  node["man_made"="storage_tank"]({self.bbox});
  node["building"="storage_tank"]({self.bbox});

  // Pipeline infrastructure
  way["man_made"="pipeline"]({self.bbox});
  way["utility"="pipeline"]({self.bbox});

  // Utility corridors
  way["utility"="yes"]({self.bbox});

  // Cable infrastructure
  way["man_made"="cable"]({self.bbox});
  way["communication"="line"]({self.bbox});

  // Power lines
  way["power"="line"]({self.bbox});
  way["power"="cable"]({self.bbox});
  way["power"="minor_line"]({self.bbox});

  // Water mains
  way["water"="main"]({self.bbox});
  way["water"="pipe"]({self.bbox});
  way["man_made"="pipeline"]["substance"="water"]({self.bbox});

  // Sewer lines
  way["man_made"="pipeline"]["substance"="sewage"]({self.bbox});
  way["sewer"="main"]({self.bbox});

  // Gas lines
  way["man_made"="pipeline"]["substance"="gas"]({self.bbox});
  way["gas"="main"]({self.bbox});
  way["gas"="pipe"]({self.bbox});
);
out geom;
"""

    def create_financial_query(self) -> str:
        """Comprehensive financial services query"""
        return f"""
[out:json][timeout:300];
(
  // Banks
  node["amenity"="bank"]({self.bbox});
  node["building"="bank"]({self.bbox});

  // Credit unions
  node["amenity"="credit_union"]({self.bbox});

  // ATMs
  node["amenity"="atm"]({self.bbox});

  // Investment services
  node["office"="financial"]({self.bbox});
  node["office"="investment"]({self.bbox});
  node["office"="stock_broker"]({self.bbox});

  // Insurance
  node["office"="insurance"]({self.bbox});
  node["shop"="insurance"]({self.bbox});

  // Accounting services
  node["office"="accountant"]({self.bbox});
  node["shop"="accountant"]({self.bbox});

  // Tax services
  node["office"="tax"]({self.bbox});
  node["office"="tax_advisor"]({self.bbox});

  // Legal services
  node["office"="lawyer"]({self.bbox});
  node["office"="notary"]({self.bbox});

  // Real estate
  node["office"="estate_agent"]({self.bbox});
  node["shop"="real_estate"]({self.bbox});

  // Financial consulting
  node["office"="financial_advisor"]({self.bbox});

  // Money services
  node["shop"="money_transfer"]({self.bbox});
  node["shop"="money_lender"]({self.bbox});
  node["shop"="cash_withdrawal"]({self.bbox});

  // Check cashing
  node["shop"="cheque_cashing"]({self.bbox});

  // Currency exchange
  node["shop"="currency_exchange"]({self.bbox});

  // Pawn shops
  node["shop"="pawnbroker"]({self.bbox});

  // Gold and precious metals
  node["shop"="jewelry"]["buy"="yes"]({self.bbox});
  node["shop"="gold"]({self.bbox});

  // Financial technology
  node["office"="fintech"]({self.bbox});
  node["office"="cryptocurrency"]({self.bbox});

  // Microfinance
  node["office"="microfinance"]({self.bbox});

  // Credit services
  node["office"="credit"]({self.bbox});

  // Debt services
  node["office"="debt_counseling"]({self.bbox});

  // Financial education
  node["amenity"="financial_education"]({self.bbox});
  node["office"="financial_education"]({self.bbox});
);
out geom;
"""

    def create_professional_query(self) -> str:
        """Comprehensive professional services query"""
        return f"""
[out:json][timeout:300];
(
  // Medical offices
  node["amenity"="doctors"]({self.bbox});
  node["amenity"="dentist"]({self.bbox});
  node["amenity"="clinic"]({self.bbox});

  // Legal offices
  node["office"="lawyer"]({self.bbox});
  node["office"="notary"]({self.bbox});
  node["office"="legal"]({self.bbox});

  // Accounting and finance
  node["office"="accountant"]({self.bbox});
  node["office"="financial"]({self.bbox});
  node["office"="bookkeeper"]({self.bbox});

  // Real estate
  node["office"="estate_agent"]({self.bbox});
  node["office"="surveyor"]({self.bbox});
  node["office"="architect"]({self.bbox});

  // Engineering
  node["office"="engineer"]({self.bbox});
  node["office"="surveying"]({self.bbox});

  // Technology and IT
  node["office"="it"]({self.bbox});
  node["office"="software"]({self.bbox});
  node["office"="telecommunications"]({self.bbox});

  // Consulting
  node["office"="consultant"]({self.bbox});
  node["office"="management_consulting"]({self.bbox});

  // Marketing and advertising
  node["office"="advertising"]({self.bbox});
  node["office"="marketing"]({self.bbox});
  node["office"="public_relations"]({self.bbox});

  // Design services
  node["office"="graphic_design"]({self.bbox});
  node["office"="interior_design"]({self.bbox});
  node["office"="web_design"]({self.bbox});

  // Printing and publishing
  node["shop"="copyshop"]({self.bbox});
  node["shop"="printer"]({self.bbox});
  node["office"="publisher"]({self.bbox});

  // Photography
  node["shop"="photo"]({self.bbox});
  node["office"="photographer"]({self.bbox});

  // Event planning
  node["office"="event_planner"]({self.bbox});
  node["office"="wedding_planner"]({self.bbox});

  // Translation services
  node["office"="translator"]({self.bbox});

  // Employment services
  node["office"="employment_agency"]({self.bbox});
  node["shop"="employment_agency"]({self.bbox});

  // Business centers
  node["office"="business_center"]({self.bbox});
  node["amenity"="coworking_space"]({self.bbox});

  // Secretarial services
  node["office"="secretarial"]({self.bbox});
  node["shop"="secretarial"]({self.bbox});

  // Research services
  node["office"="research"]({self.bbox});
  node["amenity"="research_institute"]({self.bbox});

  // Testing laboratories
  node["office"="laboratory"]({self.bbox});
  node["amenity"="laboratory"]({self.bbox});

  // Quality control
  node["office"="quality_control"]({self.bbox});

  // Project management
  node["office"="project_management"]({self.bbox});

  // Human resources
  node["office"="human_resources"]({self.bbox});

  // Training and education
  node["office"="training"]({self.bbox});
  node["amenity"="training"]({self.bbox});

  // Business consulting
  node["office"="business_consulting"]({self.bbox});

  // Insurance agents
  node["office"="insurance_agent"]({self.bbox});

  // Financial advisors
  node["office"="financial_advisor"]({self.bbox});

  // Tax preparation
  node["office"="tax_preparation"]({self.bbox});

  // Bookkeeping services
  node["office"="bookkeeping"]({self.bbox});

  // Payroll services
  node["office"="payroll"]({self.bbox});

  // Courier services
  node["office"="courier"]({self.bbox});
  node["amenity"="courier"]({self.bbox});
);
out geom;
"""

    def query_service_category(self, category: str) -> Dict[str, Any]:
        """Query a specific service category"""
        if category not in self.service_categories:
            logger.error(f"Unknown service category: {category}")
            return {"type": "FeatureCollection", "features": []}

        query = self.service_categories[category]()

        logger.info(f"Querying {category} services...")

        try:
            response = requests.post(
                self.overpass_url,
                data=query,
                headers={'Content-Type': 'text/plain'},
                timeout=300
            )
            response.raise_for_status()
            data = response.json()

            # Convert to GeoJSON
            geojson_data = self.osm_to_geojson(data, category)

            feature_count = len(geojson_data.get('features', []))
            logger.info(f"Found {feature_count} {category} services")

            return geojson_data

        except Exception as e:
            logger.error(f"Failed to query {category}: {e}")
            return {"type": "FeatureCollection", "features": []}

    def osm_to_geojson(self, osm_data: Dict[str, Any], service_type: str) -> Dict[str, Any]:
        """Convert Overpass API response to GeoJSON format"""
        geojson_features = []

        for element in osm_data.get('elements', []):
            if element['type'] == 'way' and 'geometry' in element:
                # Way (line/polygon) elements
                coords = [[node['lon'], node['lat']] for node in element['geometry']]

                if len(coords) >= 2:
                    geometry_type = "LineString"
                    if coords[0] == coords[-1] and len(coords) >= 4:
                        geometry_type = "Polygon"
                        coords = [coords]

                    feature = {
                        "type": "Feature",
                        "properties": {
                            "id": element['id'],
                            "service_type": service_type,
                            "osm_tags": element.get('tags', {}),
                            "name": element.get('tags', {}).get('name', f"{service_type} {element['id']}")
                        },
                        "geometry": {
                            "type": geometry_type,
                            "coordinates": coords
                        }
                    }
                    geojson_features.append(feature)

            elif element['type'] == 'node' and 'lat' in element and 'lon' in element:
                # Node (point) elements
                feature = {
                    "type": "Feature",
                    "properties": {
                        "id": element['id'],
                        "service_type": service_type,
                        "osm_tags": element.get('tags', {}),
                        "name": element.get('tags', {}).get('name', f"{service_type} {element['id']}")
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [element['lon'], element['lat']]
                    }
                }
                geojson_features.append(feature)

        return {
            "type": "FeatureCollection",
            "features": geojson_features,
            "metadata": {
                "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
                "source": "OpenStreetMap via Overpass API",
                "service_type": service_type,
                "feature_count": len(geojson_features),
                "bbox": self.bbox
            }
        }

    def download_all_services(self) -> Dict[str, Any]:
        """Download all municipal services data"""
        logger.info("\n" + "="*80)
        logger.info("COMPREHENSIVE MUNICIPAL SERVICES DATA COLLECTION")
        logger.info("="*80)

        results = {}
        total_features = 0

        for category in self.service_categories.keys():
            logger.info(f"\n[DOWNLOADING] {category.upper()} services...")

            # Query the service category
            data = self.query_service_category(category)

            if data.get('features'):
                # Save to file
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"{timestamp}_westchester_{category}_services.geojson"
                filepath = self.data_dir / filename

                with open(filepath, 'w') as f:
                    json.dump(data, f, indent=2)

                feature_count = len(data['features'])
                total_features += feature_count
                results[category] = data

                logger.info(f"[SUCCESS] {category}: {feature_count} services saved to {filename}")
            else:
                logger.warning(f"[WARNING] {category}: No services found")
                results[category] = {"type": "FeatureCollection", "features": []}

            # Rate limiting between categories
            time.sleep(2)

        # Create summary report
        summary = {
            "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_categories": len(self.service_categories),
            "total_services": total_features,
            "categories_processed": list(self.service_categories.keys()),
            "data_directory": str(self.data_dir),
            "bbox": self.bbox,
            "category_summary": {}
        }

        for category, data in results.items():
            summary["category_summary"][category] = {
                "feature_count": len(data.get('features', [])),
                "data_quality": "unknown"
            }

        # Save summary
        summary_file = self.data_dir / f"municipal_services_summary_{time.strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

        logger.info(f"\n[SUCCESS] All municipal services data collected!")
        logger.info(f"Total services collected: {total_features}")
        logger.info(f"Categories processed: {len(self.service_categories)}")
        logger.info(f"Summary report: {summary_file}")
        logger.info(f"Data directory: {self.data_dir}")

        return results


def main():
    """Download comprehensive municipal services data"""
    importer = MunicipalServicesImporter()

    logger.info("[START] Starting comprehensive municipal services collection...")
    logger.info("   This will collect 10+ categories of municipal services and facilities")
    logger.info("   including healthcare, education, emergency services, government, and more.")

    results = importer.download_all_services()

    logger.info("\n" + "="*80)
    logger.info("COMPREHENSIVE MUNICIPAL SERVICES COLLECTION COMPLETE!")
    logger.info("="*80)

    total_features = sum(len(data.get('features', [])) for data in results.values())
    logger.info(f"[SUCCESS] Collected {total_features} total municipal service features")

    for category, data in results.items():
        feature_count = len(data.get('features', []))
        logger.info(f"   - {category}: {feature_count} services")

    logger.info(f"\n[FILES] All data saved to: {importer.data_dir}")
    logger.info("[READY] Comprehensive municipal services data ready for analysis!")


if __name__ == "__main__":
    main()