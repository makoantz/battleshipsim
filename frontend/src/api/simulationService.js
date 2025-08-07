import axios from 'axios';

// The base URL of our Flask backend server.
const API_BASE_URL = 'http://10.58.122.80:5015/api';

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
 * Renames a JSON-defined algorithm.
 *
 * @param {string} oldAlgoId - The current ID of the algorithm.
 * @param {string} newAlgoId - The new ID for the algorithm.
 * @returns {Promise<Object>} A promise that resolves to the backend response.
 */
export const renameJsonAlgorithm = async (oldAlgoId, newAlgoId) => {
  try {
    const response = await apiClient.post(`/algorithms/json/${oldAlgoId}/rename`, { new_id: newAlgoId });
    return response.data;
  } catch (error) {
    console.error(`Error renaming algorithm ${oldAlgoId}:`, error);
    throw new Error(error.response?.data?.error || `Could not rename algorithm.`);
  }
};

/**
 * Saves (creates or updates) a JSON-defined algorithm.
 *
 * @param {string} algoId - The ID of the JSON algorithm.
 * @param {Object} content - The JSON content of the algorithm.
 * @returns {Promise<Object>} A promise that resolves to the backend response.
 */
export const saveJsonAlgorithm = async (algoId, content) => {
  try {
    const response = await apiClient.post(`/algorithms/json/${algoId}`, content);
    return response.data;
  } catch (error) {
    console.error(`Error saving JSON for algorithm ${algoId}:`, error);
    throw new Error(`Could not save content for ${algoId}.`);
  }
};

/**
 * Fetches the content of a specific JSON-defined algorithm.
 *
 * @param {string} algoId - The ID of the JSON algorithm.
 * @returns {Promise<Object>} A promise that resolves to the JSON content of the algorithm.
 */
export const getJsonAlgorithm = async (algoId) => {
  try {
    const response = await apiClient.get(`/algorithms/json/${algoId}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching JSON for algorithm ${algoId}:`, error);
    throw new Error(`Could not fetch content for ${algoId}.`);
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