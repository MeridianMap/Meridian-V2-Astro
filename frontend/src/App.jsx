import React, { useState, useEffect } from 'react';
import './App.css'
import AstroMap from './Astromap';
import LayerManager from './utils/LayerManager';
import TimeManager from './utils/TimeManager';
import ChartHeader from './components/ChartHeader';
import CCGDateControls from './components/CCGDateControls';
import ChartForm from './components/ChartForm';
import ChartDisplay from './components/ChartDisplay';
import DemoCharts from './components/DemoCharts';
import NatalDisplayControls from './components/NatalDisplayControls';
import TransitControls from './components/TransitControls';
import CCGControls from './components/CCGControls';
import useChartData from './hooks/useChartData';
import useAstroData from './hooks/useAstroData';
import useTransitData from './hooks/useTransitData';
import useCCGData from './hooks/useCCGData';

const GEOAPIFY_API_KEY = import.meta.env.VITE_GEOAPIFY_API_KEY
const TIMEZONEDB_API_KEY = 'YHIFBIVJIA14'
const ACCESS_PASSWORD = import.meta.env.VITE_ACCESS_PASSWORD || 'explore'
const REQUIRE_AUTH = import.meta.env.VITE_REQUIRE_AUTH === 'true'

function App() {
  // Authentication state (always at top level)
  const [isAuthenticated, setIsAuthenticated] = useState(!REQUIRE_AUTH);
  const [passwordInput, setPasswordInput] = useState('');
  const [authError, setAuthError] = useState('');

  // Check for stored auth on component mount
  useEffect(() => {
    if (REQUIRE_AUTH) {
      const storedAuth = sessionStorage.getItem('meridian_auth');
      if (storedAuth === 'authenticated') {
        setIsAuthenticated(true);
      }
    }
  }, []);

  // Password submit handler
  const handlePasswordSubmit = (e) => {
    e.preventDefault();
    if (passwordInput === ACCESS_PASSWORD) {
      setIsAuthenticated(true);
      sessionStorage.setItem('meridian_auth', 'authenticated');
      setAuthError('');
    } else {
      setAuthError('Incorrect password. Please try again.');
      setPasswordInput('');
    }
  };

  // Logout handler
  const handleLogout = () => {
    sessionStorage.removeItem('meridian_auth');
    setIsAuthenticated(false);
    setPasswordInput('');
    setAuthError('');
  };

  // Force re-render trigger for map updates
  const [mapUpdateTrigger, setMapUpdateTrigger] = useState(0);
  const forceMapUpdate = React.useCallback(() => {
    setMapUpdateTrigger(prev => prev + 1);
  }, []);

  // Initialize managers
  const [layerManager] = useState(() => new LayerManager());
  const [timeManager] = useState(() => new TimeManager());
  
  // Chart display state
  const [currentChartLayer, setCurrentChartLayer] = useState('NATAL');
  
    const [formData, setFormData] = useState({
    name: '',
    birth_date: '',
    birth_time: '',
    birth_city: '',
    birth_state: '',
    birth_country: '',
    timezone: '',
    house_system: 'whole_sign' // Default house system
  })  // Replace chart, astro, transit, and CCG state/handlers with hooks
  const { response, loadingStep: chartLoading, error, fetchChart, setError } = useChartData(timeManager);
  const { astroData, setAstroData } = useAstroData(layerManager, forceMapUpdate);
  const { isTransitEnabled, fetchTransits, loadingStep: transitLoading } = useTransitData(layerManager, forceMapUpdate);
  const { fetchCCG, loadingStep: ccgLoading } = useCCGData(layerManager, forceMapUpdate);

  // Enhanced progress tracking with detailed steps
  const [overallProgress, setOverallProgress] = useState({
    step: null,
    percentage: 0,
    message: '',
    layerStatuses: {
      natal: { status: 'pending', progress: 0, message: '' },
      transit: { status: 'pending', progress: 0, message: '' },
      ccg: { status: 'pending', progress: 0, message: '' }
    }
  });

  // Helper function xto update individual layer progress
  const updateLayerProgress = (layerName, status, progress, message) => {
    setOverallProgress(prev => ({
      ...prev,
      layerStatuses: {
        ...prev.layerStatuses,
        [layerName]: { status, progress, message }
      }
    }));
  };

  // Helper function to calculate overall progress from layer statuses
  const calculateOverallProgress = (layerStatuses) => {
    const layers = Object.values(layerStatuses);
    const totalProgress = layers.reduce((sum, layer) => sum + layer.progress, 0);
    const averageProgress = totalProgress / layers.length;
    const completedLayers = layers.filter(layer => layer.status === 'completed').length;
    const failedLayers = layers.filter(layer => layer.status === 'failed').length;
    
    return {
      percentage: Math.round(averageProgress),
      completedLayers,
      failedLayers,
      totalLayers: layers.length
    };
  };

  // Combine all loading states for display
  const activeLoadingStep = overallProgress.step || chartLoading || transitLoading || ccgLoading;
  const loadingStep = activeLoadingStep;
  // Initialize layers
  React.useEffect(() => {
    // Set up natal layer
    layerManager.addLayer('natal', {
      visible: true,
      order: 0,
      type: 'natal',
      style: {
        color: 'inherit', // Use existing planet colors
        width: 2,
        opacity: 1.0
      }
    });

    // Set up transit layer with unique colors 
    layerManager.addLayer('transit', {
      visible: false,
      order: 1,
      type: 'transit',
      style: {
        color: '#ff6600', // Bright orange
        width: 3,         // Slightly wider than natal
        opacity: 0.9      // Good visibility
      },
      subLayers: {
        ac_dc: true,
        ic_mc: true,
        parans: true
      }
    });

    // Register CCG layer (with hermetic lots toggle)
    layerManager.addLayer('CCG', {
      visible: false,
      order: 1.5,
      type: 'overlay',
      style: { color: '#4A90E2', width: 3, opacity: 0.8 },
      subLayers: { ac_dc: true, ic_mc: true, parans: true, lots: true }
    });

    // Listen for layer changes
    const unsubscribe = layerManager.addListener((event) => {
      if (event === 'layerToggled' || event === 'subLayerToggled') {
        // Force re-render when layers change
        forceMapUpdate();
      }
    });

    return unsubscribe;
  }, [layerManager, forceMapUpdate]);

  // Current transit date/time state
  const [currentTransitDateTime, setCurrentTransitDateTime] = useState(new Date());

  // Update handleGenerateTransits to use fetchTransits
  const handleGenerateTransits = async (customDateTime = null) => {
    try {
      console.log('handleGenerateTransits called with:', customDateTime);
      console.log('formData:', formData);
      console.log('currentTransitDateTime:', currentTransitDateTime);
      await fetchTransits(formData, customDateTime || currentTransitDateTime);
      console.log('fetchTransits completed');
    } catch (error) {
      console.error('Error in handleGenerateTransits:', error);
    }
  };

  // CCG date state (default to today)
  const [ccgDate, setCCGDate] = useState(() => {
    const today = new Date();
    return today.toISOString().slice(0, 10);
  });

  // UI toggles for JSON display
  const [showJson, setShowJson] = useState(false);
  const [showAstroJson, setShowAstroJson] = useState(false);
  const [showGptJson, setShowGptJson] = useState(false);
  const [gptData, setGptData] = useState(null);
  // Progress/animation indicator
  // Natal/planet toggles
  const [lineToggles, setLineToggles] = useState({
    planet: true,
    mc_aspects: true,
    ac_aspects: true,
    fixed_star: true,
    hermetic_lot: true,
    parans: true,
    ic_mc: true,
    ac_dc: true
  });
  // CCG toggles (mirrors natal toggles)
  const [ccgLineToggles, setCCGLineToggles] = useState({
    planet: true,
    mc_aspects: true,
    ac_aspects: true,
    fixed_star: false,
    hermetic_lot: true,
    parans: true,
    ic_mc: true,
    ac_dc: true
  });

  const allBodies = [
    "Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto", "Lunar Node",
    "Chiron", "Ceres", "Pallas", "Juno", "Vesta", "Black Moon Lilith", "Pholus"
  ];
  const ccgBodies = [
    "Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto",
    "Chiron", "Ceres", "Pallas", "Juno", "Vesta", "Black Moon Lilith", "Pholus"
  ];
  const [bodyToggles, setBodyToggles] = useState(
    Object.fromEntries(allBodies.map(name => [name, true]))
  );
  const [ccgBodyToggles, setCCGBodyToggles] = useState(
    Object.fromEntries(ccgBodies.map(name => [name, true]))
  );
  const [showBodyAccordion, setShowBodyAccordion] = useState(true);
  const [ccgShowBodyAccordion, setCCGShowBodyAccordion] = useState(true);
  const [transitShowBodyAccordion, setTransitShowBodyAccordion] = useState(true);

  // Transit toggles (similar to CCG but separate)
  const [transitLineToggles, setTransitLineToggles] = useState({
    planet: true,
    mc_aspects: true,
    ac_aspects: true,
    hermetic_lot: true,
    parans: true,
    ic_mc: true,
    ac_dc: true
  });
  // Transit bodies (all bodies like natal)
  const transitBodies = allBodies;
  const [transitBodyToggles, setTransitBodyToggles] = useState(
    Object.fromEntries(transitBodies.map(name => [name, true]))
  );

  // Line labels
  const lineLabels = {
    planet: 'Planet Lines',
    mc_aspects: 'MC Aspects',
    ac_aspects: 'AC Aspects',
    fixed_star: 'Fixed Stars',
    hermetic_lot: 'Hermetic Lots',
    parans: 'Parans',  };
  
  // Consolidated chart generation handler with enhanced progress tracking
  const handleConsolidatedGeneration = async (formData) => {
    const errors = [];
    
    try {
      // Reset all layer statuses
      setOverallProgress({
        step: 'starting',
        percentage: 0,
        message: 'Initializing chart generation...',
        layerStatuses: {
          natal: { status: 'pending', progress: 0, message: 'Waiting to start...' },
          transit: { status: 'pending', progress: 0, message: 'Waiting to start...' },
          ccg: { status: 'pending', progress: 0, message: 'Waiting to start...' }
        }
      });

      // Step 1: Generate Natal Chart (Priority: First, 0-25%)
      updateLayerProgress('natal', 'processing', 10, 'Calculating ephemeris...');
      setOverallProgress(prev => ({ ...prev, step: 'natal_ephemeris', percentage: 5, message: 'Step 1/4: Calculating natal ephemeris...' }));
      
      const chartData = await fetchChart(formData);
      
      if (chartData) {
        updateLayerProgress('natal', 'processing', 80, 'Processing astrocartography...');
        setOverallProgress(prev => ({ ...prev, step: 'natal_astro', percentage: 15, message: 'Step 1/4: Processing natal astrocartography...' }));
        
        if (chartData.astrocartography) {
          console.log('🎯 Setting natal astrocartography data:', {
            features: chartData.astrocartography.features?.length || 0,
            dataKeys: Object.keys(chartData.astrocartography)
          });
          
          setAstroData(chartData.astrocartography);
          layerManager.setLayerData('natal', chartData.astrocartography);
          updateLayerProgress('natal', 'completed', 100, 'Natal chart complete!');
          forceMapUpdate();
        } else {
          updateLayerProgress('natal', 'failed', 0, 'No astrocartography data');
          errors.push('Natal chart: No astrocartography data');
        }
      } else {
        updateLayerProgress('natal', 'failed', 0, 'Chart generation failed');
        errors.push('Natal chart generation failed');
      }
      
      setOverallProgress(prev => ({ ...prev, percentage: 25, message: 'Step 1/4: Natal chart complete! Starting other layers...' }));

      // Steps 2-4: Generate all other layers in parallel for maximum efficiency
      const layerPromises = [];
      
      // Step 2: Transit Layer (25% - 45%)
      updateLayerProgress('transit', 'processing', 20, 'Calculating transit ephemeris...');
      layerPromises.push(
        fetchTransits(formData, new Date()).then(() => {
          updateLayerProgress('transit', 'completed', 100, 'Transit layer complete!');
          console.log('✅ Transit layer completed successfully');
        }).catch(error => {
          console.error('❌ Transit generation failed:', error);
          updateLayerProgress('transit', 'failed', 0, `Failed: ${error.message}`);
          errors.push('Transit layer generation failed');
        })
      );
      
      // Step 3: CCG Layer (50% - 70%)
      updateLayerProgress('ccg', 'processing', 20, 'Calculating CCG ephemeris...');
      layerPromises.push(
        fetchCCG(formData, ccgDate, ccgLineToggles).then(() => {
          updateLayerProgress('ccg', 'completed', 100, 'CCG layer complete!');
          console.log('✅ CCG layer completed successfully');
        }).catch(error => {
          console.error('❌ CCG generation failed:', error);
          updateLayerProgress('ccg', 'failed', 0, `Failed: ${error.message}`);
          errors.push('CCG layer generation failed');
        })
      );
      
      // Update progress as layers are processing
      setOverallProgress(prev => ({ ...prev, step: 'parallel_layers', percentage: 30, message: 'Steps 2-4: Generating Transit and CCG layers in parallel...' }));
      
      // Monitor progress while waiting for parallel operations
      const progressInterval = setInterval(() => {
        setOverallProgress(prev => {
          const progress = calculateOverallProgress(prev.layerStatuses);
          return {
            ...prev,
            percentage: Math.max(25, progress.percentage), // Ensure we're at least 25% after natal
            message: `Processing ${progress.totalLayers - progress.completedLayers - progress.failedLayers} layers... (${progress.completedLayers}/${progress.totalLayers} complete)`
          };
        });
      }, 500);
      
      // Wait for all parallel operations to complete
      await Promise.allSettled(layerPromises);
      clearInterval(progressInterval);
      
      // Step 5: Finalize (100%)
      setOverallProgress(prev => {
        const progress = calculateOverallProgress(prev.layerStatuses);
        return {
          ...prev,
          step: 'finalizing',
          percentage: 95,
          message: `Step 5/5: Finalizing... (${progress.completedLayers}/${progress.totalLayers} layers successful)`
        };
      });
      
      // Ensure only natal lines are visible by default
      layerManager.setLayerVisible('natal', true);
      layerManager.setLayerVisible('transit', false);
      layerManager.setLayerVisible('CCG', true);
      
      forceMapUpdate();
      
      // Calculate final results
      const finalProgress = calculateOverallProgress(overallProgress.layerStatuses);
      let completionMessage = `Chart generation complete! ✅ ${finalProgress.completedLayers}/${finalProgress.totalLayers} layers successful`;
      if (errors.length > 0) {
        completionMessage += ` ❌ ${finalProgress.failedLayers} failed: ${errors.join(', ')}`;
      }
      
      setOverallProgress(prev => ({ ...prev, step: 'complete', percentage: 100, message: completionMessage }));
      
      // Clear progress after delay
      setTimeout(() => {
        setOverallProgress({
          step: null,
          percentage: 0,
          message: '',
          layerStatuses: {
            natal: { status: 'pending', progress: 0, message: '' },
            transit: { status: 'pending', progress: 0, message: '' },
            ccg: { status: 'pending', progress: 0, message: '' }
          }
        });
      }, 4000);
      
    } catch (error) {
      setOverallProgress({
        step: null,
        percentage: 0,
        message: '',
        layerStatuses: {
          natal: { status: 'pending', progress: 0, message: '' },
          transit: { status: 'pending', progress: 0, message: '' },
          ccg: { status: 'pending', progress: 0, message: '' }
        }
      });
      console.error('Consolidated chart generation failed:', error);
      setError('Chart generation failed. Please try again.');
    }
  };

  // Form submit handler - now calls consolidated generation
  const handleSubmit = async (e) => {
    e.preventDefault();
    await handleConsolidatedGeneration(formData);
  };  // Restore handleGenerateCCG for CCGControls
  const handleGenerateCCG = async () => {
    try {
      setOverallProgress({ step: 'ccg_ephemeris', percentage: 25, message: 'Calculating CCG ephemeris...' });
      await fetchCCG(formData, ccgDate, ccgLineToggles);
      setOverallProgress({ step: 'ccg_complete', percentage: 100, message: 'CCG overlay generated!' });
      forceMapUpdate(); // Ensure map updates immediately after CCG overlay is generated
      
      // Clear progress after delay
      setTimeout(() => {
        setOverallProgress({ step: null, percentage: 0, message: '' });
      }, 2000);
    } catch (error) {
      setOverallProgress({ step: null, percentage: 0, message: '' });
      console.error('CCG generation failed:', error);
    }
  };

  // Demo chart handler - now uses consolidated generation
  const handleDemoChart = async (demoData) => {
    console.log('Loading demo chart:', demoData);
    
    // Update form data with demo values
    setFormData(demoData);

    // Generate all layers using consolidated generation
    await handleConsolidatedGeneration(demoData);
  };

  // Highlight summary state (for GPT integration)
  const [highlightSummary, setHighlightSummary] = useState(null);

  // Handle GPT format generation
  const handleGptFormat = async () => {
    // Check if we have the required form data
    if (!formData.birth_date || !formData.birth_time || !formData.birth_city) {
      alert('Please fill out the birth information first and generate a chart before using GPT format.');
      return;
    }

    if (showGptJson) {
      // If already showing, just hide it
      setShowGptJson(false);
      return;
    }

    try {
      console.log('Sending GPT format request with data:', formData);
      // Call the GPT comprehensive endpoint
      const gptResponse = await fetch('/api/gpt/comprehensive', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          birth_date: formData.birth_date,
          birth_time: formData.birth_time,
          birth_city: formData.birth_city,
          birth_state: formData.birth_state,
          birth_country: formData.birth_country,
          timezone: formData.timezone,
          house_system: formData.house_system || 'whole_sign',
          coordinates: formData.coordinates,
          astrocartography_summary: highlightSummary // <-- pass highlight summary if present
        })
      });

      if (!gptResponse.ok) {
        const errorText = await gptResponse.text();
        throw new Error(`GPT formatting failed: ${gptResponse.status} - ${errorText}`);
      }

      const gptResult = await gptResponse.json();
      console.log('GPT formatted data:', gptResult);
      
      setGptData(gptResult);
      setShowGptJson(true);
      
    } catch (error) {
      console.error('Error formatting for GPT:', error);
      alert(`Failed to format data for GPT: ${error.message}`);
    }
  };

  // Merged/filtered data for map
  const mergedFilteredData = React.useMemo(() => {
    let features = [];
    // Natal layer
    if (astroData && layerManager.isLayerVisible('natal')) {
      let natalFeatures = astroData.features || [];
      natalFeatures = natalFeatures.filter(f => {
        // FIRST: Exclude any features tagged as CCG
        if (f.properties?.layer === 'CCG') return false;
        
        const cat = f.properties?.category;
        const lineType = f.properties?.line_type;
        const aspectTo = f.properties?.to;
        // Parans toggle
        if (cat === 'parans' && !lineToggles.parans) return false;
        if (cat === 'fixed_star' && !lineToggles.fixed_star) return false;
        
        // Handle hermetic lots first - they have their own toggle and should NOT be affected by IC/MC toggle
        if (cat === 'hermetic_lot' || cat === 'lot' || f.properties?.body_type === 'lot') {
          return lineToggles.hermetic_lot; // Only check hermetic lot toggle, ignore IC/MC toggle
        }
        
        // Aspect handling
        if (cat === 'aspect') {
          if (aspectTo === 'MC' || lineType === 'MC' || lineType === 'IC') {
            if (!lineToggles.mc_aspects) return false;
          } else if (aspectTo === 'ASC' || lineType === 'ASC' || lineType === 'DSC' || lineType === 'HORIZON') {
            if (!lineToggles.ac_aspects) return false;
          } else {
            if (!lineToggles.mc_aspects && !lineToggles.ac_aspects) return false;
          }
        }
        // IC/MC line toggle
        if (lineType === 'IC' || lineType === 'MC') {
          if (!lineToggles.ic_mc) return false;
        }
        // AC/DC line toggle
        if (lineType === 'AC' || lineType === 'DC' || lineType === 'HORIZON') {
          if (!lineToggles.ac_dc) return false;
        }
        // Other categories
        if (cat in lineToggles && !lineToggles[cat]) return false;
        // Planet/body filtering
        let body = f.properties?.planet || f.properties?.body || f.properties?.name;
        if (body === 'Pallas Athena') body = 'Pallas';
        if (body === 'Lilith' || body === 'BML' || body === 'Black Moon') body = 'Black Moon Lilith';
        if (body === 'North Node' || body === 'NN' || body === 'Rahu') body = 'Lunar Node';
        if (body && bodyToggles[body] === false) return false;
        return true;
      });
      features = features.concat(natalFeatures.map(f => ({ ...f, layerName: 'natal' })));
    }
    // CCG overlay - simplified filtering using unified controls
    const ccgLayer = layerManager.getLayer('CCG');
    if (layerManager.isLayerVisible('CCG') && ccgLayer && ccgLayer.data && ccgLayer.data.features) {
      let ccgFeatures = ccgLayer.data.features;
      ccgFeatures = ccgFeatures.filter(f => {
        // CCG Feature Type Filtering
        if (f.properties?.category === 'parans' && !ccgLineToggles.parans) return false;
        if (f.properties?.category === 'fixed_star' && !ccgLineToggles.fixed_star) return false;
        
        // Handle hermetic lots first - they have their own toggle and should NOT be affected by IC/MC toggle
        if (f.properties?.category === 'hermetic_lot' || f.properties?.category === 'lot' || f.properties?.body_type === 'lot') {
          return ccgLineToggles.hermetic_lot; // Only check hermetic lot toggle, ignore IC/MC toggle
        }
        
        // CCG Body Filtering (extract body name first)
        let body = f.properties?.planet || f.properties?.body || f.properties?.name;
        // Remove " CCG" suffix if present in the name
        if (body && body.endsWith(' CCG')) {
          body = body.replace(' CCG', '');
        }
        if (body === 'Pallas Athena') body = 'Pallas';
        if (body === 'Lilith' || body === 'BML' || body === 'Black Moon') body = 'Black Moon Lilith';
        if (body === 'North Node' || body === 'NN' || body === 'Rahu') body = 'Lunar Node';
        
        // For planet lines (IC/MC/AC/DC), check both line type AND body toggles
        if (f.properties?.line_type === 'IC' || f.properties?.line_type === 'MC') {
          if (!ccgLineToggles.ic_mc) return false; // Line type disabled
          if (body && ccgBodyToggles[body] === false) return false; // Body disabled
        } else if (f.properties?.line_type === 'AC' || f.properties?.line_type === 'DC' || f.properties?.line_type === 'HORIZON') {
          if (!ccgLineToggles.ac_dc) return false; // Line type disabled  
          if (body && ccgBodyToggles[body] === false) return false; // Body disabled
        } else {
          // For other features (parans, etc.), check body if it exists
          if (body && ccgBodyToggles[body] === false) return false;
        }
        
        return true;
      });
      features = features.concat(ccgFeatures.map(f => ({ ...f, layerName: 'CCG' })));
    }

    // Transit Overlay
    if (layerManager.isLayerVisible('transit')) {
      const transitData = layerManager.getLayer('transit')?.data;
      let transitFeatures = transitData?.features || [];
      
      transitFeatures = transitFeatures.filter(f => {
        try {
          // Defensive null checks
          if (!f || !f.properties) return false;
          
          const cat = f.properties?.category;
          const lineType = f.properties?.line_type;
          
          // Transit Feature Type Filtering
          if (cat === 'parans' && !transitLineToggles.parans) return false;
          
          // Handle hermetic lots first - they have their own toggle and should NOT be affected by IC/MC toggle
          if (cat === 'hermetic_lot' || cat === 'lot' || f.properties?.body_type === 'lot') {
            return transitLineToggles.hermetic_lot; // Only check hermetic lot toggle, ignore IC/MC toggle
          }
          
          // Transit Body Filtering (extract body name first)
          let body = f.properties?.planet || f.properties?.body || f.properties?.name;
          // Remove " Transit" suffix if present in the name
          if (body && body.endsWith && body.endsWith(' Transit')) {
            body = body.replace(' Transit', '');
          }
          if (body === 'Pallas Athena') body = 'Pallas';
          if (body === 'Lilith' || body === 'BML' || body === 'Black Moon') body = 'Black Moon Lilith';
          if (body === 'North Node' || body === 'NN' || body === 'Rahu') body = 'Lunar Node';
          
          // For planet lines (IC/MC/AC/DC), check both line type AND body toggles
          if (lineType === 'IC' || lineType === 'MC') {
            if (!transitLineToggles.ic_mc) return false; // Line type disabled
            if (body && transitBodyToggles[body] === false) return false; // Body disabled
          } else if (lineType === 'AC' || lineType === 'DC' || lineType === 'HORIZON') {
            if (!transitLineToggles.ac_dc) return false; // Line type disabled  
            if (body && transitBodyToggles[body] === false) return false; // Body disabled
          } else {
            // For other features (parans, etc.), check body if it exists
            if (body && transitBodyToggles[body] === false) return false;
          }
          
          return true;
        } catch (err) {
          console.error('Error filtering transit feature:', err, f);
          return false; // Filter out problematic features
        }
      });
      features = features.concat(transitFeatures.map(f => ({ ...f, layerName: 'transit' })));
    }

    console.log('[DEBUG] Total merged features:', features.length);
    return { features };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [astroData, lineToggles, bodyToggles, ccgLineToggles, ccgBodyToggles, transitLineToggles, transitBodyToggles, layerManager, mapUpdateTrigger]);

  // Show password prompt if not authenticated
  if (!isAuthenticated) {
    return (
      <div className="auth-container" style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        padding: '2rem',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
      }}>
        <div style={{
          background: 'white',
          padding: '2rem',
          borderRadius: '10px',
          boxShadow: '0 10px 25px rgba(0,0,0,0.2)',
          maxWidth: '400px',
          width: '100%'
        }}>
          <h1 style={{ 
            textAlign: 'center', 
            marginBottom: '1.5rem', 
            color: '#333',
            fontSize: '2rem'
          }}>
            🌟 Meridian V2.1
          </h1>
          <p style={{ 
            textAlign: 'center', 
            color: '#666', 
            marginBottom: '1.5rem',
            fontSize: '1rem'
          }}>
            Enter the access password to continue
          </p>
          <form onSubmit={handlePasswordSubmit}>
            <input
              type="password"
              value={passwordInput}
              onChange={(e) => setPasswordInput(e.target.value)}
              placeholder="Enter password"
              style={{
                width: '100%',
                padding: '12px',
                border: '2px solid #ddd',
                borderRadius: '5px',
                fontSize: '16px',
                marginBottom: '1rem',
                boxSizing: 'border-box'
              }}
              autoFocus
            />
            <button
              type="submit"
              style={{
                width: '100%',
                padding: '12px',
                background: '#667eea',
                color: 'white',
                border: 'none',
                borderRadius: '5px',
                fontSize: '16px',
                cursor: 'pointer',
                transition: 'background 0.3s'
              }}
              onMouseOver={(e) => e.target.style.background = '#5a6fd8'}
              onMouseOut={(e) => e.target.style.background = '#667eea'}
            >
              Access Application
            </button>
          </form>
          {authError && (
            <p style={{ 
              color: '#e74c3c', 
              textAlign: 'center', 
              marginTop: '1rem',
              fontSize: '0.9rem'
            }}>
              {authError}
            </p>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      {/* Logout button for authenticated users */}
      {REQUIRE_AUTH && (
        <div style={{ textAlign: 'right', padding: '0.5rem 1rem', borderBottom: '1px solid #eee' }}>
          <button 
            onClick={handleLogout}
            style={{
              padding: '6px 12px',
              background: '#e74c3c',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              fontSize: '12px',
              cursor: 'pointer'
            }}
          >
            Logout
          </button>
        </div>
      )}
      
      {/* JSON buttons at the top, only show after chart is generated */}
      {(response || astroData) && (
        <div className="json-buttons">
          <button
            onClick={() => setShowJson(prev => !prev)}
            className="json-button"
          >
            {showJson ? 'Hide' : 'Show'} Natal Chart JSON
          </button>
          <button
            onClick={() => setShowAstroJson(v => !v)}
            className="json-button"
          >
            {showAstroJson ? 'Hide' : 'Show'} Astrocartography JSON
          </button>
          <button
            onClick={handleGptFormat}
            className="json-button gpt-button"
            disabled={!response}
            title="Format chart data for AI interpretation"
          >
            {showGptJson ? 'Hide' : 'Show'} GPT Format
          </button>
        </div>
      )}
      {/* JSON output blocks */}
      {showJson && response && (
        <pre style={{
          maxHeight: 300,
          overflow: 'auto',
          background: '#222',
          color: '#fff',
          padding: 8,
          borderRadius: 4,
          fontSize: 11,
          margin: '0 auto 0.5rem auto',
          width: '95%',
        }}>
          {JSON.stringify(response, null, 2)}
        </pre>
      )}
      {showAstroJson && astroData && (
        <pre style={{
          maxHeight: 300,
          overflow: 'auto',
          background: '#222',
          color: '#fff',
          padding: 8,
          borderRadius: 4,
          fontSize: 11,
          margin: '0 auto 0.5rem auto',
          width: '95%',
        }}>
          {JSON.stringify(astroData, null, 2)}
        </pre>
      )}
      {showGptJson && gptData && (
        <div style={{ margin: '0 auto 0.5rem auto', width: '95%' }}>
          <div style={{
            background: '#1a4a3a',
            color: '#fff',
            padding: '8px 12px',
            borderRadius: '4px 4px 0 0',
            fontSize: '12px',
            fontWeight: 'bold',
            borderBottom: '2px solid #2d8659'
          }}>
            🤖 GPT-Optimized Format (AI-Ready Data)
          </div>
          <pre style={{
            maxHeight: 400,
            overflow: 'auto',
            background: '#1a3d2e',
            color: '#a8f5c7',
            padding: 12,
            borderRadius: '0 0 4px 4px',
            fontSize: 11,
            margin: 0,
            border: '1px solid #2d8659'
          }}>
            {JSON.stringify(gptData, null, 2)}
          </pre>
        </div>
      )}
      <h1>Meridian V2</h1>
      
      {/* Demo Charts Section */}
      <DemoCharts onLoadDemo={handleDemoChart} />
      
      <ChartForm
        formData={formData}
        setFormData={setFormData}
        setChartData={() => {}} // This is now handled by the hook
        setLoading={() => {}}   // This is now handled by the hook
        setProgress={() => {}}  // This is now handled by the hook
        setError={setError}
        error={error}
        onSubmit={handleSubmit}
      />      {/* Enhanced Progress Bar with detailed layer status */}
      {(loadingStep || overallProgress.step) && (
        <div className="progress-container" style={{ 
          margin: '1rem auto', 
          maxWidth: '600px',
          padding: '1rem',
          background: '#f8f9fa',
          borderRadius: '8px',
          border: '1px solid #e9ecef'
        }}>
          {/* Main Progress Bar */}
          <div className="progress-bar" style={{
            width: '100%',
            height: '20px',
            backgroundColor: '#e9ecef',
            borderRadius: '10px',
            overflow: 'hidden',
            marginBottom: '0.75rem'
          }}>
            <div className="progress-fill" style={{
              width: overallProgress.percentage > 0 ? `${overallProgress.percentage}%` :
                     // Chart generation steps
                     loadingStep === 'ephemeris' ? '15%' : 
                     loadingStep === 'astro' ? '35%' :
                     // Transit steps
                     loadingStep === 'transit_ephemeris' ? '60%' :
                     loadingStep === 'transit_astro' ? '80%' :
                     // CCG steps
                     loadingStep === 'ccg_ephemeris' || ccgLoading === 'ephemeris' ? '25%' :
                     loadingStep === 'ccg_astro' || ccgLoading === 'astro' ? '75%' :
                     // Completion states
                     loadingStep === 'done' || loadingStep === 'ccg_complete' ? '100%' : 
                     '10%',
              height: '100%',
              backgroundColor: overallProgress.percentage === 100 ? '#28a745' : '#007bff',
              transition: 'width 0.3s ease',
              borderRadius: '10px'
            }} />
          </div>
          
          {/* Main Status Message */}
          <div className="progress-text" style={{
            textAlign: 'center',
            fontWeight: 'bold',
            marginBottom: '0.75rem',
            color: '#495057'
          }}>
            {overallProgress.message || (
              <>
                {/* Consolidated generation steps */}
                {loadingStep === 'natal_ephemeris' && 'Step 1/4: Calculating natal chart ephemeris...'}
                {loadingStep === 'natal_astro' && 'Step 1/4: Generating natal astrocartography lines...'}
                {loadingStep === 'parallel_layers' && 'Steps 2-4: Generating Transit and CCG layers...'}
                {loadingStep === 'finalizing' && 'Step 5/5: Finalizing all layers...'}
                {loadingStep === 'complete' && 'All layers generated successfully!'}
                
                {/* Individual chart generation (legacy) */}
                {loadingStep === 'ephemeris' && 'Calculating natal chart ephemeris...'}
                {loadingStep === 'astro' && 'Generating astrocartography lines...'}
                
                {/* Transit steps */}
                {loadingStep === 'transit_ephemeris' && 'Calculating transit ephemeris...'}
                {loadingStep === 'transit_astro' && 'Generating transit astrocartography...'}
                
                {/* CCG steps */}
                {(loadingStep === 'ccg_ephemeris' || ccgLoading === 'ephemeris') && 'Calculating CCG ephemeris...'}
                {(loadingStep === 'ccg_astro' || ccgLoading === 'astro') && 'Generating CCG astrocartography...'}
                
                {/* Completion states */}
                {loadingStep === 'done' && 'Natal chart complete!'}
                {loadingStep === 'ccg_complete' && 'CCG overlay generated!'}
                
                {/* Generic loading fallback */}
                {!['natal_ephemeris', 'natal_astro', 'parallel_layers', 'finalizing', 'complete',
                    'ephemeris', 'astro', 'transit_ephemeris', 'transit_astro', 'ccg_ephemeris', 'ccg_astro', 
                    'chart_calculation', 'done', 'ccg_complete'].includes(loadingStep) && 
                 'Processing...'}
              </>
            )}
          </div>

          {/* Detailed Layer Status (only show during consolidated generation) */}
          {overallProgress.layerStatuses && overallProgress.step && (
            <div className="layer-status-grid" style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
              gap: '0.5rem',
              fontSize: '0.85rem'
            }}>
              {Object.entries(overallProgress.layerStatuses).map(([layerName, status]) => (
                <div key={layerName} style={{
                  padding: '0.5rem',
                  background: status.status === 'completed' ? '#d4edda' : 
                             status.status === 'failed' ? '#f8d7da' : 
                             status.status === 'processing' ? '#fff3cd' : '#e2e3e5',
                  borderRadius: '4px',
                  border: '1px solid ' + (
                    status.status === 'completed' ? '#c3e6cb' : 
                    status.status === 'failed' ? '#f5c6cb' : 
                    status.status === 'processing' ? '#ffeaa7' : '#d1d3d4'
                  )
                }}>
                  <div style={{ fontWeight: 'bold', textTransform: 'capitalize', marginBottom: '0.25rem' }}>
                    {layerName}
                    {status.status === 'completed' && ' ✅'}
                    {status.status === 'failed' && ' ❌'}
                    {status.status === 'processing' && ' ⏳'}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: '#6c757d' }}>
                    {status.message}
                  </div>
                  {status.status === 'processing' && (
                    <div style={{
                      width: '100%',
                      height: '4px',
                      backgroundColor: '#e9ecef',
                      borderRadius: '2px',
                      overflow: 'hidden',
                      marginTop: '0.25rem'
                    }}>
                      <div style={{
                        width: `${status.progress}%`,
                        height: '100%',
                        backgroundColor: '#ffc107',
                        transition: 'width 0.3s ease'
                      }} />
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Summary sentence after completion */}
      {/* REMOVED: This was the green chart summary block marked with X in the screenshot */}
      {error && <p style={{ color: 'red', marginTop: '1rem' }}>{error}</p>}

      

      {/* Astrocartography visualization */}
      {astroData && (
        <>
          {/* Chart Header */}
          <ChartHeader 
            formData={formData}
            response={response}
            astroData={astroData}
          />

          {/* Chart Display with Layer Tabs */}
          <div className="chart-section">
            <div className="chart-layer-tabs">
              <button 
                className={`layer-tab ${currentChartLayer === 'NATAL' ? 'active' : ''}`}
                onClick={() => setCurrentChartLayer('NATAL')}
              >
                Natal Chart
              </button>
              {/*
              <button 
                className={`layer-tab ${currentChartLayer === 'TRANSIT' ? 'active' : ''}`}
                onClick={() => setCurrentChartLayer('TRANSIT')}
              >
                Transit Chart
              </button>
              */}
              {/*
              <button 
                className={`layer-tab ${currentChartLayer === 'COMPOSITE' ? 'active' : ''}`}
                onClick={() => setCurrentChartLayer('COMPOSITE')}
              >
                Composite Chart
              </button>
              */}
            </div>
            
            <ChartDisplay 
              chartData={response}
              currentLayer={currentChartLayer}
            />
          </div>

          {/* Map Container - Full Width */}
          <div className="map-container" style={{ width: '100%', marginBottom: '1rem' }}>
            <AstroMap 
              data={mergedFilteredData} 
              onHighlightSummary={setHighlightSummary}
              birthCoordinates={response?.coordinates}
            />
          </div>

          {/* Controls Section - Two Columns Below Map */}
          <div className="controls-below-map">
            {/* Natal Display Controls */}
            <NatalDisplayControls
              lineToggles={lineToggles}
              setLineToggles={setLineToggles}
              lineLabels={lineLabels}
              allBodies={allBodies}
              bodyToggles={bodyToggles}
              setBodyToggles={setBodyToggles}
              showBodyAccordion={showBodyAccordion}
              setShowBodyAccordion={setShowBodyAccordion}
            />
            {/* CCG Controls Section */}
            <CCGControls
              layerManager={layerManager}
              forceMapUpdate={forceMapUpdate}
              ccgDate={ccgDate}
              setCCGDate={setCCGDate}
              handleGenerateCCG={handleGenerateCCG}
              lineToggles={ccgLineToggles}
              setLineToggles={setCCGLineToggles}
              allBodies={ccgBodies}
              bodyToggles={ccgBodyToggles}
              setBodyToggles={setCCGBodyToggles}
              showBodyAccordion={ccgShowBodyAccordion}
              setShowBodyAccordion={setCCGShowBodyAccordion}
            />
            {/* Transit Controls */}
            <TransitControls
              isTransitEnabled={isTransitEnabled}
              layerManager={layerManager}
              forceMapUpdate={forceMapUpdate}
              handleGenerateTransits={handleGenerateTransits}
              loadingStep={loadingStep}
              currentTransitDateTime={currentTransitDateTime}
              setCurrentTransitDateTime={setCurrentTransitDateTime}
              lineToggles={transitLineToggles}
              setLineToggles={setTransitLineToggles}
              allBodies={transitBodies}
              bodyToggles={transitBodyToggles}
              setBodyToggles={setTransitBodyToggles}
              showBodyAccordion={transitShowBodyAccordion}
              setShowBodyAccordion={setTransitShowBodyAccordion}
            />
          </div>
        </>
      )}
    </div>
  )
}

export default App
