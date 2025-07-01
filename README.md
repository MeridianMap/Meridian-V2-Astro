# Meridian Astrocartography Platform V2.1

## 🌟 Project Overview
Meridian is a comprehensive astrocartography and ephemeris calculation platform that combines high-precision astronomical calculations with an intuitive, interactive mapping interface. Built with modern web technologies, it provides professional-grade astrological tools for astrologers, researchers, and enthusiasts.

### Key Features
- **High-Precision Calculations**: Powered by Swiss Ephemeris for astronomical accuracy
- **Interactive Astrocartography**: Real-time planetary line mapping with geographic visualization
- **SVG Chart Rendering**: Generate professional astrological charts for all layers (Natal, Human Design, Transit, CCG)
- **Human Design Integration**: Complete Human Design chart calculations and gate systems
- **Multiple House Systems**: Support for all major house systems with detailed comparisons
- **Location Intelligence**: Advanced geocoding with timezone detection
- **Responsive Design**: Optimized for desktop and mobile devices
- **Real-time Updates**: Live chart calculations with dynamic parameter adjustments

## 🏗️ Architecture

### Backend (Python + Flask)
- **Framework**: Flask with CORS support
- **Calculations**: Swiss Ephemeris (pyswisseph) for astronomical precision
- **Astrocartography**: Custom algorithms for planetary line calculations
- **Geocoding**: Geoapify integration for location services
- **House Systems**: Comprehensive support for traditional and modern systems

### Frontend (React + Vite)
- **Framework**: React 19 with modern hooks and context
- **Build Tool**: Vite for fast development and optimized production builds
- **Mapping**: Leaflet with React-Leaflet for interactive cartography
- **State Management**: React Context API with custom hooks
- **Styling**: Modern CSS with responsive design principles

## 📁 Project Structure

```
Meridian Map V2.1/
├── backend/                     # Python Flask API
│   ├── api.py                  # Main Flask application and routes
│   ├── ephemeris.py            # Core astronomical calculations
│   ├── astrocartography.py     # Astrocartography line calculations
│   ├── humandesign_gates.py    # Human Design system integration
│   ├── house_systems.py        # Multiple house system support
│   ├── location_utils.py       # Geocoding and timezone utilities
│   ├── layers/                 # Specialized calculation layers
│   ├── ephe/                   # Swiss Ephemeris data files
│   ├── test_*.py              # Comprehensive test suite
│   └── requirements.txt        # Python dependencies
├── frontend/                   # React application
│   ├── src/
│   │   ├── components/         # Reusable UI components
│   │   ├── hooks/             # Custom React hooks for data management
│   │   ├── App.jsx            # Main application component
│   │   └── main.jsx           # Application entry point
│   ├── public/                # Static assets
│   └── package.json           # Node.js dependencies
├── docs/                      # Comprehensive documentation
├── tests/                     # Integration and E2E tests
├── docker-compose.yml         # Docker deployment configuration
├── render.yaml               # Render.com deployment settings
└── DEPLOY.md                 # Detailed deployment instructions
```

## 🚀 Quick Start (Local Development)

### Prerequisites
- **Python**: 3.9+ (recommended: 3.11)
- **Node.js**: 18+ (for frontend development)
- **Git**: For version control

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd "Meridian Map V2.1"
   ```

2. **Backend Setup**
   ```bash
   # Install Python dependencies
   pip install -r backend/requirements.txt
   
   # Or use the lock file for exact versions
   pip install -r backend/requirements.lock
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

4. **Environment Configuration**
   
   Create a `.env` file in the backend directory:
   ```env
   # Optional: Geoapify API key for enhanced geocoding
   GEOAPIFY_API_KEY=your_geoapify_api_key_here
   
   # Flask configuration
   FLASK_ENV=development
   FLASK_DEBUG=true
   ```
   
   Create a `.env` file in the frontend directory:
   ```env
   # Geoapify API key for location search
   VITE_GEOAPIFY_API_KEY=your_geoapify_api_key_here
   
   # API endpoint (adjust for your setup)
   VITE_API_BASE_URL=http://localhost:5000/api
   ```

5. **Start Development Servers**
   ```bash
   # Terminal 1: Start backend
   python -m backend.api
   
   # Terminal 2: Start frontend
   cd frontend
   npm run dev
   ```

6. **Access the Application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:5000/api
   - Health Check: http://localhost:5000/api/health

## 🌍 Environment Variables

| Variable | Location | Default/Example | Description |
|----------|----------|-----------------|-------------|
| `VITE_GEOAPIFY_API_KEY` | Frontend | `your_api_key` | Geoapify API key for location search and geocoding |
| `GEOAPIFY_API_KEY` | Backend | `your_api_key` | Server-side Geoapify key (optional) |
| `FLASK_ENV` | Backend | `development` | Flask environment setting |
| `FLASK_DEBUG` | Backend | `true` | Enable Flask debug mode |
| `VITE_API_BASE_URL` | Frontend | `http://localhost:5000/api` | Backend API endpoint URL |

## 🔧 API Endpoints

### Core Endpoints
- `GET /api/health` — Service health check, returns `{ok: true}`
- `GET /api` — API status and version information
- `POST /api/calculate` — Generate natal charts with planetary positions
- `POST /api/astrocartography` — Calculate astrocartography lines for mapping
- `POST /api/interpret` — Get astrological interpretations for chart elements

### Utility Endpoints
- `GET /api/house-systems` — List all supported house systems with categories
- `GET /api/location-suggestions` — Geocoding and location search
- `GET /api/detect-timezone` — Automatic timezone detection from coordinates
- `GET /api/timezones` — List available timezones
- `POST /api/parans` — Calculate paran relationships between celestial bodies

### Specialized Features
- **Human Design Integration**: Complete Human Design chart calculations
- **Transit Calculations**: Real-time planetary transits and progressions  
- **Fixed Star Analysis**: Traditional fixed star positions and influences
- **Multiple Coordinate Systems**: Support for various astronomical coordinate systems

## 🧪 Testing

The project includes comprehensive testing across multiple domains:

### Backend Testing
```bash
# Run all backend tests
cd backend
python -m pytest

# Run specific test categories
python -m pytest test_api.py          # API endpoint tests
python -m pytest test_ccg*.py         # Chart calculation tests
python -m pytest test_hd*.py          # Human Design tests
python -m pytest test_transit*.py     # Transit calculation tests
```

### Available Test Suites
- **API Tests**: Endpoint functionality and data validation
- **Calculation Tests**: Astronomical accuracy and edge cases
- **Integration Tests**: Full workflow testing
- **Human Design Tests**: Gate calculations and chart generation
- **Geocoding Tests**: Location services and timezone detection

## 🚀 Production Deployment

See [DEPLOY.md](DEPLOY.md) for comprehensive deployment instructions including:
- **Render.com**: One-click deployment with `render.yaml`
- **Docker**: Containerized deployment with `docker-compose.yml`
- **Manual Deployment**: Traditional server setup
- **Environment Configuration**: Production environment variables

## 📚 Documentation

Comprehensive documentation is available in the `docs/` directory:
- **[API Reference](docs/api.md)** — Complete API documentation
- **[Contributing Guide](docs/contributing.md)** — Development guidelines
- **[Human Design](docs/humandesign.md)** — Human Design system integration
- **[Environment Setup](docs/env.md)** — Configuration details

## 🔄 Development Workflow

### Branch Strategy
- `main` — Production-ready code
- `render-deploy` — Deployment-specific configurations
- `feature/*` — Feature development branches

### Code Quality
- **Python**: Follows PEP 8 standards with comprehensive docstrings
- **JavaScript**: Modern ES6+ with React best practices
- **Testing**: Test-driven development with high coverage
- **Documentation**: Inline comments and comprehensive docs

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Development setup instructions
- Code style guidelines
- Testing requirements
- Pull request process
- Issue reporting guidelines

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support & Community

- **Issues**: Report bugs and request features on GitHub Issues
- **Documentation**: Comprehensive guides in the `docs/` folder
- **API Questions**: Check the API documentation in `docs/api.md`

## ⚡ Performance & Scalability

- **Swiss Ephemeris**: Optimized for high-precision calculations
- **Caching**: Intelligent caching for frequently requested calculations
- **Responsive Design**: Optimized for all device sizes
- **Production Ready**: Configured for horizontal scaling

---

*Meridian V2.1 - Bridging ancient wisdom with modern technology* ✨
- All documentation is consolidated in `docs/` (MkDocs-ready).
- See `Makefile` for dev/test/build commands.
