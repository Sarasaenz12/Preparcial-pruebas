Feature: Registro de notas académicas
  Como estudiante de la Universidad Regional del Sur
  Quiero registrar mis notas por materia y semestre
  Para conocer mi situación académica y calcular mi promedio

  Background:
    Given un registro de notas vacío

  # ─── REQ-2: Aprobación y reprobación ───────────────────────────────────────

  @critical
  Scenario: Estudiante aprueba con nota exactamente en el límite
    Given el estudiante registra una nota de 3.0 en "Calculo" para el semestre "2024-1"
    When consulta si aprueba "Calculo" en "2024-1"
    Then el sistema indica que aprueba

  @critical
  Scenario: Estudiante reprueba con nota justo por debajo del límite
    Given el estudiante registra una nota de 2.9 en "Calculo" para el semestre "2024-1"
    When consulta si aprueba "Calculo" en "2024-1"
    Then el sistema indica que reprueba

  @smoke
  Scenario Outline: Verificacion de aprobacion segun diferentes notas
    Given el estudiante registra una nota de <nota> en "<materia>" para el semestre "2024-1"
    When consulta si aprueba "<materia>" en "2024-1"
    Then el sistema indica que <resultado>

    Examples:
      | nota | materia       | resultado |
      | 5.0  | Matematicas   | aprueba   |
      | 3.0  | Fisica        | aprueba   |
      | 2.9  | Quimica       | reprueba  |
      | 0.0  | Historia      | reprueba  |

  # ─── REQ-3: Promedio ────────────────────────────────────────────────────────

  @smoke
  Scenario: Promedio de estudiante sin notas registradas es cero
    When el estudiante consulta su promedio
    Then el promedio es 0.0

  @regression
  Scenario: Promedio con multiples materias calcula la media correcta
    Given el estudiante registra una nota de 3.0 en "Matematicas" para el semestre "2024-1"
    And el estudiante registra una nota de 4.0 en "Fisica" para el semestre "2024-1"
    And el estudiante registra una nota de 5.0 en "Quimica" para el semestre "2024-1"
    When el estudiante consulta su promedio
    Then el promedio es 4.0

  # ─── REQ-4: Duplicados ──────────────────────────────────────────────────────

  @critical
  Scenario: El sistema rechaza registrar la misma materia dos veces en el mismo semestre
    Given el estudiante registra una nota de 3.5 en "Matematicas" para el semestre "2024-1"
    When intenta registrar una nota de 4.0 en "Matematicas" para el semestre "2024-1"
    Then el sistema lanza un error de nota duplicada

  @regression
  Scenario: La misma materia en semestre diferente si se permite
    Given el estudiante registra una nota de 2.5 en "Matematicas" para el semestre "2024-1"
    When intenta registrar una nota de 3.8 en "Matematicas" para el semestre "2024-2"
    Then la nota queda registrada correctamente

  @regression
  Scenario: La nota original no cambia tras intentar duplicar
    Given el estudiante registra una nota de 3.5 en "Calculo" para el semestre "2024-1"
    When intenta registrar una nota de 1.0 en "Calculo" para el semestre "2024-1"
    Then el sistema lanza un error de nota duplicada
    And la nota de "Calculo" en "2024-1" sigue siendo 3.5