import { useState } from 'react';
import { calculateChart } from '../apiClient';

export default function useChartData(timeManager) {
  const [response, setResponse] = useState(null);
  const [loadingStep, setLoadingStep] = useState(null);
  const [error, setError] = useState(null);

  const fetchChart = async (formData) => {
    setError(null);
    setLoadingStep('ephemeris');
    try {
      // Enhanced debugging for 400 error investigation
      console.log('🚀 Calling calculateChart with detailed data:');
      console.log('📋 Form data validation:', {
        hasName: !!formData.name,
        hasBirthDate: !!formData.birth_date,
        hasBirthTime: !!formData.birth_time,
        hasBirthCity: !!formData.birth_city,
        hasBirthState: !!formData.birth_state,
        hasBirthCountry: !!formData.birth_country,
        hasTimezone: !!formData.timezone,
        hasHouseSystem: !!formData.house_system,
        formDataKeys: Object.keys(formData),
        formDataValues: formData
      });
      
      const chartResult = await calculateChart({ ...formData, use_extended_planets: true });
      
      console.log('✅ Chart result received:', {
        keys: Object.keys(chartResult),
        astrocartography_features: chartResult.astrocartography?.features?.length || 0,
        chart_data_keys: Object.keys(chartResult.chart_data || {}),
      });
      setResponse(chartResult);
      timeManager.setNatalTime && timeManager.setNatalTime({
        birth_date: formData.birth_date,
        birth_time: formData.birth_time,
        timezone: formData.timezone,
        coordinates: chartResult.coordinates
      });
      setLoadingStep('done');
      return chartResult;
    } catch (e) {
      console.error('❌ Chart request failed with detailed error:', {
        message: e.message,
        status: e.response?.status,
        statusText: e.response?.statusText,
        responseData: e.response?.data,
        requestData: formData,
        fullError: e
      });
      setError(`Chart calculation failed: ${e.response?.data?.error || e.response?.data || e.message || 'Unknown error'}`);
      setLoadingStep(null);
      return null;
    }
  };

  return { response, loadingStep, error, fetchChart, setError, setLoadingStep };
}
