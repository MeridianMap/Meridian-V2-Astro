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
        
        # Add chart title and legend
        self._add_chart_title_and_legend(dwg, chart_data, layer_type, config)
        
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
        """Draw planets on the chart with collision detection"""
        if radius is None:
            radius = self.planet_radius
            
        color = self.colors.get(style, 'black')
        
        # Sort planets by longitude for better positioning
        sorted_planets = sorted(
            [(name, data) for name, data in planets.items() 
             if isinstance(data, dict) and 'longitude' in data],
            key=lambda x: x[1]['longitude']
        )
        
        # Track occupied positions to avoid overlaps
        occupied_positions = []
        min_distance = 15  # Minimum distance between planet symbols
        
        for planet_name, planet_data in sorted_planets:
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
            gradient_id = f"gradient_{planet_name}_{style}"
            gradient = dwg.defs.add(dwg.radialGradient(id=gradient_id, center=(0.3, 0.3)))
            gradient.add_stop_color(offset=0, color='white')
            gradient.add_stop_color(offset=1, color=color, opacity=0.8)
            
            # Planet circle with enhanced styling
            dwg.add(dwg.circle(center=(x, y), r=10, fill=f'url(#{gradient_id})', 
                             stroke=color, stroke_width=2, opacity=0.9))
            
            # Draw planet symbol
            dwg.add(dwg.text(symbol, insert=(x, y), 
                           text_anchor='middle', dominant_baseline='central',
                           font_size=12, font_family='Arial Unicode MS, Arial', 
                           fill=color, font_weight='bold'))
            
            # Add degree marking with sign
            degree = longitude % 30
            sign_index = int(longitude // 30)
            sign_symbol = list(self.sign_symbols.values())[sign_index]
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
            
        for aspect_name, aspect_list in aspects.items():
            if isinstance(aspect_list, list):
                for aspect in aspect_list:
                    planet1 = aspect.get('planet1', '').lower()
                    planet2 = aspect.get('planet2', '').lower()
                    
                    if planet1 in planets and planet2 in planets:
                        self._draw_aspect_line(dwg, planets[planet1], planets[planet2], aspect)

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
        legend_x = self.width - 150
        legend_y = 60
        
        # Legend background
        dwg.add(dwg.rect(insert=(legend_x - 10, legend_y - 10), 
                        size=(140, 200), fill='white', stroke='#cccccc',
                        stroke_width=1, opacity=0.9, rx=5))
        
        # Legend title
        dwg.add(dwg.text("Legend", insert=(legend_x, legend_y + 10), 
                       font_size=12, font_family='Arial', font_weight='bold',
                       fill='#333333'))
        
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
            y_pos = legend_y + 30 + (i * 18)
            
            # Symbol
            dwg.add(dwg.text(symbol, insert=(legend_x, y_pos), 
                           font_size=12, font_family='Arial Unicode MS, Arial',
                           fill=color))
            
            # Label
            dwg.add(dwg.text(label, insert=(legend_x + 20, y_pos), 
                           font_size=10, font_family='Arial', fill='#333333'))


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
