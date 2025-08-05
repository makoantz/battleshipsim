import pkgutil
import inspect
from typing import Dict, List, Type, Any

# Import the base class and types for checking and instantiation
from .base import TargetingAlgorithm, ShipConfiguration

# The global registry. It will map a unique string ID to a dictionary
# containing the algorithm's class and its user-friendly name.
# e.g., {'huntandtarget': {'class': HuntAndTarget, 'name': 'Hunt and Target'}}
ALGORITHM_REGISTRY: Dict[str, Dict[str, Any]] = {}


def discover_algorithms():
    """
    Dynamically discovers and registers all TargetingAlgorithm subclasses.

    This function scans the 'app.algorithms' package, imports all modules within it,
    and finds any classes that inherit from TargetingAlgorithm. It populates
    the ALGORITHM_REGISTRY.

    This function should be called once when the application starts.
    """
    # Import the package where this code resides, using the full path from the root
    import app.algorithms

    # Iterate over all modules in the 'app.algorithms' package path
    for _, module_name, _ in pkgutil.iter_modules(app.algorithms.__path__, prefix=app.algorithms.__name__ + '.'):
        # Import the module dynamically
        module = __import__(module_name, fromlist=["*"])

        # Now, inspect the imported module for classes
        for _, member_class in inspect.getmembers(module, inspect.isclass):
            # Check three conditions:
            # 1. Is the member a subclass of our base class?
            # 2. Is it not the base class itself?
            # 3. Is it defined in the currently inspected module (prevents re-registering base class)
            if (issubclass(member_class, TargetingAlgorithm) and
                    member_class is not TargetingAlgorithm and
                    member_class.__module__ == module.__name__):

                # Use the lowercase class name as the unique ID
                algo_id = member_class.__name__.lower()

                # To get the friendly name, we must instantiate the class.
                # We assume the constructor can be called with dummy data.
                temp_instance = member_class(board_size=10, ship_config=[])
                
                ALGORITHM_REGISTRY[algo_id] = {
                    "class": member_class,
                    "name": temp_instance.name
                }
                print(f"Discovered and registered algorithm: id='{algo_id}', name='{temp_instance.name}'")


def get_algorithm_instance(algo_id: str, board_size: int, ship_config: ShipConfiguration) -> TargetingAlgorithm:
    """
    Factory function to create an instance of a registered algorithm.

    This is the primary way the simulation engine will get an algorithm object
    to work with.

    Args:
        algo_id (str): The unique ID of the algorithm (e.g., 'randomsearch').
        board_size (int): The board dimension to pass to the algorithm's constructor.
        ship_config (ShipConfiguration): The ship list to pass to the constructor.

    Returns:
        An instance of the requested TargetingAlgorithm subclass.

    Raises:
        ValueError: If the requested algo_id is not in the registry.
    """
    if algo_id not in ALGORITHM_REGISTRY:
        raise ValueError(f"Unknown algorithm ID: '{algo_id}'. Available: {list(ALGORITHM_REGISTRY.keys())}")

    algo_class: Type[TargetingAlgorithm] = ALGORITHM_REGISTRY[algo_id]['class']
    return algo_class(board_size=board_size, ship_config=ship_config)


def get_available_algorithms() -> List[Dict[str, str]]:
    """
    Returns a list of available algorithms, formatted for API responses.

    This is used to populate the dropdown menu on the frontend.

    Returns:
        A list of dictionaries, e.g., [{'id': 'huntandtarget', 'name': 'Hunt and Target'}]
    """
    # Sort the results alphabetically by the algorithm's friendly name for a better UX
    return sorted(
        [
            {"id": key, "name": value["name"]}
            for key, value in ALGORITHM_REGISTRY.items()
        ],
        key=lambda x: x['name']
    )

# --- Initial Discovery ---
# Run the discovery process as soon as this module is imported.
# This ensures the registry is populated when the app starts.
discover_algorithms()