#!/usr/bin/env python
"""
Herramienta de análisis de logs de contexto de Groq
Este script permite analizar y visualizar estadísticas de los contextos enviados a Groq.
"""
import json
import os
from pathlib import Path
import argparse
from datetime import datetime, timedelta
import pandas as pd
from tabulate import tabulate

def parse_args():
    parser = argparse.ArgumentParser(description='Analizar logs de contexto de Groq')
    parser.add_argument('--date', type=str, default=None, help='Fecha a analizar (formato YYYY-MM-DD)')
    parser.add_argument('--days', type=int, default=7, help='Número de días a analizar desde hoy')
    parser.add_argument('--format', choices=['table', 'json', 'csv'], default='table', help='Formato de salida')
    parser.add_argument('--output', type=str, default=None, help='Archivo de salida')
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

def analyze_logs(logs):
    """Analiza los logs y genera estadísticas"""
    if not logs:
        print("No se encontraron logs para analizar.")
        return None
    
    # Convertir a DataFrame para facilitar el análisis
    df = pd.DataFrame([
        {
            'timestamp': log.get('timestamp'),
            'user_id': log.get('user_id'),
            'conversation_id': log.get('conversation_id'),
            'context_length': log.get('stats', {}).get('context_length', 0),
            'context_tokens': log.get('stats', {}).get('context_tokens', 0),
            'question_tokens': log.get('stats', {}).get('question_tokens', 0),
            'history_tokens': log.get('stats', {}).get('history_tokens', 0),
            'prompt_tokens': log.get('stats', {}).get('prompt_tokens', 0)
        } for log in logs
    ])
    
    # Convertir timestamp a datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['date'] = df['timestamp'].dt.date
    
    # Calcular estadísticas
    stats = {
        'total_logs': len(logs),
        'total_users': df['user_id'].nunique(),
        'total_conversations': df['conversation_id'].nunique(),
        'avg_context_length': df['context_length'].mean(),
        'avg_context_tokens': df['context_tokens'].mean(),
        'avg_question_tokens': df['question_tokens'].mean(),
        'avg_history_tokens': df['history_tokens'].mean(),
        'avg_prompt_tokens': df['prompt_tokens'].mean(),
        'max_context_tokens': df['context_tokens'].max(),
        'max_prompt_tokens': df['prompt_tokens'].max(),
        'daily_stats': df.groupby('date').agg({
            'timestamp': 'count',
            'context_tokens': 'mean',
            'prompt_tokens': 'mean'
        }).rename(columns={'timestamp': 'count'}).reset_index().to_dict('records')
    }
    
    return stats

def display_stats(stats, format_type='table', output_file=None):
    """Muestra las estadísticas en el formato especificado"""
    if not stats:
        return
    
    # Estadísticas generales
    general_stats = {
        'Total de logs': stats['total_logs'],
        'Usuarios únicos': stats['total_users'],
        'Conversaciones únicas': stats['total_conversations'],
        'Promedio de tokens de contexto': round(stats['avg_context_tokens'], 2),
        'Promedio de tokens de pregunta': round(stats['avg_question_tokens'], 2),
        'Promedio de tokens de historial': round(stats['avg_history_tokens'], 2),
        'Promedio de tokens de prompt': round(stats['avg_prompt_tokens'], 2),
        'Máximo de tokens de contexto': stats['max_context_tokens'],
        'Máximo de tokens de prompt': stats['max_prompt_tokens']
    }
    
    # Estadísticas diarias
    daily_stats = stats['daily_stats']
    
    # Formatear salida
    if format_type == 'json':
        output = json.dumps(stats, indent=2, default=str)
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(output)
        else:
            print(output)
    elif format_type == 'csv':
        df_general = pd.DataFrame([general_stats])
        df_daily = pd.DataFrame(daily_stats)
        
        if output_file:
            # Guardar en dos archivos separados
            df_general.to_csv(f"{output_file}_general.csv", index=False)
            df_daily.to_csv(f"{output_file}_daily.csv", index=False)
        else:
            print("Estadísticas generales:")
            print(df_general.to_csv(index=False))
            print("\nEstadísticas diarias:")
            print(pd.DataFrame(daily_stats).to_csv(index=False))
    else:  # table
        print("=== Estadísticas de Logs de Contexto de Groq ===\n")
        
        # Tabla de estadísticas generales
        general_table = [[k, v] for k, v in general_stats.items()]
        print(tabulate(general_table, headers=['Métrica', 'Valor'], tablefmt='grid'))
        
        print("\n=== Estadísticas Diarias ===\n")
        
        # Formatear fechas para la tabla
        daily_table = []
        for day in daily_stats:
            daily_table.append([
                day['date'],
                day['count'],
                round(day['context_tokens'], 2),
                round(day['prompt_tokens'], 2)
            ])
        
        print(tabulate(daily_table, 
                      headers=['Fecha', 'Consultas', 'Prom. Tokens Contexto', 'Prom. Tokens Prompt'], 
                      tablefmt='grid'))
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("=== Estadísticas de Logs de Contexto de Groq ===\n\n")
                f.write(tabulate(general_table, headers=['Métrica', 'Valor'], tablefmt='grid'))
                f.write("\n\n=== Estadísticas Diarias ===\n\n")
                f.write(tabulate(daily_table, 
                                headers=['Fecha', 'Consultas', 'Prom. Tokens Contexto', 'Prom. Tokens Prompt'], 
                                tablefmt='grid'))

def main():
    args = parse_args()
    logs = load_logs(args.date, args.days)
    stats = analyze_logs(logs)
    if stats:
        display_stats(stats, args.format, args.output)

if __name__ == "__main__":
    main()
