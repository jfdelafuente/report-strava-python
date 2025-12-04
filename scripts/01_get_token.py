#!/usr/bin/env python3
"""
Script interactivo para obtener y refrescar tokens de Strava.

Este script facilita el proceso de autenticación con Strava mediante:
- Generación de URL de autorización
- Intercambio de código por tokens
- Renovación de tokens expirados
- Verificación de tokens existentes

Uso:
    python scripts/01_get_token.py              # Modo interactivo
    python scripts/01_get_token.py --verify     # Verificar token existente
    python scripts/01_get_token.py --refresh    # Forzar renovación
    python scripts/01_get_token.py --help       # Mostrar ayuda

Requisitos:
    1. Tener una aplicación creada en https://www.strava.com/settings/api
    2. Conocer tu client_id y client_secret
    3. Tener configurada la Authorization Callback Domain

Autor: Jose F. de la Fuente
Fecha: 2025-12-03
Versión: 1.0.0
"""

import sys
import os
import json
import argparse
import webbrowser
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Agregar el directorio raíz al path para imports
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

try:
    from py_strava.api.auth import StravaTokenManager, StravaAuthError
except ImportError as e:
    print(f"❌ Error al importar módulos: {e}")
    print(f"   Asegúrate de estar en el directorio raíz del proyecto: {ROOT_DIR}")
    sys.exit(1)


# =============================================================================
# CONFIGURACIÓN
# =============================================================================

DEFAULT_TOKEN_FILE = ROOT_DIR / "json" / "strava_tokens.json"
STRAVA_AUTHORIZE_URL = "https://www.strava.com/oauth/authorize"
STRAVA_API_SETTINGS = "https://www.strava.com/settings/api"


# =============================================================================
# FUNCIONES AUXILIARES
# =============================================================================


def print_header(title: str) -> None:
    """Imprime un encabezado formateado."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def print_success(message: str) -> None:
    """Imprime un mensaje de éxito."""
    print(f"✅ {message}")


def print_error(message: str) -> None:
    """Imprime un mensaje de error."""
    print(f"❌ {message}")


def print_warning(message: str) -> None:
    """Imprime un mensaje de advertencia."""
    print(f"⚠️  {message}")


def print_info(message: str) -> None:
    """Imprime un mensaje informativo."""
    print(f"ℹ️  {message}")


def print_step(step: int, message: str) -> None:
    """Imprime un paso numerado."""
    print(f"\n{step}. {message}")


def get_user_input(prompt: str, default: Optional[str] = None) -> str:
    """
    Obtiene entrada del usuario con valor por defecto opcional.

    Args:
        prompt: Mensaje a mostrar
        default: Valor por defecto (opcional)

    Returns:
        Entrada del usuario o valor por defecto
    """
    if default:
        user_input = input(f"{prompt} [{default}]: ").strip()
        return user_input if user_input else default
    else:
        return input(f"{prompt}: ").strip()


def confirm_action(message: str) -> bool:
    """
    Solicita confirmación del usuario.

    Args:
        message: Mensaje de confirmación

    Returns:
        True si el usuario confirma, False en caso contrario
    """
    response = get_user_input(f"{message} (s/n)", "s").lower()
    return response in ["s", "si", "yes", "y"]


def format_timestamp(timestamp: int) -> str:
    """
    Formatea un timestamp Unix a fecha legible.

    Args:
        timestamp: Timestamp Unix

    Returns:
        Fecha formateada
    """
    try:
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, OSError):
        return "Fecha inválida"


def display_token_info(tokens: Dict[str, Any]) -> None:
    """
    Muestra información del token de forma segura.

    Args:
        tokens: Dict con los tokens
    """
    print("\n📋 Información del token:")
    print(f"   Token Type:     {tokens.get('token_type', 'N/A')}")

    # Mostrar access_token censurado
    access_token = tokens.get("access_token", "")
    if access_token:
        print(f"   Access Token:   {access_token[:15]}...{access_token[-10:]}")

    # Mostrar refresh_token censurado
    refresh_token = tokens.get("refresh_token", "")
    if refresh_token:
        print(f"   Refresh Token:  {refresh_token[:15]}...{refresh_token[-10:]}")

    # Mostrar expiración
    expires_at = tokens.get("expires_at", 0)
    if expires_at:
        formatted_date = format_timestamp(expires_at)
        import time

        remaining = expires_at - time.time()
        hours = remaining / 3600
        print(f"   Expira:         {formatted_date} ({hours:.1f} horas)")

    # Información del atleta (si está disponible)
    athlete = tokens.get("athlete", {})
    if athlete:
        print(f"\n👤 Información del atleta:")
        print(f"   Nombre:         {athlete.get('firstname', '')} {athlete.get('lastname', '')}")
        print(f"   ID:             {athlete.get('id', 'N/A')}")


# =============================================================================
# FLUJOS PRINCIPALES
# =============================================================================


def get_credentials() -> tuple[str, str]:
    """
    Obtiene las credenciales de Strava (client_id y client_secret).

    Returns:
        Tupla (client_id, client_secret)
    """
    print_info("Obtención de credenciales de Strava")
    print("   Las credenciales se pueden obtener de:")
    print(f"   {STRAVA_API_SETTINGS}\n")

    # Intentar obtener de variables de entorno
    client_id = os.getenv("STRAVA_CLIENT_ID")
    client_secret = os.getenv("STRAVA_CLIENT_SECRET")

    if client_id and client_secret:
        print_info("Credenciales encontradas en variables de entorno")
        if confirm_action("¿Usar estas credenciales?"):
            return client_id, client_secret

    # Solicitar credenciales al usuario
    print("\n📝 Ingresa tus credenciales de Strava:")
    client_id = get_user_input("   Client ID")
    client_secret = get_user_input("   Client Secret")

    if not client_id or not client_secret:
        print_error("Client ID y Client Secret son obligatorios")
        sys.exit(1)

    return client_id, client_secret


def generate_authorization_url(client_id: str) -> str:
    """
    Genera la URL de autorización de Strava.

    Args:
        client_id: Client ID de la aplicación

    Returns:
        URL de autorización
    """
    # Scopes recomendados para la aplicación
    scopes = "read,activity:read_all,activity:write"
    redirect_uri = "http://localhost"

    auth_url = (
        f"{STRAVA_AUTHORIZE_URL}"
        f"?client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type=code"
        f"&approval_prompt=force"
        f"&scope={scopes}"
    )

    return auth_url


def get_authorization_code(client_id: str) -> str:
    """
    Guía al usuario para obtener el código de autorización.

    Args:
        client_id: Client ID de la aplicación

    Returns:
        Código de autorización
    """
    print_step(1, "Generar código de autorización")

    auth_url = generate_authorization_url(client_id)

    print(f"\n   URL de autorización:\n   {auth_url}\n")

    if confirm_action("¿Abrir URL en el navegador?"):
        try:
            webbrowser.open(auth_url)
            print_success("Navegador abierto")
        except Exception as e:
            print_warning(f"No se pudo abrir el navegador: {e}")
            print_info("Copia y pega la URL manualmente")
    else:
        print_info("Copia y pega la URL en tu navegador")

    print("\n" + "-" * 70)
    print("Instrucciones:")
    print("1. Autoriza la aplicación en Strava")
    print("2. Serás redirigido a: http://localhost/?state=&code=CODIGO_AQUI&scope=...")
    print("3. Copia el valor del parámetro 'code' de la URL")
    print("-" * 70 + "\n")

    code = get_user_input("📋 Pega el código de autorización aquí")

    if not code:
        print_error("Código de autorización requerido")
        sys.exit(1)

    # Limpiar el código (remover espacios, saltos de línea, etc.)
    code = code.strip()

    print_success(f"Código recibido: {code[:20]}...")
    return code


def authenticate_and_save(client_id: str, client_secret: str, token_file: Path) -> Dict[str, Any]:
    """
    Realiza la autenticación completa y guarda los tokens.

    Args:
        client_id: Client ID de Strava
        client_secret: Client Secret de Strava
        token_file: Ruta donde guardar los tokens

    Returns:
        Dict con los tokens obtenidos
    """
    print_header("AUTENTICACIÓN NUEVA")

    # Obtener código de autorización
    code = get_authorization_code(client_id)

    # Crear manager y autenticar
    print_step(2, "Intercambiar código por tokens")

    try:
        manager = StravaTokenManager(
            token_file=str(token_file), client_id=client_id, client_secret=client_secret
        )

        print_info("Contactando con Strava API...")
        tokens = manager.authenticate(code)

        print_success("Autenticación exitosa")
        print_success(f"Tokens guardados en: {token_file}")

        display_token_info(tokens)

        return tokens

    except StravaAuthError as e:
        print_error(f"Error de autenticación: {e}")
        print_info("Verifica que:")
        print("   - El código sea correcto y no haya expirado (válido por 10 minutos)")
        print("   - Las credenciales (client_id, client_secret) sean correctas")
        print("   - La aplicación esté configurada en Strava API Settings")
        sys.exit(1)
    except Exception as e:
        print_error(f"Error inesperado: {e}")
        sys.exit(1)


def verify_token(token_file: Path) -> Dict[str, Any]:
    """
    Verifica un token existente.

    Args:
        token_file: Ruta del archivo de tokens

    Returns:
        Dict con los tokens verificados
    """
    print_header("VERIFICAR TOKEN EXISTENTE")

    if not token_file.exists():
        print_error(f"Archivo de tokens no encontrado: {token_file}")
        print_info("Ejecuta el script sin argumentos para crear uno nuevo")
        sys.exit(1)

    try:
        # Cargar tokens
        with open(token_file) as f:
            tokens = json.load(f)

        print_success(f"Archivo encontrado: {token_file}")

        # Verificar campos requeridos
        required_fields = [
            "access_token",
            "refresh_token",
            "expires_at",
            "client_id",
            "client_secret",
        ]
        missing_fields = [f for f in required_fields if f not in tokens]

        if missing_fields:
            print_error(f"Campos faltantes: {', '.join(missing_fields)}")
            sys.exit(1)

        print_success("Estructura del token válida")

        # Verificar expiración
        import time

        expires_at = tokens.get("expires_at", 0)
        current_time = time.time()

        if expires_at < current_time:
            print_warning("Token EXPIRADO")
            remaining = expires_at - current_time
            hours = abs(remaining) / 3600
            print(f"   Expiró hace {hours:.1f} horas")
            print_info("Usa --refresh para renovar el token")
        else:
            print_success("Token VÁLIDO")
            remaining = expires_at - current_time
            hours = remaining / 3600
            print(f"   Válido por {hours:.1f} horas más")

        display_token_info(tokens)

        return tokens

    except json.JSONDecodeError as e:
        print_error(f"Error al leer JSON: {e}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Error inesperado: {e}")
        sys.exit(1)


def refresh_token(token_file: Path) -> Dict[str, Any]:
    """
    Renueva un token existente.

    Args:
        token_file: Ruta del archivo de tokens

    Returns:
        Dict con los nuevos tokens
    """
    print_header("RENOVAR TOKEN")

    if not token_file.exists():
        print_error(f"Archivo de tokens no encontrado: {token_file}")
        print_info("Ejecuta el script sin argumentos para crear uno nuevo")
        sys.exit(1)

    try:
        # Cargar tokens actuales
        with open(token_file) as f:
            current_tokens = json.load(f)

        # Obtener credenciales del archivo
        client_id = current_tokens.get("client_id")
        client_secret = current_tokens.get("client_secret")

        if not client_id or not client_secret:
            print_error("Credenciales no encontradas en el archivo de tokens")
            print_info("Usa el modo interactivo para generar un nuevo token")
            sys.exit(1)

        # Crear manager y renovar
        manager = StravaTokenManager(
            token_file=str(token_file), client_id=client_id, client_secret=client_secret
        )

        print_info("Renovando token...")
        new_tokens = manager.get_valid_token()

        print_success("Token renovado exitosamente")
        print_success(f"Tokens actualizados en: {token_file}")

        display_token_info(new_tokens)

        return new_tokens

    except StravaAuthError as e:
        print_error(f"Error al renovar token: {e}")
        print_info("Si el refresh_token también expiró, necesitas generar uno nuevo")
        sys.exit(1)
    except Exception as e:
        print_error(f"Error inesperado: {e}")
        sys.exit(1)


def interactive_mode(token_file: Path) -> Dict[str, Any]:
    """
    Modo interactivo principal.

    Args:
        token_file: Ruta del archivo de tokens

    Returns:
        Dict con los tokens obtenidos/renovados
    """
    print_header("OBTENCIÓN DE TOKENS DE STRAVA - MODO INTERACTIVO")

    # Verificar si ya existe un archivo de tokens
    if token_file.exists():
        print_info(f"Archivo de tokens existente encontrado: {token_file}")
        print("\nOpciones:")
        print("  1. Verificar token existente")
        print("  2. Renovar token existente")
        print("  3. Generar nuevo token (sobrescribirá el existente)")
        print("  4. Salir")

        choice = get_user_input("\nSelecciona una opción", "1")

        if choice == "1":
            return verify_token(token_file)
        elif choice == "2":
            return refresh_token(token_file)
        elif choice == "3":
            if not confirm_action("⚠️  ¿Estás seguro? Esto sobrescribirá el token actual"):
                print_info("Operación cancelada")
                sys.exit(0)
        elif choice == "4":
            print_info("Saliendo...")
            sys.exit(0)
        else:
            print_error("Opción inválida")
            sys.exit(1)

    # Crear directorio si no existe
    token_file.parent.mkdir(parents=True, exist_ok=True)

    # Obtener credenciales
    client_id, client_secret = get_credentials()

    # Autenticar y guardar
    return authenticate_and_save(client_id, client_secret, token_file)


# =============================================================================
# FUNCIÓN PRINCIPAL
# =============================================================================


def main():
    """Función principal del script."""
    parser = argparse.ArgumentParser(
        description="Script interactivo para obtener y refrescar tokens de Strava",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python scripts/01_get_token.py                    # Modo interactivo
  python scripts/01_get_token.py --verify           # Verificar token
  python scripts/01_get_token.py --refresh          # Renovar token
  python scripts/01_get_token.py --token custom.json  # Archivo personalizado

Para más información sobre la API de Strava:
  https://developers.strava.com/docs/authentication/
        """,
    )

    parser.add_argument(
        "--verify", action="store_true", help="Verificar token existente sin modificar"
    )

    parser.add_argument("--refresh", action="store_true", help="Forzar renovación del token")

    parser.add_argument(
        "--token",
        type=str,
        default=str(DEFAULT_TOKEN_FILE),
        help=f"Ruta del archivo de tokens (default: {DEFAULT_TOKEN_FILE})",
    )

    args = parser.parse_args()

    token_file = Path(args.token)

    try:
        if args.verify:
            verify_token(token_file)
        elif args.refresh:
            refresh_token(token_file)
        else:
            interactive_mode(token_file)

        print_header("✅ PROCESO COMPLETADO EXITOSAMENTE")

    except KeyboardInterrupt:
        print("\n\n⚠️  Proceso interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        print_error(f"Error fatal: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
