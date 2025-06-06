#!/usr/bin/env python3
"""
Script de prueba para verificar que el servicio de mensajes funciona correctamente
"""
import sys
import os

# Agregar el directorio padre al path para poder importar los módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import get_database_url
from app.services.message_service import get_messages_statistics, get_user_messages_with_filters

def test_message_service():
    """Probar el servicio de mensajes"""
    try:
        # Crear la conexión a la base de datos
        database_url = get_database_url()
        engine = create_engine(database_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        with SessionLocal() as db:
            print("=== Probando estadísticas sin filtros ===")
            stats = get_messages_statistics(db)
            print(f"Estadísticas: {stats}")
            
            print("\n=== Probando obtener mensajes sin filtros (límite 5) ===")
            messages = get_user_messages_with_filters(db, limit=5)
            print(f"Se obtuvieron {len(messages)} mensajes")
            for i, m in enumerate(messages[:3]):  # Mostrar solo los primeros 3
                print(f"  {i+1}. {m['text'][:50]}... - Usuario: {m['userName']}")
            
            print("\n=== Prueba completada con éxito ===")
            
    except Exception as e:
        print(f"Error en la prueba: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_message_service()
