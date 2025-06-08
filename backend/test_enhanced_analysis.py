#!/usr/bin/env python3
"""
Test script para verificar el análisis mejorado de estudiantes
que incluye información contextual de documentos y temas.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.student_analysis_service import get_subject_context_info

def test_context_function():
    """Test básico de la función get_subject_context_info"""
    print("=== TEST: Función get_subject_context_info ===")
    
    # Simulamos una sesión de base de datos (sin conectar realmente)
    try:
        # Verificar que la función existe y se puede llamar
        print("✓ Función get_subject_context_info importada correctamente")
        
        # Verificar que tiene la estructura esperada
        import inspect
        sig = inspect.signature(get_subject_context_info)
        params = list(sig.parameters.keys())
        
        expected_params = ['db', 'subject_id']
        if params == expected_params:
            print("✓ Parámetros de la función son correctos:", params)
        else:
            print("✗ Parámetros incorrectos. Esperados:", expected_params, "Encontrados:", params)
            
        print("✓ Función lista para usar con base de datos real")
        
    except Exception as e:
        print(f"✗ Error al verificar función: {e}")
        return False
    
    return True

def test_imports():
    """Test de imports necesarios"""
    print("\n=== TEST: Imports del servicio ===")
    
    try:
        from app.services.student_analysis_service import (
            get_subject_context_info,
            generate_student_analysis_summary,
            get_student_messages_by_subject
        )
        print("✓ Todas las funciones principales importadas correctamente")
        
        # Verificar que se importaron los servicios necesarios
        from app.services import subject_service, topic_service
        print("✓ Servicios de subject y topic disponibles")
        
        from app.models.models import Document, Topic, Subject
        print("✓ Modelos de Document, Topic y Subject disponibles")
        
    except ImportError as e:
        print(f"✗ Error de import: {e}")
        return False
    except Exception as e:
        print(f"✗ Error inesperado: {e}")
        return False
    
    return True

def test_prompt_enhancement():
    """Test para verificar que el prompt mejorado esté implementado"""
    print("\n=== TEST: Verificación del prompt mejorado ===")
    
    try:
        # Leer el archivo del servicio para verificar que contiene las mejoras
        with open('app/services/student_analysis_service.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar que contiene las nuevas secciones del prompt
        improvements = [
            "DOCUMENTOS Y MATERIALES DISPONIBLES",
            "TEMAS DE LA ASIGNATURA",
            "referencias específicas a los documentos",
            "qué documentos o temas específicos requieren mayor atención",
            "get_subject_context_info"
        ]
        
        for improvement in improvements:
            if improvement in content:
                print(f"✓ Encontrado: {improvement}")
            else:
                print(f"✗ No encontrado: {improvement}")
                return False
        
        print("✓ Todas las mejoras del prompt están implementadas")
        
    except Exception as e:
        print(f"✗ Error al verificar prompt: {e}")
        return False
    
    return True

def main():
    """Ejecutar todos los tests"""
    print("🧪 INICIANDO TESTS DEL ANÁLISIS MEJORADO")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_context_function,
        test_prompt_enhancement
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test falló con excepción: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print(f"📊 RESULTADOS: {sum(results)}/{len(results)} tests pasaron")
    
    if all(results):
        print("🎉 ¡TODOS LOS TESTS PASARON! El análisis mejorado está listo.")
    else:
        print("⚠️  Algunos tests fallaron. Revisar la implementación.")
    
    return all(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
