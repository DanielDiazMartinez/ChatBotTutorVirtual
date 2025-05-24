#!/usr/bin/env python
"""
Script para monitorear la calidad del contexto de las consultas
"""
import json
import os
from pathlib import Path
import sys
import argparse
from datetime import datetime, timedelta
import pandas as pd
# Configurar backend no interactivo antes de importar plt
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

# Configurar argumentos
def parse_args():
    parser = argparse.ArgumentParser(description='Monitorear calidad del contexto')
    parser.add_argument('--date', type=str, default=None, 
                       help='Fecha a analizar (formato YYYY-MM-DD)')
    parser.add_argument('--days', type=int, default=7, 
                       help='Número de días a analizar')
    parser.add_argument('--threshold', type=int, default=30,
                       help='Umbral de tokens mínimo para un buen contexto')
    parser.add_argument('--output', type=str, default=None,
                       help='Directorio para guardar gráficos')
    return parser.parse_args()

def load_logs(date_filter=None, days=7):
    """Carga los logs de contexto de Groq"""
    logs_dir = Path("/home/dani/Proyectos/ChatBotTutorVirtual/backend/logs/chat/groq_contexts")
    
    if not logs_dir.exists():
        print(f"El directorio {logs_dir} no existe.")
        return []
    
    logs = []
    
    if date_filter:
        # Si se especifica una fecha, solo analizamos esa carpeta
        date_dir = logs_dir / date_filter
        if date_dir.exists():
            for log_file in date_dir.glob("*.json"):
                with open(log_file, 'r', encoding='utf-8') as f:
                    try:
                        log_data = json.load(f)
                        logs.append(log_data)
                    except json.JSONDecodeError:
                        print(f"Error al leer {log_file}")
    else:
        # Si no se especifica fecha, analizamos los últimos N días
        today = datetime.now().date()
        for i in range(days):
            date_str = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            date_dir = logs_dir / date_str
            if date_dir.exists():
                for log_file in date_dir.glob("*.json"):
                    with open(log_file, 'r', encoding='utf-8') as f:
                        try:
                            log_data = json.load(f)
                            logs.append(log_data)
                        except json.JSONDecodeError:
                            print(f"Error al leer {log_file}")
    
    return logs

def analyze_context_quality(logs, threshold=30):
    """Analiza la calidad del contexto basado en el número de tokens"""
    if not logs:
        print("No se encontraron logs para analizar.")
        return None
    
    # Convertir a DataFrame
    df = pd.DataFrame([
        {
            'timestamp': log.get('timestamp'),
            'conversation_id': log.get('conversation_id'),
            'user_question': log.get('user_question', '')[:50],
            'context_tokens': log.get('stats', {}).get('context_tokens', 0),
            'context_length': log.get('stats', {}).get('context_length', 0),
            'has_context': log.get('context', '') != '',
            'question_tokens': log.get('stats', {}).get('question_tokens', 0),
        } for log in logs
    ])
    
    # Convertir timestamp a datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['date'] = df['timestamp'].dt.date
    
    # Clasificar la calidad del contexto
    df['context_quality'] = 'Sin contexto'
    df.loc[df['context_tokens'] > 0, 'context_quality'] = 'Insuficiente'
    df.loc[df['context_tokens'] >= threshold, 'context_quality'] = 'Adecuado'
    
    # Estadísticas de calidad
    quality_stats = df['context_quality'].value_counts()
    
    # Identificar consultas problemáticas
    problem_queries = df[df['context_tokens'] < threshold].sort_values('timestamp', ascending=False)
    
    return {
        'dataframe': df,
        'quality_stats': quality_stats,
        'problem_queries': problem_queries,
        'total_queries': len(df),
        'percent_with_context': (df['has_context'].sum() / len(df)) * 100,
        'percent_adequate': (df['context_quality'] == 'Adecuado').mean() * 100
    }

def generate_visualizations(analysis, output_dir=None):
    """Genera visualizaciones para la calidad del contexto"""
    if not analysis:
        return
    
    df = analysis['dataframe']
    
    # Configurar estilo
    sns.set(style="whitegrid")
    
    # Crear directorio de salida si no existe
    if not output_dir:
        output_dir = "/home/dani/Proyectos/ChatBotTutorVirtual/backend/logs/chat/analysis"
        print(f"No se especificó directorio de salida. Usando: {output_dir}")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Distribución de tokens de contexto
    plt.figure(figsize=(10, 6))
    sns.histplot(df['context_tokens'], kde=True, bins=20)
    plt.title('Distribución de Tokens de Contexto')
    plt.xlabel('Número de Tokens')
    plt.ylabel('Frecuencia')
    plt.axvline(x=30, color='r', linestyle='--', label='Umbral recomendado')
    plt.legend()
    
    # Guardar siempre el gráfico
    plt.savefig(f"{output_dir}/context_tokens_distribution.png")
    print(f"Gráfico guardado en {output_dir}/context_tokens_distribution.png")
    plt.close()
    
    # 2. Proporción de calidad de contexto
    plt.figure(figsize=(8, 8))
    quality_counts = df['context_quality'].value_counts()
    plt.pie(quality_counts, labels=quality_counts.index, autopct='%1.1f%%', 
            colors=['#ff9999','#66b3ff','#99ff99'])
    plt.title('Calidad del Contexto')
    
    # Guardar siempre el gráfico
    plt.savefig(f"{output_dir}/context_quality_pie.png")
    print(f"Gráfico guardado en {output_dir}/context_quality_pie.png")
    plt.close()
    
    # 3. Evolución temporal de la calidad
    if len(df['date'].unique()) > 1:
        plt.figure(figsize=(12, 6))
        daily_quality = df.groupby(['date', 'context_quality']).size().unstack()
        daily_quality.plot(kind='bar', stacked=True)
        plt.title('Evolución de la Calidad del Contexto por Día')
        plt.xlabel('Fecha')
        plt.ylabel('Número de Consultas')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        if output_dir:
            plt.savefig(f"{output_dir}/context_quality_evolution.png")
        else:
            plt.show()
        plt.close()

def print_recommendations(analysis):
    """Imprime recomendaciones basadas en el análisis"""
    if not analysis:
        return
    
    print("\n=== RECOMENDACIONES PARA MEJORAR LA CALIDAD DEL CONTEXTO ===\n")
    
    percent_adequate = analysis['percent_adequate']
    
    if percent_adequate < 30:
        print("⚠️ ALERTA: La mayoría de las consultas tienen contexto insuficiente o nulo.")
        print("   Esta es una situación crítica que requiere atención inmediata.")
    elif percent_adequate < 70:
        print("⚠️ Advertencia: Un porcentaje significativo de consultas tienen contexto insuficiente.")
        print("   Es recomendable revisar la configuración del sistema.")
    else:
        print("✅ La calidad del contexto es generalmente buena, pero siempre hay margen de mejora.")
    
    print("\nRecomendaciones específicas:")
    
    problem_queries = analysis['problem_queries']
    if not problem_queries.empty:
        print(f"1. Hay {len(problem_queries)} consultas con contexto insuficiente o nulo.")
        print("   Ejemplos de consultas problemáticas:")
        for _, row in problem_queries.head(3).iterrows():
            print(f"   - '{row['user_question']}...' (tokens: {row['context_tokens']})")
    
    no_context = analysis['quality_stats'].get('Sin contexto', 0)
    if no_context > 0:
        print(f"\n2. Hay {no_context} consultas sin ningún contexto.")
        print("   Posibles causas:")
        print("   - Los documentos relevantes no están cargados correctamente")
        print("   - El umbral de similitud es demasiado alto")
        print("   - Los embeddings no están funcionando correctamente")
    
    print("\n3. Acciones recomendadas:")
    
    if percent_adequate < 50:
        print("   - Aumentar el límite de chunks recuperados (de 5 a 10-15)")
        print("   - Reducir el umbral de similitud para incluir más resultados")
        print("   - Verificar que los embeddings sean de la dimensión correcta")
        print("   - Revisar los documentos cargados y su procesamiento")
    else:
        print("   - Considerar ajustes finos en los umbrales de similitud")
        print("   - Monitorear periódicamente la calidad del contexto")
    
    print("\n4. Próximos pasos:")
    print("   - Ejecutar este análisis periódicamente para monitorear mejoras")
    print("   - Revisar los logs detallados para identificar patrones")
    print("   - Considerar reentrenar o ajustar el modelo de embeddings si es necesario")

def main():
    """Función principal"""
    args = parse_args()
    
    print("=== Monitor de Calidad de Contexto ===")
    print(f"Analizando logs de los últimos {args.days} días..." if not args.date else f"Analizando logs del {args.date}...")
    
    # Verificar la ruta de logs
    logs_dir = Path("/home/dani/Proyectos/ChatBotTutorVirtual/backend/logs/chat/groq_contexts")
    if args.date:
        date_dir = logs_dir / args.date
        print(f"Buscando logs en: {date_dir}")
        if date_dir.exists():
            print(f"Directorio encontrado. Contenido: {list(date_dir.glob('*.json'))}")
        else:
            print(f"¡El directorio {date_dir} no existe!")
    
    # Cargar logs
    logs = load_logs(args.date, args.days)
    
    if not logs:
        print("No se encontraron logs para analizar.")
        return
    
    print(f"Encontrados {len(logs)} registros de logs para analizar.")
    
    # Analizar calidad del contexto
    analysis = analyze_context_quality(logs, args.threshold)
    
    # Mostrar estadísticas principales
    print("\n=== ESTADÍSTICAS DE CALIDAD DEL CONTEXTO ===\n")
    print(f"Total de consultas analizadas: {analysis['total_queries']}")
    print(f"Porcentaje con algún contexto: {analysis['percent_with_context']:.2f}%")
    print(f"Porcentaje con contexto adecuado: {analysis['percent_adequate']:.2f}%")
    print("\nDistribución de calidad:")
    print(analysis['quality_stats'])
    
    # Generar visualizaciones
    if args.output:
        print(f"\nGenerando visualizaciones en {args.output}...")
        generate_visualizations(analysis, args.output)
    else:
        print("\nGenerando visualizaciones (modo interactivo)...")
        generate_visualizations(analysis)
    
    # Imprimir recomendaciones
    print_recommendations(analysis)

if __name__ == "__main__":
    main()
