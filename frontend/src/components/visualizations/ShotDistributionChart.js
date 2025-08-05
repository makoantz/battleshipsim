import React from 'react';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import './ShotDistributionChart.css';

// We need to register the components we are going to use with ChartJS
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

/**
 * A component that renders a bar chart showing the distribution of shots per game.
 * @param {Object} props - The component props.
 * @param {Object} props.histogramData - The histogram object from the API response.
 * e.g., { bins: [...], frequencies: [...] }
 */
function ShotDistributionChart({ histogramData }) {
  if (!histogramData || !histogramData.bins || !histogramData.frequencies) {
    return null;
  }

  // Chart.js configuration object
  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false, // We don't need a legend for a single dataset
      },
      title: {
        display: true,
        text: 'Distribution of Shots to Win',
        font: {
          size: 18,
        }
      },
    },
    scales: {
      x: {
        title: {
          display: true,
          text: 'Number of Shots',
        },
      },
      y: {
        title: {
          display: true,
          text: 'Frequency (Number of Games)',
        },
        beginAtZero: true,
      },
    },
  };

  // Format the data for Chart.js
  const data = {
    // The 'bins' are the labels for our X-axis (e.g., "65", "70", "75")
    labels: histogramData.bins.map(bin => bin.toFixed(0)),
    datasets: [
      {
        label: 'Frequency',
        // The 'frequencies' are the actual values for each bar
        data: histogramData.frequencies,
        backgroundColor: 'rgba(0, 123, 255, 0.6)',
        borderColor: 'rgba(0, 123, 255, 1)',
        borderWidth: 1,
      },
    ],
  };

  return (
    <div className="chart-container">
      <Bar options={options} data={data} />
    </div>
  );
}

export default ShotDistributionChart;