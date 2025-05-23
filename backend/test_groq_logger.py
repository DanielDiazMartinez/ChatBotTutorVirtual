# Test script for groq_logger
import sys
import os
from pathlib import Path
from datetime import datetime
import json
import traceback

# Path de ejecución
current_dir = Path(os.getcwd())
print(f"Directorio actual: {current_dir}")

# Añadir el directorio de la aplicación al PYTHONPATH
sys.path.append(str(current_dir))
print(f"Añadiendo path: {current_dir}")

try:
    print("Importando groq_logger...")
    from app.utils.groq_logger import log_groq_context, log_path
    
    print(f"Configuración del logger - Path base: {log_path}")
    print(f"El directorio existe: {os.path.exists(str(log_path))}")
    
    # Probar la función de logging
    print("Probando la función log_groq_context...")
    result = log_groq_context(
        user_id="test_user_123", 
        conversation_id=999, 
        user_question="¿Cómo funciona el logging?", 
        context="Este es un contexto de prueba para verificar que el logging funcione correctamente.",
        conversation_history="Historia de prueba",
        prompt="Prompt de prueba"
    )
    
    print(f"Resultado de log_groq_context: {result}")
    
    # Verificar que se haya creado el directorio diario
    current_date = datetime.now().strftime("%Y-%m-%d")
    daily_dir = log_path / current_date
    print(f"Comprobando directorio diario: {daily_dir}")
    print(f"El directorio diario existe: {os.path.exists(str(daily_dir))}")
    
    # Listar archivos en el directorio diario
    if os.path.exists(str(daily_dir)):
        print("Archivos en el directorio diario:")
        for file in os.listdir(str(daily_dir)):
            file_path = daily_dir / file
            print(f"  - {file} ({os.path.getsize(str(file_path))} bytes)")
    
except Exception as e:
    print(f"Error durante la ejecución: {str(e)}")
    print(f"Tipo de error: {type(e).__name__}")
    print("Traceback:")
    print(traceback.format_exc())
