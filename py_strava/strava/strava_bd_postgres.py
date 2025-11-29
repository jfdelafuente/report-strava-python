import psycopg2
import json
import os
from pathlib import Path


def sql_connection():
    """Establece conexión con PostgreSQL usando credenciales del archivo JSON o variables de entorno."""
    credentials_file = Path('./bd/postgres_credentials.json')

    # Intentar leer desde archivo JSON primero
    if credentials_file.exists():
        with open(credentials_file, 'r') as f:
            postgres_credentials = json.load(f)
            host = postgres_credentials['server']
            database = postgres_credentials['database']
            user = postgres_credentials['username']
            password = postgres_credentials['password']
            port = postgres_credentials['port']
    else:
        # Usar variables de entorno como respaldo
        from py_strava.config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
        host = DB_HOST
        database = DB_NAME
        user = DB_USER
        password = DB_PASSWORD
        port = DB_PORT

    try:
        conn = psycopg2.connect(host=host, database=database, port=port,
                                user=user, password=password)
        return conn
    except Exception as e:
        print(f"Error al conectar a PostgreSQL: {e}")
        raise

def commit(conn, sql_statement):
    cur = conn.cursor()

    # Asegurar que el directorio data existe
    log_dir = Path('data')
    log_dir.mkdir(exist_ok=True)

    log_file = log_dir / 'strava_activities_bd.log'

    with open(log_file, "a") as file:
        try:
            cur.execute(sql_statement)
        except Exception as e:
            error_msg = f"Error: {sql_statement}\nExcepción: {e}\n"
            print(error_msg)
            file.write(error_msg)

    conn.commit()
    cur.close()
    return print("statement committed")

def fetch(conn, sql_statement):
    cur = conn.cursor()
    cur.execute(sql_statement)
    output = cur.fetchall()
    cur.close()
    return output

def insert_statement(table_name, record):
    columns = ','.join(list(record.keys()))
    values  = str(tuple(record.values()))
    statement = """INSERT INTO {} ({}) VALUES {};""".format(table_name, columns, values)
    #print(statement)
    return statement