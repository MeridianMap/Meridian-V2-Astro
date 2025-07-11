import React, { useEffect, useRef } from 'react';
import { calculateChart } from '../apiClient';
import useCitySuggestions from '../hooks/useCitySuggestions';

function ChartForm({ formData, setFormData, setChartData, setLoading, setProgress, setError, error, onSubmit }) {
  const dropdownRef = useRef(null);
  const {
    suggestions,
    showSuggestions,
    handleInputChange,
    handleSuggestionSelect
  } = useCitySuggestions(formData, setFormData);
  
  useEffect(() => {
    // Removed `fetchHouseSystems` function and its usage
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
          {/* Options for house systems would go here */}
        </select>
        {/* Description for the selected house system would go here */}
      </div>
      
      <button type="submit">Generate All Charts</button>
      {error && <p style={{ color: 'red', marginTop: '1rem' }}>{error}</p>}
    </form>
  );
}

export default ChartForm;
