# Environment Configuration Guide

This guide provides comprehensive information about configuring your development and production environments for the Meridian Astrocartography Platform.

## 🔧 Environment Types

### Development Environment
For local development with hot reloading and debugging features.

### Production Environment  
For deployment on servers with optimized builds and performance.

### Testing Environment
For running automated tests and CI/CD pipelines.

## 📋 Environment Variables Reference

### Backend Environment Variables

#### Required Variables
| Variable | Description | Example | Default |
|----------|-------------|---------|---------|
| `FLASK_ENV` | Flask environment mode | `development` \| `production` | `development` |
| `FLASK_DEBUG` | Enable Flask debug mode | `true` \| `false` | `false` |

#### Optional Variables
| Variable | Description | Example | Default |
|----------|-------------|---------|---------|
| `GEOAPIFY_API_KEY` | Server-side Geoapify API key | `your_api_key_here` | None |
| `EPHEMERIS_PATH` | Custom path to ephemeris files | `./custom/ephe` | `./ephe` |
| `LOG_LEVEL` | Logging level | `DEBUG` \| `INFO` \| `WARNING` \| `ERROR` | `INFO` |
| `PORT` | Server port | `5000` | `5000` |
| `HOST` | Server host | `0.0.0.0` | `127.0.0.1` |

### Frontend Environment Variables

#### Required Variables
| Variable | Description | Example | Default |
|----------|-------------|---------|---------|
| `VITE_GEOAPIFY_API_KEY` | Client-side Geoapify API key | `your_api_key_here` | None |

#### Optional Variables
| Variable | Description | Example | Default |
|----------|-------------|---------|---------|
| `VITE_API_BASE_URL` | Backend API base URL | `http://localhost:5000/api` | `/api` |
| `VITE_DEBUG_MODE` | Enable debug logging | `true` \| `false` | `false` |
| `VITE_DEFAULT_MAP_CENTER_LAT` | Default map center latitude | `40.7128` | `40.7128` |
| `VITE_DEFAULT_MAP_CENTER_LNG` | Default map center longitude | `-74.0060` | `-74.0060` |
| `VITE_DEFAULT_MAP_ZOOM` | Default map zoom level | `10` | `10` |

## 📁 Environment File Setup

### Development Environment Files

**Backend `.env` file:**
```env
# Backend Development Configuration
FLASK_ENV=development
FLASK_DEBUG=true
LOG_LEVEL=DEBUG

# API Keys
GEOAPIFY_API_KEY=your_geoapify_api_key_here

# Development Settings
HOST=127.0.0.1
PORT=5000

# Ephemeris Configuration
EPHEMERIS_PATH=./ephe
```

**Frontend `.env` file:**
```env
# Frontend Development Configuration
VITE_GEOAPIFY_API_KEY=your_geoapify_api_key_here
VITE_API_BASE_URL=http://localhost:5000/api
VITE_DEBUG_MODE=true

# Map Configuration
VITE_DEFAULT_MAP_CENTER_LAT=40.7128
VITE_DEFAULT_MAP_CENTER_LNG=-74.0060
VITE_DEFAULT_MAP_ZOOM=10

# Development Features
VITE_ENABLE_DEV_TOOLS=true
```

## 🔑 API Key Setup

### Geoapify API Key
1. **Sign up** at [Geoapify](https://www.geoapify.com/)
2. **Create a new project** in your dashboard
3. **Generate an API key** with the following permissions:
   - Geocoding API
   - Places API (optional, for enhanced search)
4. **Add the key** to your environment files:
   - Backend: `GEOAPIFY_API_KEY=your_key`
   - Frontend: `VITE_GEOAPIFY_API_KEY=your_key`

### Rate Limits and Usage
- **Free Tier**: 3,000 requests per day
- **Paid Plans**: Higher limits available
- **Best Practices**: 
  - Cache geocoding results
  - Debounce search requests
  - Handle rate limit errors gracefully

## 🚀 Deployment Configuration

### Render.com
Environment variables are set in the Render.com dashboard:

**Backend Service:**
- `GEOAPIFY_API_KEY`: Your Geoapify API key
- `FLASK_ENV`: `production`

**Frontend Service:**
- `VITE_GEOAPIFY_API_KEY`: Your Geoapify API key
- `VITE_API_BASE_URL`: Backend service URL

## 🔒 Security Best Practices

### Environment Variable Security
1. **Never commit** `.env` files to version control
2. **Use secret management** systems in production
3. **Rotate API keys** regularly
4. **Limit API key permissions** to required services only

### Example `.gitignore` entries:
```gitignore
# Environment files
.env
.env.local
.env.development
.env.production
.env.test

# API keys and secrets
*.key
*.pem
secrets/
```

## 🛠️ Troubleshooting

### Common Issues

**1. Missing API Keys**
```
Error: VITE_GEOAPIFY_API_KEY is not defined
```
**Solution**: Add the API key to your `.env` file and restart the development server.

**2. CORS Issues**
```
Error: CORS policy blocked the request
```
**Solution**: Check that `VITE_API_BASE_URL` matches your backend URL.

**3. Environment Variables Not Loading**
```
Error: Cannot read property of undefined
```
**Solution**: 
- Ensure .env files are in the correct directory
- Restart development servers after changing .env files
- Check that variable names start with `VITE_` for frontend variables

---

For additional help with environment configuration, please check the [troubleshooting section](DEVELOPMENT.md#debugging) in our development guide.
