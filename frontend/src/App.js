import React, { useState } from 'react';
import './App.css';
import Dashboard from './components/dashboard/Dashboard';
import AlgorithmEditor from './components/editor/AlgorithmEditor';

function App() {
  const [activeTab, setActiveTab] = useState('simulator');

  return (
    <div className="App">
      <header className="App-header">
        <h1>Battleship Algorithm Performance Simulator</h1>
        <p>A tool to analyze, compare, and create targeting strategies</p>
        <nav className="App-nav">
          <button
            className={`nav-button ${activeTab === 'simulator' ? 'active' : ''}`}
            onClick={() => setActiveTab('simulator')}
          >
            Simulator
          </button>
          <button
            className={`nav-button ${activeTab === 'editor' ? 'active' : ''}`}
            onClick={() => setActiveTab('editor')}
          >
            JSON Algorithm Editor
          </button>
        </nav>
      </header>
      <main className="App-main">
        {activeTab === 'simulator' && <Dashboard />}
        {activeTab === 'editor' && <AlgorithmEditor />}
      </main>
      <footer className="App-footer">
        <p>Built with React & Python</p>
      </footer>
    </div>
  );
}

export default App;