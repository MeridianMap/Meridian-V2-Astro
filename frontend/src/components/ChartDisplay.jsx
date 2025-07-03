import React, { useState, useEffect, useCallback, useMemo } from 'react';
import PlanetSummaryTable from './PlanetSummaryTable';
import astroDefinitions from '../astro_definitions.json';
import './ChartDisplay.css';

// Constants for tooltip functionality
const PLANET_SYMBOLS = {
  '☉': 'Sun', '☽': 'Moon', '☿': 'Mercury', '♀': 'Venus', '♂': 'Mars',
  '♃': 'Jupiter', '♄': 'Saturn', '♅': 'Uranus', '♆': 'Neptune', '♇': 'Pluto',
  '☊': 'North Node', '☋': 'South Node', '⚷': 'Chiron'
};

const ANGLE_NAMES = {
  'AC': 'Ascendant',
  'MC': 'Midheaven',
  'DC': 'Descendant', 
  'IC': 'Imum Coeli'
};

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
    // 'TRANSIT': 'transit'  // Commented out for now
  }), []);

  // const layerEndpoints = useMemo(() => ({
  //   'NATAL': '/api/calculate',
  //   // 'TRANSIT': '/api/calculate'  // Transit charts use the same base data as natal - Commented out
  // }), []);

  const fetchLayerData = useCallback(async (layerType, layerKey) => {
    if (!chartData || !chartData.input) {
      setError('No base chart data available');
      return null;
    }

    try {
      // const endpoint = layerEndpoints[layerKey];  // Commented out since only NATAL is supported
      
      // For natal layer, use existing chartData
      if (layerKey === 'NATAL') {
        // We use the chartData prop directly as it contains the full natal chart data.
        return chartData;
      }

      // For transit layer, we need to fetch a new chart for the current time.
      // COMMENTED OUT: Transit functionality temporarily disabled
      /*
      if (layerKey === 'TRANSIT') {
        const now = new Date();
        const currentDate = now.toISOString().split('T')[0]; // YYYY-MM-DD
        const currentTime = now.toTimeString().split(' ')[0].substring(0, 5); // HH:MM
        
        // We use the location from the base natal chart, but the current time.
        // The location can be either coordinates or city/state/country.
        const requestData = {
          birth_date: currentDate,
          birth_time: currentTime,
          timezone: chartData.input.timezone, // The backend will handle the conversion to UTC
          house_system: chartData.input.house_system || 'whole_sign',
        };

        // Add location data (coordinates take precedence)
        if (chartData.coordinates && chartData.coordinates.latitude && chartData.coordinates.longitude) {
          requestData.coordinates = chartData.coordinates;
        } else {
          requestData.birth_city = chartData.input.birth_city;
          requestData.birth_state = chartData.input.birth_state;
          requestData.birth_country = chartData.input.birth_country;
        }

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

        // The result is a full chart data object for the current time.
        return result;
      }
      */

      // Fallback for any other layer types, though not currently used.
      return null;
    } catch (err) {
      console.error(`Error fetching ${layerKey} data:`, err);
      // Set a more user-friendly error message
      setError(`Failed to load ${layerKey} data. Please try again.`);
      return null; // Ensure we return null on error
    }
  }, [chartData]); // Removed layerEndpoints since only NATAL is supported

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

      // Debug logging
      console.log(`Generating ${layerKey} chart with data:`, {
        planets: chartDataForSvg.planets?.length || 0,
        houses: chartDataForSvg.houses?.length || 0,
        aspects: chartDataForSvg.aspects?.length || 0,
        show_aspects: chartConfig.show_aspects
      });

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
        // Try to get error details from response
        let errorMessage = `HTTP error! status: ${response.status}`;
        try {
          const errorData = await response.json();
          if (errorData.error) {
            errorMessage = `Server error: ${errorData.error}`;
            if (errorData.type) {
              errorMessage += ` (${errorData.type})`;
            }
          }
        } catch {
          // If we can't parse the error response, use the status text
          errorMessage = `HTTP ${response.status}: ${response.statusText}`;
        }
        throw new Error(errorMessage);
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

  // Helper functions for tooltips
  const hideCustomTooltip = useCallback(() => {
    const tooltip = document.querySelector('.chart-tooltip');
    if (tooltip) {
      tooltip.remove();
    }
  }, []);

  const showCustomTooltip = useCallback((event, text) => {
    // Remove any existing tooltip
    hideCustomTooltip();
    
    const tooltip = document.createElement('div');
    tooltip.className = 'chart-tooltip';
    tooltip.textContent = text;
    tooltip.style.cssText = `
      position: fixed;
      background: rgba(0, 0, 0, 0.9);
      color: white;
      padding: 8px 12px;
      border-radius: 6px;
      font-size: 12px;
      font-family: Arial, sans-serif;
      white-space: pre-line;
      z-index: 10000;
      pointer-events: none;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
      max-width: 200px;
      left: ${event.clientX + 15}px;
      top: ${event.clientY - 10}px;
    `;
    document.body.appendChild(tooltip);
    
    // Adjust position if tooltip would go off screen
    const rect = tooltip.getBoundingClientRect();
    if (rect.right > window.innerWidth) {
      tooltip.style.left = `${event.clientX - rect.width - 15}px`;
    }
    if (rect.bottom > window.innerHeight) {
      tooltip.style.top = `${event.clientY - rect.height - 10}px`;
    }
  }, [hideCustomTooltip]);

  const updateTooltipPosition = useCallback((event) => {
    const tooltip = document.querySelector('.chart-tooltip');
    if (tooltip) {
      tooltip.style.left = `${event.clientX + 15}px`;
      tooltip.style.top = `${event.clientY - 10}px`;
      
      // Adjust position if tooltip would go off screen
      const rect = tooltip.getBoundingClientRect();
      if (rect.right > window.innerWidth) {
        tooltip.style.left = `${event.clientX - rect.width - 15}px`;
      }
      if (rect.bottom > window.innerHeight) {
        tooltip.style.top = `${event.clientY - rect.height - 10}px`;
      }
    }
  }, []);

  // Add hover tooltip functionality
  useEffect(() => {
    if (svgContent && isExpanded) {
      const svgContainer = document.querySelector('.chart-svg-container svg');
      if (svgContainer) {
        const groups = svgContainer.querySelectorAll('g');
        
        groups.forEach((group) => {
          let tooltipText = '';
          
          // Check for planet symbols
          const symbolText = group.querySelector('text');
          if (symbolText) {
            const symbol = symbolText.textContent.trim();
            
            // Check if it's a planet symbol
            if (PLANET_SYMBOLS[symbol]) {
              tooltipText = PLANET_SYMBOLS[symbol];
              
              // Try to get additional info from nearby text elements
              const allTexts = group.querySelectorAll('text');
              if (allTexts.length > 1) {
                // Look for degree information
                for (let i = 1; i < allTexts.length; i++) {
                  const text = allTexts[i].textContent.trim();
                  if (text.includes('°')) {
                    tooltipText += `\n${text}`;
                  } else if (text.length > 2 && !PLANET_SYMBOLS[text]) {
                    // Likely a sign name
                    tooltipText += `\nin ${text}`;
                  }
                }
              }
            }
            
            // Check if it's an angle marker
            else if (ANGLE_NAMES[symbol]) {
              tooltipText = ANGLE_NAMES[symbol];
              
              // Look for degree information in nearby text
              const allTexts = group.querySelectorAll('text');
              for (let i = 1; i < allTexts.length; i++) {
                const text = allTexts[i].textContent.trim();
                if (text.includes('°')) {
                  tooltipText += `\n${text}`;
                  break;
                }
              }
            }
          }
          
          // Check for house numbers (circles with numbers)
          const circle = group.querySelector('circle');
          if (circle && symbolText && !tooltipText) {
            const text = symbolText.textContent.trim();
            if (/^\d+$/.test(text)) {
              tooltipText = `House ${text}`;
            }
          }
          
          if (tooltipText) {
            group.style.cursor = 'pointer';
            
            // Add mouse event listeners
            group.addEventListener('mouseenter', (e) => {
              showCustomTooltip(e, tooltipText);
            });
            
            group.addEventListener('mouseleave', hideCustomTooltip);
            
            group.addEventListener('mousemove', (e) => {
              updateTooltipPosition(e);
            });
          }
        });
      }
    }
    
    // Cleanup function to remove event listeners
    return () => {
      hideCustomTooltip();
    };
  }, [svgContent, isExpanded, showCustomTooltip, hideCustomTooltip, updateTooltipPosition]);

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
      // 'TRANSIT': 'Transit Chart'  // Commented out
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
