import React from 'react';
import './App.css';
import Dashboard from './components/dashboard/Dashboard';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Battleship Algorithm Performance Simulator</h1>
        <p>A tool to analyze and compare targeting strategies</p>
      </header>
      <main className="App-main">
        {/* The Dashboard component will contain all the controls,
            charts, and results for the simulator. */}
        <Dashboard />
      </main>
      <footer className="App-footer">
        <p>Built with React & Python</p>
      </footer>
    </div>
  );
}

export default App;