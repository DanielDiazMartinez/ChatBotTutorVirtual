#!/usr/bin/env python
"""
Herramienta de análisis de logs de contexto de Google AI
Este script permite analizar y visualizar estadísticas de los contextos enviados a Google AI.
"""
import json
import os
from pathlib import Path
import argparse
from datetime import datetime, timedelta
import pandas as pd
from tabulate import tabulate

def parse_args():
    parser = argparse.ArgumentParser(description='Analizar logs de contexto de Google AI')
    parser.add_argument('--date', type=str, default=None, help='Fecha a analizar (formato YYYY-MM-DD)')
    parser.add_argument('--days', type=int, default=7, help='Número de días a analizar desde hoy')
    parser.add_argument('--format', choices=['table', 'json', 'csv'], default='table', help='Formato de salida')
    parser.add_argument('--output', type=str, default=None, help='Archivo de salida')
    return parser.parse_args()

def load_logs(date_filter=None, days=7):
    """Carga los logs de contexto de Google AI"""
    logs_dir = Path("/home/dani/Proyectos/ChatBotTutorVirtual/backend/logs/chat/google_ai_contexts")
    
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
        return {}
    
    # Crear DataFrame para análisis
    data = []
    for log in logs:
        stats = log.get('stats', {})
        row = {
            'timestamp': log.get('timestamp'),
            'user_id': log.get('user_id'),
            'conversation_id': log.get('conversation_id'),
            'context_length': stats.get('context_length', 0),
            'context_tokens': stats.get('context_tokens', 0),
            'question_length': stats.get('question_length', 0),
            'question_tokens': stats.get('question_tokens', 0),
            'prompt_length': stats.get('prompt_length', 0),
            'prompt_tokens': stats.get('prompt_tokens', 0),
        }
        data.append(row)
    
    df = pd.DataFrame(data)
    
    # Calcular estadísticas
    analysis = {
        'total_requests': len(logs),
        'unique_users': df['user_id'].nunique() if not df.empty else 0,
        'unique_conversations': df['conversation_id'].nunique() if not df.empty else 0,
        'avg_context_length': df['context_length'].mean() if not df.empty else 0,
        'avg_context_tokens': df['context_tokens'].mean() if not df.empty else 0,
        'avg_question_length': df['question_length'].mean() if not df.empty else 0,
        'avg_question_tokens': df['question_tokens'].mean() if not df.empty else 0,
        'avg_prompt_length': df['prompt_length'].mean() if not df.empty else 0,
        'avg_prompt_tokens': df['prompt_tokens'].mean() if not df.empty else 0,
        'max_context_length': df['context_length'].max() if not df.empty else 0,
        'max_prompt_tokens': df['prompt_tokens'].max() if not df.empty else 0,
    }
    
    # Estadísticas por usuario
    if not df.empty:
        user_stats = df.groupby('user_id').agg({
            'conversation_id': 'count',
            'context_tokens': 'mean',
            'prompt_tokens': 'mean'
        }).rename(columns={'conversation_id': 'requests_count'})
        analysis['user_stats'] = user_stats.to_dict('index')
    
    return analysis

def format_output(analysis, format_type='table'):
    """Formatea la salida según el tipo especificado"""
    if format_type == 'json':
        return json.dumps(analysis, indent=2, default=str)
    
    elif format_type == 'csv':
        # Para CSV, convertimos las estadísticas principales a DataFrame
        main_stats = {k: v for k, v in analysis.items() if k != 'user_stats'}
        df = pd.DataFrame([main_stats])
        return df.to_csv(index=False)
    
    else:  # table
        output = []
        output.append("=" * 60)
        output.append("ANÁLISIS DE LOGS DE GOOGLE AI")
        output.append("=" * 60)
        output.append("")
        
        # Estadísticas generales
        output.append("ESTADÍSTICAS GENERALES:")
        output.append(f"  Total de solicitudes: {analysis['total_requests']}")
        output.append(f"  Usuarios únicos: {analysis['unique_users']}")
        output.append(f"  Conversaciones únicas: {analysis['unique_conversations']}")
        output.append("")
        
        # Estadísticas de contexto
        output.append("ESTADÍSTICAS DE CONTEXTO:")
        output.append(f"  Longitud promedio del contexto: {analysis['avg_context_length']:.2f} caracteres")
        output.append(f"  Tokens promedio del contexto: {analysis['avg_context_tokens']:.2f}")
        output.append(f"  Longitud máxima del contexto: {analysis['max_context_length']} caracteres")
        output.append("")
        
        # Estadísticas de preguntas
        output.append("ESTADÍSTICAS DE PREGUNTAS:")
        output.append(f"  Longitud promedio de preguntas: {analysis['avg_question_length']:.2f} caracteres")
        output.append(f"  Tokens promedio de preguntas: {analysis['avg_question_tokens']:.2f}")
        output.append("")
        
        # Estadísticas de prompts
        output.append("ESTADÍSTICAS DE PROMPTS:")
        output.append(f"  Longitud promedio del prompt: {analysis['avg_prompt_length']:.2f} caracteres")
        output.append(f"  Tokens promedio del prompt: {analysis['avg_prompt_tokens']:.2f}")
        output.append(f"  Tokens máximos del prompt: {analysis['max_prompt_tokens']}")
        output.append("")
        
        # Estadísticas por usuario
        if 'user_stats' in analysis and analysis['user_stats']:
            output.append("ESTADÍSTICAS POR USUARIO:")
            user_data = []
            for user_id, stats in analysis['user_stats'].items():
                user_data.append([
                    user_id,
                    stats['requests_count'],
                    f"{stats['context_tokens']:.2f}",
                    f"{stats['prompt_tokens']:.2f}"
                ])
            
            headers = ['Usuario', 'Solicitudes', 'Tokens Contexto Prom.', 'Tokens Prompt Prom.']
            table = tabulate(user_data, headers=headers, tablefmt='grid')
            output.append(table)
        
        return "\n".join(output)

def main():
    args = parse_args()
    
    print("Cargando logs de Google AI...")
    logs = load_logs(args.date, args.days)
    
    if not logs:
        print("No se encontraron logs para analizar.")
        return
    
    print(f"Analizando {len(logs)} registros...")
    analysis = analyze_logs(logs)
    
    # Formatear salida
    output = format_output(analysis, args.format)
    
    # Guardar o mostrar resultado
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"Análisis guardado en: {args.output}")
    else:
        print(output)

if __name__ == "__main__":
    main()
