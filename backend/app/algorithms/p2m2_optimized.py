import random
from collections import Counter, deque
from typing import List, Tuple, Set

from .base import TargetingAlgorithm, BoardState, HitHistory

class P2M2Optimized(TargetingAlgorithm):
    """
    Advanced Hybrid P2M2 implementation:
    1. Random checkerboard hunting (no diagonal)
    2. P2M2 + adjacent targeting on hits
    3. Immediate gap-filling for alternating hits (x,y) and (x+2,y)
    4. Space-aware targeting based on remaining ships
    5. Intelligent linear targeting with gap priority
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

    def _generate_random_checkerboard(self) -> List[Tuple[int, int]]:
        """Generate randomized checkerboard pattern for hunting."""
        checkerboard = []
        for r in range(self.board_size):
            for c in range(self.board_size):
                if (r + c) % 2 == 0:  # Checkerboard pattern
                    checkerboard.append((r, c))
        random.shuffle(checkerboard)  # Randomize order
        return checkerboard

    def reset(self):
        self.fired_shots.clear()
        self.target_groups.clear()
        self.ships_found_count = 0
        
        # Handle empty ship config gracefully (for registry discovery)
        if self.ship_config and len(self.ship_config) > 0:
            self.remaining_ships = Counter(len(ship['shape']) for ship in self.ship_config)
        else:
            # Default ship sizes for standard Battleship game
            self.remaining_ships = Counter({2: 1, 3: 2, 4: 1, 5: 1})
        
        # Use random checkerboard instead of diagonal
        self.hunt_targets = deque(self._generate_random_checkerboard())

    def _is_valid_and_unfired(self, r: int, c: int) -> bool:
        return 0 <= r < self.board_size and 0 <= c < self.board_size and (r, c) not in self.fired_shots

    def _get_p2m2_pattern(self, origin: Tuple[int, int]) -> List[Tuple[int, int]]:
        r, c = origin
        return [(r + 2, c), (r - 2, c), (r, c + 2), (r, c - 2)]

    def _get_adjacent_pattern(self, origin: Tuple[int, int]) -> List[Tuple[int, int]]:
        r, c = origin
        return [(r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)]

    def _is_space_large_enough_for_any_ship(self, r: int, c: int) -> bool:
        """Check if ANY remaining ship can fit at this coordinate."""
        if sum(self.remaining_ships.values()) == 0:
            return True  # If no ships info, assume it's fine
            
        # Get the smallest remaining ship size for efficiency
        min_ship_size = min(self.remaining_ships.keys()) if self.remaining_ships else 2
        
        # Quick check: can we fit the smallest ship horizontally?
        h_space = 1
        for i in range(1, min_ship_size):
            if self._is_valid_and_unfired(r, c - i): 
                h_space += 1
            else: 
                break
        for i in range(1, min_ship_size):
            if self._is_valid_and_unfired(r, c + i): 
                h_space += 1
            else: 
                break
        if h_space >= min_ship_size: 
            return True

        # Quick check: can we fit the smallest ship vertically?
        v_space = 1
        for i in range(1, min_ship_size):
            if self._is_valid_and_unfired(r - i, c): 
                v_space += 1
            else: 
                break
        for i in range(1, min_ship_size):
            if self._is_valid_and_unfired(r + i, c): 
                v_space += 1
            else: 
                break
        if v_space >= min_ship_size: 
            return True

        return False

    def _has_alternating_hit_pattern(self, group: Set[Tuple[int, int]]) -> bool:
        """Check if group has alternating hits like (x,y) and (x+2,y) or (x,y+2)."""
        if len(group) < 2:
            return False
        
        group_list = list(group)
        for i in range(len(group_list)):
            for j in range(i + 1, len(group_list)):
                r1, c1 = group_list[i]
                r2, c2 = group_list[j]
                # Check if hits are exactly 2 spaces apart horizontally or vertically
                if (abs(r1 - r2) == 2 and c1 == c2) or (abs(c1 - c2) == 2 and r1 == r2):
                    return True
        return False

    def _get_gap_filling_candidates(self, group: Set[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """Get gap-filling candidates for alternating hit patterns."""
        rows = {r for r, c in group}
        cols = {c for r, c in group}
        candidates = []
        
        if len(rows) == 1:
            # Horizontal alternating hits - fill gaps
            row = list(rows)[0]
            cols_sorted = sorted([c for r, c in group])
            min_col, max_col = cols_sorted[0], cols_sorted[-1]
            
            # Fill gaps first (PRIORITY 1)
            for c in range(min_col + 1, max_col):
                if (row, c) not in group:
                    candidates.append((row, c))
            
            # Then extend ends (PRIORITY 2)
            candidates.extend([(row, min_col - 1), (row, max_col + 1)])
            
        elif len(cols) == 1:
            # Vertical alternating hits - fill gaps
            col = list(cols)[0]
            rows_sorted = sorted([r for r, c in group])
            min_row, max_row = rows_sorted[0], rows_sorted[-1]
            
            # Fill gaps first (PRIORITY 1)
            for r in range(min_row + 1, max_row):
                if (r, col) not in group:
                    candidates.append((r, col))
            
            # Then extend ends (PRIORITY 2)
            candidates.extend([(min_row - 1, col), (max_row + 1, col)])
        
        return candidates

    def _get_target_candidates_for_group(self, group: Set[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """Get targeting candidates with immediate gap-filling for alternating hits."""
        
        if len(group) == 1:
            # Single hit - use P2M2 + adjacent for exploration
            origin = list(group)[0]
            return self._get_p2m2_pattern(origin) + self._get_adjacent_pattern(origin)
        
        # Multiple hits - check for alternating pattern FIRST
        if self._has_alternating_hit_pattern(group):
            # IMMEDIATE gap filling for alternating hits
            return self._get_gap_filling_candidates(group)
        
        # Standard multi-hit logic for linear groups
        rows = {r for r, c in group}
        cols = {c for r, c in group}
        
        if len(rows) == 1:
            # Horizontal line - fill gaps then extend
            return self._get_gap_filling_candidates(group)
        elif len(cols) == 1:
            # Vertical line - fill gaps then extend
            return self._get_gap_filling_candidates(group)
        else:
            # Non-linear pattern - use adjacent targeting only
            candidates = []
            for hit in group:
                candidates.extend(self._get_adjacent_pattern(hit))
            return candidates

    def _update_and_check_groups(self, hit_history: HitHistory):
        all_current_hits = {hit for group in self.target_groups for hit in group}
        new_hits = set(hit_history) - all_current_hits
        if not new_hits: 
            return

        if not self.target_groups and new_hits:
            self.ships_found_count += 1
        
        for r, c in new_hits:
            adjacent_groups_indices = [i for i, group in enumerate(self.target_groups) 
                                     if any(abs(r-gr) + abs(c-gc) == 1 for gr, gc in group)]
            if not adjacent_groups_indices:
                self.target_groups.append({(r, c)})
            else:
                merged_group = {(r, c)}
                for i in sorted(adjacent_groups_indices, reverse=True):
                    merged_group.update(self.target_groups.pop(i))
                self.target_groups.append(merged_group)

        # Check for sunk ships
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

    def _get_shot(self, r, c):
        self.fired_shots.add((r, c))
        return r, c

    def next_shot(self, current_board_state: BoardState, hit_history: HitHistory) -> Tuple[int, int]:
        self._update_and_check_groups(hit_history)

        # TARGETING PHASE: Handle known hits with immediate gap-filling
        if self.target_groups:
            for group in sorted(self.target_groups, key=len):
                candidates = self._get_target_candidates_for_group(group)
                
                # Process candidates in order (gaps first, then extensions)
                for r, c in candidates:
                    if self._is_valid_and_unfired(r, c):
                        return self._get_shot(r, c)
        
        # HUNTING PHASE: Random checkerboard with conditional space checking
        shots_fired = len(self.fired_shots)
        total_squares = self.board_size * self.board_size
        game_progress = shots_fired / total_squares
        
        # Early game: skip space checking for speed, late game: be more careful
        use_space_check = game_progress > 0.6  # Only check space after 60% of game
        
        while self.hunt_targets:
            r, c = self.hunt_targets.popleft()
            if self._is_valid_and_unfired(r, c):
                if not use_space_check or self._is_space_large_enough_for_any_ship(r, c):
                    return self._get_shot(r, c)

        # FALLBACK: Any remaining valid square
        all_squares = [(r, c) for r in range(self.board_size) for c in range(self.board_size)]
        random.shuffle(all_squares)
        for r, c in all_squares:
            if self._is_valid_and_unfired(r, c):
                return self._get_shot(r, c)
        
        # This should never happen in a properly functioning game
        raise RuntimeError("No valid shots available - game should have ended")