import React, { useState, useEffect, useCallback, useMemo } from 'react';
import PlanetSummaryTable from './PlanetSummaryTable';
import astroDefinitions from '../astro_definitions.json';
import './ChartDisplay.css';

const ChartDisplay = ({ chartData, currentLayer }) => {
  const [svgContent, setSvgContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isExpanded, setIsExpanded] = useState(false); // Default to collapsed
  const [layerData, setLayerData] = useState({}); // Cache data for each layer
  const [chartConfig, setChartConfig] = useState({
    width: 600,
    height: 600,
    show_aspects: true,
    show_legend: true
  });

  const summaryData = useMemo(() => {
    if (!layerData[currentLayer] || !layerData[currentLayer].planets) {
      return [];
    }
    return layerData[currentLayer].planets.map(p => ({
      planet: p.name,
      sign: p.sign,
      house: p.house,
      houseDefinition: astroDefinitions.houses[p.house] || ''
    }));
  }, [layerData, currentLayer]);

  const layerTypes = useMemo(() => ({
    'NATAL': 'natal',
    'TRANSIT': 'transit'
  }), []);

  const layerEndpoints = useMemo(() => ({
    'NATAL': '/api/calculate',
    'TRANSIT': '/api/calculate'  // Transit charts use the same base data as natal
  }), []);

  const fetchLayerData = useCallback(async (layerType, layerKey) => {
    if (!chartData || !chartData.input) {
      setError('No base chart data available');
      return null;
    }

    try {
      const endpoint = layerEndpoints[layerKey];
      
      // For natal layer, use existing chartData
      if (layerKey === 'NATAL') {
        return chartData;
      }

      // For transit layer, calculate current planetary positions
      if (layerKey === 'TRANSIT') {
        const now = new Date();
        const currentDate = now.toISOString().split('T')[0]; // YYYY-MM-DD
        const currentTime = now.toTimeString().split(' ')[0].substring(0, 5); // HH:MM
        
        const requestData = {
          birth_date: currentDate,  // Use current date instead of birth date
          birth_time: currentTime,  // Use current time instead of birth time
          birth_city: chartData.input.birth_city,
          birth_state: chartData.input.birth_state,
          birth_country: chartData.input.birth_country,
          timezone: chartData.input.timezone,
          coordinates: chartData.coordinates,
          house_system: chartData.input.house_system || 'whole_sign',
          progressed_for: null,  // This tells the backend to calculate transit positions
          progression_method: null
        };

        const response = await fetch(endpoint, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(requestData)
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        
        if (result.error) {
          throw new Error(result.error);
        }

        return result;
      }

      // For other layers, fetch from specific endpoints
      const requestData = {
        birth_date: chartData.input.birth_date,
        birth_time: chartData.input.birth_time,
        birth_city: chartData.input.birth_city,
        birth_state: chartData.input.birth_state,
        birth_country: chartData.input.birth_country,
        timezone: chartData.input.timezone,
        coordinates: chartData.coordinates,
        house_system: chartData.input.house_system || 'whole_sign'
      };

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      if (result.error) {
        throw new Error(result.error);
      }

      return result;
    } catch (err) {
      console.error(`Error fetching ${layerKey} data:`, err);
      throw err;
    }
  }, [chartData, layerEndpoints]);

  const generateChart = useCallback(async (layerType, layerKey) => {
    setLoading(true);
    setError(null);

    try {
      // Check if we already have data for this layer
      let currentLayerData = layerData[layerKey];
      
      if (!currentLayerData) {
        // Fetch data for this layer
        currentLayerData = await fetchLayerData(layerType, layerKey);
        if (!currentLayerData) return;
        
        // Cache the data
        setLayerData(prev => ({
          ...prev,
          [layerKey]: currentLayerData
        }));
      }

      // Extract chart data for SVG generation
      const chartDataForSvg = {
        planets: currentLayerData.planets,
        houses: currentLayerData.houses,
        aspects: currentLayerData.aspects,
        lots: currentLayerData.lots,
        fixed_stars: currentLayerData.fixed_stars,
        coordinates: currentLayerData.coordinates,
        utc_time: currentLayerData.utc_time,
        input: currentLayerData.input,
        chart_type: currentLayerData.chart_type
      };

      const response = await fetch(`/api/chart-svg/${layerType}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          chart_data: chartDataForSvg,
          chart_config: { ...chartConfig, show_legend: false } // Always disable SVG legend
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      if (result.error) {
        throw new Error(result.error);
      }

      setSvgContent(result.svg);
    } catch (err) {
      console.error('Chart generation error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [layerData, chartConfig, fetchLayerData]);

  // Generate chart when chartData or currentLayer changes, but only if expanded
  useEffect(() => {
    const layerType = layerTypes[currentLayer];
    if (layerType && chartData && isExpanded) {
      generateChart(layerType, currentLayer);
    }
  }, [chartData, currentLayer, generateChart, layerTypes, isExpanded]);

  // Generate chart when accordion is expanded for the first time
  useEffect(() => {
    if (isExpanded && !svgContent && !loading && chartData) {
      const layerType = layerTypes[currentLayer];
      if (layerType) {
        generateChart(layerType, currentLayer);
      }
    }
  }, [isExpanded, svgContent, loading, chartData, currentLayer, generateChart, layerTypes]);

  // Clear SVG content when layer changes to force regeneration
  useEffect(() => {
    setSvgContent('');
    setError(null);
  }, [currentLayer]);

  const handleConfigChange = (key, value) => {
    setChartConfig(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const refreshChart = () => {
    const layerType = layerTypes[currentLayer];
    if (layerType) {
      // Clear cached data for this layer to force refresh
      setLayerData(prev => {
        const updated = { ...prev };
        delete updated[currentLayer];
        return updated;
      });
      setSvgContent('');
      // Add a small delay to ensure state is cleared
      setTimeout(() => {
        generateChart(layerType, currentLayer);
      }, 100);
    }
  };

  const downloadSvg = () => {
    if (!svgContent) return;
    
    const blob = new Blob([svgContent], { type: 'image/svg+xml' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${currentLayer.toLowerCase()}_chart.svg`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const getLayerDisplayName = (layer) => {
    const names = {
      'NATAL': 'Natal Chart',
      'TRANSIT': 'Transit Chart'
    };
    return names[layer] || layer;
  };

  return (
    <div className="chart-display">
      <div className="chart-accordion">
        <div 
          className={`chart-accordion-header ${isExpanded ? 'expanded' : 'collapsed'}`}
          onClick={() => setIsExpanded(!isExpanded)}
        >
          <div className="chart-accordion-title">
            <span className="chart-accordion-icon">
              {isExpanded ? '📊' : '📈'}
            </span>
            <h3>SVG Chart Viewer - {getLayerDisplayName(currentLayer)}</h3>
            <span className="chart-accordion-toggle">
              {isExpanded ? '▼' : '▶'}
            </span>
          </div>
          {!isExpanded && (
            <div className="chart-accordion-preview">
              <span className="chart-preview-text">
                Click to view interactive {getLayerDisplayName(currentLayer)} • 
                {svgContent ? ' Chart ready' : ' Generate chart'} • 
                Hover planets for tooltips
              </span>
            </div>
          )}
        </div>

        <div className={`chart-accordion-content ${isExpanded ? 'expanded' : 'collapsed'}`}>
          <div className="chart-header">
            <div className="chart-controls">
              <div className="chart-config">
                <label>
                  <input
                    type="checkbox"
                    checked={chartConfig.show_aspects}
                    onChange={(e) => handleConfigChange('show_aspects', e.target.checked)}
                  />
                  Show Aspects
                </label>
                <select
                  value={chartConfig.width}
                  onChange={(e) => handleConfigChange('width', Number(e.target.value))}
                >
                  <option value={400}>Small (400)</option>
                  <option value={600}>Medium (600)</option>
                  <option value={800}>Large (800)</option>
                </select>
              </div>
              <div className="chart-actions">
                <button onClick={refreshChart} disabled={loading}>Refresh Chart</button>
                <button onClick={downloadSvg} disabled={!svgContent || loading}>Download SVG</button>
              </div>
            </div>
          </div>
          <div className="chart-content-area">
            <div className="chart-content">
              {loading && (
                <div className="chart-loading">
                  <div className="spinner"></div>
                  <p>Generating {getLayerDisplayName(currentLayer)}...</p>
                </div>
              )}

              {error && (
                <div className="chart-error">
                  <h4>Chart Generation Error</h4>
                  <p>{error}</p>
                  <button onClick={refreshChart}>Try Again</button>
                </div>
              )}
              {!loading && !error && svgContent && (
                <div className="chart-svg-container" dangerouslySetInnerHTML={{ __html: svgContent }} />
              )}
              {!loading && !error && !svgContent && (
                <div className="chart-placeholder">
                  <p>Select a chart type and options to begin.</p>
                </div>
              )}
            </div>
            {chartConfig.show_legend && summaryData.length > 0 && (
              <div className="planet-summary-container">
                <PlanetSummaryTable summaryData={summaryData} />
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChartDisplay;
