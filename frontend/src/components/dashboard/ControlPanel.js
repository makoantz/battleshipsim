import React, { useState, useEffect } from 'react';
import { getAlgorithms } from '../../api/simulationService';
import './ControlPanel.css';

function ControlPanel({ onRunSimulation, onRunComparison, isLoading }) {
  // State for the full list of algorithms fetched from the backend
  const [allAlgorithms, setAllAlgorithms] = useState([]);
  
  // State to track which algorithms are selected, using a Set for efficiency
  const [selectedAlgorithms, setSelectedAlgorithms] = useState(new Set());
  
  // State for the other form inputs
  const [numSimulations, setNumSimulations] = useState(1000);
  const [placementStrategy, setPlacementStrategy] = useState('random_each_round');

  // Fetch the list of algorithms when the component first mounts
  useEffect(() => {
    const fetchAlgorithms = async () => {
      try {
        const fetchedAlgorithms = await getAlgorithms();
        setAllAlgorithms(fetchedAlgorithms);
      } catch (error) {
        console.error("Failed to fetch algorithms:", error);
      }
    };
    fetchAlgorithms();
  }, []); // Empty dependency array means this runs only once on mount

  // Handles toggling a checkbox on or off
  const handleAlgorithmToggle = (algoId) => {
    const newSelection = new Set(selectedAlgorithms);
    if (newSelection.has(algoId)) {
      newSelection.delete(algoId);
    } else {
      newSelection.add(algoId);
    }
    setSelectedAlgorithms(newSelection);
  };

  const handleSubmit = (event) => {
    event.preventDefault(); // Prevent default form submission
    
    const selectedList = Array.from(selectedAlgorithms);
    if (selectedList.length === 0) {
      alert("Please select at least one algorithm.");
      return;
    }
    
    // Common parameters for both single and comparison runs
    const params = {
      num_simulations: Number(numSimulations),
      ship_placement_strategy: placementStrategy,
    };

    // Decide which function to call based on the number of selected algorithms
    if (selectedList.length === 1) {
      onRunSimulation({ ...params, algorithm: selectedList[0] });
    } else {
      onRunComparison({ ...params, algorithms: selectedList });
    }
  };

  return (
    <div className="control-panel">
      <h2>Control Panel</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Targeting Algorithm(s):</label>
          <div className="checkbox-group">
            {allAlgorithms.map((algo) => (
              <label key={algo.id} className="checkbox-label">
                <input
                  type="checkbox"
                  checked={selectedAlgorithms.has(algo.id)}
                  onChange={() => handleAlgorithmToggle(algo.id)}
                  disabled={isLoading}
                />
                {algo.name}
              </label>
            ))}
          </div>
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

        <div className="form-group">
          <label>Ship Placement:</label>
          <div className="radio-group">
            <label>
              <input 
                type="radio" 
                value="random_each_round"
                checked={true}
                readOnly
              />
              Random for each round
            </label>
          </div>
        </div>

        <button type="submit" className="run-button" disabled={isLoading || selectedAlgorithms.size === 0}>
          {isLoading ? 'Running...' : `Run Simulation (${selectedAlgorithms.size})`}
        </button>
      </form>
    </div>
  );
}

export default ControlPanel;