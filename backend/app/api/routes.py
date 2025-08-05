import copy
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
    API endpoint to start a simulation run for a SINGLE algorithm.
    """
    try:
        params = request.get_json()
        if not params:
            return jsonify({"error": "Invalid request body. JSON expected."}), 400

        required_params = ['algorithm', 'num_simulations', 'ship_placement_strategy']
        if not all(key in params for key in required_params):
            return jsonify({"error": f"Missing one or more required parameters: {required_params}"}), 400

        runner = SimulationRunner(simulation_params=params)
        raw_results = runner.run()

        analysis = StatisticalAnalyzer.analyze(raw_results)

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

    except (ValueError, RuntimeError) as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({"error": "An internal server error occurred."}), 500


@api_bp.route('/compare', methods=['POST'])
def compare_simulations():
    """
    API endpoint to run a comparative simulation for MULTIPLE algorithms.
    Ensures all algorithms face the exact same ship placements for each round.
    """
    try:
        params = request.get_json()
        if not params:
            return jsonify({"error": "Invalid request body. JSON expected."}), 400

        required_params = ['algorithms', 'num_simulations', 'ship_placement_strategy']
        if not all(key in params for key in required_params) or not isinstance(params.get('algorithms'), list) or len(params['algorithms']) < 2:
            return jsonify({"error": "Request must include a list of 2 or more 'algorithms' to compare."}), 400

        # Instantiate the runner and run the new comparison method
        runner = SimulationRunner(simulation_params=params)
        all_raw_results = runner.run_comparison()

        # Analyze each algorithm's results individually
        all_analyses = {}
        for algo_id, raw_result in all_raw_results.items():
            all_analyses[algo_id] = StatisticalAnalyzer.analyze(raw_result)

        # Perform ANOVA test across all result sets to see if there's a significant difference
        shots_data_for_anova = [res["shots_per_game"] for res in all_raw_results.values()]
        anova_results = StatisticalAnalyzer.perform_anova(shots_data_for_anova)

        # Combine everything into a final response, structured for comparison
        final_response = {
            "simulation_parameters": params,
            "individual_results": all_analyses,
            "comparison_analysis": anova_results
        }
        return jsonify(final_response)

    except (ValueError, RuntimeError) as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print(f"An unexpected error occurred during comparison: {e}")
        return jsonify({"error": "An internal server error occurred."}), 500