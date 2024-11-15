import json
import subprocess

# Function to extract field types from JSON
def get_json_field_types(json_data, parent_key=''):
    field_types = {}
    for key, value in json_data.items():
        full_key = f"{parent_key}.{key}" if parent_key else key
        if isinstance(value, dict):
            field_types[full_key] = "object"
            field_types.update(get_json_field_types(value, full_key))
        elif isinstance(value, list) and value:
            element_type = type(value[0]).__name__
            if isinstance(value[0], dict):
                field_types[full_key] = "array of objects"
                field_types.update(get_json_field_types(value[0], full_key))
            else:
                field_types[full_key] = f"array of {element_type}"
        else:
            field_type = "object" if isinstance(value, dict) else type(value).__name__
            field_types[full_key] = field_type
    return field_types

# Function to convert JSON to JSON Schema using Node.js script
def convert_json_to_json_schema(json_data, output_file='generated_schema.json'):
    json_string = json.dumps(json_data)

    try:
        result = subprocess.run(
            ['node', './routes/quicktype_converter.js'],
            input=json_string,
            text=True,
            capture_output=True
        )
        if result.returncode != 0:
            print("Error converting JSON to JSON Schema:", result.stderr)
            return None
        return json.loads(result.stdout)
    except Exception as e:
        print(f"Error running quicktype: {e}")
        return None

def update_schema_with_user_input(schema, user_fields, parent_key='', global_definitions=None):
    if global_definitions is None:
        global_definitions = schema.get("definitions", {})

    for key, value in schema.get("properties", {}).items():
        full_key = f"{parent_key}.{key}" if parent_key else key

        if key in user_fields:
            user_info = user_fields[key]

            # Update the schema's value with all fields from the user input
            for user_field_key, user_field_value in user_info.items():
                # If it's an "object" type and has "fields", process it recursively
                if user_field_key == "fields" and value.get("type") == "object":
                    update_schema_with_user_input(value, user_field_value, full_key, global_definitions)
                else:
                    value[user_field_key] = user_field_value

            # Special handling for arrays of strings
            if value.get("type") == "array of string":
                value["type"] = "array"
                value["items"] = {"type": "string"}

        # If the value contains a reference, update the referenced definition
        if "$ref" in value:
            ref_path = value["$ref"].split("/")[-1]
            if ref_path in global_definitions:
                update_schema_with_user_input(global_definitions[ref_path], user_fields.get(key, {}).get("fields", {}), full_key, global_definitions)

# Main function to combine everything
def process_json_to_schema_with_titles(json_example, user_input):
    # Step 1: Get the field types from the example JSON
    field_types = get_json_field_types(json_example)
    print("Extracted Field Types:", field_types)

    # Step 2: Convert the JSON example to JSON Schema
    json_schema = convert_json_to_json_schema(json_example)
    print("json_schema", json_schema)
    if json_schema is None:
        print("Error: Could not generate JSON Schema.")
        return

    # Step 3: Add titles and descriptions to the generated JSON Schema
    if "$ref" in json_schema and json_schema["$ref"].startswith("#/definitions/"):
        root_definition = json_schema["$ref"].split("/")[-1]
        if root_definition in json_schema.get("definitions", {}):
            update_schema_with_user_input(
                json_schema["definitions"][root_definition],
                user_input.get("fields", {}),
                global_definitions=json_schema.get("definitions", {}),
            )

    # Step 4: Rename the root definition and change $ref to point to the new name
    root_definition_name = user_input.get("rootDefinition", "GeneratedSchema")
    
    # Step 5: Add title and description for the root definition
    root_definition_title = user_input.get("rootDefinitionTitle", "Root Schema Title")
    root_definition_description = user_input.get("rootDefinitionDescription", "Root schema description goes here.")

    # If there's a root definition, rename it and add title and description
    if "definitions" in json_schema and root_definition in json_schema["definitions"]:
        json_schema["definitions"][root_definition_name] = json_schema["definitions"].pop(root_definition)
        json_schema["definitions"][root_definition_name]["title"] = root_definition_title
        json_schema["definitions"][root_definition_name]["description"] = root_definition_description

    # Step 6: Change the $ref to point to the new root definition
    json_schema["$ref"] = f"#/definitions/{root_definition_name}"

    # Step 7: Add title and description fields at the top of the JSON schema (after $schema and before $ref)
    json_schema["title"] = user_input.get("schemaTitle", "Default Title")
    json_schema["description"] = user_input.get("schemaDescription", "Default schema description.")
    json_schema["type"] = "object"

    # Save the updated schema to a file
    with open('updated_schema_with_titles.json', 'w') as file:
        json.dump(json_schema, file, indent=4)

    print(f"Updated JSON Schema saved to 'updated_schema_with_titles.json' with root definition '{root_definition_name}'.")
    
    return json_schema

def schema_postprocessing(original_schema, examples):
    first_level_keys = list(original_schema.keys())
    definitions_keys = list(original_schema["definitions"].keys())
    print(first_level_keys)
    schema_name = original_schema[first_level_keys[1]].split('/')[-1]
    definitions_except_root = {}
    for key in definitions_keys: 
        if key != schema_name:
            definitions_except_root[key] = original_schema["definitions"][key]
        
    new_schema = {
        first_level_keys[0]: original_schema[first_level_keys[0]],
        first_level_keys[3]: original_schema[first_level_keys[3]],
        first_level_keys[4]: original_schema[first_level_keys[4]],
        first_level_keys[5]: original_schema[first_level_keys[5]],
        "allOf": [
            original_schema[first_level_keys[2]][schema_name],
            {"$ref": "context.schema.json#/definitions/BaseContext"}
        ],
        "definitions": definitions_except_root,
        "examples" : [examples]
    }
    return new_schema