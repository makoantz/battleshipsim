import React, { useState, useEffect } from 'react';
import Select from 'react-select';
import { getAlgorithms } from '../../api/simulationService';
import './ControlPanel.css';

function ControlPanel({ onRunSimulation, onRunComparison, isLoading }) {
  const [allAlgorithms, setAllAlgorithms] = useState([]);
  const [selectedAlgorithms, setSelectedAlgorithms] = useState([]);
  const [numSimulations, setNumSimulations] = useState(1000);
  const [placementStrategy, setPlacementStrategy] = useState('random_each_round');

  useEffect(() => {
    const fetchAlgorithms = async () => {
      try {
        const fetchedAlgorithms = await getAlgorithms();
        // Format for react-select
        const formattedAlgos = fetchedAlgorithms.map(algo => ({
          value: algo.id,
          label: algo.name
        }));
        setAllAlgorithms(formattedAlgos);
      } catch (error) {
        console.error("Failed to fetch algorithms:", error);
      }
    };
    fetchAlgorithms();
  }, []);

  const handleAlgorithmChange = (selectedOptions) => {
    setSelectedAlgorithms(selectedOptions || []);
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    const selectedList = selectedAlgorithms.map(opt => opt.value);
    if (selectedList.length === 0) {
      alert("Please select at least one algorithm.");
      return;
    }
    
    const params = {
      num_simulations: Number(numSimulations),
      ship_placement_strategy: placementStrategy,
    };

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
          <Select
            isMulti
            options={allAlgorithms}
            value={selectedAlgorithms}
            onChange={handleAlgorithmChange}
            className="react-select-container"
            classNamePrefix="react-select"
            placeholder="Search and select algorithms..."
            isDisabled={isLoading}
          />
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