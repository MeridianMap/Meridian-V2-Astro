import { useState } from 'react';
import axios from 'axios';

export default function useCCGData(layerManager, forceMapUpdate) {
  const [loadingStep, setLoadingStep] = useState(null);
  const [error, setError] = useState(null);

  const fetchCCG = async (formData, ccgDate, lineToggles = {}) => {
    setError(null);
    setLoadingStep('ephemeris');
    try {
      console.log('🟦 fetchCCG called with:', { formData, ccgDate, lineToggles });
      
      // Validate required fields
      if (!formData.birth_date || !formData.birth_time || !formData.timezone) {
        throw new Error('Missing required birth data for CCG calculation');
      }
      
      const ccgPayload = {
        birth_date: ccgDate, // Use CCG date instead of birth date
        birth_time: formData.birth_time,
        birth_city: formData.birth_city,
        birth_state: formData.birth_state,
        birth_country: formData.birth_country,
        timezone: formData.timezone,
        house_system: formData.house_system || 'whole_sign',
        use_extended_planets: true
      };
      
      console.log('🟦 CCG API payload:', ccgPayload);
      const ccgResult = await axios.post('/api/calculate', ccgPayload);
      console.log('🟦 CCG chart result:', ccgResult.data);
      
      // Use the astrocartography data from the chart response
      if (ccgResult.data.astrocartography) {
        // Tag all features with CCG layer type and store line toggles for filtering
        const ccgData = {
          ...ccgResult.data.astrocartography,
          features: ccgResult.data.astrocartography.features.map(f => ({
            ...f,
            properties: {
              ...f.properties,
              layer: 'CCG'
            }
          })),
          lineToggles // Store the toggles so they can be used for filtering
        };
        
        layerManager.setLayerData('CCG', ccgData);
        layerManager.setLayerVisible('CCG', true);
        forceMapUpdate();
        console.log('🟦 CCG data set with', ccgData.features.length, 'features');
      } else {
        console.log('🟦 No astrocartography data in CCG response');
      }
      
      setLoadingStep('done');
    } catch (error) {
      console.error('🟦 CCG error:', error);
      setError('Failed to generate CCG overlay.');
      setLoadingStep(null);
    }
  };

  return { loadingStep, error, fetchCCG };
}
