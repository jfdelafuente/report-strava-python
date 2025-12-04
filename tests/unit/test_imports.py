"""Tests para verificar que todos los módulos se importan correctamente."""
import pytest


def test_import_cli():
    """Verificar que el módulo CLI se puede importar."""
    from py_strava.cli import main

    assert hasattr(main, "cli")


def test_import_api():
    """Verificar que el módulo API se puede importar."""
    from py_strava.api import activities, auth

    assert auth is not None
    assert activities is not None


def test_import_database():
    """Verificar que el módulo database se puede importar."""
    from py_strava.database import schema, sqlite

    assert sqlite is not None
    assert schema is not None


def test_import_core():
    """Verificar que el módulo core se puede importar."""
    from py_strava.core import reports, sync

    assert sync is not None
    assert reports is not None


def test_import_utils():
    """Verificar que el módulo utils se puede importar."""
    from py_strava.utils import dates

    assert dates is not None


def test_import_config():
    """Verificar que el módulo config se puede importar."""
    from py_strava import config

    assert config is not None
