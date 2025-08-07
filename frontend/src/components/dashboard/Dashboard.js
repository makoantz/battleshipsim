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
  const [selectedAlgorithms, setSelectedAlgorithms] = useState([]);

  const clearState = () => {
    setIsLoading(true);
    setError(null);
    setResults(null);
    setResultType(null);
  };

  // Handler for algorithm selection change
  const handleAlgorithmSelectionChange = (algorithms) => {
    setSelectedAlgorithms(algorithms);
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
    } catch (err) {
      console.error("Comparison simulation failed:", err);
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  // Helper function to get algorithm descriptions
  const getAlgorithmDescription = (algorithmId) => {
    const descriptions = {
      'huntandtarget': 'Classic hunt & target with adjacent firing after hits',
      'hunt_target': 'JSON-defined hunt & target implementation',
      'p2m2': 'Probability-based diagonal hunting with 2-space targeting',
      'p2m2_json': 'JSON-defined P2M2 implementation',
      'p2m2optimized': 'Advanced hybrid with gap-filling and space awareness',
      'p2m2_optimized': 'JSON-defined optimized P2M2 implementation',
      'p2m2stdirectional': 'P2M2 with directional smart targeting',
      'p2m2st': 'JSON-defined P2M2-ST implementation',
      'randomsearch': 'Pure random targeting strategy',
      'random_search': 'JSON-defined random search implementation',
      'smarttarget': 'Intelligent targeting with probability calculations',
      'smart_target': 'JSON-defined smart targeting implementation'
    };
    return descriptions[algorithmId] || 'Advanced battleship targeting algorithm';
  };

  return (
    <div className="dashboard">
      {/* Algorithm Summary Table */}
      {selectedAlgorithms.length > 0 && (
        <div className="algorithm-summary" style={{
          backgroundColor: '#f8f9fa',
          border: '1px solid #dee2e6',
          borderRadius: '8px',
          padding: '20px',
          marginBottom: '20px',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
        }}>
          <h3 style={{
            color: '#495057',
            marginBottom: '15px',
            fontSize: '1.2em'
          }}>
            📊 Selected Algorithms Summary ({selectedAlgorithms.length})
          </h3>
          <div className="summary-table-container" style={{ overflowX: 'auto' }}>
            <table style={{
              width: '100%',
              borderCollapse: 'collapse',
              backgroundColor: 'white',
              borderRadius: '6px',
              overflow: 'hidden',
              boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
            }}>
              <thead>
                <tr style={{ backgroundColor: '#e9ecef' }}>
                  <th style={{
                    padding: '12px 15px',
                    textAlign: 'left',
                    borderBottom: '2px solid #dee2e6',
                    fontWeight: '600',
                    color: '#495057'
                  }}>Algorithm</th>
                  <th style={{
                    padding: '12px 15px',
                    textAlign: 'center',
                    borderBottom: '2px solid #dee2e6',
                    fontWeight: '600',
                    color: '#495057'
                  }}>Type</th>
                  <th style={{
                    padding: '12px 15px',
                    textAlign: 'left',
                    borderBottom: '2px solid #dee2e6',
                    fontWeight: '600',
                    color: '#495057'
                  }}>Description</th>
                </tr>
              </thead>
              <tbody>
                {selectedAlgorithms.map((algo, index) => (
                  <tr key={algo.value} style={{
                    backgroundColor: index % 2 === 0 ? '#f8f9fa' : 'white'
                  }}>
                    <td style={{
                      padding: '12px 15px',
                      borderBottom: '1px solid #dee2e6',
                      fontWeight: '500',
                      color: '#212529'
                    }}>{algo.label}</td>
                    <td style={{
                      padding: '12px 15px',
                      borderBottom: '1px solid #dee2e6',
                      textAlign: 'center'
                    }}>
                      <span style={{
                        padding: '4px 8px',
                        borderRadius: '12px',
                        fontSize: '0.8em',
                        fontWeight: '500',
                        backgroundColor: algo.value.includes('json') || algo.value.includes('_') ? '#d4edda' : '#cce5ff',
                        color: algo.value.includes('json') || algo.value.includes('_') ? '#155724' : '#0056b3'
                      }}>
                        {algo.value.includes('json') || algo.value.includes('_') ? 'JSON' : 'Python'}
                      </span>
                    </td>
                    <td style={{
                      padding: '12px 15px',
                      borderBottom: '1px solid #dee2e6',
                      color: '#6c757d',
                      fontSize: '0.9em'
                    }}>
                      {getAlgorithmDescription(algo.value)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      <div className="dashboard-panel">
        <ControlPanel 
          onRunSimulation={handleRunSimulation} 
          onRunComparison={handleRunComparison} 
          isLoading={isLoading}
          onAlgorithmSelectionChange={handleAlgorithmSelectionChange}
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