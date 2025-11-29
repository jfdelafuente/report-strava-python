#!/usr/bin/env python
"""
Script de verificación para comprobar que el proyecto está configurado correctamente.
"""

import sys
from pathlib import Path


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

    # Test 2: Import de strava_bd_postgres (opcional si no hay psycopg2)
    try:
        from py_strava.strava import strava_bd_postgres
        print(f"{check_mark(True)} py_strava.strava.strava_bd_postgres importado correctamente")
        tests.append(True)
    except ImportError as e:
        if 'psycopg2' in str(e):
            print(f"[INFO] strava_bd_postgres (requiere psycopg2 - usa SQLite en su lugar)")
            tests.append(True)  # No falla el test
        else:
            print(f"{check_mark(False)} Error al importar strava_bd_postgres: {e}")
            tests.append(False)
    except Exception as e:
        print(f"{check_mark(False)} Error al importar strava_bd_postgres: {e}")
        tests.append(False)

    # Test 3: Import de strava_bd_1
    try:
        from py_strava.strava import strava_bd_1
        print(f"{check_mark(True)} py_strava.strava.strava_bd_1 importado correctamente")
        tests.append(True)
    except Exception as e:
        print(f"{check_mark(False)} Error al importar strava_bd_1: {e}")
        tests.append(False)

    # Test 4: Import de strava_token_1
    try:
        from py_strava.strava import strava_token_1
        print(f"{check_mark(True)} py_strava.strava.strava_token_1 importado correctamente")
        tests.append(True)
    except Exception as e:
        print(f"{check_mark(False)} Error al importar strava_token_1: {e}")
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

    base_dir = Path.cwd()
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

    base_dir = Path.cwd()
    files_to_check = [
        ('py_strava/__init__.py', True),
        ('py_strava/strava/__init__.py', True),
        ('py_strava/config.py', True),
        ('py_strava/main.py', True),
        ('py_strava/informe_strava.py', True),
        ('requirements.txt', True),
        ('bd/postgres_credentials.json', False),  # Opcional
        ('json/strava_tokens.json', False),  # Opcional
    ]

    for file_path, required in files_to_check:
        full_path = base_dir / file_path
        exists = full_path.exists() and full_path.is_file()

        if required:
            print(f"{check_mark(exists)} {file_path} {'(REQUERIDO)' if required else '(opcional)'}")
        else:
            status = "[OK]" if exists else "[INFO]"
            print(f"{status}  {file_path} (opcional - {'encontrado' if exists else 'no encontrado'})")


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
    print("=" * 60)
    print("VERIFICACIÓN DE CONFIGURACIÓN - py-strava")
    print("=" * 60)

    results = []

    # Ejecutar tests
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
        print("\nPuedes ejecutar:")
        print("  python -m py_strava.main")
        print("  python -m py_strava.informe_strava")
    else:
        print("[ERROR] ALGUNAS VERIFICACIONES FALLARON")
        print("\nRevisa los errores arriba y consulta SOLUCION_ERRORES.md")
    print("=" * 60)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
