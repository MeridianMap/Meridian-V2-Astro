"""
GPT Formatter v3.3 - Tightened Spec Compliance
Produces schema-compliant output with integer-encoded coordinates
- Only 5 major aspects (con, opp, squ, tri, sex)
- House cusps for all charts
- Decan/term indices for all bodies
- Birth metadata with coordinates
- Chart ruler and sect determination
"""

import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import logging
import importlib.util

# Import v3.1.1 constants using absolute path to avoid conflicts
current_dir = os.path.dirname(__file__)
constants_path = os.path.join(current_dir, 'constants.py')

# Load constants module directly from file to avoid Python's import resolution
spec = importlib.util.spec_from_file_location("src_constants", constants_path)
constants_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(constants_module)

# Import all needed constants from the loaded module
BODY_ID_MAP = constants_module.BODY_ID_MAP
ASPECT_TYPE_MAP = constants_module.ASPECT_TYPE_MAP
CHART_IDS = constants_module.CHART_IDS
ELEMENT_ORDER = constants_module.ELEMENT_ORDER
MODALITY_ORDER = constants_module.MODALITY_ORDER
SIGN_ELEMENT_MAP = constants_module.SIGN_ELEMENT_MAP
SIGN_MODALITY_MAP = constants_module.SIGN_MODALITY_MAP
ESSENTIAL_DIGNITY_SCORES = constants_module.ESSENTIAL_DIGNITY_SCORES
DEFAULT_ORB_POLICY = constants_module.DEFAULT_ORB_POLICY
LUMINARY_BODIES = constants_module.LUMINARY_BODIES
PLANET_BODIES = constants_module.PLANET_BODIES
ASTEROID_BODIES = constants_module.ASTEROID_BODIES
MAJOR_ASPECTS = constants_module.MAJOR_ASPECTS
GATE_RANGE = constants_module.GATE_RANGE
ORB_LIMITS = constants_module.ORB_LIMITS
deg_to_int = constants_module.deg_to_int
int_to_deg = constants_module.int_to_deg
get_body_id = constants_module.get_body_id
get_aspect_id = constants_module.get_aspect_id
get_orb_limit = constants_module.get_orb_limit
body_class = constants_module.body_class
keep_aspect = constants_module.keep_aspect

# Arabic Lots matching backend/hermetic_lots.py implementation
LOTS_CORE = {
    "fortune": ("asc", "moon", "sun"),     # ASC + Moon - Sun (day) / ASC + Sun - Moon (night)
    "spirit": ("asc", "sun", "moon"),      # ASC + Sun - Moon (day) / ASC + Moon - Sun (night)
    "eros": ("asc", "venus", "sun"),       # ASC + Venus - Sun (day) / ASC + Sun - Venus (night)
    "necessity": ("asc", "saturn", "sun"), # ASC + Saturn - Sun (day) / ASC + Sun - Saturn (night)
    "victory": ("asc", "jup", "sun"),      # ASC + Jupiter - Sun (day) / ASC + Sun - Jupiter (night)
    "courage": ("asc", "mars", "sun"),     # ASC + Mars - Sun (day) / ASC + Sun - Mars (night)
    "nemesis": ("asc", "merc", "sun"),     # ASC + Mercury - Sun (day) / ASC + Sun - Mercury (night)
}

# Fixed stars subset for v3.1
FIXED_STARS_V31 = {
    "reg": {"name": "Regulus", "lon_j2000": 149.451},      # Leo
    "spi": {"name": "Spica", "lon_j2000": 203.796},        # Virgo  
    "alg": {"name": "Algol", "lon_j2000": 56.166},         # Taurus
    "ald": {"name": "Aldebaran", "lon_j2000": 69.679},     # Taurus
    "ant": {"name": "Antares", "lon_j2000": 249.496},      # Scorpio
    "fom": {"name": "Fomalhaut", "lon_j2000": 3.521},      # Pisces
    "sir": {"name": "Sirius", "lon_j2000": 104.024}        # Cancer
}

try:
    import swisseph as swe
except ImportError:
    swe = None

logger = logging.getLogger(__name__)

def get_decan_index(longitude):
    """Get decan index (0-2) for a longitude within its sign"""
    degree_in_sign = longitude % 30
    return int(degree_in_sign // 10)

def get_term_index(longitude):
    """Get Egyptian term/bound index (0-4) for a longitude"""
    # Egyptian terms - simplified calculation for now
    degree_in_sign = longitude % 30
    # Approximate term boundaries (each term ~6 degrees)
    return int(degree_in_sign // 6) if degree_in_sign < 30 else 4

def calculate_chart_ruler(sun_sign, is_diurnal):
    """Calculate chart ruler based on sun sign and sect"""
    # Traditional rulerships
    rulers = {
        "Aries": "mars", "Taurus": "venus", "Gemini": "merc",
        "Cancer": "moon", "Leo": "sun", "Virgo": "merc",
        "Libra": "venus", "Scorpio": "mars", "Sagittarius": "jup",
        "Capricorn": "sat", "Aquarius": "sat", "Pisces": "jup"
    }
    return rulers.get(sun_sign, "sun")

def deg_to_gate_line(longitude):
    """Convert longitude to Human Design gate and line format 'gate.line'"""
    # 64 gates cover 360 degrees (5.625 degrees per gate)
    # 6 lines per gate (0.9375 degrees per line)
    
    # Normalize longitude to 0-360
    lng = longitude % 360
    
    # Calculate gate (1-64)
    gate = int(lng / 5.625) + 1
    if gate > 64:
        gate = 64
    
    # Calculate line within gate (1-6)
    gate_start = (gate - 1) * 5.625
    line_position = lng - gate_start
    line = int(line_position / 0.9375) + 1
    if line > 6:
        line = 6
    
    gate_line = f"{gate}.{line}"
    
    # Gate sanity check
    gate_num = int(gate_line.split(".")[0])
    if gate_num not in GATE_RANGE:
        raise ValueError(f"Invalid gate number {gate_num} for longitude {longitude}, gate_line: {gate_line}")
    
    return gate_line

def calculate_house_position(longitude, asc_longitude, house_system="whole_sign"):
    """Calculate house position for a given longitude"""
    if house_system == "whole_sign":
        # Whole sign houses: each sign is one house
        house = int((longitude - asc_longitude) / 30) % 12 + 1
        if house < 1:
            house += 12
        elif house > 12:
            house -= 12
        return house
    else:
        # Simplified equal house calculation for other systems
        house = int((longitude - asc_longitude) / 30) % 12 + 1
        if house < 1:
            house += 12
        elif house > 12:
            house -= 12
        return house

class GPTFormatterV33:
    """
    GPT Formatter v3.3 - Tightened spec compliance
    - Only 5 major aspects (con, opp, squ, tri, sex)
    - House cusps for all charts
    - Decan/term indices for all bodies
    - Birth metadata with coordinates
    - Chart ruler and sect determination
    """
    
    def __init__(self):
        self.version = "3.3"
        self.api_version = "1.0.0"
        self.format_id = "gpt_formatter_v3.3"
        self.ephemeris = "DE441"  # Default ephemeris
        
    def format_comprehensive_calculation(self, natal_data=None, transit_data=None, 
                                       design_data=None, request_metadata=None):
        """
        Main entry point: Transform calculation results into v3.3 format
        
        Args:
            natal_data (dict): Natal chart calculation results
            transit_data (dict): Current transit calculations (optional)
            design_data (dict): Design chart calculations (optional)
            request_metadata (dict): Original request data for context
            
        Returns:
            dict: v3.3 schema-compliant format with the following enhancements:
            
            Body field enumerations:
            - dec (0-2): Decan index within the sign (0=first 10°, 1=second 10°, 2=third 10°)
            - term (0-4): Egyptian term/bound index within sign (roughly 6° each)
            
            Aspect filtering:
            - Only 5 major aspects allowed: con, opp, squ, tri, sex
            - Forbidden aspects (ssx, ssq, sos, qui) stripped from all arrays
            - All aspect arrays sorted by orb_1e4 ascending (tightest first)
            
            House system:
            - Single canonical field in metadata.house_system only
            - No duplicate fields in birth metadata
        """
        try:
            logger.info("🚀 Formatting comprehensive calculation for GPT v3.1")
            
            # Collect all unique bodies across all charts
            all_bodies = self._collect_all_bodies(natal_data, transit_data, design_data)
            
            # Determine house system
            house_system = self._get_house_system(request_metadata, natal_data)
            
            # Create metadata
            metadata = {
                "api_ver": self.api_version,
                "format": self.format_id,  # Use canonical format ID
                "ephem": self.ephemeris,
                "bodies": sorted(all_bodies),
                "orb": DEFAULT_ORB_POLICY,
                "house_system": house_system,  # Use snake_case
                "birth": self._extract_birth_metadata(request_metadata, natal_data)
            }
            
            # Create charts array - enforce exactly (natal|design|transit)
            charts = []
            allowed_chart_ids = {"natal", "design", "transit"}
            
            # Store chart data for cross-referencing in transit aspects
            natal_chart = None
            design_chart = None
            
            # Add natal chart
            if natal_data and "error" not in natal_data:
                natal_chart = self._format_chart(natal_data, "natal", request_metadata)
                if natal_chart and natal_chart.get("id") in allowed_chart_ids:
                    charts.append(natal_chart)
            
            # Add design chart  
            if design_data and "error" not in design_data:
                design_chart = self._format_chart(design_data, "design", request_metadata)
                if design_chart and design_chart.get("id") in allowed_chart_ids:
                    charts.append(design_chart)
                    
            # Add transit chart with cross-aspects
            if transit_data and "error" not in transit_data:
                transit_chart = self._format_transit_chart(
                    transit_data, "transit", request_metadata, 
                    natal_chart, design_chart
                )
                if transit_chart and transit_chart.get("id") in allowed_chart_ids:
                    charts.append(transit_chart)
            
            # Create v3.3 response
            response = {
                "schemaVer": "3.3",
                "metadata": metadata,
                "charts": charts
            }

            # Add astrocartography summary if present in request_metadata
            if request_metadata and request_metadata.get('astrocartography_summary'):
                response['astrocartography'] = self._format_astrocartography_summary(request_metadata['astrocartography_summary'])

            # Apply canonical key ordering for clean output
            response = self._sort_object_keys_canonical(response)
            
            logger.info(f"✅ GPT v3.3 formatting complete. Charts: {[c['id'] for c in charts]}")
            return response
            
        except Exception as e:
            logger.error(f"❌ GPT v3.3 formatting failed: {str(e)}")
            return {
                "schemaVer": "3.3",
                "metadata": {
                    "api_ver": self.api_version,
                    "format": self.format_id,
                    "error": f"Formatting failed: {str(e)}"
                },
                "charts": []
            }
    
    def _collect_all_bodies(self, natal_data, transit_data, design_data):
        """Collect unique body IDs from all chart data"""
        bodies = set()
        
        for data in [natal_data, transit_data, design_data]:
            if data and "error" not in data:
                planets = data.get("planets", [])
                if isinstance(planets, list):
                    for planet in planets:
                        if isinstance(planet, dict):
                            body_name = planet.get("name", "")
                            if body_name:
                                body_id = get_body_id(body_name)
                                bodies.add(body_id)
                elif isinstance(planets, dict):
                    for body_name in planets.keys():
                        body_id = get_body_id(body_name)
                        bodies.add(body_id)
        
        return list(bodies)
    
    def _get_house_system(self, request_metadata, natal_data):
        """Determine house system with priority: request_metadata > natal_data > default"""
        # Priority 1: request_metadata
        if request_metadata and "house_system" in request_metadata:
            return request_metadata["house_system"]
        
        # Priority 2: natal_data
        if natal_data and "house_system" in natal_data:
            return natal_data["house_system"]
        
        # Priority 3: hard default
        return "whole_sign"
    
    def _format_chart(self, chart_data, chart_id, request_metadata=None):
        """Format single chart into v3.1 structure"""
        try:
            # Get calculation timestamp
            timestamp = self._get_chart_timestamp(chart_data, chart_id, request_metadata)
            
            # Format bodies (with gates for all charts)
            bodies = self._format_bodies(chart_data.get("planets", []), include_gates=True)
            
            if not bodies:
                logger.warning(f"No bodies found for chart {chart_id}")
                return None
            
            chart = {
                "id": chart_id,
                "timestamp": timestamp,
                "bodies": bodies,
                "cusps": self._calculate_house_cusps(chart_data)
            }
            
            # Add angles if available
            angles = self._format_angles(chart_data.get("houses", {}))
            if angles:
                chart["angles"] = angles
            
            # Add fixed stars for natal and design charts only
            if chart_id in ["natal", "design"]:
                stars = self._calculate_fixed_stars(chart_data)
                if stars:
                    chart["stars"] = stars
            
            # Add chart-specific extras
            if chart_id == "natal":
                # Comprehensive tight aspects for natal - full coverage within orb limits
                provided_aspects = chart_data.get("aspects", [])
                if provided_aspects:
                    # Use provided aspects if available
                    aspects = self._extract_tight_aspects(provided_aspects)
                else:
                    # Calculate all aspects if none provided for zero-compute coverage
                    aspects = self._calculate_all_aspects_comprehensive(chart_data)
                
                if aspects:
                    chart["tightAspects"] = aspects
                    
                # Arabic lots
                arabic_lots = self._calculate_arabic_lots(chart_data)
                if arabic_lots:
                    chart["arabicLots"] = arabic_lots
                
                # Element and modality tallies for natal (same as design)
                elem_tally = self._calculate_element_tally(chart_data.get("planets", []))
                mode_tally = self._calculate_modality_tally(chart_data.get("planets", []))
                chart["elemTally"] = elem_tally
                chart["modeTally"] = mode_tally
                    
            elif chart_id == "design":
                # Tight aspects for design (parallel to natal)
                provided_aspects = chart_data.get("aspects", [])
                if provided_aspects:
                    # Use provided aspects if available
                    aspects = self._extract_tight_aspects(provided_aspects)
                else:
                    # Calculate all aspects if none provided for zero-compute coverage
                    aspects = self._calculate_all_aspects_comprehensive(chart_data)
                
                if aspects:
                    chart["tightDesignAspects"] = aspects
                
                # Element and modality tallies for design
                elem_tally = self._calculate_element_tally(chart_data.get("planets", []))
                mode_tally = self._calculate_modality_tally(chart_data.get("planets", []))
                chart["elemTally"] = elem_tally
                chart["modeTally"] = mode_tally
            
            # Add dignity scores
            dignity = self._calculate_dignity_scores(chart_data.get("planets", []))
            if dignity:
                chart["dignity"] = dignity
            
            # Add chartRuler and sect (required for all charts in v3.3)
            chart["chartRuler"] = self._calculate_chart_ruler(chart_data)
            chart["sect"] = self._determine_sect(chart_data)
            
            return chart
            
        except Exception as e:
            logger.error(f"Failed to format chart {chart_id}: {e}")
            return None
    
    def _format_transit_chart(self, chart_data, chart_id, request_metadata, natal_chart, design_chart):
        """Format transit chart with cross-aspects to natal and design"""
        try:
            # Start with regular chart formatting
            chart = self._format_chart(chart_data, chart_id, request_metadata)
            if not chart:
                return None
            
            # Add transit-specific features
            # 1. Cross-aspects to natal chart
            if natal_chart:
                to_natal = self._calculate_cross_aspects(chart_data, natal_chart)
                if to_natal:
                    chart["toNatal"] = to_natal
            
            # 2. Cross-aspects to design chart  
            if design_chart:
                to_design = self._calculate_cross_aspects(chart_data, design_chart)
                if to_design:
                    chart["toDesign"] = to_design
            
            # 3. Transit hits to natal angles (ASC/MC for forecasting without compute)
            if natal_chart:
                to_angles = self._calculate_transit_to_angles(chart_data, natal_chart)
                if to_angles:
                    chart["toAngles"] = to_angles
            
            return chart
            
        except Exception as e:
            logger.error(f"Failed to format transit chart: {e}")
            return None
    
    def _calculate_cross_aspects(self, transit_data, target_chart):
        """Calculate tight aspects between transit bodies and target chart bodies"""
        aspects = []
        
        transit_planets = transit_data.get("planets", [])
        target_bodies = target_chart.get("bodies", {})
        
        # Convert transit planets to bodies dict for easier access
        transit_bodies = {}
        if isinstance(transit_planets, list):
            for planet in transit_planets:
                if isinstance(planet, dict):
                    body_name = planet.get("name", "")
                    if body_name:
                        body_id = get_body_id(body_name)
                        transit_bodies[body_id] = planet
        
        # Calculate aspects between each transit body and each target body
        for transit_id, transit_body in transit_bodies.items():
            transit_lng = transit_body.get("longitude", 0)
            
            for target_id, target_data in target_bodies.items():
                # Extract longitude from target body data
                target_lng_1e4 = target_data.get("lng_1e4", 0)
                target_lng = target_lng_1e4 / 10000.0
                
                # Calculate aspects
                aspect_data = self._calculate_aspect(transit_lng, target_lng)
                if aspect_data:
                    aspect_id = get_aspect_id(aspect_data["type"])
                    orb = abs(aspect_data["orb"])
                    
                    aspect_entry = {
                        "a": transit_id,
                        "b": target_id,
                        "t": aspect_id.lower(),  # Ensure lowercase
                        "orb_1e4": deg_to_int(orb)
                    }
                    
                    # Filter using keep_aspect function
                    if keep_aspect(aspect_entry):
                        aspects.append(aspect_entry)
        
        # Filter forbidden aspects and sort properly
        return self._filter_and_sort_aspects(aspects)
    
    def _calculate_aspect(self, lng1, lng2):
        """Calculate aspect between two longitudes - only 5 major aspects allowed"""
        diff = abs(lng1 - lng2)
        if diff > 180:
            diff = 360 - diff
        
        # Only the 5 major aspects allowed in v3.3
        aspects = [
            (0, "conjunction", 8),
            (60, "sextile", 6),
            (90, "square", 8),
            (120, "trine", 8),
            (180, "opposition", 8)
            # Removed: semi-sextile, semi-square, sesqui-square, quincunx
        ]
        
        for angle, aspect_type, max_orb in aspects:
            orb = abs(diff - angle)
            if orb <= max_orb:
                return {"type": aspect_type, "orb": orb}
        
        return None
    
    def _calculate_fixed_stars(self, chart_data):
        """Calculate fixed star positions with houses and gates"""
        stars = {}
        
        # Get ascendant for house calculations
        houses = chart_data.get("houses", {})
        asc_lng = None
        if "ascendant" in houses:
            asc_data = houses["ascendant"]
            if isinstance(asc_data, dict):
                asc_lng = asc_data.get("longitude", 0)
        
        if asc_lng is None:
            asc_lng = 0  # Fallback
        
        # Calculate each fixed star
        for star_id, star_data in FIXED_STARS_V31.items():
            lon_j2000 = star_data["lon_j2000"]
            
            # Apply precession to current epoch (simplified - using ~0.014°/year)
            # For 2025, that's about 25 years from J2000, so ~0.35° precession
            current_longitude = (lon_j2000 + 0.35) % 360
            
            # Calculate house
            house = calculate_house_position(current_longitude, asc_lng)
            
            # Calculate gate
            gate = deg_to_gate_line(current_longitude)
            
            stars[star_id] = {
                "lng_1e4": deg_to_int(current_longitude),
                "house": house,
                "gate": gate
            }
        
        return stars
    
    def _get_chart_timestamp(self, chart_data, chart_id, request_metadata):
        """Get or calculate chart timestamp"""
        # Try to get from chart data first
        if "calculation_time" in chart_data:
            return chart_data["calculation_time"]
        
        # For natal/design, use birth date/time from request metadata
        if chart_id in ["natal", "design"] and request_metadata:
            birth_date = request_metadata.get("birth_date")
            birth_time = request_metadata.get("birth_time")
            
            if birth_date:
                try:
                    if birth_time:
                        dt_str = f"{birth_date}T{birth_time}"
                    else:
                        dt_str = f"{birth_date}T12:00:00"
                    
                    # Ensure proper ISO format
                    if not dt_str.endswith('Z') and '+' not in dt_str[-6:]:
                        dt_str += "Z"
                    
                    return dt_str
                except Exception:
                    pass
        
        # Fallback to current time
        return datetime.utcnow().isoformat() + "Z"
    
    def _format_bodies(self, planets_data, include_gates=False):
        """Format planet data into v3.1 body structure"""
        bodies = {}
        
        # Handle both list and dict formats
        if isinstance(planets_data, list):
            for planet in planets_data:
                if isinstance(planet, dict):
                    body_name = planet.get("name", "")
                    if body_name:
                        body_id = get_body_id(body_name)
                        body_data = self._format_single_body(planet, include_gates)
                        if body_data:
                            bodies[body_id] = body_data
                            
        elif isinstance(planets_data, dict):
            for body_name, planet_data in planets_data.items():
                if isinstance(planet_data, dict):
                    body_id = get_body_id(body_name)
                    body_data = self._format_single_body(planet_data, include_gates)
                    if body_data:
                        bodies[body_id] = body_data
        
        return bodies
    
    def _format_single_body(self, planet_data, include_gates=False):
        """Format single planet into v3.3 body structure with decan/term indices"""
        longitude = planet_data.get("longitude", 0)
        
        body = {
            "lng_1e4": deg_to_int(longitude),
            "dec": get_decan_index(longitude),
            "term": get_term_index(longitude)
        }
        
        # Add optional fields only if present - do not output null/None
        if "latitude" in planet_data and planet_data["latitude"] is not None:
            body["lat_1e4"] = deg_to_int(planet_data["latitude"])
            
        if "speed" in planet_data and planet_data["speed"] is not None:
            body["spd_1e4"] = deg_to_int(planet_data["speed"])
            
        if "declination" in planet_data and planet_data["declination"] is not None:
            body["dec_1e4"] = deg_to_int(planet_data["declination"])
            
        if "retrograde" in planet_data:
            body["rx"] = planet_data["retrograde"]
            
        # Guarantee house is int 1-12 if present, otherwise omit
        if "house" in planet_data:
            house_val = planet_data["house"]
            if isinstance(house_val, (int, str)):
                try:
                    house_int = int(house_val)
                    if 1 <= house_int <= 12:
                        body["house"] = house_int
                except (ValueError, TypeError):
                    pass  # Omit invalid house values
        
        # Add gate annotation for v3.3
        if include_gates:
            body["gate"] = deg_to_gate_line(longitude)
        
        return body
    
    def _format_angles(self, houses_data):
        """Format house angles into v3.2 structure with horizon validation"""
        angles = {}
        
        # Map angle names
        angle_map = {
            "ascendant": "asc",
            "midheaven": "mc", 
            "descendant": "desc",
            "imum_coeli": "ic"
        }
        
        for full_name, short_name in angle_map.items():
            if full_name in houses_data:
                angle_data = houses_data[full_name]
                if isinstance(angle_data, dict) and "longitude" in angle_data:
                    # Ensure lng_1e4 is always in [0, 3599999] via modulo wrap
                    longitude = angle_data["longitude"] % 360
                    angles[short_name] = {
                        "lng_1e4": deg_to_int(longitude)
                    }
        
        # Validate ASC/DESC horizon relationship (DESC should be ASC + 180°)
        if "asc" in angles and "desc" in angles:
            asc_lng = angles["asc"]["lng_1e4"]
            desc_lng = angles["desc"]["lng_1e4"]
            expected_desc = (asc_lng + 1800000) % 3600000  # 180° in 1e-4 format
            if abs(desc_lng - expected_desc) > 100:  # Allow small rounding errors
                logger.warning(f"ASC/DESC horizon mismatch: ASC={asc_lng}, DESC={desc_lng}, expected={expected_desc}")
        
        return angles if angles else None
    
    def _extract_tight_aspects(self, aspects_data):
        """Extract ALL aspects within orb limits for zero-compute coverage"""
        aspects = []
        
        # Method 1: Use provided aspects data if available
        if aspects_data:
            for aspect in aspects_data:
                if isinstance(aspect, dict):
                    orb = abs(aspect.get("orb", 10))
                    planet1 = aspect.get("planet1", "")
                    planet2 = aspect.get("planet2", "")
                    aspect_type = aspect.get("aspect", "")
                    
                    if planet1 and planet2 and aspect_type:
                        body_a = get_body_id(planet1)
                        body_b = get_body_id(planet2)
                        aspect_id = get_aspect_id(aspect_type)
                        
                        # Skip same-body aspects
                        if body_a == body_b:
                            continue
                        
                        aspect_entry = {
                            "a": body_a,
                            "b": body_b,
                            "t": aspect_id.lower(),  # Ensure lowercase
                            "orb_1e4": deg_to_int(orb)
                        }
                        
                        # For natal tightAspects: include ALL aspects within orb limits (no type filtering)
                        if self._is_within_orb_limits_comprehensive(aspect_entry):
                            aspects.append(aspect_entry)
        
        # Filter forbidden aspects and sort properly
        return self._filter_and_sort_aspects(aspects)
    
    def _calculate_all_aspects_comprehensive(self, chart_data):
        """Calculate ALL aspects between all bodies within orb limits for comprehensive coverage"""
        aspects = []
        planets = chart_data.get("planets", [])
        
        # Convert planets to list format if needed
        planet_list = []
        if isinstance(planets, list):
            planet_list = planets
        elif isinstance(planets, dict):
            planet_list = [{"name": name, **data} for name, data in planets.items()]
        
        # Calculate aspects between all pairs of bodies
        for i, planet1 in enumerate(planet_list):
            for j, planet2 in enumerate(planet_list[i+1:], i+1):
                if isinstance(planet1, dict) and isinstance(planet2, dict):
                    lng1 = planet1.get("longitude", 0)
                    lng2 = planet2.get("longitude", 0)
                    name1 = planet1.get("name", "")
                    name2 = planet2.get("name", "")
                    
                    if name1 and name2:
                        # Calculate all possible aspects
                        calculated_aspects = self._calculate_all_aspects_between_bodies_comprehensive(lng1, lng2, name1, name2)
                        aspects.extend(calculated_aspects)
        
        # Filter forbidden aspects and sort properly
        return self._filter_and_sort_aspects(aspects)
    
    def _calculate_all_aspects_between_bodies(self, lng1, lng2, name1, name2):
        """Calculate all aspects between two bodies within orb limits"""
        aspects = []
        diff = abs(lng1 - lng2)
        if diff > 180:
            diff = 360 - diff
        
        # All aspect types with their angles and max orbs
        # Include both major and minor aspects for comprehensive coverage
        all_aspects = [
            (0, "conjunction", 8),
            (30, "semi-sextile", 3),
            (45, "semi-square", 3),
            (60, "sextile", 6),
            (90, "square", 8),
            (120, "trine", 8),
            (135, "sesqui-square", 3),
            (150, "quincunx", 3),
            (180, "opposition", 8)
        ]
        
        for angle, aspect_type, max_orb in all_aspects:
            orb = abs(diff - angle)
            if orb <= max_orb:
                body_a = get_body_id(name1)
                body_b = get_body_id(name2)
                aspect_id = get_aspect_id(aspect_type)
                
                # Calculate exact orb based on longitude difference
                exact_orb = min(orb, 360 - orb) if orb > 180 else orb
                
                aspect_entry = {
                    "a": body_a,
                    "b": body_b,
                    "t": aspect_id.lower(),
                    "orb_1e4": deg_to_int(exact_orb)
                }
                
                # Check orb limits based on body types
                if self._is_within_orb_limits(aspect_entry):
                    aspects.append(aspect_entry)
        
        return aspects
    
    def _is_within_orb_limits(self, aspect_entry):
        """Check if aspect is within proper orb limits based on body types"""
        body_a = aspect_entry["a"]
        body_b = aspect_entry["b"]
        orb_1e4 = aspect_entry["orb_1e4"]
        aspect_type = aspect_entry["t"]
        
        # Get the orb limits in degrees and convert to 1e4 format
        orb_limit_a_deg = get_orb_limit(body_a)
        orb_limit_b_deg = get_orb_limit(body_b)
        
        # Use the larger of the two limits (more permissive for major aspects)
        if aspect_type in ["con", "opp", "squ", "tri"]:
            # Major aspects get the larger orb allowance
            orb_limit_deg = max(orb_limit_a_deg, orb_limit_b_deg)
        else:
            # Minor aspects get stricter limits
            orb_limit_deg = min(orb_limit_a_deg, orb_limit_b_deg) / 2  # Half the orb for minor aspects
        
        # Convert to 1e4 format for comparison
        orb_limit_1e4 = deg_to_int(orb_limit_deg)
        
        return orb_1e4 <= orb_limit_1e4
    
    def _is_within_orb_limits_comprehensive(self, aspect_entry):
        """Check if aspect is within orb limits for comprehensive coverage (all aspect types)"""
        body_a = aspect_entry["a"]
        body_b = aspect_entry["b"]
        orb_1e4 = aspect_entry["orb_1e4"]
        aspect_type = aspect_entry["t"]
        
        # Get the orb limits in degrees and convert to 1e4 format
        orb_limit_a_deg = get_orb_limit(body_a)
        orb_limit_b_deg = get_orb_limit(body_b)
        
        # For comprehensive coverage, use generous orb allowances for all aspects
        if aspect_type in ["con", "opp", "squ", "tri"]:
            # Major aspects get the larger orb allowance
            orb_limit_deg = max(orb_limit_a_deg, orb_limit_b_deg)
        elif aspect_type in ["sex"]:
            # Sextile gets slightly reduced allowance
            orb_limit_deg = max(orb_limit_a_deg, orb_limit_b_deg) * 0.75
        else:
            # Minor aspects get standard allowance (not half like in filtered version)
            orb_limit_deg = max(orb_limit_a_deg, orb_limit_b_deg) * 0.5
        
        # Convert to 1e4 format for comparison
        orb_limit_1e4 = deg_to_int(orb_limit_deg)
        
        return orb_1e4 <= orb_limit_1e4
    
    def _calculate_all_aspects_between_bodies_comprehensive(self, lng1, lng2, name1, name2):
        """Calculate all aspects between two bodies within orb limits for comprehensive coverage"""
        aspects = []
        diff = abs(lng1 - lng2)
        if diff > 180:
            diff = 360 - diff
        
        # All aspect types with their angles and max orbs for comprehensive coverage
        # Include both major and minor aspects
        all_aspects = [
            (0, "conjunction", 10),          # Generous orb for conjunctions
            (30, "semi-sextile", 4),         # Semi-sextile with moderate orb
            (45, "semi-square", 4),          # Semi-square/octile with moderate orb
            (60, "sextile", 8),              # Sextile with good orb
            (90, "square", 10),              # Square with generous orb
            (120, "trine", 10),              # Trine with generous orb
            (135, "sesqui-square", 4),       # Sesqui-square with moderate orb
            (150, "quincunx", 4),            # Quincunx/inconjunct with moderate orb
            (180, "opposition", 10)          # Opposition with generous orb
        ]
        
        for angle, aspect_type, max_orb in all_aspects:
            orb = abs(diff - angle)
            if orb <= max_orb:
                body_a = get_body_id(name1)
                body_b = get_body_id(name2)
                aspect_id = get_aspect_id(aspect_type)
                
                # Skip same-body aspects
                if body_a == body_b:
                    continue
                
                # Calculate exact orb
                exact_orb = orb
                
                aspect_entry = {
                    "a": body_a,
                    "b": body_b,
                    "t": aspect_id.lower(),
                    "orb_1e4": deg_to_int(exact_orb)
                }
                
                # Check orb limits with comprehensive coverage rules
                if self._is_within_orb_limits_comprehensive(aspect_entry):
                    aspects.append(aspect_entry)
        
        return aspects
    
    def _calculate_element_tally(self, planets_data):
        """Calculate element distribution [fire, air, earth, water]"""
        tally = [0, 0, 0, 0]  # [Fire, Air, Earth, Water]
        
        # Handle both list and dict formats
        if isinstance(planets_data, list):
            for planet in planets_data:
                if isinstance(planet, dict):
                    sign = planet.get("sign", "")
                    element = SIGN_ELEMENT_MAP.get(sign)
                    if element:
                        idx = ELEMENT_ORDER.index(element)
                        tally[idx] += 1
                        
        elif isinstance(planets_data, dict):
            for planet_data in planets_data.values():
                if isinstance(planet_data, dict):
                    sign = planet_data.get("sign", "")
                    element = SIGN_ELEMENT_MAP.get(sign)
                    if element:
                        idx = ELEMENT_ORDER.index(element)
                        tally[idx] += 1
        
        return tally
    
    def _calculate_modality_tally(self, planets_data):
        """Calculate modality distribution [cardinal, fixed, mutable] - order enforced"""
        # Enforce order: [Cardinal, Fixed, Mutable]
        card, fixed, mutable = 0, 0, 0
        
        # Handle both list and dict formats
        if isinstance(planets_data, list):
            for planet in planets_data:
                if isinstance(planet, dict):
                    sign = planet.get("sign", "")
                    modality = SIGN_MODALITY_MAP.get(sign)
                    if modality == "Cardinal":
                        card += 1
                    elif modality == "Fixed":
                        fixed += 1
                    elif modality == "Mutable":
                        mutable += 1
                        
        elif isinstance(planets_data, dict):
            for planet_data in planets_data.values():
                if isinstance(planet_data, dict):
                    sign = planet_data.get("sign", "")
                    modality = SIGN_MODALITY_MAP.get(sign)
                    if modality == "Cardinal":
                        card += 1
                    elif modality == "Fixed":
                        fixed += 1
                    elif modality == "Mutable":
                        mutable += 1
        
        # Enforce order guard
        mode_tally = [card, fixed, mutable]  # enforce order
        return mode_tally
    
    def _calculate_arabic_lots(self, chart_data):
        """Calculate Arabic lots using canonical body IDs with deg_to_int encoding"""
        lots = {}
        
        # Get necessary data
        planets = chart_data.get("planets", [])
        houses = chart_data.get("houses", {})
        
        # Build a lookup from canonical body IDs to longitude values
        body_longitudes = {}
        
        # Get ascendant from houses
        if "ascendant" in houses:
            asc_data = houses["ascendant"]
            if isinstance(asc_data, dict) and "longitude" in asc_data:
                body_longitudes["asc"] = asc_data["longitude"]
        
        # Get planets - need to map names to canonical IDs
        canonical_map = {
            "Sun": "sun",
            "Moon": "moon", 
            "Venus": "venus",
            "Jupiter": "jup",
            "Mercury": "merc",
            "Saturn": "saturn",
            "Mars": "mars"
        }
        
        if isinstance(planets, list):
            for planet in planets:
                if isinstance(planet, dict):
                    name = planet.get("name", "")
                    if name in canonical_map and "longitude" in planet:
                        canonical_id = canonical_map[name]
                        body_longitudes[canonical_id] = planet["longitude"]
        elif isinstance(planets, dict):
            for name, planet_data in planets.items():
                if name in canonical_map and isinstance(planet_data, dict) and "longitude" in planet_data:
                    canonical_id = canonical_map[name]
                    body_longitudes[canonical_id] = planet_data["longitude"]
        
        # Check if we have required bodies for day/night determination
        if "sun" not in body_longitudes or "asc" not in body_longitudes:
            return None
            
        # Determine if day chart (Sun above horizon)
        sun_asc_diff = (body_longitudes["sun"] - body_longitudes["asc"]) % 360
        is_day = 0 <= sun_asc_diff < 180
        
        # Calculate each lot using LOTS_CORE definitions
        for lot_name, (base, addend, subtrahend) in LOTS_CORE.items():
            if all(body_id in body_longitudes for body_id in [base, addend, subtrahend]):
                base_lng = body_longitudes[base]
                add_lng = body_longitudes[addend]
                sub_lng = body_longitudes[subtrahend]
                
                # Apply day/night formula adjustments
                if lot_name in ["fortune", "spirit", "eros", "necessity", "victory", "courage", "nemesis"]:
                    if is_day:
                        # Day formula: base + addend - subtrahend
                        lot_lng = (base_lng + add_lng - sub_lng) % 360
                    else:
                        # Night formula: base + subtrahend - addend (swap addend/subtrahend)
                        lot_lng = (base_lng + sub_lng - add_lng) % 360
                else:
                    # Standard formula for other lots
                    lot_lng = (base_lng + add_lng - sub_lng) % 360
                
                lots[lot_name] = int(lot_lng * 10_000)  # Integer encoding
        
        return lots if lots else None
    
    def _calculate_dignity_scores(self, planets_data):
        """Calculate essential and accidental dignity scores"""
        dignity = {}
        
        # Handle both list and dict formats
        if isinstance(planets_data, list):
            for planet in planets_data:
                if isinstance(planet, dict):
                    body_name = planet.get("name", "")
                    sign = planet.get("sign", "")
                    house = planet.get("house")
                    
                    if body_name and sign:
                        body_id = get_body_id(body_name)
                        scores = self._get_dignity_score(body_id, sign, house)
                        if scores:
                            dignity[body_id] = scores
                            
        elif isinstance(planets_data, dict):
            for body_name, planet_data in planets_data.items():
                if isinstance(planet_data, dict):
                    sign = planet_data.get("sign", "")
                    house = planet_data.get("house")
                    
                    body_id = get_body_id(body_name)
                    scores = self._get_dignity_score(body_id, sign, house)
                    if scores:
                        dignity[body_id] = scores
        
        return dignity if dignity else None
    
    def _get_dignity_score(self, body_id, sign, house):
        """Calculate dignity score for single body"""
        scores = {}
        
        # Essential dignity
        if body_id in ESSENTIAL_DIGNITY_SCORES:
            sign_scores = ESSENTIAL_DIGNITY_SCORES[body_id]
            if sign in sign_scores:
                scores["ess"] = sign_scores[sign]
            else:
                scores["ess"] = 0
        else:
            scores["ess"] = 0
        
        # Accidental dignity (simplified - based on house)
        if isinstance(house, int):
            # Angular houses (1,4,7,10) get +2, succeedent +1, cadent 0
            if house in [1, 4, 7, 10]:
                scores["acc"] = 2
            elif house in [2, 5, 8, 11]:
                scores["acc"] = 1
            else:
                scores["acc"] = 0
        else:
            scores["acc"] = 0
        
        return scores if scores else None

    def _calculate_chart_ruler(self, chart_data):
        """Calculate chart ruler based on Ascendant sign"""
        try:
            # Get Ascendant longitude
            houses = chart_data.get("houses", {})
            asc_lng = None
            
            if "ascendant" in houses:
                asc_data = houses["ascendant"]
                if isinstance(asc_data, dict):
                    asc_lng = asc_data.get("longitude", 0)
            
            if asc_lng is None:
                return "sun"  # Default fallback
            
            # Get Ascendant sign
            asc_sign_num = int(asc_lng // 30)
            signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
            asc_sign = signs[asc_sign_num]
            
            is_diurnal = self._is_diurnal_chart(chart_data)
            return calculate_chart_ruler(asc_sign, is_diurnal)
        except Exception as e:
            logger.error(f"Error calculating chart ruler: {e}")
            return "sun"  # Default fallback
    
    def _determine_sect(self, chart_data):
        """Determine if chart is diurnal or nocturnal"""
        try:
            return "diurnal" if self._is_diurnal_chart(chart_data) else "nocturnal"
        except Exception as e:
            logger.error(f"Error determining sect: {e}")
            return "diurnal"  # Default fallback
    
    def _is_diurnal_chart(self, chart_data):
        """Check if chart is diurnal (Sun above horizon)"""
        try:
            # Get Sun longitude
            planets = chart_data.get("planets", [])
            sun_lng = None
            
            if isinstance(planets, list):
                for planet in planets:
                    if isinstance(planet, dict) and planet.get("name") == "Sun":
                        sun_lng = planet.get("longitude", 0)
                        break
            elif isinstance(planets, dict):
                sun_data = planets.get("Sun", {})
                if isinstance(sun_data, dict):
                    sun_lng = sun_data.get("longitude", 0)
            
            if sun_lng is None:
                return True  # Default to diurnal
            
            # Get Ascendant longitude
            houses = chart_data.get("houses", {})
            asc_lng = 0
            if "ascendant" in houses:
                asc_data = houses["ascendant"]
                if isinstance(asc_data, dict):
                    asc_lng = asc_data.get("longitude", 0)
            
            # Simple check: if Sun is in houses 7-12 (above horizon), it's diurnal
            sun_house = self._calculate_house_number(sun_lng, asc_lng)
            return sun_house >= 7
        except Exception as e:
            logger.error(f"Error checking diurnal status: {e}")
            return True  # Default to diurnal
    
    def _calculate_house_number(self, longitude, asc_longitude):
        """Calculate house number for a given longitude"""
        try:
            house = int((longitude - asc_longitude) / 30) % 12 + 1
            if house < 1:
                house += 12
            elif house > 12:
                house -= 12
            return house
        except Exception:
            return 1  # Default fallback
    
    def _calculate_house_cusps(self, chart_data):
        """Calculate 12 house cusps in lng_1e4 format"""
        try:
            # For whole sign houses, cusps are at 0° of each sign
            # Starting from the Ascendant sign
            houses = chart_data.get("houses", {})
            asc_lng = 0
            
            if "ascendant" in houses:
                asc_data = houses["ascendant"]
                if isinstance(asc_data, dict):
                    asc_lng = asc_data.get("longitude", 0)
            
            asc_sign_start = int(asc_lng // 30) * 30
            
            cusps = []
            for i in range(12):
                cusp_lng = (asc_sign_start + (i * 30)) % 360
                cusps.append(deg_to_int(cusp_lng))
            
            return cusps
        except Exception as e:
            logger.error(f"Error calculating house cusps: {e}")
            return [0] * 12  # Default to 12 zeros
    
    def _extract_birth_metadata(self, request_metadata, natal_data):
        """Extract birth information for metadata"""
        try:
            birth_data = request_metadata or {}
            
            return {
                "name": birth_data.get("name", "Unknown"),
                "date": birth_data.get("birth_date", birth_data.get("date", "1900-01-01")),
                "time": birth_data.get("birth_time", birth_data.get("time", "12:00:00")),
                "lat_1e4": deg_to_int(birth_data.get("latitude", 0.0)),
                "lon_1e4": deg_to_int(birth_data.get("longitude", 0.0)),
                "tz": birth_data.get("timezone", birth_data.get("tz", "+00:00"))
            }
        except Exception as e:
            logger.warning(f"Error extracting birth metadata: {e}")
            return {
                "name": "Unknown",
                "date": "1900-01-01", 
                "time": "12:00:00",
                "lat_1e4": 0,
                "lon_1e4": 0,
                "tz": "+00:00"
            }
    
    def _calculate_transit_to_angles(self, transit_data, natal_chart):
        """Calculate transit aspects to natal angles (ASC/MC) for forecasting"""
        angle_aspects = []
        
        # Get natal angles
        natal_angles = natal_chart.get("angles", {})
        if not natal_angles:
            return []
        
        # Get transit planets
        transit_planets = transit_data.get("planets", [])
        transit_bodies = {}
        
        if isinstance(transit_planets, list):
            for planet in transit_planets:
                if isinstance(planet, dict):
                    body_name = planet.get("name", "")
                    if body_name:
                        body_id = get_body_id(body_name)
                        transit_bodies[body_id] = planet
        
        # Calculate aspects between transit bodies and natal angles
        for transit_id, transit_body in transit_bodies.items():
            transit_lng = transit_body.get("longitude", 0)
            
            # Check aspects to ASC and MC (most important angles for forecasting)
            for angle_name in ["asc", "mc"]:
                if angle_name in natal_angles:
                    angle_lng_1e4 = natal_angles[angle_name].get("lng_1e4", 0)
                    angle_lng = angle_lng_1e4 / 10000.0
                    
                    # Calculate aspect
                    aspect_data = self._calculate_aspect(transit_lng, angle_lng)
                    if aspect_data:
                        aspect_id = get_aspect_id(aspect_data["type"])
                        orb = abs(aspect_data["orb"])
                        
                        aspect_entry = {
                            "a": transit_id,
                            "b": angle_name,  # Use angle name directly
                            "t": aspect_id.lower(),
                            "orb_1e4": deg_to_int(orb)
                        }
                        
                        # Use tighter orb limits for angles (they're important timing points)
                        if orb <= 3.0:  # 3-degree max orb for angle transits
                            angle_aspects.append(aspect_entry)
        
        # Filter forbidden aspects and sort properly
        return self._filter_and_sort_aspects(angle_aspects)
    
    def _filter_and_sort_aspects(self, aspects):
        """Filter out forbidden aspects and sort by orb ascending"""
        # Forbidden aspects that should be stripped from all aspect arrays
        forbidden_aspects = {"ssx", "ssq", "sos", "qui"}
        
        # Filter out forbidden aspects
        filtered_aspects = []
        for aspect in aspects:
            if isinstance(aspect, dict):
                aspect_type = aspect.get("t", "")
                if aspect_type not in forbidden_aspects:
                    filtered_aspects.append(aspect)
        
        # Sort by orb ascending (tightest first)
        filtered_aspects.sort(key=lambda x: x.get("orb_1e4", 0))
        
        return filtered_aspects

    def _sort_object_keys_canonical(self, obj):
        """Sort object keys into canonical order for clean diffs and LLM processing"""
        if not isinstance(obj, dict):
            return obj
            
        # Define canonical key order for different object types
        metadata_order = ["api_ver", "format", "ephem", "bodies", "orb", "house_system", "birth"]
        birth_order = ["name", "date", "time", "lat_1e4", "lon_1e4", "tz"]
        chart_order = ["id", "timestamp", "bodies", "angles", "cusps", "stars", "tightAspects", 
                       "tightDesignAspects", "toNatal", "toDesign", "toAngles", "arabicLots", 
                       "elemTally", "modeTally", "dignity", "chartRuler", "sect"]
        body_order = ["lng_1e4", "lat_1e4", "spd_1e4", "dec_1e4", "rx", "house", "dec", "term", "gate"]
        angle_order = ["lng_1e4"]
        aspect_order = ["a", "b", "t", "orb_1e4"]
        
        # Determine object type and apply appropriate sorting
        keys = list(obj.keys())
        
        if "api_ver" in keys and "format" in keys:
            # This is metadata
            ordered_keys = [k for k in metadata_order if k in keys] + sorted([k for k in keys if k not in metadata_order])
        elif "name" in keys and "date" in keys and "time" in keys:
            # This is birth metadata
            ordered_keys = [k for k in birth_order if k in keys] + sorted([k for k in keys if k not in birth_order])
        elif "id" in keys and "timestamp" in keys:
            # This is a chart
            ordered_keys = [k for k in chart_order if k in keys] + sorted([k for k in keys if k not in chart_order])
        elif "lng_1e4" in keys and ("dec" in keys or "term" in keys):
            # This is a body
            ordered_keys = [k for k in body_order if k in keys] + sorted([k for k in keys if k not in body_order])
        elif "a" in keys and "b" in keys and "t" in keys:
            # This is an aspect
            ordered_keys = [k for k in aspect_order if k in keys] + sorted([k for k in keys if k not in aspect_order])
        else:
            # Default alphabetical sort
            ordered_keys = sorted(keys)
        
        # Create new ordered dict and recursively sort nested objects
        result = {}
        for key in ordered_keys:
            value = obj[key]
            if isinstance(value, dict):
                result[key] = self._sort_object_keys_canonical(value)
            elif isinstance(value, list):
                result[key] = [self._sort_object_keys_canonical(item) if isinstance(item, dict) else item for item in value]
            else:
                result[key] = value
                
        return result

    # Add this method to the GPTFormatterV33 class:
    def _minimize_astrocartography_properties(self, props):
        """
        Remove interpretive elements from properties, keeping only technical/geometric data.
        Keeps: category, type, layer_type, source_lines, *_hd_gate, *_hd_line, *_house, *_sign, intersection_lat, intersection_lon, and any other non-interpretive keys.
        """
        keep_prefixes = (
            "category", "type", "layer_type", "source_lines",
            "intersection_lat", "intersection_lon"
        )
        keep_suffixes = ("_hd_gate", "_hd_line", "_house", "_sign")
        minimized = {}
        for k, v in props.items():
            if k in keep_prefixes:
                minimized[k] = v
            elif any(k.endswith(suf) for suf in keep_suffixes):
                minimized[k] = v
            elif k.startswith("source_lines"):
                minimized[k] = v
            elif k.startswith("intersection_"):
                minimized[k] = v
            elif k in ("Mars_hd_gate", "Mars_hd_line", "Mars_house", "Mars_sign", "Pluto_hd_gate", "Pluto_hd_line", "Pluto_house", "Pluto_sign"):
                minimized[k] = v
            # Do NOT keep *_name, label, or other interpretive fields
        return minimized

    def _format_astrocartography_summary(self, summary):
        """
        Format the astrocartography summary for GPT output (deterministic, multi-layered, zero-hallucination)
        
        Improvements:
        - Normalize layer field values to lowercase underscore style
        - Add timestamp field for non-natal layers
        - Enhanced planetary metadata extraction for type: "line" features
        - Ensure gate/line values are integers
        - Add intersection_lon for paran entries with lon = -180
        - Full compatibility with formatter_v3.3 spec
        """
        if not summary:
            return None
            
        center = summary.get('center', [None, None])
        radius = summary.get('radius', None)
        features = summary.get('features', [])
        
        def normalize_layer_name(layer_raw):
            """Normalize layer names to lowercase underscore style"""
            if not layer_raw:
                return 'natal'
            
            # Handle common layer name variations
            layer_map = {
                'HD_DESIGN': 'hd_design',
                'Human Design': 'hd_design',
                'humandesign': 'hd_design',
                'HD Design': 'hd_design',
                'TRANSIT': 'transit',
                'Transit': 'transit',
                'NATAL': 'natal',
                'Natal': 'natal',
                'CCG': 'ccg',
                'Continuous': 'ccg',
                'PROGRESSION': 'progression',
                'Progression': 'progression',
                'SOLAR_RETURN': 'solar_return',
                'Solar Return': 'solar_return'
            }
            
            # Direct mapping first
            if layer_raw in layer_map:
                return layer_map[layer_raw]
            
            # Fallback: convert to lowercase with underscores
            normalized = str(layer_raw).lower().replace(' ', '_').replace('-', '_')
            return normalized
        
        def extract_timestamp_for_layer(props, layer_name):
            """Extract or generate timestamp for non-natal layers"""
            if layer_name == 'natal':
                return None  # Natal doesn't need timestamp
                
            # Check if timestamp already exists in properties
            existing_timestamp = props.get('timestamp') or props.get('calculation_time') or props.get('date')
            if existing_timestamp:
                return existing_timestamp
                
            # For transit layers, try to infer from current time context
            if layer_name == 'transit':
                from datetime import datetime
                return datetime.utcnow().isoformat() + "Z"
                
            # For other layers, return None (will be handled upstream)
            return None
        
        def enhance_planetary_metadata(props, planet_key, existing_data):
            """Enhance planetary metadata with additional context from properties"""
            enhanced = existing_data.copy()
            
            # Try to extract additional metadata from various property patterns
            planet_patterns = [planet_key, planet_key.capitalize(), planet_key.upper()]
            
            for pattern in planet_patterns:
                # Check for additional angle information
                if f'{pattern}_angle' in props and 'angle' not in enhanced:
                    angle_val = str(props[f'{pattern}_angle']).upper()
                    if angle_val in ("AC", "IC", "MC", "DSC"):
                        enhanced['angle'] = angle_val
                
                # Check for longitude/position data to infer missing fields
                if f'{pattern}_longitude' in props:
                    try:
                        lng = float(props[f'{pattern}_longitude'])
                        # Could potentially derive sign/house from longitude if needed
                        # This would require ephemeris calculations, so leaving as placeholder
                    except (ValueError, TypeError):
                        pass
                        
                # Check for declination/latitude data
                if f'{pattern}_declination' in props:
                    try:
                        decl = float(props[f'{pattern}_declination'])
                        enhanced['declination'] = round(decl, 4)
                    except (ValueError, TypeError):
                        pass
            
            return enhanced
        
        def calculate_intersection_lon(props, lon):
            """Calculate intersection longitude for paran entries with lon = -180"""
            if lon != -180:
                return None
                
            # Try to find intersection data in properties
            intersection_lat = props.get('intersection_lat') or props.get('crossing_lat')
            intersection_lon = props.get('intersection_lon') or props.get('crossing_lon')
            
            if intersection_lon is not None:
                try:
                    return round(float(intersection_lon), 5)
                except (ValueError, TypeError):
                    pass
                    
            # Try to calculate midpoint if we have line data
            source_lines = props.get('source_lines', [])
            if len(source_lines) >= 2:
                # This would require more complex calculation of line intersections
                # For now, return a computed estimate or None
                pass
                
            return None
        
        def parse_body_keys(props):
            """Enhanced body parsing with deterministic metadata extraction"""
            # Define canonical planet keys (combining luminaries and planets)
            canonical_planets = set(LUMINARY_BODIES + PLANET_BODIES)
            
            # Create mapping for common planet name variations to canonical names
            planet_name_map = {
                'mercury': 'merc',
                'jupiter': 'jup', 
                'saturn': 'sat',
                'uranus': 'uran',
                'neptune': 'nep',
                # Add exact matches
                'sun': 'sun',
                'moon': 'moon',
                'merc': 'merc',
                'venus': 'venus', 
                'mars': 'mars',
                'jup': 'jup',
                'sat': 'sat',
                'uran': 'uran',
                'nep': 'nep',
                'pluto': 'pluto'
            }
            
            bodies = {}
            
            # Process underscore-separated keys like Mars_sign, Pluto_hd_gate, etc.
            for k, v in props.items():
                if '_' in k:
                    planet, attr = k.split('_', 1)
                    planet_lc = planet.lower()
                    
                    # Map planet name to canonical form
                    canonical_planet = planet_name_map.get(planet_lc)
                    
                    # Only process canonical planets
                    if not canonical_planet or canonical_planet not in canonical_planets:
                        continue
                        
                    if canonical_planet not in bodies:
                        bodies[canonical_planet] = {}
                    
                    # Process attributes with strict type validation
                    if attr == 'hd_gate':
                        try:
                            gate_val = int(float(v)) if isinstance(v, (int, float, str)) and str(v).replace('.','').replace('-','').isdigit() else None
                            if gate_val is not None and 1 <= gate_val <= 64:  # Valid HD gate range
                                bodies[canonical_planet]['gate'] = gate_val
                        except (ValueError, TypeError):
                            pass
                    elif attr == 'hd_line':
                        try:
                            line_val = int(float(v)) if isinstance(v, (int, float, str)) and str(v).replace('.','').replace('-','').isdigit() else None
                            if line_val is not None and 1 <= line_val <= 6:  # Valid HD line range
                                bodies[canonical_planet]['line'] = line_val
                        except (ValueError, TypeError):
                            pass
                    elif attr == 'house':
                        try:
                            house_val = int(float(v)) if isinstance(v, (int, float, str)) and str(v).replace('.','').replace('-','').isdigit() else None
                            if house_val is not None and 1 <= house_val <= 12:  # Valid house range
                                bodies[canonical_planet]['house'] = house_val
                        except (ValueError, TypeError):
                            pass
                    elif attr == 'sign':
                        if v and str(v).strip():
                            sign_val = str(v).strip()
                            # Validate sign names
                            valid_signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 
                                         'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
                            if sign_val in valid_signs:
                                bodies[canonical_planet]['sign'] = sign_val
                    elif attr in ('angle', 'ac', 'ic', 'mc', 'dsc'):
                        # Accept explicit angle keys
                        angle_val = attr.upper() if attr in ('ac','ic','mc','dsc') else str(v).upper()
                        if angle_val in ("AC", "IC", "MC", "DSC"):
                            bodies[canonical_planet]['angle'] = angle_val
                            
            # Process source_lines to infer angles for planets
            source_lines = props.get('source_lines', [])
            if isinstance(source_lines, list):
                for line in source_lines:
                    if isinstance(line, str) and '_' in line:
                        planet, angle = line.split('_', 1)
                        planet_lc = planet.lower()
                        
                        # Map planet name to canonical form
                        canonical_planet = planet_name_map.get(planet_lc)
                        
                        # Only process canonical planets
                        if not canonical_planet or canonical_planet not in canonical_planets:
                            continue
                            
                        if canonical_planet not in bodies:
                            bodies[canonical_planet] = {}
                        
                        angle_upper = angle.upper()
                        if angle_upper in ("AC", "IC", "MC", "DSC"):
                            bodies[canonical_planet]['angle'] = angle_upper
            
            # Enhance each planet's metadata
            for planet_key in list(bodies.keys()):
                bodies[planet_key] = enhance_planetary_metadata(props, planet_key, bodies[planet_key])
            
            # Remove empty objects and ensure all planets have at least one valid field
            valid_bodies = {}
            for planet, data in bodies.items():
                # Remove None values and empty strings
                cleaned_data = {k: v for k, v in data.items() if v is not None and v != ''}
                
                # Only include if there's at least one valid field
                if cleaned_data:
                    valid_bodies[planet] = cleaned_data
            
            return valid_bodies
        
        # Build the formatted response
        formatted = {
            "center": {
                "lat": round(center[0], 5) if center[0] is not None else None,
                "lon": round(center[1], 5) if center[1] is not None else None
            },
            "radius_m": int(radius) if radius is not None else None,
            "features": []
        }
        
        for f in features:
            feat = f.get('feature', {})
            dist = f.get('distance', None)
            props = feat.get('properties', {})
            
            # Determine type with enhanced detection
            type_val = 'line'  # Default
            if props.get('type') == 'crossing_latitude' or props.get('category') == 'parans':
                type_val = 'paran'
            elif props.get('line_type') in ['MC', 'IC', 'HORIZON']:
                type_val = 'line'
            elif props.get('type') == 'fixed_star':
                type_val = 'point'  # For fixed stars
            
            # Normalize layer name
            layer_raw = props.get('layer_type') or props.get('layer') or props.get('layerName') or 'natal'
            layer_val = normalize_layer_name(layer_raw)
            
            # Extract geometry
            lat, lon = None, None
            if feat.get('geometry', {}).get('type') == 'Point':
                coords = feat['geometry'].get('coordinates', [None, None])
                lon, lat = coords[0], coords[1]
            elif feat.get('geometry', {}).get('type') in ('LineString', 'MultiLineString'):
                coords = feat['geometry'].get('coordinates', [])
                if coords and isinstance(coords[0], list):
                    if isinstance(coords[0][0], (float, int)):
                        lon, lat = coords[0][0], coords[0][1]
                    elif isinstance(coords[0][0], list):
                        lon, lat = coords[0][0][0], coords[0][0][1]
            
            # Build feature object
            feature_obj = {
                "type": type_val,
                "layer": layer_val,
                "lat": round(lat, 5) if lat is not None else None,
                "lon": round(lon, 5) if lon is not None else None,
                "distance_m": int(dist) if dist is not None else None,
                "bodies": parse_body_keys(props)
            }
            
            # Add timestamp for non-natal layers
            if layer_val != 'natal':
                timestamp = extract_timestamp_for_layer(props, layer_val)
                if timestamp:
                    feature_obj["timestamp"] = timestamp
            
            # Add intersection_lon for paran entries with lon = -180
            if type_val == 'paran' and lon == -180:
                intersection_lon = calculate_intersection_lon(props, lon)
                if intersection_lon is not None:
                    feature_obj["intersection_lon"] = intersection_lon
            
            formatted['features'].append(feature_obj)
        
        return formatted
# Factory function for backwards compatibility
def create_formatter_v33():
    """Create new GPT Formatter v3.3 instance"""
    return GPTFormatterV33()

# Main generation function
def generate(natal_data=None, transit_data=None, design_data=None, request_metadata=None):
    """
    Generate v3.3 format output
    
    Args:
        natal_data: Natal chart data
        transit_data: Transit chart data  
        design_data: Design chart data
        request_metadata: Request context
        
    Returns:
        dict: v3.3 schema-compliant payload
    """
    formatter = GPTFormatterV33()
    return formatter.format_comprehensive_calculation(
        natal_data, transit_data, design_data, request_metadata
    )
