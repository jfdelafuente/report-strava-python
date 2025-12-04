"""
Módulo para gestionar operaciones de base de datos PostgreSQL de forma segura y eficiente.

Este módulo proporciona una interfaz de alto nivel para PostgreSQL con:
- Pool de conexiones para mejor rendimiento
- Context managers para gestión automática de recursos
- Logging profesional
- Transacciones batch para mejor rendimiento
- Prevención de SQL injection con parámetros preparados
- API compatible con strava_db_sqlite para intercambiabilidad
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor

# Configurar logger para este módulo
logger = logging.getLogger(__name__)

# Pool global de conexiones
_connection_pool: Optional[pool.SimpleConnectionPool] = None


def _load_credentials() -> Dict[str, Any]:
    """
    Carga credenciales desde archivo JSON o variables de entorno.

    Returns:
        Diccionario con credenciales de PostgreSQL

    Raises:
        FileNotFoundError: Si no hay archivo ni variables de entorno
    """
    credentials_file = Path("./bd/postgres_credentials.json")

    # Intentar leer desde archivo JSON primero
    if credentials_file.exists():
        with open(credentials_file) as f:
            postgres_credentials = json.load(f)
            return {
                "host": postgres_credentials["server"],
                "database": postgres_credentials["database"],
                "user": postgres_credentials["username"],
                "password": postgres_credentials["password"],
                "port": postgres_credentials["port"],
            }
    else:
        # Usar variables de entorno como respaldo
        try:
            from py_strava.config import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER

            return {
                "host": DB_HOST,
                "database": DB_NAME,
                "user": DB_USER,
                "password": DB_PASSWORD,
                "port": DB_PORT,
            }
        except ImportError:
            raise FileNotFoundError(
                "No se encontró archivo de credenciales ni configuración en variables de entorno. "
                "Crea './bd/postgres_credentials.json' o configura py_strava.config"
            )


def initialize_pool(minconn: int = 1, maxconn: int = 10) -> None:
    """
    Inicializa el pool de conexiones PostgreSQL.

    Esta función debe llamarse una vez al inicio de la aplicación.
    El pool reutiliza conexiones para mejor rendimiento.

    Args:
        minconn: Número mínimo de conexiones en el pool
        maxconn: Número máximo de conexiones en el pool

    Example:
        >>> # Al inicio de la aplicación
        >>> initialize_pool(minconn=2, maxconn=10)
    """
    global _connection_pool

    if _connection_pool is not None:
        logger.warning("Pool de conexiones ya inicializado")
        return

    try:
        credentials = _load_credentials()

        _connection_pool = pool.SimpleConnectionPool(
            minconn,
            maxconn,
            host=credentials["host"],
            database=credentials["database"],
            user=credentials["user"],
            password=credentials["password"],
            port=credentials["port"],
        )

        logger.info(
            f"Pool de conexiones PostgreSQL inicializado "
            f"(min={minconn}, max={maxconn}, db={credentials['database']})"
        )

    except Exception as e:
        logger.error(f"Error inicializando pool de conexiones: {e}")
        raise


def close_pool() -> None:
    """
    Cierra el pool de conexiones.

    Debe llamarse al finalizar la aplicación para liberar recursos.
    """
    global _connection_pool

    if _connection_pool is not None:
        _connection_pool.closeall()
        _connection_pool = None
        logger.info("Pool de conexiones cerrado")


class DatabaseConnection:
    """
    Context manager para conexiones PostgreSQL con pool.

    Gestiona automáticamente la obtención y devolución de conexiones al pool,
    además de commit/rollback según el resultado de las operaciones.

    Example:
        >>> # Inicializar pool una vez
        >>> initialize_pool()
        >>>
        >>> # Usar context manager
        >>> with DatabaseConnection() as conn:
        ...     insert(conn, 'activities', {'name': 'Running', 'distance': 5000})
        ...     # Auto-commit y auto-devolución al pool
    """

    def __init__(self):
        """Inicializa el context manager."""
        global _connection_pool

        if _connection_pool is None:
            # Auto-inicializar pool si no existe
            initialize_pool()

        self.conn: Optional[psycopg2.extensions.connection] = None

    def __enter__(self) -> psycopg2.extensions.connection:
        """
        Obtiene una conexión del pool al entrar en el context manager.

        Returns:
            Conexión PostgreSQL del pool
        """
        self.conn = _connection_pool.getconn()
        logger.debug("Conexión obtenida del pool")
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Devuelve la conexión al pool al salir del context manager.

        Hace commit si no hubo errores, rollback si los hubo.
        """
        if self.conn:
            if exc_type is None:
                self.conn.commit()
                logger.debug("Transacción commiteada")
            else:
                self.conn.rollback()
                logger.warning(f"Transacción revertida por error: {exc_val}")

            # Devolver conexión al pool (NO cerrar)
            _connection_pool.putconn(self.conn)
            logger.debug("Conexión devuelta al pool")

        return False  # No suprimir excepciones


def sql_connection() -> psycopg2.extensions.connection:
    """
    Establece conexión con PostgreSQL (legacy function).

    NOTA: Para nuevo código, se recomienda usar DatabaseConnection como context manager.
    Esta función se mantiene para compatibilidad con código existente.

    Returns:
        Objeto de conexión PostgreSQL

    Raises:
        psycopg2.Error: Si hay error al conectar

    Example:
        >>> conn = sql_connection()
        >>> try:
        ...     # Usar conexión
        ...     pass
        ... finally:
        ...     conn.close()
    """
    global _connection_pool

    # Auto-inicializar pool si no existe
    if _connection_pool is None:
        initialize_pool()

    try:
        conn = _connection_pool.getconn()
        logger.info("Conexión PostgreSQL establecida (legacy mode)")
        return conn

    except psycopg2.Error as e:
        logger.error(f"Error al conectar con PostgreSQL: {e}")
        raise


def execute(
    conn: psycopg2.extensions.connection,
    sql_statement: str,
    params: Optional[Union[Tuple, List]] = None,
    commit: bool = True,
) -> psycopg2.extensions.cursor:
    """
    Ejecuta un statement SQL de forma segura con parámetros preparados.

    PostgreSQL usa %s como placeholder (no ? como SQLite).

    Args:
        conn: Conexión activa a la base de datos
        sql_statement: Statement SQL con placeholders '%s'
        params: Parámetros para el statement SQL
        commit: Si True, hace commit automáticamente

    Returns:
        Cursor con el resultado de la operación

    Raises:
        psycopg2.Error: Si ocurre un error durante la ejecución

    Example:
        >>> with DatabaseConnection() as conn:
        ...     execute(conn, "INSERT INTO activities (name) VALUES (%s)", ("Running",))
    """
    cur = conn.cursor()

    try:
        if params:
            cur.execute(sql_statement, params)
        else:
            cur.execute(sql_statement)

        if commit:
            conn.commit()
            logger.debug(f"Statement ejecutado y commiteado: {sql_statement[:50]}...")
        else:
            logger.debug(f"Statement ejecutado (sin commit): {sql_statement[:50]}...")

        return cur

    except psycopg2.Error as e:
        logger.error(
            f"Error ejecutando SQL en PostgreSQL\n"
            f"Statement: {sql_statement}\n"
            f"Params: {params}\n"
            f"Error: {e}"
        )
        raise


def execute_many(
    conn: psycopg2.extensions.connection, sql_statement: str, params_list: List[Tuple]
) -> int:
    """
    Ejecuta múltiples inserts/updates de forma eficiente (batch).

    Args:
        conn: Conexión activa a la base de datos
        sql_statement: Statement SQL con placeholders '%s'
        params_list: Lista de tuplas con parámetros

    Returns:
        Número de filas afectadas

    Example:
        >>> records = [
        ...     ("Running", 5000),
        ...     ("Cycling", 20000)
        ... ]
        >>> with DatabaseConnection() as conn:
        ...     count = execute_many(
        ...         conn,
        ...         "INSERT INTO activities (name, distance) VALUES (%s, %s)",
        ...         records
        ...     )
    """
    cur = conn.cursor()

    try:
        cur.executemany(sql_statement, params_list)
        conn.commit()

        rows_affected = cur.rowcount
        logger.info(f"Batch ejecutado: {rows_affected} filas afectadas")

        return rows_affected

    except psycopg2.Error as e:
        logger.error(f"Error en batch execution: {e}")
        raise
    finally:
        cur.close()


def fetch(
    conn: psycopg2.extensions.connection,
    sql_statement: str,
    params: Optional[Union[Tuple, List]] = None,
    as_dict: bool = False,
) -> List:
    """
    Ejecuta una consulta SQL SELECT y retorna los resultados.

    Args:
        conn: Conexión activa a la base de datos
        sql_statement: Statement SQL SELECT con placeholders '%s'
        params: Parámetros para el statement SQL
        as_dict: Si True, retorna diccionarios; si False, tuplas

    Returns:
        Lista de resultados (tuplas o diccionarios según as_dict)

    Raises:
        psycopg2.Error: Si ocurre un error durante la ejecución

    Example:
        >>> with DatabaseConnection() as conn:
        ...     # Tuplas
        ...     results = fetch(conn, "SELECT * FROM activities WHERE distance > %s", (5000,))
        ...     # Diccionarios
        ...     results = fetch(
        ...         conn,
        ...         "SELECT * FROM activities WHERE distance > %s",
        ...         (5000,),
        ...         as_dict=True
        ...     )
        ...     for row in results:
        ...         print(row['name'], row['distance'])
    """
    cursor_factory = RealDictCursor if as_dict else None
    cur = conn.cursor(cursor_factory=cursor_factory)

    try:
        if params:
            cur.execute(sql_statement, params)
        else:
            cur.execute(sql_statement)

        results = cur.fetchall()
        logger.debug(f"Query ejecutado: {len(results)} filas obtenidas")

        return results

    except psycopg2.Error as e:
        logger.error(
            f"Error ejecutando query\n"
            f"Statement: {sql_statement}\n"
            f"Params: {params}\n"
            f"Error: {e}"
        )
        raise
    finally:
        cur.close()


def fetch_one(
    conn: psycopg2.extensions.connection,
    sql_statement: str,
    params: Optional[Union[Tuple, List]] = None,
    as_dict: bool = False,
) -> Optional[Any]:
    """
    Ejecuta una consulta SQL y retorna solo la primera fila.

    Args:
        conn: Conexión activa a la base de datos
        sql_statement: Statement SQL SELECT
        params: Parámetros para el statement
        as_dict: Si True, retorna diccionario; si False, tupla

    Returns:
        Primera fila del resultado o None si no hay resultados

    Example:
        >>> with DatabaseConnection() as conn:
        ...     activity = fetch_one(
        ...         conn,
        ...         "SELECT * FROM activities WHERE id_activity = %s",
        ...         (12345,),
        ...         as_dict=True
        ...     )
        ...     if activity:
        ...         print(activity['name'])
    """
    cursor_factory = RealDictCursor if as_dict else None
    cur = conn.cursor(cursor_factory=cursor_factory)

    try:
        if params:
            cur.execute(sql_statement, params)
        else:
            cur.execute(sql_statement)

        result = cur.fetchone()
        return result

    except psycopg2.Error as e:
        logger.error(f"Error en fetch_one: {e}")
        raise
    finally:
        cur.close()


def insert(
    conn: psycopg2.extensions.connection,
    table_name: str,
    record: Dict[str, Any],
    returning: Optional[str] = None,
    commit: bool = True,
) -> Optional[Any]:
    """
    Inserta un registro en una tabla de forma segura.

    PostgreSQL soporta la cláusula RETURNING para obtener valores generados.

    Args:
        conn: Conexión activa a la base de datos
        table_name: Nombre de la tabla
        record: Diccionario con columna: valor
        returning: Columna a retornar (ej: 'id' para obtener ID generado)
        commit: Si True, hace commit automáticamente

    Returns:
        Valor de la columna RETURNING si se especificó, sino None

    Example:
        >>> with DatabaseConnection() as conn:
        ...     # Insertar y obtener ID generado
        ...     activity_id = insert(
        ...         conn,
        ...         'activities',
        ...         {'name': 'Running', 'distance': 5000},
        ...         returning='id'
        ...     )
        ...     print(f"ID generado: {activity_id}")
    """
    columns = ",".join(record.keys())
    placeholders = ",".join(["%s" for _ in record.keys()])

    statement = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

    if returning:
        statement += f" RETURNING {returning}"

    params = tuple(record.values())

    cur = execute(conn, statement, params, commit=commit)

    try:
        if returning:
            result = cur.fetchone()[0]
            logger.debug(f"Registro insertado en {table_name}, {returning}={result}")
            return result
        else:
            logger.debug(f"Registro insertado en {table_name}")
            return None
    finally:
        cur.close()


def insert_many(
    conn: psycopg2.extensions.connection, table_name: str, records: List[Dict[str, Any]]
) -> int:
    """
    Inserta múltiples registros de forma eficiente (batch).

    Args:
        conn: Conexión activa a la base de datos
        table_name: Nombre de la tabla
        records: Lista de diccionarios con los datos

    Returns:
        Número de registros insertados

    Example:
        >>> records = [
        ...     {'name': 'Running', 'distance': 5000},
        ...     {'name': 'Cycling', 'distance': 20000}
        ... ]
        >>> with DatabaseConnection() as conn:
        ...     count = insert_many(conn, 'activities', records)
        ...     print(f"{count} registros insertados")
    """
    if not records:
        return 0

    # Usar las claves del primer registro para todas las inserciones
    columns = ",".join(records[0].keys())
    placeholders = ",".join(["%s" for _ in records[0].keys()])

    statement = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

    # Convertir cada dict a tupla de valores
    params_list = [tuple(record.values()) for record in records]

    rows_affected = execute_many(conn, statement, params_list)
    logger.info(f"{rows_affected} registros insertados en {table_name}")

    return rows_affected


def update(
    conn: psycopg2.extensions.connection,
    table_name: str,
    updates: Dict[str, Any],
    where_clause: str,
    where_params: Optional[Tuple] = None,
) -> int:
    """
    Actualiza registros en una tabla.

    Args:
        conn: Conexión activa a la base de datos
        table_name: Nombre de la tabla
        updates: Diccionario con columna: nuevo_valor
        where_clause: Cláusula WHERE (ej: "id = %s")
        where_params: Parámetros para la cláusula WHERE

    Returns:
        Número de filas actualizadas

    Example:
        >>> with DatabaseConnection() as conn:
        ...     rows = update(
        ...         conn,
        ...         'activities',
        ...         {'kudos_count': 10},
        ...         "id_activity = %s",
        ...         (12345,)
        ...     )
        ...     print(f"{rows} filas actualizadas")
    """
    set_clause = ",".join([f"{col} = %s" for col in updates.keys()])
    statement = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"

    params = list(updates.values())
    if where_params:
        params.extend(where_params)

    cur = execute(conn, statement, tuple(params))
    rows_affected = cur.rowcount
    cur.close()

    logger.debug(f"{rows_affected} filas actualizadas en {table_name}")
    return rows_affected


def insert_statement(table_name: str, record: Dict[str, Any]) -> Tuple[str, Tuple]:
    """
    Genera un statement SQL INSERT seguro con parámetros preparados.

    Esta función construye un statement INSERT usando placeholders para prevenir
    SQL injection. Los valores se retornan por separado como tupla de parámetros.

    NOTA: Para nuevo código, se recomienda usar la función insert() directamente.
    Esta función se mantiene para compatibilidad con código existente.

    PostgreSQL usa %s como placeholder (no ? como SQLite).

    Args:
        table_name: Nombre de la tabla donde insertar los datos
        record: Diccionario con los datos a insertar. Las claves son los
                nombres de las columnas y los valores son los datos

    Returns:
        Una tupla de dos elementos:
            - str: Statement SQL INSERT con placeholders '%s'
            - tuple: Tupla con los valores a insertar

    Example:
        >>> record = {'name': 'Running', 'distance': 5000, 'date': '2025-11-30'}
        >>> stmt, params = insert_statement('activities', record)
        >>> print(stmt)
        INSERT INTO activities (name,distance,date) VALUES (%s,%s,%s)
        >>> print(params)
        ('Running', 5000, '2025-11-30')
        >>> commit(conn, stmt, params)
    """
    columns = ",".join(record.keys())
    placeholders = ",".join(["%s" for _ in record.keys()])
    statement = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
    params = tuple(record.values())

    return statement, params


def commit(
    conn: psycopg2.extensions.connection,
    sql_statement: Union[str, Tuple[str, Tuple]],
    params: Optional[Tuple] = None,
) -> None:
    """
    Ejecuta un statement SQL y realiza commit en la base de datos.

    Esta función mantiene compatibilidad con código legacy. Para nuevo código,
    se recomienda usar execute() o insert() directamente.

    Args:
        conn: Conexión activa a la base de datos
        sql_statement: Statement SQL a ejecutar, o tupla (statement, params)
                      retornada por insert_statement()
        params: Tupla de parámetros para el statement SQL (opcional si
                sql_statement ya es una tupla)

    Raises:
        psycopg2.Error: Si ocurre un error durante la ejecución del statement

    Example:
        >>> conn = sql_connection()
        >>> # Opción 1: statement y params separados
        >>> commit(conn, "INSERT INTO activities (name) VALUES (%s)", ("Running",))
        >>> # Opción 2: usando insert_statement
        >>> stmt, params = insert_statement('activities', {'name': 'Cycling'})
        >>> commit(conn, stmt, params)
        >>> conn.close()
    """
    # Soporte para compatibilidad con insert_statement que retorna (stmt, params)
    if isinstance(sql_statement, tuple):
        stmt, stmt_params = sql_statement
        execute(conn, stmt, stmt_params, commit=True)
    else:
        execute(conn, sql_statement, params, commit=True)

    logger.info("Statement committed")


# Mantener compatibilidad con código existente que espera print
# pero solo si el logging está en nivel DEBUG o inferior
if logger.level <= logging.DEBUG:
    _original_commit = commit

    def commit(*args, **kwargs):
        _original_commit(*args, **kwargs)
        print("statement committed")
