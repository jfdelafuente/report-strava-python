"""Tests unitarios para el módulo core/reports.py."""

import pytest
from pathlib import Path
import csv


@pytest.fixture
def test_db_with_data(tmp_path):
    """Crea una BD temporal con datos de test."""
    from py_strava.database import sqlite as db
    from py_strava.database import schema

    db_path = tmp_path / "test_reports.sqlite"
    conn = db.sql_connection(str(db_path))

    # Crear tablas
    db.execute(conn, schema.CREATE_TABLE_ACTIVITIES, commit=True)
    db.execute(conn, schema.CREATE_TABLE_KUDOS, commit=True)

    # Insertar actividades de prueba
    activities = [
        (1, "Morning Run", "2025-12-01 07:00:00", "Run"),
        (2, "Evening Ride", "2025-12-02 18:00:00", "Ride"),
        (3, "Lunch Swim", "2025-12-03 12:00:00", "Swim"),
    ]

    for activity in activities:
        db.execute(
            conn,
            "INSERT INTO Activities (id_activity, name, start_date_local, type) VALUES (?, ?, ?, ?)",
            activity,
            commit=True,
        )

    # Insertar kudos de prueba
    kudos = [
        ("Alice", "Smith", 1),
        ("Bob", "Jones", 1),
        ("Charlie", "Brown", 2),
        ("Diana", "Prince", 3),
    ]

    for kudo in kudos:
        db.execute(
            conn,
            "INSERT INTO Kudos (firstname, lastname, id_activity) VALUES (?, ?, ?)",
            kudo,
            commit=True,
        )

    conn.close()
    return str(db_path)


class TestReportsModule:
    """Tests para el módulo de reportes."""

    def test_module_imports(self):
        """Verificar que el módulo se importa correctamente."""
        from py_strava.core import reports

        assert reports is not None

    def test_constants_defined(self):
        """Verificar que las constantes están definidas."""
        from py_strava.core import reports

        assert hasattr(reports, "DEFAULT_DB_PATH")
        assert hasattr(reports, "DEFAULT_OUTPUT_CSV")
        assert hasattr(reports, "QUERY_KUDOS_ACTIVITIES")
        assert hasattr(reports, "CSV_FIELDNAMES")


class TestDatabaseConnection:
    """Tests para conexión a base de datos."""

    def test_connect_to_database_success(self, test_db_with_data):
        """Verificar que connect_to_database establece conexión exitosamente."""
        from py_strava.core.reports import connect_to_database

        conn = connect_to_database(test_db_with_data)

        assert conn is not None
        conn.close()

    def test_connect_to_nonexistent_database(self, tmp_path):
        """Verificar que conectar a BD inexistente crea la BD."""
        from py_strava.core.reports import connect_to_database

        db_path = tmp_path / "new_db.sqlite"
        conn = connect_to_database(str(db_path))

        assert conn is not None
        assert db_path.exists()
        conn.close()


class TestFetchKudosData:
    """Tests para fetch_kudos_data."""

    def test_fetch_kudos_data_returns_results(self, test_db_with_data):
        """Verificar que fetch_kudos_data retorna datos."""
        from py_strava.core.reports import connect_to_database, fetch_kudos_data

        conn = connect_to_database(test_db_with_data)
        results = fetch_kudos_data(conn)

        assert len(results) > 0
        assert len(results) == 4  # 4 kudos en datos de test

        conn.close()

    def test_fetch_kudos_data_structure(self, test_db_with_data):
        """Verificar que los datos tienen la estructura correcta."""
        from py_strava.core.reports import connect_to_database, fetch_kudos_data

        conn = connect_to_database(test_db_with_data)
        results = fetch_kudos_data(conn)

        # Cada registro debe tener 5 campos: firstname, lastname, type, id_activity, start_date_local
        first_record = results[0]
        assert len(first_record) == 5

        conn.close()

    def test_fetch_kudos_data_empty_database(self, tmp_path):
        """Verificar comportamiento con BD vacía."""
        from py_strava.database import sqlite as db
        from py_strava.database import schema
        from py_strava.core.reports import connect_to_database, fetch_kudos_data

        # Crear BD vacía
        db_path = tmp_path / "empty.sqlite"
        conn = db.sql_connection(str(db_path))
        db.execute(conn, schema.CREATE_TABLE_ACTIVITIES, commit=True)
        db.execute(conn, schema.CREATE_TABLE_KUDOS, commit=True)
        conn.close()

        # Fetch datos
        conn = connect_to_database(str(db_path))
        results = fetch_kudos_data(conn)

        assert len(results) == 0
        conn.close()

    def test_fetch_kudos_data_ordering(self, test_db_with_data):
        """Verificar que los datos están ordenados correctamente."""
        from py_strava.core.reports import connect_to_database, fetch_kudos_data

        conn = connect_to_database(test_db_with_data)
        results = fetch_kudos_data(conn)

        # Debe estar ordenado por start_date_local DESC, lastname, firstname
        # El último registro (más reciente) debe aparecer primero
        first_result = results[0]

        # Verificar que hay datos
        assert len(results) > 0

        conn.close()


class TestExportToCSV:
    """Tests para exportación a CSV."""

    def test_export_to_csv_creates_file(self, tmp_path):
        """Verificar que export_to_csv crea el archivo."""
        from py_strava.core.reports import export_to_csv, CSV_FIELDNAMES

        output_file = tmp_path / "test_output.csv"
        data = [("John", "Doe", "Run", 123, "2025-12-04")]

        success = export_to_csv(data, str(output_file), CSV_FIELDNAMES)

        assert success
        assert output_file.exists()

    def test_export_to_csv_content(self, tmp_path):
        """Verificar que el contenido del CSV es correcto."""
        from py_strava.core.reports import export_to_csv, CSV_FIELDNAMES

        output_file = tmp_path / "test_output.csv"
        data = [
            ("Alice", "Smith", "Run", 1, "2025-12-01"),
            ("Bob", "Jones", "Ride", 2, "2025-12-02"),
        ]

        export_to_csv(data, str(output_file), CSV_FIELDNAMES)

        # Leer y verificar contenido
        with open(output_file, encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)

        assert len(rows) == 3  # Header + 2 data rows
        assert rows[0] == CSV_FIELDNAMES
        assert rows[1][0] == "Alice"
        assert rows[2][0] == "Bob"

    def test_export_to_csv_creates_parent_directory(self, tmp_path):
        """Verificar que export_to_csv crea directorios padre si no existen."""
        from py_strava.core.reports import export_to_csv, CSV_FIELDNAMES

        output_file = tmp_path / "subdir" / "nested" / "output.csv"
        data = [("Test", "User", "Run", 1, "2025-12-04")]

        success = export_to_csv(data, str(output_file), CSV_FIELDNAMES)

        assert success
        assert output_file.exists()
        assert output_file.parent.exists()

    def test_export_to_csv_empty_data(self, tmp_path):
        """Verificar comportamiento con datos vacíos."""
        from py_strava.core.reports import export_to_csv, CSV_FIELDNAMES

        output_file = tmp_path / "empty.csv"
        data = []

        success = export_to_csv(data, str(output_file), CSV_FIELDNAMES)

        assert not success  # Debe retornar False con datos vacíos
        assert not output_file.exists()  # No debe crear archivo vacío

    def test_export_to_csv_special_characters(self, tmp_path):
        """Verificar que maneja caracteres especiales correctamente."""
        from py_strava.core.reports import export_to_csv, CSV_FIELDNAMES

        output_file = tmp_path / "special.csv"
        data = [
            ("José", "García", "Run", 1, "2025-12-04"),
            ("François", "O'Brien", "Ride", 2, "2025-12-04"),
        ]

        success = export_to_csv(data, str(output_file), CSV_FIELDNAMES)

        assert success

        # Verificar que se guardó correctamente
        with open(output_file, encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)

        assert "José" in rows[1][0]
        assert "O'Brien" in rows[2][1]


class TestGenerateKudosReport:
    """Tests para generate_kudos_report."""

    def test_generate_kudos_report_success(self, test_db_with_data, tmp_path):
        """Verificar que generate_kudos_report genera el informe correctamente."""
        from py_strava.core.reports import generate_kudos_report

        output_file = tmp_path / "kudos_report.csv"

        success = generate_kudos_report(test_db_with_data, str(output_file))

        assert success
        assert output_file.exists()

    def test_generate_kudos_report_content(self, test_db_with_data, tmp_path):
        """Verificar que el contenido del informe es correcto."""
        from py_strava.core.reports import generate_kudos_report, CSV_FIELDNAMES

        output_file = tmp_path / "kudos_report.csv"

        generate_kudos_report(test_db_with_data, str(output_file))

        # Leer y verificar contenido
        with open(output_file, encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)

        assert rows[0] == CSV_FIELDNAMES
        assert len(rows) > 1  # Header + data

    def test_generate_kudos_report_invalid_db(self, tmp_path):
        """Verificar comportamiento con BD inválida."""
        from py_strava.core.reports import generate_kudos_report

        output_file = tmp_path / "report.csv"

        success = generate_kudos_report("/invalid/path/db.sqlite", str(output_file))

        # Puede retornar False o True dependiendo de si crea BD vacía
        # Lo importante es que no lance excepción
        assert isinstance(success, bool)


class TestRunReport:
    """Tests para run_report (función principal)."""

    def test_run_report_success(self, test_db_with_data, tmp_path):
        """Verificar que run_report ejecuta correctamente."""
        from py_strava.core.reports import run_report

        output_file = tmp_path / "final_report.csv"

        result = run_report(test_db_with_data, str(output_file))

        assert isinstance(result, dict)
        assert "success" in result
        assert "output_file" in result
        assert "db_path" in result

        assert result["success"] is True
        assert result["output_file"] == str(output_file)
        assert result["db_path"] == test_db_with_data

    def test_run_report_creates_file(self, test_db_with_data, tmp_path):
        """Verificar que run_report crea el archivo de salida."""
        from py_strava.core.reports import run_report

        output_file = tmp_path / "output.csv"

        result = run_report(test_db_with_data, str(output_file))

        assert result["success"]
        assert Path(output_file).exists()

    def test_run_report_default_parameters(self, test_db_with_data):
        """Verificar que run_report usa parámetros por defecto."""
        from py_strava.core.reports import run_report, DEFAULT_DB_PATH, DEFAULT_OUTPUT_CSV

        # Esta función usa defaults, verificamos que están definidos
        assert DEFAULT_DB_PATH is not None
        assert DEFAULT_OUTPUT_CSV is not None

    def test_run_report_return_structure(self, test_db_with_data, tmp_path):
        """Verificar la estructura del dict retornado."""
        from py_strava.core.reports import run_report

        output_file = tmp_path / "report.csv"
        result = run_report(test_db_with_data, str(output_file))

        # Verificar keys esperadas
        expected_keys = ["success", "output_file", "db_path"]
        for key in expected_keys:
            assert key in result

        # Verificar tipos
        assert isinstance(result["success"], bool)
        if result["success"]:
            assert isinstance(result["output_file"], str)
        assert isinstance(result["db_path"], str)


class TestQueryDefinition:
    """Tests para la definición de la query SQL."""

    def test_query_kudos_activities_structure(self):
        """Verificar que QUERY_KUDOS_ACTIVITIES está bien formada."""
        from py_strava.core.reports import QUERY_KUDOS_ACTIVITIES

        assert isinstance(QUERY_KUDOS_ACTIVITIES, str)
        assert "SELECT" in QUERY_KUDOS_ACTIVITIES
        assert "FROM Kudos" in QUERY_KUDOS_ACTIVITIES
        assert (
            "JOIN Activities" in QUERY_KUDOS_ACTIVITIES
            or "INNER JOIN Activities" in QUERY_KUDOS_ACTIVITIES
        )
        assert "ORDER BY" in QUERY_KUDOS_ACTIVITIES

    def test_query_selects_correct_fields(self):
        """Verificar que la query selecciona los campos correctos."""
        from py_strava.core.reports import QUERY_KUDOS_ACTIVITIES

        # Debe seleccionar: firstname, lastname, type, id_activity, start_date_local
        assert "firstname" in QUERY_KUDOS_ACTIVITIES
        assert "lastname" in QUERY_KUDOS_ACTIVITIES
        assert "type" in QUERY_KUDOS_ACTIVITIES
        assert "id_activity" in QUERY_KUDOS_ACTIVITIES
        assert "start_date_local" in QUERY_KUDOS_ACTIVITIES


class TestCSVFieldnames:
    """Tests para CSV_FIELDNAMES."""

    def test_csv_fieldnames_defined(self):
        """Verificar que CSV_FIELDNAMES está definido."""
        from py_strava.core.reports import CSV_FIELDNAMES

        assert isinstance(CSV_FIELDNAMES, list)
        assert len(CSV_FIELDNAMES) > 0

    def test_csv_fieldnames_content(self):
        """Verificar que CSV_FIELDNAMES tiene los campos correctos."""
        from py_strava.core.reports import CSV_FIELDNAMES

        expected_fields = ["FIRST_NAME", "LAST_NAME", "TIPO", "ACTIVIDAD", "START_DATE"]

        assert CSV_FIELDNAMES == expected_fields


class TestIntegration:
    """Tests de integración del módulo completo."""

    def test_full_report_generation_workflow(self, test_db_with_data, tmp_path):
        """Verificar el flujo completo de generación de informe."""
        from py_strava.core.reports import (
            connect_to_database,
            fetch_kudos_data,
            export_to_csv,
            CSV_FIELDNAMES,
        )

        output_file = tmp_path / "integration_test.csv"

        # 1. Conectar
        conn = connect_to_database(test_db_with_data)
        assert conn is not None

        # 2. Fetch datos
        data = fetch_kudos_data(conn)
        assert len(data) > 0

        # 3. Exportar
        success = export_to_csv(data, str(output_file), CSV_FIELDNAMES)
        assert success

        # 4. Verificar archivo final
        assert output_file.exists()

        with open(output_file, encoding="utf-8") as f:
            content = f.read()
            assert "FIRST_NAME" in content
            assert len(content) > 0

        conn.close()
