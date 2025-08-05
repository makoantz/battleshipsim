import numpy as np
from typing import Dict, List, Any

# Define type hints for clarity
SimulationResult = Dict[str, Any]
StatisticalAnalysis = Dict[str, Any]

class StatisticalAnalyzer:
    """
    Performs statistical analysis on the results of a simulation run.

    This class takes the raw data from the SimulationRunner, specifically the
    list of shots per game, and computes a variety of descriptive statistics
    and data needed for frontend visualizations.
    """

    @staticmethod
    def analyze(simulation_result: SimulationResult) -> StatisticalAnalysis:
        """
        Analyzes the results of a single algorithm's simulation run.

        Args:
            simulation_result (SimulationResult): The dictionary of results from
                                                  a SimulationRunner instance.

        Returns:
            A dictionary containing summary statistics and histogram data.
        """
        shots_data = simulation_result.get("shots_per_game", [])
        
        if not shots_data:
            return {
                "summary_stats": {
                    "mean": 0, "median": 0, "std_dev": 0, "min": 0, "max": 0,
                    "total_simulations": 0
                },
                "histogram": {"bins": [], "frequencies": []}
            }
            
        # Use numpy for efficient calculations
        shots_array = np.array(shots_data)
        
        summary_stats = {
            "mean": np.mean(shots_array),
            "median": np.median(shots_array),
            "std_dev": np.std(shots_array),
            "min": int(np.min(shots_array)), # Convert from numpy types to standard python types
            "max": int(np.max(shots_array)),
            "total_simulations": len(shots_data)
        }
        
        # Generate data for a histogram visualization
        # We can define the number of bins for the histogram, e.g., 20
        # np.histogram returns the frequencies and the bin edges.
        num_bins = 20
        frequencies, bin_edges = np.histogram(shots_array, bins=num_bins)
        
        # Format histogram data for easy use with charting libraries
        histogram = {
            "frequencies": frequencies.tolist(),
            # We return the center of the bins for easier plotting
            "bins": ((bin_edges[:-1] + bin_edges[1:]) / 2).tolist()
        }
        
        return {
            "summary_stats": summary_stats,
            "histogram": histogram
        }

    @staticmethod
    def perform_anova(results_from_multiple_runs: List[List[int]]) -> Dict[str, float]:
        """
        Performs a one-way ANOVA test to compare multiple simulation runs.

        This is used to determine if there is a statistically significant
        difference between the means of two or more independent groups.

        Args:
            results_from_multiple_runs (List[List[int]]): A list where each
                element is a list of shot counts from a different algorithm's
                simulation run. e.g., [[run1_shots], [run2_shots], ...]

        Returns:
            A dictionary containing the F-statistic and the p-value.
        """
        # ANOVA requires at least two groups to compare
        if len(results_from_multiple_runs) < 2:
            return {"f_statistic": 0.0, "p_value": 1.0}

        try:
            # We must import scipy here, as it's a heavier dependency used only for this feature
            from scipy.stats import f_oneway
            
            f_statistic, p_value = f_oneway(*results_from_multiple_runs)
            
            return {"f_statistic": f_statistic, "p_value": p_value}

        except ImportError:
            print("Warning: 'scipy' is not installed. ANOVA analysis is unavailable.")
            return {"f_statistic": 0.0, "p_value": 1.0, "error": "scipy_not_installed"}
        except Exception as e:
            print(f"An error occurred during ANOVA calculation: {e}")
            return {"f_statistic": 0.0, "p_value": 1.0, "error": str(e)}