# Usa una imagen oficial de Python
FROM python:3.12-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Instala dependencias del sistema, incluyendo `postgresql-client`
RUN apt-get update && apt-get install -y postgresql-client

# Copia el archivo de dependencias primero (antes de copiar todo el código)
COPY requirements.txt .

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código de la aplicación
COPY . .

# Hacer ejecutable el script de inicio
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Exponer el puerto de la aplicación
EXPOSE 8000

# Usar el script como punto de entrada
ENTRYPOINT ["/start.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]