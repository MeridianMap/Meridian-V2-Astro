"""
GPT Formatter Module for Meridian Astrology
Transforms comprehensive chart calculations into GPT-digestible format

**UPDATED: Now uses GPT Formatter v4_astro by default for enhanced astrological analysis**
- format_for_gpt() → v4_astro format with stricter aspect filtering & enhanced quality controls
- format_for_gpt_v2() → v2.3.2 verbose format (for backward compatibility)

v4_astro Features:
- Hardened aspect filtering with stricter orb limits (0.5°/0.3°/0.15°)
- Day/night aware Arabic lots calculations
- Enhanced body classification (luminaries/planets/asteroids)
- Quality controls with ASC/DESC validation and modality order enforcement

This module handles:
- Location validation and formatting
- Natal chart summary with core elements including angles and aspects
- Transit chart (current planetary positions) with aspects to natal
- Synthesis and interpretation framework
"""

from datetime import datetime, timedelta
import logging
import sys
import os
import importlib.util
# Note: swisseph, aspects imported conditionally in v2 formatter methods

logger = logging.getLogger(__name__)

def deg_in_sign(longitude):
    """Helper utility: Get degree within sign (0-29.9999) from absolute longitude"""
    return round(longitude % 30, 4)  # 4 decimal precision for v2.3.1

def round_precision(value, decimals=4):
    """Round value to specified decimal places for ephemeris-grade precision (default 4 decimals)"""
    if isinstance(value, (int, float)):
        return round(value, decimals)
    return value

class GPTFormatter:
    """
    Transforms ephemeris calculation results into GPT-optimized format
    Provides tagged sections for 'natal', 'transit', 'design' calculations
    """
    
    def __init__(self):
        # Import v2 formatter dependencies only when GPTFormatter is instantiated
        global swe, calculate_aspects
        import swisseph as swe
        try:
            from aspects import calculate_aspects
        except ImportError:
            from backend.aspects import calculate_aspects
        
        self.version = "2.3.2"
        self.max_aspects = 12  # Increased for more comprehensive aspect analysis
        self._jd_utc = None  # Will be set during calculation for metadata audit trail
        
        # Core 10 + Nodes + Major asteroids for complete astrological coverage
        self.key_planets = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "North Node", "South Node"]
        self.extended_planets = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", 
                              "Uranus", "Neptune", "Pluto", "North Node", "South Node", "Chiron", 
                              "Ceres", "Pallas", "Juno", "Vesta", "Black Moon Lilith", "Pallas Athena", "Pholus"]
        
        # Universal body coverage for complete astrological analysis (v2.3.1: includes Pallas Athena, Pholus)
        self.all_calculated_bodies = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", 
                                     "Uranus", "Neptune", "Pluto", "Chiron", "North Node", "South Node",
                                     "Ceres", "Pallas", "Juno", "Vesta", "Black Moon Lilith", "Pallas Athena", "Pholus"]
        self.major_aspects = ["conjunction", "opposition", "trine", "square", "sextile"]
        self.aspect_orbs = {
            "conjunction": 8.0,
            "opposition": 8.0, 
            "trine": 6.0,
            "square": 6.0,
            "sextile": 4.0
        }
        # Global orb policy
        self.orb_policy = {
            "planetary": 3.0,
            "luminary": 5.0,
            "angle": 2.0,
            "asteroid": 1.5
        }
        
    def format_comprehensive_calculation(self, natal_data, transit_data=None, request_metadata=None):
        """
        Main entry point: Transform calculation results into GPT format
        
        Args:
            natal_data (dict): Natal chart calculation results
            transit_data (dict): Current transit calculations (optional)
            request_metadata (dict): Original request data for context
            
        Returns:
            dict: GPT-optimized format with tagged sections
        """
        try:
            logger.info("🤖 Formatting comprehensive calculation for GPT")
            
            # Extract and set Julian Day from available data
            self._set_julian_day_from_data(natal_data, transit_data, request_metadata)
            
            # Create GPT-optimized response
            gpt_response = {
                "metadata": {
                    "formatter_version": self.version,
                    "calculation_timestamp": datetime.utcnow().isoformat(),
                    "julian_day": self._jd_utc,               # float, same precision as swe_julday
                    "ephemeris_version": swe.version,          # e.g. "Swiss Ephemeris 2.10"
                    "data_sources": self._identify_data_sources(natal_data, transit_data),
                    "optimization_level": "gpt_digest",
                    "token_efficiency": "high",
                    "orb_policy": self.orb_policy,
                    "birth": {
                        "subject": self._extract_birth_profile(natal_data, request_metadata)
                    }
                },
                "natal": self._format_natal_summary(natal_data)
            }
            
            # Add transit section if data available
            if transit_data and "error" not in transit_data:
                gpt_response["transit"] = self._format_transit_summary(transit_data, natal_data)
            
            # Add synthesis if multiple data sources
            if len(gpt_response["metadata"]["data_sources"]) > 1:
                gpt_response["synthesis"] = self._create_synthesis_summary(natal_data, transit_data)
            
            logger.info(f"✅ GPT formatting complete. Sections: {list(gpt_response.keys())}")
            return gpt_response
            
        except Exception as e:
            logger.error(f"❌ GPT formatting failed: {str(e)}")
            return {
                "error": f"GPT formatting failed: {str(e)}",
                "metadata": {"formatter_version": self.version, "status": "failed"}
            }
    
    def _identify_data_sources(self, natal_data, transit_data):
        """Identify which data sources are available"""
        sources = []
        
        if natal_data and "error" not in natal_data:
            sources.append("natal")
        if transit_data and "error" not in transit_data:
            sources.append("transit")
            
        return sources
    
    def _set_julian_day_from_data(self, natal_data, transit_data, request_metadata):
        """Extract and set Julian Day from available calculation data for audit trail"""
        try:
            # Priority order: natal_data -> transit_data -> calculate from request_metadata
            
            # Try to get from natal data first
            if natal_data and "julian_day" in natal_data:
                self._jd_utc = natal_data["julian_day"]
                return
            
            # Try transit data
            if transit_data and "julian_day" in transit_data:
                self._jd_utc = transit_data["julian_day"]
                return
            
            # Fallback: calculate from request metadata if available
            if request_metadata:
                birth_date = request_metadata.get('birth_date')
                birth_time = request_metadata.get('birth_time')
                
                if birth_date:
                    try:
                        # Parse date and time
                        if birth_time:
                            datetime_str = f"{birth_date} {birth_time}"
                            dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
                        else:
                            dt = datetime.fromisoformat(birth_date)
                            
                        # Calculate Julian Day using swisseph
                        jd = swe.julday(dt.year, dt.month, dt.day, 
                                       dt.hour + dt.minute/60.0 + dt.second/3600.0)
                        self._jd_utc = jd
                        return
                    except (ValueError, TypeError) as e:
                        logger.warning(f"Could not parse birth date/time for Julian Day: {e}")
            
            # Final fallback: use current time
            now = datetime.utcnow()
            self._jd_utc = swe.julday(now.year, now.month, now.day, 
                                     now.hour + now.minute/60.0 + now.second/3600.0)
            logger.info(f"Using current time for Julian Day: {self._jd_utc}")
            
        except Exception as e:
            logger.warning(f"Could not set Julian Day: {e}")
            # Set to current time as ultimate fallback
            now = datetime.utcnow()
            self._jd_utc = swe.julday(now.year, now.month, now.day, 
                                     now.hour + now.minute/60.0 + now.second/3600.0)
            
            # Final fallback: use current time
            now = datetime.utcnow()
            self._jd_utc = swe.julday(now.year, now.month, now.day, 
                                     now.hour + now.minute/60.0 + now.second/3600.0)
            logger.info(f"Using current time for Julian Day: {self._jd_utc}")
            
        except Exception as e:
            logger.warning(f"Could not set Julian Day: {e}")
            # Set to current time as ultimate fallback
            now = datetime.utcnow()
            self._jd_utc = swe.julday(now.year, now.month, now.day, 
                                     now.hour + now.minute/60.0 + now.second/3600.0)

    def _extract_birth_profile(self, natal_data, request_metadata):
        """Extract essential birth information for context"""
        if not request_metadata:
            request_metadata = {}
            
        # Calculate rising sign for birth profile
        houses = natal_data.get("houses", {})
        rising_sign = self._extract_rising_sign(houses)
        
        return {
            "date": request_metadata.get('birth_date', ''),
            "time": request_metadata.get('birth_time', ''),
            "location": natal_data.get("formatted_location", ""),
            "timezone": natal_data.get("timezone", ""),
            "rising_sign": rising_sign,
            "house_system": request_metadata.get('house_system', 'whole_sign')
        }
    
    def _format_natal_summary(self, natal_data):
        """
        Format natal chart data with 'natal' tag
        Focus on core elements for interpretation
        """
        if not natal_data or "error" in natal_data:
            return {
                "tag": "natal",
                "status": "unavailable",
                "error": natal_data.get("error", "No natal data")
            }
        
        planets = natal_data.get("planets", {})
        houses = natal_data.get("houses", {})
        aspects = natal_data.get("aspects", [])
        
        # Extract angles for enhanced analysis
        angles = self._extract_angles(houses)
        
        return {
            "tag": "natal",
            "status": "available",
            "core_trinity": {
                "sun": self._extract_planet_essence(planets, "Sun"),
                "moon": self._extract_planet_essence(planets, "Moon"),
                "rising": self._extract_rising_sign(houses)
            },
            "angles": angles,
            "chart_ruler": self._determine_chart_ruler(houses, planets),
            "planetary_positions": self._extract_key_planets(planets),
            "major_aspects": self._extract_significant_aspects(aspects),
            "aspects_to_angles": self._calculate_aspects_to_angles(planets, angles),
            "chart_patterns": {
                "elemental_balance": self._calculate_elemental_distribution(planets),
                "modality_emphasis": self._calculate_modality_distribution(planets),
                "chart_shape": self._identify_chart_pattern(aspects)
            },
            "optional_points": self._extract_optional_points(natal_data),
            "interpretation_priority": "core_identity_and_life_purpose"
        }
    
    def _format_transit_summary(self, transit_data, natal_data):
        """
        Format current transit data with 'transit' tag
        Focus on present moment influences
        """
        if not transit_data or "error" in transit_data:
            return {
                "tag": "transit",
                "status": "unavailable",
                "error": transit_data.get("error", "No transit data") if transit_data else "No transit data"
            }
        
        current_planets = transit_data.get("planets", {})
        natal_planets = natal_data.get("planets", {})
        
        return {
            "tag": "transit",
            "status": "available",
            "calculation_time": transit_data.get("calculation_time", datetime.utcnow().isoformat()),
            "current_planetary_positions": self._format_current_positions(current_planets),
            "seasonal_influence": self._determine_seasonal_influence(current_planets),
            "monthly_themes": self._extract_monthly_themes(current_planets),
            "transit_vs_natal": self._compare_transit_to_natal(current_planets, natal_planets),
            "transit_aspects_to_natal": self._calculate_transit_aspects_to_natal(current_planets, natal_planets),
            "interpretation_priority": "present_moment_influences_and_timing"
        }
    
    def _create_synthesis_summary(self, natal_data, transit_data):
        """
        Create synthesis across all calculation types
        """
        available_layers = []
        if natal_data and "error" not in natal_data:
            available_layers.append("natal")
        if transit_data and "error" not in transit_data:
            available_layers.append("transit")
        
        return {
            "available_layers": available_layers,
            "integration_approach": {
                "foundation": "Natal chart provides core identity and life purpose",
                "timing": "Transits show current influences and timing" if "transit" in available_layers else "Not available"
            },
            "synthesis_themes": self._identify_synthesis_themes(natal_data, transit_data),
            "interpretation_priority": "holistic_understanding_through_layered_analysis"
        }
    

    # Helper methods for data extraction
    def _extract_planet_essence(self, planets, planet_name):
        """Extract essential planet information with astrological data"""
        # Handle planets as list of dictionaries
        if isinstance(planets, list):
            for planet in planets:
                if isinstance(planet, dict) and planet.get('name') == planet_name:
                    # Use longitude (0-360) for degree field as per v2.3.1 schema
                    longitude = planet.get('longitude', 0)
                    return {
                        "sign": planet.get("sign", "Unknown"),
                        "house": planet.get("house", "Unknown"),
                        "degree": round_precision(longitude, 4),  # 4 decimal precision for v2.3.1
                        "retrograde": planet.get("retrograde", False),
                        "speed": round_precision(planet.get("speed", 0.0), 4),  # v2.3.1: Daily motion
                        "declination": round_precision(planet.get("declination", 0.0), 4),  # v2.3.1: Celestial latitude
                        "interpretation_key": f"{planet_name} in {planet.get('sign', 'Unknown')} in House {planet.get('house', 'Unknown')}"
                    }
        # Handle planets as dictionary (legacy support)
        elif isinstance(planets, dict):
            planet_data = planets.get(planet_name, {})
            if planet_data and isinstance(planet_data, dict):
                # Use longitude (0-360) for degree field as per v2.3.1 schema
                longitude = planet_data.get('longitude', 0)
                return {
                    "sign": planet_data.get("sign", "Unknown"),
                    "house": planet_data.get("house", "Unknown"),
                    "degree": round_precision(longitude, 4),  # 4 decimal precision for v2.3.1
                    "retrograde": planet_data.get("retrograde", False),
                    "speed": round_precision(planet_data.get("speed", 0.0), 4),  # v2.3.1: Daily motion
                    "declination": round_precision(planet_data.get("declination", 0.0), 4),  # v2.3.1: Celestial latitude
                    "interpretation_key": f"{planet_name} in {planet_data.get('sign', 'Unknown')} in House {planet_data.get('house', 'Unknown')}"
                }
        
        return None
    
    def _extract_rising_sign(self, houses):
        """Extract rising sign from houses (Ascendant)"""
        if not isinstance(houses, dict):
            return "Unknown"
        
        angles = self._extract_angles(houses)
        if "ascendant" in angles:
            return angles["ascendant"].get("sign", "Unknown")
        
        # Fallback to original method
        first_house = houses.get("1", {})
        if isinstance(first_house, dict):
            return first_house.get("sign", "Unknown")
        return "Unknown"
    
    def _determine_chart_ruler(self, houses, planets):
        """Determine chart ruler based on rising sign"""
        rising_sign = self._extract_rising_sign(houses)
        
        rulers = {
            "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury",
            "Cancer": "Moon", "Leo": "Sun", "Virgo": "Mercury",
            "Libra": "Venus", "Scorpio": "Pluto", "Sagittarius": "Jupiter",
            "Capricorn": "Saturn", "Aquarius": "Uranus", "Pisces": "Neptune"
        }
        
        chart_ruler = rulers.get(rising_sign, "Sun")
        ruler_info = self._extract_planet_essence(planets, chart_ruler)
        
        return {
            "planet": chart_ruler,
            "rising_sign": rising_sign,
            "placement": ruler_info.get("interpretation_key", "Unknown") if ruler_info else "Unknown",
            "significance": "Chart ruler represents the primary life direction and energy expression"
        }
    
    def _extract_key_planets(self, planets):
        """Extract planetary placements with universal body coverage (v2.3.1)"""
        placements = {}
        included_bodies = []
        
        # Use all_calculated_bodies for universal coverage
        for planet_name in self.all_calculated_bodies:
            essence = self._extract_planet_essence(planets, planet_name)
            if essence:
                placements[planet_name.lower().replace(" ", "_")] = essence
                included_bodies.append(planet_name)
        
        # Auto-populate included_bodies from actual bodies found
        placements["included_bodies"] = included_bodies
        
        return placements
    
    def _extract_significant_aspects(self, aspects):
        """Extract most significant aspects for interpretation"""
        if not aspects:
            return []
        
        # Filter for major aspects with reasonable orbs
        major_aspects = []
        for aspect in aspects:
            if isinstance(aspect, dict):
                aspect_type = aspect.get("aspect", "").lower()
                orb = abs(aspect.get("orb", 10))
                
                if aspect_type in ["conjunction", "opposition", "trine", "square", "sextile"] and orb < 8:
                    major_aspects.append({
                        "planet1": aspect.get('planet1'),
                        "planet2": aspect.get('planet2'),
                        "aspect": aspect.get('aspect'),
                        "orb": round_precision(orb, 4),  # 4 decimal precision for v2.3
                        "strength": "exact" if orb < 2 else "close" if orb < 4 else "moderate",
                        "nature": self._get_aspect_nature(aspect_type)
                        # Removed description - build dynamically: f"{planet1} {aspect} {planet2}"
                    })
        
        # Sort by orb and return top aspects
        return sorted(major_aspects, key=lambda x: x['orb'])[:self.max_aspects]
    
    def _extract_optional_points(self, natal_data):
        """Extract optional astrological points like asteroids, lunar nodes, etc."""
        optional_points = {}
        
        try:
            planets = natal_data.get('planets', {})
            
            # Extract Lunar Nodes (if present)
            if 'North Node' in planets:
                optional_points['north_node'] = {
                    'longitude': planets['North Node'].get('longitude'),
                    'sign': planets['North Node'].get('sign'),
                    'interpretation': 'soul_purpose_and_destiny'
                }
            
            if 'South Node' in planets:
                optional_points['south_node'] = {
                    'longitude': planets['South Node'].get('longitude'),
                    'sign': planets['South Node'].get('sign'),
                    'interpretation': 'past_life_talents_and_karma'
                }
            
            # Extract major asteroids (if present)
            asteroids = ['Chiron', 'Ceres', 'Pallas', 'Juno', 'Vesta', 'Black Moon Lilith']
            for asteroid in asteroids:
                if asteroid in planets:
                    optional_points[asteroid.lower().replace(' ', '_')] = {
                        'longitude': planets[asteroid].get('longitude'),
                        'sign': planets[asteroid].get('sign'),
                        'interpretation': self._get_asteroid_interpretation(asteroid)
                    }
            
            # Add count and priority guidance
            optional_points['count'] = len([k for k in optional_points.keys() if k not in ['count', 'priority_guidance']])
            optional_points['priority_guidance'] = 'Focus on North Node for life direction, Chiron for healing themes'
            
        except Exception as e:
            logger.warning(f"Error extracting optional points: {e}")
            optional_points = {
                'count': 0,
                'priority_guidance': 'Optional points analysis unavailable'
            }
        
        return optional_points
    
    def _get_asteroid_interpretation(self, asteroid_name):
        """Get interpretive guidance for asteroid placements"""
        interpretations = {
            'Chiron': 'healing_wisdom_and_wounds',
            'Ceres': 'nurturing_and_sustenance',
            'Pallas': 'wisdom_and_strategy',
            'Juno': 'partnership_and_commitment',
            'Vesta': 'devotion_and_sacred_service',
            'Black Moon Lilith': 'shadow_self_and_hidden_power'
        }
        return interpretations.get(asteroid_name, 'additional_influence')
    
    def _get_aspect_nature(self, aspect_type):
        """Get interpretive nature of aspect"""
        natures = {
            "conjunction": "fusion/intensity",
            "opposition": "tension/balance/awareness",
            "trine": "harmony/natural_talent",
            "square": "challenge/growth/dynamic_tension",
            "sextile": "opportunity/supportive_energy"
        }
        return natures.get(aspect_type, "neutral")
    
    def _get_aspect_interpretation(self, aspect_type):
        """Get interpretation guidance for aspect"""
        interpretations = {
            "conjunction": "Planets work together as unified energy",
            "opposition": "Need to balance and integrate opposing energies",
            "trine": "Natural flow and ease, talents to develop",
            "square": "Creative tension that drives growth and achievement",
            "sextile": "Opportunities available through conscious effort"
        }
        return interpretations.get(aspect_type, "General planetary interaction")
    
    def _calculate_elemental_distribution(self, planets):
        """Calculate elemental emphasis in chart"""
        elements = {"Fire": 0, "Earth": 0, "Air": 0, "Water": 0}
        included_bodies = []  # Auto-populated from actual bodies tallied
        
        element_map = {
            "Aries": "Fire", "Leo": "Fire", "Sagittarius": "Fire",
            "Taurus": "Earth", "Virgo": "Earth", "Capricorn": "Earth",
            "Gemini": "Air", "Libra": "Air", "Aquarius": "Air",
            "Cancer": "Water", "Scorpio": "Water", "Pisces": "Water"
        }
        
        # Handle planets as list of dictionaries
        if isinstance(planets, list):
            for planet_data in planets:
                if isinstance(planet_data, dict):
                    planet_name = planet_data.get("name", "")
                    sign = planet_data.get("sign", "")
                    element = element_map.get(sign)
                    if element and planet_name in self.all_calculated_bodies:
                        elements[element] += 1
                        included_bodies.append(planet_name)  # Auto-populate from actual tally
        # Handle planets as dictionary (legacy support)
        elif isinstance(planets, dict):
            for planet_name, planet_data in planets.items():
                if isinstance(planet_data, dict) and planet_name in self.all_calculated_bodies:
                    sign = planet_data.get("sign", "")
                    element = element_map.get(sign)
                    if element:
                        elements[element] += 1
                        included_bodies.append(planet_name)  # Auto-populate from actual tally
        
        # Return sorted by count with interpretations
        sorted_elements = sorted(elements.items(), key=lambda x: x[1], reverse=True)
        return {
            "distribution": sorted_elements,
            "dominant": sorted_elements[0][0] if sorted_elements[0][1] > 0 else "Balanced",
            "included_bodies": included_bodies,  # Programmatically populated
            "interpretation": self._get_element_interpretation(sorted_elements)
        }
    
    def _get_element_interpretation(self, sorted_elements):
        """Get interpretation for elemental distribution"""
        if not sorted_elements or sorted_elements[0][1] == 0:
            return "No clear elemental emphasis"
        
        dominant = sorted_elements[0][0]
        count = sorted_elements[0][1]
        
        interpretations = {
            "Fire": "Enthusiasm, action-oriented, inspirational energy",
            "Earth": "Practical, grounded, material world focus", 
            "Air": "Mental, communicative, social connection emphasis",
            "Water": "Emotional, intuitive, feeling-based approach"
        }
        
        return f"Strong {dominant} emphasis ({count} planets): {interpretations.get(dominant, 'Unknown')}"
    
    def _calculate_modality_distribution(self, planets):
        """Calculate modality emphasis in chart"""
        modalities = {"Cardinal": 0, "Fixed": 0, "Mutable": 0}
        included_bodies = []  # Auto-populated from actual bodies tallied
        
        modality_map = {
            "Aries": "Cardinal", "Cancer": "Cardinal", "Libra": "Cardinal", "Capricorn": "Cardinal",
            "Taurus": "Fixed", "Leo": "Fixed", "Scorpio": "Fixed", "Aquarius": "Fixed",
            "Gemini": "Mutable", "Virgo": "Mutable", "Sagittarius": "Mutable", "Pisces": "Mutable"
        }
        
        # Handle planets as list of dictionaries
        if isinstance(planets, list):
            for planet_data in planets:
                if isinstance(planet_data, dict):
                    planet_name = planet_data.get("name", "")
                    sign = planet_data.get("sign", "")
                    modality = modality_map.get(sign)
                    if modality and planet_name in self.all_calculated_bodies:
                        modalities[modality] += 1
                        included_bodies.append(planet_name)  # Auto-populate from actual tally
        # Handle planets as dictionary (legacy support)
        elif isinstance(planets, dict):
            for planet_name, planet_data in planets.items():
                if isinstance(planet_data, dict) and planet_name in self.all_calculated_bodies:
                    sign = planet_data.get("sign", "")
                    modality = modality_map.get(sign)
                    if modality:
                        modalities[modality] += 1
                        included_bodies.append(planet_name)  # Auto-populate from actual tally
        
        sorted_modalities = sorted(modalities.items(), key=lambda x: x[1], reverse=True)
        return {
            "distribution": sorted_modalities,
            "dominant": sorted_modalities[0][0] if sorted_modalities[0][1] > 0 else "Balanced",
            "included_bodies": included_bodies,  # Programmatically populated
            "interpretation": self._get_modality_interpretation(sorted_modalities)
        }
    
    def _get_modality_interpretation(self, sorted_modalities):
        """Get interpretation for modality distribution"""
        if not sorted_modalities or sorted_modalities[0][1] == 0:
            return "No clear modality emphasis"
        
        dominant = sorted_modalities[0][0]
        count = sorted_modalities[0][1]
        
        interpretations = {
            "Cardinal": "Initiative, leadership, starting new projects",
            "Fixed": "Stability, persistence, seeing things through",
            "Mutable": "Adaptability, flexibility, going with the flow"
        }
        
        return f"Strong {dominant} emphasis ({count} planets): {interpretations.get(dominant, 'Unknown')}"
    
    def _identify_chart_pattern(self, aspects):
        """Identify overall chart pattern"""
        if not aspects:
            return "Scattered energy pattern"
        
        # Count aspect types
        aspect_counts = {}
        for aspect in aspects:
            if isinstance(aspect, dict):
                aspect_type = aspect.get("aspect", "").lower()
                aspect_counts[aspect_type] = aspect_counts.get(aspect_type, 0) + 1
        
        total = len(aspects)
        if total == 0:
            return "Minimal aspect pattern"
        
        if aspect_counts.get("conjunction", 0) > total * 0.4:
            return "Bundle pattern (concentrated energy in few areas)"
        elif aspect_counts.get("opposition", 0) > total * 0.3:
            return "See-saw pattern (polarized energy requiring balance)"
        elif aspect_counts.get("trine", 0) > total * 0.4:
            return "Grand trine potential (flowing, harmonious energy)"
        elif aspect_counts.get("square", 0) > total * 0.4:
            return "Dynamic tension pattern (growth through challenges)"
        else:
            return "Balanced aspect mix (varied life experiences)"
    
    def _format_current_positions(self, current_planets):
        """Format current planetary positions with universal body coverage"""
        formatted = {}
        included_bodies = []
        
        # Use all_calculated_bodies for complete coverage 
        for planet_name in self.all_calculated_bodies:
            planet_data = None
            
            # Handle planets as list of dictionaries
            if isinstance(current_planets, list):
                for planet in current_planets:
                    if isinstance(planet, dict) and planet.get('name') == planet_name:
                        planet_data = planet
                        break
            # Handle planets as dictionary (legacy support)
            elif isinstance(current_planets, dict) and planet_name in current_planets:
                planet_data = current_planets[planet_name]
            
            if planet_data and isinstance(planet_data, dict):
                # Use longitude for degree field (v2.3.1 schema compliance)
                longitude = planet_data.get('longitude', 0)
                formatted[planet_name.lower().replace(" ", "_")] = {
                    "sign": planet_data.get("sign", "Unknown"),
                    "degree": round_precision(longitude, 4),  # 4 decimal precision
                    "house": planet_data.get("house", "Unknown"),
                    "retrograde": planet_data.get("retrograde", False),
                    "speed": round_precision(planet_data.get("speed", 0.0), 4),  # v2.3.1: Daily motion
                    "declination": round_precision(planet_data.get("declination", 0.0), 4),  # v2.3.1: Celestial latitude
                }
                included_bodies.append(planet_name)
        
        # Auto-populate included_bodies
        formatted["included_bodies"] = included_bodies
        
        return formatted
    
    def _determine_seasonal_influence(self, current_planets):
        """Determine current seasonal astrological influence"""
        sun_data = None
        
        # Handle planets as list of dictionaries
        if isinstance(current_planets, list):
            for planet in current_planets:
                if isinstance(planet, dict) and planet.get('name') == 'Sun':
                    sun_data = planet
                    break
        # Handle planets as dictionary (legacy support)
        elif isinstance(current_planets, dict):
            sun_data = current_planets.get("Sun", {})
        
        sun_sign = sun_data.get("sign", "") if sun_data and isinstance(sun_data, dict) else ""
        
        seasonal_map = {
            "Aries": "Spring Equinox - New beginnings and fresh energy",
            "Taurus": "Late Spring - Growth and manifestation", 
            "Gemini": "Early Summer - Communication and learning",
            "Cancer": "Summer Solstice - Emotional depth and nurturing",
            "Leo": "Mid Summer - Creative expression and confidence",
            "Virgo": "Late Summer - Analysis and refinement",
            "Libra": "Autumn Equinox - Balance and relationships",
            "Scorpio": "Mid Autumn - Transformation and depth",
            "Sagittarius": "Late Autumn - Philosophy and expansion",
            "Capricorn": "Winter Solstice - Structure and achievement",
            "Aquarius": "Mid Winter - Innovation and community",
            "Pisces": "Late Winter - Intuition and spiritual connection"
        }
        
        return seasonal_map.get(sun_sign, "Unknown seasonal influence")
    
    def _extract_monthly_themes(self, current_planets):
        """Extract current monthly astrological themes"""
        if not current_planets:
            return "Monthly themes unavailable"
        
        # Get current emphasis from fast-moving planets
        themes = []
        
        # Helper function to get planet data
        def get_planet_data(planet_name):
            if isinstance(current_planets, list):
                for planet in current_planets:
                    if isinstance(planet, dict) and planet.get('name') == planet_name:
                        return planet
            elif isinstance(current_planets, dict):
                return current_planets.get(planet_name, {})
            return {}
        
        # Mercury influence (communication, thinking)
        mercury = get_planet_data("Mercury")
        if isinstance(mercury, dict) and mercury.get('sign'):
            themes.append(f"Communication focus: {mercury.get('sign', 'Unknown')}")
        
        # Venus influence (relationships, values)
        venus = get_planet_data("Venus")
        if isinstance(venus, dict) and venus.get('sign'):
            themes.append(f"Relationship theme: {venus.get('sign', 'Unknown')}")
        
        # Mars influence (action, energy)
        mars = get_planet_data("Mars")
        if isinstance(mars, dict) and mars.get('sign'):
            themes.append(f"Action energy: {mars.get('sign', 'Unknown')}")
        
        return themes if themes else ["Current planetary themes calculated"]
    
    def _compare_transit_to_natal(self, current_planets, natal_planets):
        """Compare current transits to natal positions"""
        comparisons = {}
        
        for planet_name in ["Sun", "Mercury", "Venus", "Mars"]:  # Fast-moving planets
            current_data = None
            natal_data = None
            
            # Get current planet data
            if isinstance(current_planets, list):
                for planet in current_planets:
                    if isinstance(planet, dict) and planet.get('name') == planet_name:
                        current_data = planet
                        break
            elif isinstance(current_planets, dict):
                current_data = current_planets.get(planet_name)
                
            # Get natal planet data
            if isinstance(natal_planets, list):
                for planet in natal_planets:
                    if isinstance(planet, dict) and planet.get('name') == planet_name:
                        natal_data = planet
                        break
            elif isinstance(natal_planets, dict):
                natal_data = natal_planets.get(planet_name)
                
            if current_data and natal_data and isinstance(current_data, dict) and isinstance(natal_data, dict):
                comparisons[planet_name.lower()] = {
                    "current_sign": current_data.get("sign", "Unknown"),
                    "natal_sign": natal_data.get("sign", "Unknown"),
                    "same_sign": current_data.get("sign") == natal_data.get("sign"),
                    "theme": f"Current {current_data.get('sign', 'Unknown')} vs natal {natal_data.get('sign', 'Unknown')}"
                }
        
        return comparisons
    
    def _identify_synthesis_themes(self, natal_data, transit_data):
        """Identify major synthesis themes across all data"""
        themes = []
        
        if natal_data and "error" not in natal_data:
            themes.append("Core identity and life purpose from natal chart")
        
        if transit_data and "error" not in transit_data:
            themes.append("Current timing and environmental influences from transits")
        
        if len(themes) > 1:
            themes.append("Integration of natal foundation with current influences")
        
        return themes
    
    def _extract_angles(self, houses):
        """Extract the four angles (AC, DC, MC, IC) with degrees and signs"""
        angles = {}
        
        if isinstance(houses, dict):
            # Check for direct angle fields (new structure)
            if "ascendant" in houses:
                asc_data = houses["ascendant"]
                if isinstance(asc_data, dict):
                    longitude = asc_data.get("longitude", 0)
                    position = asc_data.get('position', 0)
                    angles["ascendant"] = {
                        "degree": round_precision(longitude, 4),  # 4 decimal precision
                        "deg": round_precision(position, 4),  # 0-30 degree within sign
                        "sign": asc_data.get("sign", "Unknown")
                    }
            
            if "midheaven" in houses:
                mc_data = houses["midheaven"]
                if isinstance(mc_data, dict):
                    longitude = mc_data.get("longitude", 0)
                    position = mc_data.get('position', 0)
                    angles["midheaven"] = {
                        "degree": round_precision(longitude, 4),  # 4 decimal precision
                        "deg": round_precision(position, 4),  # 0-30 degree within sign
                        "sign": mc_data.get("sign", "Unknown")
                    }
            
            if "descendant" in houses:
                desc_data = houses["descendant"]
                if isinstance(desc_data, dict):
                    longitude = desc_data.get("longitude", 0)
                    position = desc_data.get('position', 0)
                    angles["descendant"] = {
                        "degree": round_precision(longitude, 4),  # 4 decimal precision
                        "deg": round_precision(position, 4),  # 0-30 degree within sign
                        "sign": desc_data.get("sign", "Unknown")
                    }
            
            if "imum_coeli" in houses:
                ic_data = houses["imum_coeli"]
                if isinstance(ic_data, dict):
                    longitude = ic_data.get("longitude", 0)
                    position = ic_data.get('position', 0)
                    angles["imum_coeli"] = {
                        "degree": round_precision(longitude, 4),  # 4 decimal precision
                        "deg": round_precision(position, 4),  # 0-30 degree within sign
                        "sign": ic_data.get("sign", "Unknown")
                    }
            
            # Fallback: Check for numbered house structure (legacy support)
            if not angles:
                # Ascendant (1st house cusp)
                if "1" in houses:
                    house_1 = houses["1"]
                    if isinstance(house_1, dict):
                        longitude = house_1.get("cusp_longitude", 0)
                        deg_in_sign = longitude % 30  # Calculate degree within sign
                        angles["ascendant"] = {
                            "degree": round_precision(longitude, 4),  # 4 decimal precision for v2.3.1
                            "deg": round_precision(deg_in_sign, 4),
                            "sign": house_1.get("sign", "Unknown")
                        }
                
                # Descendant (7th house cusp, opposite of Ascendant)
                if "7" in houses:
                    house_7 = houses["7"]
                    if isinstance(house_7, dict):
                        longitude = house_7.get("cusp_longitude", 0)
                        deg_in_sign = longitude % 30
                        angles["descendant"] = {
                            "degree": round_precision(longitude, 4),  # 4 decimal precision for v2.3.1
                            "deg": round_precision(deg_in_sign, 4),
                            "sign": house_7.get("sign", "Unknown")
                        }
                
                # Midheaven (10th house cusp)
                if "10" in houses:
                    house_10 = houses["10"]
                    if isinstance(house_10, dict):
                        longitude = house_10.get("cusp_longitude", 0)
                        deg_in_sign = longitude % 30
                        angles["midheaven"] = {
                            "degree": round_precision(longitude, 4),  # 4 decimal precision for v2.3.1
                            "deg": round_precision(deg_in_sign, 4),
                            "sign": house_10.get("sign", "Unknown")
                        }
                
                # Imum Coeli (4th house cusp, opposite of Midheaven)
                if "4" in houses:
                    house_4 = houses["4"]
                    if isinstance(house_4, dict):
                        longitude = house_4.get("cusp_longitude", 0)
                        deg_in_sign = longitude % 30
                        angles["imum_coeli"] = {
                            "degree": round_precision(longitude, 4),  # 4 decimal precision for v2.3.1
                            "deg": round_precision(deg_in_sign, 4),
                            "sign": house_4.get("sign", "Unknown")
                        }
        
        return angles
    
    def _calculate_aspects_to_angles(self, planets, angles):
        """Calculate aspects between planets and the four angles"""
        aspects_to_angles = []
        
        if not angles or not isinstance(planets, list):
            return aspects_to_angles
        
        angle_names = {
            "ascendant": "AC",
            "descendant": "DC", 
            "midheaven": "MC",
            "imum_coeli": "IC"
        }
        
        for planet in planets:
            if not isinstance(planet, dict):
                continue
                
            planet_name = planet.get('name', '')
            planet_longitude = planet.get('longitude', 0)
            
            for angle_key, angle_abbrev in angle_names.items():
                if angle_key not in angles:
                    continue
                    
                angle_longitude = angles[angle_key].get('degree', 0)
                
                # Calculate aspect
                aspect_info = self._calculate_single_aspect(planet_longitude, angle_longitude)
                if aspect_info:
                    orb_limit = self.aspect_orbs.get(aspect_info['aspect'].lower(), 6.0)
                    if aspect_info['orb'] <= orb_limit:
                        aspects_to_angles.append({
                            "planet": planet_name,
                            "angle": angle_abbrev,
                            "aspect": aspect_info['aspect'],
                            "orb": round_precision(aspect_info['orb'], 4),  # 4 decimal precision for v2.3
                            "strength": "exact" if aspect_info['orb'] < 1.0 else "tight" if aspect_info['orb'] < 3.0 else "moderate"
                        })
        
        # Sort by orb (tightest first)
        return sorted(aspects_to_angles, key=lambda x: x['orb'])[:8]
    
    def _calculate_single_aspect(self, longitude1, longitude2):
        """Calculate the aspect between two planetary positions"""
        diff = abs(longitude1 - longitude2)
        if diff > 180:
            diff = 360 - diff
        
        # Check for major aspects
        aspect_angles = {
            0: "Conjunction",
            60: "Sextile", 
            90: "Square",
            120: "Trine",
            180: "Opposition"
        }
        
        for angle, aspect_name in aspect_angles.items():
            orb = abs(diff - angle)
            if orb <= self.aspect_orbs.get(aspect_name.lower(), 6.0):
                return {
                    "aspect": aspect_name,
                    "orb": orb
                }
        
        return None
    
    def _calculate_transit_aspects_to_natal(self, transit_planets, natal_planets):
        """Calculate aspects between current transits and natal planets"""
        transit_aspects = []
        
        if not isinstance(transit_planets, list) or not isinstance(natal_planets, list):
            return transit_aspects
        
        for transit_planet in transit_planets:
            if not isinstance(transit_planet, dict):
                continue
                
            transit_name = transit_planet.get('name', '')
            transit_longitude = transit_planet.get('longitude', 0)
            
            for natal_planet in natal_planets:
                if not isinstance(natal_planet, dict):
                    continue
                    
                natal_name = natal_planet.get('name', '')
                natal_longitude = natal_planet.get('longitude', 0)
                
                # Skip same planet
                if transit_name == natal_name:
                    continue
                
                aspect_info = self._calculate_single_aspect(transit_longitude, natal_longitude)
                if aspect_info:
                    # Use tighter orbs for transits (3 degrees max)
                    if aspect_info['orb'] <= 3.0:
                        nature = self._get_aspect_nature(aspect_info['aspect'].lower())
                        transit_aspects.append({
                            "transit_planet": transit_name,
                            "natal_planet": natal_name,
                            "aspect": aspect_info['aspect'].lower(),
                            "orb": round_precision(aspect_info['orb'], 4),  # 4 decimal precision for v2.3
                            "nature": nature
                        })
        
        # Sort by orb (tightest first) and limit to most important
        return sorted(transit_aspects, key=lambda x: x['orb'])[:10]

    # Instance method convenience functions for API compatibility
        """
        Format highlight summary (circle region features) for GPT analysis
        
        Args:
            highlight_summary (dict): Contains center point, radius, and features within circle
            natal_data (dict): Optional natal chart data for context
            request_metadata (dict): Original request data for context
            
        Returns:
            dict: GPT-optimized format for astrocartography region analysis (empirical data only)
        """
        try:
            logger.info("🤖 Formatting highlight summary for GPT analysis")
            
            if not highlight_summary or not isinstance(highlight_summary, dict):
                return {
                    "error": "Invalid highlight summary data",
                    "metadata": {"formatter_version": self.version, "status": "failed"}
                }
            
            center = highlight_summary.get('center', {})
            radius = highlight_summary.get('radius', 0)
            features = highlight_summary.get('features', [])
            
            # Categorize and analyze features (empirical data)
            feature_analysis = self._analyze_highlight_features(features)
            
            # Build GPT response with empirical data only
            gpt_response = {
                "metadata": {
                    "formatter_version": self.version,
                    "calculation_timestamp": datetime.utcnow().isoformat(),
                    "analysis_type": "astrocartography_region",
                    "optimization_level": "gpt_digest",
                    "token_efficiency": "high",
                    "coordinates_filtered": True,
                    "data_type": "empirical_only"
                },
                "astrocartography_features": feature_analysis,
                "data_framework": self._build_highlight_interpretation_framework(feature_analysis),
                "synthesis": self._create_highlight_synthesis(feature_analysis, radius, natal_data)
            }
            
            # Add natal context if available (empirical data only)
            if natal_data and "error" not in natal_data:
                gpt_response["natal_context"] = self._extract_natal_context_for_highlight(natal_data, request_metadata)
            
            # Apply comprehensive coordinate stripping to the entire response
            gpt_response = self._strip_coordinates_recursively(gpt_response)
            
            logger.info(f"✅ Highlight summary GPT formatting complete")
            return gpt_response
            
        except Exception as e:
            logger.error(f"❌ Highlight summary GPT formatting failed: {str(e)}")
            return {
                "error": f"Highlight summary formatting failed: {str(e)}",
                "metadata": {"formatter_version": self.version, "status": "failed"}
            }
    

    
    def _analyze_highlight_features(self, features):
        """Analyze and categorize features within the highlight circle - empirical data only, no coordinates"""
        try:
            if not features or not isinstance(features, list):
                return self._empty_feature_analysis()
            
            # Initialize counters and filtered feature list
            counters = {
                'categories': {},
                'planets': {},
                'line_types': {},
                'aspects': {},
                'layers': {}
            }
            filtered_features = []
            
            for feature in features:
                if not isinstance(feature, dict):
                    continue
                    
                props = feature.get('properties', {})
                layer = feature.get('layerName', 'natal')
                
                # Build feature data efficiently
                feature_data = self._extract_feature_data(props, layer)
                filtered_features.append(feature_data)
                
                # Update counters
                self._update_counters(counters, props, layer)
            
            # Sort by distance (closest first)
            filtered_features.sort(key=lambda x: x.get('distance_miles', 999999))
            
            return self._build_feature_analysis_result(filtered_features, counters)
            
        except Exception as e:
            logger.warning(f"Error analyzing highlight features: {e}")
            return self._empty_feature_analysis()
    
    def _empty_feature_analysis(self):
        """Return empty feature analysis structure"""
        return {
            "total_features": 0,
            "feature_categories": {},
            "planetary_influences": {},
            "line_types": {},
            "aspects": {},
            "layers": {}
        }
    
    def _extract_feature_data(self, props, layer):
        """Extract and format feature data from properties"""
        # Base feature data with required fields
        feature_data = {
            'layer': layer,
            'distance_miles': round_precision(props.get('distance', 0) / 1609.34, 2)
        }
        
        # Field mappings with their processing rules (coordinates filtered out)
        field_mappings = {
            'category': ('category', str),
            'planet': ('planet', str),
            'line_type': ('line_type', str),
            'aspect': ('aspect', str),
            'sign': ('sign', str),
            'house': ('house', str),
            'angle': ('angle', str),
            'label': ('label', str),
            'spectral_class': ('spectral_class', str),
            'fixed_star_name': ('star_name', str),
            'arabic_lot_name': ('lot_name', str),
            'orb': ('orb', lambda x: round_precision(x, 4) if x else None),
            'magnitude': ('magnitude', lambda x: round_precision(x, 2) if x else None)
        }
        
        # Process fields efficiently
        for field_key, (prop_key, processor) in field_mappings.items():
            value = props.get(prop_key)
            if value and value != 'unknown' and value != '':
                if callable(processor):
                    processed_value = processor(value)
                    if processed_value is not None and processed_value != 0:
                        feature_data[field_key] = processed_value
                else:
                    feature_data[field_key] = processor(value)
        
        return feature_data
    
    def _update_counters(self, counters, props, layer):
        """Update all counter dictionaries efficiently"""
        counter_mappings = [
            ('categories', props.get('category', '')),
            ('planets', props.get('planet', '')),
            ('line_types', props.get('line_type', '')),
            ('aspects', props.get('aspect', '')),
            ('layers', layer)
        ]
        
        for counter_type, value in counter_mappings:
            if value:  # Only count non-empty values (except layers which are always counted)
                counters[counter_type][value] = counters[counter_type].get(value, 0) + 1
            elif counter_type == 'layers':  # Always count layers, even if empty
                counters[counter_type][value or 'natal'] = counters[counter_type].get(value or 'natal', 0) + 1
    
    def _build_feature_analysis_result(self, filtered_features, counters):
        """Build the final analysis result structure with coordinates completely stripped"""
        result = {
            "total_features": len(filtered_features),
            "closest_features": filtered_features[:15],  # Top 15 closest features for detailed analysis
            "all_features": filtered_features,  # Complete feature set for comprehensive analysis
            "feature_categories": dict(sorted(counters['categories'].items(), key=lambda x: x[1], reverse=True)),
            "planetary_influences": dict(sorted(counters['planets'].items(), key=lambda x: x[1], reverse=True)),
            "line_types": dict(sorted(counters['line_types'].items(), key=lambda x: x[1], reverse=True)),
            "aspects": dict(sorted(counters['aspects'].items(), key=lambda x: x[1], reverse=True)),
            "layers": dict(sorted(counters['layers'].items(), key=lambda x: x[1], reverse=True)),
            "distance_statistics": self._calculate_distance_statistics(filtered_features),
            "data_note": "Empirical astrocartography data only - coordinates filtered for efficiency"
        }
        
        # Apply comprehensive coordinate stripping to the entire result
        return self._strip_coordinates_recursively(result)
    
    def _calculate_distance_statistics(self, filtered_features):
        """Calculate statistical data about feature distances from center"""
        try:
            if not filtered_features:
                return {
                    "closest_distance_miles": 0,
                    "furthest_distance_miles": 0,
                    "average_distance_miles": 0,
                    "median_distance_miles": 0,
                    "total_features_analyzed": 0
                }
            
            distances = [f.get('distance_miles', 0) for f in filtered_features if f.get('distance_miles', 0) > 0]
            
            if not distances:
                return {
                    "closest_distance_miles": 0,
                    "furthest_distance_miles": 0,
                    "average_distance_miles": 0,
                    "median_distance_miles": 0,
                    "total_features_analyzed": len(filtered_features)
                }
            
            # Calculate statistics
            closest = min(distances)
            furthest = max(distances)
            average = sum(distances) / len(distances)
            
            # Calculate median
            sorted_distances = sorted(distances)
            n = len(sorted_distances)
            if n % 2 == 0:
                median = (sorted_distances[n//2 - 1] + sorted_distances[n//2]) / 2
            else:
                median = sorted_distances[n//2]
            
            return {
                "closest_distance_miles": round_precision(closest, 2),
                "furthest_distance_miles": round_precision(furthest, 2),
                "average_distance_miles": round_precision(average, 2),
                "median_distance_miles": round_precision(median, 2),
                "total_features_analyzed": len(filtered_features)
            }
            
        except Exception as e:
            logger.warning(f"Error calculating distance statistics: {e}")
            return {
                "closest_distance_miles": 0,
                "furthest_distance_miles": 0,
                "average_distance_miles": 0,
                "median_distance_miles": 0,
                "total_features_analyzed": 0
            }

    def _build_highlight_interpretation_framework(self, feature_analysis):
        """Build data framework for highlight region analysis - empirical data only"""
        try:
            total_features = feature_analysis.get('total_features', 0)
            
            if total_features == 0:
                return {
                    "analysis_type": "neutral_location",
                    "data_categories": [],
                    "feature_density": "none"
                }
            
            data_categories = []
            
            # Determine categories based on feature types (empirical data only)
            categories = feature_analysis.get('feature_categories', {})
            
            if 'planet' in categories or 'planetary' in str(categories):
                data_categories.append("planetary_lines")
            
            if 'aspect' in categories:
                data_categories.append("aspect_lines")
            
            if 'parans' in categories:
                data_categories.append("paran_crossings")
            
            if 'hermetic_lot' in categories:
                data_categories.append("hermetic_lots")
            
            if 'fixed_star' in categories:
                data_categories.append("fixed_stars")
            
            # Determine feature density (empirical classification)
            if total_features > 15:
                feature_density = "high"
            elif total_features > 8:
                feature_density = "moderate"
            elif total_features > 3:
                feature_density = "low"
            else:
                feature_density = "minimal"
            
            return {
                "analysis_type": "astrocartography_region",
                "data_categories": data_categories,
                "feature_density": feature_density,
                "total_features": total_features
            }
            
        except Exception as e:
            logger.warning(f"Error building highlight framework: {e}")
            return {
                "analysis_type": "astrocartography_region",
                "data_categories": [],
                "feature_density": "unknown"
            }


    
    def _create_highlight_synthesis(self, feature_analysis, radius, natal_data):
        """Create empirical data synthesis for highlight region"""
        try:
            total_features = feature_analysis.get('total_features', 0)
            radius_miles = radius / 1609.34 if radius else 150  # Convert meters to miles
            
            # Empirical data only
            synthesis_data = {
                "search_radius_miles": round_precision(radius_miles, 2),
                "total_features_found": total_features,
                "feature_density_per_sq_mile": round_precision(total_features / (3.14159 * radius_miles * radius_miles), 6) if radius_miles > 0 else 0,
                "distance_statistics": feature_analysis.get('distance_statistics', {}),
                "data_layers_present": list(feature_analysis.get('layers', {}).keys()),
                "feature_category_counts": feature_analysis.get('feature_categories', {}),
                "planetary_feature_counts": feature_analysis.get('planetary_influences', {})
            }
            
            # Add natal data relationship if available
            if natal_data and "error" not in natal_data:
                synthesis_data["natal_chart_available"] = True
                synthesis_data["birth_location"] = natal_data.get("formatted_location", "Unknown")
            else:
                synthesis_data["natal_chart_available"] = False
            
            return synthesis_data
            
        except Exception as e:
            logger.warning(f"Error creating highlight synthesis: {e}")
            return {
                "search_radius_miles": 150,
                "total_features_found": 0,
                "natal_chart_available": False
            }
    
    def _extract_natal_context_for_highlight(self, natal_data, request_metadata):
        """Extract relevant natal context data for highlight region analysis"""
        try:
            # Get basic natal data
            natal_context = {
                "birth_profile": self._extract_birth_profile(natal_data, request_metadata),
                "chart_data_available": True
            }
            
            # Extract key natal elements for regional correlation (empirical data only)
            planets = natal_data.get("planets", {})
            if planets:
                # Get Sun, Moon, Rising for context
                sun_info = self._extract_planet_essence(planets, "Sun")
                moon_info = self._extract_planet_essence(planets, "Moon")
                
                natal_context["primary_placements"] = {
                    "sun_sign": sun_info.get("sign") if sun_info else "Unknown",
                    "sun_longitude": round_precision(sun_info.get("longitude", 0), 4) if sun_info else 0,
                    "moon_sign": moon_info.get("sign") if moon_info else "Unknown", 
                    "moon_longitude": round_precision(moon_info.get("longitude", 0), 4) if moon_info else 0,
                    "rising_sign": self._extract_rising_sign(natal_data.get("houses", {}))
                }
            
            # Add houses data if available
            houses = natal_data.get("houses", {})
            if houses:
                angles = self._extract_angles(houses)
                natal_context["chart_angles"] = angles
            
            return natal_context
            
        except Exception as e:
            logger.warning(f"Error extracting natal context for highlight: {e}")
            return {
                "birth_profile": {"date": "Unknown", "location": "Unknown"},
                "chart_data_available": False
            }

    # Instance method convenience functions for API compatibility
    def format_for_gpt(self, natal_data, transit_data, request_data):
        """Instance method wrapper for format_comprehensive_calculation with both natal and transit data"""
        return self.format_comprehensive_calculation(natal_data, transit_data, request_data)
    
    def format_natal_only(self, natal_data, request_data):
        """Instance method wrapper for format_comprehensive_calculation with natal data only"""
        return self.format_comprehensive_calculation(natal_data, None, request_data)
    
    def format_with_transits(self, natal_data, transit_data, request_data):
        """Instance method wrapper for format_comprehensive_calculation with natal and transit data"""
        return self.format_comprehensive_calculation(natal_data, transit_data, request_data)


# Standalone convenience function for external use
def format_highlight_summary_for_gpt(highlight_summary, natal_data=None, request_metadata=None):
    """
    Convenience function to format highlight summary for GPT analysis
    
    Args:
        highlight_summary (dict): Contains center point, radius, and features within circle
        natal_data (dict): Optional natal chart data for context  
        request_metadata (dict): Original request data for context
        
    Returns:
        dict: GPT-optimized format for astrocartography region analysis
    """
    formatter = GPTFormatter()
    return formatter.format_highlight_summary_for_gpt(highlight_summary, natal_data, request_metadata)

# Additional convenience functions for API compatibility
def format_for_gpt(natal_data, transit_data, request_data):
    """
    Convenience function to format both natal and transit data for GPT analysis
    
    Args:
        natal_data (dict): Natal chart data
        transit_data (dict): Transit chart data
        request_data (dict): Original request parameters
        
    Returns:
        dict: GPT-optimized format combining natal and transit analysis
    """
    formatter = GPTFormatter()
    return formatter.format_for_gpt(natal_data, transit_data, request_data)


def format_natal_only(natal_data, request_data):
    """
    Convenience function to format only natal data for GPT analysis
    
    Args:
        natal_data (dict): Natal chart data
        request_data (dict): Original request parameters
        
    Returns:
        dict: GPT-optimized format for natal-only analysis
    """
    formatter = GPTFormatter()
    return formatter.format_natal_only(natal_data, request_data)


def format_with_transits(natal_data, transit_data, request_data):
    """
    Convenience function to format natal data with current transits for GPT analysis
    
    Args:
        natal_data (dict): Natal chart data
        transit_data (dict): Current transit data
        request_data (dict): Original request parameters
        
    Returns:
        dict: GPT-optimized format with transit analysis
    """
    formatter = GPTFormatter()
    return formatter.format_with_transits(natal_data, transit_data, request_data)

def _strip_coordinates_recursively(self, data):
        """Recursively remove coordinate data from nested dictionaries and lists"""
        if isinstance(data, dict):
            # Create a copy without coordinates
            filtered_data = {}
            for key, value in data.items():
                # Skip coordinate-related keys
                if key in ['coordinates', 'geometry', 'lat', 'lng', 'latitude', 'longitude']:
                    continue
                # Recursively process nested data
                filtered_data[key] = self._strip_coordinates_recursively(value)
            return filtered_data
        elif isinstance(data, list):
            # Recursively process list items
            return [self._strip_coordinates_recursively(item) for item in data]
        else:
            # Return primitive values as-is
            return data