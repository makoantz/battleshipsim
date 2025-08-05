import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

// 1. Find the root DOM element from our index.html file.
const rootElement = document.getElementById('root');

// 2. Create a React root to manage rendering within that element.
const root = ReactDOM.createRoot(rootElement);

// 3. Render the main App component inside the root.
// React.StrictMode is a wrapper that helps find potential problems in an app.
// It activates additional checks and warnings for its descendants.
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);