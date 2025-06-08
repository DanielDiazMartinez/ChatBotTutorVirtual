#!/usr/bin/env python3
"""
Script de prueba para verificar el formato del análisis de estudiantes
"""

import sys
import os
sys.path.append('.')

from app.services.student_analysis_service import clean_and_format_analysis_text, convert_plain_text_to_html

# Texto de ejemplo similar al que está causando problemas
test_text_with_backticks = """```html
Resumen General:
La participación en la asignatura Asignatura1 durante los últimos 30 días ha sido del 100%, con un único estudiante realizando dos preguntas.

Carencias Detectadas:
1. Consolidación de Conocimientos Teóricos: La solicitud de ejercicios de práctica sugiere una dificultad para aplicar los conceptos teóricos.
2. Visión Holística de la Asignatura: La petición de un mapa conceptual indica una necesidad de comprender las conexiones.

Recomendaciones:
- Desarrollar un Banco de Ejercicios
- Proporcionar un Mapa Conceptual
- Fomentar el Aprendizaje Activo
```"""

test_text_plain = """Resumen General:
La participación en la asignatura ha sido buena.

Carencias Detectadas:
Los estudiantes necesitan más práctica.

Recomendaciones:
1. Más ejercicios
2. Mejores recursos"""

def test_cleaning():
    print("=== PRUEBA DE LIMPIEZA DE TEXTO ===")
    
    print("\n1. Texto con backticks:")
    result1 = clean_and_format_analysis_text(test_text_with_backticks, "Matemáticas")
    print("RESULTADO:")
    print(result1)
    
    print("\n" + "="*50)
    print("\n2. Texto plano:")
    result2 = clean_and_format_analysis_text(test_text_plain, "Física")
    print("RESULTADO:")
    print(result2)
    
    print("\n" + "="*50)
    print("\n3. Conversión directa:")
    result3 = convert_plain_text_to_html(test_text_plain, "Química")
    print("RESULTADO:")
    print(result3)

if __name__ == "__main__":
    test_cleaning()
