import React from 'react';

function ControlPanel({ onRunSimulation, isLoading }) {
  // We will build out the full UI in later steps.
  // For now, this is just a placeholder to test the API call.
  const handleTestRun = () => {
    const testParams = {
      algorithm: 'randomsearch',
      num_simulations: 500,
      ship_placement_strategy: 'random_each_round',
    };
    onRunSimulation(testParams);
  };

  return (
    <div>
      <h2>Control Panel</h2>
      <p>Configure simulation parameters below.</p>
      {/* This button allows us to trigger the API call in Dashboard */}
      <button onClick={handleTestRun} disabled={isLoading} style={{ padding: '10px', fontSize: '1rem' }}>
        {isLoading ? 'Running Simulation...' : 'Run Test Simulation'}
      </button>
    </div>
  );
}

export default ControlPanel;