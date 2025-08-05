from abc import ABC, abstractmethod
from typing import List, Tuple, Dict, Any

# Define type hints for clarity
BoardState = List[List[str]]
HitHistory = List[Tuple[int, int]]
Ship = Dict[str, Any]
ShipConfiguration = List[Ship]

class TargetingAlgorithm(ABC):
    """
    Abstract Base Class for all targeting algorithms.

    This class defines the standard interface for how a targeting algorithm
    interacts with the game engine. Any new algorithm created for the simulator
    MUST inherit from this class and implement all its abstract methods.
    """

    def __init__(self, board_size: int, ship_config: ShipConfiguration):
        """
        Initializes the algorithm.

        Args:
            board_size (int): The dimension of the game board (e.g., 10 for a 10x10 grid).
            ship_config (ShipConfiguration): The list of ships to be sunk. This allows
                                             algorithms to be aware of the ship shapes and sizes
                                             if they need to use that information (e.g., for
                                             probabilistic models).
        """
        self.board_size = board_size
        self.ship_config = ship_config

    @property
    @abstractmethod
    def name(self) -> str:
        """
        A user-friendly name for the algorithm. This will be displayed in the UI.

        Returns:
            str: The name of the algorithm.
        """
        pass

    @abstractmethod
    def next_shot(self, current_board_state: BoardState, hit_history: HitHistory) -> Tuple[int, int]:
        """
        The core method of the algorithm. It is called by the simulation engine
        on each turn to determine the next coordinate to target.

        Args:
            current_board_state (BoardState):
                A 2D list representing the player's view of the opponent's board.
                Cells can have values like 'UNKNOWN', 'MISS', or 'HIT'.

            hit_history (HitHistory):
                An ordered list of coordinates [(r1, c1), (r2, c2), ...] that have
                resulted in a 'HIT'. This can be useful for algorithms that need
                to know the location of currently damaged but not yet sunk ships.

        Returns:
            tuple: The (row, col) coordinate for the next shot. The simulation engine
                   expects this to be a valid, untargeted square.
        """
        pass

    def reset(self):
        """
        (Optional) Resets the internal state of the algorithm.
        This is called before the start of each new game in a simulation run.
        Useful for algorithms that maintain state between shots (like hunt/target modes).
        If an algorithm is stateless, this method can simply be ignored.
        """
        pass