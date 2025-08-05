import random
from collections import deque
from typing import List, Tuple, Set

# Import the base class and type hints
from .base import TargetingAlgorithm, BoardState, HitHistory

class P2M2Enhanced(TargetingAlgorithm):
    """
    Implements the Enhanced P2M2 strategy with a checkerboard constraint.

    This algorithm fuses a systematic checkerboard hunt with the P2M2 targeting
    pattern, which naturally maintains parity.

    1. HUNT: A random parity (light/dark squares) is chosen. The hunt proceeds
       by firing only at squares of that parity, guaranteeing coverage.
    2. TARGET: Triggered on a hit. The logic follows a strict priority:
       - Priority 1 (Midpoint): If a P2M2 shot scores a hit, immediately
         target the midpoint between the two hits.
       - Priority 2 (P2M2): Fire at (+/-2, 0) and (0, +/-2). This naturally
         stays on the same checkerboard color as the hunt.
       - Priority 3 (Adjacent): If P2M2 is exhausted, fire at adjacent squares
         to handle touching ships.
       - If all patterns for a hit are exhausted, revert to the HUNT mode.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mode = 'HUNT'
        self.fired_shots: Set[Tuple[int, int]] = set()
        self.hunt_targets: List[Tuple[int, int]] = []
        self.chosen_parity = 0 # 0 for even/light, 1 for odd/dark

        self.priority_hits: deque[Tuple[int, int]] = deque()
        self.all_hits: Set[Tuple[int, int]] = set()
        
        # State variables for midpoint targeting
        self.last_hit_for_midpoint: Tuple[int, int] = None
        self.last_shot_was_p2m2_hit = False

        self.reset()

    @property
    def name(self) -> str:
        return "P2M2 Enhanced"

    def reset(self):
        """Resets the algorithm's state for a new game."""
        self.mode = 'HUNT'
        self.fired_shots.clear()
        self.priority_hits.clear()
        self.all_hits.clear()
        self.last_hit_for_midpoint = None
        self.last_shot_was_p2m2_hit = False
        
        # At the start of a game, randomly choose which parity to hunt on
        self.chosen_parity = random.choice([0, 1])

        # Generate checkerboard targets based on the chosen parity
        primary_parity_squares = []
        secondary_parity_squares = []
        for r in range(self.board_size):
            for c in range(self.board_size):
                if (r + c) % 2 == self.chosen_parity:
                    primary_parity_squares.append((r, c))
                else:
                    secondary_parity_squares.append((r, c))
        
        random.shuffle(primary_parity_squares)
        random.shuffle(secondary_parity_squares)
        
        # Hunt the chosen parity first, with the other as a fallback
        self.hunt_targets = primary_parity_squares + secondary_parity_squares

    def _is_valid_and_unfired(self, r: int, c: int) -> bool:
        return 0 <= r < self.board_size and 0 <= c < self.board_size and (r, c) not in self.fired_shots

    def _update_state(self, hit_history: HitHistory):
        """Updates internal state based on the latest game info."""
        newly_found_hits = set(hit_history) - self.all_hits
        if newly_found_hits:
            if self.mode == 'HUNT':
                self.mode = 'TARGET'

            for hit in newly_found_hits:
                # Check if this new hit was the result of a P2M2 shot
                if self.last_hit_for_midpoint and (hit in self._get_p2m2_pattern(self.last_hit_for_midpoint)):
                    self.last_shot_was_p2m2_hit = True
                
                self.all_hits.add(hit)
                self.priority_hits.appendleft(hit)

    def _get_p2m2_pattern(self, origin: Tuple[int, int]) -> List[Tuple[int, int]]:
        r, c = origin
        return [(r + 2, c), (r - 2, c), (r, c + 2), (r, c - 2)]

    def _get_adjacent_pattern(self, origin: Tuple[int, int]) -> List[Tuple[int, int]]:
        r, c = origin
        return [(r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)]

    def next_shot(self, current_board_state: BoardState, hit_history: HitHistory) -> Tuple[int, int]:
        self._update_state(hit_history)

        if self.mode == 'TARGET' and not self.priority_hits:
            self.mode = 'HUNT'

        # --- HUNT MODE ---
        if self.mode == 'HUNT':
            while self.hunt_targets:
                shot = self.hunt_targets.pop()
                if shot not in self.fired_shots:
                    self.fired_shots.add(shot)
                    self.last_hit_for_midpoint = None
                    self.last_shot_was_p2m2_hit = False
                    return shot

        # --- TARGET MODE ---
        if self.mode == 'TARGET':
            while self.priority_hits:
                origin = self.priority_hits[0]  # Peek at the current hit
                
                # Priority 1: Midpoint Targeting
                if self.last_shot_was_p2m2_hit:
                    self.last_shot_was_p2m2_hit = False
                    last_hit = origin
                    prev_hit = self.last_hit_for_midpoint
                    mid_r, mid_c = (last_hit[0] + prev_hit[0]) // 2, (last_hit[1] + prev_hit[1]) // 2
                    if self._is_valid_and_unfired(mid_r, mid_c):
                        self.fired_shots.add((mid_r, mid_c))
                        return (mid_r, mid_c)

                # Priority 2: P2M2 Pattern (Parity Compliant)
                self.last_hit_for_midpoint = origin
                for shot in self._get_p2m2_pattern(origin):
                    if self._is_valid_and_unfired(*shot):
                        self.fired_shots.add(shot)
                        return shot

                # Priority 3: Traditional Adjacent Fallback (for touching ships)
                for shot in self._get_adjacent_pattern(origin):
                    if self._is_valid_and_unfired(*shot):
                        self.fired_shots.add(shot)
                        return shot

                # If all patterns are exhausted for this hit, remove it and process the next
                self.priority_hits.popleft()

        # Final Fallback: Should rarely be reached, but ensures no crashes
        while True:
            r, c = random.randint(0, self.board_size - 1), random.randint(0, self.board_size - 1)
            if (r, c) not in self.fired_shots:
                self.fired_shots.add((r, c))
                return r, c