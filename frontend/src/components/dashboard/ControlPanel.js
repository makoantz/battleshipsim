import React, { useState, useEffect } from 'react';
import { getAlgorithms } from '../../api/simulationService';
import './ControlPanel.css';

function ControlPanel({ onRunSimulation, isLoading }) {
  // State for the list of algorithms fetched from the backend
  const [algorithms, setAlgorithms] = useState([]);
  
  // State for the user's selections in the form
  const [selectedAlgorithm, setSelectedAlgorithm] = useState('');
  const [numSimulations, setNumSimulations] = useState(1000);
  // For now, we only support the 'random_each_round' strategy in the UI
  const [placementStrategy, setPlacementStrategy] = useState('random_each_round');

  // useEffect hook to fetch algorithms when the component first mounts
  useEffect(() => {
    const fetchAlgorithms = async () => {
      try {
        const fetchedAlgorithms = await getAlgorithms();
        setAlgorithms(fetchedAlgorithms);
        // Set the default selected algorithm to the first one in the list
        if (fetchedAlgorithms.length > 0) {
          setSelectedAlgorithm(fetchedAlgorithms[0].id);
        }
      } catch (error) {
        console.error("Failed to fetch algorithms:", error);
        // Optionally, display an error message in the UI
      }
    };

    fetchAlgorithms();
  }, []); // The empty dependency array [] means this effect runs only once

  const handleSubmit = (event) => {
    event.preventDefault(); // Prevent the form from causing a page reload
    
    // Bundle up the user's selections into a parameters object
    const simulationParams = {
      algorithm: selectedAlgorithm,
      num_simulations: Number(numSimulations),
      ship_placement_strategy: placementStrategy,
      // We'll add custom ship configs later
    };
    
    // Call the function passed down from the Dashboard component
    onRunSimulation(simulationParams);
  };

  return (
    <div className="control-panel">
      <h2>Control Panel</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="algorithm-select">Targeting Algorithm:</label>
          <select
            id="algorithm-select"
            value={selectedAlgorithm}
            onChange={(e) => setSelectedAlgorithm(e.target.value)}
            disabled={isLoading}
          >
            {algorithms.map((algo) => (
              <option key={algo.id} value={algo.id}>
                {algo.name}
              </option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="num-simulations-input">Number of Simulations:</label>
          <input
            id="num-simulations-input"
            type="number"
            value={numSimulations}
            onChange={(e) => setNumSimulations(e.target.value)}
            min="1"
            max="100000"
            disabled={isLoading}
          />
        </div>

        {/* We will expand this section later to include other strategies */}
        <div className="form-group">
          <label>Ship Placement:</label>
          <div className="radio-group">
            <label>
              <input 
                type="radio" 
                value="random_each_round"
                checked={true} // For now, this is the only option
                readOnly
              />
              Random for each round
            </label>
          </div>
        </div>

        <button type="submit" className="run-button" disabled={isLoading}>
          {isLoading ? 'Running...' : 'Run Simulation'}
        </button>
      </form>
    </div>
  );
}

export default ControlPanel;