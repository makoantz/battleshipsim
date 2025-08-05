"""
This file contains predefined ship configurations for the Battleship simulator.

Each configuration is a list of dictionaries, where each dictionary represents
a single ship. This structure is used throughout the application, from the
backend simulation engine to the frontend configurator.

The format for a single ship is:
{
    "name": str,                  # A user-friendly name for the ship.
    "shape": List[List[int]]      # A list of [row, col] offsets from a local
                                    anchor point [0, 0].
}

The 'shape' defines the geometry of the ship, allowing for both classic
linear ships and complex, non-linear modern ship designs.
"""
from typing import List, Dict, Any

# Define the ship type hint again for clarity within this module
Ship = Dict[str, Any]
ShipConfiguration = List[Ship]

# --- Default Classic Configuration ---
# This is the standard fleet used in the classic game of Battleship.
# It will be used by the simulator if no custom configuration is provided.
CLASSIC_SHIP_CONFIG: ShipConfiguration = [
    {
        "name": "Carrier",
        "shape": [[0, 0], [0, 1], [0, 2], [0, 3], [0, 4]]  # 1x5
    },
    {
        "name": "Battleship",
        "shape": [[0, 0], [0, 1], [0, 2], [0, 3]]          # 1x4
    },
    {
        "name": "Cruiser",
        "shape": [[0, 0], [0, 1], [0, 2]]                  # 1x3
    },
    {
        "name": "Submarine",
        "shape": [[0, 0], [0, 1], [0, 2]]                  # 1x3
    },
    {
        "name": "Destroyer",
        "shape": [[0, 0], [0, 1]]                          # 1x2
    }
]

# --- Example Modern Configuration ---
# An example of a non-standard fleet to demonstrate the simulator's flexibility.
# These shapes are non-linear and present a different challenge for targeting algorithms.
MODERN_SHIP_CONFIG: ShipConfiguration = [
    {
        "name": "Command Ship",
        "shape": [[0, 0], [0, 1], [1, 0], [1, 1]]          # 2x2 Block
    },
    {
        "name": "L-Patrol Ship",
        "shape": [[0, 0], [1, 0], [2, 0], [2, 1]]          # L-shape
    },
    {
        "name": "Asymmetrical Cruiser",
        "shape": [[0, 1], [1, 0], [1, 1], [1, 2]]          # T-like shape
    },
    {
        "name": "Scout Ship",
        "shape": [[0, 0], [1, 1]]                          # Diagonal 2-cell
    },
    {
        "name": "Single-Cell Buoy",
        "shape": [[0, 0]]                                  # 1x1
    }
]