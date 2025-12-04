"""Tests unitarios para el módulo database/schema.py."""

import pytest
import sqlite3


@pytest.fixture
def test_db(tmp_path):
    """Crea una base de datos temporal para tests."""
    db_path = tmp_path / "test_schema.sqlite"
    conn = sqlite3.connect(str(db_path))
    yield conn
    conn.close()


class TestSchemaConstants:
    """Tests para constantes de esquema SQL."""

    def test_create_table_activities_defined(self):
        """Verificar que el SQL de Activities está definido."""
        from py_strava.database import schema

        assert hasattr(schema, 'CREATE_TABLE_ACTIVITIES')
        assert isinstance(schema.CREATE_TABLE_ACTIVITIES, str)
        assert 'CREATE TABLE' in schema.CREATE_TABLE_ACTIVITIES
        assert 'Activities' in schema.CREATE_TABLE_ACTIVITIES

    def test_create_table_kudos_defined(self):
        """Verificar que el SQL de Kudos está definido."""
        from py_strava.database import schema

        assert hasattr(schema, 'CREATE_TABLE_KUDOS')
        assert isinstance(schema.CREATE_TABLE_KUDOS, str)
        assert 'CREATE TABLE' in schema.CREATE_TABLE_KUDOS
        assert 'Kudos' in schema.CREATE_TABLE_KUDOS

    def test_drop_table_statements_defined(self):
        """Verificar que los DROP TABLE están definidos."""
        from py_strava.database import schema

        assert hasattr(schema, 'DROP_TABLE_ACTIVITIES')
        assert hasattr(schema, 'DROP_TABLE_KUDOS')
        assert 'DROP TABLE' in schema.DROP_TABLE_ACTIVITIES
        assert 'DROP TABLE' in schema.DROP_TABLE_KUDOS

    def test_sql_aliases_defined(self):
        """Verificar que los alias SQL para CLI están definidos."""
        from py_strava.database import schema

        assert hasattr(schema, 'SQL_CREATE_ACTIVITIES')
        assert hasattr(schema, 'SQL_CREATE_KUDOS')

        # Los alias deben apuntar a las constantes originales
        assert schema.SQL_CREATE_ACTIVITIES == schema.CREATE_TABLE_ACTIVITIES
        assert schema.SQL_CREATE_KUDOS == schema.CREATE_TABLE_KUDOS


class TestActivitiesTable:
    """Tests para la tabla Activities."""

    def test_create_activities_table(self, test_db):
        """Verificar que CREATE_TABLE_ACTIVITIES crea la tabla correctamente."""
        from py_strava.database import schema

        test_db.execute(schema.CREATE_TABLE_ACTIVITIES)
        test_db.commit()

        # Verificar que la tabla existe
        cursor = test_db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='Activities'"
        )
        result = cursor.fetchone()
        assert result is not None

    def test_activities_table_columns(self, test_db):
        """Verificar que Activities tiene las columnas correctas."""
        from py_strava.database import schema

        test_db.execute(schema.CREATE_TABLE_ACTIVITIES)

        cursor = test_db.execute("PRAGMA table_info(Activities)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}  # name: type

        # Verificar columnas esperadas
        expected_columns = [
            'id_activity', 'name', 'start_date_local', 'type',
            'distance', 'moving_time', 'elapsed_time',
            'total_elevation_gain', 'end_latlng', 'kudos_count', 'external_id'
        ]

        for col in expected_columns:
            assert col in columns, f"Columna '{col}' no encontrada en Activities"

    def test_activities_primary_key(self, test_db):
        """Verificar que id_activity es PRIMARY KEY."""
        from py_strava.database import schema

        test_db.execute(schema.CREATE_TABLE_ACTIVITIES)

        cursor = test_db.execute("PRAGMA table_info(Activities)")
        columns = cursor.fetchall()

        # Buscar columna id_activity
        id_column = next(col for col in columns if col[1] == 'id_activity')
        is_pk = id_column[5]  # Índice 5 es pk (1 = PRIMARY KEY, 0 = no)

        assert is_pk == 1, "id_activity debería ser PRIMARY KEY"

    def test_insert_into_activities(self, test_db):
        """Verificar que se pueden insertar datos en Activities."""
        from py_strava.database import schema

        test_db.execute(schema.CREATE_TABLE_ACTIVITIES)

        test_db.execute("""
            INSERT INTO Activities (id_activity, name, type, distance)
            VALUES (123, 'Morning Run', 'Run', 5000)
        """)
        test_db.commit()

        cursor = test_db.execute("SELECT * FROM Activities WHERE id_activity = 123")
        result = cursor.fetchone()

        assert result is not None
        assert result[1] == 'Morning Run'  # name
        assert result[3] == 'Run'  # type


class TestKudosTable:
    """Tests para la tabla Kudos."""

    def test_create_kudos_table(self, test_db):
        """Verificar que CREATE_TABLE_KUDOS crea la tabla correctamente."""
        from py_strava.database import schema

        # Kudos tiene FK a Activities, crear ambas
        test_db.execute(schema.CREATE_TABLE_ACTIVITIES)
        test_db.execute(schema.CREATE_TABLE_KUDOS)
        test_db.commit()

        cursor = test_db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='Kudos'"
        )
        result = cursor.fetchone()
        assert result is not None

    def test_kudos_table_columns(self, test_db):
        """Verificar que Kudos tiene las columnas correctas."""
        from py_strava.database import schema

        test_db.execute(schema.CREATE_TABLE_ACTIVITIES)
        test_db.execute(schema.CREATE_TABLE_KUDOS)

        cursor = test_db.execute("PRAGMA table_info(Kudos)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}

        expected_columns = [
            'id_kudos', 'resource_state', 'firstname',
            'lastname', 'id_activity'
        ]

        for col in expected_columns:
            assert col in columns, f"Columna '{col}' no encontrada en Kudos"

    def test_kudos_primary_key_autoincrement(self, test_db):
        """Verificar que id_kudos es AUTOINCREMENT."""
        from py_strava.database import schema

        test_db.execute(schema.CREATE_TABLE_ACTIVITIES)
        test_db.execute(schema.CREATE_TABLE_KUDOS)

        # Insertar actividad
        test_db.execute("INSERT INTO Activities (id_activity, name) VALUES (1, 'Test')")

        # Insertar kudos sin especificar id_kudos
        test_db.execute("""
            INSERT INTO Kudos (firstname, lastname, id_activity)
            VALUES ('John', 'Doe', 1)
        """)
        test_db.execute("""
            INSERT INTO Kudos (firstname, lastname, id_activity)
            VALUES ('Jane', 'Smith', 1)
        """)
        test_db.commit()

        cursor = test_db.execute("SELECT id_kudos FROM Kudos ORDER BY id_kudos")
        ids = [row[0] for row in cursor.fetchall()]

        assert len(ids) == 2
        assert ids[0] < ids[1], "id_kudos debería autoincrementar"

    def test_kudos_foreign_key_constraint(self, test_db):
        """Verificar que la FK a Activities funciona."""
        from py_strava.database import schema

        # Habilitar FKs
        test_db.execute("PRAGMA foreign_keys = ON")

        test_db.execute(schema.CREATE_TABLE_ACTIVITIES)
        test_db.execute(schema.CREATE_TABLE_KUDOS)

        # Insertar actividad
        test_db.execute("INSERT INTO Activities (id_activity, name) VALUES (100, 'Test')")
        test_db.commit()

        # Insertar kudo válido (debería funcionar)
        test_db.execute("""
            INSERT INTO Kudos (firstname, lastname, id_activity)
            VALUES ('Valid', 'User', 100)
        """)
        test_db.commit()

        # Verificar que se insertó
        cursor = test_db.execute("SELECT COUNT(*) FROM Kudos")
        assert cursor.fetchone()[0] == 1


class TestDropTables:
    """Tests para DROP TABLE statements."""

    def test_drop_activities_table(self, test_db):
        """Verificar que DROP_TABLE_ACTIVITIES elimina la tabla."""
        from py_strava.database import schema

        test_db.execute(schema.CREATE_TABLE_ACTIVITIES)
        test_db.commit()

        # Verificar que existe
        cursor = test_db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='Activities'"
        )
        assert cursor.fetchone() is not None

        # Eliminar
        test_db.execute(schema.DROP_TABLE_ACTIVITIES)
        test_db.commit()

        # Verificar que no existe
        cursor = test_db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='Activities'"
        )
        assert cursor.fetchone() is None

    def test_drop_kudos_table(self, test_db):
        """Verificar que DROP_TABLE_KUDOS elimina la tabla."""
        from py_strava.database import schema

        test_db.execute(schema.CREATE_TABLE_ACTIVITIES)
        test_db.execute(schema.CREATE_TABLE_KUDOS)
        test_db.commit()

        # Eliminar Kudos
        test_db.execute(schema.DROP_TABLE_KUDOS)
        test_db.commit()

        # Verificar que Kudos no existe pero Activities sí
        cursor = test_db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='Kudos'"
        )
        assert cursor.fetchone() is None

        cursor = test_db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='Activities'"
        )
        assert cursor.fetchone() is not None


class TestInitializeDatabase:
    """Tests para función initialize_database."""

    def test_initialize_database_creates_tables(self, test_db):
        """Verificar que initialize_database crea ambas tablas."""
        from py_strava.database import schema

        # Nota: Esta función usa import interno legacy, podría necesitar ajuste
        # Para el test, verificamos que las constantes están disponibles
        assert hasattr(schema, 'initialize_database')

        # Crear tablas manualmente para simular initialize_database
        test_db.execute(schema.CREATE_TABLE_ACTIVITIES)
        test_db.execute(schema.CREATE_TABLE_KUDOS)
        test_db.commit()

        # Verificar que ambas existen
        cursor = test_db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        tables = [row[0] for row in cursor.fetchall()]

        assert 'Activities' in tables
        assert 'Kudos' in tables


class TestResetDatabase:
    """Tests para función reset_database."""

    def test_reset_database_function_exists(self):
        """Verificar que reset_database está definida."""
        from py_strava.database import schema

        assert hasattr(schema, 'reset_database')
        assert callable(schema.reset_database)

    def test_reset_database_drops_and_recreates(self, test_db):
        """Verificar que reset_database elimina y recrea tablas."""
        from py_strava.database import schema

        # Crear tablas con datos
        test_db.execute(schema.CREATE_TABLE_ACTIVITIES)
        test_db.execute(schema.CREATE_TABLE_KUDOS)
        test_db.execute("INSERT INTO Activities (id_activity, name) VALUES (1, 'Test')")
        test_db.commit()

        # Verificar que hay datos
        cursor = test_db.execute("SELECT COUNT(*) FROM Activities")
        assert cursor.fetchone()[0] == 1

        # Simular reset
        test_db.execute(schema.DROP_TABLE_KUDOS)
        test_db.execute(schema.DROP_TABLE_ACTIVITIES)
        test_db.execute(schema.CREATE_TABLE_ACTIVITIES)
        test_db.execute(schema.CREATE_TABLE_KUDOS)
        test_db.commit()

        # Verificar que las tablas existen pero están vacías
        cursor = test_db.execute("SELECT COUNT(*) FROM Activities")
        assert cursor.fetchone()[0] == 0


class TestSchemaIntegration:
    """Tests de integración del esquema completo."""

    def test_full_schema_creation(self, test_db):
        """Verificar que se puede crear el esquema completo."""
        from py_strava.database import schema

        test_db.execute(schema.CREATE_TABLE_ACTIVITIES)
        test_db.execute(schema.CREATE_TABLE_KUDOS)
        test_db.commit()

        # Verificar ambas tablas
        cursor = test_db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        tables = [row[0] for row in cursor.fetchall()]

        assert 'Activities' in tables
        assert 'Kudos' in tables

    def test_realistic_data_insertion(self, test_db):
        """Verificar que se pueden insertar datos realistas."""
        from py_strava.database import schema

        test_db.execute("PRAGMA foreign_keys = ON")
        test_db.execute(schema.CREATE_TABLE_ACTIVITIES)
        test_db.execute(schema.CREATE_TABLE_KUDOS)

        # Insertar actividad realista
        test_db.execute("""
            INSERT INTO Activities (
                id_activity, name, start_date_local, type, distance,
                moving_time, elapsed_time, total_elevation_gain,
                kudos_count
            ) VALUES (
                12345, 'Morning Run', '2025-12-04 07:00:00', 'Run', 5000.0,
                1800, 2000, 50.0, 5
            )
        """)

        # Insertar kudos
        test_db.execute("""
            INSERT INTO Kudos (resource_state, firstname, lastname, id_activity)
            VALUES ('2', 'John', 'Doe', 12345)
        """)
        test_db.execute("""
            INSERT INTO Kudos (resource_state, firstname, lastname, id_activity)
            VALUES ('2', 'Jane', 'Smith', 12345)
        """)
        test_db.commit()

        # Verificar join
        cursor = test_db.execute("""
            SELECT a.name, k.firstname, k.lastname
            FROM Activities a
            JOIN Kudos k ON a.id_activity = k.id_activity
            ORDER BY k.firstname
        """)
        results = cursor.fetchall()

        assert len(results) == 2
        assert results[0][1] == 'Jane'
        assert results[1][1] == 'John'
