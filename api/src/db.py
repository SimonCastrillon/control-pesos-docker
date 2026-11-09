"""Acceso a PostgreSQL. Todos los datos de conexión vienen de variables de entorno."""
import os

import psycopg


def conectar():
    return psycopg.connect(
        host=os.environ["DB_HOST"],          # "db": nombre del servicio en docker-compose
        port=os.environ.get("DB_PORT", "5432"),
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )


def inicializar():
    with conectar() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS verificaciones (
                id SERIAL PRIMARY KEY,
                lote TEXT NOT NULL,
                n INTEGER NOT NULL,
                promedio DOUBLE PRECISION NOT NULL,
                unidades_defectuosas INTEGER NOT NULL,
                conforme BOOLEAN NOT NULL,
                creado_en TIMESTAMPTZ NOT NULL DEFAULT now()
            )
        """)


def info_conexion() -> dict:
    with conectar() as con:
        ip, base, version = con.execute(
            "SELECT host(inet_server_addr()), current_database(), current_setting('server_version')"
        ).fetchone()
    return {"host_configurado": os.environ["DB_HOST"], "ip_servidor": ip,
            "base_datos": base, "version_postgres": version}


def guardar(lote: str, r: dict) -> int:
    with conectar() as con:
        (nuevo_id,) = con.execute(
            "INSERT INTO verificaciones (lote, n, promedio, unidades_defectuosas, conforme) "
            "VALUES (%s, %s, %s, %s, %s) RETURNING id",
            (lote, r["n"], r["promedio"], r["unidades_defectuosas"], r["conforme"]),
        ).fetchone()
    return nuevo_id


def listar(limite: int = 50) -> list[dict]:
    with conectar() as con:
        filas = con.execute(
            "SELECT id, lote, n, promedio, unidades_defectuosas, conforme, creado_en "
            "FROM verificaciones ORDER BY id DESC LIMIT %s",
            (limite,),
        ).fetchall()
    claves = ["id", "lote", "n", "promedio", "unidades_defectuosas", "conforme", "creado_en"]
    resultado = [dict(zip(claves, f)) for f in filas]
    for r in resultado:
        r["creado_en"] = r["creado_en"].isoformat()
    return resultado