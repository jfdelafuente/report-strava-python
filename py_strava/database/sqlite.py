"""
Módulo para gestionar operaciones de base de datos SQLite de forma segura y eficiente.

Este módulo proporciona una interfaz de alto nivel para SQLite con:
- Context managers para gestión automática de recursos
- Logging profesional
- Transacciones batch para mejor rendimiento
- Prevención de SQL injection con parámetros preparados
- Configuración optimizada de SQLite
"""

import sqlite3
import logging
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Any, Union
from contextlib import contextmanager

# Configurar logger para este módulo
logger = logging.getLogger(__name__)


class DatabaseConnection:
    """
    Gestor de conexiones SQLite con configuración optimizada.

    Usa context manager para asegurar que las conexiones se cierren correctamente.

    Example:
        >>> with DatabaseConnection('bd/strava.sqlite') as conn:
        ...     insert(conn, 'activities', {'name': 'Running', 'distance': 5000})
    """

    def __init__(self, db_path: str, timeout: float = 5.0):
        """
        Inicializa la conexión a la base de datos.

        Args:
            db_path: Ruta al archivo de base de datos SQLite
            timeout: Tiempo de espera en segundos para locks
        """
        self.db_path = db_path
        self.timeout = timeout
        self.conn: Optional[sqlite3.Connection] = None

    def __enter__(self) -> sqlite3.Connection:
        """Abre la conexión al entrar en el context manager."""
        try:
            self.conn = sqlite3.connect(self.db_path, timeout=self.timeout)

            # Configuración optimizada de SQLite
            self.conn.execute("PRAGMA foreign_keys = ON")  # Habilitar foreign keys
            self.conn.execute("PRAGMA journal_mode = WAL")  # Write-Ahead Logging para mejor concurrencia

            # Row factory para retornar diccionarios en lugar de tuplas
            self.conn.row_factory = sqlite3.Row

            logger.info(f"Conexión establecida con {self.db_path}")
            return self.conn

        except sqlite3.Error as e:
            logger.error(f"Error al conectar con la base de datos {self.db_path}: {e}")
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cierra la conexión al salir del context manager."""
        if self.conn:
            if exc_type is None:
                self.conn.commit()
                logger.debug("Transacción commiteada")
            else:
                self.conn.rollback()
                logger.warning("Transacción revertida por error")

            self.conn.close()
            logger.info("Conexión cerrada")

        return False  # No suprimir excepciones


def sql_connection(db_path: str, timeout: float = 5.0) -> sqlite3.Connection:
    """
    Establece una conexión a una base de datos SQLite.

    NOTA: Para nuevo código, se recomienda usar DatabaseConnection como context manager.

    Args:
        db_path: Ruta al archivo de base de datos SQLite
        timeout: Tiempo de espera en segundos para locks

    Returns:
        Objeto de conexión a la base de datos

    Raises:
        sqlite3.Error: Si hay un error al conectar con la base de datos

    Example:
        >>> conn = sql_connection('bd/strava.sqlite')
        >>> try:
        ...     # Usar la conexión
        ...     pass
        ... finally:
        ...     conn.close()
    """
    try:
        conn = sqlite3.connect(db_path, timeout=timeout)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.row_factory = sqlite3.Row
        logger.info(f"Conexión establecida: {db_path}")
        return conn
    except sqlite3.Error as e:
        logger.error(f"Error al conectar con la base de datos: {e}")
        raise


def execute(
    conn: sqlite3.Connection,
    sql_statement: str,
    params: Optional[Union[Tuple, List]] = None,
    commit: bool = True
) -> sqlite3.Cursor:
    """
    Ejecuta un statement SQL de forma segura.

    Args:
        conn: Conexión activa a la base de datos
        sql_statement: Statement SQL con placeholders '?'
        params: Parámetros para el statement SQL
        commit: Si True, hace commit automáticamente

    Returns:
        Cursor con el resultado de la operación

    Raises:
        sqlite3.Error: Si ocurre un error durante la ejecución

    Example:
        >>> with DatabaseConnection('bd/strava.sqlite') as conn:
        ...     execute(conn, "INSERT INTO activities (name) VALUES (?)", ("Running",))
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

    except sqlite3.Error as e:
        logger.error(
            f"Error ejecutando SQL\n"
            f"Statement: {sql_statement}\n"
            f"Params: {params}\n"
            f"Error: {e}"
        )
        raise


def execute_many(
    conn: sqlite3.Connection,
    sql_statement: str,
    params_list: List[Tuple]
) -> int:
    """
    Ejecuta múltiples inserts/updates de forma eficiente (batch).

    Args:
        conn: Conexión activa a la base de datos
        sql_statement: Statement SQL con placeholders '?'
        params_list: Lista de tuplas con parámetros

    Returns:
        Número de filas afectadas

    Example:
        >>> records = [
        ...     ("Running", 5000),
        ...     ("Cycling", 20000)
        ... ]
        >>> with DatabaseConnection('bd/strava.sqlite') as conn:
        ...     count = execute_many(
        ...         conn,
        ...         "INSERT INTO activities (name, distance) VALUES (?, ?)",
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

    except sqlite3.Error as e:
        logger.error(f"Error en batch execution: {e}")
        raise
    finally:
        cur.close()


def fetch(
    conn: sqlite3.Connection,
    sql_statement: str,
    params: Optional[Union[Tuple, List]] = None
) -> List[sqlite3.Row]:
    """
    Ejecuta una consulta SQL SELECT y retorna los resultados.

    Args:
        conn: Conexión activa a la base de datos
        sql_statement: Statement SQL SELECT con placeholders '?'
        params: Parámetros para el statement SQL

    Returns:
        Lista de Row objects (accesibles como diccionarios)

    Raises:
        sqlite3.Error: Si ocurre un error durante la ejecución

    Example:
        >>> with DatabaseConnection('bd/strava.sqlite') as conn:
        ...     results = fetch(
        ...         conn,
        ...         "SELECT * FROM activities WHERE distance > ?",
        ...         (5000,)
        ...     )
        ...     for row in results:
        ...         print(row['name'], row['distance'])
    """
    cur = conn.cursor()

    try:
        if params:
            cur.execute(sql_statement, params)
        else:
            cur.execute(sql_statement)

        results = cur.fetchall()
        logger.debug(f"Query ejecutado: {len(results)} filas obtenidas")

        return results

    except sqlite3.Error as e:
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
    conn: sqlite3.Connection,
    sql_statement: str,
    params: Optional[Union[Tuple, List]] = None
) -> Optional[sqlite3.Row]:
    """
    Ejecuta una consulta SQL y retorna solo la primera fila.

    Args:
        conn: Conexión activa a la base de datos
        sql_statement: Statement SQL SELECT
        params: Parámetros para el statement

    Returns:
        Primera fila del resultado o None si no hay resultados

    Example:
        >>> with DatabaseConnection('bd/strava.sqlite') as conn:
        ...     activity = fetch_one(
        ...         conn,
        ...         "SELECT * FROM activities WHERE id_activity = ?",
        ...         (12345,)
        ...     )
        ...     if activity:
        ...         print(activity['name'])
    """
    cur = conn.cursor()

    try:
        if params:
            cur.execute(sql_statement, params)
        else:
            cur.execute(sql_statement)

        result = cur.fetchone()
        return result

    except sqlite3.Error as e:
        logger.error(f"Error en fetch_one: {e}")
        raise
    finally:
        cur.close()


def insert(
    conn: sqlite3.Connection,
    table_name: str,
    record: Dict[str, Any],
    commit: bool = True
) -> int:
    """
    Inserta un registro en una tabla de forma segura.

    Args:
        conn: Conexión activa a la base de datos
        table_name: Nombre de la tabla
        record: Diccionario con columna: valor
        commit: Si True, hace commit automáticamente

    Returns:
        ID del registro insertado (lastrowid)

    Example:
        >>> with DatabaseConnection('bd/strava.sqlite') as conn:
        ...     record_id = insert(
        ...         conn,
        ...         'activities',
        ...         {'name': 'Running', 'distance': 5000}
        ...     )
    """
    columns = ','.join(record.keys())
    placeholders = ','.join(['?' for _ in record.keys()])
    statement = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
    params = tuple(record.values())

    cur = execute(conn, statement, params, commit=commit)
    row_id = cur.lastrowid
    cur.close()

    logger.debug(f"Registro insertado en {table_name}, ID: {row_id}")
    return row_id


def insert_many(
    conn: sqlite3.Connection,
    table_name: str,
    records: List[Dict[str, Any]]
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
        >>> with DatabaseConnection('bd/strava.sqlite') as conn:
        ...     count = insert_many(conn, 'activities', records)
    """
    if not records:
        return 0

    # Usar las claves del primer registro para todas las inserciones
    columns = ','.join(records[0].keys())
    placeholders = ','.join(['?' for _ in records[0].keys()])
    statement = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

    # Convertir cada dict a tupla de valores
    params_list = [tuple(record.values()) for record in records]

    rows_affected = execute_many(conn, statement, params_list)
    logger.info(f"{rows_affected} registros insertados en {table_name}")

    return rows_affected


def update(
    conn: sqlite3.Connection,
    table_name: str,
    updates: Dict[str, Any],
    where_clause: str,
    where_params: Optional[Tuple] = None
) -> int:
    """
    Actualiza registros en una tabla.

    Args:
        conn: Conexión activa a la base de datos
        table_name: Nombre de la tabla
        updates: Diccionario con columna: nuevo_valor
        where_clause: Cláusula WHERE (ej: "id = ?")
        where_params: Parámetros para la cláusula WHERE

    Returns:
        Número de filas actualizadas

    Example:
        >>> with DatabaseConnection('bd/strava.sqlite') as conn:
        ...     rows = update(
        ...         conn,
        ...         'activities',
        ...         {'kudos_count': 10},
        ...         "id_activity = ?",
        ...         (12345,)
        ...     )
    """
    set_clause = ','.join([f"{col} = ?" for col in updates.keys()])
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

    Args:
        table_name: Nombre de la tabla donde insertar los datos
        record: Diccionario con los datos a insertar. Las claves son los
                nombres de las columnas y los valores son los datos

    Returns:
        Una tupla de dos elementos:
            - str: Statement SQL INSERT con placeholders '?'
            - tuple: Tupla con los valores a insertar

    Example:
        >>> record = {'name': 'Running', 'distance': 5000, 'date': '2025-11-30'}
        >>> stmt, params = insert_statement('activities', record)
        >>> print(stmt)
        INSERT INTO activities (name,distance,date) VALUES (?,?,?)
        >>> print(params)
        ('Running', 5000, '2025-11-30')
        >>> commit(conn, stmt, params)
    """
    columns = ','.join(record.keys())
    placeholders = ','.join(['?' for _ in record.keys()])
    statement = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
    params = tuple(record.values())

    return statement, params


def create_table(
    conn: sqlite3.Connection,
    table_name: str,
    create_sql: str
) -> None:
    """
    Crea una tabla en la base de datos si no existe.

    Args:
        conn: Conexión activa a la base de datos
        table_name: Nombre de la tabla a crear
        create_sql: Statement SQL CREATE TABLE completo

    Raises:
        sqlite3.Error: Si ocurre un error durante la creación

    Example:
        >>> sql = '''CREATE TABLE IF NOT EXISTS activities (
        ...     id_activity INTEGER PRIMARY KEY,
        ...     name TEXT NOT NULL
        ... )'''
        >>> with DatabaseConnection('bd/strava.sqlite') as conn:
        ...     create_table(conn, 'activities', sql)
    """
    try:
        execute(conn, create_sql, commit=False)
        logger.info(f"Tabla '{table_name}' creada/verificada exitosamente")
    except sqlite3.Error as e:
        logger.error(f"Error al crear tabla '{table_name}': {e}")
        raise


def commit(
    conn: sqlite3.Connection,
    sql_statement: Union[str, Tuple[str, Tuple]],
    params: Optional[Tuple] = None
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
        sqlite3.Error: Si ocurre un error durante la ejecución del statement

    Example:
        >>> conn = sql_connection('bd/strava.sqlite')
        >>> # Opción 1: statement y params separados
        >>> commit(conn, "INSERT INTO activities (name) VALUES (?)", ("Running",))
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
