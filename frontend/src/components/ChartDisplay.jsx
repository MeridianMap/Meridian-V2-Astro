import React, { useState, useEffect, useCallback, useMemo } from 'react';
import './ChartDisplay.css';

const ChartDisplay = ({ chartData, currentLayer }) => {
  const [svgContent, setSvgContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isExpanded, setIsExpanded] = useState(false); // Default to collapsed
  const [chartConfig, setChartConfig] = useState({
    width: 600,
    height: 600,
    show_aspects: true,
    show_legend: true
  });

  const layerTypes = useMemo(() => ({
    'NATAL': 'natal',
    'HD_DESIGN': 'human_design', 
    'TRANSIT': 'transit',
    'CCG': 'ccg'
  }), []);

  const generateChart = useCallback(async (layerType) => {
    if (!chartData || !chartData.planets) {
      setError('No chart data available');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Extract just the chart data (excluding astrocartography and other API-specific data)
      const chartDataForSvg = {
        planets: chartData.planets,
        houses: chartData.houses,
        aspects: chartData.aspects,
        lots: chartData.lots,
        fixed_stars: chartData.fixed_stars,
        coordinates: chartData.coordinates,
        utc_time: chartData.utc_time,
        input: chartData.input
      };

      const response = await fetch(`/api/chart-svg/${layerType}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          chart_data: chartDataForSvg,
          chart_config: chartConfig
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
  }, [chartData, chartConfig]);

  // Generate chart when chartData or currentLayer changes, but only if expanded
  useEffect(() => {
    const layerType = layerTypes[currentLayer];
    if (layerType && chartData && isExpanded) {
      generateChart(layerType);
    }
  }, [chartData, currentLayer, generateChart, layerTypes, isExpanded]);

  // Generate chart when accordion is expanded for the first time
  useEffect(() => {
    if (isExpanded && !svgContent && !loading && chartData) {
      const layerType = layerTypes[currentLayer];
      if (layerType) {
        generateChart(layerType);
      }
    }
  }, [isExpanded, svgContent, loading, chartData, currentLayer, generateChart, layerTypes]);

  const handleConfigChange = (key, value) => {
    setChartConfig(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const refreshChart = () => {
    const layerType = layerTypes[currentLayer];
    if (layerType) {
      generateChart(layerType);
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
      'HD_DESIGN': 'Human Design Chart',
      'TRANSIT': 'Transit Chart', 
      'CCG': 'Composite Chart'
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
                <label>
                  <input
                    type="checkbox"
                    checked={chartConfig.show_legend}
                    onChange={(e) => handleConfigChange('show_legend', e.target.checked)}
                  />
                  Show Legend
                </label>
                <select
                  value={`${chartConfig.width}x${chartConfig.height}`}
                  onChange={(e) => {
                    const [width, height] = e.target.value.split('x').map(Number);
                    setChartConfig(prev => ({ ...prev, width, height }));
                  }}
                >
                  <option value="400x400">Small (400×400)</option>
                  <option value="600x600">Medium (600×600)</option>
                  <option value="800x800">Large (800×800)</option>
                </select>
              </div>
              <div className="chart-actions">
                <button onClick={refreshChart} disabled={loading}>
                  {loading ? 'Generating...' : 'Refresh Chart'}
                </button>
                <button onClick={downloadSvg} disabled={!svgContent || loading}>
                  Download SVG
                </button>
              </div>
            </div>
          </div>

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

            {svgContent && !loading && !error && (
              <div className="chart-svg-container">
                <div 
                  className="chart-svg"
                  dangerouslySetInnerHTML={{ __html: svgContent }}
                />
              </div>
            )}

            {!svgContent && !loading && !error && (
              <div className="chart-placeholder">
                <p>Select chart data to generate {getLayerDisplayName(currentLayer)}</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChartDisplay;
