import axios from 'axios';

// The base URL of our Flask backend server.
// We'll read this from an environment variable for best practice,
// but hardcode it here for simplicity in this step.
const API_BASE_URL = 'http://localhost:5015/api';

/**
 * Creates a configured instance of axios.
 */
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Fetches the list of available algorithms from the backend.
 *
 * @returns {Promise<Array<Object>>} A promise that resolves to an array of algorithm objects.
 * e.g., [{ id: 'randomsearch', name: 'Random Search' }]
 */
export const getAlgorithms = async () => {
  try {
    const response = await apiClient.get('/algorithms');
    return response.data;
  } catch (error) {
    console.error('Error fetching algorithms:', error);
    // Rethrow a more user-friendly error or handle it as needed
    throw new Error('Could not connect to the server to get algorithm list.');
  }
};

/**
 * Runs a new simulation by sending parameters to the backend.
 *
 * @param {Object} simulationParams - The configuration object for the simulation.
 * e.g., { algorithm: 'randomsearch', num_simulations: 1000, ... }
 * @returns {Promise<Object>} A promise that resolves to the full simulation result object.
 */
export const runSimulation = async (simulationParams) => {
  try {
    const response = await apiClient.post('/simulations', simulationParams);
    return response.data;
  } catch (error) {
    // Axios wraps the actual API error in error.response
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx (e.g., 400, 500).
      console.error('Simulation API Error:', error.response.data);
      // We throw the specific error message from the backend API
      throw new Error(error.response.data.error || 'A server error occurred.');
    } else if (error.request) {
      // The request was made but no response was received (e.g., server is down)
      console.error('Network Error:', error.request);
      throw new Error('Cannot connect to the simulation server. Is it running?');
    } else {
      // Something happened in setting up the request that triggered an Error
      console.error('Error:', error.message);
      throw error;
    }
  }
};