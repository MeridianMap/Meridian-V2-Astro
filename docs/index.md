# Meridian Astrocartography Platform Documentation

Welcome to the comprehensive documentation for the Meridian Astrocartography Platform - a modern, high-precision astrocartography and ephemeris calculation platform.

## 🌟 What is Meridian?

Meridian combines cutting-edge astronomical calculations with intuitive mapping interfaces to provide professional-grade astrological tools. Built with Swiss Ephemeris for maximum accuracy and modern web technologies for optimal user experience.

### Key Features
- **High-Precision Calculations**: Swiss Ephemeris for astronomical accuracy
- **Interactive Astrocartography**: Real-time planetary line mapping
- **Human Design Integration**: Complete HD chart calculations and mapping
- **Multiple House Systems**: Support for all major astrological house systems
- **Modern Technology Stack**: React 19, Flask, and Leaflet

## 📚 Documentation Guide

### 🚀 Getting Started
| Document | Description |
|----------|-------------|
| **[Quick Start Guide](../README.md)** | Installation and basic setup |
| **[Environment Configuration](env.md)** | Environment variables and API keys |
| **[API Reference](api.md)** | Complete API documentation |

### 👨‍💻 For Developers
| Document | Description |
|----------|-------------|
| **[Development Guide](DEVELOPMENT.md)** | Architecture and development workflow |
| **[Contributing Guidelines](../CONTRIBUTING.md)** | How to contribute to the project |
| **[Changelog](../CHANGELOG.md)** | Version history and release notes |

### 🚀 For DevOps
| Document | Description |
|----------|-------------|
| **[Deployment Guide](../DEPLOY.md)** | Production deployment instructions |
| **[Environment Setup](env.md)** | Configuration and security |

### 🔮 For Astrologers
| Document | Description |
|----------|-------------|
| **[Human Design Integration](humandesign.md)** | HD system documentation |
| **[API Reference](api.md)** | Calculation options and endpoints |
| **[Feature Roadmap](ROADMAP.md)** | Upcoming astrological features |

## 🎯 Quick Links

### Most Popular Pages
- **[API Endpoints Overview](api.md#core-endpoints)** - Start here for API integration
- **[Local Development Setup](../README.md#quick-start-local-development)** - Get up and running quickly  
- **[Deployment on Render.com](../DEPLOY.md#rendercom-deployment-guide)** - Deploy to production
- **[Environment Variables](env.md#environment-variables-reference)** - Complete configuration guide

### Common Tasks
- **[Calculate a Chart](api.md#calculate-natal-chart)** - POST /api/calculate
- **[Generate Astrocartography Lines](api.md#calculate-astrocartography-lines)** - POST /api/astrocartography
- **[Get Location Suggestions](api.md#location-services)** - GET /api/location-suggestions
- **[Check Health Status](api.md#health-check)** - GET /api/health

## 🏗️ Architecture Overview

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
- **Frontend**: React 19, Vite, Leaflet, Axios
- **Backend**: Flask, Swiss Ephemeris, NumPy, Geopy
- **Deployment**: Docker, Render.com, Gunicorn
- **Testing**: Pytest, Vitest, comprehensive test suites

## 📖 API Overview

### Core Endpoints
- `GET /api/health` - Service health check
- `POST /api/calculate` - Generate natal charts
- `POST /api/astrocartography` - Calculate astrocartography lines
- `GET /api/house-systems` - List supported house systems
- `GET /api/location-suggestions` - Geocoding services

### Response Format
All API responses follow a consistent JSON structure:
```json
{
  "success": true,
  "data": { /* endpoint-specific data */ }
}
```

## 🔧 Quick Setup

### Prerequisites
- Python 3.9+ 
- Node.js 18+
- Git

### Installation
```bash
# Clone repository
git clone <repository-url>
cd "Meridian Map V2.1"

# Backend setup
pip install -r backend/requirements.txt

# Frontend setup  
cd frontend && npm install

# Start development servers
python -m backend.api &
npm run dev
```

### Environment Configuration
```env
# Frontend .env
VITE_GEOAPIFY_API_KEY=your_api_key_here
VITE_API_BASE_URL=http://localhost:5000/api

# Backend .env
GEOAPIFY_API_KEY=your_api_key_here
FLASK_ENV=development
FLASK_DEBUG=true
```

## 🤝 Community & Support

### Getting Help
- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: Community questions and discussions
- **Documentation**: Comprehensive guides and reference materials

### Contributing
We welcome contributions! See our **[Contributing Guide](../CONTRIBUTING.md)** for:
- Code style guidelines
- Development workflow
- Testing requirements
- Pull request process

## 🔄 Recent Updates

### Version 2.1.0 (Latest)
- Complete documentation overhaul
- Enhanced Human Design integration
- Improved testing coverage
- Docker containerization
- Performance optimizations

See **[Changelog](../CHANGELOG.md)** for complete version history.

## 🚀 What's Next?

Check out our **[Roadmap](ROADMAP.md)** for upcoming features:
- Enhanced transit calculations (v2.2.0)
- Fixed stars integration (v2.3.0)
- User authentication and chart storage (v2.4.0)
- AI-powered interpretations (v3.0.0)

---

*Ready to explore the stars? Start with our **[Quick Start Guide](../README.md)** or dive into the **[API Documentation](api.md)**!* ✨
