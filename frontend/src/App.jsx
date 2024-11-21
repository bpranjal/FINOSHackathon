import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [jsonInput, setJsonInput] = useState('');
  const [jsonExample, setJsonExample] = useState(null); // State to hold original JSON example
  const [jsonSchema, setJsonSchema] = useState({});
  const [fieldDetails, setFieldDetails] = useState({});
  const [staticFields, setStaticFields] = useState({
    rootDefinition: '',
    rootDefinitionTitle: '',
    rootDefinitionDescription: '',
    schemaTitle: '',
    schemaDescription: '',
  });
  const [resultantSchema, setResultantSchema] = useState(null); // New state to store the final schema

  // Function to get field types from JSON data
  const getJsonFieldTypes = (jsonData, parentKey = '') => {
    const fieldTypes = {};

    for (const [key, value] of Object.entries(jsonData)) {
      const fullKey = parentKey ? `${parentKey}.${key}` : key;

      if (typeof value === 'object' && !Array.isArray(value) && value !== null) {
        fieldTypes[fullKey] = 'object';
        Object.assign(fieldTypes, getJsonFieldTypes(value, fullKey));
      } else if (Array.isArray(value) && value.length > 0) {
        const elementType = typeof value[0];
        if (typeof value[0] === 'object' && value[0] !== null) {
          fieldTypes[fullKey] = 'array of objects';
          Object.assign(fieldTypes, getJsonFieldTypes(value[0], fullKey));
        } else {
          fieldTypes[fullKey] = `array of ${elementType}`;
        }
      } else {
        const fieldType = typeof value;
        fieldTypes[fullKey] = fieldType;
      }
    }

    return fieldTypes;
  };

  // Handle JSON input submission
  const handleInputSubmit = () => {
    try {
      const parsedJson = JSON.parse(jsonInput);
      setJsonExample(parsedJson); // Store the original JSON example
      const generatedSchema = getJsonFieldTypes(parsedJson);
      setJsonSchema(generatedSchema);

      // Initialize field details (title, description) with default values
      const initialDetails = {};
      for (const field in generatedSchema) {
        initialDetails[field] = { title: field, description: '' };
      }
      setFieldDetails(initialDetails);
    } catch (error) {
      setJsonSchema('Invalid JSON format');
    }
  };

  // Handle static field text input change
  const handleStaticFieldChange = (e, field) => {
    const updatedStaticFields = { ...staticFields, [field]: e.target.value };
    setStaticFields(updatedStaticFields);
  };

  // Handle field title change
  const handleTitleChange = (e, field) => {
    const updatedDetails = { ...fieldDetails, [field]: { ...fieldDetails[field], title: e.target.value } };
    setFieldDetails(updatedDetails);
  };

  // Handle field description change
  const handleDescriptionChange = (e, field) => {
    const updatedDetails = { ...fieldDetails, [field]: { ...fieldDetails[field], description: e.target.value } };
    setFieldDetails(updatedDetails);
  };

  // Handle field type change
  const handleFieldTypeChange = (e, field) => {
    const updatedSchema = { ...jsonSchema, [field]: e.target.value };
    setJsonSchema(updatedSchema);
  };

  // Function to combine JSON example with user-modified data
  const combineJsonWithUserInput = () => {
    return {
      jsonExample,
      userFields: {
        fieldDetails,
        staticFields,
      },
    };
  };

  // Handle final submit to send data to backend
  const handleFinalSubmit = async () => {
    const combinedData = combineJsonWithUserInput();
    console.log(JSON.stringify(combinedData));
    try {
      const response = await fetch('http://127.0.0.1:5000/schema', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(combinedData),
      });
  
      if (response.ok) {
        const responseData = await response.json();
        setResultantSchema(responseData.result); // Store the resultant schema in state
        alert('Data Submitted Successfully: ' + responseData.message);
      } else {
        const errorData = await response.json();
        alert('Error submitting data: ' + errorData.error);
      }
    } catch (error) {
      console.error('Error submitting data:', error);
      alert('Error submitting data');
    }
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

          {/* Static Fields Section */}
          <div className="static-fields">
            <div className="static-field">
              <label><strong>rootDefinition</strong></label>
              <input
                type="text"
                value={staticFields.rootDefinition}
                onChange={(e) => handleStaticFieldChange(e, 'rootDefinition')}
                placeholder="Enter rootDefinition"
              />
            </div>
            <div className="static-field">
              <label><strong>rootDefinitionTitle</strong></label>
              <input
                type="text"
                value={staticFields.rootDefinitionTitle}
                onChange={(e) => handleStaticFieldChange(e, 'rootDefinitionTitle')}
                placeholder="Enter rootDefinitionTitle"
              />
            </div>
            <div className="static-field">
              <label><strong>rootDefinitionDescription</strong></label>
              <input
                type="text"
                value={staticFields.rootDefinitionDescription}
                onChange={(e) => handleStaticFieldChange(e, 'rootDefinitionDescription')}
                placeholder="Enter rootDefinitionDescription"
              />
            </div>
            <div className="static-field">
              <label><strong>schemaTitle</strong></label>
              <input
                type="text"
                value={staticFields.schemaTitle}
                onChange={(e) => handleStaticFieldChange(e, 'schemaTitle')}
                placeholder="Enter schemaTitle"
              />
            </div>
            <div className="static-field">
              <label><strong>schemaDescription</strong></label>
              <input
                type="text"
                value={staticFields.schemaDescription}
                onChange={(e) => handleStaticFieldChange(e, 'schemaDescription')}
                placeholder="Enter schemaDescription"
              />
            </div>
          </div>

          {/* Dynamic Fields for JSON Schema */}
          {Object.entries(jsonSchema).length > 0 ? (
            <div className="schema-fields">
              {Object.entries(jsonSchema).map(([field, type]) => (
                <div className="schema-field" key={field}>
                  {/* Label for Field Name (Bold, Larger Size) */}
                  <div className="field-label">
                    <strong style={{ fontSize: '18px' }}>{field}</strong>
                  </div>

                  <div className="field-title">
                    <label>Title</label>
                    <input
                      type="text"
                      value={fieldDetails[field]?.title || ''}
                      onChange={(e) => handleTitleChange(e, field)}
                      placeholder="Field title"
                    />
                  </div>

                  <div className="field-description">
                    <label>Description</label>
                    <input
                      type="text"
                      value={fieldDetails[field]?.description || ''}
                      onChange={(e) => handleDescriptionChange(e, field)}
                      placeholder="Field description"
                    />
                  </div>

                  <div className="field-type">
                    <label>Field Type</label>
                    <select
                      value={type}
                      onChange={(e) => handleFieldTypeChange(e, field)}
                    >
                      <option value="string">string</option>
                      <option value="number">number</option>
                      <option value="boolean">boolean</option>
                      <option value="object">object</option>
                      <option value="array of objects">array of objects</option>
                      <option value="array of string">array of string</option>
                      <option value="array of number">array of number</option>
                    </select>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p>Your schema will appear here...</p>
          )}
          <button onClick={handleFinalSubmit} className="submit-button">
            Submit Field Details
          </button>

          {/* Display the resultant JSON Schema */}
          {resultantSchema && (
            <div className="result-schema">
              <h2>Resultant JSON Schema</h2>
              <pre>{JSON.stringify(resultantSchema, null, 2)}</pre>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
