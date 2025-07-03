import React from 'react';
import './DemoCharts.css';

const DemoCharts = ({ onLoadDemo }) => {
  const demoProfiles = {
    j: {
      name: 'J',
      birth_date: '1987-07-15',
      birth_time: '09:01',
      birth_city: 'Dallas',
      birth_state: 'Texas',
      birth_country: 'United States',
      timezone: 'America/Chicago',
      house_system: 'whole_sign',
      coordinates: {
        latitude: 32.776272,
        longitude: -96.796856
      }
    },
    a: {
      name: 'A',
      birth_date: '1983-09-08',
      birth_time: '03:36',
      birth_city: 'Santa Fe',
      birth_state: 'New Mexico',
      birth_country: 'United States',
      timezone: 'America/Denver',
      house_system: 'whole_sign',
      coordinates: {
        latitude: 35.687610,
        longitude: -105.938456
      }
    }
  };

  const handleDemoClick = (profileKey) => {
    const profile = demoProfiles[profileKey];
    if (profile && onLoadDemo) {
      onLoadDemo(profile);
    }
  };

  return (
    <div className="demo-charts-container">
      <div className="demo-charts-header">
        <h3>🎯 Demo Charts</h3>
        <p>Try these pre-configured charts for testing</p>
      </div>
      
      <div className="demo-buttons">
        <button
          onClick={() => handleDemoClick('j')}
          className="demo-button demo-j"
          title="Dallas, TX • 1987-07-15 • 09:01 CDT"
        >
          <div className="demo-button-content">
            <span className="demo-name">Chart J</span>
            <span className="demo-location">Dallas, TX</span>
            <span className="demo-date">July 15, 1987</span>
          </div>
        </button>

        <button
          onClick={() => handleDemoClick('a')}
          className="demo-button demo-a"
          title="Santa Fe, NM • 1983-09-08 • 03:36 MDT"
        >
          <div className="demo-button-content">
            <span className="demo-name">Chart A</span>
            <span className="demo-location">Santa Fe, NM</span>
            <span className="demo-date">September 8, 1983</span>
          </div>
        </button>
      </div>

      <div className="demo-info">
        <small>
          These charts use verified coordinates and timezone data for accurate calculations.
        </small>
      </div>
    </div>
  );
};

export default DemoCharts;
