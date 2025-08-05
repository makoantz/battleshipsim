import React from 'react';
import StatsTable from '../visualizations/StatsTable';

function ResultsDisplay({ result }) {
  if (!result) {
    return null;
  }

  return (
    <div>
      <h2>Simulation Results</h2>
      
      {/* Render the new StatsTable component */}
      <StatsTable stats={result.analysis.summary_stats} />

      {/* We can still keep the raw data for debugging if we want, or remove it.
          Let's comment it out for now. */}
      {/*
      <pre style={{ textAlign: 'left', backgroundColor: '#f0f0f0', padding: '15px', borderRadius: '5px', whiteSpace: 'pre-wrap' }}>
        {JSON.stringify(result, null, 2)}
      </pre>
      */}
    </div>
  );
}

export default ResultsDisplay;