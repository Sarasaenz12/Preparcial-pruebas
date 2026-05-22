import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from src.registro_notas import RegistroNotas, NotaInvalidaError, NotaDuplicadaError


@pytest.fixture
def registro():
    return RegistroNotas()


class TestRegistrarNota:

    def test_CP01_nota_valida_en_rango_normal_se_registra_correctamente(self, registro):
        registro.registrar_nota("Matematicas", "2024-1", 3.5)
        assert registro.obtener_nota("Matematicas", "2024-1") == 3.5

    def test_CP02_nota_cero_punto_cero_es_valida_limite_inferior(self, registro):
        registro.registrar_nota("Fisica", "2024-1", 0.0)
        assert registro.obtener_nota("Fisica", "2024-1") == 0.0

    def test_CP03_nota_cinco_punto_cero_es_valida_limite_superior(self, registro):
        registro.registrar_nota("Quimica", "2024-1", 5.0)
        assert registro.obtener_nota("Quimica", "2024-1") == 5.0

    def test_CP04_nota_negativa_lanza_error(self, registro):
        with pytest.raises(NotaInvalidaError):
            registro.registrar_nota("Matematicas", "2024-1", -0.1)

    def test_CP05_nota_mayor_a_cinco_lanza_error(self, registro):
        with pytest.raises(NotaInvalidaError):
            registro.registrar_nota("Matematicas", "2024-1", 5.1)