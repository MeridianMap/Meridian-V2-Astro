# SVG Chart Rendering Feature

This feature adds the ability to generate SVG astrological charts for all four layers in the Meridian Map application.

## Overview

The SVG chart rendering system provides:
- **Natal Charts**: Traditional birth charts with planets, houses, and aspects
- **Human Design Charts**: Specialized charts with HD-specific elements
- **Transit Charts**: Current planetary positions overlaid on natal chart
- **CCG Charts**: Composite/comparison charts between two people

## API Endpoints

### Generate Chart SVG
```
POST /api/chart-svg/<layer_type>
```

**Parameters:**
- `layer_type`: One of `natal`, `human_design`, `transit`, `ccg`

**Request Body:**
```json
{
  "chart_data": {
    "birth_date": "1990-01-15",
    "birth_time": "14:30", 
    "coordinates": {
      "latitude": 40.7128,
      "longitude": -74.0060
    },
    "planets": { ... },
    "houses": { ... }
  },
  "chart_config": {
    "width": 600,
    "height": 600,
    "show_aspects": true,
    "style": "modern"
  }
}
```

**Response:**
```json
{
  "svg": "<svg>...</svg>",
  "layer_type": "natal",
  "width": 600,
  "height": 600
}
```

### Get Chart Configuration Options
```
GET /api/chart-config
```

Returns available chart styles, sizes, and configuration options.

## Usage Examples

### Frontend Integration

```javascript
// Generate a natal chart
const generateNatalChart = async (chartData) => {
  const response = await fetch('/api/chart-svg/natal', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      chart_data: chartData,
      chart_config: {
        width: 600,
        height: 600,
        show_aspects: true
      }
    })
  });
  
  const result = await response.json();
  
  // Insert SVG into DOM
  document.getElementById('chart-container').innerHTML = result.svg;
};

// Generate charts for all layers
const layers = ['natal', 'human_design', 'transit', 'ccg'];
for (const layer of layers) {
  const svg = await generateChart(chartData, layer);
  document.getElementById(`${layer}-chart`).innerHTML = svg;
}
```

### Python Integration

```python
from chart_renderer import generate_chart_svg

# Generate chart programmatically
chart_data = {
  "planets": {...},
  "houses": {...}
}

result = generate_chart_svg(chart_data, 'natal', {
  'width': 800,
  'height': 800,
  'show_aspects': True
})

# Save to file
with open('natal_chart.svg', 'w') as f:
    f.write(result['svg'])
```

## Chart Configuration Options

### Sizes
- **Small**: 400x400px
- **Medium**: 600x600px (default)
- **Large**: 800x800px

### Styles
- **Modern**: Clean, minimal design
- **Traditional**: Classic astrological styling
- **Minimal**: Simplified layout

### Display Options
- `show_aspects`: Show aspect lines between planets
- `show_house_numbers`: Display house numbers
- `show_degrees`: Show planetary degree positions
- `show_planet_names`: Display planet names
- `color_scheme`: Color scheme for chart elements

### Layer-Specific Options

#### Natal Charts
- `show_natal_aspects`: Include natal aspects
- `highlight_chart_ruler`: Emphasize chart ruler

#### Human Design Charts
- `show_gates`: Display HD gates
- `show_channels`: Show HD channels
- `show_centers`: Include HD centers

#### Transit Charts
- `show_transit_aspects`: Show transit-to-natal aspects
- `highlight_active_transits`: Emphasize close transits

#### CCG Charts
- `composite_method`: Midpoint or other composite method
- `show_synastry_aspects`: Include synastry aspects

## File Structure

```
backend/
├── chart_renderer.py      # Main SVG chart rendering engine
├── test_chart_renderer.py # Test script for chart generation
├── test_api_svg.py       # API endpoint testing
└── requirements.txt      # Updated with svgwrite dependency
```

## Dependencies

- **svgwrite**: Python library for generating SVG graphics
- **math**: For trigonometric calculations (standard library)
- **logging**: For error handling and debugging (standard library)

## Testing

Run the test suite to verify chart generation:

```bash
cd backend
python test_chart_renderer.py
```

Test the API endpoints (requires Flask server running):

```bash
python test_api_svg.py
```

## Technical Details

### Chart Rendering Process

1. **Initialize renderer** with specified dimensions
2. **Draw zodiac wheel** with 12 signs and divisions
3. **Add house cusps** based on house system
4. **Place planets** at calculated positions
5. **Draw aspects** between planetary bodies
6. **Add layer-specific elements** (HD gates, transits, etc.)
7. **Generate SVG string** for client consumption

### Coordinate System

- Charts use a 360° coordinate system
- 0° = Aries point (traditional chart top)
- Positions calculated using trigonometric functions
- Supports multiple house systems via existing backend

### Customization

The renderer is highly modular and can be extended with:
- Additional chart styles
- New planetary symbols
- Custom color schemes
- Different aspect line styles
- Enhanced Human Design elements

## Future Enhancements

- [ ] Add more detailed Human Design bodygraph
- [ ] Include fixed star positions
- [ ] Support for Arabic parts/lots
- [ ] Animation capabilities for transit movements
- [ ] PDF export functionality
- [ ] Mobile-optimized responsive sizing
