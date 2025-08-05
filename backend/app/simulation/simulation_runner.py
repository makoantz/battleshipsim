import copy
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
    Orchestrates the execution of Battleship game simulations.
    Can run a batch for a single algorithm or a comparative run for multiple.
    """

    def __init__(self, simulation_params: Dict[str, Any]):
        """
        Initializes the runner with parameters from the user's request.
        """
        self.params = simulation_params
        self.board_size = self.params.get('board_size', 10)
        self.ship_config = self.params.get('ship_configuration', CLASSIC_SHIP_CONFIG)

    def run(self) -> SimulationResult:
        """
        Executes a simulation run for a SINGLE algorithm.
        """
        shots_per_game = []
        heat_map_grid = [[0 for _ in range(self.board_size)] for _ in range(self.board_size)]

        algorithm = get_algorithm_instance(
            algo_id=self.params['algorithm'],
            board_size=self.board_size,
            ship_config=self.ship_config
        )

        for _ in range(self.params['num_simulations']):
            game = PlacementStrategy.get_game_instance(
                strategy_id=self.params['ship_placement_strategy'],
                board_size=self.board_size,
                ship_config=self.ship_config,
                fixed_placement_grid=self.params.get('fixed_placements'),
                placement_set_grids=self.params.get('placement_set')
            )
            algorithm.reset()
            shot_count, game_shots = self._play_single_game(game, algorithm)
            shots_per_game.append(shot_count)
            for r, c in game_shots:
                heat_map_grid[r][c] += 1

        return {
            "shots_per_game": shots_per_game,
            "heat_map": heat_map_grid,
        }

    def run_comparison(self) -> Dict[str, SimulationResult]:
        """
        Runs a simulation comparing MULTIPLE algorithms side-by-side.
        Ensures each algorithm plays on an identical copy of the board per round.
        """
        # Initialize result containers for each algorithm
        results = {
            algo_id: {"shots_per_game": [], "heat_map": [[0] * self.board_size for _ in range(self.board_size)]}
            for algo_id in self.params['algorithms']
        }
        
        # Instantiate all selected algorithms
        algorithms = {
            algo_id: get_algorithm_instance(algo_id, self.board_size, self.ship_config)
            for algo_id in self.params['algorithms']
        }

        # Main simulation loop
        for _ in range(self.params['num_simulations']):
            # 1. Generate ONE game board to serve as the template for this round
            game_template = PlacementStrategy.get_game_instance(
                strategy_id=self.params['ship_placement_strategy'],
                board_size=self.board_size,
                ship_config=self.ship_config,
                fixed_placement_grid=self.params.get('fixed_placements'),
                placement_set_grids=self.params.get('placement_set')
            )
            
            # 2. Loop through each algorithm and have it play on a DEEP COPY of the board
            for algo_id, algorithm in algorithms.items():
                # deepcopy is essential to prevent one algorithm's moves from affecting another's
                game_instance = copy.deepcopy(game_template)
                algorithm.reset()
                
                shot_count, game_shots = self._play_single_game(game_instance, algorithm)
                
                # Store results for this specific algorithm
                results[algo_id]["shots_per_game"].append(shot_count)
                for r, c in game_shots:
                    results[algo_id]["heat_map"][r][c] += 1
        
        return results

    def _play_single_game(self, game: BattleshipGame, algorithm: Any) -> tuple[int, list]:
        """
        Manages the gameplay loop for one individual game. (This method is unchanged).
        """
        shots_fired_coords = []
        hit_history = []
        player_view = [['UNKNOWN' for _ in range(self.board_size)] for _ in range(self.board_size)]

        while not game.is_game_over:
            r, c = algorithm.next_shot(player_view, hit_history)

            if player_view[r][c] != 'UNKNOWN':
                print(f"Warning: Algorithm '{algorithm.name}' targeted an already known square ({r},{c}).")
                break

            shots_fired_coords.append((r, c))
            result = game.take_shot(r, c)
            
            player_view[r][c] = result
            if result == 'HIT':
                hit_history.append((r, c))

        return len(shots_fired_coords), shots_fired_coords