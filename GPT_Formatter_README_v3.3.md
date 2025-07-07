# GPT Formatter v3.3 README

## Overview

The GPT Formatter v3.3 provides tightened spec compliance for AI interpretation of astrological chart data. This version implements strict filtering and enhanced metadata requirements.

## Key Features

### 🎯 Tightened Aspect Filtering
- **Only 5 Major Aspects**: con, opp, squ, tri, sex
- **Forbidden Aspects Removed**: qui, sem, ssq, bio, qnt, etc.
- **Strict Enforcement**: All aspect lists filtered consistently

### 🏛️ Enhanced Chart Structure
- **Chart Ruler**: Traditional rulership based on Ascendant sign
- **Sect Determination**: Diurnal/nocturnal based on Sun position
- **House Cusps**: 12-element array in lng_1e4 format for all charts
- **Birth Metadata**: Complete birth information in top-level metadata

### 📍 Precision Coordinates
- **Integer Encoding**: All coordinates in lng_1e4/lat_1e4 format
- **Decan/Term Indices**: Added to all body structures
- **Human Design Gates**: Included for all celestial bodies

## Usage

### Basic Usage
```python
from src.gpt_formatter_v3_1 import generate

# Generate v3.3 compliant output
result = generate(
    natal_data=natal_chart_data,
    design_data=design_chart_data, 
    transit_data=transit_chart_data,
    request_metadata=request_info
)

print(f"Schema: {result['schemaVer']}")
print(f"Format: {result['metadata']['format']}")
```

### Advanced Usage
```python
from src.gpt_formatter_v3_1 import GPTFormatterV33

formatter = GPTFormatterV33()

# Access individual methods
chart_ruler = formatter._calculate_chart_ruler(chart_data)
sect = formatter._determine_sect(chart_data)
cusps = formatter._calculate_house_cusps(chart_data)
birth_meta = formatter._extract_birth_metadata(request_metadata, natal_data)
```

## Output Schema

### Metadata Structure
```json
{
  "metadata": {
    "api_ver": "1.0.0",
    "format": "gpt_formatter_v3.3",
    "ephem": "DE441",
    "bodies": ["sun", "moon", "merc", ...],
    "orb": {"planetary": 30000, "luminary": 50000, ...},
    "house_system": "whole_sign",
    "birth": {
      "name": "Chart Name",
      "date": "1985-07-15",
      "time": "14:30:00", 
      "lat_1e4": 407128,
      "lon_1e4": -740060,
      "tz": "-04:00",
      "house_system": "whole_sign"
    }
  }
}
```

### Chart Structure
```json
{
  "id": "natal",
  "timestamp": "1985-07-15T14:30:00Z",
  "chartRuler": "sun",
  "sect": "diurnal",
  "cusps": [900000, 1200000, 1500000, ...],
  "bodies": {
    "sun": {
      "lng_1e4": 1205000,
      "dec": 0,
      "term": 2,
      "lat_1e4": 0,
      "spd_1e4": 9800,
      "gate": "41.3"
    }
  },
  "angles": {
    "asc": {"lng_1e4": 1050000},
    "mc": {"lng_1e4": 150000}
  },
  "tightAspects": [
    {
      "a": "sun",
      "b": "moon", 
      "t": "tri",
      "orb_1e4": 3000
    }
  ]
}
```

## Validation

### Aspect Filtering
```python
# Only these 5 aspects are allowed
MAJOR_ASPECTS = {'con', 'opp', 'squ', 'tri', 'sex'}

# All others are filtered out
FORBIDDEN = {'qui', 'sem', 'ssq', 'bio', 'qnt', 'sep', 'nov'}
```

### Required Fields
- **All Charts**: `chartRuler`, `sect`, `cusps` (12 elements)
- **All Bodies**: `lng_1e4`, `dec`, `term` 
- **Metadata**: `birth` block with 7 fields
- **Coordinates**: Integer format (degrees × 10,000)

## Testing

### Verification Scripts
```bash
# Comprehensive feature test
python test_v33_comprehensive.py

# Edge cases and error handling  
python test_v33_edge_cases.py

# Quick feature verification
python verify_v33.py
```

### Expected Results
- ✅ Aspect filtering: 5 allowed, forbidden blocked
- ✅ Chart ruler/sect: Present in all charts
- ✅ Cusps array: 12 elements, lng_1e4 format
- ✅ Birth metadata: All required fields
- ✅ Edge cases: Robust error handling

## Migration from v3.2

### Breaking Changes
1. **Aspect Types**: Only 5 major aspects now allowed
2. **Required Fields**: `chartRuler`, `sect`, `cusps` now mandatory
3. **Metadata**: `birth` block now required in metadata

### Non-Breaking Changes
- Body structure enhanced with `dec`/`term` indices
- Integer coordinate encoding maintains precision
- Graceful fallbacks for missing data

## Integration

### Backend Integration
```python
# In backend/gpt_formatter.py
from src.gpt_formatter_v3_1 import generate

def format_for_gpt(natal_data, design_data, transit_data, metadata):
    return generate(natal_data, design_data, transit_data, metadata)
```

### API Response
```python
# The formatted output is ready for AI consumption
{
  "schemaVer": "3.2",
  "metadata": {...},
  "charts": [...]
}
```

## Support

- **Class**: `GPTFormatterV33`
- **Entry Point**: `generate()` function
- **Version**: "3.3"
- **Format ID**: "gpt_formatter_v3.3"
- **Schema**: "3.2" with v3.3 enhancements

---

**Status**: ✅ Production Ready
**Compliance**: 100% v3.2 spec adherent  
**Testing**: Comprehensive verification complete
