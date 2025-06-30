import { useState } from 'react';
import axios from 'axios';

export default function useHumanDesignData(layerManager, forceMapUpdate) {
  const [loadingStep, setLoadingStep] = useState(null);
  const [error, setError] = useState(null);
  const fetchHumanDesign = async (formData, coordinates = null) => {
    setError(null);
    setLoadingStep('hd_calculation');
    
    try {
      console.log('🟣 fetchHumanDesign called with:', formData, 'coordinates:', coordinates);
      
      // Validate required fields
      if (!formData.birth_date || !formData.birth_time || !formData.timezone) {
        throw new Error('Missing required birth data for Human Design calculation');
      }
      
      const hdPayload = {
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
          include_fixed_stars: false, // HD excludes fixed stars
          include_hermetic_lots: true,
          include_parans: true,
          include_ac_dc: true,
          include_ic_mc: true,
          layer_type: 'HD_DESIGN' // Critical: tells backend to use HD calculation
        }
      };
      
      console.log('🟣 HD API payload for /api/astrocartography:', hdPayload);
      const hdResult = await axios.post('/api/astrocartography', hdPayload);
      console.log('🟣 HD astrocartography result:', hdResult.data);
      
      // Log design vs birth datetime comparison
      if (hdResult.data.properties) {
        console.log('🟣 HD Datetime Comparison:', {
          birthDatetime: hdResult.data.properties.birth_datetime,
          designDatetime: hdResult.data.properties.design_datetime,
          timeDifference: hdResult.data.properties.design_datetime ? 
            `${Math.round((new Date(hdResult.data.properties.birth_datetime) - new Date(hdResult.data.properties.design_datetime)) / (1000 * 60 * 60 * 24))} days` : 
            'N/A'
        });
      }
      
      // The response is already a GeoJSON FeatureCollection from /api/astrocartography
      if (hdResult.data.features) {
        // Features should already be tagged with HD_DESIGN layer by backend
        const hdData = hdResult.data;
        
        console.log('🟣 HD Features Sample (first 3):', hdData.features.slice(0, 3).map(f => ({
          planet: f.properties?.planet,
          layer: f.properties?.layer,
          lineType: f.properties?.line_type,
          coordinates: f.geometry?.coordinates?.[0]?.[0] // First coordinate
        })));
        
        // Store the data in layer manager
        layerManager.setLayerData('HD_DESIGN', hdData);
        layerManager.setLayerVisible('HD_DESIGN', true);
        
        forceMapUpdate();
        console.log('🟣 HD data set with', hdData.features.length, 'features');
      } else {
        console.log('🟣 No features in HD response');
      }
      
      setLoadingStep('done');
      setLoadingStep('done');
    } catch (err) {
      console.error('🟣 Human Design generation error:', err);
      setError(`Failed to generate Human Design data: ${err.message}`);
      setLoadingStep(null);
    }
  };

  return { loadingStep, error, fetchHumanDesign };
}
