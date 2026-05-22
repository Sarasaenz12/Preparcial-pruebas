class NotaInvalidaError(ValueError):
    pass

class NotaDuplicadaError(Exception):
    pass

class RegistroNotas:

    def __init__(self):
        self._notas = {}

    def registrar_nota(self, materia, semestre, nota):
        if nota < 0.0 or nota > 5.0:          # mínimo para pasar los tests
            raise NotaInvalidaError(f"Nota {nota} fuera de rango.")
        self._notas[(materia, semestre)] = nota

    def obtener_nota(self, materia, semestre):
        return self._notas[(materia, semestre)]