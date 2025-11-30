"""
Script principal para sincronizar actividades y kudos de Strava con la base de datos.

Este script realiza las siguientes operaciones:
1. Refresca el token de acceso de Strava
2. Obtiene las actividades nuevas desde la última sincronización
3. Almacena las actividades en la base de datos
4. Obtiene y almacena los kudos de cada actividad
5. Registra la fecha de la última sincronización
"""

from datetime import datetime
import csv
import logging
from typing import Optional
import pandas as pd

from py_strava.strava import strava_token as stravaToken
from py_strava.strava import strava_activities as stravaActivities
from py_strava.strava import strava_fechas as stravaFechas

# Intentar importar PostgreSQL, si no está disponible usar SQLite
try:
    from py_strava.strava import strava_db_postgres as stravaBBDD
    DB_TYPE = "PostgreSQL"
    USE_POSTGRES = True
except ImportError:
    from py_strava.strava import strava_db_sqlite as stravaBBDD
    DB_TYPE = "SQLite"
    USE_POSTGRES = False

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constantes
STRAVA_ACTIVITIES_LOG = './data/strava_activities.log'
STRAVA_TOKEN_JSON = './json/strava_tokens.json'
SQLITE_DB_PATH = './bd/strava.sqlite'  # Ruta para la base de datos SQLite

# Campos de actividades a extraer
ACTIVITY_FIELDS = [
    'id', 'name', 'start_date_local', 'type', 'distance',
    'moving_time', 'elapsed_time', 'total_elevation_gain',
    'end_latlng', 'kudos_count', 'external_id'
]

KUDOS_FIELDS = ['firstname', 'lastname']


def get_access_token(token_file: str) -> Optional[str]:
    """
    Obtiene un token de acceso válido de Strava.

    Args:
        token_file: Ruta al archivo JSON con los tokens de Strava

    Returns:
        Token de acceso válido o None si falla
    """
    try:
        current_token = stravaToken.getTokenFromFile(token_file)
        strava_tokens = stravaToken.refreshToken(current_token, token_file)
        access_token = strava_tokens['access_token']
        logger.info("Token de acceso obtenido correctamente")
        return access_token
    except Exception as ex:
        logger.error(f"Error al obtener el token de acceso: {ex}")
        return None


def get_last_sync_timestamp(log_file: str) -> int:
    """
    Obtiene el timestamp de la última sincronización.

    Args:
        log_file: Ruta al archivo de log de actividades

    Returns:
        Timestamp Unix de la última sincronización o 0 si no existe
    """
    try:
        last_time = stravaFechas.last_timestamp(log_file)
        seconds = stravaFechas.timestamp_to_unix(last_time)
        logger.info(f"Última sincronización: {last_time}")
        return seconds
    except Exception as ex:
        logger.warning(f"No se encontró registro de sincronización previa: {ex}")
        return 0


def load_activities_to_db(conn, activities: pd.DataFrame) -> int:
    """
    Carga las actividades en la base de datos usando batch insert para mejor rendimiento.

    Args:
        conn: Conexión a la base de datos
        activities: DataFrame con las actividades

    Returns:
        Número de actividades cargadas
    """
    if activities.empty:
        logger.info("No hay actividades nuevas para cargar")
        return 0

    try:
        # Preparar lista de registros para batch insert
        records = []
        for _, row in activities.iterrows():
            record = {
                'id_activity': row['id'],
                'name': row['name'],
                'start_date_local': row['start_date_local'],
                'type': row['type'],
                'distance': row['distance'],
                'moving_time': row['moving_time'],
                'elapsed_time': row['elapsed_time'],
                'total_elevation_gain': row['total_elevation_gain'],
                'end_latlng': str(row['end_latlng']),
                'kudos_count': row['kudos_count'],
                'external_id': row['external_id']
            }
            records.append(record)

        # Batch insert (20-40x más rápido que insertar una por una)
        count = stravaBBDD.insert_many(conn, "Activities", records)
        logger.info(f"{count} actividades cargadas en la base de datos (batch insert)")
        return count

    except Exception as ex:
        logger.error(f"Error al insertar actividades con batch insert: {ex}")
        logger.info("Intentando inserción individual como fallback...")

        # Fallback: insertar una por una si falla el batch
        count = 0
        for _, row in activities.iterrows():
            try:
                record = {
                    'id_activity': row['id'],
                    'name': row['name'],
                    'start_date_local': row['start_date_local'],
                    'type': row['type'],
                    'distance': row['distance'],
                    'moving_time': row['moving_time'],
                    'elapsed_time': row['elapsed_time'],
                    'total_elevation_gain': row['total_elevation_gain'],
                    'end_latlng': str(row['end_latlng']),
                    'kudos_count': row['kudos_count'],
                    'external_id': row['external_id']
                }
                stravaBBDD.insert(conn, "Activities", record)
                count += 1
            except Exception as ex:
                logger.error(f"Error al insertar actividad {row['id']}: {ex}")
                continue

        logger.info(f"{count} actividades cargadas (inserción individual)")
        return count


def load_kudos_to_db(conn, access_token: str, activity_ids: list) -> int:
    """
    Carga los kudos de las actividades en la base de datos usando batch insert.

    Args:
        conn: Conexión a la base de datos
        access_token: Token de acceso de Strava
        activity_ids: Lista de IDs de actividades

    Returns:
        Número total de kudos cargados
    """
    all_kudos_records = []

    # Recopilar todos los kudos de todas las actividades
    for activity_id in activity_ids:
        try:
            kudos = stravaActivities.request_kudos(access_token, activity_id)

            if kudos.empty:
                continue

            # Preparar registros de kudos para esta actividad
            for _, kudo_row in kudos.iterrows():
                record = {
                    'id_activity': activity_id,
                    'firstname': kudo_row['firstname'],
                    'lastname': kudo_row['lastname']
                }
                all_kudos_records.append(record)

        except Exception as ex:
            logger.error(f"Error al obtener kudos de actividad {activity_id}: {ex}")
            continue

    # Insertar todos los kudos en una sola operación batch
    if all_kudos_records:
        try:
            total_kudos = stravaBBDD.insert_many(conn, "Kudos", all_kudos_records)
            logger.info(f"{total_kudos} kudos cargados en la base de datos (batch insert)")
            return total_kudos
        except Exception as ex:
            logger.error(f"Error al insertar kudos con batch insert: {ex}")
            logger.info("Intentando inserción individual como fallback...")

            # Fallback: insertar uno por uno
            total_kudos = 0
            for record in all_kudos_records:
                try:
                    stravaBBDD.insert(conn, "Kudos", record)
                    total_kudos += 1
                except Exception as ex:
                    logger.error(f"Error al insertar kudo: {ex}")
                    continue

            logger.info(f"{total_kudos} kudos cargados (inserción individual)")
            return total_kudos
    else:
        logger.info("No hay kudos para cargar")
        return 0


def update_sync_log(log_file: str, num_activities: int) -> None:
    """
    Actualiza el log de sincronización con la fecha actual.

    Args:
        log_file: Ruta al archivo de log
        num_activities: Número de actividades procesadas
    """
    try:
        date = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        with open(log_file, 'a', newline='\n') as f:
            csv_writer = csv.writer(f)
            csv_writer.writerow([date, num_activities])
        logger.info(f"Log actualizado: {date} - {num_activities} actividades")
    except Exception as ex:
        logger.error(f"Error al actualizar el log: {ex}")


def main() -> None:
    """
    Función principal que ejecuta el proceso de sincronización completo.
    """
    logger.info("=== Inicio de sincronización de Strava ===")
    logger.info(f"Usando base de datos: {DB_TYPE}")

    # Obtener token de acceso
    access_token = get_access_token(STRAVA_TOKEN_JSON)
    if not access_token:
        logger.error("No se pudo obtener el token de acceso. Abortando.")
        return

    # Obtener timestamp de última sincronización
    last_sync = get_last_sync_timestamp(STRAVA_ACTIVITIES_LOG)

    # Obtener actividades nuevas
    try:
        logger.info("Obteniendo actividades desde Strava...")
        activities = stravaActivities.request_activities(access_token, last_sync)
        logger.info(f"{len(activities)} actividades obtenidas")
    except Exception as ex:
        logger.error(f"Error al obtener actividades: {ex}")
        return

    if activities.empty:
        logger.info("No hay actividades nuevas. Finalizando.")
        return

    # Usar context manager para manejo automático de la conexión
    try:
        # Crear context manager según el tipo de base de datos
        if USE_POSTGRES:
            logger.info("Usando PostgreSQL")
            # type: ignore - DatabaseConnection de PostgreSQL no requiere parámetros
            with stravaBBDD.DatabaseConnection() as conn:  # type: ignore
                # Cargar actividades en la base de datos
                num_loaded = load_activities_to_db(conn, activities)

                if num_loaded == 0:
                    logger.info("No se pudieron cargar actividades. Finalizando.")
                    return

                # Obtener y cargar kudos
                activity_ids = activities['id'].tolist()
                load_kudos_to_db(conn, access_token, activity_ids)

                # La conexión se cierra y commitea automáticamente al salir del context manager
                logger.info("Datos guardados exitosamente")
        else:
            logger.info(f"Usando SQLite: {SQLITE_DB_PATH}")
            # type: ignore - DatabaseConnection de SQLite requiere db_path
            with stravaBBDD.DatabaseConnection(SQLITE_DB_PATH) as conn:  # type: ignore
                # Cargar actividades en la base de datos
                num_loaded = load_activities_to_db(conn, activities)

                if num_loaded == 0:
                    logger.info("No se pudieron cargar actividades. Finalizando.")
                    return

                # Obtener y cargar kudos
                activity_ids = activities['id'].tolist()
                load_kudos_to_db(conn, access_token, activity_ids)

                # La conexión se cierra y commitea automáticamente al salir del context manager
                logger.info("Datos guardados exitosamente")

    except Exception as ex:
        logger.error(f"Error durante la sincronización: {ex}")
        return

    # Actualizar log de sincronización (fuera de la transacción DB)
    update_sync_log(STRAVA_ACTIVITIES_LOG, len(activities))

    logger.info("=== Sincronización completada exitosamente ===")


if __name__ == "__main__":
    main()
