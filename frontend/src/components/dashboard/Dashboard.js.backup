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

  // Extract performance summary from results
  const getPerformanceSummary = () => {
    if (!results) return [];

    if (resultType === 'single') {
      // Single algorithm result
      return [{
        algorithm: results.algorithm_name || results.algorithm,
        meanShots: results.mean_shots?.toFixed(2),
        medianShots: results.median_shots,
        stdDev: results.std_dev?.toFixed(2),
        minShots: results.min_shots,
        maxShots: results.max_shots,
        totalSimulations: results.total_simulations
      }];
    } else if (resultType === 'comparison' && results.algorithms) {
      // Multiple algorithm comparison
      return results.algorithms.map(algo => ({
        algorithm: algo.name,
        meanShots: algo.mean_shots?.toFixed(2),
        medianShots: algo.median_shots,
        stdDev: algo.std_dev?.toFixed(2),
        minShots: algo.min_shots,
        maxShots: algo.max_shots,
        totalSimulations: algo.total_simulations
      }));
    }

    return [];
  };

  const performanceSummary = getPerformanceSummary();

  return (
    <div className="dashboard">
      {/* Performance Summary Table */}
      {results && performanceSummary.length > 0 && (
        <div className="performance-summary" style={{
          backgroundColor: '#e8f5e8',
          border: '2px solid #28a745',
          borderRadius: '10px',
          padding: '20px',
          marginBottom: '25px',
          boxShadow: '0 4px 8px rgba(0,0,0,0.1)'
        }}>
          <h3 style={{
            color: '#155724',
            marginBottom: '20px',
            fontSize: '1.4em',
            textAlign: 'center',
            fontWeight: 'bold'
          }}>
            🎯 Performance Summary - All Algorithms
          </h3>
          <div className="performance-table-container" style={{ overflowX: 'auto' }}>
            <table style={{
              width: '100%',
              borderCollapse: 'collapse',
              backgroundColor: 'white',
              borderRadius: '8px',
              overflow: 'hidden',
              boxShadow: '0 2px 6px rgba(0,0,0,0.1)',
              border: '1px solid #dee2e6'
            }}>
              <thead>
                <tr style={{ backgroundColor: '#28a745', color: 'white' }}>
                  <th style={{
                    padding: '15px 12px',
                    textAlign: 'left',
                    fontWeight: '600',
                    fontSize: '0.9em'
                  }}>Algorithm</th>
                  <th style={{
                    padding: '15px 12px',
                    textAlign: 'center',
                    fontWeight: '600',
                    fontSize: '0.9em'
                  }}>Mean Shots</th>
                  <th style={{
                    padding: '15px 12px',
                    textAlign: 'center',
                    fontWeight: '600',
                    fontSize: '0.9em'
                  }}>Median</th>
                  <th style={{
                    padding: '15px 12px',
                    textAlign: 'center',
                    fontWeight: '600',
                    fontSize: '0.9em'
                  }}>Std Dev</th>
                  <th style={{
                    padding: '15px 12px',
                    textAlign: 'center',
                    fontWeight: '600',
                    fontSize: '0.9em'
                  }}>Min/Max</th>
                  <th style={{
                    padding: '15px 12px',
                    textAlign: 'center',
                    fontWeight: '600',
                    fontSize: '0.9em'
                  }}>Simulations</th>
                </tr>
              </thead>
              <tbody>
                {performanceSummary.map((algo, index) => {
                  const isP2M2Optimized = algo.algorithm.toLowerCase().includes('p2m2 optimized');
                  return (
                    <tr key={index} style={{
                      backgroundColor: index % 2 === 0 ? '#f8f9fa' : 'white',
                      borderLeft: isP2M2Optimized ? '4px solid #ffc107' : 'none'
                    }}>
                      <td style={{
                        padding: '12px',
                        borderBottom: '1px solid #dee2e6',
                        fontWeight: isP2M2Optimized ? '700' : '500',
                        color: isP2M2Optimized ? '#856404' : '#212529',
                        backgroundColor: isP2M2Optimized ? '#fff3cd' : 'inherit'
                      }}>
                        {isP2M2Optimized && '⭐ '}{algo.algorithm}
                      </td>
                      <td style={{
                        padding: '12px',
                        borderBottom: '1px solid #dee2e6',
                        textAlign: 'center',
                        fontWeight: '600',
                        color: '#495057'
                      }}>
                        {algo.meanShots}
                      </td>
                      <td style={{
                        padding: '12px',
                        borderBottom: '1px solid #dee2e6',
                        textAlign: 'center',
                        color: '#495057'
                      }}>
                        {algo.medianShots}
                      </td>
                      <td style={{
                        padding: '12px',
                        borderBottom: '1px solid #dee2e6',
                        textAlign: 'center',
                        color: '#495057'
                      }}>
                        {algo.stdDev}
                      </td>
                      <td style={{
                        padding: '12px',
                        borderBottom: '1px solid #dee2e6',
                        textAlign: 'center',
                        color: '#495057',
                        fontSize: '0.9em'
                      }}>
                        {algo.minShots} / {algo.maxShots}
                      </td>
                      <td style={{
                        padding: '12px',
                        borderBottom: '1px solid #dee2e6',
                        textAlign: 'center',
                        color: '#6c757d',
                        fontSize: '0.9em'
                      }}>
                        {algo.totalSimulations?.toLocaleString()}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          <div style={{
            marginTop: '15px',
            fontSize: '0.85em',
            color: '#6c757d',
            textAlign: 'center'
          }}>
            ⭐ = Your optimized algorithm | Lower mean shots = Better performance
          </div>
        </div>
      )}

      {/* Algorithm Selection Summary */}
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
            📊 Selected Algorithms ({selectedAlgorithms.length})
          </h3>
          <div className="selected-algorithms" style={{
            display: 'flex',
            flexWrap: 'wrap',
            gap: '10px'
          }}>
            {selectedAlgorithms.map((algo, index) => (
              <span key={index} style={{
                padding: '8px 12px',
                backgroundColor: '#e3f2fd',
                color: '#1565c0',
                borderRadius: '20px',
                fontSize: '0.9em',
                fontWeight: '500',
                border: '1px solid #bbdefb'
              }}>
                {algo.label}
              </span>
            ))}
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