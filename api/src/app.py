from flask import Flask, jsonify

app = Flask(__name__)


@app.get("/salud")
def salud():
    return jsonify({"estado": "ok", "servicio": "api"})