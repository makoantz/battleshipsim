import React, { useState } from 'react';

// Import the real components and API service
import ControlPanel from './ControlPanel';
import ResultsDisplay from './ResultsDisplay';
import { runSimulation } from '../../api/simulationService'; // <-- Real API service
import './Dashboard.css';

function Dashboard() {
  const [simulationResult, setSimulationResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // This function is passed to the ControlPanel.
  // It now makes a real network request.
  const handleRunSimulation = async (simulationParams) => {
    setIsLoading(true);
    setError(null);
    setSimulationResult(null);

    console.log("Calling backend with params:", simulationParams);
    try {
      // ** This is the REAL API CALL **
      const result = await runSimulation(simulationParams);
      console.log("Received result from backend:", result);
      setSimulationResult(result);
    } catch (err) {
      console.error("Simulation API call failed:", err);
      // The error message comes from our simulationService error handling
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="dashboard">
      <div className="dashboard-panel">
        {/* Render the real ControlPanel component */}
        <ControlPanel onRunSimulation={handleRunSimulation} isLoading={isLoading} />
      </div>

      <div className="dashboard-panel">
        {isLoading && <div className="loading-spinner">Running simulation on server...</div>}

        {error && <div className="error-message">Error: {error}</div>}
        
        {simulationResult && (
          // Render the real ResultsDisplay component
          <ResultsDisplay result={simulationResult} />
        )}

        {/* This placeholder text will show on initial load */}
        {!isLoading && !error && !simulationResult && (
          <div className="placeholder-text">
            Click "Run Test Simulation" to get results from the backend.
          </div>
        )}
      </div>
    </div>
  );
}

export default Dashboard;