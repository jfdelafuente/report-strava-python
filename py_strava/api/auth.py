"""
Módulo para gestión de autenticación con la API de Strava.

Este módulo proporciona funcionalidades para:
- Obtener tokens de autenticación OAuth2
- Renovar tokens expirados automáticamente
- Almacenar y recuperar tokens desde archivos JSON
- Gestión segura de credenciales mediante variables de entorno

Seguridad:
    Las credenciales (client_id, client_secret) deben configurarse mediante
    variables de entorno para evitar exposición en el código fuente.

Variables de entorno requeridas:
    STRAVA_CLIENT_ID: ID del cliente de la aplicación Strava
    STRAVA_CLIENT_SECRET: Secret del cliente de la aplicación Strava

Ejemplo:
    >>> # Usando la clase (recomendado)
    >>> manager = StravaTokenManager('token.json')
    >>> token = manager.get_valid_token()
    >>>
    >>> # Usando funciones legacy (compatibilidad)
    >>> tokens = getTokenFromFile('token.json')
    >>> tokens = refreshToken(tokens, 'token.json')
"""

import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Dict, Optional

import requests

# Configuración de logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class StravaConfig:
    """Configuración centralizada para la API de Strava."""

    BASE_URL = "https://www.strava.com/oauth/token"
    TIMEOUT = 10  # segundos
    TOKEN_EXPIRY_MARGIN = 300  # Renovar 5 minutos antes de expirar

    # Intentar obtener credenciales de variables de entorno
    CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
    CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")


class StravaAuthError(Exception):
    """Excepción personalizada para errores de autenticación de Strava."""

    pass


class StravaTokenManager:
    """
    Gestiona la autenticación y renovación de tokens de Strava.

    Esta clase proporciona una interfaz orientada a objetos para manejar
    el ciclo de vida completo de los tokens de acceso de Strava, incluyendo
    renovación automática cuando expiran.

    Args:
        token_file: Ruta al archivo JSON donde se almacenan los tokens
        client_id: ID del cliente (opcional, usa variable de entorno si no se proporciona)
        client_secret: Secret del cliente (opcional, usa variable de entorno si no se proporciona)

    Raises:
        StravaAuthError: Si las credenciales no están disponibles

    Example:
        >>> manager = StravaTokenManager('tokens.json')
        >>> token = manager.get_valid_token()
        >>> print(token['access_token'])
    """

    def __init__(
        self, token_file: str, client_id: Optional[str] = None, client_secret: Optional[str] = None
    ):
        """Inicializa el gestor de tokens."""
        self.token_file = Path(token_file)
        self.client_id = client_id or StravaConfig.CLIENT_ID
        self.client_secret = client_secret or StravaConfig.CLIENT_SECRET

        if not self.client_id or not self.client_secret:
            logger.warning(
                "Credenciales no configuradas. Configure STRAVA_CLIENT_ID y "
                "STRAVA_CLIENT_SECRET como variables de entorno."
            )

    def authenticate(self, code: str) -> Dict[str, Any]:
        """
        Realiza la autenticación inicial con Strava usando un código de autorización.

        Args:
            code: Código de autorización obtenido del flujo OAuth

        Returns:
            Dict con los tokens (access_token, refresh_token, expires_at, etc.)

        Raises:
            StravaAuthError: Si la autenticación falla
            requests.RequestException: Si hay error de conexión
        """
        if not self.client_id or not self.client_secret:
            raise StravaAuthError(
                "Credenciales no configuradas. Configure STRAVA_CLIENT_ID y "
                "STRAVA_CLIENT_SECRET como variables de entorno."
            )

        logger.info("Iniciando autenticación con Strava")

        try:
            response = requests.post(
                url=StravaConfig.BASE_URL,
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                },
                timeout=StravaConfig.TIMEOUT,
            )
            response.raise_for_status()

            tokens = response.json()

            if not self._validate_token_response(tokens):
                raise StravaAuthError("Respuesta de token inválida o incompleta")

            # Guardar tokens automáticamente
            self.save_tokens(tokens)
            logger.info("Autenticación exitosa, tokens guardados")

            return tokens

        except requests.HTTPError as e:
            logger.error(f"Error HTTP en autenticación: {e}")
            raise StravaAuthError(f"Error de autenticación: {e}")
        except requests.RequestException as e:
            logger.error(f"Error de conexión: {e}")
            raise

    def get_valid_token(self) -> Dict[str, Any]:
        """
        Obtiene un token válido, renovándolo automáticamente si ha expirado.

        Returns:
            Dict con los tokens válidos

        Raises:
            FileNotFoundError: Si el archivo de tokens no existe
            StravaAuthError: Si no se puede renovar el token
        """
        tokens = self.load_tokens()

        if self._is_expired(tokens):
            logger.info("Token expirado, renovando...")
            tokens = self._refresh_token(tokens)
        else:
            logger.debug("Token vigente")

        return tokens

    def load_tokens(self) -> Dict[str, Any]:
        """
        Carga los tokens desde el archivo JSON.

        Returns:
            Dict con los tokens

        Raises:
            FileNotFoundError: Si el archivo no existe
            json.JSONDecodeError: Si el archivo no es JSON válido
        """
        if not self.token_file.exists():
            raise FileNotFoundError(f"Archivo de tokens no encontrado: {self.token_file}")

        try:
            with open(self.token_file) as f:
                tokens = json.load(f)
            logger.debug(f"Tokens cargados desde {self.token_file}")
            return tokens
        except json.JSONDecodeError as e:
            logger.error(f"Error al parsear JSON: {e}")
            raise

    def save_tokens(self, tokens: Dict[str, Any]) -> None:
        """
        Guarda los tokens en el archivo JSON.

        Args:
            tokens: Dict con los tokens a guardar
        """
        # Crear directorio si no existe
        self.token_file.parent.mkdir(parents=True, exist_ok=True)

        with open(self.token_file, "w") as f:
            json.dump(tokens, f, indent=2)
        logger.debug(f"Tokens guardados en {self.token_file}")

    def _refresh_token(self, current_tokens: Dict[str, Any]) -> Dict[str, Any]:
        """
        Renueva el token usando el refresh_token.

        Args:
            current_tokens: Tokens actuales (debe contener refresh_token)

        Returns:
            Dict con los nuevos tokens

        Raises:
            StravaAuthError: Si la renovación falla
        """
        if not self.client_id or not self.client_secret:
            raise StravaAuthError("Credenciales no configuradas para renovar token")

        if "refresh_token" not in current_tokens:
            raise StravaAuthError("Token actual no contiene refresh_token")

        try:
            response = requests.post(
                url=StravaConfig.BASE_URL,
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "grant_type": "refresh_token",
                    "refresh_token": current_tokens["refresh_token"],
                },
                timeout=StravaConfig.TIMEOUT,
            )
            response.raise_for_status()

            new_tokens = response.json()

            if not self._validate_token_response(new_tokens):
                raise StravaAuthError("Respuesta de renovación inválida")

            # Guardar nuevos tokens
            self.save_tokens(new_tokens)
            logger.info("Token renovado exitosamente")

            return new_tokens

        except requests.HTTPError as e:
            logger.error(f"Error HTTP al renovar token: {e}")
            raise StravaAuthError(f"Error al renovar token: {e}")
        except requests.RequestException as e:
            logger.error(f"Error de conexión al renovar token: {e}")
            raise

    def _is_expired(self, tokens: Dict[str, Any]) -> bool:
        """
        Verifica si el token ha expirado o está próximo a expirar.

        Args:
            tokens: Dict con los tokens (debe contener expires_at)

        Returns:
            True si el token ha expirado o expirará pronto
        """
        if "expires_at" not in tokens:
            logger.warning("Token no contiene campo expires_at")
            return True

        # Considerar expirado si falta menos del margen configurado
        time_until_expiry = tokens["expires_at"] - time.time()
        is_expired = time_until_expiry < StravaConfig.TOKEN_EXPIRY_MARGIN

        if is_expired:
            logger.debug(
                f"Token expirado o próximo a expirar " f"(faltan {time_until_expiry:.0f} segundos)"
            )

        return is_expired

    @staticmethod
    def _validate_token_response(tokens: Dict[str, Any]) -> bool:
        """
        Valida que la respuesta de token contenga todos los campos requeridos.

        Args:
            tokens: Dict con la respuesta de la API

        Returns:
            True si la respuesta es válida
        """
        required_fields = ["access_token", "refresh_token", "expires_at"]
        is_valid = all(field in tokens for field in required_fields)

        if not is_valid:
            missing = [f for f in required_fields if f not in tokens]
            logger.error(f"Campos faltantes en respuesta: {missing}")

        return is_valid


# =============================================================================
# FUNCIONES LEGACY PARA COMPATIBILIDAD CON CÓDIGO EXISTENTE
# =============================================================================
# Estas funciones mantienen la API original para evitar romper código existente
# Se recomienda migrar a la clase StravaTokenManager para nuevos desarrollos


def makeStravaAuth(
    code: str, client_id: Optional[int] = None, client_secret: Optional[str] = None
) -> Dict[str, Any]:
    """
    Realiza autenticación OAuth con Strava (función legacy).

    ADVERTENCIA: Esta función mantiene compatibilidad con código existente.
    Para nuevos desarrollos, use StravaTokenManager.authenticate()

    Args:
        code: Código de autorización de Strava
        client_id: ID del cliente (opcional, usa variable de entorno)
        client_secret: Secret del cliente (opcional, usa variable de entorno)

    Returns:
        Dict con los tokens de autenticación

    Raises:
        StravaAuthError: Si la autenticación falla
    """
    cid = client_id or StravaConfig.CLIENT_ID
    csecret = client_secret or StravaConfig.CLIENT_SECRET

    if not cid or not csecret:
        raise StravaAuthError(
            "Credenciales no configuradas. Configure STRAVA_CLIENT_ID y "
            "STRAVA_CLIENT_SECRET como variables de entorno, o páselas como parámetros."
        )

    try:
        response = requests.post(
            url=StravaConfig.BASE_URL,
            data={
                "client_id": cid,
                "client_secret": csecret,
                "code": code,
                "grant_type": "authorization_code",
            },
            timeout=StravaConfig.TIMEOUT,
        )
        response.raise_for_status()
        return response.json()

    except requests.HTTPError as e:
        logger.error(f"Error HTTP en makeStravaAuth: {e}")
        raise StravaAuthError(f"Error de autenticación: {e}")
    except requests.RequestException as e:
        logger.error(f"Error de conexión en makeStravaAuth: {e}")
        raise


def saveTokenFile(strava_tokens: Dict[str, Any], file: str) -> None:
    """
    Guarda tokens en archivo JSON (función legacy).

    ADVERTENCIA: Esta función mantiene compatibilidad con código existente.
    Para nuevos desarrollos, use StravaTokenManager.save_tokens()

    Args:
        strava_tokens: Dict con los tokens a guardar
        file: Ruta del archivo donde guardar
    """
    try:
        # Crear directorio si no existe
        Path(file).parent.mkdir(parents=True, exist_ok=True)

        with open(file, "w") as outfile:
            json.dump(strava_tokens, outfile, indent=2)
        logger.debug(f"Tokens guardados en {file}")

    except OSError as e:
        logger.error(f"Error al guardar tokens: {e}")
        raise


def getTokenFromFile(token_file: str) -> Dict[str, Any]:
    """
    Carga tokens desde archivo JSON (función legacy).

    ADVERTENCIA: Esta función mantiene compatibilidad con código existente.
    Para nuevos desarrollos, use StravaTokenManager.load_tokens()

    Args:
        token_file: Ruta del archivo JSON con tokens

    Returns:
        Dict con los tokens

    Raises:
        FileNotFoundError: Si el archivo no existe
        json.JSONDecodeError: Si el archivo no es JSON válido
    """
    if not Path(token_file).exists():
        logger.error(f"Archivo no encontrado: {token_file}")
        raise FileNotFoundError(f"Archivo de tokens no encontrado: {token_file}")

    try:
        with open(token_file) as json_file:
            strava_tokens = json.load(json_file)
        logger.debug(f"Tokens cargados desde {token_file}")
        return strava_tokens

    except json.JSONDecodeError as e:
        logger.error(f"Error al parsear JSON: {e}")
        raise


def refreshToken(
    strava_tokens: Dict[str, Any],
    file: str,
    client_id: Optional[int] = None,
    client_secret: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Renueva el token si ha expirado (función legacy).

    ADVERTENCIA: Esta función mantiene compatibilidad con código existente.
    Para nuevos desarrollos, use StravaTokenManager.get_valid_token()

    Args:
        strava_tokens: Dict con los tokens actuales
        file: Ruta donde guardar los nuevos tokens
        client_id: ID del cliente (opcional, usa variable de entorno)
        client_secret: Secret del cliente (opcional, usa variable de entorno)

    Returns:
        Dict con los tokens (renovados si fue necesario)

    Raises:
        StravaAuthError: Si la renovación falla
    """
    # Verificar si el token ha expirado
    if strava_tokens.get("expires_at", 0) < time.time():
        logger.info("Token expirado, renovando...")

        cid = client_id or StravaConfig.CLIENT_ID
        csecret = client_secret or StravaConfig.CLIENT_SECRET

        if not cid or not csecret:
            raise StravaAuthError("Credenciales no configuradas para renovar token")

        try:
            response = requests.post(
                url=StravaConfig.BASE_URL,
                data={
                    "client_id": cid,
                    "client_secret": csecret,
                    "grant_type": "refresh_token",
                    "refresh_token": strava_tokens["refresh_token"],
                },
                timeout=StravaConfig.TIMEOUT,
            )
            response.raise_for_status()

            new_strava_tokens = response.json()
            saveTokenFile(new_strava_tokens, file)
            logger.info("Token renovado exitosamente")

            return new_strava_tokens

        except requests.HTTPError as e:
            logger.error(f"Error HTTP al renovar token: {e}")
            raise StravaAuthError(f"Error al renovar token: {e}")
        except requests.RequestException as e:
            logger.error(f"Error de conexión al renovar token: {e}")
            raise
    else:
        logger.debug("Token vigente, no requiere renovación")
        return strava_tokens


def openTokenFile(file: str) -> Dict[str, Any]:
    """
    Abre y muestra el contenido del archivo de tokens (función legacy).

    ADVERTENCIA: Esta función es para debug/testing únicamente.
    No usar en producción ya que imprime información sensible.

    Args:
        file: Ruta del archivo JSON con tokens

    Returns:
        Dict con los tokens
    """
    try:
        with open(file) as check:
            data = json.load(check)

        # Imprimir versión censurada para seguridad
        safe_data = data.copy()
        if "access_token" in safe_data:
            safe_data["access_token"] = safe_data["access_token"][:10] + "..."
        if "refresh_token" in safe_data:
            safe_data["refresh_token"] = safe_data["refresh_token"][:10] + "..."

        print(f"Tokens cargados desde {file}:")
        print(json.dumps(safe_data, indent=2))

        return data

    except FileNotFoundError:
        logger.error(f"Archivo no encontrado: {file}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Error al parsear JSON: {e}")
        raise


# =============================================================================
# EJEMPLO DE USO
# =============================================================================

if __name__ == "__main__":
    """
    Ejemplos de uso del módulo.

    Configuración requerida:
        export STRAVA_CLIENT_ID="tu_client_id"
        export STRAVA_CLIENT_SECRET="tu_client_secret"
    """

    # Ejemplo 1: Usando la clase (recomendado para nuevos desarrollos)
    print("=== Ejemplo 1: Usando StravaTokenManager ===")
    try:
        manager = StravaTokenManager("tokens.json")

        # Primera vez: autenticar con código
        # manager.authenticate('codigo_de_autorizacion_aqui')

        # Obtener token válido (renueva automáticamente si expiró)
        token = manager.get_valid_token()
        print(f"Access token obtenido: {token['access_token'][:20]}...")

    except FileNotFoundError:
        print("Archivo de tokens no encontrado. Ejecute authenticate() primero.")
    except StravaAuthError as e:
        print(f"Error de autenticación: {e}")

    # Ejemplo 2: Usando funciones legacy (compatibilidad con código existente)
    print("\n=== Ejemplo 2: Usando funciones legacy ===")
    try:
        tokens = getTokenFromFile("tokens.json")
        tokens = refreshToken(tokens, "tokens.json")
        print(f"Access token: {tokens['access_token'][:20]}...")

    except FileNotFoundError:
        print("Archivo de tokens no encontrado.")
    except StravaAuthError as e:
        print(f"Error: {e}")
