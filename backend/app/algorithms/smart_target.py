import random
from collections import Counter, deque
from typing import List, Tuple, Set

from .base import TargetingAlgorithm, BoardState, HitHistory

class SmartTarget(TargetingAlgorithm):
    """
    Implements a highly efficient and robust Hunt/Target strategy.
    This version removes the 'no-fly zone' concept to optimize for scenarios
    with touching ships, preventing bimodal performance distributions.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fired_shots: Set[Tuple[int, int]] = set()
        self.hunt_targets: deque[Tuple[int, int]] = deque()
        self.remaining_ships: Counter = Counter()
        self.target_groups: List[Set[Tuple[int, int]]] = []
        self.last_shot_coord: Tuple[int, int] = None
        self.reset()

    @property
    def name(self) -> str:
        return "Smart Target"

    def reset(self):
        self.fired_shots.clear()
        self.target_groups.clear()
        self.last_shot_coord = None
        self.remaining_ships = Counter(len(ship['shape']) for ship in self.ship_config)
        parity = random.choice([0, 1])
        primary_squares = [(r, c) for r in range(self.board_size) for c in range(self.board_size) if (r + c) % 2 == parity]
        secondary_squares = [(r, c) for r in range(self.board_size) for c in range(self.board_size) if (r + c) % 2 != parity]
        random.shuffle(primary_squares)
        random.shuffle(secondary_squares)
        self.hunt_targets = deque(primary_squares + secondary_squares)

    def _is_valid_and_unfired(self, r: int, c: int) -> bool:
        return 0 <= r < self.board_size and 0 <= c < self.board_size and (r, c) not in self.fired_shots

    def _get_adjacent_pattern(self, origin: Tuple[int, int]) -> List[Tuple[int, int]]:
        r, c = origin
        return [(r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)]

    def _update_target_groups(self, hit_history: HitHistory):
        all_current_hits = {hit for group in self.target_groups for hit in group}
        new_hits = set(hit_history) - all_current_hits
        if not new_hits: return
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
        if len(group) == 1:
            return self._get_adjacent_pattern(list(group)[0])
        else:
            rows, cols = {r for r, c in group}, {c for r, c in group}
            min_r, max_r, min_c, max_c = min(rows), max(rows), min(cols), max(cols)
            if len(rows) == 1: return [(min_r, min_c - 1), (min_r, max_c + 1)]
            elif len(cols) == 1: return [(min_r - 1, min_c), (max_r + 1, min_c)]
            else:
                all_adj = {adj for hit in group for adj in self._get_adjacent_pattern(hit)}
                return [shot for shot in all_adj if shot not in group]

    def _get_shot(self, r, c):
        self.fired_shots.add((r, c))
        self.last_shot_coord = (r, c)
        return r, c

    def next_shot(self, current_board_state: BoardState, hit_history: HitHistory) -> Tuple[int, int]:
        if self.last_shot_coord and current_board_state[self.last_shot_coord[0]][self.last_shot_coord[1]] == 'MISS':
            self._check_for_sunk_ships()
        self._update_target_groups(hit_history)

        if self.target_groups:
            for group in sorted(self.target_groups, key=len):
                for r, c in self._get_target_candidates_for_group(group):
                    if self._is_valid_and_unfired(r, c):
                        return self._get_shot(r, c)
        
        while self.hunt_targets:
            r, c = self.hunt_targets.popleft()
            if self._is_valid_and_unfired(r, c):
                return self._get_shot(r, c)

        while True:
            r, c = random.randint(0, self.board_size - 1), random.randint(0, self.board_size - 1)
            if self._is_valid_and_unfired(r, c):
                return self._get_shot(r, c)