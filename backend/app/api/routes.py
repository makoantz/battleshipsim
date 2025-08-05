from flask import Blueprint, request, jsonify

# Import the backend components that this API will orchestrate
from app.algorithms.registry import get_available_algorithms
from app.simulation.simulation_runner import SimulationRunner
from app.simulation.statistical_analyzer import StatisticalAnalyzer

# Create a Blueprint. This is Flask's way of organizing a group of related routes.
api_bp = Blueprint('api_bp', __name__)

@api_bp.route('/algorithms', methods=['GET'])
def list_algorithms():
    """
    API endpoint to get the list of all available targeting algorithms.
    It reads from the algorithm registry.
    """
    try:
        algorithms = get_available_algorithms()
        return jsonify(algorithms)
    except Exception as e:
        # Log the exception e
        return jsonify({"error": "Failed to retrieve algorithms"}), 500

@api_bp.route('/simulations', methods=['POST'])
def run_simulation():
    """
    API endpoint to start a simulation run.
    This is the primary endpoint for the application. It receives simulation
    parameters from the frontend, runs the simulation, performs statistical
    analysis, and returns the complete results.
    """
    try:
        # 1. Get simulation parameters from the request body
        params = request.get_json()
        if not params:
            return jsonify({"error": "Invalid request body. JSON expected."}), 400

        # Basic validation of required parameters
        required_params = ['algorithm', 'num_simulations', 'ship_placement_strategy']
        if not all(key in params for key in required_params):
            return jsonify({"error": f"Missing one or more required parameters: {required_params}"}), 400

        # 2. Instantiate the runner and run the simulation to get raw results
        runner = SimulationRunner(simulation_params=params)
        raw_results = runner.run()

        # 3. Analyze the raw results to get statistics
        analysis = StatisticalAnalyzer.analyze(raw_results)

        # 4. Combine all results into a single response object
        full_response = {
            "simulation_parameters": params,
            "raw_data": {
                "shots_per_game": raw_results["shots_per_game"]
            },
            "analysis": {
                "summary_stats": analysis["summary_stats"],
                "histogram": analysis["histogram"]
            },
            "visualizations": {
                "heat_map": raw_results["heat_map"]
            }
        }

        return jsonify(full_response)

    except ValueError as e:
        # Catches known errors, like an invalid algorithm ID
        return jsonify({"error": str(e)}), 400
    except RuntimeError as e:
        # Catches game-specific errors, like an impossible ship placement
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        # Generic catch-all for any other unexpected errors
        # In a real production app, you would log the full error `e`
        print(f"An unexpected error occurred: {e}") # For debugging
        return jsonify({"error": "An internal server error occurred."}), 500

# Placeholder for future ANOVA endpoint
@api_bp.route('/compare', methods=['POST'])
def compare_algorithms():
    """
    (Future) API endpoint to compare results from multiple algorithms
    using an ANOVA test.
    """
    # This endpoint would receive multiple sets of results and use
    # StatisticalAnalyzer.perform_anova()
    return jsonify({"message": "Endpoint not yet implemented."}), 501