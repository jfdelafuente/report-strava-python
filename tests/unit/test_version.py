"""Test para verificar la versión del proyecto."""
import pytest


def test_cli_version():
    """Verificar que la versión del CLI esté definida."""
    from py_strava.cli.main import __version__

    assert __version__ == "2.2.0"
    assert isinstance(__version__, str)
    assert len(__version__) > 0


def test_version_format():
    """Verificar que el formato de la versión sea correcto."""
    from py_strava.cli.main import __version__

    # Verificar formato semver (major.minor.patch)
    parts = __version__.split(".")
    assert len(parts) == 3
    assert all(part.isdigit() for part in parts)
