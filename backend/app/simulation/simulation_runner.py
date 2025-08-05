from typing import Dict, List, Any

# Import the components this runner will orchestrate
from app.algorithms.registry import get_algorithm_instance
from app.simulation.game_engine import BattleshipGame
from app.simulation.placement_strategy import PlacementStrategy
from app.simulation.ship_configs import CLASSIC_SHIP_CONFIG

# Define type hints for the results structure
SimulationResult = Dict[str, Any]

class SimulationRunner:
    """
    Orchestrates the execution of a batch of Battleship game simulations.

    This class ties together the game engine, placement strategies, and targeting
    algorithms to run a specified number of games and collect performance data.
    """

    def __init__(self, simulation_params: Dict[str, Any]):
        """
        Initializes the runner with parameters from the user's request.

        Args:
            simulation_params (Dict[str, Any]): A dictionary containing all the
                settings for the simulation run, such as 'algorithm_id',
                'num_simulations', 'ship_placement_strategy', etc.
        """
        self.params = simulation_params
        self.board_size = self.params.get('board_size', 10)
        self.ship_config = self.params.get('ship_configuration', CLASSIC_SHIP_CONFIG)

    def run(self) -> SimulationResult:
        """
        Executes the entire simulation run from start to finish.

        Returns:
            A dictionary containing the raw results of the simulation.
        """
        shots_per_game = []
        heat_map_grid = [[0 for _ in range(self.board_size)] for _ in range(self.board_size)]

        # Get a single instance of the algorithm. We will call its reset() method for each game.
        algorithm = get_algorithm_instance(
            algo_id=self.params['algorithm'],
            board_size=self.board_size,
            ship_config=self.ship_config
        )

        for _ in range(self.params['num_simulations']):
            # 1. Get a game instance based on the chosen placement strategy
            game = PlacementStrategy.get_game_instance(
                strategy_id=self.params['ship_placement_strategy'],
                board_size=self.board_size,
                ship_config=self.ship_config,
                fixed_placement_grid=self.params.get('fixed_placements'),
                placement_set_grids=self.params.get('placement_set')
            )

            # 2. Reset the algorithm's state for the new game
            algorithm.reset()

            # 3. Play the game until it's over
            shot_count, game_shots = self._play_single_game(game, algorithm)
            
            # 4. Record the results from the completed game
            shots_per_game.append(shot_count)
            for r, c in game_shots:
                heat_map_grid[r][c] += 1

        return {
            "shots_per_game": shots_per_game,
            "heat_map": heat_map_grid,
        }

    def _play_single_game(self, game: BattleshipGame, algorithm: Any) -> tuple[int, list]:
        """
        Manages the gameplay loop for one individual game.

        Args:
            game (BattleshipGame): An initialized game instance.
            algorithm (TargetingAlgorithm): An initialized algorithm instance.

        Returns:
            A tuple containing:
            - The total number of shots fired in the game.
            - A list of the coordinates that were fired at.
        """
        shots_fired_coords = []
        hit_history = []
        player_view = [['UNKNOWN' for _ in range(self.board_size)] for _ in range(self.board_size)]

        while not game.is_game_over:
            # Get the next shot from the algorithm
            r, c = algorithm.next_shot(player_view, hit_history)

            # Ensure the algorithm isn't making a mistake (optional but good practice)
            if player_view[r][c] != 'UNKNOWN':
                # This indicates a flawed algorithm. We stop to prevent infinite loops.
                print(f"Warning: Algorithm '{algorithm.name}' targeted an already known square ({r},{c}).")
                # For robustness, we could try to get another shot, but for now we stop.
                break

            shots_fired_coords.append((r, c))
            result = game.take_shot(r, c)
            
            # Update the player's view of the board
            player_view[r][c] = result
            if result == 'HIT':
                hit_history.append((r, c))

        return len(shots_fired_coords), shots_fired_coords