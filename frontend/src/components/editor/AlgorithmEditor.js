import React, { useState, useEffect } from 'react';
import AceEditor from 'react-ace';
import 'ace-builds/src-noconflict/mode-json';
import 'ace-builds/src-noconflict/theme-github';
import { getAlgorithms, getJsonAlgorithm, saveJsonAlgorithm, renameJsonAlgorithm } from '../../api/simulationService';
import './AlgorithmEditor.css';

const NEW_ALGO_TEMPLATE = {
  name: "My New Algorithm",
  description: "A custom algorithm.",
  initial_state: "HUNT",
  queues: ["hunt_targets", "priority_targets"],
  states: {
    HUNT: {
      on_entry: [{ action: "generate_checkerboard_hunt", queue: "hunt_targets" }],
      next_shot: [{ action: "pop_from_queue", queue: "hunt_targets" }],
      transitions: [{ condition: "on_hit", next_state: "TARGET" }]
    },
    TARGET: {
      on_entry: [{ action: "add_adjacent_to_queue", queue: "priority_targets" }],
      next_shot: [{ action: "pop_from_queue", queue: "priority_targets" }],
      transitions: [{ condition: { queue_empty: "priority_targets" }, next_state: "HUNT" }]
    }
  }
};

function AlgorithmEditor() {
  const [jsonAlgorithms, setJsonAlgorithms] = useState([]);
  const [selectedAlgo, setSelectedAlgo] = useState(null);
  const [editorContent, setEditorContent] = useState('');
  const [isCreating, setIsCreating] = useState(false);
  const [renameInput, setRenameInput] = useState('');

  const fetchJsonAlgos = async () => {
    try {
      const allAlgos = await getAlgorithms();
      const jsonAlgos = allAlgos.filter(algo => algo.is_json);
      setJsonAlgorithms(jsonAlgos);
    } catch (error) {
      console.error("Failed to fetch JSON algorithms:", error);
    }
  };

  useEffect(() => {
    fetchJsonAlgos();
  }, []);

  const handleAlgoSelect = async (algo) => {
    try {
      setIsCreating(false);
      const content = await getJsonAlgorithm(algo.id);
      setSelectedAlgo(algo);
      setEditorContent(JSON.stringify(content, null, 2));
    } catch (error) {
      alert(`Failed to load algorithm content: ${error.message}`);
    }
  };

  const handleCreateNew = () => {
    setSelectedAlgo(null);
    setIsCreating(true);
    setEditorContent(JSON.stringify(NEW_ALGO_TEMPLATE, null, 2));
  };

  const handleSave = async () => {
    let algoId;
    let content;

    try {
      content = JSON.parse(editorContent);
    } catch (error) {
      alert("Invalid JSON. Please correct the syntax before saving.");
      return;
    }

    if (isCreating) {
      const newName = content.name || "new_algorithm";
      algoId = newName.toLowerCase().replace(/\s+/g, '_');
      const isDuplicate = jsonAlgorithms.some(algo => algo.id === algoId);
      if (isDuplicate) {
        if (!window.confirm(`An algorithm with ID '${algoId}' already exists. Overwrite it?`)) {
          return;
        }
      }
    } else if (selectedAlgo) {
      algoId = selectedAlgo.id;
    } else {
      alert("No algorithm selected to save.");
      return;
    }

    try {
      await saveJsonAlgorithm(algoId, content);
      alert(`Algorithm '${algoId}' saved successfully!`);
      // Refresh the list
      fetchJsonAlgos();
      setIsCreating(false);
      // Select the newly saved algorithm
      const newAlgo = { id: algoId, name: content.name, is_json: true };
      setSelectedAlgo(newAlgo);
    } catch (error) {
      alert(`Failed to save algorithm: ${error.message}`);
    }
  };

  const handleRename = async () => {
    if (!selectedAlgo || isCreating) {
      alert("Please select an existing algorithm to rename.");
      return;
    }
    if (!renameInput) {
      alert("Please enter a new name for the algorithm.");
      return;
    }

    const newId = renameInput.toLowerCase().replace(/\s+/g, '_');
    if (newId === selectedAlgo.id) {
      alert("The new name must be different from the current name.");
      return;
    }

    try {
      await renameJsonAlgorithm(selectedAlgo.id, newId);
      alert(`Algorithm renamed to '${newId}' successfully!`);
      // Refresh list, clear selection
      fetchJsonAlgos();
      setSelectedAlgo(null);
      setEditorContent('');
      setRenameInput('');
    } catch (error) {
      alert(`Failed to rename algorithm: ${error.message}`);
    }
  };

  return (
    <div className="algorithm-editor">
      <h2>JSON Algorithm Editor</h2>
      <div className="editor-layout">
        <div className="algorithm-list-panel">
          <h3>JSON Algorithms</h3>
          <ul>
            {jsonAlgorithms.map(algo => (
              <li
                key={algo.id}
                onClick={() => handleAlgoSelect(algo)}
                className={selectedAlgo?.id === algo.id && !isCreating ? 'selected' : ''}
              >
                {algo.name}
              </li>
            ))}
          </ul>
          <button onClick={handleCreateNew}>Create New Algorithm</button>
        </div>
        <div className="editor-panel">
          <h3>{isCreating ? 'Creating New Algorithm' : (selectedAlgo ? `Editing: ${selectedAlgo.name}` : 'Editor')}</h3>
          <AceEditor
            mode="json"
            theme="github"
            onChange={setEditorContent}
            value={editorContent}
            name="json-editor"
            editorProps={{ $blockScrolling: true }}
            width="100%"
            height="400px"
            fontSize={14}
            showPrintMargin={true}
            showGutter={true}
            highlightActiveLine={true}
            setOptions={{
              useWorker: false,
            }}
          />
          <div className="editor-actions">
            <input
              type="text"
              placeholder="Enter new name to rename..."
              value={renameInput}
              onChange={(e) => setRenameInput(e.target.value)}
              disabled={!selectedAlgo || isCreating}
            />
            <button onClick={handleRename} disabled={!selectedAlgo || isCreating}>Rename</button>
            <button onClick={handleSave}>Save</button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default AlgorithmEditor;
