import copy
import os
from flask import Blueprint, request, jsonify

# --- MODIFICATION IS ON THIS LINE ---
from app.algorithms.registry import get_available_algorithms, get_algorithm_instance
from app.simulation.simulation_runner import SimulationRunner
from app.simulation.statistical_analyzer import StatisticalAnalyzer

api_bp = Blueprint('api_bp', __name__)

@api_bp.route('/algorithms', methods=['GET'])
def list_algorithms():
    try:
        algorithms = get_available_algorithms()
        return jsonify(algorithms)
    except Exception as e:
        return jsonify({"error": "Failed to retrieve algorithms"}), 500

@api_bp.route('/algorithms/json/<algo_id>', methods=['GET'])
def get_json_algorithm(algo_id):
    try:
        # Construct the path to the JSON file
        # This assumes the 'json_algorithms' directory is at a known location
        # relative to the 'api' directory.
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_algos_path = os.path.join(current_dir, '..', 'json_algorithms')
        file_path = os.path.join(json_algos_path, f"{algo_id}.json")

        if not os.path.exists(file_path):
            return jsonify({"error": "JSON algorithm not found."}), 404

        with open(file_path, 'r') as f:
            content = f.read()

        # The content is already a JSON string, so we can return it directly,
        # but it's better to load and dump it to ensure it's valid JSON.
        import json
        return jsonify(json.loads(content))

    except Exception as e:
        print(f"Error getting JSON algorithm {algo_id}: {e}")
        return jsonify({"error": "Failed to retrieve JSON algorithm"}), 500

@api_bp.route('/algorithms/json/<algo_id>', methods=['POST'])
def save_json_algorithm(algo_id):
    try:
        json_content = request.get_json()
        if not json_content:
            return jsonify({"error": "Invalid request body. JSON expected."}), 400

        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_algos_path = os.path.join(current_dir, '..', 'json_algorithms')
        file_path = os.path.join(json_algos_path, f"{algo_id}.json")

        # Pretty-print the JSON to the file
        with open(file_path, 'w') as f:
            import json
            json.dump(json_content, f, indent=2)

        # We need to re-discover the algorithms so the registry is updated
        from app.algorithms.json_registry import discover_json_algorithms
        discover_json_algorithms()

        return jsonify({"message": f"Algorithm '{algo_id}' saved successfully."}), 200

    except Exception as e:
        print(f"Error saving JSON algorithm {algo_id}: {e}")
        return jsonify({"error": "Failed to save JSON algorithm"}), 500

@api_bp.route('/algorithms/json/<algo_id>/rename', methods=['POST'])
def rename_json_algorithm(algo_id):
    try:
        data = request.get_json()
        new_algo_id = data.get('new_id')
        if not new_algo_id:
            return jsonify({"error": "Missing 'new_id' in request body."}), 400

        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_algos_path = os.path.join(current_dir, '..', 'json_algorithms')

        old_file_path = os.path.join(json_algos_path, f"{algo_id}.json")
        new_file_path = os.path.join(json_algos_path, f"{new_algo_id}.json")

        if not os.path.exists(old_file_path):
            return jsonify({"error": "Algorithm to rename not found."}), 404
        if os.path.exists(new_file_path):
            return jsonify({"error": "An algorithm with the new name already exists."}), 409

        os.rename(old_file_path, new_file_path)

        # Re-discover algorithms to update the registry
        from app.algorithms.json_registry import discover_json_algorithms
        discover_json_algorithms()

        return jsonify({"message": f"Algorithm '{algo_id}' renamed to '{new_algo_id}' successfully."}), 200

    except Exception as e:
        print(f"Error renaming JSON algorithm {algo_id}: {e}")
        return jsonify({"error": "Failed to rename JSON algorithm"}), 500

@api_bp.route('/simulations', methods=['POST'])
def run_simulation():
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
            "analysis": {
                "summary_stats": analysis["summary_stats"],
                "histogram": analysis["histogram"]
            },
            "visualizations": {
                "heat_map": raw_results["heat_map"],
                "sample_game": raw_results.get("sample_game") 
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
    try:
        params = request.get_json()
        if not params:
            return jsonify({"error": "Invalid request body. JSON expected."}), 400
        required_params = ['algorithms', 'num_simulations', 'ship_placement_strategy']
        if not all(key in params for key in required_params) or not isinstance(params.get('algorithms'), list) or len(params['algorithms']) < 2:
            return jsonify({"error": "Request must include a list of 2 or more 'algorithms' to compare."}), 400

        runner = SimulationRunner(simulation_params=params)
        all_raw_results = runner.run_comparison()
        all_analyses = {}
        for algo_id, raw_result in all_raw_results.items():
            analysis = StatisticalAnalyzer.analyze(raw_result)
            # This line now works because of the fixed import
            analysis['algorithm_name'] = get_algorithm_instance(algo_id, 10, []).name
            analysis['sample_game'] = raw_result.get("sample_game")
            all_analyses[algo_id] = analysis
            
        shots_data_for_anova = [res["shots_per_game"] for res in all_raw_results.values()]
        anova_results = StatisticalAnalyzer.perform_anova(shots_data_for_anova)

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