import random
from typing import List, Dict, Any, Tuple, Set

# Import the predefined ship configuration types
from .ship_configs import Ship, ShipConfiguration, CLASSIC_SHIP_CONFIG

# Define type hints for clarity
Grid = List[List[Any]]
Coordinate = Tuple[int, int]

class BattleshipGame:
    """
    Manages the state and logic for a single game of Battleship.
    """
    def __init__(self, board_size: int = 10, ship_config: ShipConfiguration = None):
        self.board_size = board_size
        self.ship_config = ship_config if ship_config is not None else CLASSIC_SHIP_CONFIG
        
        # --- THIS IS THE FIX ---
        # `solution_grid` is the pristine "answer key" and is NEVER modified after placement.
        self.solution_grid: Grid = []
        # `tracking_grid` represents the game in progress, storing 'HIT' markers.
        self.tracking_grid: Grid = []
        
        self.total_ship_segments = 0
        self.hits_made = 0
        
        self.reset()

    def reset(self):
        """
        Resets the game to a new, clean state for another run.
        """
        # --- THIS IS THE FIX ---
        # Initialize both the solution and tracking grids.
        self.solution_grid = [[None for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.tracking_grid = [[None for _ in range(self.board_size)] for _ in range(self.board_size)]

        self.hits_made = 0
        self.total_ship_segments = sum(len(ship['shape']) for ship in self.ship_config)
        self._place_ships()

    @property
    def is_game_over(self) -> bool:
        """Returns True if all ship segments have been hit."""
        return self.hits_made >= self.total_ship_segments

    def take_shot(self, r: int, c: int) -> str:
        """
        Processes a shot at a given coordinate.
        It CHECKS the solution_grid but only MODIFIES the tracking_grid.
        """
        # --- THIS IS THE FIX ---
        # Check for a ship in the pristine solution_grid.
        if self.solution_grid[r][c] is not None:
            # Prevent counting the same hit twice by checking the tracking_grid.
            if self.tracking_grid[r][c] != 'HIT':
                self.tracking_grid[r][c] = 'HIT' # Mark the hit on the tracking grid
                self.hits_made += 1
            return 'HIT'
        else:
            self.tracking_grid[r][c] = 'MISS'
            return 'MISS'

    def _get_random_orientation(self, shape: List[Coordinate]) -> List[Coordinate]:
        """Applies a random rotation and/or flip to a ship's shape."""
        transformed_shape = shape
        if random.choice([True, False]):
            transformed_shape = [(-r, c) for r, c in transformed_shape]
        if random.choice([True, False]):
            transformed_shape = [(r, -c) for r, c in transformed_shape]
        rotations = random.randint(0, 3)
        for _ in range(rotations):
            transformed_shape = [(-c, r) for r, c in transformed_shape]
        return transformed_shape

    def _place_ships(self):
        """
        Places all ships from the configuration onto the solution grid.
        This method is unchanged.
        """
        max_placement_attempts = 1000
        for ship in self.ship_config:
            is_placed = False
            for _ in range(max_placement_attempts):
                oriented_shape = self._get_random_orientation(ship['shape'])
                min_r, max_r = min(r for r,c in oriented_shape), max(r for r,c in oriented_shape)
                min_c, max_c = min(c for r,c in oriented_shape), max(c for r,c in oriented_shape)
                anchor_r = random.randint(-min_r, self.board_size - 1 - max_r)
                anchor_c = random.randint(-min_c, self.board_size - 1 - max_c)
                absolute_coords = [(anchor_r + r, anchor_c + c) for r, c in oriented_shape]
                if all(self.solution_grid[r][c] is None for r, c in absolute_coords):
                    for r, c in absolute_coords:
                        self.solution_grid[r][c] = ship['name']
                    is_placed = True
                    break
            if not is_placed:
                raise RuntimeError(f"Failed to place ship '{ship['name']}'.")