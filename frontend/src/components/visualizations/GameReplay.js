import React, { useState, useMemo } from 'react';
import './GameReplay.css';

/**
 * A component to visually replay the shot sequence of a sample game.
 * 
 * @param {Object} props - Component props.
 * @param {Object} props.sampleGame - The sample_game object from the API.
 *                                    { shots: [...], solution_grid: [...] }
 */
function GameReplay({ sampleGame }) {
  const [replayStep, setReplayStep] = useState(0);

  // useMemo will re-calculate the board state only when the step changes,
  // which is more efficient than recalculating on every render.
  const currentBoardState = useMemo(() => {
    if (!sampleGame) return [];

    const boardSize = sampleGame.solution_grid.length;
    // Start with an empty 'UNKNOWN' board
    const board = Array(boardSize).fill(null).map(() => Array(boardSize).fill('UNKNOWN'));

    // Replay shots up to the current step
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
              // Determine if the cell contains a ship segment in the solution
              const isShip = sampleGame.solution_grid[r][c] !== null;
              // Determine if this cell is the most recent shot
              const isLastShot = replayStep > 0 && sampleGame.shots[replayStep - 1][0] === r && sampleGame.shots[replayStep - 1][1] === c;

              // The final class depends on the cell state and if it's a ship
              let cellClass = `replay-cell cell-${cell}`;
              if (cell === 'UNKNOWN' && isShip) {
                cellClass += ' cell-ship-hidden';
              }
              if (isLastShot) {
                cellClass += ' cell-last-shot';
              }

              return (
                <div key={c} className={cellClass}>
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