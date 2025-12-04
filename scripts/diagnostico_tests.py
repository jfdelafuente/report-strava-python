#!/usr/bin/env python
"""
Script de diagnóstico para el entorno de testing.

Verifica que todas las dependencias y archivos necesarios estén correctamente configurados.
"""

import os
import sys
from pathlib import Path

# Configurar encoding para Windows
if sys.platform == "win32":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


def verificar_python():
    """Verificar versión de Python."""
    print("=" * 60)
    print("1. VERIFICACIÓN DE PYTHON")
    print("=" * 60)
    print(f"Versión de Python: {sys.version}")
    print(f"Ejecutable: {sys.executable}")

    version_info = sys.version_info
    if version_info.major >= 3 and version_info.minor >= 8:
        print("✅ Versión de Python es compatible (>=3.8)")
    else:
        print("❌ Versión de Python no compatible. Requiere Python 3.8+")
        return False
    print()
    return True


def verificar_dependencias():
    """Verificar que pytest y plugins estén instalados."""
    print("=" * 60)
    print("2. VERIFICACIÓN DE DEPENDENCIAS")
    print("=" * 60)

    dependencias = {"pytest": "pytest", "pytest-cov": "pytest_cov", "pytest-mock": "pytest_mock"}

    todas_ok = True
    for nombre, modulo in dependencias.items():
        try:
            mod = __import__(modulo)
            version = getattr(mod, "__version__", "desconocida")
            print(f"✅ {nombre}: v{version}")
        except ImportError:
            print(f"❌ {nombre}: NO INSTALADO")
            todas_ok = False

    print()
    return todas_ok


def verificar_estructura_directorios():
    """Verificar que existan los directorios necesarios."""
    print("=" * 60)
    print("3. VERIFICACIÓN DE ESTRUCTURA DE DIRECTORIOS")
    print("=" * 60)

    base_dir = Path(__file__).parent.parent
    directorios = ["tests", "tests/unit", "data/test", "json/test", "bd", "py_strava", "docs/dev"]

    todas_ok = True
    for directorio in directorios:
        path = base_dir / directorio
        if path.exists():
            print(f"✅ {directorio}/")
        else:
            print(f"❌ {directorio}/ - NO EXISTE")
            todas_ok = False

    print()
    return todas_ok


def verificar_archivos_datos():
    """Verificar que existan los archivos de datos de prueba."""
    print("=" * 60)
    print("4. VERIFICACIÓN DE ARCHIVOS DE DATOS DE PRUEBA")
    print("=" * 60)

    base_dir = Path(__file__).parent.parent
    archivos = ["data/test/strava_activities_all_fields.csv", "json/test/strava_tokens.json"]

    todas_ok = True
    for archivo in archivos:
        path = base_dir / archivo
        if path.exists():
            size = path.stat().st_size
            print(f"✅ {archivo} ({size} bytes)")
        else:
            print(f"❌ {archivo} - NO EXISTE")
            todas_ok = False

    print()
    return todas_ok


def verificar_archivos_test():
    """Verificar que existan los archivos de test."""
    print("=" * 60)
    print("5. VERIFICACIÓN DE ARCHIVOS DE TEST")
    print("=" * 60)

    base_dir = Path(__file__).parent.parent
    test_dir = base_dir / "tests" / "unit"

    if not test_dir.exists():
        print(f"❌ Directorio {test_dir} no existe")
        return False

    archivos_test = list(test_dir.glob("test_*.py"))
    print(f"Encontrados {len(archivos_test)} archivos de test:")

    for archivo in sorted(archivos_test):
        print(f"  ✅ {archivo.name}")

    print()
    return len(archivos_test) > 0


def verificar_pytest_ini():
    """Verificar configuración de pytest."""
    print("=" * 60)
    print("6. VERIFICACIÓN DE PYTEST.INI")
    print("=" * 60)

    base_dir = Path(__file__).parent.parent
    pytest_ini = base_dir / "pytest.ini"

    if pytest_ini.exists():
        print(f"✅ pytest.ini encontrado")
        with open(pytest_ini, encoding="utf-8") as f:
            contenido = f.read()
            print("\nContenido:")
            print("-" * 40)
            print(contenido[:500])
            if len(contenido) > 500:
                print("...")
    else:
        print(f"❌ pytest.ini NO EXISTE")
        return False

    print()
    return True


def ejecutar_test_simple():
    """Ejecutar un test simple para verificar que pytest funciona."""
    print("=" * 60)
    print("7. EJECUCIÓN DE TEST SIMPLE")
    print("=" * 60)

    import subprocess

    base_dir = Path(__file__).parent.parent
    os.chdir(base_dir)

    try:
        # Ejecutar un test simple
        resultado = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/unit/test_version.py", "-v"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if resultado.returncode == 0:
            print("✅ Tests ejecutados correctamente")
            print("\nSalida:")
            print(resultado.stdout[-500:] if len(resultado.stdout) > 500 else resultado.stdout)
        else:
            print("❌ Tests fallaron")
            print("\nError:")
            print(resultado.stderr[-500:] if len(resultado.stderr) > 500 else resultado.stderr)
            return False
    except Exception as e:
        print(f"❌ Error al ejecutar pytest: {e}")
        return False

    print()
    return True


def main():
    """Ejecutar todas las verificaciones."""
    print("\n" + "=" * 60)
    print("DIAGNÓSTICO DEL ENTORNO DE TESTING")
    print("=" * 60)
    print()

    resultados = []

    # Ejecutar verificaciones
    resultados.append(("Python", verificar_python()))
    resultados.append(("Dependencias", verificar_dependencias()))
    resultados.append(("Estructura de directorios", verificar_estructura_directorios()))
    resultados.append(("Archivos de datos", verificar_archivos_datos()))
    resultados.append(("Archivos de test", verificar_archivos_test()))
    resultados.append(("pytest.ini", verificar_pytest_ini()))
    resultados.append(("Test simple", ejecutar_test_simple()))

    # Resumen
    print("=" * 60)
    print("RESUMEN")
    print("=" * 60)

    for nombre, ok in resultados:
        estado = "✅ OK" if ok else "❌ ERROR"
        print(f"{nombre:.<40} {estado}")

    print()

    total_ok = sum(1 for _, ok in resultados if ok)
    total = len(resultados)

    if total_ok == total:
        print(f"✅ Todas las verificaciones pasaron ({total_ok}/{total})")
        print("\n🎉 El entorno está correctamente configurado!")
        return 0
    else:
        print(f"⚠️  Algunas verificaciones fallaron ({total_ok}/{total})")
        print("\n❌ El entorno necesita correcciones.")
        print("\nConsulta la guía en: docs/dev/GUIA_TESTING.md")
        return 1


if __name__ == "__main__":
    sys.exit(main())
