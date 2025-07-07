# GPT Formatter Changelog

## v3.2.0 (2025-07-06) - "Hardened Compliance"

### 🔒 Hardened Aspect Filtering
- **BREAKING**: Dramatically reduced orb limits for tighter aspect lists
  - Luminaries (Sun/Moon): 50,000 → 5,000 (5.0° → 0.5°) 
  - Planets (Mercury-Pluto, Nodes, Chiron, BML): 30,000 → 3,000 (3.0° → 0.3°)
  - Asteroids (Ceres, Juno, Vesta, Pallas, Pholus): 15,000 → 1,500 (1.5° → 0.15°)
- **BREAKING**: Major aspects only - removed minor aspects (semi-square, sesqui-square)
- Updated `keep_aspect()` function with class-based orb caps

### ✅ Gate Validation
- Added strict Human Design gate range validation (1-64)
- `deg_to_gate_line()` now throws `ValueError` for invalid gates
- Added `GATE_RANGE = range(1, 65)` constant

### 🎯 Enhanced Body Classification  
- **BREAKING**: Refined `body_class()` function replacing `class_of()`
- Chiron (`chir`) reclassified from "asteroid" to "planet"
- Added "aster" class for true asteroids (Ceres, Juno, Vesta, Pallas, Pholus)
- New classification logic:
  ```python
  def body_class(pid: str) -> str:
      if pid in {"sun", "moon"}: return "lum"
      if pid in {"mars", "venus", "merc", "jup", "sat", "uran", "nep", "pluto", 
                 "nn", "sn", "chir", "bml"}: return "planet"
      if pid in {"cer", "juno", "vest", "pall", "phol"}: return "aster"
      return "point"
  ```

### 🌙 Day/Night Arabic Lots
- **BREAKING**: Arabic lots now respect day/night chart formulas
- Matches backend `hermetic_lots.py` implementation exactly
- Day charts: ASC + addend - subtrahend
- Night charts: ASC + subtrahend - addend (swapped)
- Reduced to 7 core lots: fortune, spirit, eros, necessity, victory, courage, nemesis

### 🛡️ Quality Controls
- ASC/DESC horizon relationship validation (DESC = ASC + 180°)
- Modality tally order enforcement: `[cardinal, fixed, mutable]`
- Angle validation with warning on horizon mismatches

### 📊 Updated Metadata
- Format ID: `"gpt_formatter_v3.1"` → `"gpt_formatter_v3.2"`
- Version: `"3.1.1"` → `"3.2"`
- Class name: `GPTFormatterV31` → `GPTFormatterV32`

### 🧪 Comprehensive Testing
- Added `test_spec_v32.py` with 8 specification compliance tests
- Updated existing tests for v3.2 compatibility
- All tests validate hardened filtering and quality controls

### 📚 Documentation
- Updated README_v3.2.md with complete v3.2 documentation
- Added migration guide from v3.1
- Performance notes on stricter filtering benefits

---

## v3.1.1 (2025-07-06) - "Enhanced Integration"

### ✨ Human Design Gates
- Added gate annotations (`gate: "64.6"`) for all bodies and fixed stars
- `deg_to_gate_line()` function for longitude-to-gate conversion
- 64 gates × 6 lines covering 360° zodiac

### 🌟 Fixed Stars
- Added 7 major fixed stars for natal and design charts only
- Includes: Regulus, Spica, Algol, Aldebaran, Antares, Fomalhaut, Sirius
- Each star has longitude, house position, and gate annotation
- Precession-corrected positions for 2025 epoch

### 🔄 Transit Cross-Aspects
- Transit charts now include `toNatal` and `toDesign` aspect arrays
- Cross-chart aspect calculations between transit and natal/design bodies
- Maintains same tight orb filtering as natal aspects

### 📋 Enhanced Metadata
- Added `schemaVer: "3.1"` to response root
- Added `house_system` to metadata (e.g., "whole_sign")
- Priority: request_metadata > natal_data > "whole_sign" default

### 🎯 Aspect Filtering
- Major aspects only: conjunction, opposition, trine, square, sextile, quincunx
- Orb limits by body class: luminaries (5°), planets (3°), asteroids (1.5°)
- `keep_aspect()` function for consistent filtering across all aspect arrays

### 📊 Element/Modality Tallies
- Added for both natal and design charts
- `elemTally: [fire, air, earth, water]` counts
- `modeTally: [cardinal, fixed, mutable]` counts
- Based on sign positions of planets

### 🗂️ Arabic Lots
- 20+ hermetic lots with integer encoding
- Includes: fortune, spirit, eros, victory, love, marriage, etc.
- Day/night chart awareness for fortune and spirit calculations
- Integer format: degrees × 10,000

### 🏠 Dignity Scores
- Essential dignity: rulership (+5), exaltation (+4)
- Accidental dignity: angular houses (+2), succedent (+1), cadent (0)
- Format: `{"ess": 5, "acc": 2}` per body

---

## v3.0.1 (2025-07-05) - "Foundation"

### 🎯 Core Format
- Integer coordinate encoding (degrees × 10,000)
- Canonical body IDs: 3-5 characters (sun, moon, merc, venus, etc.)
- Schema version "3.0" with strict validation

### 📊 Chart Types
- Natal: birth chart with tight aspects
- Design: 88-day pre-birth chart  
- Transit: current positions with cross-aspects

### 🔢 Coordinate System
- Longitude: 0° = 0, 359.9999° = 3,599,999
- Latitude: -90° = -900,000, +90° = 900,000
- Speed: degrees/day × 10,000
- Declination: degrees × 10,000

### 🎭 House Systems
- Support for multiple house systems
- Whole sign default with configurable override
- House positions 1-12 for all bodies

### ⚖️ Aspect Engine
- Major aspects with tight orbs
- Body-class based orb limits
- No self-aspects or wide minor aspects
- Lowercase aspect codes: con, opp, tri, squ, sex, qui

### 📐 Angles
- ASC, MC, DESC, IC with integer encoding
- Automatic descendant calculation (ASC + 180°)
- Midheaven and IC from ephemeris

### 🌍 Timezone Support
- UTC timestamps in ISO format
- Configurable timezone handling
- Birth time validation and defaults
