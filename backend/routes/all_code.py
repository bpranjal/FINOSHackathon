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
            ['node', 'quicktype_converter.js'],
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

# Function to update schema with user input titles, descriptions, and types
def update_schema_with_user_input(schema, user_fields, parent_key='', global_definitions=None):
    if global_definitions is None:
        global_definitions = schema.get("definitions", {})

    for key, value in schema.get("properties", {}).items():
        full_key = f"{parent_key}.{key}" if parent_key else key

        if key in user_fields:
            user_info = user_fields[key]
            value["title"] = user_info.get("title", f"Title for {key}")
            value["description"] = user_info.get("description", f"Description for the field {key}.")
            value["type"] = user_info.get("type", value.get("type"))

            if value["type"] == "object" and "fields" in user_info:
                update_schema_with_user_input(value, user_info["fields"], full_key, global_definitions)
            elif value["type"] == "array of string":
                value["type"] = "array"
                value["items"] = {"type": "string"}

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

# Sample example JSON
json_example = {
    "name": "John Doe",
    "age": 30,
    "email": "johndoe@example.com",
    "is_active": True,
    "balance": 1234.56,
    "address": {
        "street": "123 Main St",
        "city": "Anytown",
        "id": {
            "id1": "1",
            "id2": "2"
        }
    },
    "preferences": ["email", "sms"]
}

# Sample user input JSON
user_input = {
    "rootDefinition": "UserSchema",  # The name you want to give to the root definition
    "rootDefinitionTitle": "User Information Schema",  # Title for the root definition
    "rootDefinitionDescription": "This schema contains information about the user, including personal and contact details.",  # Description for the root definition
    "schemaTitle": "User Data Schema",  # Main title for the schema
    "schemaDescription": "This schema defines the structure of the user data.",  # Main description for the schema
    "fields": {
        "name": {
            "title": "User's Full Name",
            "description": "The full name of the user.",
            "type": "string"
        },
        "age": {
            "title": "User's Age",
            "description": "The age of the user in years.",
            "type": "integer",
            "abcd": "adfskj"
        },
        "email": {
            "title": "Email Address",
            "description": "The user's email address.",
            "type": "string"
        },
        "is_active": {
            "title": "Active Status",
            "description": "Indicates whether the user account is active.",
            "type": "boolean"
        },
        "balance": {
            "title": "Account Balance",
            "description": "The current balance in the user's account.",
            "type": "number"
        },
        "address": {
            "title": "User Address",
            "description": "The user's address details.",
            "type": "object",
            "fields": {
                "street": {
                    "title": "Street Address",
                    "description": "The street address of the user.",
                    "type": "string"
                },
                "city": {
                    "title": "City",
                    "description": "The city where the user resides.",
                    "type": "string"
                },
                "id": {
                    "title": "Identification",
                    "description": "Identification details for the address.",
                    "type": "object",
                    "fields": {
                        "id1": {
                            "title": "ID Part 1",
                            "description": "First part of the identification.",
                            "type": "string"
                        },
                        "id2": {
                            "title": "ID Part 2",
                            "description": "Second part of the identification.",
                            "type": "string"
                        }
                    }
                }
            }
        },
        "preferences": {
            "title": "Communication Preferences",
            "description": "User's preferred modes of communication.",
            "type": "array of string"
        }
    }
}

# Run the main function with the example JSON and user input
process_json_to_schema_with_titles(json_example, user_input)
