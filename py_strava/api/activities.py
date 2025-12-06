"""Módulo para interactuar con la API de Strava y obtener actividades y kudos.

Este módulo proporciona funciones para:
- Obtener actividades del atleta autenticado
- Obtener kudos de actividades específicas
- Manejar paginación automática de resultados
"""

import logging
from datetime import datetime
from typing import Any, Dict, Optional

import pandas as pd
import requests

# Configuración de logging
logger = logging.getLogger(__name__)

# Constantes
STRAVA_API_URL = "https://www.strava.com/api/v3"
DEFAULT_TIMEOUT = 30  # segundos
MAX_RETRIES = 3


class StravaAPIError(Exception):
    """Excepción personalizada para errores de la API de Strava."""

    pass


def request_activities(
    access_token: str, start_date: Optional[int] = None, verify_ssl: bool = True
) -> pd.DataFrame:
    """Recupera las actividades del atleta desde la API de Strava.

    Args:
        access_token: Token de acceso a la API de Strava
        start_date: Timestamp Unix opcional para obtener actividades después de esta fecha
        verify_ssl: Si debe verificar certificados SSL (False para entornos corporativos)

    Returns:
        DataFrame con las actividades obtenidas

    Raises:
        StravaAPIError: Si hay un error en la comunicación con la API
    """
    endpoint = "athlete/activities"
    activities_url = f"{STRAVA_API_URL}/{endpoint}"
    page = 1
    all_activities = []

    # Suprimir advertencia de SSL si está deshabilitado
    if not verify_ssl:
        import urllib3

        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        logger.warning("⚠️  Verificación SSL deshabilitada")

    logger.info(f"Obteniendo actividades desde Strava (start_date: {start_date or 'todas'})")

    while True:
        # Configurar headers y parámetros
        headers = {"Authorization": f"Bearer {access_token}"}
        params = {"per_page": 200, "page": page}

        if start_date:
            params["after"] = start_date

        try:
            logger.debug(f"Llamando al API Strava - {endpoint} (página {page})")

            response = requests.get(
                activities_url,
                headers=headers,
                params=params,
                timeout=DEFAULT_TIMEOUT,
                verify=verify_ssl,
            )

            # Verificar si la respuesta fue exitosa
            response.raise_for_status()

            activities_batch = response.json()

            # Si no hay más actividades, salir del loop
            if not activities_batch:
                logger.debug(f"No hay más actividades en página {page}")
                break

            logger.info(f"Página {page}: {len(activities_batch)} actividades obtenidas")

            # Agregar actividades a la lista
            all_activities.extend(activities_batch)

            # Incrementar página para la siguiente iteración
            page += 1

        except requests.exceptions.SSLError as e:
            logger.error(f"Error SSL al conectar con Strava: {e}")
            raise StravaAPIError(
                "Error de certificado SSL. Usa verify_ssl=False para entornos corporativos o "
                "consulta SSL_CERTIFICADOS.md para soluciones."
            ) from e

        except requests.exceptions.HTTPError as e:
            status_code = (
                e.response.status_code if hasattr(e.response, "status_code") else "unknown"
            )
            logger.error(f"Error HTTP {status_code} en {endpoint}: {e}")

            if status_code == 401:
                raise StravaAPIError(
                    "Token de acceso inválido o expirado. "
                    "Ejecuta: python -m py_strava.main para refrescar el token."
                ) from e
            elif status_code == 429:
                raise StravaAPIError(
                    "Límite de tasa de API excedido. Espera unos minutos antes de reintentar."
                ) from e
            else:
                raise StravaAPIError(f"Error HTTP {status_code} al obtener actividades") from e

        except requests.exceptions.RequestException as e:
            logger.error(f"Error de red al llamar a {endpoint}: {e}")
            raise StravaAPIError(f"Error de red: {e}") from e

        except Exception as e:
            logger.error(f"Error inesperado al procesar actividades: {e}")
            raise StravaAPIError(f"Error inesperado: {e}") from e

    # Convertir lista de actividades a DataFrame
    if not all_activities:
        logger.warning("No se encontraron actividades")
        return pd.DataFrame(
            columns=[
                "id",
                "name",
                "start_date_local",
                "type",
                "distance",
                "moving_time",
                "elapsed_time",
                "total_elevation_gain",
                "end_latlng",
                "kudos_count",
                "external_id",
            ]
        )

    logger.info(f"Total de actividades obtenidas: {len(all_activities)}")

    # Crear DataFrame con las columnas especificadas
    activities_df = pd.DataFrame(all_activities)

    # Asegurar que las columnas importantes existan
    required_columns = [
        "id",
        "name",
        "start_date_local",
        "type",
        "distance",
        "moving_time",
        "elapsed_time",
        "total_elevation_gain",
        "end_latlng",
        "kudos_count",
        "external_id",
    ]

    # Seleccionar solo las columnas que existen
    existing_columns = [col for col in required_columns if col in activities_df.columns]
    activities_df = activities_df[existing_columns]

    return activities_df


def request_kudos(access_token: str, activity_id: int, verify_ssl: bool = True) -> pd.DataFrame:
    """Recupera los kudos de una actividad específica desde la API de Strava.

    Args:
        access_token: Token de acceso a la API de Strava
        activity_id: ID de la actividad
        verify_ssl: Si debe verificar certificados SSL (False para entornos corporativos)

    Returns:
        DataFrame con los kudos obtenidos (firstname, lastname)

    Raises:
        StravaAPIError: Si hay un error en la comunicación con la API
    """
    endpoint = f"activities/{activity_id}/kudos"
    kudos_url = f"{STRAVA_API_URL}/{endpoint}"
    page = 1
    all_kudos = []

    # Suprimir advertencia de SSL si está deshabilitado
    if not verify_ssl:
        import urllib3

        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    logger.debug(f"Obteniendo kudos para actividad {activity_id}")

    while True:
        headers = {"Authorization": f"Bearer {access_token}"}
        params = {"per_page": 30, "page": page}

        try:
            logger.debug(f"Llamando al API Strava - {endpoint} (página {page})")

            response = requests.get(
                kudos_url,
                headers=headers,
                params=params,
                timeout=DEFAULT_TIMEOUT,
                verify=verify_ssl,
            )

            # Verificar si la respuesta fue exitosa
            response.raise_for_status()

            kudos_batch = response.json()

            # Si no hay más kudos, salir del loop
            if not kudos_batch:
                break

            # Agregar kudos a la lista
            all_kudos.extend(kudos_batch)

            # Incrementar página
            page += 1

        except requests.exceptions.SSLError as e:
            logger.error(f"Error SSL al obtener kudos para actividad {activity_id}: {e}")
            raise StravaAPIError(
                "Error de certificado SSL. Usa verify_ssl=False para entornos corporativos."
            ) from e

        except requests.exceptions.HTTPError as e:
            status_code = (
                e.response.status_code if hasattr(e.response, "status_code") else "unknown"
            )

            if status_code == 401:
                raise StravaAPIError("Token de acceso inválido o expirado") from e
            elif status_code == 404:
                logger.warning(f"Actividad {activity_id} no encontrada")
                return pd.DataFrame(columns=["firstname", "lastname"])
            else:
                logger.error(f"Error HTTP {status_code} al obtener kudos: {e}")
                raise StravaAPIError(f"Error HTTP {status_code}") from e

        except requests.exceptions.RequestException as e:
            logger.error(f"Error de red al obtener kudos: {e}")
            raise StravaAPIError(f"Error de red: {e}") from e

        except Exception as e:
            logger.error(f"Error inesperado al procesar kudos: {e}")
            raise StravaAPIError(f"Error inesperado: {e}") from e

    # Convertir lista de kudos a DataFrame
    if not all_kudos:
        return pd.DataFrame(columns=["firstname", "lastname"])

    logger.debug(f"Total de kudos obtenidos para actividad {activity_id}: {len(all_kudos)}")

    kudos_df = pd.DataFrame(all_kudos)

    # Seleccionar solo las columnas relevantes
    relevant_columns = ["firstname", "lastname"]
    existing_columns = [col for col in relevant_columns if col in kudos_df.columns]

    return kudos_df[existing_columns]


def get_activity_summary(activities_df: pd.DataFrame) -> Dict[str, Any]:
    """Genera un resumen estadístico de las actividades.

    Args:
        activities_df: DataFrame con las actividades

    Returns:
        Diccionario con estadísticas de las actividades
    """
    if activities_df.empty:
        return {
            "total_activities": 0,
            "total_distance_km": 0,
            "total_time_hours": 0,
            "activities_by_type": {},
        }

    summary = {
        "total_activities": len(activities_df),
        "total_distance_km": (
            activities_df["distance"].sum() / 1000 if "distance" in activities_df.columns else 0
        ),
        "total_time_hours": (
            activities_df["moving_time"].sum() / 3600
            if "moving_time" in activities_df.columns
            else 0
        ),
        "activities_by_type": (
            activities_df["type"].value_counts().to_dict()
            if "type" in activities_df.columns
            else {}
        ),
    }

    return summary


def format_activity_date(date_str: str) -> str:
    """Formatea una fecha de actividad de Strava a formato legible.

    Args:
        date_str: Fecha en formato ISO 8601 (ej: '2025-11-27T10:30:00Z')

    Returns:
        Fecha formateada (ej: '27/11/2025 10:30')
    """
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return dt.strftime("%d/%m/%Y %H:%M")
    except Exception:
        return date_str
