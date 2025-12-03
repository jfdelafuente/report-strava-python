"""
Módulo strava - Wrapper de retrocompatibilidad.

ADVERTENCIA: Este módulo está deprecado.
Los módulos se han reorganizado en la nueva estructura:

- strava_token → py_strava.api.auth
- strava_activities → py_strava.api.activities
- strava_db_sqlite → py_strava.database.sqlite
- strava_db_postgres → py_strava.database.postgres
- strava_fechas → py_strava.utils.dates

Este módulo se mantiene para compatibilidad con código existente,
pero será eliminado en una versión futura (v3.0.0).
"""

import warnings

warnings.warn(
    "El módulo 'py_strava.strava' está deprecado. "
    "Los módulos se han reorganizado: api/, database/, utils/. "
    "Actualiza tus imports a la nueva estructura.",
    DeprecationWarning,
    stacklevel=2
)
