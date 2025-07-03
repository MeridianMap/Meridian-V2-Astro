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
import HumanDesignControls from './components/HumanDesignControls';
import useChartData from './hooks/useChartData';
import useAstroData from './hooks/useAstroData';
import useTransitData from './hooks/useTransitData';
import useCCGData from './hooks/useCCGData';
import useHumanDesignData from './hooks/useHumanDesignData';

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
  const { isTransitEnabled, fetchTransits, loadingStep: transitLoading } = useTransitData(layerManager, forceMapUpdate, timeManager);
  const { fetchCCG, loadingStep: ccgLoading } = useCCGData(layerManager, forceMapUpdate);
  const { fetchHumanDesign, loadingStep: hdLoading } = useHumanDesignData(layerManager, forceMapUpdate);

  // Enhanced progress tracking
  const [overallProgress, setOverallProgress] = useState({
    step: null,
    percentage: 0,
    message: ''
  });

  // Combine all loading states for display
  const activeLoadingStep = overallProgress.step || chartLoading || transitLoading || ccgLoading || hdLoading;
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

    // Register Human Design layer (with all natal features except fixed stars)
    layerManager.addLayer('HD_DESIGN', {
      visible: false,
      order: 2,
      type: 'overlay',
      style: { color: '#D47AFF', width: 3, opacity: 0.85 }, // Purple color for HD
      subLayers: { 
        ac_dc: true, 
        ic_mc: true, 
        parans: true, 
        lots: true,
        aspects: true // HD includes aspects unlike CCG/Transit
      }
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
    fixed_star: true,
    hermetic_lot: true,
    parans: true,
    ic_mc: true,
    ac_dc: true
  });
  // Human Design toggles (includes aspects unlike CCG/Transit)
  const [hdLineToggles, setHDLineToggles] = useState({
    planet: true,
    mc_aspects: true,
    ac_aspects: true,
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
  // CCG body toggles (exclude nodes)
  const [ccgBodyToggles, setCCGBodyToggles] = useState(
    Object.fromEntries(ccgBodies.map(name => [name, true]))
  );
  // Human Design body toggles (includes all bodies like natal)
  const [hdBodyToggles, setHDBodyToggles] = useState(
    Object.fromEntries(allBodies.map(name => [name, true]))
  );
  const [showBodyAccordion, setShowBodyAccordion] = useState(true);
  const [ccgShowBodyAccordion, setCCGShowBodyAccordion] = useState(true);
  const [hdShowBodyAccordion, setHDShowBodyAccordion] = useState(true);

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
  const [transitShowBodyAccordion, setTransitShowBodyAccordion] = useState(true);

  // Line labels
  const lineLabels = {
    planet: 'Planet Lines',
    mc_aspects: 'MC Aspects',
    ac_aspects: 'AC Aspects',
    fixed_star: 'Fixed Stars',
    hermetic_lot: 'Hermetic Lots',
    parans: 'Parans',  };
  
  // Form submit handler
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      // Step 1: Calculate natal chart
      setOverallProgress({ step: 'ephemeris', percentage: 20, message: 'Calculating natal ephemeris...' });
      const chartData = await fetchChart(formData);
      
      if (chartData) {
        // Step 2: Use astrocartography data from chart response
        setOverallProgress({ step: 'astro', percentage: 60, message: 'Processing astrocartography lines...' });
        
        // Set the astrocartography data from the chart response instead of making another API call
        if (chartData.astrocartography) {
          console.log('🎯 Setting astrocartography data from chart response:', {
            features: chartData.astrocartography.features?.length || 0,
            dataKeys: Object.keys(chartData.astrocartography)
          });
          
          console.log('🎯 Natal Features Sample (first 3):', chartData.astrocartography.features?.slice(0, 3).map(f => ({
            planet: f.properties?.planet,
            layer: f.properties?.layer,
            lineType: f.properties?.line_type,
            coordinates: f.geometry?.coordinates?.[0]?.[0] // First coordinate
          })));
          
          setAstroData(chartData.astrocartography);
          // Set the data in layer manager
          layerManager.setLayerData('natal', chartData.astrocartography);
          forceMapUpdate();
        } else {
          console.log('❌ No astrocartography data in chart response');
        }
        
        // Step 3: Complete
        setOverallProgress({ step: 'done', percentage: 100, message: 'Chart generation complete!' });
        
        // Clear progress after a short delay
        setTimeout(() => {
          setOverallProgress({ step: null, percentage: 0, message: '' });
        }, 2000);
      }
    } catch (error) {
      setOverallProgress({ step: null, percentage: 0, message: '' });
      console.error('Chart generation failed:', error);
    }
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

  // Human Design handler
  const handleGenerateHD = async () => {
    try {
      setOverallProgress({ step: 'hd_calculation', percentage: 30, message: 'Calculating Human Design chart...' });
      // Get coordinates from natal chart response
      const coordinates = response?.coordinates;
      await fetchHumanDesign(formData, coordinates);
      setOverallProgress({ step: 'hd_complete', percentage: 100, message: 'Human Design overlay generated!' });
      // Ensure HD_DESIGN layer is visible after generation
      layerManager.setLayerVisible('HD_DESIGN', true);
      forceMapUpdate(); // Ensure map updates immediately after HD overlay is generated
      
      // Clear progress after delay
      setTimeout(() => {
        setOverallProgress({ step: null, percentage: 0, message: '' });
      }, 2000);
    } catch (error) {
      setOverallProgress({ step: null, percentage: 0, message: '' });
      console.error('Human Design generation failed:', error);
    }
  };

  // Demo chart handler
  const handleDemoChart = async (demoData) => {
    console.log('Loading demo chart:', demoData);
    
    // Update form data with demo values
    setFormData(demoData);

    // Generate the chart automatically
    try {
      setOverallProgress({ step: 'ephemeris', percentage: 20, message: `Generating demo chart for ${demoData.name}...` });
      const chartData = await fetchChart(demoData);
      
      if (chartData) {
        setOverallProgress({ step: 'astro', percentage: 60, message: 'Processing demo astrocartography...' });
        
        if (chartData.astrocartography) {
          console.log('🎯 Setting demo astrocartography data:', {
            features: chartData.astrocartography.features?.length || 0,
            dataKeys: Object.keys(chartData.astrocartography)
          });
          
          setAstroData(chartData.astrocartography);
          layerManager.setLayerData('natal', chartData.astrocartography);
          forceMapUpdate();
        }
        
        setOverallProgress({ step: 'done', percentage: 100, message: `Demo chart for ${demoData.name} complete!` });
        
        setTimeout(() => {
          setOverallProgress({ step: null, percentage: 0, message: '' });
        }, 2000);
      }
    } catch (error) {
      setOverallProgress({ step: null, percentage: 0, message: '' });
      console.error('Demo chart generation failed:', error);
      setError(`Failed to generate demo chart for ${demoData.name}. Please try again.`);
    }
  };

  // Re-generate CCG overlay when ccgDate or line toggles change
  useEffect(() => {
    if (layerManager.isLayerVisible('CCG')) {
      handleGenerateCCG();
    }
    // eslint-disable-next-line
  }, [ccgDate, ccgLineToggles]); // Also re-generate when line toggles change

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
    console.log('🟦 CCG Layer Debug:', {
      isVisible: layerManager.isLayerVisible('CCG'),
      hasLayer: !!ccgLayer,
      hasData: !!(ccgLayer && ccgLayer.data),
      hasFeatures: !!(ccgLayer && ccgLayer.data && ccgLayer.data.features),
      featuresCount: ccgLayer?.data?.features?.length || 0,
      firstFeatureLayer: ccgLayer?.data?.features?.[0]?.properties?.layer,
      firstFeatureProps: ccgLayer?.data?.features?.[0]?.properties
    });
    if (layerManager.isLayerVisible('CCG') && ccgLayer && ccgLayer.data && ccgLayer.data.features) {
      let ccgFeatures = ccgLayer.data.features;
      // Don't filter by layer property initially - let's see all features
      ccgFeatures = ccgFeatures.filter(f => {
        // Remove the layer check temporarily for debugging
        // if (f.properties?.layer !== 'CCG') return false;
        
        const cat = f.properties?.category;
        const lineType = f.properties?.line_type;
        
        // CCG Feature Type Filtering
        if (cat === 'parans' && !ccgLineToggles.parans) return false;
        if (cat === 'fixed_star' && !ccgLineToggles.fixed_star) return false;
        
        // Handle hermetic lots first - they have their own toggle and should NOT be affected by IC/MC toggle
        if (cat === 'hermetic_lot' || cat === 'lot' || f.properties?.body_type === 'lot') {
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
        if (lineType === 'IC' || lineType === 'MC') {
          if (!ccgLineToggles.ic_mc) return false; // Line type disabled
          if (body && ccgBodyToggles[body] === false) return false; // Body disabled
        } else if (lineType === 'AC' || lineType === 'DC' || lineType === 'HORIZON') {
          if (!ccgLineToggles.ac_dc) return false; // Line type disabled  
          if (body && ccgBodyToggles[body] === false) return false; // Body disabled
        } else {
          // For other features (parans, etc.), check body if it exists
          if (body && ccgBodyToggles[body] === false) return false;
        }
        
        return true;
      });
      console.log('🟦 Final CCG features count:', ccgFeatures.length);
      features = features.concat(ccgFeatures.map(f => ({ ...f, layerName: 'CCG' })));
    }

    // Human Design overlay - filtering using unified controls
    const hdLayer = layerManager.getLayer('HD_DESIGN');
    console.log('🟣 HD Layer Debug:', {
      isVisible: layerManager.isLayerVisible('HD_DESIGN'),
      hasLayer: !!hdLayer,
      hasData: !!(hdLayer && hdLayer.data),
      hasFeatures: !!(hdLayer && hdLayer.data && hdLayer.data.features),
      featuresCount: hdLayer?.data?.features?.length || 0,
      firstFeatureLayer: hdLayer?.data?.features?.[0]?.properties?.layer,
      firstFeatureProps: hdLayer?.data?.features?.[0]?.properties
    });
    if (layerManager.isLayerVisible('HD_DESIGN') && hdLayer && hdLayer.data && hdLayer.data.features) {
      console.log('🟣 HD Layer visible and has data, features count:', hdLayer.data.features.length);
      let hdFeatures = hdLayer.data.features;
      hdFeatures = hdFeatures.filter(f => {
        // Remove the layer check temporarily for debugging
        // if (f.properties?.layer !== 'HD_DESIGN') return false;
        
        const cat = f.properties?.category;
        const lineType = f.properties?.line_type;
        
        // HD Feature Type Filtering
        if (cat === 'parans' && !hdLineToggles.parans) return false;
        
        // Handle hermetic lots first - they have their own toggle and should NOT be affected by IC/MC toggle
        if (cat === 'hermetic_lot' || cat === 'lot' || f.properties?.body_type === 'lot') {
          return hdLineToggles.hermetic_lot; // Only check hermetic lot toggle, ignore IC/MC toggle
        }
        
        // Aspect handling for HD (unlike CCG/Transit, HD includes aspects)
        if (cat === 'aspect') {
          const aspectTo = f.properties?.to;
          if (aspectTo === 'MC' && !hdLineToggles.mc_aspects) return false;
          if (aspectTo === 'AC' && !hdLineToggles.ac_aspects) return false;
          if (!aspectTo) {
            if (!hdLineToggles.mc_aspects && !hdLineToggles.ac_aspects) return false;
          }
        }
        
        // HD Body Filtering (extract body name first)
        let body = f.properties?.planet || f.properties?.body || f.properties?.name;
        // Remove " HD" suffix if present in the name
        if (body && body.endsWith(' HD')) {
          body = body.replace(' HD', '');
        }
        if (body === 'Pallas Athena') body = 'Pallas';
        if (body === 'Lilith' || body === 'BML' || body === 'Black Moon') body = 'Black Moon Lilith';
        if (body === 'North Node' || body === 'NN' || body === 'Rahu') body = 'Lunar Node';
        
        // For planet lines (IC/MC/AC/DC), check both line type AND body toggles
        if (lineType === 'IC' || lineType === 'MC') {
          if (!hdLineToggles.ic_mc) return false; // Line type disabled
          if (body && hdBodyToggles[body] === false) return false; // Body disabled
        } else if (lineType === 'AC' || lineType === 'DC' || lineType === 'HORIZON') {
          if (!hdLineToggles.ac_dc) return false; // Line type disabled  
          if (body && hdBodyToggles[body] === false) return false; // Body disabled
        } else {
          // For other features (parans, aspects, etc.), check body if it exists
          if (body && hdBodyToggles[body] === false) return false;
        }
        
        return true;
      });
      console.log('🟣 HD Features after filtering:', hdFeatures.length);
      features = features.concat(hdFeatures.map(f => ({ ...f, layerName: 'HD_DESIGN' })));
    }

    // Transit Overlay
    if (layerManager.isLayerVisible('transit')) {
      console.log('🟪 Transit layer is visible, processing transit data...');
      const transitData = layerManager.getLayer('transit')?.data;
      console.log('🟪 Transit data from layer manager:', {
        hasTransitData: !!transitData,
        featuresCount: transitData?.features?.length || 0,
        firstFeatureLayer: transitData?.features?.[0]?.properties?.layer,
        firstFeatureProps: transitData?.features?.[0]?.properties
      });
      let transitFeatures = transitData?.features || [];
      console.log('🟪 Transit features before filtering:', transitFeatures.length);
      
      transitFeatures = transitFeatures.filter(f => {
        try {
          // Defensive null checks
          if (!f || !f.properties) return false;
          
          // Remove the layer check temporarily for debugging
          // if (f.properties?.layer !== 'transit') {
          //   console.log('Feature filtered out - not transit layer:', f.properties?.layer);
          //   return false;
          // }
          
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
          
          console.log('🟪 Transit features after filtering:', transitFeatures.length);
          return true;
        } catch (err) {
          console.error('Error filtering transit feature:', err, f);
          return false; // Filter out problematic features
        }
      });
      console.log('🟪 Final transit features count:', transitFeatures.length);
      features = features.concat(transitFeatures.map(f => ({ ...f, layerName: 'transit' })));
    }

    console.log('[DEBUG] Total merged features:', features.length);
    return { features };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [astroData, lineToggles, bodyToggles, ccgLineToggles, ccgBodyToggles, hdLineToggles, hdBodyToggles, transitLineToggles, transitBodyToggles, layerManager, mapUpdateTrigger]);

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
      />      {loadingStep && (
        <div className="progress-container">
          <div className="progress-bar">
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
                     // Human Design steps
                     loadingStep === 'chart_calculation' || hdLoading === 'chart_calculation' ? '20%' :
                     loadingStep === 'hd_calculation' || hdLoading === 'hd_calculation' ? '70%' :
                     // Completion states
                     loadingStep === 'done' || loadingStep === 'ccg_complete' || loadingStep === 'hd_complete' ? '100%' : 
                     '10%'
            }} />
          </div>
          <span className="progress-text">
            {overallProgress.message || (
              <>
                {/* Chart generation */}
                {loadingStep === 'ephemeris' && 'Calculating natal chart ephemeris...'}
                {loadingStep === 'astro' && 'Generating astrocartography lines...'}
                
                {/* Transit steps */}
                {loadingStep === 'transit_ephemeris' && 'Calculating transit ephemeris...'}
                {loadingStep === 'transit_astro' && 'Generating transit astrocartography...'}
                
                {/* CCG steps */}
                {(loadingStep === 'ccg_ephemeris' || ccgLoading === 'ephemeris') && 'Calculating CCG ephemeris...'}
                {(loadingStep === 'ccg_astro' || ccgLoading === 'astro') && 'Generating CCG astrocartography...'}
                
                {/* Human Design steps */}
                {(loadingStep === 'chart_calculation' || hdLoading === 'chart_calculation') && 'Calculating base chart data...'}
                {(loadingStep === 'hd_calculation' || hdLoading === 'hd_calculation') && 'Generating Human Design astrocartography...'}
                
                {/* Completion states */}
                {loadingStep === 'done' && 'Natal chart complete!'}
                {loadingStep === 'ccg_complete' && 'CCG overlay generated!'}
                {loadingStep === 'hd_complete' && 'Human Design overlay generated!'}
                
                {/* Generic loading fallback */}
                {!['ephemeris', 'astro', 'transit_ephemeris', 'transit_astro', 'ccg_ephemeris', 'ccg_astro', 
                    'chart_calculation', 'hd_calculation', 'done', 'ccg_complete', 'hd_complete'].includes(loadingStep) && 
                 'Processing...'}
              </>
            )}
          </span>
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
                className={`layer-tab ${currentChartLayer === 'HUMAN_DESIGN' ? 'active' : ''}`}
                onClick={() => setCurrentChartLayer('HUMAN_DESIGN')}
              >
                Human Design
              </button>
              */}
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
            <AstroMap data={mergedFilteredData} />
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
            {/* Human Design Controls Section */}
            <HumanDesignControls
              layerManager={layerManager}
              forceMapUpdate={forceMapUpdate}
              handleGenerateHD={handleGenerateHD}
              loadingStep={loadingStep}
              lineToggles={hdLineToggles}
              setLineToggles={setHDLineToggles}
              allBodies={allBodies}
              bodyToggles={hdBodyToggles}
              setBodyToggles={setHDBodyToggles}
              showBodyAccordion={hdShowBodyAccordion}
              setShowBodyAccordion={setHDShowBodyAccordion}
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
