# Inicialización de Base de Datos SQLite

Este documento describe cómo usar el script `init_database.py` para crear y gestionar la base de datos SQLite de la aplicación Strava.

## Descripción

El script `init_database.py` crea las tablas necesarias para almacenar:

- **Activities**: Actividades deportivas de Strava
- **Kudos**: Kudos recibidos en cada actividad

## Ubicación de la Base de Datos

La base de datos se crea en:
```
bd/strava.sqlite
```

## Uso

### 1. Crear las tablas (primera vez)

```bash
python init_database.py
```

Este comando:
- Crea las tablas `Activities` y `Kudos` si no existen
- Verifica que las tablas se crearon correctamente
- Muestra estadísticas de la base de datos

### 2. Verificar tablas existentes

```bash
python init_database.py --verify
```

Este comando:
- Verifica que las tablas existan
- Muestra las columnas de cada tabla
- Muestra estadísticas (número de registros)

### 3. Resetear la base de datos

```bash
python init_database.py --reset
```

⚠️ **¡CUIDADO!** Este comando:
- Elimina TODAS las tablas y datos existentes
- Recrea las tablas vacías
- Solicita confirmación antes de ejecutar

## Estructura de las Tablas

### Tabla Activities

Almacena las actividades deportivas de Strava:

| Columna               | Tipo    | Descripción                           |
|-----------------------|---------|---------------------------------------|
| id_activity           | INTEGER | ID único de la actividad (PRIMARY KEY)|
| name                  | TEXT    | Nombre de la actividad                |
| start_date_local      | TEXT    | Fecha y hora de inicio                |
| type                  | TEXT    | Tipo de actividad (Run, Ride, etc.)  |
| distance              | REAL    | Distancia en metros                   |
| moving_time           | REAL    | Tiempo en movimiento (segundos)       |
| elapsed_time          | REAL    | Tiempo total (segundos)               |
| total_elevation_gain  | REAL    | Desnivel positivo (metros)            |
| end_latlng            | TEXT    | Coordenadas finales                   |
| kudos_count           | INTEGER | Número de kudos                       |
| external_id           | INTEGER | ID externo                            |

### Tabla Kudos

Almacena los kudos recibidos en cada actividad:

| Columna         | Tipo    | Descripción                           |
|-----------------|---------|---------------------------------------|
| id_kudos        | INTEGER | ID único del kudo (PRIMARY KEY)       |
| resource_state  | TEXT    | Estado del recurso                    |
| firstname       | TEXT    | Nombre del usuario que dio el kudo    |
| lastname        | TEXT    | Apellido del usuario                  |
| id_activity     | INTEGER | ID de la actividad (FOREIGN KEY)      |

La tabla Kudos tiene una **relación de clave foránea** con Activities mediante `id_activity`.

## Ejemplos de Salida

### Creación exitosa:

```
2025-12-03 14:31:15,937 - INFO - Ruta de base de datos: bd\strava.sqlite
2025-12-03 14:31:15,956 - INFO - Inicializando base de datos...
2025-12-03 14:31:15,956 - INFO - Creando tablas...
2025-12-03 14:31:15,964 - INFO -   ✓ Tabla 'Activities' creada
2025-12-03 14:31:15,967 - INFO -   ✓ Tabla 'Kudos' creada
2025-12-03 14:31:15,967 - INFO - ✓ Base de datos inicializada correctamente
```

### Verificación:

```
2025-12-03 14:31:33,712 - INFO - Verificando tablas existentes...
2025-12-03 14:31:33,712 - INFO -   ✓ Tabla 'Activities' existe
2025-12-03 14:31:33,713 - INFO -     Columnas: id_activity, name, start_date_local, type, distance...
2025-12-03 14:31:33,713 - INFO -   ✓ Tabla 'Kudos' existe
2025-12-03 14:31:33,713 - INFO -     Columnas: id_kudos, resource_state, firstname, lastname...
2025-12-03 14:31:33,714 - INFO - ✓ Todas las tablas están correctamente creadas
```

## Características Técnicas

- **Seguridad**: Foreign keys habilitadas para mantener integridad referencial
- **Rendimiento**: Modo WAL (Write-Ahead Logging) para mejor concurrencia
- **Transacciones**: Uso de context managers para garantizar commits/rollbacks automáticos
- **Logging**: Registro detallado de todas las operaciones

## Solución de Problemas

### Error: "Table already exists"

Si recibes este error, las tablas ya están creadas. Usa `--verify` para verificar o `--reset` para recrearlas.

### Error: "Database is locked"

Asegúrate de que no hay otra aplicación usando la base de datos. Cierra cualquier conexión abierta.

### Error de permisos

Verifica que tienes permisos de escritura en el directorio `bd/`.

## Próximos Pasos

Después de inicializar la base de datos:

1. Configura tus tokens de Strava en `json/strava_tokens.json`
2. Ejecuta el script principal para obtener actividades:
   ```bash
   python -m py_strava.main
   ```
3. Genera informes:
   ```bash
   python -m py_strava.informe_strava
   ```

## Ayuda

Para ver todas las opciones disponibles:

```bash
python init_database.py --help
```
