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

class TestAprobacion:

    def test_CP08_nota_tres_punto_cero_exacto_aprueba(self, registro):
        registro.registrar_nota("Calculo", "2024-1", 3.0)
        assert registro.aprueba("Calculo", "2024-1") is True

    def test_CP09_nota_dos_punto_nueve_reprueba(self, registro):
        registro.registrar_nota("Calculo", "2024-1", 2.9)
        assert registro.aprueba("Calculo", "2024-1") is False

    def test_CP10_nota_alta_cuatro_punto_cinco_aprueba(self, registro):
        registro.registrar_nota("Programacion", "2024-1", 4.5)
        assert registro.aprueba("Programacion", "2024-1") is True

    def test_CP11_nota_cero_reprueba(self, registro):
        registro.registrar_nota("Estadistica", "2024-1", 0.0)
        assert registro.aprueba("Estadistica", "2024-1") is False   

class TestCalcularPromedio:

    def test_CP12_promedio_sin_notas_es_cero(self, registro):
        assert registro.calcular_promedio() == 0.0

    def test_CP13_promedio_con_una_nota_es_la_nota_misma(self, registro):
        registro.registrar_nota("Fisica", "2024-1", 4.0)
        assert registro.calcular_promedio() == 4.0

    def test_CP14_promedio_con_multiples_notas_calcula_correctamente(self, registro):
        registro.registrar_nota("Matematicas", "2024-1", 3.0)
        registro.registrar_nota("Fisica", "2024-1", 4.0)
        registro.registrar_nota("Quimica", "2024-1", 5.0)
        assert registro.calcular_promedio() == 4.0

    def test_CP15_promedio_con_notas_extremas(self, registro):
        registro.registrar_nota("A", "2024-1", 0.0)
        registro.registrar_nota("B", "2024-1", 5.0)
        assert registro.calcular_promedio() == 2.5