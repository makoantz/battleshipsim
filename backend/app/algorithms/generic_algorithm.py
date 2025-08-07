import random
import copy
from collections import deque
from typing import List, Tuple, Dict, Any, Set

from .base import TargetingAlgorithm, BoardState, HitHistory, ShipConfiguration

class GenericAlgorithm(TargetingAlgorithm):
    """
    A generic targeting algorithm configured by a JSON object.
    It uses a state machine defined in the JSON to determine its behavior.
    """

    def __init__(self, board_size: int, ship_config: ShipConfiguration, algorithm_json: Dict[str, Any]):
        super().__init__(board_size, ship_config)
        self.config = algorithm_json
        self._name = self.config.get("name", "Generic JSON Algorithm")
        self.reset()

    @property
    def name(self) -> str:
        return self._name

    def reset(self):
        """Resets the algorithm's state according to the JSON configuration."""
        self.fired_shots: Set[Tuple[int, int]] = set()
        self.active_hits: Set[Tuple[int, int]] = set()
        self.last_shot_returned: Tuple[int, int] | None = None

        # Initialize queues
        self.queues: Dict[str, deque] = {name: deque() for name in self.config.get("queues", [])}

        # Initialize variables
        self.variables: Dict[str, Any] = copy.deepcopy(self.config.get("variables", {}))

        # Set initial state
        self.current_state: str = self.config["initial_state"]

        # Run on_entry actions for the initial state
        self._execute_on_entry_actions()

    def next_shot(self, current_board_state: BoardState, hit_history: HitHistory) -> Tuple[int, int]:
        # 1. Determine the result of the last shot
        last_shot_result = self._determine_last_shot_result(current_board_state)

        # 2. Update internal state based on new hits
        newly_found_hits = set(hit_history) - self.active_hits
        if newly_found_hits:
            self.active_hits.update(newly_found_hits)
            last_shot_result = "HIT" # Override if we found a new hit

        # 3. Check for state transitions based on the result
        self._check_transitions(last_shot_result, hit_history)

        # 4. Get the next shot from the current state's logic
        shot = self._get_next_shot_from_actions(hit_history)

        # 5. If no valid shot was produced, use a fallback
        if not shot or shot in self.fired_shots:
            shot = self._get_random_unfired_shot()

        # 6. Record the shot and return it
        self.fired_shots.add(shot)
        self.last_shot_returned = shot
        return shot

    def _determine_last_shot_result(self, board_state: BoardState) -> str | None:
        """Determines if the last shot was a MISS."""
        if self.last_shot_returned:
            r, c = self.last_shot_returned
            if board_state[r][c] == 'MISS':
                return 'MISS'
        return None

    def _check_transitions(self, last_shot_result: str | None, hit_history: HitHistory):
        state_config = self.config["states"].get(self.current_state, {})
        transitions = state_config.get("transitions", [])
        for transition in transitions:
            if self._evaluate_condition(transition["condition"], last_shot_result, hit_history):
                self.current_state = transition["next_state"]
                # Pass the last hit as context to the entry actions
                last_hit = hit_history[-1] if last_shot_result == "HIT" and hit_history else None
                self._execute_on_entry_actions(last_hit)
                break  # Assume only one transition per turn

    def _execute_on_entry_actions(self, last_hit: Tuple[int, int] | None = None):
        state_config = self.config["states"].get(self.current_state, {})
        on_entry_actions = state_config.get("on_entry", [])
        for action_config in on_entry_actions:
            self._execute_action(action_config, last_hit)

    def _get_next_shot_from_actions(self, hit_history: HitHistory) -> Tuple[int, int] | None:
        state_config = self.config["states"].get(self.current_state, {})
        actions = state_config.get("next_shot", [])

        last_hit = hit_history[-1] if hit_history else None

        for action_config in actions:
            if "condition" in action_config and not self._evaluate_condition(action_config["condition"], None, hit_history):
                continue

            potential_shot = self._execute_action(action_config, last_hit)
            if potential_shot and potential_shot not in self.fired_shots:
                return potential_shot
        return None

    def _execute_action(self, action_config: Dict[str, Any], last_hit: Tuple[int, int] | None) -> Tuple[int, int] | None:
        action = action_config["action"]

        if action == "pop_from_queue":
            queue = self.queues[action_config["queue"]]
            while queue:
                shot = queue.popleft()
                if shot not in self.fired_shots:
                    return shot
            return None

        elif action == "generate_random_shot":
            return self._get_random_unfired_shot()

        elif action == "generate_diagonal_hunt":
            path = self._generate_diagonal_hunt_paths()
            # For simplicity, using a fixed parity. A more robust implementation could randomize this.
            parity = 0
            filtered_path = [pos for pos in path if (pos[0] + pos[1]) % 2 == parity]
            self.queues[action_config["queue"]].extend(filtered_path)

        elif action == "generate_checkerboard_hunt":
            pattern = self._generate_checkerboard_pattern()
            self.queues[action_config["queue"]].extend(pattern)

        elif action == "increment_variable":
            self.variables[action_config["variable"]] += 1

        elif action == "add_adjacent_to_queue" and last_hit:
            r, c = last_hit
            shots = [(r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)]
            self._add_valid_shots_to_queue(shots, action_config["queue"])

        elif action == "add_p2m2_to_queue" and last_hit:
            r, c = last_hit
            shots = [(r - 2, c), (r + 2, c), (r, c - 2), (r, c + 2)]
            self._add_valid_shots_to_queue(shots, action_config["queue"])

        return None

    def _evaluate_condition(self, condition: Any, last_shot_result: str | None, hit_history: HitHistory) -> bool:
        if isinstance(condition, str):
            if condition == "on_hit": return last_shot_result == "HIT"
            if condition == "on_miss": return last_shot_result == "MISS"
            return False

        key, value = next(iter(condition.items()))
        if key == "queue_empty":
            return not self.queues.get(value)
        elif key == "variable_less_equal":
            return self.variables.get(value["name"], 0) <= value["value"]

        return False

    def _add_valid_shots_to_queue(self, shots: List[Tuple[int, int]], queue_name: str):
        for r, c in shots:
            if 0 <= r < self.board_size and 0 <= c < self.board_size and (r, c) not in self.fired_shots:
                self.queues[queue_name].append((r, c))

    def _get_random_unfired_shot(self) -> Tuple[int, int]:
        while True:
            r, c = random.randint(0, self.board_size - 1), random.randint(0, self.board_size - 1)
            if (r, c) not in self.fired_shots:
                return r, c

    def _generate_diagonal_hunt_paths(self) -> List[Tuple[int, int]]:
        paths = []
        for k in range(self.board_size * 2 - 1):
            path = []
            for r in range(self.board_size):
                c = k - r
                if 0 <= c < self.board_size:
                    path.append((r, c))
            if k % 2 == 1: path.reverse()
            paths.extend(path)
        return paths

    def _generate_checkerboard_pattern(self) -> List[Tuple[int, int]]:
        """Generates a randomized checkerboard pattern."""
        parity = random.choice([0, 1])
        primary_squares = [(r, c) for r in range(self.board_size) for c in range(self.board_size) if (r + c) % 2 == parity]
        secondary_squares = [(r, c) for r in range(self.board_size) for c in range(self.board_size) if (r + c) % 2 != parity]
        random.shuffle(primary_squares)
        random.shuffle(secondary_squares)
        return primary_squares + secondary_squares
