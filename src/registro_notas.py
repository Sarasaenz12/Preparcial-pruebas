class NotaInvalidaError(ValueError):
    pass

class NotaDuplicadaError(Exception):
    pass

class RegistroNotas:

    NOTA_MINIMA = 0.0
    NOTA_MAXIMA = 5.0
    NOTA_APROBACION = 3.0

    def __init__(self):
        self._notas = {}

    def registrar_nota(self, materia, semestre, nota):
        self._validar_nota(nota)
        self._notas[(materia, semestre)] = nota

    def _validar_nota(self, nota):
        if nota < self.NOTA_MINIMA or nota > self.NOTA_MAXIMA:
            raise NotaInvalidaError(
                f"La nota {nota} no es valida. Debe estar entre "
                f"{self.NOTA_MINIMA} y {self.NOTA_MAXIMA}."
            )
        
    def aprueba(self, materia: str, semestre: str) -> bool:
        """Retorna True si la nota es >= 3.0."""
        return self._notas[(materia, semestre)] >= self.NOTA_APROBACION

    def obtener_nota(self, materia, semestre):
        return self._notas[(materia, semestre)]