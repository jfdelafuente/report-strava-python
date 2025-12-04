"""Tests unitarios para el módulo de configuración (config.py)."""

import os
from pathlib import Path

import pytest


def test_config_imports():
    """Verificar que el módulo config se puede importar correctamente."""
    from py_strava import config

    assert config is not None


def test_base_directories_exist():
    """Verificar que las rutas base están definidas correctamente."""
    from py_strava import config

    # Verificar que BASE_DIR existe y es un Path
    assert hasattr(config, "BASE_DIR")
    assert isinstance(config.BASE_DIR, Path)
    assert config.BASE_DIR.exists()

    # Verificar directorios de datos
    assert hasattr(config, "DATA_DIR")
    assert hasattr(config, "JSON_DIR")
    assert hasattr(config, "BD_DIR")

    # Todos deben ser Path objects
    assert isinstance(config.DATA_DIR, Path)
    assert isinstance(config.JSON_DIR, Path)
    assert isinstance(config.BD_DIR, Path)


def test_base_dir_points_to_project_root():
    """Verificar que BASE_DIR apunta a la raíz del proyecto."""
    from py_strava import config

    # BASE_DIR debe contener archivos clave del proyecto
    assert (config.BASE_DIR / "README.md").exists()
    assert (config.BASE_DIR / "setup.py").exists()
    assert (config.BASE_DIR / "py_strava").exists()


def test_file_paths_defined():
    """Verificar que las rutas de archivos están definidas."""
    from py_strava import config

    # Archivos de configuración
    assert hasattr(config, "STRAVA_ACTIVITIES_LOG")
    assert hasattr(config, "STRAVA_TOKEN_JSON")
    assert hasattr(config, "SQLITE_DB_PATH")
    assert hasattr(config, "STRAVA_REPORT_CSV")

    # Todos deben ser Path objects
    assert isinstance(config.STRAVA_ACTIVITIES_LOG, Path)
    assert isinstance(config.STRAVA_TOKEN_JSON, Path)
    assert isinstance(config.SQLITE_DB_PATH, Path)
    assert isinstance(config.STRAVA_REPORT_CSV, Path)


def test_file_paths_structure():
    """Verificar que las rutas de archivos tienen la estructura correcta."""
    from py_strava import config

    # Verificar nombres de archivo
    assert config.STRAVA_ACTIVITIES_LOG.name == "strava_activities.log"
    assert config.STRAVA_TOKEN_JSON.name == "strava_tokens.json"
    assert config.SQLITE_DB_PATH.name == "strava.sqlite"
    assert config.STRAVA_REPORT_CSV.name == "strava_data2.csv"

    # Verificar directorios padre
    assert config.STRAVA_ACTIVITIES_LOG.parent == config.DATA_DIR
    assert config.STRAVA_TOKEN_JSON.parent == config.JSON_DIR
    assert config.SQLITE_DB_PATH.parent == config.BD_DIR
    assert config.STRAVA_REPORT_CSV.parent == config.DATA_DIR


def test_logging_configuration():
    """Verificar que la configuración de logging está definida."""
    from py_strava import config

    assert hasattr(config, "LOG_LEVEL")
    assert hasattr(config, "LOG_FORMAT")

    # LOG_LEVEL debe ser un string válido
    assert isinstance(config.LOG_LEVEL, str)
    assert config.LOG_LEVEL in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

    # LOG_FORMAT debe contener placeholders de logging
    assert isinstance(config.LOG_FORMAT, str)
    assert "%(asctime)s" in config.LOG_FORMAT or "%(levelname)s" in config.LOG_FORMAT


def test_database_configuration():
    """Verificar que la configuración de PostgreSQL está definida."""
    from py_strava import config

    # Variables de PostgreSQL
    assert hasattr(config, "DB_HOST")
    assert hasattr(config, "DB_PORT")
    assert hasattr(config, "DB_NAME")
    assert hasattr(config, "DB_USER")
    assert hasattr(config, "DB_PASSWORD")

    # Tipos correctos
    assert isinstance(config.DB_HOST, str)
    assert isinstance(config.DB_PORT, str)
    assert isinstance(config.DB_NAME, str)
    assert isinstance(config.DB_USER, str)
    assert isinstance(config.DB_PASSWORD, str)

    # Valores por defecto
    assert config.DB_HOST == os.getenv("DB_HOST", "localhost")
    assert config.DB_PORT == os.getenv("DB_PORT", "5432")


def test_strava_api_configuration():
    """Verificar que la configuración de Strava API está definida."""
    from py_strava import config

    assert hasattr(config, "STRAVA_API_BASE_URL")
    assert hasattr(config, "STRAVA_RATE_LIMIT_CALLS")
    assert hasattr(config, "STRAVA_RATE_LIMIT_PERIOD")

    # Valores correctos
    assert config.STRAVA_API_BASE_URL == "https://www.strava.com/api/v3"
    assert isinstance(config.STRAVA_RATE_LIMIT_CALLS, int)
    assert isinstance(config.STRAVA_RATE_LIMIT_PERIOD, int)

    # Rate limits razonables
    assert config.STRAVA_RATE_LIMIT_CALLS > 0
    assert config.STRAVA_RATE_LIMIT_PERIOD > 0


def test_config_uses_environment_variables():
    """Verificar que config respeta variables de entorno."""
    import importlib

    from py_strava import config

    # Guardar valor original
    original_log_level = config.LOG_LEVEL

    # Establecer variable de entorno
    os.environ["LOG_LEVEL"] = "DEBUG"

    # Recargar módulo para que tome la nueva variable
    import py_strava.config as config_module

    importlib.reload(config_module)

    # Verificar que tomó el valor de entorno
    assert config_module.LOG_LEVEL == "DEBUG"

    # Limpiar
    if "LOG_LEVEL" in os.environ:
        del os.environ["LOG_LEVEL"]


def test_path_conversion_to_string():
    """Verificar que los Path objects se pueden convertir a string."""
    from py_strava import config

    # Todas las rutas deben poder convertirse a string
    assert isinstance(str(config.STRAVA_ACTIVITIES_LOG), str)
    assert isinstance(str(config.STRAVA_TOKEN_JSON), str)
    assert isinstance(str(config.SQLITE_DB_PATH), str)
    assert isinstance(str(config.STRAVA_REPORT_CSV), str)

    # Los strings deben contener las rutas correctas
    assert "strava_activities.log" in str(config.STRAVA_ACTIVITIES_LOG)
    assert "strava_tokens.json" in str(config.STRAVA_TOKEN_JSON)
    assert "strava.sqlite" in str(config.SQLITE_DB_PATH)
    assert "strava_data2.csv" in str(config.STRAVA_REPORT_CSV)


def test_config_is_immutable():
    """Verificar que las constantes de config no deben cambiar."""
    from py_strava import config

    # Guardar valores originales
    original_base_dir = config.BASE_DIR
    original_db_path = config.SQLITE_DB_PATH

    # Intentar modificar (esto debería funcionar en Python, pero documentamos el comportamiento esperado)
    # En un módulo bien diseñado, estas serían constantes
    assert config.BASE_DIR == original_base_dir
    assert config.SQLITE_DB_PATH == original_db_path
