# Scripts de Utilidad

Este directorio contiene scripts de utilidad para el proyecto.

## diagnostico_tests.py

Script de diagnóstico automático del entorno de testing.

### Uso

```bash
python scripts/diagnostico_tests.py
```

### Descripción

Este script verifica automáticamente que el entorno de testing esté correctamente configurado. Realiza las siguientes verificaciones:

1. **Versión de Python** - Verifica Python >= 3.8
2. **Dependencias** - pytest, pytest-cov, pytest-mock
3. **Estructura de directorios** - tests/, data/test/, json/test/, etc.
4. **Archivos de datos** - CSV y JSON de prueba
5. **Archivos de test** - Todos los test_*.py
6. **pytest.ini** - Configuración de pytest
7. **Test simple** - Ejecuta un test básico

### Salida

El script muestra un reporte detallado con ✅ o ❌ para cada verificación y un resumen final.

### Cuándo usarlo

- Después de clonar el repositorio
- Cuando los tests fallan inesperadamente
- Antes de reportar un error
- Después de actualizar dependencias

### Características

- Compatible con Windows (manejo correcto de encoding UTF-8)
- Timeout de 30 segundos para tests
- Mensajes claros y detallados
- Exit code 0 si todo OK, 1 si hay errores

### Documentación completa

Ver [docs/dev/GUIA_TESTING.md](../docs/dev/GUIA_TESTING.md) para más información.
