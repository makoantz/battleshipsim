import random
from typing import List, Tuple

# Import the base class and type hints from our defined interface
from .base import TargetingAlgorithm, BoardState, HitHistory

class RandomSearch(TargetingAlgorithm):
    """
    A simple targeting algorithm that fires at random, valid squares.

    This algorithm serves as the baseline for performance comparison. It does not
    use any sophisticated logic; it simply maintains a list of untargeted
    squares and picks one at random for each shot.
    """

    def __init__(self, *args, **kwargs):
        """
        Initializes the RandomSearch algorithm. It accepts any arguments to ensure
        compatibility with the factory but does not use them.
        """
        super().__init__(*args, **kwargs)
        self.unfired_shots = None
        self.reset()

    @property
    def name(self) -> str:
        """Returns the user-friendly name of the algorithm."""
        return "Random Search"

    def reset(self):
        """
        Resets the algorithm's state for a new game.
        It repopulates the list of all possible coordinates on the board.
        """
        self.unfired_shots = [
            (r, c) for r in range(self.board_size) for c in range(self.board_size)
        ]
        random.shuffle(self.unfired_shots)

    def next_shot(self, current_board_state: BoardState, hit_history: HitHistory) -> Tuple[int, int]:
        """
        Selects the next shot by picking a random coordinate from its list of
        available shots.

        Note: This specific implementation ignores the 'current_board_state' and
        'hit_history' arguments because its internal list of unfired shots is
        a more efficient way to track available targets. It simply pops a
        pre-shuffled coordinate from its list.

        Returns:
            A tuple (row, col) for the next target.
        """
        if not self.unfired_shots:
            # This should ideally not be reached in a normal game,
            # but is a safeguard against an empty list.
            raise ValueError("No available squares left to target.")

        return self.unfired_shots.pop()