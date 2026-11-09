"""Reglas de verificación de lotes. No depende de Flask ni de la base de datos."""
from statistics import mean


def verificar_lote(pesos: list[float], nominal: float, tolerancia: float) -> dict:
    """Criterio didáctico: el lote es conforme si el promedio >= nominal
    y ninguna unidad pesa menos que (nominal - tolerancia)."""
    if not pesos:
        raise ValueError("la lista de pesos está vacía")
    if nominal <= 0 or tolerancia < 0:
        raise ValueError("nominal debe ser > 0 y tolerancia >= 0")

    limite_inferior = nominal - tolerancia
    defectuosas = sum(1 for p in pesos if p < limite_inferior)
    promedio = mean(pesos)

    return {
        "n": len(pesos),
        "promedio": round(promedio, 3),
        "limite_inferior": round(limite_inferior, 3),
        "unidades_defectuosas": defectuosas,
        "conforme": promedio >= nominal and defectuosas == 0,
    }