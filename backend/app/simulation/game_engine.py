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

    This class is responsible for:
    - Creating the game board.
    - Placing ships according to a given configuration, including rotations.
    - Processing shots and determining if they are hits or misses.
    - Tracking the game's state (e.g., if it's over).
    """
    def __init__(self, board_size: int = 10, ship_config: ShipConfiguration = None):
        """
        Initializes a new game of Battleship.

        Args:
            board_size (int): The dimension of the square game board.
            ship_config (ShipConfiguration): A list of ship definitions. If None,
                                             the classic configuration is used.
        """
        self.board_size = board_size
        self.ship_config = ship_config if ship_config is not None else CLASSIC_SHIP_CONFIG
        
        # The 'solution' grid where ships are actually placed.
        # 'None' represents water. A ship's name marks its segments.
        self.solution_grid: Grid = []
        
        self.total_ship_segments = 0
        self.hits_made = 0
        
        self.reset()

    def reset(self):
        """
        Resets the game to a new, clean state for another run.
        This involves clearing the board and placing the ships again.
        """
        self.solution_grid = [[None for _ in range(self.board_size)] for _ in range(self.board_size)]
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

        Args:
            r (int): The row of the shot.
            c (int): The column of the shot.

        Returns:
            str: 'HIT' if the shot hit a ship, 'MISS' otherwise.
        """
        if self.solution_grid[r][c] is not None:
            # Prevent counting the same hit twice
            if self.solution_grid[r][c] != 'HIT':
                self.solution_grid[r][c] = 'HIT'
                self.hits_made += 1
            return 'HIT'
        else:
            return 'MISS'

    def _get_random_orientation(self, shape: List[Coordinate]) -> List[Coordinate]:
        """Applies a random rotation and/or flip to a ship's shape."""
        transformed_shape = shape
        
        # Randomly flip
        if random.choice([True, False]):
            transformed_shape = [(-r, c) for r, c in transformed_shape] # Vertical flip
        if random.choice([True, False]):
            transformed_shape = [(r, -c) for r, c in transformed_shape] # Horizontal flip
            
        # Randomly rotate 0, 90, 180, or 270 degrees
        rotations = random.randint(0, 3)
        for _ in range(rotations):
            transformed_shape = [(-c, r) for r, c in transformed_shape] # 90-degree rotation
            
        return transformed_shape

    def _place_ships(self):
        """
        Places all ships from the configuration onto the solution grid.
        It attempts to place each ship with a random orientation and position.
        """
        max_placement_attempts = 1000 # Safety break for impossible configs

        for ship in self.ship_config:
            is_placed = False
            for _ in range(max_placement_attempts):
                # 1. Get a randomly oriented version of the ship shape
                oriented_shape = self._get_random_orientation(ship['shape'])
                
                # 2. Find the bounding box to select a valid anchor point
                min_r = min(r for r, c in oriented_shape)
                max_r = max(r for r, c in oriented_shape)
                min_c = min(c for r, c in oriented_shape)
                max_c = max(c for r, c in oriented_shape)
                
                # 3. Pick a random anchor coordinate on the board
                anchor_r = random.randint(-min_r, self.board_size - 1 - max_r)
                anchor_c = random.randint(-min_c, self.board_size - 1 - max_c)
                
                # 4. Calculate absolute coordinates and check for validity
                absolute_coords = [(anchor_r + r, anchor_c + c) for r, c in oriented_shape]
                
                if all(self.solution_grid[r][c] is None for r, c in absolute_coords):
                    # 5. If valid, place the ship and move to the next one
                    for r, c in absolute_coords:
                        self.solution_grid[r][c] = ship['name']
                    is_placed = True
                    break
            
            if not is_placed:
                raise RuntimeError(
                    f"Failed to place ship '{ship['name']}'. "
                    "Check if the board is too small or the ship configuration is impossible."
                )