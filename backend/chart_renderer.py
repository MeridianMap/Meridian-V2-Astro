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
import io

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
    Generates the SVG for a single-wheel chart (natal, transit, etc.).
    """
    width = chart_config.get('width', 600)
    height = chart_config.get('height', 600)
    center_x, center_y = width / 2, height / 2
    outer_radius = min(center_x, center_y) - 20
    zodiac_band_width = 50
    house_cusp_radius = outer_radius - zodiac_band_width
    inner_radius = house_cusp_radius - 30
    planet_radius = inner_radius - 30

    # Debug logging
    print(f"DEBUG: Generating chart - Houses: {len(chart_data.get('houses', []))}, Planets: {len(chart_data.get('planets', []))}, Aspects: {len(chart_data.get('aspects', []))}")

    svg_io = io.StringIO()
    dwg = svgwrite.Drawing(stringio=svg_io, size=(width, height))
    dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), fill='white'))

    renderer = ChartRenderer(dwg, width, height, chart_config, chart_data)
    
    # Render all components for a single-wheel chart
    print("DEBUG: Drawing zodiac signs...")
    renderer._draw_zodiac_signs(outer_radius, zodiac_band_width)
    print("DEBUG: Drawing house cusps...")
    renderer._draw_house_cusps(house_cusp_radius)
    print("DEBUG: Drawing house segments...")
    renderer._draw_house_segments(outer_radius, inner_radius)
    print("DEBUG: Drawing houses...")
    renderer._draw_houses(inner_radius, house_cusp_radius)
    print("DEBUG: Drawing planets...")
    renderer._draw_planets(chart_data.get('planets', []), planet_radius)
    
    if chart_config.get('show_aspects', True):
        print("DEBUG: Drawing aspects...")
        renderer._draw_aspects(chart_data.get('aspects', []), planet_radius)

    # Add a title based on the chart type and data
    layer_type = chart_config.get('layer_type', 'chart')
    title_text = f"{layer_type.title()} Chart"
    if chart_data.get('input', {}).get('birth_date'):
        title_text += f" - {chart_data['input']['birth_date']}"
    
    dwg.add(dwg.text(title_text, insert=(center_x, 20), text_anchor='middle', font_size=16, fill='#333'))

    print("DEBUG: Chart generation complete")
    return svg_io.getvalue()

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
        
        print(f"DEBUG: Drawing houses - house_data type: {type(house_data)}")
        print(f"DEBUG: houses count: {len(houses)}")
        if houses and len(houses) > 0:
            print(f"DEBUG: First house: {houses[0]}")
        
        # Always draw 12 houses using the simplest approach for now
        for i in range(12):
            house_num = i + 1
            
            # Use simple equal house division for now to get house numbers working
            chart_angle = i * 30 + 15 - 90  # Middle of house segment, adjusted for chart orientation
            
            # Draw house number
            text_radius = (inner_radius + house_cusp_radius) / 2
            x = self.center_x + text_radius * math.cos(math.radians(chart_angle))
            y = self.center_y + text_radius * math.sin(math.radians(chart_angle))
            
            print(f"DEBUG: House {house_num}: angle={chart_angle}, position=({x:.1f}, {y:.1f})")
            
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
        for planet in planets:
            angle = self._get_planet_angle(planet['longitude'])
            x = self.center_x + radius * math.cos(math.radians(angle))
            y = self.center_y + radius * math.sin(math.radians(angle))
            
            fill_color = '#4a4a4a' # Standard color for all planets in a single wheel

            symbol = PLANET_SYMBOLS.get(planet['name'], '?')
            self.dwg.add(self.dwg.text(symbol, insert=(x, y), text_anchor="middle", alignment_baseline="middle", font_size="14", fill=fill_color))
            
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
