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

Note: Astrocartography information is excluded from this module
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
        from aspects import calculate_aspects
        
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
                "natal": self._format_natal_summary(natal_data),
                "interpretation_framework": self._build_interpretation_framework(natal_data, transit_data)
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
            "coordinates": natal_data.get("coordinates", {}),
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
    
    def _build_interpretation_framework(self, natal_data, transit_data):
        """
        Build framework to guide GPT interpretation
        """
        available_data = self._identify_data_sources(natal_data, transit_data)
        
        # Build interpretation sequence based on available data
        sequence = ["establish_natal_foundation"]
        focus_areas = ["sun_moon_rising", "chart_ruler", "major_aspects"]
        
        if "transit" in available_data:
            sequence.append("assess_current_timing_and_influences")
            focus_areas.append("current_planetary_emphasis")
        
        if len(available_data) > 1:
            sequence.append("synthesize_natal_and_current_influences")
        
        return {
            "interpretation_sequence": sequence,
            "focus_areas": focus_areas,
            "approach": "layer_natal_with_temporal",
            "depth_level": "comprehensive_yet_accessible",
            "guidance_style": "empowering_and_practical"
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
    

# Convenience functions for easy import and use
def format_for_gpt(natal_data, transit_data=None, request_metadata=None):
    """
    Convenience function to format calculation results for GPT using v4_astro format
    
    Args:
        natal_data (dict): Natal chart calculation results
        transit_data (dict): Transit calculation results (optional)
        request_metadata (dict): Original request data for context
        
    Returns:
        dict: GPT v4_astro format with tightened aspect filtering (5 major only), house cusps & birth metadata
    """
    # Import v3.1 formatter with proper path handling
    import sys
    import os
    import importlib.util
    
    # Get the absolute paths
    current_dir = os.path.dirname(__file__)
    src_path = os.path.abspath(os.path.join(current_dir, '..', 'src'))
    backend_path = os.path.abspath(current_dir)
    formatter_path = os.path.join(src_path, 'gpt_formatter_v3_1.py')
    
    # Store original sys.path
    original_path = sys.path.copy()
    
    # Ensure src is first (for v3.1 constants), backend is available (for dependencies)
    paths_to_add = [src_path, backend_path]
    for path in paths_to_add:
        if path not in sys.path:
            if path == src_path:
                sys.path.insert(0, path)  # src must be first
            else:
                sys.path.append(path)      # backend can be later
    
    try:
        # Load the v3.3 module dynamically to isolate imports
        spec = importlib.util.spec_from_file_location("gpt_formatter_v3_1", formatter_path)
        gpt_formatter_v3_3 = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(gpt_formatter_v3_3)
        
        # Use v4_astro formatter for latest features (tightened aspects, house cusps, birth metadata)
        result = gpt_formatter_v3_3.generate(natal_data=natal_data, transit_data=transit_data, 
                                           request_metadata=request_metadata)
        return result
    finally:
        # Restore original sys.path to avoid conflicts
        sys.path[:] = original_path


def format_natal_only(natal_data, request_metadata=None):
    """
    Format only natal chart data for GPT
    
    Args:
        natal_data (dict): Natal chart calculation results
        request_metadata (dict): Original request data for context
        
    Returns:
        dict: GPT-optimized natal format
    """
    return format_for_gpt(natal_data, None, request_metadata)


def format_with_transits(natal_data, transit_data, request_metadata=None):
    """
    Format natal chart with current transits for GPT
    
    Args:
        natal_data (dict): Natal chart calculation results
        transit_data (dict): Transit calculation results
        request_metadata (dict): Original request data for context
        
    Returns:
        dict: GPT-optimized format with transits
    """
    return format_for_gpt(natal_data, transit_data, request_metadata)


def format_for_gpt_v2(natal_data, transit_data=None, request_metadata=None):
    """
    Legacy v2.3.2 formatter - produces verbose output (for backward compatibility)
    Use format_for_gpt() for new v4_astro format with enhanced astrological analysis
    
    Args:
        natal_data (dict): Natal chart calculation results
        transit_data (dict): Transit calculation results (optional)
        request_metadata (dict): Original request data for context
        
    Returns:
        dict: GPT v2.3.2 verbose format
    """
    formatter = GPTFormatter()
    return formatter.format_comprehensive_calculation(natal_data, transit_data, request_metadata)