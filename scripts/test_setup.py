#!/usr/bin/env python
"""
Script de verificación para comprobar que el proyecto está configurado correctamente.

Uso:
    python scripts/test_setup.py           # Verificación completa
    python scripts/test_setup.py --quick   # Verificación rápida (solo imports)
    python scripts/test_setup.py --verbose # Verificación con más detalles
"""

import sys
import argparse
from pathlib import Path

# Añadir el directorio raíz del proyecto al path de Python
# Esto permite importar py_strava desde cualquier ubicación
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Variable global para modo verbose
VERBOSE = False


def check_mark(condition):
    """Retorna una marca visual según la condición."""
    return "[OK]" if condition else "[FAIL]"


def test_imports():
    """Verifica que los imports funcionen correctamente."""
    print("\n=== Verificando Imports ===\n")

    tests = []

    # Test 1: Import de config
    try:
        from py_strava import config
        print(f"{check_mark(True)} py_strava.config importado correctamente")
        tests.append(True)
    except Exception as e:
        print(f"{check_mark(False)} Error al importar py_strava.config: {e}")
        tests.append(False)

    # Test 2: Import de strava_db_postgres (opcional si no hay psycopg2)
    try:
        from py_strava.strava import strava_db_postgres
        print(f"{check_mark(True)} py_strava.strava.strava_db_postgres importado correctamente")
        tests.append(True)
    except ImportError as e:
        if 'psycopg2' in str(e):
            print(f"[INFO] strava_db_postgres (requiere psycopg2 - usa SQLite en su lugar)")
            tests.append(True)  # No falla el test
        else:
            print(f"{check_mark(False)} Error al importar strava_db_postgres: {e}")
            tests.append(False)
    except Exception as e:
        print(f"{check_mark(False)} Error al importar strava_db_postgres: {e}")
        tests.append(False)

    # Test 3: Import de strava_db_sqlite
    try:
        from py_strava.strava import strava_db_sqlite
        print(f"{check_mark(True)} py_strava.strava.strava_db_sqlite importado correctamente")
        tests.append(True)
    except Exception as e:
        print(f"{check_mark(False)} Error al importar strava_db_sqlite: {e}")
        tests.append(False)

    # Test 4: Import de strava_token
    try:
        from py_strava.strava import strava_token
        print(f"{check_mark(True)} py_strava.strava.strava_token importado correctamente")
        tests.append(True)
    except Exception as e:
        print(f"{check_mark(False)} Error al importar strava_token: {e}")
        tests.append(False)

    # Test 5: Import de strava_activities
    try:
        from py_strava.strava import strava_activities
        print(f"{check_mark(True)} py_strava.strava.strava_activities importado correctamente")
        tests.append(True)
    except Exception as e:
        print(f"{check_mark(False)} Error al importar strava_activities: {e}")
        tests.append(False)

    # Test 6: Import de strava_fechas
    try:
        from py_strava.strava import strava_fechas
        print(f"{check_mark(True)} py_strava.strava.strava_fechas importado correctamente")
        tests.append(True)
    except Exception as e:
        print(f"{check_mark(False)} Error al importar strava_fechas: {e}")
        tests.append(False)

    return all(tests)


def test_directories():
    """Verifica que existan los directorios necesarios."""
    print("\n=== Verificando Estructura de Directorios ===\n")

    # Usar la raíz del proyecto, no el directorio actual
    base_dir = project_root
    dirs_to_check = [
        'py_strava',
        'py_strava/strava',
        'bd',
        'data',
        'json'
    ]

    tests = []
    for dir_path in dirs_to_check:
        full_path = base_dir / dir_path
        exists = full_path.exists() and full_path.is_dir()
        print(f"{check_mark(exists)} {dir_path}/")
        tests.append(exists)

    return all(tests)


def test_files():
    """Verifica que existan los archivos necesarios."""
    print("\n=== Verificando Archivos Clave ===\n")

    # Usar la raíz del proyecto, no el directorio actual
    base_dir = project_root
    files_to_check = [
        ('py_strava/__init__.py', True),
        ('py_strava/strava/__init__.py', True),
        ('py_strava/config.py', True),
        ('py_strava/main.py', True),
        ('py_strava/informe_strava.py', True),
        ('requirements.txt', True),
        ('bd/postgres_credentials.json', False),  # Opcional
        ('json/strava_tokens.json', False),  # Opcional
        ('data/strava_activities.log', False),  # Opcional pero recomendado
    ]

    tests = []
    for file_path, required in files_to_check:
        full_path = base_dir / file_path
        exists = full_path.exists() and full_path.is_file()

        if required:
            print(f"{check_mark(exists)} {file_path} {'(REQUERIDO)' if required else '(opcional)'}")
            if required:
                tests.append(exists)
        else:
            status = "[OK]" if exists else "[INFO]"
            print(f"{status}  {file_path} (opcional - {'encontrado' if exists else 'no encontrado'})")

    return all(tests)


def test_dependencies():
    """Verifica que las dependencias estén instaladas."""
    print("\n=== Verificando Dependencias ===\n")

    # Dependencias requeridas
    required_deps = [
        'pandas',
        'numpy',
        'requests',
        'dateutil'
    ]

    # Dependencias opcionales
    optional_deps = [
        'psycopg2'
    ]

    tests = []

    # Verificar dependencias requeridas
    for dep in required_deps:
        try:
            __import__(dep)
            print(f"{check_mark(True)} {dep}")
            tests.append(True)
        except ImportError:
            print(f"{check_mark(False)} {dep} - NO INSTALADO (REQUERIDO)")
            tests.append(False)

    # Verificar dependencias opcionales (no fallan el test)
    for dep in optional_deps:
        try:
            __import__(dep)
            print(f"[OK]  {dep} (opcional - instalado)")
        except ImportError:
            print(f"[INFO] {dep} (opcional - no instalado, usa SQLite)")

    return all(tests)


def test_config():
    """Verifica la configuración."""
    print("\n=== Verificando Configuración ===\n")

    try:
        from py_strava import config

        print(f"Base Directory: {config.BASE_DIR}")
        print(f"Data Directory: {config.DATA_DIR}")
        print(f"JSON Directory: {config.JSON_DIR}")
        print(f"DB Host: {config.DB_HOST}")
        print(f"DB Port: {config.DB_PORT}")
        print(f"DB Name: {config.DB_NAME}")
        print(f"DB User: {config.DB_USER}")
        print(f"DB Password: {'***' if config.DB_PASSWORD else '(no configurada)'}")

        return True
    except Exception as e:
        print(f"{check_mark(False)} Error al leer configuración: {e}")
        return False


def main():
    """Función principal que ejecuta todas las verificaciones."""
    global VERBOSE

    # Parsear argumentos
    parser = argparse.ArgumentParser(
        description='Verificar configuración del proyecto py-strava',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--quick', action='store_true',
                       help='Verificación rápida (solo imports críticos)')
    parser.add_argument('--verbose', action='store_true',
                       help='Mostrar información detallada')

    args = parser.parse_args()
    VERBOSE = args.verbose

    print("=" * 60)
    print("VERIFICACIÓN DE CONFIGURACIÓN - py-strava")
    print("=" * 60)

    if VERBOSE:
        print(f"Raíz del proyecto: {project_root}")
        print(f"Ejecutando desde: {Path(__file__).parent}")
        print(f"Python: {sys.version}")
        print("=" * 60)

    results = []

    # Ejecutar tests
    if args.quick:
        # Modo rápido: solo imports y dependencias
        print("\n[MODO RÁPIDO] Ejecutando verificaciones esenciales...\n")
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
    print("\n" + "=" * 60)
    print("RESUMEN")
    print("=" * 60)

    for name, passed in results:
        if passed is not None:
            print(f"{check_mark(passed)} {name}")

    # Determinar si pasó todas las verificaciones
    all_passed = all(result for _, result in results if result is not None)

    print("\n" + "=" * 60)
    if all_passed:
        print("[SUCCESS] TODAS LAS VERIFICACIONES PASARON")
        print("\nProximos pasos:")
        print("  1. Sincronizar actividades:")
        print("     python -m py_strava.main")
        print("\n  2. Generar informe:")
        print("     python -m py_strava.informe_strava")
        print("\n  3. Inicializar base de datos (si no esta hecha):")
        print("     python scripts/init_database.py")
        print("\n  4. Ver ejemplos de uso:")
        print("     python examples/ejemplo_uso_bd.py")
    else:
        print("[ERROR] ALGUNAS VERIFICACIONES FALLARON")
        print("\nAcciones recomendadas:")
        print("  1. Revisa los errores marcados con [FAIL] arriba")
        print("  2. Consulta docs/user/SOLUCION_ERRORES.md")
        print("  3. Verifica que ejecutas desde la raiz del proyecto")
        print("  4. Asegurate de que el venv esta activado")
    print("=" * 60)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
