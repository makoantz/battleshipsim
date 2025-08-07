import React, { useState } from 'react';
import ControlPanel from './ControlPanel';
import ResultsDisplay from './ResultsDisplay';
import { runSimulation, runComparison } from '../../api/simulationService';
import './Dashboard.css';

function Dashboard() {
  const [results, setResults] = useState(null);
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

  const handleAlgorithmSelectionChange = (algorithms) => {
    setSelectedAlgorithms(algorithms);
  };

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

  // Debug: Always show test data
  const getPerformanceSummary = () => {
    console.log("Results:", results);
    console.log("ResultType:", resultType);
    
    if (!results) {
      // Return test data when no results
      return [
        {
          algorithm: "Test Algorithm 1",
          meanShots: "65.30",
          medianShots: 65,
          stdDev: "4.20",
          minShots: 45,
          maxShots: 85,
          totalSimulations: 1000
        },
        {
          algorithm: "P2M2 Optimized",
          meanShots: "62.10",
          medianShots: 62,
          stdDev: "3.80",
          minShots: 42,
          maxShots: 82,
          totalSimulations: 1000
        }
      ];
    }

    if (resultType === 'single') {
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
  console.log("Performance Summary:", performanceSummary);

  return (
    <div className="dashboard">
      {/* DEBUG: Force show table */}
      <div style={{
        position: 'relative',
        zIndex: 1000,
        backgroundColor: '#e8f5e8',
        border: '3px solid #28a745',
        borderRadius: '10px',
        padding: '20px',
        marginBottom: '25px',
        boxShadow: '0 4px 8px rgba(0,0,0,0.3)'
      }}>
        <h3 style={{
          color: '#155724',
          marginBottom: '20px',
          fontSize: '1.4em',
          textAlign: 'center',
          fontWeight: 'bold'
        }}>
          🎯 DEBUG: Performance Summary Table (Always Visible)
        </h3>
        <div style={{ overflowX: 'auto' }}>
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
                <th style={{ padding: '15px 12px', textAlign: 'left' }}>Algorithm</th>
                <th style={{ padding: '15px 12px', textAlign: 'center' }}>Mean Shots</th>
                <th style={{ padding: '15px 12px', textAlign: 'center' }}>Median</th>
                <th style={{ padding: '15px 12px', textAlign: 'center' }}>Std Dev</th>
                <th style={{ padding: '15px 12px', textAlign: 'center' }}>Min/Max</th>
                <th style={{ padding: '15px 12px', textAlign: 'center' }}>Simulations</th>
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
                    <td style={{ padding: '12px', borderBottom: '1px solid #dee2e6', textAlign: 'center', fontWeight: '600' }}>
                      {algo.meanShots}
                    </td>
                    <td style={{ padding: '12px', borderBottom: '1px solid #dee2e6', textAlign: 'center' }}>
                      {algo.medianShots}
                    </td>
                    <td style={{ padding: '12px', borderBottom: '1px solid #dee2e6', textAlign: 'center' }}>
                      {algo.stdDev}
                    </td>
                    <td style={{ padding: '12px', borderBottom: '1px solid #dee2e6', textAlign: 'center', fontSize: '0.9em' }}>
                      {algo.minShots} / {algo.maxShots}
                    </td>
                    <td style={{ padding: '12px', borderBottom: '1px solid #dee2e6', textAlign: 'center', fontSize: '0.9em' }}>
                      {algo.totalSimulations?.toLocaleString()}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
        <div style={{ marginTop: '15px', fontSize: '0.85em', color: '#6c757d', textAlign: 'center' }}>
          ⭐ = Your optimized algorithm | Lower mean shots = Better performance
        </div>
      </div>

      {selectedAlgorithms.length > 0 && (
        <div style={{
          backgroundColor: '#f8f9fa',
          border: '1px solid #dee2e6',
          borderRadius: '8px',
          padding: '20px',
          marginBottom: '20px'
        }}>
          <h3>📊 Selected Algorithms ({selectedAlgorithms.length})</h3>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
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
        {results && <ResultsDisplay resultData={results} resultType={resultType} />}
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
