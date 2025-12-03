"""Configuración de pytest y fixtures compartidos."""

import pytest
from pathlib import Path

@pytest.fixture
def project_root():
    """Retorna la raíz del proyecto."""
    return Path(__file__).parent.parent

@pytest.fixture
def sample_db_path(tmp_path):
    """Retorna path a BD temporal para tests."""
    return tmp_path / 'test_strava.sqlite'
