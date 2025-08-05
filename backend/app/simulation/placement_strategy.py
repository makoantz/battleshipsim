import random
from typing import List, Optional

# Import the main game engine class and type hints
from .game_engine import BattleshipGame, ShipConfiguration, Grid

class PlacementStrategy:
    """
    A factory class for creating BattleshipGame instances based on a chosen strategy.

    This class centralizes the logic for handling different user-defined board setups,
    such as creating a new random board every time, using one fixed board for all
    simulations, or picking randomly from a user-provided set of boards.
    """

    @staticmethod
    def get_game_instance(
        strategy_id: str,
        board_size: int,
        ship_config: ShipConfiguration,
        fixed_placement_grid: Optional[Grid] = None,
        placement_set_grids: Optional[List[Grid]] = None
    ) -> BattleshipGame:
        """
        Main factory method to generate a BattleshipGame instance.

        Args:
            strategy_id (str): The identifier for the strategy to use.
                               Expected values: 'random_each_round', 'fixed_for_all_rounds',
                               'random_from_set'.
            board_size (int): The dimension of the board.
            ship_config (ShipConfiguration): The list of ship definitions.
            fixed_placement_grid (Optional[Grid]): The single grid to use for the
                                                   'fixed_for_all_rounds' strategy.
            placement_set_grids (Optional[List[Grid]]): The list of grids to choose
                                                        from for the 'random_from_set' strategy.

        Returns:
            A BattleshipGame instance configured according to the chosen strategy.
        """
        if strategy_id == 'random_each_round':
            return PlacementStrategy._create_from_random(board_size, ship_config)

        if strategy_id == 'fixed_for_all_rounds':
            if not fixed_placement_grid:
                raise ValueError("A 'fixed_placement_grid' must be provided for this strategy.")
            return PlacementStrategy._create_from_fixed_grid(board_size, ship_config, fixed_placement_grid)

        if strategy_id == 'random_from_set':
            if not placement_set_grids or not placement_set_grids:
                raise ValueError("A 'placement_set_grids' list must be provided for this strategy.")
            return PlacementStrategy._create_from_random_set(board_size, ship_config, placement_set_grids)

        raise ValueError(f"Unknown placement strategy ID: '{strategy_id}'")

    @staticmethod
    def _create_from_random(board_size: int, ship_config: ShipConfiguration) -> BattleshipGame:
        """Creates a game with a new, fully random ship layout."""
        # The default behavior of the BattleshipGame constructor is to randomize the board.
        return BattleshipGame(board_size=board_size, ship_config=ship_config)

    @staticmethod
    def _create_from_fixed_grid(board_size: int, ship_config: ShipConfiguration, grid: Grid) -> BattleshipGame:
        """Creates a game instance using a predefined, fixed grid."""
        # Create a game instance, but we will override its generated board.
        game = BattleshipGame(board_size=board_size, ship_config=ship_config)

        # Manually set the solution grid to the one provided by the user.
        game.solution_grid = grid

        # CRITICAL: Recalculate the total number of ship segments based on the
        # provided grid, otherwise the game's win condition will be incorrect.
        total_segments = sum(1 for r in range(board_size) for c in range(board_size) if grid[r][c] is not None)
        game.total_ship_segments = total_segments
        
        # Ensure the hit count is reset to zero.
        game.hits_made = 0
        
        return game

    @staticmethod
    def _create_from_random_set(board_size: int, ship_config: ShipConfiguration, grids: List[Grid]) -> BattleshipGame:
        """Creates a game by randomly selecting one grid from a provided set."""
        # Randomly choose one of the boards from the user-defined set.
        selected_grid = random.choice(grids)
        
        # Once a grid is selected, the logic is identical to creating a fixed board.
        return PlacementStrategy._create_from_fixed_grid(board_size, ship_config, selected_grid)