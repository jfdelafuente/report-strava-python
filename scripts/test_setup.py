#!/usr/bin/env python
"""
Script de verificación para comprobar que el proyecto está configurado correctamente.

Uso:
    python scripts/test_setup.py           # Verificación completa
    python scripts/test_setup.py --quick   # Verificación rápida (solo imports)
    python scripts/test_setup.py --verbose # Verificación con más detalles
"""

import argparse
import sys
from pathlib import Path

# Configurar codificación UTF-8 para Windows
if sys.platform == "win32":
    import codecs

    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

# Añadir el directorio raíz del proyecto al path de Python
# Esto permite importar py_strava desde cualquier ubicación
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Variable global para modo verbose
VERBOSE = False


# Códigos de color ANSI
class Colors:
    """Códigos de color ANSI para terminal."""

    RESET = "\033[0m"
    BOLD = "\033[1m"

    # Colores básicos
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"

    # Backgrounds
    BG_RED = "\033[101m"
    BG_GREEN = "\033[102m"
    BG_YELLOW = "\033[103m"


def colored(text, color):
    """Aplica color al texto."""
    return f"{color}{text}{Colors.RESET}"


def check_mark(condition):
    """Retorna una marca visual según la condición."""
    if condition:
        return colored("✅", Colors.GREEN)
    else:
        return colored("❌", Colors.RED)


def info_mark():
    """Retorna una marca de información."""
    return colored("ℹ️ ", Colors.BLUE)


def test_imports():
    """Verifica que los imports funcionen correctamente."""
    print(f"\n{colored('═══ 📦 Verificando Imports ═══', Colors.CYAN + Colors.BOLD)}\n")

    tests = []

    # Test 1: Import de config
    try:
        from py_strava import config  # noqa: F401

        print(f"{check_mark(True)} py_strava.config importado correctamente")
        tests.append(True)
    except Exception as e:
        print(f"{check_mark(False)} Error al importar py_strava.config: {e}")
        tests.append(False)

    # Test 2: Import de postgres (opcional si no hay psycopg2)
    try:
        from py_strava.database import postgres  # noqa: F401

        print(f"{check_mark(True)} py_strava.database.postgres importado correctamente")
        tests.append(True)
    except ImportError as e:
        if "psycopg2" in str(e):
            print(f"{info_mark()}postgres (requiere psycopg2 - usa SQLite en su lugar)")
            tests.append(True)  # No falla el test
        else:
            print(f"{check_mark(False)} Error al importar postgres: {e}")
            tests.append(False)
    except Exception as e:
        print(f"{check_mark(False)} Error al importar postgres: {e}")
        tests.append(False)

    # Test 3: Import de sqlite
    try:
        from py_strava.database import sqlite  # noqa: F401

        print(f"{check_mark(True)} py_strava.database.sqlite importado correctamente")
        tests.append(True)
    except Exception as e:
        print(f"{check_mark(False)} Error al importar sqlite: {e}")
        tests.append(False)

    # Test 4: Import de auth
    try:
        from py_strava.api import auth  # noqa: F401

        print(f"{check_mark(True)} py_strava.api.auth importado correctamente")
        tests.append(True)
    except Exception as e:
        print(f"{check_mark(False)} Error al importar auth: {e}")
        tests.append(False)

    # Test 5: Import de activities
    try:
        from py_strava.api import activities  # noqa: F401

        print(f"{check_mark(True)} py_strava.api.activities importado correctamente")
        tests.append(True)
    except Exception as e:
        print(f"{check_mark(False)} Error al importar activities: {e}")
        tests.append(False)

    # Test 6: Import de dates
    try:
        from py_strava.utils import dates  # noqa: F401

        print(f"{check_mark(True)} py_strava.utils.dates importado correctamente")
        tests.append(True)
    except Exception as e:
        print(f"{check_mark(False)} Error al importar dates: {e}")
        tests.append(False)

    return all(tests)


def test_directories():
    """Verifica que existan los directorios necesarios."""
    print(
        f"\n{colored('═══ 📁 Verificando Estructura de Directorios ═══', Colors.CYAN + Colors.BOLD)}\n"
    )

    # Usar la raíz del proyecto, no el directorio actual
    base_dir = project_root
    dirs_to_check = ["py_strava", "py_strava/strava", "bd", "data", "json"]

    tests = []
    for dir_path in dirs_to_check:
        full_path = base_dir / dir_path
        exists = full_path.exists() and full_path.is_dir()
        print(f"{check_mark(exists)} {dir_path}/")
        tests.append(exists)

    return all(tests)


def test_files():
    """Verifica que existan los archivos necesarios."""
    print(f"\n{colored('═══ 📄 Verificando Archivos Clave ═══', Colors.CYAN + Colors.BOLD)}\n")

    # Usar la raíz del proyecto, no el directorio actual
    base_dir = project_root
    files_to_check = [
        ("py_strava/__init__.py", True),
        ("py_strava/strava/__init__.py", True),
        ("py_strava/config.py", True),
        ("py_strava/main.py", True),
        ("py_strava/informe_strava.py", True),
        ("requirements.txt", True),
        ("bd/postgres_credentials.json", False),  # Opcional
        ("json/strava_tokens.json", False),  # Opcional
        ("data/strava_activities.log", False),  # Opcional pero recomendado
    ]

    tests = []
    for file_path, required in files_to_check:
        full_path = base_dir / file_path
        exists = full_path.exists() and full_path.is_file()

        if required:
            status = check_mark(exists)
            req_label = colored("(REQUERIDO)", Colors.YELLOW) if required else "(opcional)"
            print(f"{status} {file_path} {req_label}")
            if required:
                tests.append(exists)
        else:
            status = colored("✓", Colors.GREEN) if exists else info_mark()
            found_label = (
                colored("encontrado", Colors.GREEN)
                if exists
                else colored("no encontrado", Colors.YELLOW)
            )
            print(f"{status}  {file_path} (opcional - {found_label})")

    return all(tests)


def test_dependencies():
    """Verifica que las dependencias estén instaladas."""
    print(f"\n{colored('═══ 📚 Verificando Dependencias ═══', Colors.CYAN + Colors.BOLD)}\n")

    # Dependencias requeridas
    required_deps = ["pandas", "numpy", "requests", "dateutil"]

    # Dependencias opcionales
    optional_deps = ["psycopg2"]

    tests = []

    # Verificar dependencias requeridas
    for dep in required_deps:
        try:
            __import__(dep)
            print(f"{check_mark(True)} {dep}")
            tests.append(True)
        except ImportError:
            print(
                f"{check_mark(False)} {dep} - {colored('NO INSTALADO (REQUERIDO)', Colors.RED + Colors.BOLD)}"
            )
            tests.append(False)

    # Verificar dependencias opcionales (no fallan el test)
    for dep in optional_deps:
        try:
            __import__(dep)
            print(f"{colored('✓', Colors.GREEN)}  {dep} (opcional - instalado)")
        except ImportError:
            print(f"{info_mark()}{dep} (opcional - no instalado, usa SQLite)")

    return all(tests)


def test_config():
    """Verifica la configuración."""
    print(f"\n{colored('═══ ⚙️  Verificando Configuración ═══', Colors.CYAN + Colors.BOLD)}\n")

    try:
        from py_strava import config

        print(
            f"{colored('📂', Colors.BLUE)} Base Directory: {colored(config.BASE_DIR, Colors.WHITE)}"
        )
        print(
            f"{colored('📂', Colors.BLUE)} Data Directory: {colored(config.DATA_DIR, Colors.WHITE)}"
        )
        print(
            f"{colored('📂', Colors.BLUE)} JSON Directory: {colored(config.JSON_DIR, Colors.WHITE)}"
        )
        print(f"{colored('🔌', Colors.BLUE)} DB Host: {colored(config.DB_HOST, Colors.WHITE)}")
        print(f"{colored('🔌', Colors.BLUE)} DB Port: {colored(config.DB_PORT, Colors.WHITE)}")
        print(f"{colored('💾', Colors.BLUE)} DB Name: {colored(config.DB_NAME, Colors.WHITE)}")
        print(f"{colored('👤', Colors.BLUE)} DB User: {colored(config.DB_USER, Colors.WHITE)}")
        pwd_display = (
            colored("***", Colors.YELLOW)
            if config.DB_PASSWORD
            else colored("(no configurada)", Colors.YELLOW)
        )
        print(f"{colored('🔐', Colors.BLUE)} DB Password: {pwd_display}")

        return True
    except Exception as e:
        print(f"{check_mark(False)} Error al leer configuración: {e}")
        return False


def main():
    """Función principal que ejecuta todas las verificaciones."""
    global VERBOSE

    # Parsear argumentos
    parser = argparse.ArgumentParser(
        description="Verificar configuración del proyecto py-strava",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--quick", action="store_true", help="Verificación rápida (solo imports críticos)"
    )
    parser.add_argument("--verbose", action="store_true", help="Mostrar información detallada")

    args = parser.parse_args()
    VERBOSE = args.verbose

    # Banner principal
    print("\n" + colored("═" * 60, Colors.MAGENTA + Colors.BOLD))
    print(colored("🔍 VERIFICACIÓN DE CONFIGURACIÓN - py-strava 🏃", Colors.MAGENTA + Colors.BOLD))
    print(colored("═" * 60, Colors.MAGENTA + Colors.BOLD))

    if VERBOSE:
        print(
            f"\n{colored('📍', Colors.BLUE)} Raíz del proyecto: {colored(project_root, Colors.WHITE)}"
        )
        print(
            f"{colored('📍', Colors.BLUE)} Ejecutando desde: {colored(Path(__file__).parent, Colors.WHITE)}"
        )
        print(
            f"{colored('🐍', Colors.BLUE)} Python: {colored(sys.version.split()[0], Colors.WHITE)}"
        )
        print(colored("═" * 60, Colors.MAGENTA))

    results = []

    # Ejecutar tests
    if args.quick:
        # Modo rápido: solo imports y dependencias
        print(
            f"\n{colored('⚡ [MODO RÁPIDO]', Colors.YELLOW + Colors.BOLD)} Ejecutando verificaciones esenciales...\n"
        )
        results.append(("Dependencias", test_dependencies()))
        results.append(("Imports", test_imports()))
    else:
        # Modo completo
        results.append(("Directorios", test_directories()))
        results.append(("Archivos", test_files()))
        results.append(("Dependencias", test_dependencies()))
        results.append(("Imports", test_imports()))
        results.append(("Configuración", test_config()))

    # Resumen
    print("\n" + colored("═" * 60, Colors.MAGENTA + Colors.BOLD))
    print(colored("📊 RESUMEN", Colors.MAGENTA + Colors.BOLD))
    print(colored("═" * 60, Colors.MAGENTA + Colors.BOLD) + "\n")

    for name, passed in results:
        if passed is not None:
            print(f"{check_mark(passed)} {name}")

    # Determinar si pasó todas las verificaciones
    all_passed = all(result for _, result in results if result is not None)

    print("\n" + colored("═" * 60, Colors.MAGENTA + Colors.BOLD))
    if all_passed:
        print(
            colored(
                "✨ [SUCCESS] TODAS LAS VERIFICACIONES PASARON ✨",
                Colors.GREEN + Colors.BOLD,
            )
        )
        print(f"\n{colored('📝 Próximos pasos:', Colors.CYAN + Colors.BOLD)}")
        print(f"  {colored('1️⃣ ', Colors.BLUE)} Sincronizar actividades:")
        print(f"     {colored('python -m py_strava.main', Colors.WHITE)}")
        print(f"\n  {colored('2️⃣ ', Colors.BLUE)} Generar informe:")
        print(f"     {colored('python -m py_strava.informe_strava', Colors.WHITE)}")
        print(f"\n  {colored('3️⃣ ', Colors.BLUE)} Inicializar base de datos (si no está hecha):")
        print(f"     {colored('python scripts/init_database.py', Colors.WHITE)}")
        print(f"\n  {colored('4️⃣ ', Colors.BLUE)} Ver ejemplos de uso:")
        print(f"     {colored('python examples/advanced/ejemplo_uso_bd.py', Colors.WHITE)}")
    else:
        print(
            colored(
                "❌ [ERROR] ALGUNAS VERIFICACIONES FALLARON ❌",
                Colors.RED + Colors.BOLD,
            )
        )
        print(f"\n{colored('🔧 Acciones recomendadas:', Colors.YELLOW + Colors.BOLD)}")
        print(f"  {colored('•', Colors.RED)} Revisa los errores marcados con ❌ arriba")
        print(f"  {colored('•', Colors.RED)} Consulta docs/user/SOLUCION_ERRORES.md")
        print(f"  {colored('•', Colors.RED)} Verifica que ejecutas desde la raíz del proyecto")
        print(f"  {colored('•', Colors.RED)} Asegúrate de que el venv está activado")
    print(colored("═" * 60, Colors.MAGENTA + Colors.BOLD) + "\n")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
