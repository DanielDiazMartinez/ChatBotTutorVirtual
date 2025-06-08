# Test script for google_ai_logger
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
    print("Importando google_logger...")
    from app.utils.google_logger import log_google_context, log_path
    
    print(f"Configuración del logger - Path base: {log_path}")
    print(f"El directorio existe: {os.path.exists(str(log_path))}")
    
    # Probar la función de logging
    print("Probando la función log_google_context...")
    result = log_google_context(
        user_id="test_user_123", 
        conversation_id=999, 
        user_question="¿Cómo funciona el logging?", 
        context="Este es un contexto de prueba para verificar que el logging funcione correctamente.",
        conversation_history="Historia de prueba",
        prompt="Prompt de prueba"
    )
    
    print(f"Resultado de log_google_context: {result}")
    
    # Verificar que se haya creado el directorio diario
    current_date = datetime.now().strftime("%Y-%m-%d")
    daily_dir = log_path / current_date
    print(f"Comprobando directorio diario: {daily_dir}")
    print(f"El directorio diario existe: {os.path.exists(str(daily_dir))}")
    
    # Verificar que se hayan creado archivos
    if os.path.exists(str(daily_dir)):
        files = list(daily_dir.glob("*.json"))
        print(f"Archivos JSON en el directorio: {len(files)}")
        for file in files:
            print(f"  - {file.name}")
            
        # Mostrar el contenido del último archivo creado
        if files:
            latest_file = max(files, key=os.path.getctime)
            print(f"\nContenido del archivo más reciente ({latest_file.name}):")
            with open(latest_file, 'r', encoding='utf-8') as f:
                content = json.load(f)
                print(json.dumps(content, indent=2, ensure_ascii=False))
    
    print("\n✅ Test de google_logger completado exitosamente!")
    
except Exception as e:
    print(f"\n❌ Error durante el test: {str(e)}")
    print(f"Tipo de error: {type(e).__name__}")
    print("\nTraceback completo:")
    traceback.print_exc()
