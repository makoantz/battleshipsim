import React from 'react';
import StatsTable from '../visualizations/StatsTable';
import ShotDistributionChart from '../visualizations/ShotDistributionChart';
import GameReplay from '../visualizations/GameReplay';

/**
 * A component to display the results of a simulation.
 * It can handle both single algorithm runs and comparison runs.
 * 
 * @param {Object} props - The component props.
 * @param {Object} props.resultData - The full result object from the API.
 * @param {string} props.resultType - The type of result ('single' or 'comparison').
 */
function ResultsDisplay({ resultData, resultType }) {
  // Do not render anything if there is no data
  if (!resultData) {
    return null;
  }

  // --- RENDER LOGIC FOR A SINGLE SIMULATION RUN ---
  if (resultType === 'single') {
    const algorithmName = resultData.simulation_parameters.algorithm;
    // Use optional chaining (?.) for safety, in case the sample_game data is missing
    const sampleGameData = resultData.visualizations?.sample_game;

    return (
      <div>
        <h2>Results for: <span className="algorithm-name">{algorithmName}</span></h2>
        
        <StatsTable stats={resultData.analysis.summary_stats} />
        <ShotDistributionChart histogramData={resultData.analysis.histogram} />
        
        {/* Only render the replay component if the data for it exists */}
        {sampleGameData && <GameReplay sampleGame={sampleGameData} />}
      </div>
    );
  }

  // --- RENDER LOGIC FOR A COMPARISON SIMULATION RUN ---
  if (resultType === 'comparison') {
    const { individual_results, comparison_analysis } = resultData;
    const algorithmIds = Object.keys(individual_results);

    return (
      <div>
        <h2>Comparison Results</h2>
        
        {/* Display the ANOVA test results at the top */}
        <div className="anova-results">
          <h3>ANOVA Test Results</h3>
          <p>
            This test checks if there is a statistically significant difference between the average
            performance of the selected algorithms. A p-value less than 0.05 typically indicates
            a significant difference.
          </p>
          <div className="anova-values">
            <span>F-statistic: <strong>{comparison_analysis.f_statistic.toFixed(4)}</strong></span>
            <span>p-value: <strong>{comparison_analysis.p_value.toExponential(4)}</strong></span>
          </div>
        </div>
        
        {/* Map over each algorithm's results and render its complete set of visualizations */}
        {algorithmIds.map((algoId) => {
          const result = individual_results[algoId];
          const sampleGameData = result.sample_game;
          
          return (
            <div key={algoId} className="result-group">
              <h3>Algorithm: <span className="algorithm-name">{result.algorithm_name || algoId}</span></h3>
              <StatsTable stats={result.summary_stats} />
              <ShotDistributionChart histogramData={result.histogram} />
              {sampleGameData && <GameReplay sampleGame={sampleGameData} />}
            </div>
          );
        })}
      </div>
    );
  }

  // Fallback in case of an unknown result type
  return null;
}

export default ResultsDisplay;