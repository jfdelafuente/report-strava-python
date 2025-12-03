"""
Script para generar informes de actividades y kudos de Strava desde la base de datos.

ADVERTENCIA: Este módulo es un wrapper de retrocompatibilidad.
La lógica de generación de informes se ha movido a py_strava.core.reports

Para nuevos desarrollos, use:
    from py_strava.core.reports import run_report
    run_report()

Este script:
1. Se conecta a la base de datos de Strava
2. Extrae información de actividades y kudos
3. Genera un archivo CSV con los datos
"""

import logging
import warnings

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Emitir warning de deprecación
warnings.warn(
    "py_strava.informe_strava está deprecado como módulo de lógica de negocio. "
    "Para nuevos desarrollos, use py_strava.core.reports.run_report(). "
    "Este wrapper se mantendrá para compatibilidad pero podría ser eliminado en versiones futuras.",
    DeprecationWarning,
    stacklevel=2
)

# Importar la lógica desde el nuevo módulo core
from py_strava.core.reports import run_report

# Constantes para compatibilidad
STRAVA_BD = 'bd/strava.sqlite'
STRAVA_DATA_CSV = 'data/strava_data2.csv'



def main() -> None:
    """
    Función principal que ejecuta la generación del informe.

    Esta función mantiene compatibilidad con el código existente,
    pero delega toda la lógica a py_strava.core.reports.run_report()
    """
    try:
        result = run_report(
            db_path=STRAVA_BD,
            output_csv=STRAVA_DATA_CSV
        )

        if result['success']:
            logger.info(f"Informe generado exitosamente en: {result['output_file']}")
        else:
            logger.error("Error al generar el informe")
    except Exception as ex:
        logger.error(f"Error en la generación del informe: {ex}")
        raise


if __name__ == "__main__":
    main()
