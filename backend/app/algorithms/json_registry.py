import os
import json
from typing import Dict, List, Any

from app.algorithms.generic_algorithm import GenericAlgorithm
from app.algorithms.base import TargetingAlgorithm, ShipConfiguration

JSON_ALGORITHM_REGISTRY: Dict[str, Dict[str, Any]] = {}

def discover_json_algorithms():
    """
    Discovers and registers all algorithms defined in .json files.
    """
    # Correctly locate the json_algorithms directory relative to this file
    # __file__ -> .../backend/app/algorithms/json_registry.py
    # os.path.dirname(__file__) -> .../backend/app/algorithms
    # The target is .../backend/app/json_algorithms
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_algos_path = os.path.join(current_dir, '..', 'json_algorithms')

    if not os.path.exists(json_algos_path):
        print(f"Warning: JSON algorithm directory not found at {json_algos_path}")
        return

    for filename in os.listdir(json_algos_path):
        if filename.endswith(".json"):
            algo_id = os.path.splitext(filename)[0]
            filepath = os.path.join(json_algos_path, filename)

            with open(filepath, 'r') as f:
                try:
                    json_config = json.load(f)
                    algo_name = json_config.get("name", algo_id)

                    JSON_ALGORITHM_REGISTRY[algo_id] = {
                        "name": algo_name,
                        "config": json_config
                    }
                    print(f"Discovered and registered JSON algorithm: id='{algo_id}', name='{algo_name}'")
                except json.JSONDecodeError:
                    print(f"Warning: Could not parse JSON from file: {filename}")
                except Exception as e:
                    print(f"Error loading JSON algorithm {filename}: {e}")

def get_json_algorithm_instance(algo_id: str, board_size: int, ship_config: ShipConfiguration) -> TargetingAlgorithm:
    """
    Factory function to create an instance of a registered JSON-based algorithm.
    """
    if algo_id not in JSON_ALGORITHM_REGISTRY:
        raise ValueError(f"Unknown JSON algorithm ID: '{algo_id}'")

    algo_config = JSON_ALGORITHM_REGISTRY[algo_id]['config']
    # Pass the necessary arguments to the GenericAlgorithm constructor
    return GenericAlgorithm(board_size=board_size, ship_config=ship_config, algorithm_json=algo_config)

def get_available_json_algorithms() -> List[Dict[str, str]]:
    """
    Returns a list of available JSON-based algorithms, formatted for API responses.
    """
    return sorted(
        [
            {"id": key, "name": value["name"]}
            for key, value in JSON_ALGORITHM_REGISTRY.items()
        ],
        key=lambda x: x['name']
    )

# --- Initial Discovery ---
# This runs when the module is imported, populating the registry.
discover_json_algorithms()
