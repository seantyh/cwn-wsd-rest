from flask import Flask
from flask_cors import CORS
from flask import request, make_response, jsonify

from .ckiptagger import tag, ckip_warmup
from .cwn_wsd import wsd, wsd_warmup

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    return "API working normally"

@app.route("/warmup", methods=["POST"])
def load_models():
    try:
        ckip_warmup()
        wsd_warmup()
        return make_response({"status": "warmed-up"})
    except Exception as ex:
        return make_response({
            "status": "error", 
            "message": str(ex)
            }, 500)

@app.route("/wsd", methods=["POST", "GET"])
def wsd_sentence():
    if request.method != "POST":
        return make_response(({"status": "bad request"}, 400))
    if request.content_type != "application/json":
        return make_response(({"status": "expect application/json"}, 400))
    in_data = request.get_json(silent=True)
    if not in_data:
        return make_response({"status": "empty input"}, 400)

    tagged_list = tag(in_data["sentences"])

    wsd_list = wsd(tagged_list)
    return make_response(({
        "status": "ok",
        "data": wsd_list
        }, 200))

