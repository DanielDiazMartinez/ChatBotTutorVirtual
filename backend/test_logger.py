# Test script for groq_logger
import os
from pathlib import Path
from datetime import datetime
import json

LOGS_DIR = Path("/home/dani/Proyectos/ChatBotTutorVirtual/backend/logs/chat/groq_contexts")
log_path = LOGS_DIR.resolve()

# Ensure directory exists
os.makedirs(str(LOGS_DIR), exist_ok=True)
print(f"Log directory exists: {os.path.exists(str(LOGS_DIR))}")

# Create a daily directory
current_date = datetime.now().strftime("%Y-%m-%d")
daily_dir = log_path / current_date
os.makedirs(str(daily_dir), exist_ok=True)
print(f"Daily directory exists: {os.path.exists(str(daily_dir))}")

# Create a test log file
test_file_path = str(daily_dir / "test_log.json")
test_data = {"test": "content", "timestamp": datetime.now().isoformat()}

print(f"Attempting to write to: {test_file_path}")
try:
    with open(test_file_path, 'w', encoding='utf-8') as f:
        json.dump(test_data, f, ensure_ascii=False, indent=2)
    print(f"Successfully wrote to file: {test_file_path}")
    print(f"File exists: {os.path.exists(test_file_path)}")
except Exception as e:
    print(f"Error writing to file: {str(e)}")
