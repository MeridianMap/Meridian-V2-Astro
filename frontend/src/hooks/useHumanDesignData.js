import { useState } from 'react';
import axios from 'axios';

export default function useAstroData(layerManager, forceMapUpdate) {
  const [loadingStep, setLoadingStep] = useState(null);
  const [error, setError] = useState(null);
  const fetchAstroData = async (formData, coordinates = null) => {
    setError(null);
    setLoadingStep('astro_calculation');
    
    try {
      console.log('🟣 fetchAstroData called with:', formData, 'coordinates:', coordinates);
      
      // Validate required fields
      if (!formData.birth_date || !formData.birth_time || !formData.timezone) {
        throw new Error('Missing required birth data for Astro calculation');
      }
      
      const astroPayload = {
        birth_date: formData.birth_date,
        birth_time: formData.birth_time,
        birth_city: formData.birth_city,
        birth_state: formData.birth_state,
        birth_country: formData.birth_country,
        timezone: formData.timezone,
        house_system: formData.house_system || 'whole_sign',
        use_extended_planets: true,
        // Include coordinates if available
        ...(coordinates && { coordinates }),
        filter_options: {
          include_planets: true,
          include_aspects: true,
          include_fixed_stars: false, // Excludes fixed stars
          include_hermetic_lots: true,
          include_parans: true,
          include_ac_dc: true,
          include_ic_mc: true,
        }
      };
      
      console.log('🟣 API payload for /api/astrocartography:', astroPayload);
      const astroResult = await axios.post('/api/astrocartography', astroPayload);
      console.log('🟣 Astrocartography result:', astroResult.data);
      
      // The response is already a GeoJSON FeatureCollection from /api/astrocartography
      if (astroResult.data.features) {
        // Features should already be tagged by backend
        const astroData = astroResult.data;
        
        console.log('🟣 Features Sample (first 3):', astroData.features.slice(0, 3).map(f => ({
          planet: f.properties?.planet,
          layer: f.properties?.layer,
          lineType: f.properties?.line_type,
          coordinates: f.geometry?.coordinates?.[0]?.[0] // First coordinate
        })));
        
        // Store the data in layer manager
        layerManager.setLayerData('ASTRO_CARTOGRAPHY', astroData);
        layerManager.setLayerVisible('ASTRO_CARTOGRAPHY', true);
        
        forceMapUpdate();
        console.log('🟣 Astro data set with', astroData.features.length, 'features');
      } else {
        console.log('🟣 No features in response');
      }
      
      setLoadingStep('done');
    } catch (err) {
      console.error('🟣 Astro generation error:', err);
      setError(`Failed to generate Astro data: ${err.message}`);
      setLoadingStep(null);
    }
  };

  return { loadingStep, error, fetchAstroData };
}
