# Development Guide

## 🏗️ Architecture Overview

### System Architecture
Meridian follows a modern client-server architecture with clear separation of concerns:

```
┌─────────────────┐    HTTP/REST     ┌─────────────────┐
│   React Frontend│ ◄──────────────► │  Flask Backend  │
│   (Vite + Leaflet) │                │  (Swiss Ephemeris) │
└─────────────────┘                  └─────────────────┘
         │                                      │
         │                                      │
    ┌──────────┐                        ┌──────────────┐
    │  Leaflet │                        │ Swiss        │
    │  Maps    │                        │ Ephemeris    │
    │  UI      │                        │ Calculations │
    └──────────┘                        └──────────────┘
```

### Technology Stack

**Frontend:**
- **React 19**: Modern React with concurrent features
- **Vite**: Fast build tool and dev server
- **Leaflet**: Interactive mapping library
- **Axios**: HTTP client for API communication

**Backend:**
- **Flask**: Lightweight Python web framework
- **Swiss Ephemeris**: High-precision astronomical calculations
- **Geopy**: Geocoding and location services
- **NumPy/SciPy**: Mathematical calculations

## 📁 Project Structure Deep Dive

### Backend Structure
```
backend/
├── api.py                    # Main Flask application & routing
├── ephemeris.py             # Core astronomical calculations
├── astrocartography.py      # Astrocartography line generation
├── house_systems.py         # House system implementations
├── humandesign_gates.py     # Human Design calculations
├── location_utils.py        # Geocoding & timezone utilities
├── layers/                  # Specialized calculation layers
│   ├── __init__.py
│   └── humandesign.py      # Human Design layer calculations
├── ephe/                   # Swiss Ephemeris data files
├── test_*.py              # Test files (multiple categories)
└── utils.py               # Shared utility functions
```

### Frontend Structure
```
frontend/src/
├── App.jsx                 # Main application component
├── main.jsx               # Application entry point
├── components/            # Reusable UI components
│   ├── CCGControls.jsx   # Chart control panel
│   ├── CCGDateControls.jsx # Date/time controls
│   ├── ChartForm.jsx     # Chart input form
│   ├── ErrorBoundary.jsx # Error handling component
│   └── TransitControls.jsx # Transit controls
├── hooks/                 # Custom React hooks
│   ├── useAstroData.js   # Astrological data management
│   ├── useCCGData.js     # Chart calculation data
│   ├── useChartData.js   # Chart state management
│   ├── useCitySuggestions.js # Location search
│   ├── useHouseSystems.js # House system data
│   ├── useHumanDesignData.js # HD calculations
│   └── useTransitData.js # Transit calculations
├── Astromap.jsx          # Main map component
├── AstroTooltipContent.jsx # Map tooltip content
└── apiClient.js          # API communication layer
```

## 🔧 Development Environment Setup

### Required Tools
- **Python 3.9+** (3.11 recommended for performance)
- **Node.js 18+** with npm
- **Git** for version control
- **VS Code** (recommended) with extensions:
  - Python
  - ES7+ React/Redux/React-Native snippets
  - Prettier - Code formatter
  - Python Docstring Generator

### Environment Configuration

**Backend Environment Variables:**
```bash
# .env file in backend/
FLASK_ENV=development
FLASK_DEBUG=true
GEOAPIFY_API_KEY=your_api_key_here
EPHEMERIS_PATH=./ephe
LOG_LEVEL=INFO
```

**Frontend Environment Variables:**
```bash
# .env file in frontend/
VITE_GEOAPIFY_API_KEY=your_api_key_here
VITE_API_BASE_URL=http://localhost:5000/api
VITE_DEBUG_MODE=true
```

### IDE Configuration

**VS Code Settings (.vscode/settings.json):**
```json
{
  "python.defaultInterpreterPath": "./backend/venv/bin/python",
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "editor.formatOnSave": true,
  "files.associations": {
    "*.jsx": "javascriptreact"
  }
}
```

## 🧩 Core Components Deep Dive

### Backend Components

#### 1. Ephemeris Calculations (`ephemeris.py`)
```python
def calculate_chart(birth_date, birth_time, coordinates, house_system='placidus'):
    """
    Core function for chart calculations.
    
    Handles:
    - Planetary position calculations
    - House cusp calculations  
    - Aspect calculations
    - Coordinate transformations
    """
```

#### 2. Astrocartography (`astrocartography.py`)
```python
def calculate_astrocartography_lines_geojson(birth_data, line_types, planets):
    """
    Generates GeoJSON for astrocartography lines.
    
    Returns:
    - GeoJSON FeatureCollection
    - Line coordinates for mapping
    - Metadata for each line type
    """
```

#### 3. House Systems (`house_systems.py`)
```python
def get_house_system_choices():
    """
    Returns available house systems with categories:
    - Quadrant systems (Placidus, Koch, etc.)
    - Equal systems (Whole Sign, Equal, etc.)
    - Other systems (Campanus, Regiomontanus, etc.)
    """
```

### Frontend Components

#### 1. Chart Data Hooks
```javascript
// useChartData.js - Manages chart calculation state
const useChartData = () => {
  const [chartData, setChartData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const calculateChart = async (birthData) => {
    // Chart calculation logic
  };
  
  return { chartData, loading, error, calculateChart };
};
```

#### 2. Astrocartography Map Component
```javascript
// Astromap.jsx - Main mapping component
const Astromap = ({ chartData, onLineSelect }) => {
  const [map, setMap] = useState(null);
  const [lines, setLines] = useState([]);
  
  // Map initialization and line rendering logic
  
  return (
    <MapContainer>
      {/* Map layers and controls */}
    </MapContainer>
  );
};
```

## 🔄 Data Flow

### Chart Calculation Flow
```
1. User Input (ChartForm) 
   ↓
2. Form Validation
   ↓  
3. API Request (useChartData)
   ↓
4. Backend Processing (ephemeris.py)
   ↓
5. Swiss Ephemeris Calculations
   ↓
6. Response Formatting
   ↓
7. Frontend State Update
   ↓
8. UI Rendering
```

### Astrocartography Flow
```
1. Chart Data Available
   ↓
2. Line Type Selection
   ↓
3. API Request (astrocartography.py)
   ↓
4. Line Calculation
   ↓
5. GeoJSON Generation
   ↓
6. Map Layer Update (Leaflet)
   ↓
7. Interactive Line Display
```

## 🧪 Testing Strategy

### Backend Testing Approach

**1. Unit Tests (`test_*.py`):**
```python
# test_ephemeris.py
def test_sun_position_calculation():
    """Test accurate Sun position for known date"""
    result = calculate_planet_position('sun', datetime(2000, 1, 1, 12, 0))
    assert abs(result['longitude'] - expected_longitude) < 0.01

def test_house_cusp_calculation():
    """Test house cusp calculations for different systems"""
    for system in ['placidus', 'koch', 'whole_sign']:
        cusps = calculate_house_cusps(test_data, system)
        assert len(cusps) == 12
        assert all(0 <= cusp < 360 for cusp in cusps.values())
```

**2. Integration Tests:**
```python
# test_api.py
def test_chart_calculation_endpoint():
    """Test full chart calculation via API"""
    response = client.post('/api/calculate', json=test_birth_data)
    assert response.status_code == 200
    data = response.get_json()
    assert 'planets' in data['data']
    assert 'houses' in data['data']
```

**3. Calculation Accuracy Tests:**
```python
# test_ccg_*.py files
def test_fixed_star_positions():
    """Verify fixed star positions against known ephemeris"""
    # Test against standard ephemeris values
```

### Frontend Testing Approach

**1. Component Tests:**
```javascript
// ChartForm.test.jsx
describe('ChartForm', () => {
  test('validates required fields', () => {
    render(<ChartForm onSubmit={mockSubmit} />);
    fireEvent.click(screen.getByText('Calculate'));
    expect(screen.getByText('Birth date is required')).toBeInTheDocument();
  });
});
```

**2. Hook Tests:**
```javascript
// useChartData.test.js
describe('useChartData', () => {
  test('calculates chart data correctly', async () => {
    const { result } = renderHook(() => useChartData());
    await act(() => result.current.calculateChart(testData));
    expect(result.current.chartData).toBeDefined();
  });
});
```

## 🚀 Performance Optimization

### Backend Performance

**1. Calculation Caching:**
```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def calculate_planetary_positions(julian_day, planet_list):
    """Cache expensive planetary calculations"""
    # Expensive Swiss Ephemeris calculations
```

**2. Efficient Data Structures:**
```python
# Use NumPy arrays for bulk calculations
import numpy as np

def calculate_multiple_aspects(planet_positions):
    """Vectorized aspect calculations"""
    positions = np.array(list(planet_positions.values()))
    # Vectorized calculations for performance
```

### Frontend Performance

**1. Component Memoization:**
```javascript
import React, { memo, useMemo } from 'react';

const AstroLine = memo(({ line, isSelected }) => {
  const lineStyle = useMemo(() => ({
    color: line.planet_color,
    weight: isSelected ? 3 : 1
  }), [line.planet_color, isSelected]);
  
  return <Polyline {...props} pathOptions={lineStyle} />;
});
```

**2. Data Loading Optimization:**
```javascript
// Lazy loading for non-critical components
const TransitControls = lazy(() => import('./components/TransitControls'));

// Debounced API calls for user input
const debouncedLocationSearch = useMemo(
  () => debounce(searchLocations, 300),
  []
);
```

## 🔧 Debugging Guide

### Backend Debugging

**1. Swiss Ephemeris Debugging:**
```python
# debug_chart.py - Debugging utilities
def debug_ephemeris_calculation(date, location):
    """Debug planetary calculations step by step"""
    logging.info(f"Calculating for {date} at {location}")
    # Detailed logging of each calculation step
```

**2. API Debugging:**
```bash
# Enable Flask debug mode
export FLASK_DEBUG=true
python -m backend.api

# Test specific endpoints
curl -X POST http://localhost:5000/api/calculate \
  -H "Content-Type: application/json" \
  -d '{"birth_date": "1990-01-15", ...}'
```

### Frontend Debugging

**1. React DevTools:**
- Install React Developer Tools browser extension
- Use Profiler to identify performance bottlenecks
- Monitor component re-renders

**2. Network Debugging:**
```javascript
// Add request/response logging
axios.interceptors.request.use(request => {
  console.log('Starting Request:', request);
  return request;
});

axios.interceptors.response.use(response => {
  console.log('Response:', response);
  return response;
});
```

## 🔄 Development Workflow

### Daily Development Process

**1. Start Development Environment:**
```bash
# Terminal 1: Backend
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
python -m api

# Terminal 2: Frontend  
cd frontend
npm run dev

# Terminal 3: Tests
python -m pytest backend/ --watch
```

**2. Feature Development Cycle:**
```bash
# 1. Create feature branch
git checkout -b feature/new-astro-feature

# 2. Develop with tests
# Write tests first (TDD approach)
# Implement feature
# Verify tests pass

# 3. Integration testing
# Test full workflow manually
# Check API integration
# Verify UI/UX

# 4. Code review preparation
# Run linting: black backend/ && npm run lint
# Update documentation
# Create pull request
```

### Code Quality Checks

**Pre-commit Hooks:**
```bash
# Install pre-commit
pip install pre-commit
pre-commit install

# Manual run
pre-commit run --all-files
```

**Continuous Integration:**
```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Python tests
        run: |
          pip install -r backend/requirements.txt
          python -m pytest backend/
  
  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Frontend tests
        run: |
          cd frontend
          npm install
          npm test
```

## 📊 Monitoring & Analytics

### Performance Monitoring
```python
# Add timing decorators for performance monitoring
def timing_decorator(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        logging.info(f"{func.__name__} took {end - start:.2f}s")
        return result
    return wrapper

@timing_decorator
def calculate_astrocartography_lines(data):
    # Monitored function
```

### Error Tracking
```javascript
// Frontend error boundary with reporting
class ErrorBoundary extends React.Component {
  componentDidCatch(error, errorInfo) {
    // Log error to monitoring service
    console.error('Component Error:', error, errorInfo);
  }
}
```

## 🛠️ Useful Development Tools

### Backend Tools
- **iPython**: Interactive Python shell for testing
- **pytest-watch**: Automatic test running
- **Black**: Code formatting
- **Pylint**: Code linting
- **Memory Profiler**: Performance profiling

### Frontend Tools
- **React DevTools**: Component debugging
- **Redux DevTools**: State debugging (if using Redux)
- **Lighthouse**: Performance auditing
- **Chrome DevTools**: Network and performance debugging

### Swiss Ephemeris Tools
- **Astrolog**: Cross-reference calculations
- **Online Ephemeris**: Verify planetary positions
- **JPL Horizons**: NASA ephemeris for verification

---

This development guide provides the foundation for contributing effectively to Meridian. For specific questions, consult the codebase documentation or create a GitHub discussion.
