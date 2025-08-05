import random
from collections import Counter, deque
from typing import List, Tuple, Set

from .base import TargetingAlgorithm, BoardState, HitHistory

class P2M2STDirectional(TargetingAlgorithm):
    """
    The most advanced P2M2 implementation. It combines:
    1. A systematic diagonal checkerboard hunt.
    2. A multi-stage targeting system:
       - If 1 hit is found (and ships <= 4), it uses the P2M2 pattern.
       - If 2+ hits form a line, it ABANDONS P2M2 and switches to a purely
         linear targeting logic (filling gaps and targeting ends).
    3. The robust SmartTarget engine for hit clustering and sunk ship confirmation.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fired_shots: Set[Tuple[int, int]] = set()
        self.hunt_targets: deque[Tuple[int, int]] = deque()
        self.remaining_ships: Counter = Counter()
        self.target_groups: List[Set[Tuple[int, int]]] = []
        self.last_shot_coord: Tuple[int, int] = None
        self.ships_found_count = 0
        self.reset()

    @property
    def name(self) -> str:
        return "P2M2-ST (Directional)"

    def _generate_diagonal_hunt_paths(self) -> List[Tuple[int, int]]:
        paths = []
        for k in range(self.board_size * 2 - 1):
            path = []
            for r in range(self.board_size):
                c = k - r
                if 0 <= c < self.board_size: path.append((r, c))
            if k % 2 == 1: path.reverse()
            paths.extend(path)
        return paths

    def reset(self):
        self.fired_shots.clear()
        self.target_groups.clear()
        self.last_shot_coord = None
        self.ships_found_count = 0
        self.remaining_ships = Counter(len(ship['shape']) for ship in self.ship_config)
        diagonal_path = self._generate_diagonal_hunt_paths()
        edge_squares = [(r, c) for r in range(self.board_size) for c in range(self.board_size) if r == 0 or r == self.board_size - 1 or c == 0 or c == self.board_size - 1]
        start_pos = random.choice(edge_squares)
        try:
            start_index = diagonal_path.index(start_pos)
            ordered_path = diagonal_path[start_index:] + diagonal_path[:start_index]
        except ValueError:
            ordered_path = diagonal_path
        parity = (start_pos[0] + start_pos[1]) % 2
        self.hunt_targets = deque([pos for pos in ordered_path if (pos[0] + pos[1]) % 2 == parity])

    def _is_valid_and_unfired(self, r: int, c: int) -> bool:
        return 0 <= r < self.board_size and 0 <= c < self.board_size and (r, c) not in self.fired_shots

    def _get_p2m2_pattern(self, origin: Tuple[int, int]) -> List[Tuple[int, int]]:
        r, c = origin
        return [(r + 2, c), (r - 2, c), (r, c + 2), (r, c - 2)]

    def _get_adjacent_pattern(self, origin: Tuple[int, int]) -> List[Tuple[int, int]]:
        r, c = origin
        return [(r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)]

    def _update_target_groups(self, hit_history: HitHistory):
        all_current_hits = {hit for group in self.target_groups for hit in group}
        new_hits = set(hit_history) - all_current_hits
        if not new_hits: return
        # A new "ship" is considered found only when we get the first hit of a new cluster
        if not self.target_groups:
            self.ships_found_count += 1
        for r, c in new_hits:
            adjacent_groups_indices = []
            for i, group in enumerate(self.target_groups):
                for gr, gc in group:
                    if abs(r - gr) + abs(c - gc) == 1:
                        if i not in adjacent_groups_indices: adjacent_groups_indices.append(i)
                        break
            if not adjacent_groups_indices:
                self.target_groups.append({(r, c)})
            else:
                merged_group = {(r, c)}
                for i in sorted(adjacent_groups_indices, reverse=True):
                    merged_group.update(self.target_groups.pop(i))
                self.target_groups.append(merged_group)

    def _check_for_sunk_ships(self):
        sunk_groups_indices = []
        for i, group in enumerate(self.target_groups):
            candidates = self._get_target_candidates_for_group(group)
            is_boxed_in = not any(self._is_valid_and_unfired(*shot) for shot in candidates)
            if is_boxed_in:
                group_size = len(group)
                if group_size in self.remaining_ships and self.remaining_ships[group_size] > 0:
                    self.remaining_ships[group_size] -= 1
                    sunk_groups_indices.append(i)
        if sunk_groups_indices:
            for i in sorted(sunk_groups_indices, reverse=True):
                del self.target_groups[i]

    def _get_target_candidates_for_group(self, group: Set[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """The new, highly intelligent targeting logic."""
        # Case 1: Only one hit in the group. Use P2M2 or Adjacent based on ship count.
        if len(group) == 1:
            origin = list(group)[0]
            if self.ships_found_count <= 4:
                return self._get_p2m2_pattern(origin) + self._get_adjacent_pattern(origin) # P2M2 is priority
            else:
                return self._get_adjacent_pattern(origin) # Fallback for later ships

        # Case 2: Multiple hits. Infer direction.
        rows, cols = {r for r, c in group}, {c for r, c in group}
        min_r, max_r, min_c, max_c = min(rows), max(rows), min(cols), max(cols)

        # Subcase 2a: A clear horizontal line is formed.
        if len(rows) == 1:
            candidates = []
            # Priority 1: Fill any gaps
            for c in range(min_c + 1, max_c):
                if (min_r, c) not in group:
                    candidates.append((min_r, c))
            # Priority 2: Target the ends
            candidates.extend([(min_r, min_c - 1), (min_r, max_c + 1)])
            return candidates

        # Subcase 2b: A clear vertical line is formed.
        elif len(cols) == 1:
            candidates = []
            # Priority 1: Fill any gaps
            for r in range(min_r + 1, max_r):
                if (r, min_c) not in group:
                    candidates.append((r, min_c))
            # Priority 2: Target the ends
            candidates.extend([(min_r - 1, min_c), (max_r + 1, min_c)])
            return candidates
            
        # Subcase 2c: Complex shape (touching ships). Fall back to general patterns.
        else:
            if self.ships_found_count <= 4:
                return [s for h in group for s in self._get_p2m2_pattern(h)] + \
                       [s for h in group for s in self._get_adjacent_pattern(h)]
            else:
                return [s for h in group for s in self._get_adjacent_pattern(h)]

    def _get_shot(self, r, c):
        self.fired_shots.add((r, c))
        self.last_shot_coord = (r, c)
        return r, c

    def next_shot(self, current_board_state: BoardState, hit_history: HitHistory) -> Tuple[int, int]:
        if self.last_shot_coord and current_board_state[self.last_shot_coord[0]][self.last_shot_coord[1]] == 'MISS':
            self._check_for_sunk_ships()
        self._update_target_groups(hit_history)

        # TARGET LOGIC
        if self.target_groups:
            for group in sorted(self.target_groups, key=len):
                # The new helper function contains all the complex logic
                candidates = self._get_target_candidates_for_group(group)
                for r, c in candidates:
                    if self._is_valid_and_unfired(r, c):
                        return self._get_shot(r, c)
        
        # HUNT LOGIC
        while self.hunt_targets:
            r, c = self.hunt_targets.popleft()
            if self._is_valid_and_unfired(r, c):
                return self._get_shot(r, c)

        # FALLBACK LOGIC
        while True:
            r, c = random.randint(0, self.board_size - 1), random.randint(0, self.board_size - 1)
            if self._is_valid_and_unfired(r, c):
                return self._get_shot(r, c)