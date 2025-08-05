import React, { useState } from 'react';
import ControlPanel from './ControlPanel';
import ResultsDisplay from './ResultsDisplay';
import { runSimulation, runComparison } from '../../api/simulationService';
import './Dashboard.css';

function Dashboard() {
  // State to hold the final results. Can be a single result or a comparison result.
  const [results, setResults] = useState(null);
  
  // State to track the type of result we have ('single' or 'comparison')
  const [resultType, setResultType] = useState(null);

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const clearState = () => {
    setIsLoading(true);
    setError(null);
    setResults(null);
    setResultType(null);
  };

  // Handler for running a single algorithm simulation
  const handleRunSimulation = async (simulationParams) => {
    clearState();
    console.log("Calling backend for SINGLE simulation:", simulationParams);
    try {
      const result = await runSimulation(simulationParams);
      console.log("Received SINGLE result:", result);
      setResults(result);
      setResultType('single');
    } catch (err) {
      console.error("Single simulation failed:", err);
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  // Handler for running a comparison of multiple algorithms
  const handleRunComparison = async (comparisonParams) => {
    clearState();
    console.log("Calling backend for COMPARISON:", comparisonParams);
    try {
      const result = await runComparison(comparisonParams);
      console.log("Received COMPARISON result:", result);
      setResults(result);
      setResultType('comparison');
    } catch (err)
    {
      console.error("Comparison simulation failed:", err);
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="dashboard">
      <div className="dashboard-panel">
        <ControlPanel 
          onRunSimulation={handleRunSimulation} 
          onRunComparison={handleRunComparison} 
          isLoading={isLoading} 
        />
      </div>

      <div className="dashboard-panel">
        {isLoading && <div className="loading-spinner">Running simulation on server...</div>}
        
        {error && <div className="error-message">Error: {error}</div>}
        
        {results && (
          <ResultsDisplay resultData={results} resultType={resultType} />
        )}

        {!isLoading && !error && !results && (
          <div className="placeholder-text">
            Select one or more algorithms and click "Run" to see the results.
          </div>
        )}
      </div>
    </div>
  );
}

export default Dashboard;