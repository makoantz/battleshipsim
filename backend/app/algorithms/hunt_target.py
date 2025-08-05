import random
from typing import List, Tuple, Set

# Import the base class and type hints
from .base import TargetingAlgorithm, BoardState, HitHistory

class HuntAndTarget(TargetingAlgorithm):
    """
    An algorithm that uses a two-stage Hunt/Target strategy.

    - In 'HUNT' mode, it uses a checkerboard (parity) pattern to find ships
      efficiently. It only shoots at every other square, guaranteeing that it
      will find any ship, as the smallest ship is 2 squares long.

    - Once a shot is a 'HIT', it switches to 'TARGET' mode. It then builds a
      list of priority targets around the hit and explores them to sink the
      ship. Once the ship is believed to be sunk (no more priority targets),
      it reverts to 'HUNT' mode.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mode = 'HUNT'
        self.hunt_targets: List[Tuple[int, int]] = []
        self.priority_targets: List[Tuple[int, int]] = []
        # Use a set for active hits for efficient lookup
        self.active_hits: Set[Tuple[int, int]] = set()
        self.reset()

    @property
    def name(self) -> str:
        return "Hunt and Target"

    def reset(self):
        """Resets the algorithm to its initial state for a new game."""
        self.mode = 'HUNT'
        self.priority_targets.clear()
        self.active_hits.clear()

        # Generate checkerboard targets
        self.hunt_targets = [
            (r, c) for r in range(self.board_size) for c in range(self.board_size)
            if (r + c) % 2 == 0  # Black squares
        ]
        random.shuffle(self.hunt_targets)
        # Add the other half (white squares) in shuffled order to the end
        # This is a fallback in case all ships are on white squares only
        white_squares = [
            (r, c) for r in range(self.board_size) for c in range(self.board_size)
            if (r + c) % 2 != 0
        ]
        random.shuffle(white_squares)
        self.hunt_targets.extend(white_squares)

    def _is_valid_and_unknown(self, r: int, c: int, board_state: BoardState) -> bool:
        """Checks if a coordinate is within board bounds and is 'UNKNOWN'."""
        return 0 <= r < self.board_size and 0 <= c < self.board_size and board_state[r][c] == 'UNKNOWN'

    def _update_state(self, hit_history: HitHistory, board_state: BoardState):
        """Synchronizes the algorithm's state based on the latest game info."""
        newly_found_hits = set(hit_history) - self.active_hits
        if newly_found_hits:
            self.mode = 'TARGET'
            for hit in newly_found_hits:
                self.active_hits.add(hit)
                r, c = hit
                # Add adjacent squares to priority targets
                potential_targets = [(r-1, c), (r+1, c), (r, c-1), (r, c+1)]
                for pr, pc in potential_tickets:
                    if self._is_valid_and_unknown(pr, pc, board_state):
                        if (pr, pc) not in self.priority_targets:
                            self.priority_targets.append((pr, pc))

        # If we are in target mode but have no more priority targets,
        # it implies the ship(s) have been sunk. Revert to hunt mode.
        if self.mode == 'TARGET' and not self.priority_targets:
            self.mode = 'HUNT'
            self.active_hits.clear() # Clear hits as we assume they form a sunk ship

    def next_shot(self, current_board_state: BoardState, hit_history: HitHistory) -> Tuple[int, int]:
        """Determines the next shot based on the current mode."""
        self._update_state(hit_history, current_board_state)

        # In Target mode, always prioritize sinking the known ship
        if self.mode == 'TARGET':
            # Pop from the end of the list (LIFO stack behavior)
            return self.priority_targets.pop()

        # In Hunt mode, find the next valid hunt target
        while self.hunt_targets:
            shot = self.hunt_targets.pop()
            # We must check if the spot is UNKNOWN, as it might have been
            # revealed as part of sinking a ship found on a 'white' square.
            if current_board_state[shot[0]][shot[1]] == 'UNKNOWN':
                return shot

        # Fallback in case hunt_targets is exhausted (should not happen in a valid game)
        raise ValueError("No valid hunt targets left.")