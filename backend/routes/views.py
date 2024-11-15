from flask import jsonify, request
from routes.all_code import process_json_to_schema_with_titles

def schema_converter():
    if request.method == 'POST':  # Corrected request.method
        data = request.get_json()  # Corrected request.get_json()
        json_example = data.get('json_example')
        user_input = data.get('user_input')
        print(json_example)
        print(user_input)
        json_schema = process_json_to_schema_with_titles(json_example, user_input)
        return json_schema, 201
    else:
        return jsonify({'error': 'method not allowed'}), 405
