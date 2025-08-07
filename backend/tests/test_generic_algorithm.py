import pytest
from app.algorithms.registry import get_available_algorithms, get_algorithm_instance
from app.simulation.ship_configs import CLASSIC_SHIP_CONFIG

def test_discover_json_algorithms():
    """
    Tests if the JSON algorithms are discovered and available.
    """
    available_algos = get_available_algorithms()
    algo_names = [algo['name'] for algo in available_algos]

    assert "Random Search (JSON)" in algo_names
    assert "P2M2 (JSON)" in algo_names

def test_instantiate_random_search_json():
    """
    Tests if the 'random_search.json' algorithm can be instantiated.
    """
    algo = get_algorithm_instance(
        algo_id='random_search',
        board_size=10,
        ship_config=CLASSIC_SHIP_CONFIG
    )
    assert algo.name == "Random Search (JSON)"
    # Check that it's a GenericAlgorithm instance
    assert 'GenericAlgorithm' in str(type(algo))

def test_random_search_json_next_shot():
    """
    Tests if the JSON-based random search algorithm can generate valid shots.
    """
    algo = get_algorithm_instance(
        algo_id='random_search',
        board_size=10,
        ship_config=CLASSIC_SHIP_CONFIG
    )

    # Create a valid, empty board state
    board_state = [['UNKNOWN' for _ in range(10)] for _ in range(10)]

    # Generate a few shots and check if they are valid
    for _ in range(5):
        shot = algo.next_shot(current_board_state=board_state, hit_history=[])
        assert isinstance(shot, tuple)
        assert len(shot) == 2
        assert 0 <= shot[0] < 10
        assert 0 <= shot[1] < 10
        # Mark the shot as MISS to avoid issues with re-shot protection in the algorithm
        board_state[shot[0]][shot[1]] = 'MISS'


def test_instantiate_p2m2_json():
    """
    Tests if the 'p2m2_json.json' algorithm can be instantiated.
    """
    algo = get_algorithm_instance(
        algo_id='p2m2_json',
        board_size=10,
        ship_config=CLASSIC_SHIP_CONFIG
    )
    assert algo.name == "P2M2 (JSON)"
    assert 'GenericAlgorithm' in str(type(algo))
    assert algo.current_state == "HUNT"

def test_p2m2_json_state_transition():
    """
    Tests the HUNT -> TARGET state transition for the JSON-based P2M2.
    """
    algo = get_algorithm_instance(
        algo_id='p2m2_json',
        board_size=10,
        ship_config=CLASSIC_SHIP_CONFIG
    )

    # Initial state should be HUNT
    assert algo.current_state == "HUNT"

    # Simulate a hit
    # The next_shot call will internally check for transitions based on the updated game state
    # We pass a non-empty hit_history to simulate that a hit has occurred.
    # The GenericAlgorithm's logic will see the new hit and trigger the transition.

    # Let's manually trigger the state update logic for a clearer test
    algo._check_transitions(last_shot_result="HIT", hit_history=[(5,5)])

    # Now the state should be TARGET
    assert algo.current_state == "TARGET"
    # And the ships_found_count should be incremented
    assert algo.variables['ships_found_count'] == 1
