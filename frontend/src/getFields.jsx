function getJsonFieldTypes(jsonData, parentKey = '') {
    const fieldTypes = {};
  
    for (const [key, value] of Object.entries(jsonData)) {
      // Construct the full key for nested fields
      const fullKey = parentKey ? `${parentKey}.${key}` : key;
  
      if (typeof value === 'object' && !Array.isArray(value) && value !== null) {
        // Record the current field as an "object"
        fieldTypes[fullKey] = 'object';
        // Recursively process nested objects
        Object.assign(fieldTypes, getJsonFieldTypes(value, fullKey));
      } else if (Array.isArray(value) && value.length > 0) {
        // Check the type of elements in the array
        const elementType = typeof value[0];
        if (typeof value[0] === 'object' && value[0] !== null) {
          // If the first element is an object, process it as an "array of objects"
          fieldTypes[fullKey] = 'array of objects';
          // Recursively process the first element in the list for nested types
          Object.assign(fieldTypes, getJsonFieldTypes(value[0], fullKey));
        } else {
          // For non-object items, use the element type directly
          fieldTypes[fullKey] = `array of ${elementType}`;
        }
      } else {
        // Directly set the type for basic types and empty lists
        const fieldType = typeof value;
        fieldTypes[fullKey] = fieldType;
      }
    }
    console.log(fieldTypes);
    return fieldTypes;
  }
  

  