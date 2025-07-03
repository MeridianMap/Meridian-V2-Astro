
import React from 'react';
import './PlanetSummaryTable.css';

const PlanetSummaryTable = ({ summaryData }) => {
  if (!summaryData || summaryData.length === 0) {
    return <p>No planet data available for summary.</p>;
  }

  return (
    <div className="planet-summary-table-container">
      <table className="planet-summary-table">
        <thead>
          <tr>
            <th>Planet</th>
            <th>Sign</th>
            <th>House</th>
            <th>House Meaning</th>
          </tr>
        </thead>
        <tbody>
          {summaryData.map((item, index) => (
            <tr key={index}>
              <td>{item.planet}</td>
              <td>{item.sign}</td>
              <td>{item.house}</td>
              <td className="house-definition">{item.houseDefinition}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default PlanetSummaryTable;
