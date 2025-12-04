"""Tests unitarios para el módulo database/sqlite.py."""

import sqlite3
from pathlib import Path

import pytest


@pytest.fixture
def test_db(tmp_path):
    """Crea una base de datos temporal para tests."""
    db_path = tmp_path / "test.sqlite"
    return str(db_path)


@pytest.fixture
def test_conn(test_db):
    """Crea una conexión a la BD de test."""
    from py_strava.database import sqlite as db

    conn = db.sql_connection(test_db)
    yield conn
    conn.close()


class TestDatabaseConnection:
    """Tests para conexión a base de datos."""

    def test_sql_connection_creates_db(self, test_db):
        """Verificar que sql_connection crea la BD si no existe."""
        from py_strava.database import sqlite as db

        conn = db.sql_connection(test_db)
        assert conn is not None
        assert Path(test_db).exists()
        conn.close()

    def test_sql_connection_foreign_keys_enabled(self, test_conn):
        """Verificar que las foreign keys están habilitadas."""
        cursor = test_conn.cursor()
        cursor.execute("PRAGMA foreign_keys")
        result = cursor.fetchone()
        assert result[0] == 1  # Foreign keys ON

    def test_sql_connection_row_factory(self, test_conn):
        """Verificar que row_factory está configurado."""
        assert test_conn.row_factory == sqlite3.Row

    def test_database_context_manager(self, test_db):
        """Verificar que DatabaseConnection funciona como context manager."""
        from py_strava.database.sqlite import DatabaseConnection

        with DatabaseConnection(test_db) as conn:
            assert conn is not None
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            assert result[0] == 1

    def test_database_context_manager_auto_commit(self, test_db):
        """Verificar que el context manager hace commit automáticamente."""
        from py_strava.database.sqlite import DatabaseConnection

        # Crear tabla y datos en un context
        with DatabaseConnection(test_db) as conn:
            conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
            conn.execute("INSERT INTO test (id, name) VALUES (1, 'test')")

        # Verificar que los datos persisten en otra conexión
        with DatabaseConnection(test_db) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM test")
            count = cursor.fetchone()[0]
            assert count == 1


class TestExecuteOperations:
    """Tests para operaciones execute."""

    def test_execute_simple_query(self, test_conn):
        """Verificar que execute funciona con queries simples."""
        from py_strava.database import sqlite as db

        cursor = db.execute(test_conn, "SELECT 1", commit=False)
        result = cursor.fetchone()
        assert result[0] == 1

    def test_execute_with_params(self, test_conn):
        """Verificar que execute funciona con parámetros."""
        from py_strava.database import sqlite as db

        db.execute(test_conn, "CREATE TABLE test (id INTEGER, value TEXT)", commit=True)
        db.execute(test_conn, "INSERT INTO test VALUES (?, ?)", (1, "hello"), commit=True)

        cursor = db.execute(test_conn, "SELECT value FROM test WHERE id = ?", (1,), commit=False)
        result = cursor.fetchone()
        assert result[0] == "hello"

    def test_execute_commit_behavior(self, test_conn):
        """Verificar que el commit funciona correctamente."""
        from py_strava.database import sqlite as db

        db.execute(test_conn, "CREATE TABLE test (id INTEGER)", commit=True)

        # Sin commit
        db.execute(test_conn, "INSERT INTO test VALUES (1)", commit=False)

        # Con commit
        db.execute(test_conn, "INSERT INTO test VALUES (2)", commit=True)

        cursor = db.execute(test_conn, "SELECT COUNT(*) FROM test", commit=False)
        assert cursor.fetchone()[0] == 2


class TestInsertOperations:
    """Tests para operaciones de inserción."""

    def test_insert_single_record(self, test_conn):
        """Verificar que insert inserta un registro correctamente."""
        from py_strava.database import sqlite as db

        db.execute(test_conn, "CREATE TABLE test (id INTEGER, name TEXT, age INTEGER)", commit=True)

        record = {"id": 1, "name": "Alice", "age": 30}
        row_id = db.insert(test_conn, "test", record)

        assert row_id > 0

        cursor = test_conn.execute("SELECT * FROM test WHERE id = 1")
        result = cursor.fetchone()
        assert result["name"] == "Alice"
        assert result["age"] == 30

    def test_insert_returns_lastrowid(self, test_conn):
        """Verificar que insert retorna el ID del registro insertado."""
        from py_strava.database import sqlite as db

        db.execute(
            test_conn,
            "CREATE TABLE test (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT)",
            commit=True,
        )

        row_id_1 = db.insert(test_conn, "test", {"name": "First"})
        row_id_2 = db.insert(test_conn, "test", {"name": "Second"})

        assert row_id_2 > row_id_1

    def test_insert_many_records(self, test_conn):
        """Verificar que insert_many inserta múltiples registros."""
        from py_strava.database import sqlite as db

        db.execute(test_conn, "CREATE TABLE test (id INTEGER, name TEXT)", commit=True)

        records = [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
            {"id": 3, "name": "Charlie"},
        ]

        count = db.insert_many(test_conn, "test", records)
        assert count == 3

        cursor = test_conn.execute("SELECT COUNT(*) FROM test")
        assert cursor.fetchone()[0] == 3

    def test_insert_many_empty_list(self, test_conn):
        """Verificar que insert_many con lista vacía retorna 0."""
        from py_strava.database import sqlite as db

        db.execute(test_conn, "CREATE TABLE test (id INTEGER)", commit=True)

        count = db.insert_many(test_conn, "test", [])
        assert count == 0


class TestFetchOperations:
    """Tests para operaciones de consulta."""

    def test_fetch_all_records(self, test_conn):
        """Verificar que fetch retorna todos los registros."""
        from py_strava.database import sqlite as db

        db.execute(test_conn, "CREATE TABLE test (id INTEGER, name TEXT)", commit=True)
        db.execute(test_conn, "INSERT INTO test VALUES (1, 'Alice'), (2, 'Bob')", commit=True)

        results = db.fetch(test_conn, "SELECT * FROM test ORDER BY id")

        assert len(results) == 2
        assert results[0]["name"] == "Alice"
        assert results[1]["name"] == "Bob"

    def test_fetch_with_params(self, test_conn):
        """Verificar que fetch funciona con parámetros."""
        from py_strava.database import sqlite as db

        db.execute(test_conn, "CREATE TABLE test (id INTEGER, value INTEGER)", commit=True)
        db.execute(test_conn, "INSERT INTO test VALUES (1, 100), (2, 200), (3, 150)", commit=True)

        results = db.fetch(test_conn, "SELECT * FROM test WHERE value > ?", (120,))

        assert len(results) == 2

    def test_fetch_one_single_result(self, test_conn):
        """Verificar que fetch_one retorna un solo registro."""
        from py_strava.database import sqlite as db

        db.execute(test_conn, "CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)", commit=True)
        db.execute(test_conn, "INSERT INTO test VALUES (1, 'Alice')", commit=True)

        result = db.fetch_one(test_conn, "SELECT * FROM test WHERE id = ?", (1,))

        assert result is not None
        assert result["name"] == "Alice"

    def test_fetch_one_no_result(self, test_conn):
        """Verificar que fetch_one retorna None si no hay resultados."""
        from py_strava.database import sqlite as db

        db.execute(test_conn, "CREATE TABLE test (id INTEGER)", commit=True)

        result = db.fetch_one(test_conn, "SELECT * FROM test WHERE id = 999")

        assert result is None


class TestUpdateOperations:
    """Tests para operaciones de actualización."""

    def test_update_single_field(self, test_conn):
        """Verificar que update actualiza campos correctamente."""
        from py_strava.database import sqlite as db

        db.execute(test_conn, "CREATE TABLE test (id INTEGER, name TEXT, age INTEGER)", commit=True)
        db.execute(test_conn, "INSERT INTO test VALUES (1, 'Alice', 30)", commit=True)

        rows = db.update(test_conn, "test", {"age": 31}, "id = ?", (1,))

        assert rows == 1

        result = db.fetch_one(test_conn, "SELECT age FROM test WHERE id = 1")
        assert result["age"] == 31

    def test_update_multiple_fields(self, test_conn):
        """Verificar que update puede actualizar múltiples campos."""
        from py_strava.database import sqlite as db

        db.execute(test_conn, "CREATE TABLE test (id INTEGER, name TEXT, age INTEGER)", commit=True)
        db.execute(test_conn, "INSERT INTO test VALUES (1, 'Alice', 30)", commit=True)

        db.update(test_conn, "test", {"name": "Alicia", "age": 35}, "id = ?", (1,))

        result = db.fetch_one(test_conn, "SELECT * FROM test WHERE id = 1")
        assert result["name"] == "Alicia"
        assert result["age"] == 35

    def test_update_returns_affected_rows(self, test_conn):
        """Verificar que update retorna el número de filas afectadas."""
        from py_strava.database import sqlite as db

        db.execute(test_conn, "CREATE TABLE test (id INTEGER, status TEXT)", commit=True)
        db.execute(
            test_conn,
            "INSERT INTO test VALUES (1, 'active'), (2, 'active'), (3, 'inactive')",
            commit=True,
        )

        rows = db.update(test_conn, "test", {"status": "archived"}, "status = ?", ("active",))

        assert rows == 2


class TestCreateTable:
    """Tests para creación de tablas."""

    def test_create_table_simple(self, test_conn):
        """Verificar que create_table crea tablas correctamente."""
        from py_strava.database import sqlite as db

        sql = """
            CREATE TABLE IF NOT EXISTS test (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            )
        """

        db.create_table(test_conn, "test", sql)

        # Verificar que la tabla existe
        cursor = test_conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='test'"
        )
        result = cursor.fetchone()
        assert result is not None
        assert result[0] == "test"

    def test_create_table_if_not_exists(self, test_conn):
        """Verificar que create_table no falla si la tabla ya existe."""
        from py_strava.database import sqlite as db

        sql = "CREATE TABLE IF NOT EXISTS test (id INTEGER)"

        # Crear dos veces, no debe fallar
        db.create_table(test_conn, "test", sql)
        db.create_table(test_conn, "test", sql)  # No debe lanzar excepción


class TestInsertStatement:
    """Tests para generación de statements INSERT."""

    def test_insert_statement_generation(self):
        """Verificar que insert_statement genera SQL correcto."""
        from py_strava.database import sqlite as db

        record = {"id": 1, "name": "Alice", "age": 30}
        stmt, params = db.insert_statement("users", record)

        assert "INSERT INTO users" in stmt
        assert "VALUES" in stmt
        assert stmt.count("?") == 3
        assert params == (1, "Alice", 30)

    def test_insert_statement_with_commit(self, test_conn):
        """Verificar que el statement generado funciona con commit."""
        from py_strava.database import sqlite as db

        db.execute(test_conn, "CREATE TABLE test (id INTEGER, name TEXT)", commit=True)

        record = {"id": 1, "name": "Test"}
        stmt, params = db.insert_statement("test", record)

        db.commit(test_conn, stmt, params)

        result = db.fetch_one(test_conn, "SELECT * FROM test WHERE id = 1")
        assert result["name"] == "Test"


class TestCommit:
    """Tests para función commit."""

    def test_commit_with_statement_and_params(self, test_conn):
        """Verificar que commit ejecuta statements correctamente."""
        from py_strava.database import sqlite as db

        db.execute(test_conn, "CREATE TABLE test (value TEXT)", commit=True)

        db.commit(test_conn, "INSERT INTO test VALUES (?)", ("hello",))

        result = db.fetch_one(test_conn, "SELECT value FROM test")
        assert result["value"] == "hello"

    def test_commit_with_tuple_format(self, test_conn):
        """Verificar que commit acepta tupla (stmt, params) de insert_statement."""
        from py_strava.database import sqlite as db

        db.execute(test_conn, "CREATE TABLE test (id INTEGER, name TEXT)", commit=True)

        record = {"id": 1, "name": "Test"}
        stmt_tuple = db.insert_statement("test", record)

        db.commit(test_conn, stmt_tuple)

        result = db.fetch_one(test_conn, "SELECT * FROM test")
        assert result["name"] == "Test"


class TestErrorHandling:
    """Tests para manejo de errores."""

    def test_execute_invalid_sql_raises_error(self, test_conn):
        """Verificar que SQL inválido lanza excepción."""
        from py_strava.database import sqlite as db

        with pytest.raises(sqlite3.Error):
            db.execute(test_conn, "INVALID SQL QUERY", commit=False)

    def test_insert_into_nonexistent_table_raises_error(self, test_conn):
        """Verificar que insertar en tabla inexistente lanza excepción."""
        from py_strava.database import sqlite as db

        with pytest.raises(sqlite3.Error):
            db.insert(test_conn, "nonexistent_table", {"id": 1})

    def test_fetch_invalid_table_raises_error(self, test_conn):
        """Verificar que consultar tabla inexistente lanza excepción."""
        from py_strava.database import sqlite as db

        with pytest.raises(sqlite3.Error):
            db.fetch(test_conn, "SELECT * FROM nonexistent_table")
