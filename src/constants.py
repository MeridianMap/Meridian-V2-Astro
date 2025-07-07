"""
Constants for GPT Formatter v3.2
Canonical body IDs and mappings for lean payload format
"""

# Canonical body ID mappings (3-5 characters)
BODY_ID_MAP = {
    "Sun": "sun",
    "Moon": "moon", 
    "Mercury": "merc",
    "Venus": "venus",
    "Mars": "mars",
    "Jupiter": "jup",
    "Saturn": "sat",
    "Uranus": "uran",
    "Neptune": "nep", 
    "Pluto": "pluto",
    "North Node": "nn",
    "South Node": "sn",
    "Chiron": "chir",
    "Ceres": "cer",
    "Pallas": "pal",
    "Juno": "juno",
    "Vesta": "vest",
    "Black Moon Lilith": "bml",
    "Pallas Athena": "pall",  # Alternative name for Pallas
    "Pholus": "phol"
}

# Reverse mapping for lookups
ID_TO_BODY_MAP = {v: k for k, v in BODY_ID_MAP.items()}

# Aspect type abbreviations
ASPECT_TYPE_MAP = {
    "conjunction": "con",
    "opposition": "opp", 
    "trine": "tri",
    "square": "squ",
    "sextile": "sex",
    "quincunx": "qui",
    "semi-sextile": "ssx",
    "semisquare": "ssq",
    "semi-square": "ssq",  # Alternative name
    "sesquiquadrate": "sos",
    "sesqui-square": "sos"  # Alternative name
}

# Reverse mapping for aspect types
ID_TO_ASPECT_MAP = {v: k for k, v in ASPECT_TYPE_MAP.items()}

# Chart type IDs
CHART_IDS = {
    "natal": "natal",
    "design": "design", 
    "transit": "transit",
    "birth": "birth"
}

# Element order for tally arrays
ELEMENT_ORDER = ["Fire", "Air", "Earth", "Water"]

# Modality order for tally arrays  
MODALITY_ORDER = ["Cardinal", "Fixed", "Mutable"]

# Sign to element mapping
SIGN_ELEMENT_MAP = {
    "Aries": "Fire", "Leo": "Fire", "Sagittarius": "Fire",
    "Gemini": "Air", "Libra": "Air", "Aquarius": "Air", 
    "Taurus": "Earth", "Virgo": "Earth", "Capricorn": "Earth",
    "Cancer": "Water", "Scorpio": "Water", "Pisces": "Water"
}

# Sign to modality mapping
SIGN_MODALITY_MAP = {
    "Aries": "Cardinal", "Cancer": "Cardinal", "Libra": "Cardinal", "Capricorn": "Cardinal",
    "Taurus": "Fixed", "Leo": "Fixed", "Scorpio": "Fixed", "Aquarius": "Fixed", 
    "Gemini": "Mutable", "Virgo": "Mutable", "Sagittarius": "Mutable", "Pisces": "Mutable"
}

# Essential dignity scoring
ESSENTIAL_DIGNITY_SCORES = {
    # Rulership (+5), Exaltation (+4), Own Sign (+3), etc.
    "sun": {
        "Leo": 5,      # Rulership
        "Aries": 4     # Exaltation
    },
    "moon": {
        "Cancer": 5,   # Rulership  
        "Taurus": 4    # Exaltation
    },
    "merc": {
        "Gemini": 5, "Virgo": 5,  # Rulership
        "Virgo": 4                # Exaltation (alternative)
    },
    "venus": {
        "Taurus": 5, "Libra": 5,  # Rulership
        "Pisces": 4               # Exaltation
    },
    "mars": {
        "Aries": 5, "Scorpio": 5, # Rulership (traditional)
        "Capricorn": 4            # Exaltation
    },
    "jup": {
        "Sagittarius": 5, "Pisces": 5, # Rulership (traditional)
        "Cancer": 4                     # Exaltation
    },
    "sat": {
        "Capricorn": 5, "Aquarius": 5, # Rulership (traditional)
        "Libra": 4                      # Exaltation
    },
    "uran": {
        "Aquarius": 5   # Modern rulership
    },
    "nep": {
        "Pisces": 5     # Modern rulership
    },
    "pluto": {
        "Scorpio": 5    # Modern rulership
    }
}

# Default orb policy
DEFAULT_ORB_POLICY = {
    "lum": 5.0,      # Luminaries (Sun/Moon)
    "planet": 3.0,   # Major planets
    "asteroid": 1.5  # Asteroids and minor bodies
}

# Major aspect codes for filtering - ONLY these five are allowed
MAJOR_ASPECTS = {"con", "opp", "squ", "tri", "sex"}

# Explicitly forbidden aspects (removed from v3.3)
FORBIDDEN_ASPECTS = {"qui", "ssq", "sos", "semis", "sesqui"}

# Gate range for Human Design validation
GATE_RANGE = range(1, 65)

# Orb limits in 1e-4 degrees for tight aspect filtering  
ORB_LIMITS = {
    "lum": 5000,      # Sun, Moon
    "planet": 3000,   # Merc-Pluto, NN/SN, Chiron, BML
    "aster": 1500,    # Ceres/Juno/Vesta/Pallas/Pholus
    "star": 5000      # fixed stars (not used now but future-proof)
}

LUMINARY_BODIES = ["sun", "moon"]
PLANET_BODIES = ["merc", "venus", "mars", "jup", "sat", "uran", "nep", "pluto"]
ASTEROID_BODIES = ["chir", "cer", "pal", "juno", "vest", "bml", "pall", "phol"]

def deg_to_int(degrees):
    """Convert degrees to integer format (degrees × 10,000)"""
    return int(round(degrees * 10000))

def int_to_deg(int_value):
    """Convert integer format back to degrees"""
    return int_value / 10000.0

def get_body_id(body_name):
    """Get canonical body ID from full name"""
    return BODY_ID_MAP.get(body_name, body_name.lower()[:5])

def get_aspect_id(aspect_name):
    """Get canonical aspect ID from full name"""
    return ASPECT_TYPE_MAP.get(aspect_name.lower(), aspect_name[:3])

def get_orb_limit(body_id):
    """Get orb limit for body based on category"""
    if body_id in LUMINARY_BODIES:
        return DEFAULT_ORB_POLICY["lum"]
    elif body_id in PLANET_BODIES:
        return DEFAULT_ORB_POLICY["planet"] 
    else:
        return DEFAULT_ORB_POLICY["asteroid"]

def body_class(pid: str) -> str:
    """Classify body type for orb limits"""
    if pid in {"sun", "moon"}:
        return "lum"
    if pid in {"mars", "venus", "merc", "jup", "sat", "uran", "nep", "pluto", 
               "nn", "sn", "chir", "bml"}:
        return "planet"
    if pid in {"cer", "juno", "vest", "pall", "phol"}:
        return "aster"
    return "point"

def class_of(body_id: str, bodies_meta=None) -> str:
    """Classify body type for orb limits (legacy alias)"""
    return body_class(body_id)

def keep_aspect(a: dict, bodies_meta=None) -> bool:
    """Return True if aspect a passes spec:
       – major aspect only
       – not same body to itself
       – orb ≤ class-based cap (larger class of the two bodies)"""
    if a["t"] not in MAJOR_ASPECTS:  # minor aspect? drop
        return False
    if a["a"] == a["b"]:  # same body aspect? drop
        return False
    cap = max(ORB_LIMITS[body_class(a["a"])],
              ORB_LIMITS[body_class(a["b"])])
    return abs(a["orb_1e4"]) <= cap
