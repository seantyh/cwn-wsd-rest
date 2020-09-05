from flask import Flask
from flask_cors import CORS
from flask import request, make_response, jsonify

from .ckiptagger import tag
from .cwn_wsd import wsd

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    return "API working normally"
    
@app.route("/wsd", methods=["POST", "GET"])
def wsd_sentence():
    if request.method != "POST":
        return make_response(({"status": "bad request"}, 400))
    if request.content_type != "application/json":
        return make_response(({"status": "expect application/json"}, 400))
    in_data = request.get_json(silent=True)
    if not in_data:
        return make_response({"status": "empty input"}, 400)

    return make_response(({
        "status": "ok",
        "data": in_data        
        }, 200))

