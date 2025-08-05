import random
from collections import Counter, deque
from typing import List, Tuple, Set

from .base import TargetingAlgorithm, BoardState, HitHistory

class P2M2Optimized(TargetingAlgorithm):
    """
    The definitive P2M2 implementation, featuring:
    1. A systematic diagonal checkerboard hunt.
    2. Adaptive Targeting: Uses P2M2 for exploration, but switches to linear
       targeting once a ship's orientation is known.
    3. Instant Sunk Detection: A sunk ship is identified and removed from targeting
       the moment the final hit is registered.
    4. Dead-Square Pruning: The algorithm will not fire at any square unless the
       surrounding space can fit the smallest remaining ship.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fired_shots: Set[Tuple[int, int]] = set()
        self.hunt_targets: deque[Tuple[int, int]] = deque()
        self.remaining_ships: Counter = Counter()
        self.target_groups: List[Set[Tuple[int, int]]] = []
        self.ships_found_count = 0
        self.reset()

    @property
    def name(self) -> str:
        return "P2M2 Optimized"

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
        self.ships_found_count = 0
        self.remaining_ships = Counter(len(ship['shape']) for ship in self.ship_config)
        diagonal_path = self._generate_diagonal_hunt_paths()
        edge_squares = [(r, c) for r in range(self.board_size) for c in range(self.board_size) if r == 0 or r == self.board_size - 1 or c == 0 or c == self.board_size - 1]
        start_pos = random.choice(edge_squares)
        try:
            start_index = diagonal_path.index(start_pos)
            ordered_path = diagonal_path[start_index:] + diagonal_path[:start_index]
        except ValueError: ordered_path = diagonal_path
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

    def _update_and_check_groups(self, hit_history: HitHistory):
        all_current_hits = {hit for group in self.target_groups for hit in group}
        new_hits = set(hit_history) - all_current_hits
        if not new_hits: return

        if not self.target_groups and new_hits:
            self.ships_found_count += 1
        
        for r, c in new_hits:
            adjacent_groups_indices = [i for i, group in enumerate(self.target_groups) if any(abs(r-gr) + abs(c-gc) == 1 for gr, gc in group)]
            if not adjacent_groups_indices:
                self.target_groups.append({(r, c)})
            else:
                merged_group = {(r, c)}
                for i in sorted(adjacent_groups_indices, reverse=True):
                    merged_group.update(self.target_groups.pop(i))
                self.target_groups.append(merged_group)

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

    def _is_space_large_enough(self, r: int, c: int) -> bool:
        """Checks if a ship can fit at this coordinate."""
        # --- THIS IS THE FIX ---
        # If the sum of remaining ship counts is 0, no ships are left.
        if sum(self.remaining_ships.values()) == 0:
            return False
            
        smallest_ship = min(self.remaining_ships.elements())

        h_space = 1
        for i in range(1, smallest_ship):
            if self._is_valid_and_unfired(r, c - i): h_space += 1
            else: break
        for i in range(1, smallest_ship):
            if self._is_valid_and_unfired(r, c + i): h_space += 1
            else: break
        if h_space >= smallest_ship: return True

        v_space = 1
        for i in range(1, smallest_ship):
            if self._is_valid_and_unfired(r - i, c): v_space += 1
            else: break
        for i in range(1, smallest_ship):
            if self._is_valid_and_unfired(r + i, c): v_space += 1
            else: break
        if v_space >= smallest_ship: return True

        return False

    def _get_target_candidates_for_group(self, group: Set[Tuple[int, int]]) -> List[Tuple[int, int]]:
        if len(group) == 1:
            origin = list(group)[0]
            if self.ships_found_count <= 4: return self._get_p2m2_pattern(origin) + self._get_adjacent_pattern(origin)
            else: return self._get_adjacent_pattern(origin)
        
        rows, cols = {r for r,c in group}, {c for r,c in group}
        min_r, max_r, min_c, max_c = min(rows), max(rows), min(cols), max(cols)
        
        if len(rows) == 1:
            candidates = [(min_r, c) for c in range(min_c + 1, max_c) if (min_r, c) not in group]
            candidates.extend([(min_r, min_c - 1), (min_r, max_c + 1)])
            return candidates
        elif len(cols) == 1:
            candidates = [(r, min_c) for r in range(min_r + 1, max_r) if (r, min_c) not in group]
            candidates.extend([(min_r - 1, min_c), (max_r + 1, min_c)])
            return candidates
        else:
            if self.ships_found_count <= 4:
                return [s for h in group for s in self._get_p2m2_pattern(h)] + \
                       [s for h in group for s in self._get_adjacent_pattern(h)]
            else:
                return [s for h in group for s in self._get_adjacent_pattern(h)]

    def _get_shot(self, r, c):
        self.fired_shots.add((r, c))
        return r, c

    def next_shot(self, current_board_state: BoardState, hit_history: HitHistory) -> Tuple[int, int]:
        self._update_and_check_groups(hit_history)

        if self.target_groups:
            for group in sorted(self.target_groups, key=len):
                candidates = self._get_target_candidates_for_group(group)
                for r, c in candidates:
                    if self._is_valid_and_unfired(r, c):
                        return self._get_shot(r, c)
        
        while self.hunt_targets:
            r, c = self.hunt_targets.popleft()
            if self._is_valid_and_unfired(r, c) and self._is_space_large_enough(r, c):
                return self._get_shot(r, c)

        all_squares = [(r, c) for r in range(self.board_size) for c in range(self.board_size)]
        random.shuffle(all_squares)
        for r, c in all_squares:
            if self._is_valid_and_unfired(r, c):
                return self._get_shot(r, c)
        
        return -1, -1