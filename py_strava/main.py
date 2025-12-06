"""
Script principal para sincronizar actividades de Strava con la base de datos.

ADVERTENCIA: Este módulo es un wrapper de retrocompatibilidad.
La lógica de sincronización se ha movido a py_strava.core.sync

Para nuevos desarrollos, use:
    from py_strava.core.sync import run_sync
    run_sync()

Este script realiza las siguientes operaciones:
1. Refresca el token de acceso de Strava
2. Obtiene las actividades nuevas desde la última sincronización
3. Almacena las actividades en la base de datos
4. Registra la fecha de la última sincronización
"""

import logging
import warnings

# Importar configuración centralizada
from py_strava import config

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Emitir warning de deprecación
warnings.warn(
    "py_strava.main está deprecado como módulo de lógica de negocio. "
    "Para nuevos desarrollos, use py_strava.core.sync.run_sync(). "
    "Este wrapper se mantendrá para compatibilidad pero podría ser eliminado en versiones futuras.",
    DeprecationWarning,
    stacklevel=2,
)

# Importar la lógica desde el nuevo módulo core
from py_strava.core.sync import run_sync

# Usar constantes de config.py (convertir a string para compatibilidad)
STRAVA_ACTIVITIES_LOG = str(config.STRAVA_ACTIVITIES_LOG)
STRAVA_TOKEN_JSON = str(config.STRAVA_TOKEN_JSON)
SQLITE_DB_PATH = str(config.SQLITE_DB_PATH)


def main() -> None:
    """
    Función principal que ejecuta el proceso de sincronización completo.

    Esta función mantiene compatibilidad con el código existente,
    pero delega toda la lógica a py_strava.core.sync.run_sync()
    """
    try:
        result = run_sync(
            token_file=STRAVA_TOKEN_JSON,
            activities_log=STRAVA_ACTIVITIES_LOG,
            db_path=SQLITE_DB_PATH,
        )
        logger.info(f"Sincronización completada: {result}")
    except Exception as ex:
        logger.error(f"Error en la sincronización: {ex}")
        raise


if __name__ == "__main__":
    main()
