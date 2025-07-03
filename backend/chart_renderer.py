#!/usr/bin/env python3
"""
SVG Chart Renderer for Meridian Map
Generates SVG astrological charts for different layers using svgwrite
"""

import svgwrite
# from svgwrite.base import Title  # Tooltip functionality disabled
import math
import logging
import traceback
from typing import Dict, List, Tuple, Any, Optional

logger = logging.getLogger(__name__)

# --- Constants ---
PLANET_SYMBOLS = {
    'sun': '☉', 'moon': '☽', 'mercury': '☿', 'venus': '♀', 'mars': '♂',
    'jupiter': '♃', 'saturn': '♄', 'uranus': '♅', 'neptune': '♆', 'pluto': '♇',
    'north_node': '☊', 'south_node': '☋', 'chiron': '⚷', 'ascendant': 'ASC',
    'midheaven': 'MC', 'descendant': 'DSC', 'imum_coeli': 'IC'
}

ZODIAC_SIGNS = {
    'Aries': 0, 'Taurus': 30, 'Gemini': 60, 'Cancer': 90, 'Leo': 120, 'Virgo': 150,
    'Libra': 180, 'Scorpio': 210, 'Sagittarius': 240, 'Capricorn': 270, 'Aquarius': 300, 'Pisces': 330
}

ASPECT_COLORS = {
    'conjunction': '#4169E1', 'opposition': '#DC143C', 'trine': '#228B22',
    'square': '#FF4500', 'sextile': '#9932CC', 'quincunx': '#708090',
    'semisextile': '#A0A0A0'
}

ASPECT_STYLES = {
    'conjunction': None, 'opposition': None, 'trine': None, 'square': None,
    'sextile': None, 'quincunx': '5,3', 'semisextile': '3,2'
}


def generate_chart_svg(chart_data, chart_config):
    """
    Generates a clean, beautiful SVG for a single-wheel chart (natal, transit, etc.).
    """
    try:
        logger.info(f"Starting chart generation with config: {chart_config}")
        
        # Add validation for chart_data
        if not chart_data or not isinstance(chart_data, dict):
            logger.error(f"Invalid chart_data: {chart_data}")
            raise ValueError("chart_data must be a non-empty dictionary")
        
        width = chart_config.get('width', 600)
        height = chart_config.get('height', 600)
        center_x, center_y = width / 2, height / 2
        
        # Improved radius calculations for better separation and readability
        outer_radius = min(center_x, center_y) - 30
        zodiac_radius = outer_radius - 30  # Move zodiac band slightly inward
        zodiac_label_radius = outer_radius - 5  # New: zodiac names outside the wheel
        house_radius = zodiac_radius - 35  # Move house numbers further in
        planet_radius = zodiac_radius - 10  # Planets just inside zodiac band, above houses
        inner_radius = house_radius - 70

        # Improved defensive data extraction
        def safe_extract_data(data, key):
            """Safely extract list data from potentially nested structures"""
            if not data or not isinstance(data, dict):
                return []
            
            value = data.get(key, [])
            
            # If value is None, return empty list
            if value is None:
                return []
            
            # If value is already a list, return it
            if isinstance(value, list):
                return value
            
            # If value is a dict, try to find nested list
            if isinstance(value, dict):
                # Look for common nested keys
                for nested_key in [key, 'data', 'items']:
                    if nested_key in value and isinstance(value[nested_key], list):
                        return value[nested_key]
                return []
            
            # Try to convert to list if it's iterable
            try:
                return list(value) if hasattr(value, '__iter__') and not isinstance(value, str) else []
            except:
                return []

        planets = safe_extract_data(chart_data, 'planets')
        houses = safe_extract_data(chart_data, 'houses')
        aspects = safe_extract_data(chart_data, 'aspects')

        # Debug logging
        logger.info(f"Chart data summary - Houses: {len(houses)}, Planets: {len(planets)}, Aspects: {len(aspects)}")
        logger.debug(f"Chart data keys: {list(chart_data.keys())}")

        # Create SVG drawing with clean white background
        dwg = svgwrite.Drawing(size=(width, height))
        dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), fill='#fafafa'))

        renderer = ChartRenderer(dwg, width, height, chart_config, chart_data)
        
        # Render components in order for clean layering
        logger.debug("Drawing clean chart base...")
        renderer._draw_clean_base(outer_radius, zodiac_radius, house_radius, inner_radius)
        
        logger.debug("Drawing zodiac signs...")
        renderer._draw_clean_zodiac(zodiac_radius, zodiac_label_radius)
        
        logger.debug("Drawing house numbers...")
        renderer._draw_clean_houses(house_radius)
        
        logger.debug("Drawing planets...")
        renderer._draw_clean_planets(planets, planet_radius)
        
        if chart_config.get('show_aspects', True):
            logger.debug("Drawing aspects...")
            renderer._draw_clean_aspects(aspects, planet_radius)

        # Add a clean title
        layer_type = chart_config.get('layer_type', 'chart')
        title_text = f"{layer_type.title()} Chart"
        if chart_data.get('input', {}).get('birth_date'):
            title_text += f" - {chart_data['input']['birth_date']}"
        
        dwg.add(dwg.text(
            title_text, 
            insert=(center_x, 25), 
            text_anchor='middle', 
            font_size=18, 
            fill='#2c3e50',
            font_family="Arial, sans-serif",
            font_weight="bold"
        ))

        logger.info("Chart generation completed successfully")
        return dwg.tostring()
        
    except Exception as e:
        logger.error(f"Error in generate_chart_svg: {str(e)}")
        logger.error(f"Chart data keys: {list(chart_data.keys()) if chart_data else 'None'}")
        logger.error(f"Chart config: {chart_config}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise

class ChartRenderer:
    def __init__(self, dwg, width, height, chart_config, chart_data):
        self.dwg = dwg
        self.width = width
        self.height = height
        self.chart_config = chart_config
        self.chart_data = chart_data
        self.center_x = width / 2
        self.center_y = height / 2
        self.outer_radius = min(width, height) / 2 - 20
        self.inner_radius = self.outer_radius - 100
        self.planet_radius = self.outer_radius - 30

    def _draw_zodiac_signs(self, outer_radius, zodiac_band_width):
        """Draws the zodiac signs around the chart."""
        for sign, angle in ZODIAC_SIGNS.items():
            # Calculate position
            x = self.center_x + (outer_radius - zodiac_band_width / 2) * math.cos(math.radians(angle))
            y = self.center_y + (outer_radius - zodiac_band_width / 2) * math.sin(math.radians(angle))
            
            # Draw the sign symbol
            self.dwg.add(self.dwg.text(sign, insert=(x, y), text_anchor="middle", alignment_baseline="middle", font_size="12", fill="#333"))
    
    def _draw_house_cusps(self, house_cusp_radius):
        """Draws the house cusps on the chart using actual house data."""
        house_data = self.chart_data.get('houses', {})
        
        # Extract the actual house list from the nested structure
        if isinstance(house_data, dict):
            houses = house_data.get('houses', [])
        else:
            houses = house_data if isinstance(house_data, list) else []
        
        if not houses:
            # Fallback to equal houses if no house data
            for i in range(12):
                angle = i * 30  # 30 degrees per house
                x = self.center_x + house_cusp_radius * math.cos(math.radians(angle))
                y = self.center_y + house_cusp_radius * math.sin(math.radians(angle))
                self.dwg.add(self.dwg.line(start=(self.center_x, self.center_y), end=(x, y), stroke="#999", stroke_width=1))
        else:
            # Use actual house cusp positions
            for house in houses:
                if isinstance(house, dict):
                    cusp_longitude = house.get('longitude', 0)
                    angle = self._get_planet_angle(cusp_longitude)
                    x = self.center_x + house_cusp_radius * math.cos(math.radians(angle))
                    y = self.center_y + house_cusp_radius * math.sin(math.radians(angle))
                    self.dwg.add(self.dwg.line(start=(self.center_x, self.center_y), end=(x, y), stroke="#999", stroke_width=1))
    
    def _draw_house_segments(self, outer_radius, inner_radius):
        """Draws the segments of the houses."""
        for i in range(12):
            angle = i * 30  # 30 degrees per house
            next_angle = (i + 1) * 30
            
            # Calculate points for the house segment
            p1 = (self.center_x + outer_radius * math.cos(math.radians(angle)), self.center_y + outer_radius * math.sin(math.radians(angle)))
            p2 = (self.center_x + inner_radius * math.cos(math.radians(angle)), self.center_y + inner_radius * math.sin(math.radians(angle)))
            p3 = (self.center_x + inner_radius * math.cos(math.radians(next_angle)), self.center_y + inner_radius * math.sin(math.radians(next_angle)))
            p4 = (self.center_x + outer_radius * math.cos(math.radians(next_angle)), self.center_y + outer_radius * math.sin(math.radians(next_angle)))
            
            # Draw the house segment
            self.dwg.add(self.dwg.polygon(points=[p1, p2, p3, p4], fill="none", stroke="#ccc", stroke_width=1))
    
    def _draw_houses(self, inner_radius, house_cusp_radius):
        """Draws the house numbers and areas on the chart."""
        house_data = self.chart_data.get('houses', {})
        
        # Extract the actual house list from the nested structure
        if isinstance(house_data, dict):
            houses = house_data.get('houses', [])
        else:
            houses = house_data if isinstance(house_data, list) else []
        
        logger.debug(f"Drawing houses - house_data type: {type(house_data)}")
        logger.debug(f"houses count: {len(houses)}")
        if houses and len(houses) > 0:
            logger.debug(f"First house: {houses[0]}")
        
        # Always draw 12 houses using the simplest approach for now
        for i in range(12):
            house_num = i + 1
            
            # Use simple equal house division for now to get house numbers working
            chart_angle = i * 30 + 15 - 90  # Middle of house segment, adjusted for chart orientation
            
            # Draw house number
            text_radius = (inner_radius + house_cusp_radius) / 2
            x = self.center_x + text_radius * math.cos(math.radians(chart_angle))
            y = self.center_y + text_radius * math.sin(math.radians(chart_angle))
            
            logger.debug(f"House {house_num}: angle={chart_angle}, position=({x:.1f}, {y:.1f})")
            
            # Make house numbers more prominent and visible
            self.dwg.add(self.dwg.text(
                str(house_num), 
                insert=(x, y), 
                text_anchor="middle", 
                alignment_baseline="middle", 
                font_size="20", 
                font_weight="bold",
                fill="#FF0000",  # Red color to make them obvious
                stroke="white",
                stroke_width="1"
            ))
    
    def _draw_planets(self, planets, radius):
        """Draws planets on the chart."""
        logger.info(f"Drawing {len(planets)} planets at radius {radius}")
        
        if not planets:
            logger.warning("No planets data provided to _draw_planets")
            return
            
        for i, planet in enumerate(planets):
            logger.debug(f"Drawing planet {i}: {planet}")
            
            # Validate planet data
            if 'longitude' not in planet:
                logger.error(f"Planet missing longitude: {planet}")
                continue
            if 'name' not in planet:
                logger.error(f"Planet missing name: {planet}")
                continue
                
            angle = self._get_planet_angle(planet['longitude'])
            x = self.center_x + radius * math.cos(math.radians(angle))
            y = self.center_y + radius * math.sin(math.radians(angle))
            
            logger.debug(f"Planet {planet['name']}: longitude={planet['longitude']}, angle={angle}, position=({x:.1f}, {y:.1f})")
            
            fill_color = '#4a4a4a' # Standard color for all planets in a single wheel

            symbol = PLANET_SYMBOLS.get(planet['name'], planet['name'][:3].upper())  # Use first 3 letters as fallback
            logger.debug(f"Planet {planet['name']} symbol: '{symbol}'")
            
            # Add a small circle as position marker
            circle = self.dwg.circle(
                center=(x, y),
                r=8,
                fill='none',
                stroke='red',
                stroke_width=1
            )
            self.dwg.add(circle)
            
            # Add planet symbol with better visibility
            planet_text = self.dwg.text(
                symbol, 
                insert=(x, y), 
                text_anchor="middle", 
                alignment_baseline="middle", 
                font_size="16",  # Increased font size
                fill=fill_color,
                font_family="Arial, sans-serif"  # Explicit font family
            )
            self.dwg.add(planet_text)
            
            # Also add planet name as backup
            name_text = self.dwg.text(
                planet['name'][:3], 
                insert=(x + 20, y), 
                text_anchor="middle", 
                alignment_baseline="middle", 
                font_size="10",
                fill="#666",
                font_family="Arial, sans-serif"
            )
            self.dwg.add(name_text)
            
            # Add degree/minute labels
            degrees = int(planet['longitude'] % 30)
            minutes = int((planet['longitude'] % 1) * 60)
            
            text_group = self.dwg.g()
            text_group.add(self.dwg.text(f"{degrees}°", insert=(x, y + 12), text_anchor="middle", font_size="10", fill=fill_color))
            text_group.add(self.dwg.text(f"{minutes}'", insert=(x, y + 22), text_anchor="middle", font_size="8", fill=fill_color))
            self.dwg.add(text_group)

    def _draw_aspects(self, aspects, planet_radius):
        """Draws aspect lines between planets on a single wheel."""
        if not aspects:
            logger.info("No aspects data to draw")
            return

        logger.info(f"Drawing {len(aspects)} aspects")
        
        for aspect in aspects:
            try:
                planet1_name = aspect.get('planet1')
                planet2_name = aspect.get('planet2')
                aspect_type = aspect.get('aspect')
                
                if not all([planet1_name, planet2_name, aspect_type]):
                    continue

                planet1 = self._find_planet(planet1_name, self.chart_data['planets'])
                planet2 = self._find_planet(planet2_name, self.chart_data['planets'])

                if planet1 and planet2:
                    angle1 = self._get_planet_angle(planet1['longitude'])
                    angle2 = self._get_planet_angle(planet2['longitude'])

                    x1 = self.center_x + planet_radius * math.cos(math.radians(angle1))
                    y1 = self.center_y + planet_radius * math.sin(math.radians(angle1))
                    x2 = self.center_x + planet_radius * math.cos(math.radians(angle2))
                    y2 = self.center_y + planet_radius * math.sin(math.radians(angle2))

                    color = ASPECT_COLORS.get(aspect_type.lower(), '#888888')
                    stroke_dasharray = ASPECT_STYLES.get(aspect_type.lower())

                    line = self.dwg.line(start=(x1, y1), end=(x2, y2), stroke=color, stroke_width=2, opacity=0.7)
                    if stroke_dasharray:
                        line.dasharray(stroke_dasharray)
                    self.dwg.add(line)
                    
            except Exception as e:
                logger.error(f"Error drawing aspect {aspect}: {e}")
                continue

    def _find_planet(self, planet_name, planet_list):
        """Finds a planet in a given list of planets."""
        for planet in planet_list:
            if planet['name'].lower() == planet_name.lower():
                return planet
        return None

    def _get_planet_angle(self, longitude):
        """Converts a planet's longitude to an angle for positioning."""
        return longitude - 90  # Adjusting for chart orientation

    def _draw_clean_base(self, outer_radius, zodiac_radius, house_radius, inner_radius):
        """Draw clean base circles and structure."""
        # Outer circle (chart boundary)
        self.dwg.add(self.dwg.circle(
            center=(self.center_x, self.center_y),
            r=outer_radius,
            fill='none',
            stroke='#34495e',
            stroke_width=2
        ))
        
        # Zodiac circle
        self.dwg.add(self.dwg.circle(
            center=(self.center_x, self.center_y),
            r=zodiac_radius,
            fill='none',
            stroke='#7f8c8d',
            stroke_width=1
        ))
        
        # House circle
        self.dwg.add(self.dwg.circle(
            center=(self.center_x, self.center_y),
            r=house_radius,
            fill='none',
            stroke='#bdc3c7',
            stroke_width=1
        ))
        
        # Inner circle
        self.dwg.add(self.dwg.circle(
            center=(self.center_x, self.center_y),
            r=inner_radius,
            fill='none',
            stroke='#ecf0f1',
            stroke_width=1
        ))

    def _draw_clean_zodiac(self, zodiac_radius, zodiac_label_radius):
        """Draw clean zodiac signs with degree markings around the chart, and zodiac names outside the wheel."""
        zodiac_signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
                       'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
        for i, sign in enumerate(zodiac_signs):
            angle = i * 30 - 90  # Start from top (Aries)
            # Zodiac sign names outside the wheel
            x = self.center_x + zodiac_label_radius * math.cos(math.radians(angle + 15))
            y = self.center_y + zodiac_label_radius * math.sin(math.radians(angle + 15))
            self.dwg.add(self.dwg.text(
                sign,
                insert=(x, y),
                text_anchor="middle",
                alignment_baseline="middle",
                font_size="13",
                fill='#34495e',
                font_family="Arial, sans-serif",
                font_weight="600"
            ))
            # Draw main zodiac division lines (every 30 degrees) - make them bolder
            line_start_x = self.center_x + zodiac_radius * math.cos(math.radians(angle))
            line_start_y = self.center_y + zodiac_radius * math.sin(math.radians(angle))
            line_end_x = self.center_x + (zodiac_label_radius) * math.cos(math.radians(angle))
            line_end_y = self.center_y + (zodiac_label_radius) * math.sin(math.radians(angle))
            self.dwg.add(self.dwg.line(
                start=(line_start_x, line_start_y),
                end=(line_end_x, line_end_y),
                stroke='#2c3e50',
                stroke_width=3
            ))
            # Add 10-degree tick marks for easier degree reading
            for tick in [10, 20]:
                tick_angle = angle + tick
                tick_start_x = self.center_x + zodiac_radius * math.cos(math.radians(tick_angle))
                tick_start_y = self.center_y + zodiac_radius * math.sin(math.radians(tick_angle))
                tick_end_x = self.center_x + (zodiac_radius + 12) * math.cos(math.radians(tick_angle))
                tick_end_y = self.center_y + (zodiac_radius + 12) * math.sin(math.radians(tick_angle))
                self.dwg.add(self.dwg.line(
                    start=(tick_start_x, tick_start_y),
                    end=(tick_end_x, tick_end_y),
                    stroke='#34495e',
                    stroke_width=2
                ))
            # Add 5-degree tick marks for even finer degree reading
            for tick in [5, 15, 25]:
                tick_angle = angle + tick
                tick_start_x = self.center_x + zodiac_radius * math.cos(math.radians(tick_angle))
                tick_start_y = self.center_y + zodiac_radius * math.sin(math.radians(tick_angle))
                tick_end_x = self.center_x + (zodiac_radius + 8) * math.cos(math.radians(tick_angle))
                tick_end_y = self.center_y + (zodiac_radius + 8) * math.sin(math.radians(tick_angle))
                self.dwg.add(self.dwg.line(
                    start=(tick_start_x, tick_start_y),
                    end=(tick_end_x, tick_end_y),
                    stroke='#7f8c8d',
                    stroke_width=1
                ))

    def _draw_clean_houses(self, house_radius):
        """Draw clean house numbers, further inside to avoid overlap with planets."""
        for i in range(12):
            house_num = i + 1
            angle = i * 30 + 15 - 90  # Middle of house segment
            text_radius = house_radius - 25  # Move house numbers further in
            x = self.center_x + text_radius * math.cos(math.radians(angle))
            y = self.center_y + text_radius * math.sin(math.radians(angle))
            self.dwg.add(self.dwg.text(
                str(house_num),
                insert=(x, y),
                text_anchor="middle",
                alignment_baseline="middle",
                font_size="16",
                fill='#e74c3c',
                font_family="Arial, sans-serif",
                font_weight="bold"
            ))

    def _draw_clean_planets(self, planets, radius):
        """Draw planets with clean, readable styling, just inside the zodiac band. (Tooltips temporarily disabled)"""
        logger.info(f"Drawing {len(planets)} planets at radius {radius}")
        if not planets:
            logger.warning("No planets data provided to _draw_clean_planets")
            return
        planet_colors = {
            'sun': '#f39c12',
            'moon': '#8e44ad', 
            'mercury': '#3498db',
            'venus': '#e91e63',
            'mars': '#e74c3c',
            'jupiter': '#2ecc71',
            'saturn': '#34495e',
            'uranus': '#1abc9c',
            'neptune': '#9b59b6',
            'pluto': '#795548'
        }
        # from svgwrite.base import Title  # Tooltip logic disabled
        for i, planet in enumerate(planets):
            if 'longitude' not in planet or 'name' not in planet:
                continue
            angle = self._get_planet_angle(planet['longitude'])
            x = self.center_x + radius * math.cos(math.radians(angle))
            y = self.center_y + radius * math.sin(math.radians(angle))
            planet_name = planet['name'].lower()
            color = planet_colors.get(planet_name, '#2c3e50')
            # Tooltip logic disabled
            # tooltip = planet['name'].capitalize()
            # if 'sign' in planet and 'degree' in planet:
            #     tooltip += f"\n{planet['sign']} {planet['degree']}
            # if 'house' in planet:
            #     tooltip += f"\nHouse {planet['house']}"
            planet_group = self.dwg.g()
            planet_group.add(self.dwg.circle(
                center=(x, y),
                r=15,
                fill=color,
                stroke='#fff',
                stroke_width=2,
                opacity=0.95
            ))
            planet_group.add(self.dwg.text(
                PLANET_SYMBOLS.get(planet_name, '?'),
                insert=(x, y+2),
                text_anchor="middle",
                alignment_baseline="middle",
                font_size="18",
                fill='#fff',
                font_family="Arial, sans-serif",
                font_weight="bold"
            ))
            # planet_group.add(Title(tooltip))  # Tooltip logic disabled
            self.dwg.add(planet_group)

    def _draw_clean_aspects(self, aspects, planet_radius):
        """Draw aspect lines with a colorful, visually distinct palette."""
        if not aspects:
            return
        # Colorful aspect palette
        colorful_aspect_colors = {
            'conjunction': '#e74c3c',     # Red
            'opposition': '#2980b9',      # Blue
            'trine': '#27ae60',           # Green
            'square': '#f1c40f',          # Yellow
            'sextile': '#8e44ad',         # Purple
            'quincunx': '#16a085',        # Teal
            'semisextile': '#e67e22'      # Orange
        }
        for aspect in aspects:
            planet1_name = aspect.get('planet1')
            planet2_name = aspect.get('planet2')
            aspect_type = aspect.get('aspect')
            if not all([planet1_name, planet2_name, aspect_type]):
                continue
            planet1 = self._find_planet(planet1_name, self.chart_data['planets'])
            planet2 = self._find_planet(planet2_name, self.chart_data['planets'])
            if planet1 and planet2:
                angle1 = self._get_planet_angle(planet1['longitude'])
                angle2 = self._get_planet_angle(planet2['longitude'])
                inner_radius = planet_radius - 60
                x1 = self.center_x + inner_radius * math.cos(math.radians(angle1))
                y1 = self.center_y + inner_radius * math.sin(math.radians(angle1))
                x2 = self.center_x + inner_radius * math.cos(math.radians(angle2))
                y2 = self.center_y + inner_radius * math.sin(math.radians(angle2))
                color = colorful_aspect_colors.get(aspect_type, '#95a5a6')
                # Enhanced line styling based on aspect importance
                if aspect_type in ['conjunction', 'opposition']:
                    stroke_width = 2.8
                    opacity = 0.88
                elif aspect_type in ['trine', 'square']:
                    stroke_width = 2.2
                    opacity = 0.78
                else:
                    stroke_width = 1.7
                    opacity = 0.68
                dash_array = None
                if aspect_type == 'quincunx':
                    dash_array = '5,3'
                elif aspect_type == 'semisextile':
                    dash_array = '2,2'
                self.dwg.add(self.dwg.line(
                    start=(x1, y1),
                    end=(x2, y2),
                    stroke=color,
                    stroke_width=stroke_width,
                    opacity=opacity,
                    stroke_dasharray=dash_array
                ))
