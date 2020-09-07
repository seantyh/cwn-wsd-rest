from flask import Flask
from flask_cors import CORS
from flask import request, make_response, jsonify
from time import time

from .ckiptagger import tag, ckip_warmup
from .cwn_wsd import wsd, wsd_warmup
from .senses import get_sense_clouds, get_sense_data, get_lemma_senses

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

    t0 = time()
    tagged_list = tag(in_data["sentences"])

    t1 = time()
    wsd_list = wsd(tagged_list)

    t2 = time()
    return make_response(({
        "status": "ok",
        "data": wsd_list,
        "debug": {
            "timer": {
                "tag": int((t1-t0)*1000),
                "wsd": int((t2-t1)*1000)
                }
            }
        }, 200))

@app.route("/sense_cloud", methods=["GET"])
def sense_clouds():
    if "sids" not in request.args:
        return make_response({
            "status": "error", 
            "message": "expect sids parameter"}, 400)
    sids = request.args.get("sids").split(",")
    if not sids:
        return make_response({"status": "ok", "data": []})
    
    data = {}
    for sid in sids:
        data[sid] = get_sense_clouds(sid)
    
    return make_response({"status": "ok", "data": data})

@app.route("/lemma/<lemma>")
def lemma_senses(lemma):
    senses = get_lemma_senses(lemma)
    return make_response({"status": "ok", "data": senses})

@app.route("/sense_data/<sid>")
def sense_data(sid):
    sense_data = get_sense_data(sid)
    return make_response({"status": "ok", "data": sense_data})
