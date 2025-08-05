import React from 'react';

// This component will eventually contain all our charts and stats.
function ResultsDisplay({ result }) {
  if (!result) {
    return null;
  }

  // For now, we'll just display the raw JSON from the backend
  // to confirm that we are receiving the data correctly.
  return (
    <div>
      <h2>Simulation Results</h2>
      <pre style={{ textAlign: 'left', backgroundColor: '#f0f0f0', padding: '15px', borderRadius: '5px', whiteSpace: 'pre-wrap' }}>
        {JSON.stringify(result, null, 2)}
      </pre>
    </div>
  );
}

export default ResultsDisplay;