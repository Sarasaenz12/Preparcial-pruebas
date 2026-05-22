# Registro de Notas Académicas — Preparcial Pruebas de Software

Sistema de registro de notas para la Universidad Regional del Sur, construido desde cero aplicando TDD, BDD y un pipeline CI/CD en GitHub Actions.

---

## Tecnología elegida

**Python + uv + pytest + pytest-bdd**

Elegí Python porque es el lenguaje con el que más cómodo trabajo y porque el ecosistema de pytest es muy completo para hacer tanto TDD como BDD en el mismo proyecto. `uv` lo usé como gestor de dependencias porque es más rápido que pip y maneja los entornos virtuales de forma transparente.

---

## Estructura del repositorio

```
Preparcial/
├── src/
│   ├── __init__.py
│   └── registro_notas.py            # Código de producción
├── tests/
│   ├── unit/
│   │   └── test_registro_notas.py   # Tests unitarios TDD
│   └── bdd/
│       ├── features/
│       │   └── notas_academicas.feature  # Escenarios Gherkin
│       └── steps/
│           └── test_notas_steps.py  # Step definitions
├── .github/
│   └── workflows/
│       └── ci.yml                   # Pipeline GitHub Actions
├── pyproject.toml
└── README.md
```

---

## Cómo ejecutar los tests

```bash
# Instalar dependencias
uv sync

# Todos los tests con cobertura
uv run pytest tests/ -v --cov=src --cov-report=term-missing

# Solo tests unitarios
uv run pytest tests/unit/ -v

# Solo tests BDD
uv run pytest tests/bdd/ -v

# Por tag de Gherkin
uv run pytest tests/bdd/ -v -m smoke
uv run pytest tests/bdd/ -v -m critical
uv run pytest tests/bdd/ -v -m regression
```

---

## PARTE 1 — Análisis previo al código

Antes de escribir cualquier test o línea de producción, analicé los requerimientos para entender qué casos podían romperse y dónde estaban los puntos críticos del sistema.

### 1.1 — Particiones de equivalencia

La idea fue dividir todo el dominio posible de notas en grupos donde el sistema debería comportarse igual. Identifiqué 5 particiones:

| Partición | Rango | Valor representativo | Resultado esperado |
|---|---|---|---|
| Válida — rango normal | [1.0 – 4.0] | 3.5 | Nota registrada sin error |
| Válida — límite inferior exacto | 0.0 | 0.0 | Nota registrada sin error |
| Válida — límite superior exacto | 5.0 | 5.0 | Nota registrada sin error |
| Inválida — por debajo del mínimo | (−∞, 0.0) | −1.0 | `NotaInvalidaError` |
| Inválida — por encima del máximo | (5.0, +∞) | 6.0 | `NotaInvalidaError` |

Separé los bordes (0.0 y 5.0) como particiones propias porque son puntos de decisión críticos donde un operador mal escrito (`>` en vez de `>=`) haría fallar la validación de forma silenciosa.

---

### 1.2 — Análisis de valores límite 

Complementé las particiones probando los valores exactos en cada borde del rango, más el inmediatamente interior y el inmediatamente exterior:

| Valor | Posición en el rango | Resultado esperado |
|---|---|---|
| −0.1 | Justo antes del límite inferior | `NotaInvalidaError` |
| 0.0 | Límite inferior exacto | Nota registrada correctamente |
| 0.1 | Justo después del límite inferior | Nota registrada correctamente |
| 4.9 | Justo antes del límite superior | Nota registrada correctamente |
| 5.0 | Límite superior exacto | Nota registrada correctamente |
| 5.1 | Justo después del límite superior | `NotaInvalidaError` |

Este análisis me sirvió para asegurarme de que la condición de validación usara `>=` y `<=` y no `>` y `<`. Un error así es muy fácil de cometer y muy difícil de detectar sin probar el límite exacto.

---

### 1.3 — Preguntas al Product Owner 

Antes de diseñar los casos de prueba para el requerimiento de duplicados, identifiqué dos preguntas que necesitaba responder para saber exactamente qué probar.

**Pregunta 1: ¿Qué se entiende por "misma materia"? ¿La comparación es por nombre exacto y es case-sensitive, o el sistema normaliza el texto?**

Si "Matematicas" y "matematicas" son distintas para el sistema, un estudiante podría registrar dos notas para la misma asignatura real simplemente cambiando una mayúscula. Necesitaba saber si debía probar variantes de capitalización, tildes o espacios. La respuesta cambia completamente el diseño de los casos de prueba: si normaliza, hay que agregar casos con variantes; si no normaliza, los casos quedan limitados a coincidencia exacta.

**Pregunta 2: Cuando se detecta un duplicado, ¿el sistema siempre rechaza, o en algún caso podría permitir actualizar la nota?**

Si existe algún flujo de actualización (por ejemplo, si la nueva nota es mayor, o si lo autoriza un coordinador), necesitaría casos de prueba para ese camino alternativo: el happy path de actualización, los casos donde no se cumple la condición y el rechazo, y la diferencia entre actores con y sin permisos. Si siempre es rechazo total, los únicos casos relevantes son el intento fallido y verificar que la nota original no se tocó.

---

## PARTE 2 — Tabla de casos de prueba

Diseñé 19 casos de prueba antes de escribir una sola línea de código. Estos casos son el documento que le daría a cualquier tester del equipo para ejecutar las pruebas manualmente.

| ID | Requerimiento | Descripción | Precondición | Datos de entrada | Pasos | Resultado esperado | Tipo |
|---|---|---|---|---|---|---|---|
| CP-01 | REQ-1 | Nota en rango medio se registra correctamente | Registro vacío | materia="Matematicas", semestre="2024-1", nota=3.5 | 1. Llamar `registrar_nota` con los datos | Nota almacenada sin excepción | Positivo |
| CP-02 | REQ-1 | Nota en el límite inferior exacto (0.0) es válida | Registro vacío | materia="Fisica", semestre="2024-1", nota=0.0 | 1. Llamar `registrar_nota` con nota=0.0 | Nota almacenada sin excepción | Borde |
| CP-03 | REQ-1 | Nota en el límite superior exacto (5.0) es válida | Registro vacío | materia="Quimica", semestre="2024-1", nota=5.0 | 1. Llamar `registrar_nota` con nota=5.0 | Nota almacenada sin excepción | Borde |
| CP-04 | REQ-1 | Nota negativa (-0.1) lanza error | Registro vacío | materia="Matematicas", semestre="2024-1", nota=-0.1 | 1. Llamar `registrar_nota` con nota=-0.1 | Se lanza `NotaInvalidaError` | Negativo |
| CP-05 | REQ-1 | Nota mayor a 5.0 (5.1) lanza error | Registro vacío | materia="Matematicas", semestre="2024-1", nota=5.1 | 1. Llamar `registrar_nota` con nota=5.1 | Se lanza `NotaInvalidaError` | Negativo |
| CP-06 | REQ-1 | Nota extremadamente negativa (-10) lanza error | Registro vacío | materia="Historia", semestre="2024-1", nota=-10.0 | 1. Llamar `registrar_nota` con nota=-10.0 | Se lanza `NotaInvalidaError` | Negativo |
| CP-07 | REQ-1 | Nota absurdamente alta (100) lanza error | Registro vacío | materia="Historia", semestre="2024-1", nota=100.0 | 1. Llamar `registrar_nota` con nota=100.0 | Se lanza `NotaInvalidaError` | Negativo |
| CP-08 | REQ-2 | Nota exactamente 3.0 es aprobatoria | Nota 3.0 registrada en "Calculo/2024-1" | materia="Calculo", semestre="2024-1" | 1. Llamar `aprueba("Calculo", "2024-1")` | Retorna `True` | Borde |
| CP-09 | REQ-2 | Nota 2.9 está bajo el límite y reprueba | Nota 2.9 registrada en "Calculo/2024-1" | materia="Calculo", semestre="2024-1" | 1. Llamar `aprueba("Calculo", "2024-1")` | Retorna `False` | Borde |
| CP-10 | REQ-2 | Nota alta (4.5) es aprobatoria | Nota 4.5 registrada en "Programacion/2024-1" | materia="Programacion", semestre="2024-1" | 1. Llamar `aprueba("Programacion", "2024-1")` | Retorna `True` | Positivo |
| CP-11 | REQ-2 | Nota mínima (0.0) reprueba | Nota 0.0 registrada en "Estadistica/2024-1" | materia="Estadistica", semestre="2024-1" | 1. Llamar `aprueba("Estadistica", "2024-1")` | Retorna `False` | Negativo |
| CP-12 | REQ-3 | Promedio sin notas registradas es 0.0 | Registro vacío | ninguno | 1. Llamar `calcular_promedio()` | Retorna `0.0` | Borde |
| CP-13 | REQ-3 | Promedio con una sola nota es esa misma nota | Nota 4.0 en "Fisica/2024-1" | ninguno | 1. Llamar `calcular_promedio()` | Retorna `4.0` | Positivo |
| CP-14 | REQ-3 | Promedio con múltiples notas calcula la media | Notas 3.0, 4.0 y 5.0 en tres materias | ninguno | 1. Llamar `calcular_promedio()` | Retorna `4.0` | Positivo |
| CP-15 | REQ-3 | Promedio con notas extremas (0.0 y 5.0) es 2.5 | Notas 0.0 y 5.0 en dos materias | ninguno | 1. Llamar `calcular_promedio()` | Retorna `2.5` | Borde |
| CP-16 | REQ-4 | Registrar misma materia y semestre dos veces lanza error | Nota 3.5 ya registrada en "Matematicas/2024-1" | materia="Matematicas", semestre="2024-1", nota=4.0 | 1. Llamar `registrar_nota` con los mismos datos | Se lanza `NotaDuplicadaError` | Negativo |
| CP-17 | REQ-4 | Misma materia en semestre diferente sí se permite | Nota 2.5 en "Matematicas/2024-1" | materia="Matematicas", semestre="2024-2", nota=3.8 | 1. Llamar `registrar_nota("Matematicas","2024-2",3.8)` | Nota registrada; existen dos notas para "Matematicas" | Positivo |
| CP-18 | REQ-4 | Materias distintas en el mismo semestre sí se permiten | Nota en "Matematicas/2024-1" | materia="Fisica", semestre="2024-1", nota=4.0 | 1. Llamar `registrar_nota("Fisica","2024-1",4.0)` | Total de notas = 2 | Positivo |
| CP-19 | REQ-4 | Al rechazar el duplicado, la nota original no cambia | Nota 3.5 en "Calculo/2024-1" | materia="Calculo", semestre="2024-1", nota=1.0 | 1. Intentar registrar nota=1.0; 2. Verificar nota existente | Se lanza `NotaDuplicadaError`; nota original sigue siendo 3.5 | Negativo |

---

## PARTE 3 — Ciclo TDD

Implementé los 4 requerimientos siguiendo el ciclo Red-Green-Refactor. El historial de commits del repositorio evidencia cada fase:

```
[ESTRUCTURA]    Setup inicial: carpetas y pyproject.toml
[ANALISIS]      README: particiones, valores límite y preguntas al PO
[CASOS]         README: tabla de 19 casos de prueba formales
[RED-REQ1]      Tests CP-01 a CP-05: validación de rango (CP-04 y CP-05 fallan)
[GREEN-REQ1]    Implementación mínima: validación 0.0-5.0 con NotaInvalidaError
[REFACTOR-REQ1] Extrae NOTA_MINIMA, NOTA_MAXIMA y método _validar_nota()
[RED-REQ2]      Tests CP-08 a CP-11: aprobación y reprobación (fallan)
[GREEN-REQ2]    Implementación mínima de aprueba() con NOTA_APROBACION
[REFACTOR-REQ2] Extrae _obtener_nota_registrada() para centralizar acceso al dict
[RED-REQ3]      Tests CP-12 a CP-15: cálculo de promedio (fallan)
[GREEN-REQ3]    Implementación mínima de calcular_promedio()
[REFACTOR-REQ3] Extrae _hay_notas() para encapsular verificación de registro vacío
[RED-REQ4]      Tests CP-16 a CP-19: duplicados (fallan)
[GREEN-REQ4]    Implementación mínima de _verificar_duplicado() y total_notas()
[REFACTOR-REQ4] Mejora mensaje de NotaDuplicadaError mostrando la nota existente
[BDD]           Feature Gherkin con 8 escenarios + step definitions
[CI]            Pipeline GitHub Actions con cobertura mínima del 80%
```

---

## Reporte de cobertura

```
========================================== test session starts ==========================================
platform win32 -- Python 3.12.10, pytest-9.0.3, pluggy-1.6.0
plugins: bdd-8.1.0, cov-7.1.0

collected 28 items

tests/unit/test_registro_notas.py .................  [ 60%]
tests/bdd/steps/test_notas_steps.py ...........      [100%]

================================== tests coverage ==================================

Name                      Stmts   Miss  Cover   Missing
--------------------------------------------------------
src/__init__.py               0      0   100%
src/registro_notas.py        33      0   100%
--------------------------------------------------------
TOTAL                        33      0   100%

Required test coverage of 80% reached. Total coverage: 100.00%
====================================== 28 passed in 0.27s ==============================
```

**28 tests pasando | Cobertura: 100%**

---

## PARTE 6 — Reflexión

**¿Qué diferencia noté entre diseñar los casos de prueba antes de programar versus programar directamente?**

La diferencia más grande fue que al llenar la tabla de casos primero, me obligué a pensar en el sistema como un contrato: qué entra, qué sale, qué pasa cuando algo falla. Ese ejercicio me hizo descubrir preguntas que de otra forma no habría hecho hasta encontrar el bug en producción. Por ejemplo, el CP-19 (verificar que la nota original no se modifica tras el rechazo del duplicado) no lo habría pensado si me hubiera puesto a codificar directamente. Habría implementado el error y dado por hecho que la nota quedaba intacta, sin haberlo verificado nunca. La tabla me obligó a ser explícito con cada resultado esperado antes de asumir nada.

**¿Qué fue lo más difícil del ciclo TDD y cuándo sentí la tentación de saltarme un paso?**

Lo más difícil fue hacer el commit RED antes de tocar el código de producción. Cada vez que terminaba de escribir un test, ya tenía en la cabeza cómo iba a quedar la implementación y el impulso era escribirla de una vez. El momento más crítico fue en el REQ-4: la lógica de `_verificar_duplicado` era tan obvia que parecía una pérdida de tiempo hacer el commit con los tests fallando primero. Pero al resistirlo me di cuenta de que pensar en el test antes me llevó a cubrir el caso CP-19, que de otra manera probablemente habría quedado sin probar. Esa es exactamente la trampa que TDD busca evitar: implementar lo que uno cree que necesita, en lugar de lo que el comportamiento esperado realmente requiere.