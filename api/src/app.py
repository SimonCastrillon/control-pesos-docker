from flask import Flask, jsonify, request

from src import db
from src.logica import verificar_lote

app = Flask(__name__)


@app.get("/salud")
def salud():
    return jsonify({"estado": "ok", "servicio": "api"})


@app.get("/salud/db")
def salud_db():
    try:
        return jsonify({"estado": "ok", **db.info_conexion()})
    except Exception as e:
        return jsonify({"estado": "error", "detalle": str(e)}), 503


@app.post("/verificaciones")
def crear_verificacion():
    datos = request.get_json(silent=True) or {}
    try:
        resultado = verificar_lote(
            pesos=[float(p) for p in datos["pesos"]],
            nominal=float(datos["nominal"]),
            tolerancia=float(datos["tolerancia"]),
        )
    except (KeyError, TypeError, ValueError) as e:
        return jsonify({"error": f"datos inválidos: {e}"}), 400

    resultado["id"] = db.guardar(datos.get("lote", "sin-lote"), resultado)
    return jsonify(resultado), 201


@app.get("/verificaciones")
def listar_verificaciones():
    return jsonify(db.listar())


# Crea la tabla una sola vez al arrancar
db.inicializar()