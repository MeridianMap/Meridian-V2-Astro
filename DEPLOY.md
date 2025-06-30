# Meridian V2.1 Deployment Guide

## Render.com Deployment

This application is configured for easy deployment on Render.com using the `render.yaml` configuration file.

### Prerequisites

1. **GitHub Repository**: Push your code to a GitHub repository
2. **Render Account**: Sign up for a free account at [render.com](https://render.com)

### Deployment Steps

1. **Connect Repository**:
   - Go to Render.com dashboard
   - Click "New +" → "Blueprint"
   - Connect your GitHub account and select your repository
   - Choose the `render-deploy` branch

2. **Environment Variables**:
   The following environment variables are automatically configured in `render.yaml`:
   - `PYTHONUNBUFFERED=1`
   - `FLASK_ENV=production`
   - `PORT=5000`

3. **Optional: Add Geoapify API Key**:
   - In the Render dashboard, go to your service settings
   - Add environment variable: `VITE_GEOAPIFY_API_KEY` (for location search functionality)
   - Get a free API key at [geoapify.com](https://www.geoapify.com/)

### Service Configuration

The deployment creates a single web service that:
- Serves the React frontend at the root URL
- Provides API endpoints at `/api/*`
- Uses Docker for consistent deployment
- Runs on Render's free tier

### Architecture

```
Render Service (meridian-v2)
├── Frontend (React + Vite) → served at /
├── Backend (Flask + Python) → API at /api/*
├── Swiss Ephemeris Data → included in Docker image
└── Database → None (stateless calculations)
```

### URLs

After deployment, your application will be available at:
- **Frontend**: `https://meridian-v2.onrender.com`
- **API Health**: `https://meridian-v2.onrender.com/api/health`
- **API Docs**: `https://meridian-v2.onrender.com/api`

### Features Included

✅ **Natal Chart Calculations**
✅ **Astrocartography Lines**  
✅ **Transit Overlays**
✅ **CCG (Cyclic Cosmology) Overlays**
✅ **Human Design Integration**
✅ **Fixed Star Calculations**
✅ **Hermetic Lots**
✅ **Parans Calculations**
✅ **Multiple House Systems**
✅ **Interactive Map with Tooltips**
✅ **Layer Management System**

### Performance Notes

- **Cold Start**: ~30-60 seconds on free tier
- **Active Response**: <3 seconds for calculations
- **Memory Usage**: ~512MB typical
- **Build Time**: ~5-10 minutes

### Troubleshooting

1. **Build Fails**: Check that all requirements.txt dependencies are compatible
2. **Frontend 404**: Ensure frontend build completed successfully
3. **API Errors**: Check logs in Render dashboard for Python errors
4. **Swiss Ephemeris Issues**: Ephemeris data is bundled in Docker image

### Local Development

For local development:
```bash
# Backend
cd backend
pip install -r requirements.txt
python api.py

# Frontend  
cd frontend
npm install
npm run dev
```

### Support

For deployment issues, check:
- Render service logs
- GitHub Actions (if using CI/CD)
- This repository's Issues section
