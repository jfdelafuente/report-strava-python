"""Configuración centralizada para la aplicación de Strava."""

import os
from pathlib import Path

# Rutas base
BASE_DIR = Path(__file__).parent.parent  # Subir al directorio raíz del proyecto
DATA_DIR = BASE_DIR / "data"
JSON_DIR = BASE_DIR / "json"
BD_DIR = BASE_DIR / "bd"

# Archivos de configuración
STRAVA_ACTIVITIES_LOG = DATA_DIR / "strava_activities.log"
STRAVA_TOKEN_JSON = JSON_DIR / "strava_tokens.json"
SQLITE_DB_PATH = BD_DIR / "strava.sqlite"
STRAVA_REPORT_CSV = DATA_DIR / "strava_data2.csv"

# Configuración de logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

# Configuración de la base de datos
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "strava")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# Configuración de Strava API
STRAVA_API_BASE_URL = "https://www.strava.com/api/v3"
STRAVA_RATE_LIMIT_CALLS = 100
STRAVA_RATE_LIMIT_PERIOD = 900  # 15 minutos en segundos
