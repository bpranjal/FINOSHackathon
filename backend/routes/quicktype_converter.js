const { quicktype, InputData, jsonInputForTargetLanguage } = require("quicktype-core");

async function jsonToJSONSchema(typeName, jsonString) {
    const jsonInput = jsonInputForTargetLanguage("json-schema");

    await jsonInput.addSource({
        name: typeName,
        samples: [jsonString]
    });

    const inputData = new InputData();
    inputData.addInput(jsonInput);

    const { lines } = await quicktype({
        inputData,
        lang: "json-schema"
    });

    return lines.join("\n");
}

(async () => {
    const jsonString = await new Promise((resolve, reject) => {
        let input = '';
        process.stdin.on('data', chunk => input += chunk);
        process.stdin.on('end', () => resolve(input));
        process.stdin.on('error', err => reject(err));
    });

    try {
        const jsonSchema = await jsonToJSONSchema("GeneratedSchema", jsonString);
        console.log(jsonSchema);
    } catch (error) {
        console.error("Error generating JSON Schema:", error);
    }
})();
