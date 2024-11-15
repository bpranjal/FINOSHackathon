from flask import Flask
from flask_cors import CORS
from routes.views import schema_converter

app = Flask(__name__)
cors = CORS(app, origins='*')

app.add_url_rule('/schema', 'convertor_endpoint', schema_converter, methods = ['POST'])

if __name__ == "__main__":
    app.run(debug = True, port = 8080)