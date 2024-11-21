from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
# from routes.views import schema_converter
from routes.all_code import process_json_to_schema_with_titles
app = Flask(__name__)
CORS(app, supports_credentials=True)

def schema_converter(data):
    # Process the incoming data using your existing functions
    json_example = data.get("jsonExample", {})
    user_fields = data.get("userFields", {}).get("fieldDetails", {})

    # Call the process_json_to_schema_with_titles with extracted data
    schema = process_json_to_schema_with_titles(json_example, user_fields)

    # Return the processed schema
    return schema

@app.route('/schema', methods=['POST'])
def convertor_endpoint():
    try:
        data = request.json  # Get JSON data from the request
        result = schema_converter(data)
        
        # Create a proper response with CORS headers
        response = make_response(jsonify({"message": "Data submitted successfully!", "result": result}))
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:5173'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response = make_response(jsonify({"message": "Data submitted successfully!", "result": result}))
        print("final respons is:", response)
        return response
    except Exception as e:
        response = make_response(jsonify({"error": str(e)}), 400)
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:5173'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response

if __name__ == "__main__":
    app.run(debug=True, port=5000)
