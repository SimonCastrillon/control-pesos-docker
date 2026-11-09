"""Pruebas unitarias de las reglas de verificación de lotes."""
import pytest

from src.logica import verificar_lote

NOMINAL = 500
TOLERANCIA = 15


def test_lote_conforme():
    r = verificar_lote([500.5, 501.0, 499.8, 500.9], NOMINAL, TOLERANCIA)

    assert r["n"] == 4
    assert r["promedio"] == 500.55
    assert r["unidades_defectuosas"] == 0
    assert r["conforme"] is True


def test_promedio_bajo_no_es_conforme():
    r = verificar_lote([495, 496, 497], NOMINAL, TOLERANCIA)

    assert r["promedio"] == 496
    assert r["unidades_defectuosas"] == 0
    assert r["conforme"] is False


def test_promedio_exacto_con_unidad_bajo_el_limite_no_es_conforme():
    r = verificar_lote([510, 510, 480], NOMINAL, TOLERANCIA)

    assert r["promedio"] == NOMINAL
    assert r["unidades_defectuosas"] == 1
    assert r["conforme"] is False


def test_unidad_justo_en_el_limite_no_es_defectuosa():
    r = verificar_lote([485, 515], NOMINAL, TOLERANCIA)

    assert r["unidades_defectuosas"] == 0
    assert r["conforme"] is True


def test_calculo_del_limite_inferior():
    r = verificar_lote([500], NOMINAL, TOLERANCIA)

    assert r["limite_inferior"] == 485


def test_lista_vacia_lanza_value_error():
    with pytest.raises(ValueError):
        verificar_lote([], NOMINAL, TOLERANCIA)
