import React, { useState, useMemo } from 'react';
import './GameReplay.css';

// --- NEW: Color mapping for ships ---
const SHIP_COLORS = {
  // Define colors for the classic ship set names.
  // We can add more for other configurations if needed.
  "Carrier": "#FF6347",    // Tomato Red
  "Battleship": "#4682B4", // Steel Blue
  "Cruiser": "#32CD32",    // Lime Green
  "Submarine": "#FFD700",  // Gold
  "Destroyer": "#9370DB",  // Medium Purple
  // A default color for any ship not in this list
  "default": "#778899"     // Light Slate Gray
};

/**
 * A component to visually replay the shot sequence of a sample game.
 * 
 * @param {Object} props - Component props.
 * @param {Object} props.sampleGame - The sample_game object from the API.
 */
function GameReplay({ sampleGame }) {
  const [replayStep, setReplayStep] = useState(0);

  const currentBoardState = useMemo(() => {
    if (!sampleGame) return [];
    const boardSize = sampleGame.solution_grid.length;
    const board = Array(boardSize).fill(null).map(() => Array(boardSize).fill('UNKNOWN'));
    for (let i = 0; i < replayStep; i++) {
      const [r, c] = sampleGame.shots[i];
      if (sampleGame.solution_grid[r][c] !== null) {
        board[r][c] = 'HIT';
      } else {
        board[r][c] = 'MISS';
      }
    }
    return board;
  }, [replayStep, sampleGame]);

  if (!sampleGame || !sampleGame.shots || !sampleGame.solution_grid) {
    return null;
  }

  const totalShots = sampleGame.shots.length;

  return (
    <div className="replay-container">
      <h3>Sample Game Replay</h3>
      <div className="replay-grid">
        {currentBoardState.map((row, r) => (
          <div key={r} className="replay-row">
            {row.map((cell, c) => {
              const shipName = sampleGame.solution_grid[r][c];
              const isShip = shipName !== null;
              const isLastShot = replayStep > 0 && sampleGame.shots[replayStep - 1][0] === r && sampleGame.shots[replayStep - 1][1] === c;

              // --- MODIFIED: Dynamic Styling ---
              const style = {};
              let cellClass = `replay-cell cell-${cell}`;
              
              if (cell === 'HIT' && isShip) {
                // If it's a hit on a ship, apply the ship's specific color
                style.backgroundColor = SHIP_COLORS[shipName] || SHIP_COLORS.default;
              }
              
              if (isLastShot) {
                cellClass += ' cell-last-shot';
              }

              return (
                <div key={c} className={cellClass} style={style}>
                  {cell === 'HIT' ? '✕' : ''}
                </div>
              );
            })}
          </div>
        ))}
      </div>
      <div className="replay-controls">
        <label htmlFor="replay-slider">Shot: {replayStep} / {totalShots}</label>
        <input
          id="replay-slider"
          type="range"
          min="0"
          max={totalShots}
          value={replayStep}
          onChange={(e) => setReplayStep(Number(e.target.value))}
          className="slider"
        />
      </div>
    </div>
  );
}

export default GameReplay;