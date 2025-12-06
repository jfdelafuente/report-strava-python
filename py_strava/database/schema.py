"""Definiciones de esquemas SQL para la base de datos de Strava."""

CREATE_TABLE_ACTIVITIES = """
    CREATE TABLE IF NOT EXISTS Activities (
        id_activity INTEGER PRIMARY KEY,
        name TEXT,
        start_date_local TEXT,
        type TEXT,
        distance REAL,
        moving_time REAL,
        elapsed_time REAL,
        total_elevation_gain REAL,
        end_latlng TEXT,
        kudos_count INTEGER,
        external_id INTEGER
    )
"""

CREATE_TABLE_KUDOS = """
    CREATE TABLE IF NOT EXISTS Kudos (
        id_kudos INTEGER PRIMARY KEY AUTOINCREMENT,
        resource_state TEXT,
        firstname TEXT,
        lastname TEXT,
        id_activity INTEGER,
        FOREIGN KEY (id_activity) REFERENCES Activities(id_activity)
    )
"""

DROP_TABLE_ACTIVITIES = "DROP TABLE IF EXISTS Activities"
DROP_TABLE_KUDOS = "DROP TABLE IF EXISTS Kudos"

# Alias para compatibilidad con comandos CLI
SQL_CREATE_ACTIVITIES = CREATE_TABLE_ACTIVITIES
SQL_CREATE_KUDOS = CREATE_TABLE_KUDOS


def initialize_database(conn):
    """
    Inicializa la base de datos creando las tablas necesarias.

    Args:
        conn: Conexión a la base de datos
    """
    import strava.strava_db_sqlite as stravaBBDD

    stravaBBDD.commit(conn, CREATE_TABLE_ACTIVITIES)
    stravaBBDD.commit(conn, CREATE_TABLE_KUDOS)


def reset_database(conn):
    """
    Elimina y recrea todas las tablas de la base de datos.

    PRECAUCIÓN: Esta función elimina todos los datos existentes.

    Args:
        conn: Conexión a la base de datos
    """
    import strava.strava_db_sqlite as stravaBBDD

    stravaBBDD.commit(conn, DROP_TABLE_ACTIVITIES)
    stravaBBDD.commit(conn, DROP_TABLE_KUDOS)
    initialize_database(conn)
