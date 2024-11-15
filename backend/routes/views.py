from flask import jsonify, request, Response
from routes.all_code import process_json_to_schema_with_titles, schema_postprocessing
import json
def schema_converter():
    if request.method == 'POST':  # Corrected request.method
        data = request.get_json()  # Corrected request.get_json()
        json_example = data.get('json_example')
        user_input = data.get('user_input')
        json_schema = process_json_to_schema_with_titles(json_example, user_input)
        json_new = schema_postprocessing(json_schema, json_example)
        return Response(
            json.dumps(json_new, sort_keys=False),
            mimetype='application/json',
            status=201
        )
    else:
        return jsonify({'error': 'method not allowed'}), 405
