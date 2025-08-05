import React from 'react';
import StatsTable from '../visualizations/StatsTable';
import ShotDistributionChart from '../visualizations/ShotDistributionChart';

function ResultsDisplay({ result }) {
  if (!result) {
    return null;
  }

  return (
    <div>
      <h2>Simulation Results</h2>
      
      {/* Render the stats table */}
      <StatsTable stats={result.analysis.summary_stats} />
      
      {/* Render the new histogram chart */}
      <ShotDistributionChart histogramData={result.analysis.histogram} />
    </div>
  );
}

export default ResultsDisplay;