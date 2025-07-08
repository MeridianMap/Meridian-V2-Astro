import { useState, useCallback } from 'react';

export default function useTransitData(layerManager, forceMapUpdate) {
  const [loadingStep, setLoadingStep] = useState(null);
  const [isTransitEnabled, setIsTransitEnabled] = useState(false);

  const fetchTransits = useCallback(async (formData, customDateTime = null) => {
    try {
      setLoadingStep('transit_ephemeris');
      
      // Debug: Add console log to ensure we're using the latest version
      console.log('🔄 Transit fetch started - Version: 2025-01-07 Fixed');
      
      // Defensive check for required parameters
      if (!formData) {
        throw new Error('Form data is required for transit calculation');
      }
      
      if (!layerManager) {
        console.warn('⚠️  LayerManager is not available for transit data');
      }
      
      const transitDateTime = customDateTime || new Date();
      
      // For transits, we calculate a chart for the current/transit time at the birth location
      const transitData = {
        birth_date: transitDateTime.toISOString().split('T')[0], // Use transit date as birth_date
        birth_time: transitDateTime.toTimeString().split(' ')[0].substring(0, 5), // Use transit time as birth_time
        birth_city: formData.birth_city,
        birth_state: formData.birth_state || '',
        birth_country: formData.birth_country || '',
        timezone: formData.timezone,
        coordinates: formData.coordinates,
        house_system: formData.house_system || 'whole_sign',
        use_extended_planets: true
      };

      console.log('🔄 Fetching transit data with:', transitData);

      // Use the same endpoint as CCG (calculate chart for transit time)
      const response = await fetch('/api/calculate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(transitData)
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Transit API error: ${response.status} - ${errorText}`);
      }

      setLoadingStep('transit_astro');
      const chartData = await response.json();
      
      console.log('🎯 Transit chart data received:', {
        features: chartData.astrocartography?.features?.length || 0,
        hasAstrocartography: !!chartData.astrocartography
      });

      // Set the transit data in layer manager
      if (chartData.astrocartography && chartData.astrocartography.features) {
        // Tag all features as transit layer
        const transitAstroData = {
          ...chartData.astrocartography,
          features: chartData.astrocartography.features.map(f => ({
            ...f,
            properties: {
              ...f.properties,
              layer: 'TRANSIT'
            }
          }))
        };
        
        // Defensive check for layerManager
        if (layerManager && typeof layerManager.setLayerData === 'function') {
          layerManager.setLayerData('transit', transitAstroData);
          layerManager.setLayerVisible('transit', true);
          setIsTransitEnabled(true);
          
          // Defensive check for forceMapUpdate
          if (typeof forceMapUpdate === 'function') {
            forceMapUpdate();
          }
          
          console.log('✅ Transit layer data set and made visible');
        } else {
          console.warn('⚠️  LayerManager not available, skipping layer data set');
        }
      } else {
        console.log('❌ No transit astrocartography data received');
      }

      setLoadingStep(null);
      return chartData.astrocartography;
      
    } catch (error) {
      setLoadingStep(null);
      console.error('Transit generation failed:', error);
      throw error;
    }
  }, [layerManager, forceMapUpdate]);

  return {
    isTransitEnabled,
    fetchTransits,
    loadingStep
  };
}
