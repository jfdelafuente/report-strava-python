"""Configuración de pytest y fixtures compartidos."""

import shutil
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def project_root():
    """Retorna la raíz del proyecto."""
    return Path(__file__).parent.parent


@pytest.fixture
def sample_db_path(tmp_path):
    """Retorna path a BD temporal para tests."""
    return tmp_path / "test_strava.sqlite"


@pytest.fixture
def temp_data_dir(tmp_path):
    """Crea un directorio temporal para archivos de datos."""
    data_dir = tmp_path / "data"
    data_dir.mkdir(exist_ok=True)
    return data_dir


@pytest.fixture
def temp_json_dir(tmp_path):
    """Crea un directorio temporal para archivos JSON."""
    json_dir = tmp_path / "json"
    json_dir.mkdir(exist_ok=True)
    return json_dir


@pytest.fixture
def temp_bd_dir(tmp_path):
    """Crea un directorio temporal para bases de datos."""
    bd_dir = tmp_path / "bd"
    bd_dir.mkdir(exist_ok=True)
    return bd_dir


@pytest.fixture
def test_database(tmp_path):
    """Crea una base de datos SQLite temporal con esquema completo."""
    from py_strava.database import schema
    from py_strava.database import sqlite as db

    db_path = tmp_path / "test.sqlite"
    conn = db.sql_connection(str(db_path))

    # Crear tablas
    db.execute(conn, schema.CREATE_TABLE_ACTIVITIES, commit=True)
    db.execute(conn, schema.CREATE_TABLE_KUDOS, commit=True)

    yield conn, str(db_path)

    conn.close()


@pytest.fixture
def sample_activity_data():
    """Retorna datos de actividad de ejemplo para tests."""
    return {
        "id_activity": 12345,
        "name": "Morning Run",
        "start_date_local": "2025-12-04 07:00:00",
        "type": "Run",
        "distance": 5000.0,
        "moving_time": 1800,
        "elapsed_time": 2000,
        "total_elevation_gain": 50.0,
        "kudos_count": 5,
    }


@pytest.fixture
def sample_kudo_data():
    """Retorna datos de kudo de ejemplo para tests."""
    return {"firstname": "John", "lastname": "Doe", "resource_state": "2", "id_activity": 12345}


@pytest.fixture
def sample_token_data():
    """Retorna datos de token de ejemplo para tests."""
    return {
        "token_type": "Bearer",
        "expires_at": 1733500000,
        "expires_in": 21600,
        "refresh_token": "test_refresh_token",
        "access_token": "test_access_token",
        "client_id": "test_client_id",
        "client_secret": "test_client_secret",
    }


@pytest.fixture
def mock_strava_activities():
    """Retorna lista de actividades mock de Strava API."""
    return [
        {
            "id": 1,
            "name": "Morning Run",
            "start_date_local": "2025-12-01T07:00:00Z",
            "type": "Run",
            "distance": 5000.0,
            "moving_time": 1800,
            "elapsed_time": 2000,
            "total_elevation_gain": 50.0,
            "end_latlng": [40.7128, -74.0060],
            "kudos_count": 3,
            "external_id": "ext_001",
        },
        {
            "id": 2,
            "name": "Evening Ride",
            "start_date_local": "2025-12-02T18:00:00Z",
            "type": "Ride",
            "distance": 20000.0,
            "moving_time": 3600,
            "elapsed_time": 4000,
            "total_elevation_gain": 200.0,
            "end_latlng": [40.7580, -73.9855],
            "kudos_count": 7,
            "external_id": "ext_002",
        },
    ]


@pytest.fixture(autouse=True)
def cleanup_test_files(tmp_path):
    """Limpia archivos temporales después de cada test."""
    yield
    # Cleanup se hace automáticamente por pytest tmp_path
