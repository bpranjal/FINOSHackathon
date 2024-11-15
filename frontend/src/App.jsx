import React, { useState } from 'react';
import './App.css';


function App() {
  const [jsonInput, setJsonInput] = useState('');
  const [jsonSchema, setJsonSchema] = useState('');

  const processJsonData = (jsonData) => {
    // You can perform any logic here with the parsed JSON
    console.log('Processing JSON Data:', jsonData);
    // For example, just log it to the console
    return jsonData; // You can manipulate or return the data here
  };


  // Handle JSON input submission
  const handleInputSubmit = () => {
    try {
      const parsedJson = JSON.parse(jsonInput);
      console.log(parsedJson);
      console.log("Completed.........")
      const generatedSchema = processJsonData(parsedJson)
      console.log(generatedSchema);
      setJsonSchema(generatedSchema);
    } catch (error) {
      setJsonSchema('Invalid JSON format');
    }
  };

  // Handle output submission (you can add further functionality here if needed)
  const handleOutputSubmit = () => {
    alert('JSON Schema Submitted Successfully!');
  };

  return (
    <div className="app-container">
      {/* Navbar */}
      <header className="navbar">
        <h1>SchemaCraft</h1>
      </header>

      {/* Split screen layout */}
      <div className="split-screen">
        {/* Left Side: JSON Input */}
        <div className="input-box">
          <h2>JSON Input</h2>
          <textarea
            className="textarea"
            placeholder="Paste your JSON here..."
            value={jsonInput}
            onChange={(e) => setJsonInput(e.target.value)}
          />
          <button onClick={handleInputSubmit} className="submit-button">
            Submit
          </button>
        </div>

        {/* Right Side: JSON Schema Output */}
        <div className="output-box">
          <h2>Generated JSON Schema</h2>
          <pre className="output">
            {jsonSchema || 'Your schema will appear here...'}
          </pre>
          <button onClick={handleOutputSubmit} className="submit-button">
            Submit Field Details
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;
