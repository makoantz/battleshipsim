import pkgutil
import inspect
from typing import Dict, List, Type, Any

# Import the base class and types for checking and instantiation
from .base import TargetingAlgorithm, ShipConfiguration

# Import the JSON registry components
from .json_registry import get_available_json_algorithms, get_json_algorithm_instance, JSON_ALGORITHM_REGISTRY

# The global registry for classic, class-based algorithms.
ALGORITHM_REGISTRY: Dict[str, Dict[str, Any]] = {}


def discover_algorithms():
    """
    Dynamically discovers and registers all TargetingAlgorithm subclasses.
    This function scans the 'app.algorithms' package for Python-based algorithms.
    """
    import app.algorithms

    for _, module_name, _ in pkgutil.iter_modules(app.algorithms.__path__, prefix=app.algorithms.__name__ + '.'):
        # Skip the JSON registry module to prevent circular dependencies or unexpected behavior
        if 'json_registry' in module_name:
            continue

        module = __import__(module_name, fromlist=["*"])

        for _, member_class in inspect.getmembers(module, inspect.isclass):
            if (issubclass(member_class, TargetingAlgorithm) and
                    member_class is not TargetingAlgorithm and
                    member_class.__module__ == module.__name__):

                # Prevent registering the GenericAlgorithm class itself in this registry
                if member_class.__name__ == 'GenericAlgorithm':
                    continue

                algo_id = member_class.__name__.lower()
                temp_instance = member_class(board_size=10, ship_config=[])
                
                ALGORITHM_REGISTRY[algo_id] = {
                    "class": member_class,
                    "name": temp_instance.name
                }
                print(f"Discovered and registered Python algorithm: id='{algo_id}', name='{temp_instance.name}'")


def get_algorithm_instance(algo_id: str, board_size: int, ship_config: ShipConfiguration) -> TargetingAlgorithm:
    """
    Factory function to create an instance of any registered algorithm (Python or JSON).
    It first checks the classic Python algorithm registry, then the JSON registry.
    """
    # Try to get the instance from the classic registry first
    if algo_id in ALGORITHM_REGISTRY:
        algo_class: Type[TargetingAlgorithm] = ALGORITHM_REGISTRY[algo_id]['class']
        return algo_class(board_size=board_size, ship_config=ship_config)

    # If not found, try the JSON registry
    if algo_id in JSON_ALGORITHM_REGISTRY:
        return get_json_algorithm_instance(algo_id, board_size, ship_config)

    # If it's not in either, raise an error
    all_algos = list(ALGORITHM_REGISTRY.keys()) + list(JSON_ALGORITHM_REGISTRY.keys())
    raise ValueError(f"Unknown algorithm ID: '{algo_id}'. Available: {all_algos}")


def get_available_algorithms() -> List[Dict[str, str]]:
    """
    Returns a combined list of available algorithms (both Python and JSON),
    formatted for API responses.
    """
    # Get algorithms from the classic registry
    classic_algos = [
        {"id": key, "name": value["name"]}
        for key, value in ALGORITHM_REGISTRY.items()
    ]

    # Get algorithms from the JSON registry
    json_algos = get_available_json_algorithms()

    # Combine and sort the lists
    all_algorithms = classic_algos + json_algos
    return sorted(all_algorithms, key=lambda x: x['name'])

# --- Initial Discovery ---
# Run discovery for both types of algorithms when the app starts.
discover_algorithms()