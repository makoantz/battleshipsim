import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.simulation.simulation_runner import SimulationRunner
from app.algorithms.registry import get_algorithm_instance

# A fixed grid to ensure both algorithms play the exact same game
FIXED_GRID = [
    [None, None, None, None, 'Destroyer', 'Destroyer', None, None, None, None],
    [None, None, None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, 'Carrier', None, None, None],
    [None, 'Cruiser', 'Cruiser', 'Cruiser', None, None, 'Carrier', None, None, None],
    ['Submarine', 'Submarine', 'Submarine', 'Battleship', None, None, 'Carrier', None, None, None],
    [None, None, None, 'Battleship', None, None, 'Carrier', None, None, None],
    [None, None, None, 'Battleship', None, None, 'Carrier', None, None, None],
    [None, None, None, 'Battleship', None, None, None, None, None, None],
]

def run_simulation(algo_id: str):
    """
    Runs a single simulation for the given algorithm ID using a fixed grid.
    """
    print(f"--- Running simulation for: {algo_id} ---")

    simulation_params = {
        'board_size': 10,
        'num_simulations': 1,
        'ship_placement_strategy': 'fixed_for_all_rounds',
        'algorithm': algo_id,
        'fixed_placements': FIXED_GRID, # Provide the fixed grid
    }

    runner = SimulationRunner(simulation_params)
    result = runner.run()

    print(f"--- Simulation finished for: {algo_id} ---")
    # Correctly access the shot count from the result
    shot_count = result['shots_per_game'][0]
    print(f"Shots taken: {shot_count}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python run_single_simulation.py <algorithm_id>")
        sys.exit(1)

    algorithm_id = sys.argv[1]
    run_simulation(algorithm_id)
