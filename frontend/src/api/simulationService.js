import axios from 'axios';

// The base URL of our Flask backend server.
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
 */
export const getAlgorithms = async () => {
  try {
    const response = await apiClient.get('/algorithms');
    return response.data;
  } catch (error) {
    console.error('Error fetching algorithms:', error);
    throw new Error('Could not connect to the server to get algorithm list.');
  }
};

/**
 * Runs a new simulation for a SINGLE algorithm.
 *
 * @param {Object} simulationParams - The configuration object for the simulation.
 * @returns {Promise<Object>} A promise that resolves to the full simulation result object.
 */
export const runSimulation = async (simulationParams) => {
  try {
    const response = await apiClient.post('/simulations', simulationParams);
    return response.data;
  } catch (error) {
    if (error.response) {
      console.error('Simulation API Error:', error.response.data);
      throw new Error(error.response.data.error || 'A server error occurred.');
    } else if (error.request) {
      console.error('Network Error:', error.request);
      throw new Error('Cannot connect to the simulation server. Is it running?');
    } else {
      console.error('Error:', error.message);
      throw error;
    }
  }
};

/**
 * Runs a new comparison simulation for MULTIPLE algorithms.
 *
 * @param {Object} comparisonParams - The configuration object.
 * e.g., { algorithms: ['randomsearch', 'huntandtarget'], ... }
 * @returns {Promise<Object>} A promise that resolves to the comparison result object.
 */
export const runComparison = async (comparisonParams) => {
  try {
    const response = await apiClient.post('/compare', comparisonParams);
    return response.data;
  } catch (error) {
    if (error.response) {
      console.error('Comparison API Error:', error.response.data);
      throw new Error(error.response.data.error || 'A server error occurred.');
    } else if (error.request) {
      console.error('Network Error:', error.request);
      throw new Error('Cannot connect to the simulation server. Is it running?');
    } else {
      console.error('Error:', error.message);
      throw error;
    }
  }
};