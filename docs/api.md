# API Reference

## Base URL
```
Development: http://localhost:5000/api
Production: https://your-app-name.onrender.com/api
```

## Authentication
Currently, the API does not require authentication. All endpoints are publicly accessible.

## Response Format
All API responses follow a consistent JSON format:

**Success Response:**
```json
{
  "success": true,
  "data": { ... }
}
```

**Error Response:**
```json
{
  "error": "Error message description",
  "details": "Additional error details (if available)"
}
```

## Core Endpoints

### Health Check
**GET** `/api/health`

Returns the API health status.

**Response:**
```json
{
  "ok": true
}
```

### API Status
**GET** `/api`

Returns basic API information.

**Response:**
```json
{
  "status": "Meridian API running"
}
```

## Chart Calculation

### Calculate Natal Chart
**POST** `/api/calculate`

Generates a comprehensive natal chart with planetary positions, houses, and aspects.

**Request Body:**
```json
{
  "birth_date": "1990-01-15",
  "birth_time": "14:30",
  "birth_city": "New York",
  "birth_state": "NY",
  "birth_country": "USA",
  "timezone": "America/New_York",
  "house_system": "placidus",
  "use_extended_planets": true,
  "progressed_for": "2024-01-15",
  "progression_method": "secondary"
}
```

**Alternative with Coordinates:**
```json
{
  "birth_date": "1990-01-15",
  "birth_time": "14:30",
  "coordinates": {
    "latitude": 40.7128,
    "longitude": -74.0060
  },
  "timezone": "America/New_York",
  "house_system": "whole_sign"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "planets": {
      "sun": {"longitude": 295.123, "latitude": 0.0, "house": 10},
      "moon": {"longitude": 123.456, "latitude": 1.2, "house": 4},
      // ... other planets
    },
    "houses": {
      "1": {"cusp": 15.789, "sign": "Aries"},
      // ... other houses
    },
    "aspects": [
      {
        "planet1": "sun",
        "planet2": "moon", 
        "aspect": "trine",
        "orb": 2.5,
        "applying": true
      }
      // ... other aspects
    ],
    "chart_info": {
      "location": "New York, NY, USA",
      "timezone": "America/New_York",
      "house_system": "placidus"
    }
  }
}
```

### Chart Interpretation
**POST** `/api/interpret`

Provides astrological interpretations for chart elements.

**Request Body:**
```json
{
  "birth_date": "1990-01-15",
  "birth_time": "14:30",
  "birth_city": "New York",
  "interpretation_type": "personality"
}
```

## Astrocartography

### Calculate Astrocartography Lines
**POST** `/api/astrocartography`

Generates planetary lines for astrocartography mapping.

**Request Body:**
```json
{
  "birth_date": "1990-01-15",
  "birth_time": "14:30",
  "birth_city": "New York",
  "birth_state": "NY", 
  "birth_country": "USA",
  "timezone": "America/New_York",
  "line_types": ["ac", "dc", "mc", "ic"],
  "planets": ["sun", "moon", "mercury", "venus", "mars"],
  "map_bounds": {
    "north": 85,
    "south": -85,
    "east": 180,
    "west": -180
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "type": "FeatureCollection",
    "features": [
      {
        "type": "Feature",
        "geometry": {
          "type": "LineString",
          "coordinates": [[-180, 45.123], [180, 45.123]]
        },
        "properties": {
          "planet": "sun",
          "line_type": "ac",
          "description": "Sun Ascendant Line"
        }
      }
      // ... other lines
    ]
  }
}
```

## Utility Endpoints

### House Systems
**GET** `/api/house-systems`

Returns all supported house systems with categories and descriptions.

**Response:**
```json
{
  "success": true,
  "data": {
    "systems": {
      "placidus": {
        "name": "Placidus", 
        "category": "quadrant",
        "description": "Most popular time-based house system"
      },
      "whole_sign": {
        "name": "Whole Sign",
        "category": "equal", 
        "description": "Traditional equal house system"
      }
      // ... other systems
    },
    "categories": ["quadrant", "equal", "other"],
    "default": "placidus",
    "recommended": ["placidus", "whole_sign", "koch"]
  }
}
```

### Location Services
**GET** `/api/location-suggestions?query={search_term}`

Provides location suggestions for geocoding.

**Parameters:**
- `query` (required): Location search term

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "name": "New York, NY, USA",
      "latitude": 40.7128,
      "longitude": -74.0060,
      "timezone": "America/New_York",
      "country": "USA",
      "state": "NY"
    }
    // ... other suggestions
  ]
}
```

### Timezone Detection
**GET** `/api/detect-timezone?lat={latitude}&lon={longitude}`

Automatically detects timezone from coordinates.

**Parameters:**
- `lat` (required): Latitude coordinate
- `lon` (required): Longitude coordinate  

**Response:**
```json
{
  "success": true,
  "data": {
    "timezone": "America/New_York",
    "offset": "-05:00",
    "dst": true
  }
}
```

### Available Timezones
**GET** `/api/timezones`

Returns list of all available timezone identifiers.

**Response:**
```json
{
  "success": true,
  "data": [
    "America/New_York",
    "Europe/London", 
    "Asia/Tokyo",
    // ... other timezones
  ]
}
```

## Advanced Features

### Paran Calculations
**POST** `/api/parans`

Calculates paran relationships between celestial bodies.

**Request Body:**
```json
{
  "birth_date": "1990-01-15",
  "birth_time": "14:30",
  "coordinates": {
    "latitude": 40.7128,
    "longitude": -74.0060
  },
  "timezone": "America/New_York",
  "planet1": "sun",
  "planet2": "mars"
}
```

## Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid or missing parameters |
| 404 | Not Found - Endpoint does not exist |
| 500 | Internal Server Error - Calculation or server error |

## Rate Limiting

Currently, no rate limiting is implemented. For production use, consider implementing appropriate rate limiting based on your needs.

## SDKs and Examples

For detailed usage examples and integration guides, see the `/docs` directory in the project repository.
