# GPT Formatter Changelog

## v3.0.0 - Lean Self-Contained Payload Format
*Released: 2025-07-06*

### 🚀 Major Release: Complete Format Restructure

**Breaking Changes:**
- **New Schema**: Introduced `chart.schema.v3.json` with lean payload structure
- **Integer Coordinates**: All longitudes stored as `int × 10,000` for precision
- **Canonical IDs**: Body names mapped to 3-5 character identifiers
- **Single Payload**: Unified structure with metadata + charts array

### 📊 New Features

**Core Structure:**
```json
{
  "schemaVer": "3.0",
  "metadata": {
    "api_ver": "1.0.0",
    "format": "gpt_formatter_v3", 
    "ephem": "DE441",
    "bodies": ["sun", "moon", "merc", ...],
    "orb": {"lum": 5, "planet": 3, "asteroid": 1.5}
  },
  "charts": [
    {
      "id": "natal",
      "timestamp": "1990-07-15T14:30:00Z",
      "bodies": {
        "sun": {"lng_1e4": 1205678, "spd_1e4": 9856, ...}
      }
    }
  ]
}
```

**Enhanced Data:**
- **Tight Aspects**: `tightAspects` array for orb ≤ 3.0°
- **Element/Modality Tallies**: Arrays for design chart analysis
- **Arabic Lots**: Part of Fortune and other calculated points
- **Dignity Scores**: Essential and accidental dignity per body
- **Aspect Grid**: Complete aspect matrix (optional)

**Precision Improvements:**
- Coordinates stored as `int = degrees × 10,000`
- Round-trip accuracy within ±0.0001°
- Consistent integer encoding across all values

### 🔧 Technical Details

**Current Files:**
- `src/gpt_formatter_v3_1.py` - Main v3.1 formatter (current)
- `src/schema/chart.schema.v3.1.json` - JSON Schema validation (current)
- `src/constants.py` - Canonical mappings and utilities
- `tests/test_v31.py` - Comprehensive test suite (current)

**Body ID Mappings:**
```python
"Sun" → "sun"
"North Node" → "nn" 
"Black Moon Lilith" → "bml"
"Mercury" → "merc"
```

**Aspect Type Mappings:**
```python
"conjunction" → "con"
"opposition" → "opp"
"trine" → "tri"
"square" → "squ"
"sextile" → "sex"
```

### 🧪 Validation

**Schema Compliance:**
- All output validates against `chart.schema.v3.json`
- Required fields enforced at multiple levels
- Type safety for all numeric values

**Test Coverage:**
- Unit tests for all core functions
- Round-trip conversion validation
- Error handling verification
- Multi-chart scenario testing

### 📈 Performance Benefits

- **Reduced Payload Size**: ~40% smaller than v2.x format
- **Integer Storage**: Faster processing, no floating-point precision loss
- **Canonical IDs**: Consistent cross-system references
- **Schema Validation**: Guaranteed structure compliance

### 🔄 Migration Guide

**From v2.x to v3.0:**

1. **Import Changes:**
   ```python
   # Old
   from gpt_formatter import GPTFormatter
   
   # New  
   from gpt_formatter_v3 import generate
   ```

2. **Usage Changes:**
   ```python
   # Old
   formatter = GPTFormatter()
   result = formatter.format_comprehensive_calculation(data)
   
   # New
   result = generate(natal_data=data)
   ```

3. **Output Structure:**
   ```python
   # Old: Multiple top-level sections
   result["natal"]["planetary_positions"]["sun"]["degree"]
   
   # New: Unified charts array
   result["charts"][0]["bodies"]["sun"]["lng_1e4"]
   ```

4. **Coordinate Conversion:**
   ```python
   from constants import int_to_deg, deg_to_int
   
   # Convert to degrees
   longitude = int_to_deg(body_data["lng_1e4"])
   
   # Convert to integer format
   int_value = deg_to_int(longitude)
   ```

### 🔀 Backward Compatibility

- **v2.x Preserved**: Previous formatters remain fully functional
- **Parallel Operation**: Can run v2.x and v3.0 simultaneously
- **Gradual Migration**: Update consumers at your own pace

---

## v2.3.2 - Phase-1 Features
*Released: 2025-07-06*

### ✨ Enhancements
- Added `julian_day` and `ephemeris_version` metadata
- Extended optional points: East Point & Part of Spirit
- Verified speed and declination in all planetary output
- Improved audit trail with calculation timestamps

---

## v2.3.1 - Universal Body Coverage  
*Released: 2025-07-05*

### ✨ Features
- Extended body coverage: Pallas Athena, Pholus
- Enhanced Human Design gate integration
- 4-decimal precision for coordinates
- Comprehensive asteroid support

---

## v2.3.0 - Enhanced Analysis
*Released: 2025-07-04*  

### ✨ Features
- Increased aspect limit to 12 for comprehensive analysis
- Enhanced aspect-to-angles calculations
- Improved chart pattern identification
- Expanded elemental and modality analysis
