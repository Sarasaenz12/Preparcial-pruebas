## TECNOLOGIAS UTILIZADAS
**Python + pytest + pytest-bdd**

---

## Estructura del repositorio

```
notas-academicas/
├── src/
│   ├── __init__.py
│   └── registro_notas.py        # Código de producción
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
│       └── ci.yml               # Pipeline GitHub Actions
├── pyproject.toml
└── README.md
```

---

## PARTE 1 — Análisis escrito

### 1.1 — Particiones de equivalencia (Requerimiento 1: nota entre 0.0 y 5.0)

| Partición | Rango | Valor representativo | Resultado esperado |
|---|---|---|---|
| Válida — rango normal | [1.0 – 4.0] | 3.5 | Nota registrada sin error |
| Válida — límite inferior exacto | 0.0 | 0.0 | Nota registrada sin error |
| Válida — límite superior exacto | 5.0 | 5.0 | Nota registrada sin error |
| Inválida — por debajo del mínimo | (−∞, 0.0) | −1.0 | Nota invalida |
| Inválida — por encima del máximo | (5.0, +∞) | 6.0 | Nota invalida |

**Justificación:** Se identifican 3 particiones válidas (incluyendo los bordes como particiones propias porque son puntos de decisión críticos) y 2 inválidas que cubren todo el dominio fuera del rango permitido. Un valor representativo por partición es suficiente porque se asume que el comportamiento es uniforme dentro de cada partición.

---

### 1.2 — Análisis de valores límite (Requerimiento 1)

| Valor | Posición en el rango | Resultado esperado |
|---|---|---|
| −0.1 | Justo antes del límite inferior | `NotaInvalidaError` — fuera de rango |
| 0.0 | Límite inferior exacto | Nota registrada correctamente |
| 0.1 | Justo después del límite inferior | Nota registrada correctamente |
| 4.9 | Justo antes del límite superior | Nota registrada correctamente |
| 5.0 | Límite superior exacto | Nota registrada correctamente |
| 5.1 | Justo después del límite superior | `NotaInvalidaError` — fuera de rango |

**Justificación:** El análisis de valores límite complementa las particiones porque los errores de programación se concentran en los bordes (usar `>` en lugar de `>=`, por ejemplo). Probar el valor exacto del límite, el inmediatamente interior y el inmediatamente exterior garantiza que la condición de validación está codificada con el operador correcto.

---

### 1.3 — Preguntas al Product Owner (Requerimiento 4: no duplicar nota)

**Pregunta 1: ¿Qué se entiende por "misma materia"? ¿El sistema distingue por código de materia, por nombre exacto, o es case-insensitive?**

*Impacto en el diseño de pruebas:* Si la comparación es por nombre exacto y case-sensitive, "Matematicas" y "matematicas" serían materias distintas, lo que permitiría registrar dos notas para la misma asignatura real. Necesitamos saber si debemos probar variaciones de mayúsculas/minúsculas, tildes o espacios. Si el sistema normaliza el nombre, los casos de prueba deben incluir esas variantes; si no normaliza, los casos quedan limitados a coincidencia exacta.

**Pregunta 2: Si se detecta el duplicado, ¿el sistema debería ofrecer la posibilidad de actualizar la nota existente, o siempre debe rechazarlo sin excepción?**

*Impacto en el diseño de pruebas:* Si existe un flujo de "actualización permitida bajo ciertas condiciones" (por ejemplo, solo si la nota anterior es inferior, o solo si un administrador lo autoriza), necesitamos casos de prueba para ese flujo alternativo: el happy path de actualización, el caso donde no cumple la condición y debe seguir rechazándose, y el caso del actor con permisos vs. sin permisos. Si siempre es rechazo total, los únicos casos son el intento fallido y la verificación de que la nota original no se modificó.

---

## PARTE 2 — Tabla de casos de prueba

| ID | Requerimiento | Descripción | Precondición | Datos de entrada | Pasos | Resultado esperado | Tipo |
|---|---|---|---|---|---|---|---|
| CP-01 | REQ-1 | Nota en rango medio se registra correctamente | Registro vacío | materia="Matematicas", semestre="2024-1", nota=3.5 | 1. Llamar `registrar_nota` con los datos | Nota almacenada sin excepción | Positivo |
| CP-02 | REQ-1 | Nota en el límite inferior exacto (0.0) es válida | Registro vacío | materia="Fisica", semestre="2024-1", nota=0.0 | 1. Llamar `registrar_nota` con nota=0.0 | Nota almacenada sin excepción | Borde |
| CP-03 | REQ-1 | Nota en el límite superior exacto (5.0) es válida | Registro vacío | materia="Quimica", semestre="2024-1", nota=5.0 | 1. Llamar `registrar_nota` con nota=5.0 | Nota almacenada sin excepción | Borde |
| CP-04 | REQ-1 | Nota negativa (-0.1) lanza error | Registro vacío | materia="Matematicas", semestre="2024-1", nota=-0.1 | 1. Llamar `registrar_nota` con nota=-0.1 | Se lanza `NotaInvalidaError` | Negativo |
| CP-05 | REQ-1 | Nota mayor a 5.0 (5.1) lanza error | Registro vacío | materia="Matematicas", semestre="2024-1", nota=5.1 | 1. Llamar `registrar_nota` con nota=5.1 | Se lanza `NotaInvalidaError` | Negativo |
| CP-06 | REQ-1 | Nota extremadamente fuera de rango (-10) lanza error | Registro vacío | materia="Historia", semestre="2024-1", nota=-10.0 | 1. Llamar `registrar_nota` con nota=-10.0 | Se lanza `NotaInvalidaError` | Negativo |
| CP-07 | REQ-1 | Nota absurdamente alta (100) lanza error | Registro vacío | materia="Historia", semestre="2024-1", nota=100.0 | 1. Llamar `registrar_nota` con nota=100.0 | Se lanza `NotaInvalidaError` | Negativo |
| CP-08 | REQ-2 | Nota exactamente 3.0 es aprobatoria | Nota 3.0 registrada en "Calculo/2024-1" | materia="Calculo", semestre="2024-1" | 1. Llamar `aprueba("Calculo", "2024-1")` | Retorna `True` | Borde |
| CP-09 | REQ-2 | Nota 2.9 (bajo el límite) es reprobatoria | Nota 2.9 registrada en "Calculo/2024-1" | materia="Calculo", semestre="2024-1" | 1. Llamar `aprueba("Calculo", "2024-1")` | Retorna `False` | Borde |
| CP-10 | REQ-2 | Nota alta (4.5) es aprobatoria | Nota 4.5 registrada en "Programacion/2024-1" | materia="Programacion", semestre="2024-1" | 1. Llamar `aprueba("Programacion", "2024-1")` | Retorna `True` | Positivo |
| CP-11 | REQ-2 | Nota mínima (0.0) es reprobatoria | Nota 0.0 registrada en "Estadistica/2024-1" | materia="Estadistica", semestre="2024-1" | 1. Llamar `aprueba("Estadistica", "2024-1")` | Retorna `False` | Negativo |
| CP-12 | REQ-3 | Promedio con cero notas es 0.0 | Registro vacío | ninguno | 1. Llamar `calcular_promedio()` | Retorna `0.0` | Borde |
| CP-13 | REQ-3 | Promedio con una nota es esa misma nota | Nota 4.0 en "Fisica/2024-1" | ninguno | 1. Llamar `calcular_promedio()` | Retorna `4.0` | Positivo |
| CP-14 | REQ-3 | Promedio con múltiples notas calcula media aritmética | Notas 3.0, 4.0 y 5.0 en tres materias | ninguno | 1. Llamar `calcular_promedio()` | Retorna `4.0` | Positivo |
| CP-15 | REQ-3 | Promedio con notas extremas (0.0 y 5.0) es 2.5 | Notas 0.0 y 5.0 en dos materias | ninguno | 1. Llamar `calcular_promedio()` | Retorna `2.5` | Borde |
| CP-16 | REQ-4 | Registrar misma materia/semestre dos veces lanza error | Nota 3.5 ya registrada en "Matematicas/2024-1" | materia="Matematicas", semestre="2024-1", nota=4.0 | 1. Llamar `registrar_nota` con los mismos datos | Se lanza `NotaDuplicadaError` | Negativo |
| CP-17 | REQ-4 | Misma materia en semestre diferente SÍ se permite | Nota 2.5 en "Matematicas/2024-1" | materia="Matematicas", semestre="2024-2", nota=3.8 | 1. Llamar `registrar_nota("Matematicas","2024-2",3.8)` | Nota registrada sin excepción; existen dos notas para "Matematicas" | Positivo |
| CP-18 | REQ-4 | Diferentes materias en el mismo semestre SÍ se permiten | Nota en "Matematicas/2024-1" | materia="Fisica", semestre="2024-1", nota=4.0 | 1. Llamar `registrar_nota("Fisica","2024-1",4.0)` | Total de notas = 2 | Positivo |
| CP-19 | REQ-4 | Al rechazar duplicado, la nota original no se modifica | Nota 3.5 en "Calculo/2024-1" | materia="Calculo", semestre="2024-1", nota=1.0 | 1. Intentar registrar nota=1.0; 2. Verificar nota existente | Se lanza `NotaDuplicadaError`; nota original sigue siendo 3.5 | Negativo |

---

## Reporte de cobertura

```
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.0.3, pluggy-1.6.0
plugins: cov-7.1.0, bdd-8.1.0

collected 36 items

tests/unit/test_registro_notas.py  ......................   [ 63%]
tests/bdd/steps/test_notas_steps.py  .............         [100%]

================================ tests coverage ================================

Name                    Stmts   Miss  Cover   Missing
-----------------------------------------------------
src/__init__.py             0      0   100%
src/registro_notas.py      31      0   100%
-----------------------------------------------------
TOTAL                      31      0   100%

Required test coverage of 85% reached. Total coverage: 100.00%
============================== 36 passed in 0.21s ==============================
```

**36 tests pasando | Cobertura: 100%**

---

## PARTE 3 — Ciclo TDD — Historial de commits esperado

El repositorio debe mostrar la siguiente secuencia de commits que evidencia el ciclo Red-Green-Refactor aplicado por requerimiento:

```
[ESTRUCTURA] Setup inicial: estructura de carpetas y pyproject.toml
[ANÁLISIS]   README: particiones, valores límite y preguntas al PO
[CASOS]      README: tabla de 19 casos de prueba formales
[RED-REQ1]   Tests unitarios para validación de nota (fallan: no hay impl)
[GREEN-REQ1] Implementación mínima: NotaInvalidaError y validar_nota()
[REFACTOR-REQ1] Extrae constantes NOTA_MINIMA y NOTA_MAXIMA, mejora mensaje
[RED-REQ2]   Tests para aprobación/reprobación (fallan)
[GREEN-REQ2] Implementación mínima de aprueba()
[REFACTOR-REQ2] Extrae constante NOTA_APROBACION, mejora legibilidad
[RED-REQ3]   Tests para calcular_promedio (fallan)
[GREEN-REQ3] Implementación mínima de calcular_promedio()
[REFACTOR-REQ3] Manejo explícito de registro vacío
[RED-REQ4]   Tests para duplicados (fallan)
[GREEN-REQ4] Implementación mínima: _verificar_duplicado()
[REFACTOR-REQ4] Extrae lógica a método privado, mejora mensaje de error
[BDD]        Feature Gherkin con 13 escenarios + step definitions
[CI]         Pipeline GitHub Actions con cobertura >= 80%
```

---

## Cómo ejecutar los tests

```bash
# Instalar dependencias
pip install pytest pytest-bdd pytest-cov

# Todos los tests con cobertura
python -m pytest tests/ -v --cov=src --cov-report=term-missing

# Solo tests unitarios
python -m pytest tests/unit/ -v

# Solo tests BDD
python -m pytest tests/bdd/ -v

# Por tag de Gherkin
python -m pytest tests/bdd/ -v -m smoke
python -m pytest tests/bdd/ -v -m critical
```

---

## PARTE 6 — Reflexión

**¿Qué diferencia noté entre diseñar los casos de prueba antes de programar versus programar directamente?**

Diseñar la tabla de casos de prueba antes de escribir código obligó a pensar en el comportamiento del sistema como un contrato, no como una implementación. Al llenar cada fila —precondición, datos de entrada, pasos, resultado esperado— surgieron preguntas que de otro modo habrían quedado sin respuesta hasta encontrar el bug en producción: ¿qué pasa si no hay notas registradas? ¿qué ocurre si la nota duplicada tiene mejor calificación? Esa claridad previa hizo que la implementación fuera directa; el código siguió la especificación en lugar de inventarla mientras se tecleaba. Programar sin esa tabla habría significado descubrir los casos borde de forma accidental.

**¿Qué fue lo más difícil del ciclo TDD y cuándo sentí la tentación de saltarme un paso?**

Lo más difícil fue sostener la disciplina de la fase RED: escribir tests que fallan y hacer commit antes de escribir una sola línea de producción. La tentación constante fue implementar mientras se escribía el test, porque ya "se sabía" cómo quedaría el código. El momento más crítico fue al implementar el requerimiento 4 (duplicados): la lógica de verificación era tan obvia que el impulso de escribirla directamente fue fuerte. Resistirlo fue útil porque obligó a pensar primero en qué condiciones exactas hacen fallar el test, y eso llevó a cubrir el caso CP-19 (nota original intacta tras el rechazo) que de otro modo probablemente habría quedado sin probar.