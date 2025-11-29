"""
Script para obtener el token inicial de acceso de Strava.

IMPORTANTE: Este script solo se ejecuta UNA VEZ para obtener el token inicial.
Después de obtener el token, usa main.py que lo refresca automáticamente.

Pasos para obtener el código de autorización:

1. Ve a https://www.strava.com/settings/api y crea una aplicación
2. Anota tu client_id y client_secret
3. Visita esta URL (reemplaza YOUR_CLIENT_ID):
   https://www.strava.com/oauth/authorize?client_id=YOUR_CLIENT_ID&response_type=code&redirect_uri=http://localhost/exchange_token&approval_prompt=force&scope=activity:read_all

4. Autoriza la aplicación
5. Copia el 'code' de la URL de redirección (después de code=)
6. Ejecuta este script con tus credenciales

Uso:
    python -m py_strava.ejemplos.acces_token_strava
"""

import json
import logging
import sys
from pathlib import Path
from typing import Dict, Optional

import requests

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuración
STRAVA_TOKEN_URL = 'https://www.strava.com/oauth/token'
TOKEN_FILE = './json/strava_tokens.json'


def get_user_input() -> Dict[str, str]:
    """
    Solicita las credenciales al usuario de forma interactiva.

    Returns:
        Diccionario con client_id, client_secret y code
    """
    print("\n" + "=" * 60)
    print("OBTENER TOKEN INICIAL DE STRAVA")
    print("=" * 60)
    print("\nPor favor, ingresa tus credenciales de Strava:")
    print("(Puedes encontrarlas en https://www.strava.com/settings/api)\n")

    client_id = input("Client ID: ").strip()
    client_secret = input("Client Secret: ").strip()
    code = input("Authorization Code: ").strip()

    return {
        'client_id': client_id,
        'client_secret': client_secret,
        'code': code
    }


def validate_credentials(credentials: Dict[str, str]) -> bool:
    """
    Valida que las credenciales no estén vacías.

    Args:
        credentials: Diccionario con las credenciales

    Returns:
        True si son válidas, False en caso contrario
    """
    for key, value in credentials.items():
        if not value:
            logger.error(f"El campo '{key}' no puede estar vacío")
            return False

    # Validar que client_id sea numérico
    if not credentials['client_id'].isdigit():
        logger.error("El Client ID debe ser un número")
        return False

    return True


def request_token(client_id: str, client_secret: str, code: str, verify_ssl: bool = True) -> Optional[Dict]:
    """
    Solicita el token de acceso a la API de Strava.

    Args:
        client_id: ID del cliente de Strava
        client_secret: Secret del cliente de Strava
        code: Código de autorización obtenido
        verify_ssl: Si debe verificar certificados SSL (False para entornos corporativos)

    Returns:
        Diccionario con los tokens o None si falla
    """
    logger.info("Solicitando token de acceso a Strava...")

    # Suprimir advertencia de SSL si está deshabilitado
    if not verify_ssl:
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        logger.warning("⚠️  Verificación SSL deshabilitada")

    try:
        response = requests.post(
            url=STRAVA_TOKEN_URL,
            data={
                'client_id': client_id,
                'client_secret': client_secret,
                'code': code,
                'grant_type': 'authorization_code'
            },
            timeout=10,
            verify=verify_ssl
        )

        # Verificar si la respuesta fue exitosa
        response.raise_for_status()

        tokens = response.json()

        # Verificar que la respuesta contiene los campos esperados
        required_fields = ['access_token', 'refresh_token', 'expires_at']
        missing_fields = [field for field in required_fields if field not in tokens]

        if missing_fields:
            logger.error(f"La respuesta no contiene los campos: {missing_fields}")
            logger.error(f"Respuesta recibida: {tokens}")
            return None

        logger.info("✅ Token de acceso obtenido correctamente")
        return tokens

    except requests.exceptions.SSLError as e:
        logger.error(f"Error SSL al conectar con Strava: {e}")
        logger.error("\n⚠️  PROBLEMA DE CERTIFICADO SSL DETECTADO")
        logger.error("Esto suele ocurrir en redes corporativas o con proxies.")
        logger.error("\nSoluciones:")
        logger.error("1. Usa el parámetro --no-ssl para desactivar verificación (menos seguro)")
        logger.error("2. Contacta con tu administrador de red")
        logger.error("3. Configura los certificados corporativos")
        return None
    except requests.exceptions.HTTPError as e:
        logger.error(f"Error HTTP al solicitar token: {e}")
        if hasattr(e.response, 'text'):
            logger.error(f"Respuesta del servidor: {e.response.text}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error de red al solicitar token: {e}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Error al decodificar la respuesta JSON: {e}")
        return None
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        return None


def save_tokens(tokens: Dict, file_path: str) -> bool:
    """
    Guarda los tokens en un archivo JSON.

    Args:
        tokens: Diccionario con los tokens
        file_path: Ruta del archivo donde guardar

    Returns:
        True si se guardó correctamente, False en caso contrario
    """
    try:
        # Crear directorio si no existe
        output_path = Path(file_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Guardar tokens
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(tokens, f, indent=2)

        logger.info(f"✅ Tokens guardados en: {file_path}")
        return True

    except Exception as e:
        logger.error(f"Error al guardar tokens: {e}")
        return False


def verify_saved_tokens(file_path: str) -> bool:
    """
    Verifica que el archivo de tokens se guardó correctamente.

    Args:
        file_path: Ruta del archivo a verificar

    Returns:
        True si el archivo es válido, False en caso contrario
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        required_fields = ['access_token', 'refresh_token', 'expires_at']
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            logger.error(f"El archivo guardado no contiene: {missing_fields}")
            return False

        logger.info("✅ Archivo de tokens verificado correctamente")
        return True

    except Exception as e:
        logger.error(f"Error al verificar tokens guardados: {e}")
        return False


def display_token_info(tokens: Dict) -> None:
    """
    Muestra información sobre los tokens obtenidos.

    Args:
        tokens: Diccionario con los tokens
    """
    print("\n" + "=" * 60)
    print("TOKENS OBTENIDOS")
    print("=" * 60)

    # Ocultar partes sensibles del token
    access_token = tokens.get('access_token', '')
    refresh_token = tokens.get('refresh_token', '')

    print(f"Access Token: {access_token[:10]}...{access_token[-10:] if len(access_token) > 20 else ''}")
    print(f"Refresh Token: {refresh_token[:10]}...{refresh_token[-10:] if len(refresh_token) > 20 else ''}")
    print(f"Expires At: {tokens.get('expires_at', 'N/A')}")
    print(f"Token Type: {tokens.get('token_type', 'N/A')}")

    if 'athlete' in tokens:
        athlete = tokens['athlete']
        print(f"\nAtleta: {athlete.get('firstname', '')} {athlete.get('lastname', '')}")
        print(f"Username: {athlete.get('username', 'N/A')}")

    print("=" * 60)


def main() -> int:
    """
    Función principal que ejecuta el proceso completo.

    Returns:
        0 si todo fue exitoso, 1 si hubo errores
    """
    import argparse

    # Parsear argumentos de línea de comandos
    parser = argparse.ArgumentParser(description='Obtener token inicial de Strava')
    parser.add_argument('--no-ssl', action='store_true',
                        help='Desactiva verificación SSL (usar solo en redes corporativas)')
    args = parser.parse_args()

    logger.info("=== Inicio del proceso de obtención de token ===")

    if args.no_ssl:
        logger.warning("⚠️  Modo sin verificación SSL activado")

    # Solicitar credenciales
    credentials = get_user_input()

    # Validar credenciales
    if not validate_credentials(credentials):
        logger.error("Credenciales inválidas. Abortando.")
        return 1

    # Solicitar token
    verify_ssl = not args.no_ssl
    tokens = request_token(
        credentials['client_id'],
        credentials['client_secret'],
        credentials['code'],
        verify_ssl=verify_ssl
    )

    if not tokens:
        logger.error("No se pudo obtener el token. Verifica tus credenciales.")
        return 1

    # Mostrar información del token
    display_token_info(tokens)

    # Guardar tokens
    if not save_tokens(tokens, TOKEN_FILE):
        logger.error("Error al guardar tokens")
        return 1

    # Verificar tokens guardados
    if not verify_saved_tokens(TOKEN_FILE):
        logger.error("Error al verificar tokens guardados")
        return 1

    # Mensaje final
    print("\n" + "=" * 60)
    print("✅ PROCESO COMPLETADO EXITOSAMENTE")
    print("=" * 60)
    print(f"\nTus tokens han sido guardados en: {TOKEN_FILE}")
    print("\nPróximos pasos:")
    print("1. Ejecuta: python -m py_strava.main")
    print("2. El programa usará estos tokens automáticamente")
    print("3. Los tokens se refrescarán automáticamente cuando expiren")
    print("=" * 60)

    logger.info("=== Proceso completado exitosamente ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
