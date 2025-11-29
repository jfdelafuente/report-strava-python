import sqlite3
from sqlite3 import Error
from pathlib import Path


def sql_connection(bbdd):
    try:
        conn = sqlite3.connect(bbdd)
        return conn
    except Error:
        print(Error)

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
            error_msg = f"Error: {sql_statement}\nExcepcion: {e}\n"
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



