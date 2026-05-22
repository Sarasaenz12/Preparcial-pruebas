import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../'))

import pytest
from pytest_bdd import given, when, then, scenarios, parsers
from src.registro_notas import RegistroNotas, NotaDuplicadaError

scenarios('../features/notas_academicas.feature')


@pytest.fixture
def contexto():
    return {"registro": None, "resultado": None, "error": None}


@given("un registro de notas vacío")
def registro_vacio(contexto):
    contexto["registro"] = RegistroNotas()


@given(parsers.parse('el estudiante registra una nota de {nota:g} en "{materia}" para el semestre "{semestre}"'))
def registrar_nota(contexto, nota, materia, semestre):
    contexto["registro"].registrar_nota(materia, semestre, nota)


@when(parsers.parse('consulta si aprueba "{materia}" en "{semestre}"'))
def consultar_aprobacion(contexto, materia, semestre):
    contexto["resultado"] = contexto["registro"].aprueba(materia, semestre)


@when("el estudiante consulta su promedio")
def consultar_promedio(contexto):
    contexto["resultado"] = contexto["registro"].calcular_promedio()


@when(parsers.parse('intenta registrar una nota de {nota:g} en "{materia}" para el semestre "{semestre}"'))
def intentar_registrar_nota(contexto, nota, materia, semestre):
    try:
        contexto["registro"].registrar_nota(materia, semestre, nota)
        contexto["error"] = None
    except NotaDuplicadaError as e:
        contexto["error"] = e


@then("el sistema indica que aprueba")
def indica_aprueba(contexto):
    assert contexto["resultado"] is True


@then("el sistema indica que reprueba")
def indica_reprueba(contexto):
    assert contexto["resultado"] is False


@then(parsers.parse("el promedio es {valor:g}"))
def promedio_esperado(contexto, valor):
    assert contexto["resultado"] == pytest.approx(valor)


@then("el sistema lanza un error de nota duplicada")
def error_duplicado(contexto):
    assert isinstance(contexto["error"], NotaDuplicadaError)


@then("la nota queda registrada correctamente")
def nota_registrada(contexto):
    assert contexto["error"] is None


@then(parsers.parse('la nota de "{materia}" en "{semestre}" sigue siendo {valor:g}'))
def nota_original_intacta(contexto, materia, semestre, valor):
    assert contexto["registro"].obtener_nota(materia, semestre) == pytest.approx(valor)