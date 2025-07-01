#!/usr/bin/env python3
"""
SVG Chart Renderer for Meridian Map
Generates SVG astrological charts for different layers using svgwrite
"""

import svgwrite
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
        
        # Colors for different elements
        self.colors = {
            'fire': '#ff4444', 'earth': '#8b4513', 'air': '#4444ff', 'water': '#0066cc',
            'natal': '#000000', 'transit': '#ff6600', 'composite': '#9900cc',
            'human_design': '#006600', 'aspects': '#888888'
        }

    def create_chart_svg(self, chart_data: Dict, layer_type: str, config: Dict = None) -> str:
        """
        Generate SVG chart for the specified layer type
        """
        if config is None:
            config = {}
            
        # Create SVG drawing
        dwg = svgwrite.Drawing(size=(self.width, self.height))
        
        # Add background
        dwg.add(dwg.rect(insert=(0, 0), size=(self.width, self.height), 
                        fill='white', stroke='none'))
        
        # Draw based on layer type
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
            
        return dwg.tostring()

    def _draw_natal_chart(self, dwg, chart_data: Dict, config: Dict):
        """Draw natal chart"""
        # Draw outer circle (zodiac wheel)
        self._draw_zodiac_wheel(dwg)
        
        # Draw house divisions
        houses = chart_data.get('houses', {})
        if houses and 'cusps' in houses:
            self._draw_houses(dwg, houses['cusps'])
        
        # Draw planets
        planets = chart_data.get('planets', {})
        self._draw_planets(dwg, planets, style='natal')
        
        # Draw aspects if enabled
        if config.get('show_aspects', True):
            aspects = chart_data.get('aspects', {})
            self._draw_aspects(dwg, aspects, planets)

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
        if houses and 'cusps' in houses:
            self._draw_houses(dwg, houses['cusps'])

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
        """Draw the basic zodiac wheel with signs"""
        # Outer circle
        dwg.add(dwg.circle(center=(self.center_x, self.center_y), 
                          r=self.outer_radius, fill='none', stroke='black', stroke_width=2))
        
        # Inner circle
        dwg.add(dwg.circle(center=(self.center_x, self.center_y), 
                          r=self.inner_radius, fill='none', stroke='black', stroke_width=1))
        
        # Draw zodiac signs
        for i in range(12):
            angle = i * 30  # Each sign is 30 degrees
            start_angle = math.radians(angle - 90)  # Start from Aries at top
            end_angle = math.radians(angle + 30 - 90)
            
            # Sign division lines
            x1 = self.center_x + self.inner_radius * math.cos(start_angle)
            y1 = self.center_y + self.inner_radius * math.sin(start_angle)
            x2 = self.center_x + self.outer_radius * math.cos(start_angle)
            y2 = self.center_y + self.outer_radius * math.sin(start_angle)
            
            dwg.add(dwg.line(start=(x1, y1), end=(x2, y2), 
                           stroke='gray', stroke_width=1))
            
            # Sign symbols
            mid_angle = math.radians(angle + 15 - 90)
            symbol_radius = (self.outer_radius + self.inner_radius) / 2
            symbol_x = self.center_x + symbol_radius * math.cos(mid_angle)
            symbol_y = self.center_y + symbol_radius * math.sin(mid_angle)
            
            sign_symbol = self.sign_symbols.get(angle, '?')
            dwg.add(dwg.text(sign_symbol, insert=(symbol_x, symbol_y), 
                           text_anchor='middle', dominant_baseline='central',
                           font_size=16, font_family='Arial'))

    def _draw_houses(self, dwg, house_cusps: List[float]):
        """Draw house divisions"""
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
        """Draw planets on the chart"""
        if radius is None:
            radius = self.planet_radius
            
        color = self.colors.get(style, 'black')
        
        for planet_name, planet_data in planets.items():
            if isinstance(planet_data, dict) and 'longitude' in planet_data:
                longitude = planet_data['longitude']
                angle = math.radians(longitude - 90)  # Adjust for chart orientation
                
                # Planet position
                x = self.center_x + radius * math.cos(angle)
                y = self.center_y + radius * math.sin(angle)
                
                # Planet symbol
                symbol = self.planet_symbols.get(planet_name.lower(), planet_name[:2].upper())
                
                # Draw planet circle
                dwg.add(dwg.circle(center=(x, y), r=8, fill='white', 
                                 stroke=color, stroke_width=1.5))
                
                # Draw planet symbol
                dwg.add(dwg.text(symbol, insert=(x, y), 
                               text_anchor='middle', dominant_baseline='central',
                               font_size=10, font_family='Arial', fill=color))
                
                # Add degree marking
                degree_text = f"{longitude:.0f}°"
                dwg.add(dwg.text(degree_text, insert=(x, y + 20), 
                               text_anchor='middle', dominant_baseline='central',
                               font_size=8, font_family='Arial', fill=color))

    def _draw_aspects(self, dwg, aspects: Dict, planets: Dict):
        """Draw aspect lines between planets"""
        if not aspects:
            return
            
        for aspect_name, aspect_list in aspects.items():
            if isinstance(aspect_list, list):
                for aspect in aspect_list:
                    planet1 = aspect.get('planet1', '').lower()
                    planet2 = aspect.get('planet2', '').lower()
                    
                    if planet1 in planets and planet2 in planets:
                        self._draw_aspect_line(dwg, planets[planet1], planets[planet2], aspect)

    def _draw_aspect_line(self, dwg, planet1_data: Dict, planet2_data: Dict, aspect: Dict):
        """Draw a single aspect line"""
        if not all(isinstance(p, dict) and 'longitude' in p for p in [planet1_data, planet2_data]):
            return
            
        lon1 = planet1_data['longitude']
        lon2 = planet2_data['longitude']
        
        angle1 = math.radians(lon1 - 90)
        angle2 = math.radians(lon2 - 90)
        
        # Calculate positions on inner circle
        radius = self.inner_radius - 10
        x1 = self.center_x + radius * math.cos(angle1)
        y1 = self.center_y + radius * math.sin(angle1)
        x2 = self.center_x + radius * math.cos(angle2)
        y2 = self.center_y + radius * math.sin(angle2)
        
        # Determine aspect color and line style
        aspect_type = aspect.get('aspect', '').lower()
        if aspect_type in ['conjunction', 'trine', 'sextile']:
            color = 'blue'
            stroke_width = 1
        elif aspect_type in ['opposition', 'square']:
            color = 'red' 
            stroke_width = 1.5
        else:
            color = 'gray'
            stroke_width = 0.5
            
        dwg.add(dwg.line(start=(x1, y1), end=(x2, y2), 
                       stroke=color, stroke_width=stroke_width, opacity=0.6))

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


def generate_chart_svg(chart_data: Dict, layer_type: str, config: Dict = None) -> Dict:
    """
    Main function to generate SVG chart
    """
    try:
        if config is None:
            config = {}
            
        width = config.get('width', 600)
        height = config.get('height', 600)
        
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
