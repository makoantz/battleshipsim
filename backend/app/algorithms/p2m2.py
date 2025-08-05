import random
from collections import deque
from typing import List, Tuple, Set

from .base import TargetingAlgorithm, BoardState, HitHistory

class P2M2(TargetingAlgorithm):
    """
    Implements the P2M2 strategy with a SYSTEMATIC DIAGONAL hunt pattern.

    1. HUNT: Starts on a random edge and sweeps diagonally across the board,
       maintaining checkerboard parity. This is not random but a continuous path.
    2. P2M2 TARGET (First 4 Ships): On a hit, if it is one of the first four
       ships found, it uses the (x±2, y) and (x, y±2) pattern.
    3. TRADITIONAL TARGET (Ships 5+): After the fourth ship is found, it reverts
       to a simple adjacent-square targeting mode for all subsequent ships.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mode = 'HUNT'
        self.fired_shots: Set[Tuple[int, int]] = set()
        self.hunt_targets: deque[Tuple[int, int]] = deque()
        self.priority_targets: deque[Tuple[int, int]] = deque()
        self.active_hits: Set[Tuple[int, int]] = set()
        self.ships_found_count = 0
        self.reset()

    @property
    def name(self) -> str:
        return "P2M2 (Diagonal Hunt)"

    def _generate_diagonal_hunt_paths(self) -> List[Tuple[int, int]]:
        """Generates a systematic list of coordinates by sweeping diagonally."""
        paths = []
        # Generate diagonals from top-left to bottom-right
        for k in range(self.board_size * 2 - 1):
            path = []
            for r in range(self.board_size):
                c = k - r
                if 0 <= c < self.board_size:
                    path.append((r, c))
            # Reverse every other path for a sweeping "snake" motion
            if k % 2 == 1:
                path.reverse()
            paths.extend(path)
        return paths

    def reset(self):
        """Resets the algorithm's state for a new game."""
        self.mode = 'HUNT'
        self.fired_shots.clear()
        self.priority_targets.clear()
        self.active_hits.clear()
        self.ships_found_count = 0
        
        # Generate the systematic diagonal path
        diagonal_path = self._generate_diagonal_hunt_paths()
        
        # Start from a random edge square and order the hunt from there
        edge_squares = [
            (r, c) for r in range(self.board_size) for c in range(self.board_size) 
            if r == 0 or r == self.board_size - 1 or c == 0 or c == self.board_size - 1
        ]
        start_pos = random.choice(edge_squares)
        
        try:
            start_index = diagonal_path.index(start_pos)
            # Rotate the path so it starts at our random edge point
            ordered_path = diagonal_path[start_index:] + diagonal_path[:start_index]
        except ValueError:
            ordered_path = diagonal_path # Fallback

        # Filter the path by checkerboard parity for efficiency
        parity = (start_pos[0] + start_pos[1]) % 2
        self.hunt_targets = deque([pos for pos in ordered_path if (pos[0] + pos[1]) % 2 == parity])

    def _is_valid_and_unfired(self, r: int, c: int) -> bool:
        return 0 <= r < self.board_size and 0 <= c < self.board_size and (r, c) not in self.fired_shots

    def _update_state(self, hit_history: HitHistory):
        """Updates internal state based on the latest game info."""
        newly_found_hits = set(hit_history) - self.active_hits
        if newly_found_hits:
            if self.mode == 'HUNT':
                self.mode = 'TARGET'
                self.ships_found_count += 1

            for hit in newly_found_hits:
                self.active_hits.add(hit)
                # Add adjacent squares to priority queue for traditional targeting fallback
                r, c = hit
                self.priority_targets.extend([(r-1, c), (r+1, c), (r, c-1), (r, c+1)])
        
        if self.mode == 'TARGET' and not any(self._is_valid_and_unfired(*shot) for shot in self.priority_targets):
            self.mode = 'HUNT'
            self.active_hits.clear()
            self.priority_targets.clear()

    def next_shot(self, current_board_state: BoardState, hit_history: HitHistory) -> Tuple[int, int]:
        self._update_state(hit_history)

        if self.mode == 'TARGET':
            # Use P2M2 pattern only for the first 4 ships
            if self.ships_found_count <= 4:
                origin = list(self.active_hits)[-1] # Use most recent hit as origin
                r, c = origin
                p2m2_shots = [(r+2, c), (r-2, c), (r, c+2), (r, c-2)]
                for shot in p2m2_shots:
                    if self._is_valid_and_unfired(*shot):
                        self.fired_shots.add(shot)
                        return shot
            
            # Fallback to traditional adjacent targeting if P2M2 is exhausted or ship count > 4
            while self.priority_targets:
                shot = self.priority_targets.popleft()
                if self._is_valid_and_unfired(*shot):
                    self.fired_shots.add(shot)
                    return shot

        # If in HUNT mode or target queue is exhausted
        while self.hunt_targets:
            shot = self.hunt_targets.popleft()
            if not shot in self.fired_shots:
                self.fired_shots.add(shot)
                return shot
        
        # Ultimate fallback
        while True:
            r, c = random.randint(0, self.board_size - 1), random.randint(0, self.board_size - 1)
            if (r, c) not in self.fired_shots:
                self.fired_shots.add((r, c))
                return r, c