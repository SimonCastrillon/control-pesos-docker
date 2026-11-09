# Imagen base oficial con versión fija (no "latest")
FROM python:3.12-slim

# Sin archivos .pyc y logs inmediatos
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Dependencias primero: esta capa se reutiliza si solo cambia el código
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Código de la aplicación
COPY src/ ./src/

# Usuario sin privilegios
RUN useradd --create-home appuser
USER appuser

# Puerto en el que escucha la API
EXPOSE 8000

# Comando de inicio: servidor de producción Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "src.app:app"]