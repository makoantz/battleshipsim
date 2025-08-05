import React from 'react';
import './StatsTable.css';

/**
 * A component that renders a table of summary statistics.
 * @param {Object} props - The component props.
 * @param {Object} props.stats - The summary_stats object from the API response.
 * e.g., { mean: 95.5, median: 97, ... }
 */
function StatsTable({ stats }) {
  if (!stats) {
    return null; // Don't render anything if there are no stats
  }

  // Helper function to format numbers to 2 decimal places
  const formatNumber = (num) => {
    return Number(num).toLocaleString(undefined, {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });
  };

  return (
    <div className="stats-table-container">
      <h3>Summary Statistics</h3>
      <table className="stats-table">
        <tbody>
          <tr>
            <td>Mean Shots</td>
            <td>{formatNumber(stats.mean)}</td>
          </tr>
          <tr>
            <td>Median Shots</td>
            <td>{stats.median}</td>
          </tr>
          <tr>
            <td>Standard Deviation</td>
            <td>{formatNumber(stats.std_dev)}</td>
          </tr>
          <tr>
            <td>Min / Max Shots</td>
            <td>{stats.min} / {stats.max}</td>
          </tr>
          <tr>
            <td>Total Simulations</td>
            <td>{stats.total_simulations.toLocaleString()}</td>
          </tr>
        </tbody>
      </table>
    </div>
  );
}

export default StatsTable;