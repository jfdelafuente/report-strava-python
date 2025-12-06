"""
Módulo para cargar y procesar datos de actividades de Strava para el dashboard.

Este módulo proporciona funciones para:
- Cargar datos desde SQLite
- Procesar y transformar datos para visualización
- Calcular estadísticas y métricas
"""

import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd

from py_strava import config
from py_strava.database import sqlite as stravaBBDD

logger = logging.getLogger(__name__)


def load_activities_data(db_path: Optional[str] = None) -> pd.DataFrame:
    """
    Carga todas las actividades desde la base de datos SQLite.

    Args:
        db_path: Ruta a la base de datos SQLite. Si es None, usa la ruta por defecto.

    Returns:
        DataFrame con todas las actividades
    """
    if db_path is None:
        db_path = str(config.SQLITE_DB_PATH)

    try:
        conn = stravaBBDD.sql_connection(db_path)

        query = """
            SELECT
                id_activity,
                name,
                start_date_local,
                type,
                distance,
                moving_time,
                elapsed_time,
                total_elevation_gain,
                kudos_count,
                external_id
            FROM Activities
            ORDER BY start_date_local DESC
        """

        df = pd.read_sql_query(query, conn)
        conn.close()

        # Convertir fechas
        if not df.empty:
            df['start_date_local'] = pd.to_datetime(df['start_date_local'])
            df['date'] = df['start_date_local'].dt.date
            df['year'] = df['start_date_local'].dt.year
            df['month'] = df['start_date_local'].dt.month
            df['month_name'] = df['start_date_local'].dt.strftime('%B')
            df['week'] = df['start_date_local'].dt.isocalendar().week
            df['weekday'] = df['start_date_local'].dt.day_name()

            # Convertir distancia a km
            df['distance_km'] = df['distance'] / 1000

            # Convertir tiempos a horas
            df['moving_time_hours'] = df['moving_time'] / 3600
            df['elapsed_time_hours'] = df['elapsed_time'] / 3600

            # Calcular ritmo (min/km) solo para Run y Walk
            df['pace_min_km'] = None
            mask = (df['type'].isin(['Run', 'Walk'])) & (df['distance_km'] > 0)
            df.loc[mask, 'pace_min_km'] = df.loc[mask, 'moving_time'] / 60 / df.loc[mask, 'distance_km']

            # Calcular velocidad (km/h)
            df['speed_kmh'] = None
            speed_mask = df['moving_time_hours'] > 0
            df.loc[speed_mask, 'speed_kmh'] = df.loc[speed_mask, 'distance_km'] / df.loc[speed_mask, 'moving_time_hours']

        logger.info(f"Cargadas {len(df)} actividades desde {db_path}")
        return df

    except Exception as e:
        logger.error(f"Error cargando actividades: {e}")
        return pd.DataFrame()


def load_kudos_data(db_path: Optional[str] = None) -> pd.DataFrame:
    """
    Carga todos los kudos desde la base de datos SQLite.

    Args:
        db_path: Ruta a la base de datos SQLite. Si es None, usa la ruta por defecto.

    Returns:
        DataFrame con todos los kudos
    """
    if db_path is None:
        db_path = str(config.SQLITE_DB_PATH)

    try:
        conn = stravaBBDD.sql_connection(db_path)

        query = """
            SELECT
                k.id_kudos,
                k.firstname,
                k.lastname,
                k.id_activity,
                a.name as activity_name,
                a.type as activity_type,
                a.start_date_local
            FROM Kudos k
            INNER JOIN Activities a ON k.id_activity = a.id_activity
            ORDER BY a.start_date_local DESC
        """

        df = pd.read_sql_query(query, conn)
        conn.close()

        if not df.empty:
            df['start_date_local'] = pd.to_datetime(df['start_date_local'])
            df['full_name'] = df['firstname'] + ' ' + df['lastname']

        logger.info(f"Cargados {len(df)} kudos desde {db_path}")
        return df

    except Exception as e:
        logger.error(f"Error cargando kudos: {e}")
        return pd.DataFrame()


def get_summary_stats(df: pd.DataFrame) -> Dict[str, any]:
    """
    Calcula estadísticas resumidas de las actividades.

    Args:
        df: DataFrame con actividades

    Returns:
        Diccionario con estadísticas resumidas
    """
    if df.empty:
        return {
            'total_activities': 0,
            'total_distance_km': 0,
            'total_time_hours': 0,
            'total_elevation_m': 0,
            'total_kudos': 0,
            'avg_distance_km': 0,
            'avg_speed_kmh': 0,
        }

    return {
        'total_activities': len(df),
        'total_distance_km': df['distance_km'].sum(),
        'total_time_hours': df['moving_time_hours'].sum(),
        'total_elevation_m': df['total_elevation_gain'].sum(),
        'total_kudos': df['kudos_count'].sum(),
        'avg_distance_km': df['distance_km'].mean(),
        'avg_speed_kmh': df['speed_kmh'].mean(),
        'activity_types': df['type'].value_counts().to_dict(),
    }


def get_activities_by_type(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agrupa actividades por tipo.

    Args:
        df: DataFrame con actividades

    Returns:
        DataFrame agrupado por tipo de actividad
    """
    if df.empty:
        return pd.DataFrame()

    grouped = df.groupby('type').agg({
        'id_activity': 'count',
        'distance_km': 'sum',
        'moving_time_hours': 'sum',
        'total_elevation_gain': 'sum',
        'kudos_count': 'sum'
    }).reset_index()

    grouped.columns = ['Type', 'Activities', 'Distance (km)', 'Time (hours)', 'Elevation (m)', 'Kudos']
    grouped = grouped.sort_values('Activities', ascending=False)

    return grouped


def get_activities_by_month(df: pd.DataFrame, year: Optional[int] = None) -> pd.DataFrame:
    """
    Agrupa actividades por mes.

    Args:
        df: DataFrame con actividades
        year: Año a filtrar (opcional)

    Returns:
        DataFrame agrupado por mes
    """
    if df.empty:
        return pd.DataFrame()

    data = df.copy()
    if year:
        data = data[data['year'] == year]

    grouped = data.groupby(['year', 'month', 'month_name']).agg({
        'id_activity': 'count',
        'distance_km': 'sum',
        'moving_time_hours': 'sum',
    }).reset_index()

    grouped.columns = ['Year', 'Month', 'Month Name', 'Activities', 'Distance (km)', 'Time (hours)']
    grouped = grouped.sort_values(['Year', 'Month'])

    return grouped


def get_top_activities(df: pd.DataFrame, by: str = 'distance_km', n: int = 10) -> pd.DataFrame:
    """
    Obtiene las top N actividades según un criterio.

    Args:
        df: DataFrame con actividades
        by: Columna por la que ordenar ('distance_km', 'kudos_count', 'total_elevation_gain')
        n: Número de actividades a retornar

    Returns:
        DataFrame con las top N actividades
    """
    if df.empty:
        return pd.DataFrame()

    return df.nlargest(n, by)[['name', 'type', 'start_date_local', 'distance_km',
                                 'moving_time_hours', 'kudos_count', 'total_elevation_gain']]


def get_kudos_leaderboard(kudos_df: pd.DataFrame, n: int = 20) -> pd.DataFrame:
    """
    Obtiene el ranking de personas que más kudos han dado.

    Args:
        kudos_df: DataFrame con kudos
        n: Número de personas en el ranking

    Returns:
        DataFrame con el ranking
    """
    if kudos_df.empty:
        return pd.DataFrame()

    leaderboard = kudos_df.groupby('full_name').agg({
        'id_kudos': 'count'
    }).reset_index()

    leaderboard.columns = ['Name', 'Kudos Given']
    leaderboard = leaderboard.sort_values('Kudos Given', ascending=False).head(n)

    return leaderboard


def check_database_exists(db_path: Optional[str] = None) -> bool:
    """
    Verifica si la base de datos existe y tiene datos.

    Args:
        db_path: Ruta a la base de datos SQLite

    Returns:
        True si la base de datos existe y tiene datos
    """
    if db_path is None:
        db_path = str(config.SQLITE_DB_PATH)

    db_file = Path(db_path)

    if not db_file.exists():
        return False

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Activities")
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0
    except Exception:
        return False
