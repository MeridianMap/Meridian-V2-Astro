#!/usr/bin/env python3
"""
SVG Chart Renderer for Meridian Map
Generates SVG astrological charts for different layers using svgwrite
"""

import svgwrite
from svgwrite.base import Title
import math
import logging
from typing import Dict, List, Tuple, Any, Optional

logger = logging.getLogger(__name__)

class AstroChartRenderer:
    """
    Custom SVG chart renderer for astrological charts
    Supports: Natal, Human Design, Transit, and CCG charts
    """
    
    def __init__(self, width: int = 600, height: int = 600):
        self.width = width
        self.height = height
        self.center_x = width // 2
        self.center_y = height // 2
        self.outer_radius = min(width, height) // 2 - 50
        self.inner_radius = self.outer_radius - 100
        self.planet_radius = self.outer_radius - 30
        
        # Astrological symbols (simplified Unicode)
        self.planet_symbols = {
            'sun': '☉', 'moon': '☽', 'mercury': '☿', 'venus': '♀', 'mars': '♂',
            'jupiter': '♃', 'saturn': '♄', 'uranus': '♅', 'neptune': '♆', 'pluto': '♇',
            'north_node': '☊', 'south_node': '☋', 'chiron': '⚷', 'ascendant': 'ASC',
            'midheaven': 'MC', 'descendant': 'DSC', 'imum_coeli': 'IC'
        }
        
        self.sign_symbols = {
            0: '♈', 30: '♉', 60: '♊', 90: '♋', 120: '♌', 150: '♍',
            180: '♎', 210: '♏', 240: '♐', 270: '♑', 300: '♒', 330: '♓'
        }
        
        # Colors for different elements with improved contrast
        self.colors = {
            'fire': '#E74C3C', 'earth': '#8B4513', 'air': '#3498DB', 'water': '#2980B9',
            'natal': '#2C3E50', 'transit': '#E67E22', 'composite': '#8E44AD',
            'human_design': '#27AE60', 'aspects': '#34495E'
        }

    def create_chart_svg(self, chart_data: Dict, layer_type: str, config: Dict = None) -> str:
        """
        Generate SVG chart for the specified layer type
        """
        if config is None:
            config = {}
        
        # Determine if legend is enabled
        show_legend = config.get('show_legend', True)
        
        # Adjust canvas width to accommodate legend outside the chart
        canvas_width = self.width + (200 if show_legend else 0)
        canvas_height = self.height
            
        # Create SVG drawing with adjusted size
        dwg = svgwrite.Drawing(size=(canvas_width, canvas_height))
        
        # Add background
        dwg.add(dwg.rect(insert=(0, 0), size=(canvas_width, canvas_height), 
                        fill='white', stroke='none'))
        
        # Add chart title and legend
        self._add_chart_title_and_legend(dwg, chart_data, layer_type, config)
        
        # Draw based on layer type
        try:
            if layer_type == 'natal':
                self._draw_natal_chart(dwg, chart_data, config)
            elif layer_type == 'human_design':
                self._draw_human_design_chart(dwg, chart_data, config)
            elif layer_type == 'transit':
                self._draw_transit_chart(dwg, chart_data, config)
            elif layer_type == 'ccg':
                self._draw_ccg_chart(dwg, chart_data, config)
            else:
                raise ValueError(f"Unsupported layer type: {layer_type}")
        except Exception as e:
            logger.exception(f"Error drawing {layer_type} chart")
            raise Exception(f"Chart drawing failed for {layer_type}: {str(e)}")
            
        return dwg.tostring()

    def _draw_natal_chart(self, dwg, chart_data: Dict, config: Dict):
        """Draw natal chart"""
        try:
            # Draw outer circle (zodiac wheel)
            self._draw_zodiac_wheel(dwg)
            logger.info("✅ Zodiac wheel drawn")
        except Exception as e:
            logger.error(f"❌ Error drawing zodiac wheel: {e}")
            raise
        
        try:
            # Draw house divisions
            houses = chart_data.get('houses', {})
            if houses:
                self._draw_houses(dwg, houses)
                logger.info("✅ Houses drawn")
        except Exception as e:
            logger.error(f"❌ Error drawing houses: {e}")
            raise
        
        try:
            # Draw planets
            planets = chart_data.get('planets', {})
            self._draw_planets(dwg, planets, style='natal')
            logger.info("✅ Planets drawn")
        except Exception as e:
            logger.error(f"❌ Error drawing planets: {e}")
            raise
        
        try:
            # Draw aspects if enabled
            if config.get('show_aspects', True):
                aspects = chart_data.get('aspects', {})
                planets = chart_data.get('planets', {})
                
                # Ensure both aspects and planets are properly formatted for _draw_aspects
                if aspects and planets:
                    self._draw_aspects(dwg, aspects, planets)
                    logger.info("✅ Aspects drawn")
                else:
                    logger.info("⚠️ Aspects skipped (no data)")
        except Exception as e:
            logger.error(f"❌ Error drawing aspects: {e}")
            # Don't re-raise for aspects - it's not critical
            raise

    def _draw_human_design_chart(self, dwg, chart_data: Dict, config: Dict):
        """Draw Human Design chart"""
        # Start with basic natal chart structure
        self._draw_zodiac_wheel(dwg)
        
        # Draw planets with HD-specific styling
        planets = chart_data.get('planets', {})
        self._draw_planets(dwg, planets, style='human_design')
        
        # Add HD-specific elements
        hd_data = chart_data.get('human_design', {})
        if hd_data:
            self._draw_hd_gates(dwg, hd_data.get('gates', {}))
            
        # Add houses
        houses = chart_data.get('houses', {})
        if houses:
            self._draw_houses(dwg, houses)

    def _draw_transit_chart(self, dwg, chart_data: Dict, config: Dict):
        """Draw transit chart (transits around natal)"""
        # Draw zodiac wheel
        self._draw_zodiac_wheel(dwg)
        
        # Draw houses
        houses = chart_data.get('houses', {})
        if houses and 'cusps' in houses:
            self._draw_houses(dwg, houses['cusps'])
        
        # Draw natal planets (inner ring)
        natal_planets = chart_data.get('planets', {})
        self._draw_planets(dwg, natal_planets, style='natal', radius=self.inner_radius + 20)
        
        # Draw transit planets (outer ring)
        transit_data = chart_data.get('transits', {})
        current_planets = transit_data.get('current_planets', {})
        self._draw_planets(dwg, current_planets, style='transit', radius=self.planet_radius)
        
        # Draw transit aspects
        if config.get('show_transit_aspects', True):
            transit_aspects = transit_data.get('aspects', {})
            self._draw_transit_aspects(dwg, transit_aspects, natal_planets, current_planets)

    def _draw_ccg_chart(self, dwg, chart_data: Dict, config: Dict):
        """Draw CCG (Composite/Comparison) chart"""
        # Draw zodiac wheel
        self._draw_zodiac_wheel(dwg)
        
        # For composite charts, draw composite planets
        ccg_data = chart_data.get('ccg', {})
        composite_planets = ccg_data.get('composite_planets', {})
        
        if composite_planets:
            self._draw_planets(dwg, composite_planets, style='composite')
        
        # Draw composite houses if available
        composite_houses = ccg_data.get('composite_houses', {})
        if composite_houses and 'cusps' in composite_houses:
            self._draw_houses(dwg, composite_houses['cusps'])

    def _draw_zodiac_wheel(self, dwg):
        """Draw the basic zodiac wheel with signs and enhanced styling"""
        # Create gradient for zodiac wheel
        wheel_gradient = dwg.defs.add(dwg.radialGradient(id="wheel_gradient", center=(0.5, 0.5)))
        wheel_gradient.add_stop_color(offset=0, color='#f8f8f8')
        wheel_gradient.add_stop_color(offset=1, color='#e0e0e0')
        
        # Outer circle with gradient
        dwg.add(dwg.circle(center=(self.center_x, self.center_y), 
                          r=self.outer_radius, fill='url(#wheel_gradient)', 
                          stroke='#333333', stroke_width=3))
        
        # Inner circle
        dwg.add(dwg.circle(center=(self.center_x, self.center_y), 
                          r=self.inner_radius, fill='white', 
                          stroke='#666666', stroke_width=2))
        
        # Element colors for signs
        element_colors = {
            'fire': '#FF6B6B',    # Aries, Leo, Sagittarius
            'earth': '#8D6E63',   # Taurus, Virgo, Capricorn
            'air': '#64B5F6',     # Gemini, Libra, Aquarius
            'water': '#4FC3F7'    # Cancer, Scorpio, Pisces
        }
        
        elements = ['fire', 'earth', 'air', 'water'] * 3  # Repeat pattern
        
        # Draw zodiac signs with element colors
        for i in range(12):
            angle = i * 30  # Each sign is 30 degrees
            start_angle = math.radians(angle - 90)
            next_angle = math.radians(angle + 30 - 90)
            
            # Element for this sign
            element = elements[i]
            element_color = element_colors[element]
            
            # Create subtle background segments for each sign
            if i % 2 == 0:  # Alternate background colors
                # Create path for sign segment
                large_arc = 0  # 30 degrees is always less than 180
                path_data = f"M {self.center_x + self.inner_radius * math.cos(start_angle)} {self.center_y + self.inner_radius * math.sin(start_angle)} "
                path_data += f"A {self.inner_radius} {self.inner_radius} 0 {large_arc} 1 {self.center_x + self.inner_radius * math.cos(next_angle)} {self.center_y + self.inner_radius * math.sin(next_angle)} "
                path_data += f"L {self.center_x + self.outer_radius * math.cos(next_angle)} {self.center_y + self.outer_radius * math.sin(next_angle)} "
                path_data += f"A {self.outer_radius} {self.outer_radius} 0 {large_arc} 0 {self.center_x + self.outer_radius * math.cos(start_angle)} {self.center_y + self.outer_radius * math.sin(start_angle)} Z"
                
                dwg.add(dwg.path(d=path_data, fill=element_color, opacity=0.1, stroke='none'))
            
            # Sign division lines
            x1 = self.center_x + self.inner_radius * math.cos(start_angle)
            y1 = self.center_y + self.inner_radius * math.sin(start_angle)
            x2 = self.center_x + self.outer_radius * math.cos(start_angle)
            y2 = self.center_y + self.outer_radius * math.sin(start_angle)
            
            dwg.add(dwg.line(start=(x1, y1), end=(x2, y2), 
                           stroke='#999999', stroke_width=1.5, opacity=0.7))
            
            # Sign symbols with enhanced styling
            mid_angle = math.radians(angle + 15 - 90)
            symbol_radius = (self.outer_radius + self.inner_radius) / 2
            symbol_x = self.center_x + symbol_radius * math.cos(mid_angle)
            symbol_y = self.center_y + symbol_radius * math.sin(mid_angle)
            
            sign_symbol = self.sign_symbols.get(angle, '?')
            
            # Add background circle for sign symbol
            dwg.add(dwg.circle(center=(symbol_x, symbol_y), r=12, 
                             fill='white', stroke=element_color, 
                             stroke_width=1.5, opacity=0.9))
            
            dwg.add(dwg.text(sign_symbol, insert=(symbol_x, symbol_y), 
                           text_anchor='middle', dominant_baseline='central',
                           font_size=18, font_family='Arial Unicode MS, Arial', 
                           fill=element_color, font_weight='bold'))
            
            # Add degree markings every 10 degrees
            for deg_offset in [10, 20]:
                deg_angle = math.radians(angle + deg_offset - 90)
                mark_start_radius = self.outer_radius - 8
                mark_end_radius = self.outer_radius - 3
                
                mark_x1 = self.center_x + mark_start_radius * math.cos(deg_angle)
                mark_y1 = self.center_y + mark_start_radius * math.sin(deg_angle)
                mark_x2 = self.center_x + mark_end_radius * math.cos(deg_angle)
                mark_y2 = self.center_y + mark_end_radius * math.sin(deg_angle)
                
                dwg.add(dwg.line(start=(mark_x1, mark_y1), end=(mark_x2, mark_y2),
                               stroke='#666666', stroke_width=1, opacity=0.5))

    def _draw_houses(self, dwg, house_data):
        """Draw house divisions"""
        # Handle different house data formats
        house_cusps = []
        
        if isinstance(house_data, dict):
            if 'cusps' in house_data:
                # Old format: {'cusps': [0, 30, 60, ...]}
                house_cusps = house_data['cusps']
            elif 'houses' in house_data:
                # New format: {'houses': [{'house': 1, 'longitude': 60.0}, ...]}
                houses_list = house_data['houses']
                if isinstance(houses_list, list):
                    # Extract longitudes in house order
                    house_cusps = [None] * 12
                    for house_info in houses_list:
                        if isinstance(house_info, dict) and 'house' in house_info and 'longitude' in house_info:
                            house_num = house_info['house'] - 1  # Convert to 0-based index
                            if 0 <= house_num < 12:
                                house_cusps[house_num] = house_info['longitude']
        elif isinstance(house_data, list):
            # Direct list format
            house_cusps = house_data
            
        if not house_cusps:
            logger.warning("No valid house cusps found")
            return
            
        for i, cusp in enumerate(house_cusps):
            if cusp is not None:
                angle = math.radians(cusp - 90)  # Adjust for chart orientation
                
                # House cusp lines
                x1 = self.center_x + self.inner_radius * math.cos(angle)
                y1 = self.center_y + self.inner_radius * math.sin(angle)
                x2 = self.center_x + (self.inner_radius - 30) * math.cos(angle)
                y2 = self.center_y + (self.inner_radius - 30) * math.sin(angle)
                
                dwg.add(dwg.line(start=(x1, y1), end=(x2, y2), 
                               stroke='blue', stroke_width=1.5))
                
                # House numbers
                text_radius = self.inner_radius - 45
                text_x = self.center_x + text_radius * math.cos(angle)
                text_y = self.center_y + text_radius * math.sin(angle)
                
                dwg.add(dwg.text(str(i + 1), insert=(text_x, text_y), 
                               text_anchor='middle', dominant_baseline='central',
                               font_size=12, font_family='Arial', fill='blue'))

    def _draw_planets(self, dwg, planets: Dict, style: str = 'natal', radius: float = None):
        """Draw planets on the chart with collision detection"""
        if radius is None:
            radius = self.planet_radius
            
        color = self.colors.get(style, 'black')
        
        # Handle both list and dict formats for planets data
        if isinstance(planets, list):
            # Convert list format to dict format
            logger.info(f"Converting planets list to dict. List length: {len(planets)}")
            planets_dict = {}
            for planet in planets:
                if isinstance(planet, dict) and 'name' in planet and 'longitude' in planet:
                    planet_name = planet['name'].lower()
                    planets_dict[planet_name] = planet
                    logger.debug(f"Added planet: {planet_name}")
                else:
                    logger.warning(f"Invalid planet entry: {planet}")
            planets = planets_dict
            logger.info(f"Converted to dict with {len(planets)} planets")
        elif not isinstance(planets, dict):
            logger.warning(f"Invalid planets data type: {type(planets)}")
            return
        
        # Ensure planets is actually a dict before proceeding
        if not isinstance(planets, dict):
            logger.error(f"Planets is not a dict after conversion: {type(planets)}")
            return
        
        # Sort planets by longitude for better positioning
        try:
            sorted_planets = sorted(
                [(name, data) for name, data in planets.items() 
                 if isinstance(data, dict) and 'longitude' in data],
                key=lambda x: x[1]['longitude']
            )
        except Exception as e:
            logger.error(f"Error sorting planets: {e}")
            logger.error(f"Planets type: {type(planets)}, content: {planets}")
            return
        
        # Track occupied positions to avoid overlaps
        occupied_positions = []
        min_distance = 15  # Minimum distance between planet symbols
        
        logger.info(f"About to process {len(sorted_planets)} planets for tooltips")
        
        for planet_name, planet_data in sorted_planets:
            logger.info(f"Processing planet {planet_name} for tooltip")
            longitude = planet_data['longitude']
            original_angle = math.radians(longitude - 90)
            
            # Find best position avoiding collisions
            best_angle = original_angle
            best_radius = radius
            
            # Try different radial positions if there's a collision
            for radius_offset in [0, -15, 15, -30, 30]:
                test_radius = radius + radius_offset
                test_x = self.center_x + test_radius * math.cos(original_angle)
                test_y = self.center_y + test_radius * math.sin(original_angle)
                
                # Check for collisions with existing planets
                collision = False
                for occupied_x, occupied_y in occupied_positions:
                    distance = math.sqrt((test_x - occupied_x)**2 + (test_y - occupied_y)**2)
                    if distance < min_distance:
                        collision = True
                        break
                
                if not collision:
                    best_radius = test_radius
                    break
            
            # Calculate final position
            x = self.center_x + best_radius * math.cos(best_angle)
            y = self.center_y + best_radius * math.sin(best_angle)
            
            occupied_positions.append((x, y))
            
            # Planet symbol with enhanced styling
            symbol = self.planet_symbols.get(planet_name.lower(), planet_name[:2].upper())
            
            # Draw planet background circle with gradient effect
            # Sanitize gradient ID to remove spaces and special characters
            sanitized_name = planet_name.replace(' ', '_').replace('-', '_').lower()
            gradient_id = f"gradient_{sanitized_name}_{style}"
            gradient = dwg.defs.add(dwg.radialGradient(id=gradient_id, center=(0.3, 0.3)))
            gradient.add_stop_color(offset=0, color='white')
            gradient.add_stop_color(offset=1, color=color, opacity=0.8)
            
            # Create tooltip information
            degree = longitude % 30
            sign_index = int(longitude // 30)
            sign_symbol = list(self.sign_symbols.values())[sign_index]
            sign_name = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 
                        'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'][sign_index]
            
            # Format planet name for display
            display_name = planet_name.replace('_', ' ').title()
            
            # Create tooltip text with planet information
            tooltip_text = f"{display_name}\n{degree:.1f}° {sign_name}\nLongitude: {longitude:.2f}°"
            
            # Add additional planet data if available
            if isinstance(planet_data, dict):
                if 'declination' in planet_data:
                    tooltip_text += f"\nDeclination: {planet_data['declination']:.2f}°"
                if 'distance' in planet_data:
                    tooltip_text += f"\nDistance: {planet_data['distance']:.2f} AU"
                if 'speed' in planet_data:
                    tooltip_text += f"\nSpeed: {planet_data['speed']:.2f}°/day"
                if 'house' in planet_data:
                    tooltip_text += f"\nHouse: {planet_data['house']}"
            
            # Create a group for the planet with tooltip
            logger.info(f"Creating tooltip group for {planet_name}")
            planet_group = dwg.g(class_=f"planet-{sanitized_name}")
            
            # Add SVG tooltip using Title element
            logger.info(f"Adding tooltip: {tooltip_text}")
            title_element = Title(tooltip_text)
            planet_group.add(title_element)
            
            # Planet circle with enhanced styling and better contrast
            planet_group.add(dwg.circle(center=(x, y), r=12, fill=f'url(#{gradient_id})', 
                             stroke='#333333', stroke_width=2.5, opacity=1.0))
            
            # Draw planet symbol with high contrast
            symbol_color = '#000000' if style == 'natal' else color  # Use black for better readability
            planet_group.add(dwg.text(symbol, insert=(x, y), 
                           text_anchor='middle', dominant_baseline='central',
                           font_size=14, font_family='Arial Unicode MS, Arial', 
                           fill=symbol_color, font_weight='bold', 
                           stroke='white', stroke_width=0.5))  # Add white outline for contrast
            
            # Add the planet group to the drawing
            dwg.add(planet_group)
            logger.info(f"Added planet group {sanitized_name} with tooltip to SVG")
            
            # Add degree marking with sign (outside the group for better positioning)
            degree_text = f"{degree:.0f}°{sign_symbol}"
            
            # Position degree text to avoid overlap
            text_y_offset = 25 if best_radius == radius else (30 if best_radius > radius else 20)
            dwg.add(dwg.text(degree_text, insert=(x, y + text_y_offset), 
                           text_anchor='middle', dominant_baseline='central',
                           font_size=9, font_family='Arial', fill=color, opacity=0.8))

    def _draw_aspects(self, dwg, aspects: Dict, planets: Dict):
        """Draw aspect lines between planets"""
        if not aspects:
            return
        
        # Handle both list and dict formats for aspects
        if isinstance(aspects, list):
            # List format: aspects is a list of aspect objects
            for aspect in aspects:
                if isinstance(aspect, dict):
                    planet1 = aspect.get('planet1', '').lower()
                    planet2 = aspect.get('planet2', '').lower()
                    
                    # Convert planets list to dict if needed
                    planets_dict = planets
                    if isinstance(planets, list):
                        planets_dict = {p['name'].lower(): p for p in planets if isinstance(p, dict) and 'name' in p}
                    
                    if planet1 in planets_dict and planet2 in planets_dict:
                        self._draw_aspect_line(dwg, planets_dict[planet1], planets_dict[planet2], aspect)
        elif isinstance(aspects, dict):
            # Dict format: aspects organized by type
            for aspect_name, aspect_list in aspects.items():
                if isinstance(aspect_list, list):
                    for aspect in aspect_list:
                        planet1 = aspect.get('planet1', '').lower()
                        planet2 = aspect.get('planet2', '').lower()
                        
                        # Convert planets list to dict if needed
                        planets_dict = planets
                        if isinstance(planets, list):
                            planets_dict = {p['name'].lower(): p for p in planets if isinstance(p, dict) and 'name' in p}
                        
                        if planet1 in planets_dict and planet2 in planets_dict:
                            self._draw_aspect_line(dwg, planets_dict[planet1], planets_dict[planet2], aspect)

    def _draw_aspect_line(self, dwg, planet1_data: Dict, planet2_data: Dict, aspect: Dict):
        """Draw a single aspect line with enhanced styling"""
        if not all(isinstance(p, dict) and 'longitude' in p for p in [planet1_data, planet2_data]):
            return
            
        lon1 = planet1_data['longitude']
        lon2 = planet2_data['longitude']
        
        angle1 = math.radians(lon1 - 90)
        angle2 = math.radians(lon2 - 90)
        
        # Calculate positions on inner circle
        aspect_radius = self.inner_radius - 20
        x1 = self.center_x + aspect_radius * math.cos(angle1)
        y1 = self.center_y + aspect_radius * math.sin(angle1)
        x2 = self.center_x + aspect_radius * math.cos(angle2)
        y2 = self.center_y + aspect_radius * math.sin(angle2)
        
        # Determine aspect properties
        aspect_type = aspect.get('aspect', '').lower()
        orb = aspect.get('orb', 0)
        
        # Enhanced aspect styling based on type and orb
        if aspect_type == 'conjunction':
            color = '#4169E1'  # Royal Blue
            stroke_width = 3
            stroke_dasharray = None
            opacity = 0.8
        elif aspect_type == 'opposition':
            color = '#DC143C'  # Crimson
            stroke_width = 3
            stroke_dasharray = None
            opacity = 0.8
        elif aspect_type == 'trine':
            color = '#228B22'  # Forest Green
            stroke_width = 2.5
            stroke_dasharray = None
            opacity = 0.7
        elif aspect_type == 'square':
            color = '#FF4500'  # Orange Red
            stroke_width = 2.5
            stroke_dasharray = None
            opacity = 0.7
        elif aspect_type == 'sextile':
            color = '#9932CC'  # Dark Orchid
            stroke_width = 2
            stroke_dasharray = None
            opacity = 0.6
        elif aspect_type == 'quincunx':
            color = '#708090'  # Slate Gray
            stroke_width = 1.5
            stroke_dasharray = '5,3'
            opacity = 0.5
        elif aspect_type == 'semisextile':
            color = '#A0A0A0'  # Light Gray
            stroke_width = 1
            stroke_dasharray = '3,2'
            opacity = 0.4
        else:
            color = '#888888'  # Default gray
            stroke_width = 1
            stroke_dasharray = '2,2'
            opacity = 0.3
        
        # Adjust opacity based on orb tightness
        if orb <= 1:
            opacity *= 1.2  # Tighter orbs are more prominent
        elif orb >= 5:
            opacity *= 0.6  # Wider orbs are less prominent
            
        opacity = min(opacity, 1.0)  # Ensure opacity doesn't exceed 1
        
        # Create the aspect line with enhanced styling
        line_attrs = {
            'start': (x1, y1),
            'end': (x2, y2),
            'stroke': color,
            'stroke_width': stroke_width,
            'opacity': opacity
        }
        
        if stroke_dasharray:
            line_attrs['stroke_dasharray'] = stroke_dasharray
            
        dwg.add(dwg.line(**line_attrs))
        
        # Add orb information as a small text near the midpoint
        if aspect.get('show_orb', False):
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2
            orb_text = f"{orb:.1f}°"
            dwg.add(dwg.text(orb_text, insert=(mid_x, mid_y), 
                           text_anchor='middle', dominant_baseline='central',
                           font_size=8, font_family='Arial', fill=color, 
                           opacity=0.7, font_weight='bold'))

    def _draw_hd_gates(self, dwg, gates: Dict):
        """Draw Human Design gates"""
        # This is a simplified representation
        # In a full HD chart, gates would be positioned around the wheel
        for gate_num, gate_info in gates.items():
            # Position gates around the outer edge
            # This would need proper HD gate positioning logic
            pass

    def _draw_transit_aspects(self, dwg, transit_aspects: Dict, natal_planets: Dict, transit_planets: Dict):
        """Draw aspects between transit and natal planets"""
        # Similar to _draw_aspects but between different planet sets
        pass

    def _add_chart_title_and_legend(self, dwg, chart_data: Dict, layer_type: str, config: Dict):
        """Add chart title and legend"""
        # Chart title
        title_text = self._get_chart_title(chart_data, layer_type)
        dwg.add(dwg.text(title_text, insert=(self.center_x, 30), 
                       text_anchor='middle', dominant_baseline='central',
                       font_size=16, font_family='Arial', font_weight='bold',
                       fill='#333333'))
        
        # Birth info subtitle
        subtitle = self._get_chart_subtitle(chart_data)
        if subtitle:
            dwg.add(dwg.text(subtitle, insert=(self.center_x, 50), 
                           text_anchor='middle', dominant_baseline='central',
                           font_size=12, font_family='Arial', fill='#666666'))
        
        # Legend (if enabled)
        if config.get('show_legend', True):
            self._draw_legend(dwg, layer_type, config)
    
    def _get_chart_title(self, chart_data: Dict, layer_type: str) -> str:
        """Generate appropriate chart title"""
        titles = {
            'natal': 'Natal Chart',
            'human_design': 'Human Design Chart', 
            'transit': 'Transit Chart',
            'ccg': 'Composite Chart'
        }
        
        base_title = titles.get(layer_type, 'Astrological Chart')
        
        # Add name if available
        name = chart_data.get('name') or chart_data.get('birth_name')
        if name:
            return f"{base_title} - {name}"
        
        return base_title
    
    def _get_chart_subtitle(self, chart_data: Dict) -> str:
        """Generate chart subtitle with birth info"""
        date = chart_data.get('birth_date', '')
        time = chart_data.get('birth_time', '')
        city = chart_data.get('birth_city', '')
        
        if date and time:
            subtitle_parts = [f"{date} at {time}"]
            if city:
                subtitle_parts.append(city)
            return " | ".join(subtitle_parts)
        
        return ""
    
    def _draw_legend(self, dwg, layer_type: str, config: Dict):
        """Draw chart legend"""
        # Position legend to the right of the chart, outside the main chart area
        legend_x = self.width + 20  # Move legend outside the chart area
        legend_y = 60
        
        # Legend background - make it slightly larger for better visibility
        dwg.add(dwg.rect(insert=(legend_x - 10, legend_y - 10), 
                        size=(160, 220), fill='white', stroke='#666666',
                        stroke_width=2, opacity=0.95, rx=8))
        
        # Legend title
        dwg.add(dwg.text("Legend", insert=(legend_x, legend_y + 10), 
                       font_size=14, font_family='Arial', font_weight='bold',
                       fill='#222222'))
        
        legend_items = []
        
        # Planet legend
        if layer_type in ['natal', 'human_design']:
            legend_items.extend([
                ("☉", "Sun", "#333333"),
                ("☽", "Moon", "#333333"),
                ("☿", "Mercury", "#333333"),
                ("♀", "Venus", "#333333"),
                ("♂", "Mars", "#333333")
            ])
        elif layer_type == 'transit':
            legend_items.extend([
                ("●", "Natal", "#000000"),
                ("●", "Transit", "#ff6600")
            ])
        
        # Aspect legend
        if config.get('show_aspects', True):
            legend_items.extend([
                ("—", "Conjunction", "#4169E1"),
                ("—", "Opposition", "#DC143C"),
                ("—", "Trine", "#228B22"),
                ("—", "Square", "#FF4500"),
                ("—", "Sextile", "#9932CC")
            ])
        
        # Draw legend items
        for i, (symbol, label, color) in enumerate(legend_items):
            y_pos = legend_y + 30 + (i * 20)  # Increase spacing slightly
            
            # Symbol with better contrast
            dwg.add(dwg.text(symbol, insert=(legend_x, y_pos), 
                           font_size=14, font_family='Arial Unicode MS, Arial',
                           fill='#222222', font_weight='bold'))  # Use dark color for better visibility
            
            # Label
            dwg.add(dwg.text(label, insert=(legend_x + 25, y_pos), 
                           font_size=11, font_family='Arial', fill='#333333'))


def generate_chart_svg(chart_data: Dict, layer_type: str, config: Dict = None) -> Dict:
    """
    Main function to generate SVG chart
    """
    try:
        if config is None:
            config = {}
            
        width = config.get('width', 600)
        height = config.get('height', 600)
        
        # Log the chart data structure for debugging
        logger.info(f"Generating {layer_type} chart")
        logger.info(f"Chart data keys: {list(chart_data.keys())}")
        logger.info(f"Planets type: {type(chart_data.get('planets'))}")
        logger.info(f"Houses type: {type(chart_data.get('houses'))}")
        logger.info(f"Aspects type: {type(chart_data.get('aspects'))}")
        
        renderer = AstroChartRenderer(width, height)
        svg_content = renderer.create_chart_svg(chart_data, layer_type, config)
        
        return {
            "svg": svg_content,
            "layer_type": layer_type,
            "width": width,
            "height": height
        }
        
    except Exception as e:
        logger.exception(f"Error generating {layer_type} chart SVG")
        return {"error": str(e)}
