"""
Script para obtener actividades de Strava y exportarlas a CSV.

Este script obtiene las actividades del atleta autenticado y las guarda en un archivo CSV.

Uso:
    python -m py_strava.ejemplos.strava_activities_1

Requisitos:
    - Token de acceso válido en json/strava_tokens.json
    - Ejecutar primero: python -m py_strava.ejemplos.acces_token_strava

Argumentos opcionales:
    --no-ssl: Desactiva verificación SSL (usar solo en redes corporativas)
    --per-page: Número de actividades por página (default: 200)
    --output: Ruta del archivo CSV de salida (default: data/strava_activities_all_fields.csv)
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
import requests

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuración
STRAVA_ACTIVITIES_URL = "https://www.strava.com/api/v3/athlete/activities"
TOKEN_FILE = './json/strava_tokens.json'
DEFAULT_OUTPUT = './data/strava_activities_all_fields.csv'
DEFAULT_PER_PAGE = 200


def load_tokens(token_file: str) -> Optional[Dict]:
    """
    Carga los tokens de acceso desde el archivo JSON.

    Args:
        token_file: Ruta del archivo de tokens

    Returns:
        Diccionario con los tokens o None si falla
    """
    try:
        token_path = Path(token_file)

        if not token_path.exists():
            logger.error(f"Archivo de tokens no encontrado: {token_file}")
            logger.error("Primero ejecuta: python -m py_strava.ejemplos.acces_token_strava")
            return None

        with open(token_path, 'r', encoding='utf-8') as f:
            tokens = json.load(f)

        # Verificar que el token de acceso existe
        if 'access_token' not in tokens or not tokens['access_token']:
            logger.error("No se encontró access_token en el archivo")
            logger.error("El token puede haber expirado. Ejecuta: python -m py_strava.main")
            return None

        logger.info("Tokens cargados correctamente")
        return tokens

    except json.JSONDecodeError as e:
        logger.error(f"Error al decodificar el archivo JSON: {e}")
        return None
    except Exception as e:
        logger.error(f"Error al cargar tokens: {e}")
        return None


def get_activities(access_token: str, per_page: int = 200, verify_ssl: bool = True) -> Optional[List[Dict]]:
    """
    Obtiene las actividades del atleta desde la API de Strava.

    Args:
        access_token: Token de acceso a la API
        per_page: Número de actividades por página
        verify_ssl: Si debe verificar certificados SSL

    Returns:
        Lista de actividades o None si falla
    """
    logger.info("Obteniendo actividades desde Strava...")

    # Suprimir advertencia de SSL si está deshabilitado
    if not verify_ssl:
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        logger.warning("⚠️  Verificación SSL deshabilitada")

    try:
        headers = {'Authorization': f'Bearer {access_token}'}
        params = {'per_page': per_page, 'page': 1}

        response = requests.get(
            STRAVA_ACTIVITIES_URL,
            headers=headers,
            params=params,
            timeout=30,
            verify=verify_ssl
        )

        # Verificar si la respuesta fue exitosa
        response.raise_for_status()

        activities = response.json()

        if not activities:
            logger.warning("No se encontraron actividades")
            return []

        logger.info(f"✅ {len(activities)} actividades obtenidas")
        return activities

    except requests.exceptions.SSLError as e:
        logger.error(f"Error SSL al conectar con Strava: {e}")
        logger.error("\n⚠️  PROBLEMA DE CERTIFICADO SSL DETECTADO")
        logger.error("Esto suele ocurrir en redes corporativas o con proxies.")
        logger.error("\nSoluciones:")
        logger.error("1. Usa el parámetro --no-ssl para desactivar verificación")
        logger.error("2. Configura los certificados corporativos (ver SSL_CERTIFICADOS.md)")
        return None
    except requests.exceptions.HTTPError as e:
        logger.error(f"Error HTTP al obtener actividades: {e}")
        if hasattr(e.response, 'text'):
            logger.error(f"Respuesta del servidor: {e.response.text}")

        # Si es 401, el token probablemente expiró
        if e.response.status_code == 401:
            logger.error("\n⚠️  TOKEN EXPIRADO O INVÁLIDO")
            logger.error("Ejecuta: python -m py_strava.main")
            logger.error("Esto refrescará automáticamente el token")

        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error de red al obtener actividades: {e}")
        return None
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        return None


def save_to_csv(activities: List[Dict], output_file: str) -> bool:
    """
    Guarda las actividades en un archivo CSV.

    Args:
        activities: Lista de actividades
        output_file: Ruta del archivo CSV de salida

    Returns:
        True si se guardó correctamente, False en caso contrario
    """
    try:
        # Crear directorio si no existe
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Convertir a DataFrame
        df = pd.json_normalize(activities)

        # Guardar a CSV
        df.to_csv(output_file, index=False, encoding='utf-8')

        logger.info(f"✅ Actividades guardadas en: {output_file}")
        logger.info(f"   Total de actividades: {len(activities)}")
        logger.info(f"   Total de columnas: {len(df.columns)}")

        return True

    except Exception as e:
        logger.error(f"Error al guardar CSV: {e}")
        return False


def display_summary(activities: List[Dict]) -> None:
    """
    Muestra un resumen de las actividades obtenidas.

    Args:
        activities: Lista de actividades
    """
    if not activities:
        return

    print("\n" + "=" * 60)
    print("RESUMEN DE ACTIVIDADES")
    print("=" * 60)

    # Contar tipos de actividades
    types = {}
    for activity in activities:
        activity_type = activity.get('type', 'Unknown')
        types[activity_type] = types.get(activity_type, 0) + 1

    print(f"\nTotal de actividades: {len(activities)}")
    print("\nPor tipo de actividad:")
    for activity_type, count in sorted(types.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {activity_type}: {count}")

    # Mostrar primeras 5 actividades
    print("\nÚltimas actividades:")
    for i, activity in enumerate(activities[:5], 1):
        name = activity.get('name', 'Sin nombre')
        date = activity.get('start_date_local', 'Sin fecha')[:10]
        activity_type = activity.get('type', 'Unknown')
        distance_km = activity.get('distance', 0) / 1000
        print(f"  {i}. {name} ({activity_type}) - {date} - {distance_km:.2f} km")

    print("=" * 60)


def main() -> int:
    """
    Función principal que ejecuta el proceso completo.

    Returns:
        0 si todo fue exitoso, 1 si hubo errores
    """
    # Parsear argumentos de línea de comandos
    parser = argparse.ArgumentParser(
        description='Obtener actividades de Strava y exportarlas a CSV'
    )
    parser.add_argument(
        '--no-ssl',
        action='store_true',
        help='Desactiva verificación SSL (usar solo en redes corporativas)'
    )
    parser.add_argument(
        '--per-page',
        type=int,
        default=DEFAULT_PER_PAGE,
        help=f'Número de actividades por página (default: {DEFAULT_PER_PAGE})'
    )
    parser.add_argument(
        '--output',
        type=str,
        default=DEFAULT_OUTPUT,
        help=f'Ruta del archivo CSV de salida (default: {DEFAULT_OUTPUT})'
    )
    args = parser.parse_args()

    logger.info("=== Inicio de obtención de actividades de Strava ===")

    if args.no_ssl:
        logger.warning("⚠️  Modo sin verificación SSL activado")

    # Cargar tokens
    tokens = load_tokens(TOKEN_FILE)
    if not tokens:
        logger.error("No se pudieron cargar los tokens. Abortando.")
        return 1

    access_token = tokens.get('access_token', '')
    if not access_token:
        logger.error("Token de acceso vacío. Abortando.")
        return 1

    logger.info(f"Access Token: {access_token[:10]}...{access_token[-10:]}")

    # Obtener actividades
    verify_ssl = not args.no_ssl
    activities = get_activities(access_token, args.per_page, verify_ssl)

    if activities is None:
        logger.error("No se pudieron obtener las actividades")
        return 1

    if not activities:
        logger.warning("No hay actividades para procesar")
        return 0

    # Mostrar resumen
    display_summary(activities)

    # Guardar a CSV
    if not save_to_csv(activities, args.output):
        logger.error("Error al guardar actividades")
        return 1

    # Mensaje final
    print("\n" + "=" * 60)
    print("✅ PROCESO COMPLETADO EXITOSAMENTE")
    print("=" * 60)
    print(f"\nActividades guardadas en: {args.output}")
    print("\nPuedes abrir el archivo CSV con:")
    print("  - Excel")
    print("  - Google Sheets")
    print("  - Pandas: pd.read_csv(r'{}')".format(args.output))
    print("=" * 60)

    logger.info("=== Proceso completado exitosamente ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
