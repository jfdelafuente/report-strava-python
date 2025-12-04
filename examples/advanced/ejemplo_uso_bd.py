#!/usr/bin/env python
"""
Ejemplo de uso de la base de datos SQLite de Strava.

Este script muestra cómo:
- Insertar actividades y kudos
- Consultar datos
- Actualizar registros
"""

import sys
from pathlib import Path

# Añadir el directorio raíz del proyecto al path de Python
# Esto permite importar py_strava desde cualquier ubicación
# Nota: Estamos en examples/advanced/, así que subimos dos niveles para llegar a la raíz
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Usar nuevos imports reorganizados
from py_strava.database import sqlite as db


def ejemplo_insertar_actividad():
    """Ejemplo: Insertar una actividad en la base de datos."""
    print("\n" + "=" * 60)
    print("EJEMPLO 1: Insertar una actividad")
    print("=" * 60)

    db_path = project_root / "bd" / "strava.sqlite"

    # Datos de ejemplo de una actividad
    actividad = {
        "id_activity": 12345678901,
        "name": "Morning Run",
        "start_date_local": "2025-12-03T07:30:00Z",
        "type": "Run",
        "distance": 5420.5,
        "moving_time": 1850,
        "elapsed_time": 1920,
        "total_elevation_gain": 45.2,
        "end_latlng": "[40.4168, -3.7038]",
        "kudos_count": 5,
        "external_id": 98765,
    }

    with db.DatabaseConnection(str(db_path)) as conn:
        # Insertar la actividad
        activity_id = db.insert(conn, "Activities", actividad)
        print(f"[OK] Actividad insertada con ID: {activity_id}")
        print(f"  Nombre: {actividad['name']}")
        print(f"  Distancia: {actividad['distance']/1000:.2f} km")
        print(f"  Tiempo: {actividad['moving_time']//60} min {actividad['moving_time']%60} seg")


def ejemplo_insertar_kudos():
    """Ejemplo: Insertar kudos para una actividad."""
    print("\n" + "=" * 60)
    print("EJEMPLO 2: Insertar kudos")
    print("=" * 60)

    db_path = project_root / "bd" / "strava.sqlite"

    # Lista de kudos de ejemplo
    kudos_list = [
        {
            "resource_state": "2",
            "firstname": "Juan",
            "lastname": "Pérez",
            "id_activity": 12345678901,
        },
        {
            "resource_state": "2",
            "firstname": "María",
            "lastname": "García",
            "id_activity": 12345678901,
        },
        {
            "resource_state": "2",
            "firstname": "Carlos",
            "lastname": "López",
            "id_activity": 12345678901,
        },
    ]

    with db.DatabaseConnection(str(db_path)) as conn:
        # Insertar múltiples kudos
        count = db.insert_many(conn, "Kudos", kudos_list)
        print(f"[OK] {count} kudos insertados")

        for kudo in kudos_list:
            print(f"  - {kudo['firstname']} {kudo['lastname']}")


def ejemplo_consultar_actividades():
    """Ejemplo: Consultar actividades."""
    print("\n" + "=" * 60)
    print("EJEMPLO 3: Consultar actividades")
    print("=" * 60)

    db_path = project_root / "bd" / "strava.sqlite"

    with db.DatabaseConnection(str(db_path)) as conn:
        # Consultar todas las actividades
        actividades = db.fetch(conn, "SELECT * FROM Activities")

        print(f"Total de actividades: {len(actividades)}")
        print()

        for actividad in actividades:
            print(f"ID: {actividad['id_activity']}")
            print(f"  Nombre: {actividad['name']}")
            print(f"  Tipo: {actividad['type']}")
            print(f"  Distancia: {actividad['distance']/1000:.2f} km")
            print(f"  Fecha: {actividad['start_date_local']}")
            print(f"  Kudos: {actividad['kudos_count']}")
            print()


def ejemplo_consultar_con_join():
    """Ejemplo: Consultar actividades con sus kudos (JOIN)."""
    print("\n" + "=" * 60)
    print("EJEMPLO 4: Consultar actividades con kudos (JOIN)")
    print("=" * 60)

    db_path = project_root / "bd" / "strava.sqlite"

    with db.DatabaseConnection(str(db_path)) as conn:
        query = """
            SELECT
                a.name AS activity_name,
                a.type AS activity_type,
                a.distance,
                k.firstname,
                k.lastname
            FROM Activities a
            LEFT JOIN Kudos k ON a.id_activity = k.id_activity
            ORDER BY a.name, k.firstname
        """

        resultados = db.fetch(conn, query)

        print(f"Total de resultados: {len(resultados)}")
        print()

        current_activity = None
        for resultado in resultados:
            if resultado["activity_name"] != current_activity:
                current_activity = resultado["activity_name"]
                print(f"\n{resultado['activity_name']} ({resultado['activity_type']})")
                print(f"  Distancia: {resultado['distance']/1000:.2f} km")
                print("  Kudos:")

            if resultado["firstname"]:
                print(f"    - {resultado['firstname']} {resultado['lastname']}")


def ejemplo_actualizar_kudos():
    """Ejemplo: Actualizar el contador de kudos."""
    print("\n" + "=" * 60)
    print("EJEMPLO 5: Actualizar contador de kudos")
    print("=" * 60)

    db_path = project_root / "bd" / "strava.sqlite"

    with db.DatabaseConnection(str(db_path)) as conn:
        # Contar kudos reales
        resultado = db.fetch_one(
            conn, "SELECT COUNT(*) as count FROM Kudos WHERE id_activity = ?", (12345678901,)
        )

        kudos_reales = resultado["count"]
        print(f"Kudos reales en la BD: {kudos_reales}")

        # Actualizar el contador
        rows = db.update(
            conn, "Activities", {"kudos_count": kudos_reales}, "id_activity = ?", (12345678901,)
        )

        print(f"[OK] {rows} actividad actualizada")


def ejemplo_estadisticas():
    """Ejemplo: Obtener estadísticas."""
    print("\n" + "=" * 60)
    print("EJEMPLO 6: Estadísticas generales")
    print("=" * 60)

    db_path = project_root / "bd" / "strava.sqlite"

    with db.DatabaseConnection(str(db_path)) as conn:
        # Estadísticas de actividades
        stats = db.fetch_one(
            conn,
            """
            SELECT
                COUNT(*) as total_actividades,
                SUM(distance) as distancia_total,
                AVG(distance) as distancia_promedio,
                SUM(moving_time) as tiempo_total,
                SUM(total_elevation_gain) as desnivel_total
            FROM Activities
            """,
        )

        if stats["total_actividades"] > 0:
            print(f"Total actividades: {stats['total_actividades']}")
            print(f"Distancia total: {stats['distancia_total']/1000:.2f} km")
            print(f"Distancia promedio: {stats['distancia_promedio']/1000:.2f} km")
            print(
                f"Tiempo total: {stats['tiempo_total']//3600:.0f}h {(stats['tiempo_total']%3600)//60:.0f}min"
            )
            print(f"Desnivel total: {stats['desnivel_total']:.1f} m")
        else:
            print("No hay actividades en la base de datos")

        # Estadísticas de kudos
        kudos_stats = db.fetch_one(conn, "SELECT COUNT(*) as total_kudos FROM Kudos")

        print(f"\nTotal kudos recibidos: {kudos_stats['total_kudos']}")


def limpiar_datos_ejemplo():
    """Limpia los datos de ejemplo insertados."""
    print("\n" + "=" * 60)
    print("LIMPIEZA: Eliminando datos de ejemplo")
    print("=" * 60)

    db_path = project_root / "bd" / "strava.sqlite"

    with db.DatabaseConnection(str(db_path)) as conn:
        # Eliminar kudos primero (foreign key)
        db.execute(conn, "DELETE FROM Kudos WHERE id_activity = ?", (12345678901,))
        print("[OK] Kudos de ejemplo eliminados")

        # Eliminar actividad
        db.execute(conn, "DELETE FROM Activities WHERE id_activity = ?", (12345678901,))
        print("[OK] Actividad de ejemplo eliminada")


def main():
    """Ejecuta todos los ejemplos."""
    print("\n" + "=" * 80)
    print(" EJEMPLOS DE USO DE LA BASE DE DATOS SQLITE - STRAVA")
    print("=" * 80)

    try:
        # Ejecutar ejemplos
        ejemplo_insertar_actividad()
        ejemplo_insertar_kudos()
        ejemplo_consultar_actividades()
        ejemplo_consultar_con_join()
        ejemplo_actualizar_kudos()
        ejemplo_estadisticas()

        # Preguntar si quiere limpiar los datos
        print("\n" + "=" * 80)
        response = input("\n¿Deseas eliminar los datos de ejemplo? (s/n): ")
        if response.lower() == "s":
            limpiar_datos_ejemplo()
        else:
            print("\nDatos de ejemplo conservados.")
            print("Puedes ejecutar init_database.py --reset para limpiar toda la BD")

        print("\n" + "=" * 80)
        print("[SUCCESS] EJEMPLOS COMPLETADOS")
        print("=" * 80)

    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
