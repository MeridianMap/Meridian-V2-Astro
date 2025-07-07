# GPT Formatter v3.2 - Hardened Astrological Data Format

## Overview

GPT Formatter v3.2 hardens the v3.1 format with stricter aspect filtering, gate validation, and enhanced quality controls:

- **Hardened Aspect Filtering**: Tighter orb limits and major aspects only
- **Gate Validation**: Strict Human Design gate range validation (1-64)
- **Enhanced Body Classification**: Refined luminary/planet/asteroid classes
- **Day/Night Arabic Lots**: Proper hermetic lot calculations with day/night formulas
- **Quality Controls**: ASC/DESC relationship validation and order guards

## New Features in v3.2

### 1. Hardened Aspect Filtering

Stricter orb limits for cleaner aspect lists:

```json
{
  "tightAspects": [
    {"a": "sun", "b": "moon", "t": "tri", "orb_1e4": 2500}
  ]
}
```

**New Orb Limits (in 1e-4 degrees):**
- **Luminaries** (Sun, Moon): 5000 (0.5°)
- **Planets** (Mercury-Pluto, Nodes, Chiron, BML): 3000 (0.3°)  
- **Asteroids** (Ceres, Juno, Vesta, Pallas, Pholus): 1500 (0.15°)

**Major Aspects Only:**
- `con` (conjunction), `opp` (opposition), `tri` (trine)
- `squ` (square), `sex` (sextile), `qui` (quincunx)
- Minor aspects (semi-square, sesqui-square) are excluded

### 2. Gate Validation

All Human Design gates are validated to be in range 1-64:

```python
# Gate sanity check
gate_num = int(gate.split(".")[0])
if gate_num not in range(1, 65):
    raise ValueError(f"Invalid gate {gate_num}")
```

### 3. Enhanced Body Classification

Refined body type classification for orb limits:

```python
def body_class(pid: str) -> str:
    if pid in {"sun", "moon"}: return "lum"
    if pid in {"mars", "venus", "merc", "jup", "sat", "uran", "nep", "pluto", 
               "nn", "sn", "chir", "bml"}: return "planet"
    if pid in {"cer", "juno", "vest", "pall", "phol"}: return "aster"
    return "point"
```

### 4. Day/Night Arabic Lots

Proper hermetic lot calculations respecting day/night chart formulas:

```json
{
  "arabicLots": {
    "fortune": 1205000,    // Day: ASC + Moon - Sun, Night: ASC + Sun - Moon
    "spirit": 2401500,     // Day: ASC + Sun - Moon, Night: ASC + Moon - Sun
    "eros": 1156000,       // Day: ASC + Venus - Sun, Night: ASC + Sun - Venus
    "victory": 1891000,    // Day: ASC + Jupiter - Sun, Night: ASC + Sun - Jupiter
    "courage": 567000      // Day: ASC + Mars - Sun, Night: ASC + Sun - Mars
  }
}
```

Only lots computed in `backend/hermetic_lots.py` are included.

## Chart Types

v3.1 enforces exactly three chart types:

1. **Natal**: Birth chart with tight aspects, Arabic lots, fixed stars
2. **Design**: 88-day pre-birth chart with element/modality tallies, fixed stars
3. **Transit**: Current transits with cross-aspects, NO fixed stars

## Data Encoding

All coordinates use integer encoding (degrees × 10,000):

- **Longitude**: 0° = `0`, 359.9999° = `3599999`
- **Latitude**: -90° = `-900000`, +90° = `900000`
- **Orbs**: 1.5° = `15000`

## Usage Example

```python
from gpt_formatter_v3_1 import GPTFormatterV32

formatter = GPTFormatterV32()
result = formatter.format_comprehensive_calculation(
    natal_data=natal_chart,
    design_data=design_chart,
    transit_data=current_transits,
    request_metadata={"house_system": "whole_sign"}
)

print(f"Schema: {result['schemaVer']}")
print(f"Format: {result['metadata']['format']}")  # "gpt_formatter_v3.2"
print(f"Charts: {[c['id'] for c in result['charts']]}")
```

## Schema Validation

The output conforms to `chart.schema.v3.1.json` which includes:

- Required fields validation
- Coordinate range checking  
- Aspect type enforcement
- Chart ID restrictions

## Migration from v3.1

Key differences from v3.1:

1. **Formatter Version**: `"gpt_formatter_v3.1"` → `"gpt_formatter_v3.2"`
2. **Orb Limits**: Much stricter (5000/3000/1500 vs 50000/30000/15000 in 1e-4 units)
3. **Aspect Filtering**: Major aspects only, minor aspects removed
4. **Gate Validation**: Strict range checking with ValueError on invalid gates
5. **Body Classification**: Enhanced with aster class and refined planet classification
6. **Arabic Lots**: Day/night aware calculations matching backend hermetic_lots.py
7. **Quality Controls**: ASC/DESC validation and modality order enforcement

## Testing

Run the comprehensive test suite:

```bash
python tests/test_spec_v32.py
python tests/test_formatter_v31.py
```

All tests verify:
- ✅ Schema compliance
- ✅ Gate calculations and validation (1-64 range)
- ✅ Fixed star positions
- ✅ Transit aspect generation
- ✅ Coordinate encoding/decoding
- ✅ Hardened orb limit enforcement
- ✅ Major aspect filtering
- ✅ Day/night Arabic lot calculations
- ✅ Body classification accuracy
- ✅ ASC/DESC horizon relationship

## Performance

v3.1 maintains the compact v3.0 design principles:

- Integer coordinates reduce JSON size
- Canonical body IDs minimize data transfer
- Selective inclusion of tight aspects only
- No redundant star-to-planet aspects

## Changelog

### v3.2.0 (2025-07-06)
- **HARDENED ASPECT FILTERING**: Stricter orb limits (0.5°/0.3°/0.15°) and major aspects only
- **GATE VALIDATION**: Strict Human Design gate range validation (1-64) with error throwing
- **ENHANCED BODY CLASSIFICATION**: Refined luminary/planet/asteroid classes for orb calculation
- **DAY/NIGHT ARABIC LOTS**: Proper hermetic lot calculations matching backend/hermetic_lots.py
- **QUALITY CONTROLS**: ASC/DESC relationship validation and modality order guards
- **ASPECT FILTER FUNCTION**: Updated keep_aspect() with class-based orb caps
- **COMPREHENSIVE TESTS**: Added test_spec_v32.py with 8 specification compliance tests

### v3.1.0 (Previous)
- Added Human Design gate annotations for all bodies
- Added transit cross-aspects to natal and design charts
- Added fixed stars for natal and design charts (7 major stars)
- Enhanced metadata with schema version and house system
- Bumped schema version to "3.1"
- Comprehensive test suite with 11 test cases

### v3.0.1 (Previous)
- Established core v3.0 format with integer coordinates
- Arabic lots calculations
- Tight aspect filtering
- Chart ID enforcement
