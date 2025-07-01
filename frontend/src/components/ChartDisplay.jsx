import React, { useState, useEffect } from 'react';
import './ChartDisplay.css';

const ChartDisplay = ({ chartData, currentLayer }) => {
  const [svgContent, setSvgContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [chartConfig, setChartConfig] = useState({
    width: 600,
    height: 600,
    show_aspects: true,
    show_legend: true
  });

  const layerTypes = {
    'NATAL': 'natal',
    'HD_DESIGN': 'human_design', 
    'TRANSIT': 'transit',
    'CCG': 'ccg'
  };

  const generateChart = async (layerType) => {
    if (!chartData || !chartData.planets) {
      setError('No chart data available');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`/api/chart-svg/${layerType}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          chart_data: chartData,
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
  };

  // Generate chart when chartData or currentLayer changes
  useEffect(() => {
    const layerType = layerTypes[currentLayer];
    if (layerType && chartData) {
      generateChart(layerType);
    }
  }, [chartData, currentLayer]);

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
      <div className="chart-header">
        <h3>{getLayerDisplayName(currentLayer)}</h3>
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
  );
};

export default ChartDisplay;
