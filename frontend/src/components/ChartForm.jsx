import React, { useEffect, useRef, useState } from 'react';
import { calculateChart } from '../apiClient';
import useCitySuggestions from '../hooks/useCitySuggestions';

function ChartForm({ formData, setFormData, setChartData, setLoading, setProgress, setError, error, onSubmit }) {
  const dropdownRef = useRef(null);
  const [houseSystems, setHouseSystems] = useState([]);
  const [houseSystemInfo, setHouseSystemInfo] = useState({});
  const {
    suggestions,
    showSuggestions,
    handleInputChange,
    handleSuggestionSelect
  } = useCitySuggestions(formData, setFormData);
  
  useEffect(() => {
    // Fetch house systems from backend
    const fetchHouseSystems = async () => {
      try {
        const response = await fetch('/api/house-systems');
        const data = await response.json();
        if (data.house_systems) {
          setHouseSystems(data.house_systems);
          // Create a lookup object for descriptions
          const infoLookup = {};
          data.house_systems.forEach(system => {
            infoLookup[system.id] = system;
          });
          setHouseSystemInfo(infoLookup);
        }
      } catch (err) {
        console.error('Failed to fetch house systems:', err);
        // Fallback to basic house systems if API fails
        setHouseSystems([
          { id: 'whole_sign', name: 'Whole Sign', description: 'Each zodiac sign equals one house' },
          { id: 'placidus', name: 'Placidus', description: 'Most popular modern system' },
          { id: 'koch', name: 'Koch', description: 'Similar to Placidus' },
          { id: 'equal', name: 'Equal House', description: 'Equal 30° segments from Ascendant' }
        ]);
      }
    };
    
    fetchHouseSystems();
  }, [setError]);

  const handleFormChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setProgress(10);
    try {
      const chart = await calculateChart(formData);
      if (chart.error) throw new Error(chart.error);
      setChartData(chart);
      setProgress(100);
    } catch (err) {
      console.error(err);
      setError(err.message);
      setProgress(0);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={onSubmit || handleSubmit}>
      <input type="text" name="name" placeholder="Full Name" value={formData.name} onChange={handleFormChange} required />
      <input type="date" name="birth_date" value={formData.birth_date} onChange={handleFormChange} required />
      <input type="time" name="birth_time" value={formData.birth_time} onChange={handleFormChange} required />
      <div style={{ position: 'relative' }} ref={dropdownRef}>
        <input
          type="text"
          name="birth_city"
          placeholder="City"
          value={formData.birth_city}
          onChange={handleInputChange}
          onFocus={() => formData.birth_city.length > 2 && handleInputChange({ target: { name: 'birth_city', value: formData.birth_city } })}
          required
        />
        {showSuggestions && suggestions.length > 0 && (
          <ul style={{
            position: 'absolute', background: '#fff', border: '1px solid #ccc',
            zIndex: 1000, maxHeight: '200px', overflowY: 'auto', margin: 0, padding: 0,
            listStyle: 'none', width: '100%'
          }}>
            {suggestions.map((s, i) => {
              const city = s.city || s.properties?.city || s.formatted || 'Unknown City';
              const state = s.state || s.properties?.state || '';
              const country = s.country || s.properties?.country || '';
              const label = `${city}, ${state}, ${country}`;
              return (
                <li
                  key={i}
                  style={{ padding: '0.5rem', cursor: 'pointer' }}
                  onMouseDown={e => {
                    e.preventDefault();
                    handleSuggestionSelect(s);
                  }}
                >
                  {label}
                </li>
              );
            })}
          </ul>
        )}      </div>
      
      {/* House System Dropdown */}
      <div style={{ marginTop: '1rem' }}>
        <label htmlFor="house_system" style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold' }}>
          House System:
        </label>
        <select
          id="house_system"
          name="house_system"
          value={formData.house_system || 'whole_sign'}
          onChange={handleFormChange}
          style={{
            width: '100%',
            padding: '0.5rem',
            border: '1px solid #ccc',
            borderRadius: '4px',
            fontSize: '1rem'
          }}
        >
          {houseSystems.map(system => (
            <option key={system.id} value={system.id}>
              {system.name}
            </option>
          ))}
        </select>
        {/* Description for the selected house system */}
        {houseSystemInfo[formData.house_system || 'whole_sign'] && (
          <p style={{ 
            marginTop: '0.5rem', 
            fontSize: '0.9rem', 
            color: '#666',
            fontStyle: 'italic'
          }}>
            {houseSystemInfo[formData.house_system || 'whole_sign'].description}
          </p>
        )}
      </div>
      
      <button type="submit">Generate All Charts</button>
      {error && <p style={{ color: 'red', marginTop: '1rem' }}>{error}</p>}
    </form>
  );
}

export default ChartForm;
