"""
Dashboard Web Interactivo para Actividades de Strava

Aplicación Streamlit que muestra visualizaciones y estadísticas
de tus actividades de Strava almacenadas en la base de datos local.

Uso:
    streamlit run dashboard_app.py
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd

from py_strava.dashboard.data_loader import (
    load_activities_data,
    load_kudos_data,
    get_summary_stats,
    get_activities_by_type,
    get_activities_by_month,
    get_top_activities,
    get_kudos_leaderboard,
    check_database_exists
)
from py_strava import config

# Configuración de la página
st.set_page_config(
    page_title="Strava Dashboard",
    page_icon="🏃",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos personalizados
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #FC4C02;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    </style>
""", unsafe_allow_html=True)


def format_time(hours):
    """Formatea horas a formato HH:MM:SS"""
    if pd.isna(hours):
        return "N/A"
    total_seconds = int(hours * 3600)
    hours_int = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours_int:02d}:{minutes:02d}:{seconds:02d}"


def format_pace(pace):
    """Formatea ritmo a formato MM:SS"""
    if pd.isna(pace):
        return "N/A"
    minutes = int(pace)
    seconds = int((pace - minutes) * 60)
    return f"{minutes:02d}:{seconds:02d}"


@st.cache_data(ttl=300)  # Cache por 5 minutos
def load_data():
    """Carga los datos con cache"""
    activities_df = load_activities_data()
    kudos_df = load_kudos_data()
    return activities_df, kudos_df


def main():
    # Header
    st.markdown('<h1 class="main-header">🏃 Strava Dashboard</h1>', unsafe_allow_html=True)

    # Verificar que existe la base de datos
    if not check_database_exists():
        st.error("⚠️ No se encontró la base de datos o está vacía.")
        st.info("""
        Para usar este dashboard necesitas:
        1. Sincronizar tus actividades con: `strava sync`
        2. Verificar que la base de datos existe en: `bd/strava.sqlite`
        """)
        st.stop()

    # Cargar datos
    with st.spinner("Cargando datos..."):
        activities_df, kudos_df = load_data()

    if activities_df.empty:
        st.warning("No hay actividades en la base de datos. Ejecuta `strava sync` para sincronizar.")
        st.stop()

    # Sidebar - Filtros
    st.sidebar.header("📊 Filtros")

    # Filtro por tipo de actividad
    activity_types = ['Todas'] + sorted(activities_df['type'].unique().tolist())
    selected_type = st.sidebar.selectbox("Tipo de Actividad", activity_types)

    # Filtro por rango de fechas
    min_date = activities_df['date'].min()
    max_date = activities_df['date'].max()

    date_range = st.sidebar.date_input(
        "Rango de Fechas",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    # Aplicar filtros
    filtered_df = activities_df.copy()

    if selected_type != 'Todas':
        filtered_df = filtered_df[filtered_df['type'] == selected_type]

    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = filtered_df[
            (filtered_df['date'] >= start_date) &
            (filtered_df['date'] <= end_date)
        ]

    # Estadísticas resumidas
    stats = get_summary_stats(filtered_df)

    st.sidebar.markdown("---")
    st.sidebar.info(f"""
    **Base de datos:** `{config.SQLITE_DB_PATH.name}`

    **Última actualización:** {max_date.strftime('%d/%m/%Y')}

    **Total actividades:** {len(activities_df)}
    """)

    # Métricas principales
    st.header("📈 Resumen General")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            "Total Actividades",
            f"{stats['total_activities']:,}",
            help="Número total de actividades en el período seleccionado"
        )

    with col2:
        st.metric(
            "Distancia Total",
            f"{stats['total_distance_km']:.1f} km",
            help="Suma de distancias de todas las actividades"
        )

    with col3:
        st.metric(
            "Tiempo Total",
            format_time(stats['total_time_hours']),
            help="Tiempo total en movimiento"
        )

    with col4:
        st.metric(
            "Desnivel Total",
            f"{stats['total_elevation_m']:.0f} m",
            help="Desnivel acumulado total"
        )

    with col5:
        st.metric(
            "Total Kudos",
            f"{stats['total_kudos']:.0f}",
            help="Suma de todos los kudos recibidos"
        )

    # Tabs para diferentes secciones
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Análisis", "🏆 Top Actividades", "👍 Kudos", "📋 Datos"])

    with tab1:
        st.header("Análisis de Actividades")

        # Gráfico: Distribución por tipo
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Actividades por Tipo")
            type_data = get_activities_by_type(filtered_df)

            if not type_data.empty:
                fig_type = px.pie(
                    type_data,
                    values='Activities',
                    names='Type',
                    title='Distribución de Actividades por Tipo',
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                st.plotly_chart(fig_type, use_container_width=True)

        with col2:
            st.subheader("Distancia por Tipo")
            if not type_data.empty:
                fig_distance = px.bar(
                    type_data,
                    x='Type',
                    y='Distance (km)',
                    title='Distancia Total por Tipo de Actividad',
                    color='Type',
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig_distance.update_layout(showlegend=False)
                st.plotly_chart(fig_distance, use_container_width=True)

        # Gráfico: Evolución temporal
        st.subheader("Evolución Temporal")

        # Agrupar por mes
        monthly_data = filtered_df.groupby(filtered_df['start_date_local'].dt.to_period('M')).agg({
            'id_activity': 'count',
            'distance_km': 'sum',
            'moving_time_hours': 'sum'
        }).reset_index()

        monthly_data['start_date_local'] = monthly_data['start_date_local'].dt.to_timestamp()

        metric_choice = st.selectbox(
            "Métrica a visualizar",
            ["Número de Actividades", "Distancia (km)", "Tiempo (horas)"]
        )

        metric_map = {
            "Número de Actividades": "id_activity",
            "Distancia (km)": "distance_km",
            "Tiempo (horas)": "moving_time_hours"
        }

        if not monthly_data.empty:
            fig_timeline = px.line(
                monthly_data,
                x='start_date_local',
                y=metric_map[metric_choice],
                title=f'Evolución de {metric_choice} por Mes',
                markers=True
            )
            fig_timeline.update_traces(line_color='#FC4C02', line_width=3)
            st.plotly_chart(fig_timeline, use_container_width=True)

        # Gráfico: Actividades por día de la semana
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Actividades por Día de la Semana")
            weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            weekday_data = filtered_df['weekday'].value_counts().reindex(weekday_order, fill_value=0)

            fig_weekday = px.bar(
                x=weekday_data.index,
                y=weekday_data.values,
                labels={'x': 'Día', 'y': 'Actividades'},
                title='Distribución por Día de la Semana',
                color=weekday_data.values,
                color_continuous_scale='Oranges'
            )
            fig_weekday.update_layout(showlegend=False, coloraxis_showscale=False)
            st.plotly_chart(fig_weekday, use_container_width=True)

        with col2:
            st.subheader("Estadísticas por Tipo")
            if not type_data.empty:
                st.dataframe(
                    type_data.style.format({
                        'Activities': '{:.0f}',
                        'Distance (km)': '{:.2f}',
                        'Time (hours)': '{:.2f}',
                        'Elevation (m)': '{:.0f}',
                        'Kudos': '{:.0f}'
                    }),
                    use_container_width=True
                )

    with tab2:
        st.header("🏆 Top Actividades")

        col1, col2 = st.columns(2)

        with col1:
            criterion = st.selectbox(
                "Ordenar por",
                ["Distancia", "Kudos", "Desnivel"]
            )

        with col2:
            n_top = st.slider("Mostrar top", 5, 50, 10)

        criterion_map = {
            "Distancia": "distance_km",
            "Kudos": "kudos_count",
            "Desnivel": "total_elevation_gain"
        }

        top_activities = get_top_activities(filtered_df, by=criterion_map[criterion], n=n_top)

        if not top_activities.empty:
            # Crear tabla formateada
            display_df = top_activities.copy()
            display_df['start_date_local'] = display_df['start_date_local'].dt.strftime('%d/%m/%Y %H:%M')
            display_df['moving_time_hours'] = display_df['moving_time_hours'].apply(format_time)

            display_df = display_df.rename(columns={
                'name': 'Actividad',
                'type': 'Tipo',
                'start_date_local': 'Fecha',
                'distance_km': 'Distancia (km)',
                'moving_time_hours': 'Tiempo',
                'kudos_count': 'Kudos',
                'total_elevation_gain': 'Desnivel (m)'
            })

            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )

            # Gráfico de barras
            fig_top = px.bar(
                top_activities,
                x='name',
                y=criterion_map[criterion],
                title=f'Top {n_top} Actividades por {criterion}',
                color=criterion_map[criterion],
                color_continuous_scale='Oranges'
            )
            fig_top.update_layout(
                xaxis_title="Actividad",
                yaxis_title=criterion,
                showlegend=False,
                coloraxis_showscale=False
            )
            st.plotly_chart(fig_top, use_container_width=True)

    with tab3:
        st.header("👍 Análisis de Kudos")

        if not kudos_df.empty:
            col1, col2 = st.columns(2)

            with col1:
                st.metric("Total Kudos Recibidos", f"{len(kudos_df):,}")

            with col2:
                st.metric("Personas Únicas", f"{kudos_df['full_name'].nunique():,}")

            # Leaderboard
            st.subheader("🏆 Top Seguidores (más kudos dados)")
            n_kudos = st.slider("Mostrar top", 5, 50, 20, key="kudos_slider")

            leaderboard = get_kudos_leaderboard(kudos_df, n=n_kudos)

            if not leaderboard.empty:
                col1, col2 = st.columns([2, 3])

                with col1:
                    st.dataframe(
                        leaderboard,
                        use_container_width=True,
                        hide_index=True
                    )

                with col2:
                    fig_kudos = px.bar(
                        leaderboard.head(15),
                        x='Kudos Given',
                        y='Name',
                        orientation='h',
                        title=f'Top 15 Seguidores por Kudos',
                        color='Kudos Given',
                        color_continuous_scale='Oranges'
                    )
                    fig_kudos.update_layout(
                        yaxis={'categoryorder': 'total ascending'},
                        showlegend=False,
                        coloraxis_showscale=False
                    )
                    st.plotly_chart(fig_kudos, use_container_width=True)

            # Kudos por tipo de actividad
            st.subheader("Kudos por Tipo de Actividad")
            kudos_by_type = kudos_df.groupby('activity_type').size().reset_index(name='Kudos')
            kudos_by_type = kudos_by_type.sort_values('Kudos', ascending=False)

            fig_kudos_type = px.pie(
                kudos_by_type,
                values='Kudos',
                names='activity_type',
                title='Distribución de Kudos por Tipo de Actividad',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            st.plotly_chart(fig_kudos_type, use_container_width=True)

        else:
            st.info("No hay datos de kudos disponibles en la base de datos.")

    with tab4:
        st.header("📋 Tabla de Datos")

        # Mostrar datos filtrados
        st.subheader(f"Actividades ({len(filtered_df)} registros)")

        # Seleccionar columnas a mostrar
        display_columns = st.multiselect(
            "Seleccionar columnas a mostrar",
            options=['name', 'type', 'start_date_local', 'distance_km', 'moving_time_hours',
                     'total_elevation_gain', 'kudos_count', 'speed_kmh', 'pace_min_km'],
            default=['name', 'type', 'start_date_local', 'distance_km', 'moving_time_hours', 'kudos_count']
        )

        if display_columns:
            display_df = filtered_df[display_columns].copy()

            # Formatear columnas
            if 'start_date_local' in display_df.columns:
                display_df['start_date_local'] = display_df['start_date_local'].dt.strftime('%d/%m/%Y %H:%M')

            # Renombrar columnas
            column_names = {
                'name': 'Actividad',
                'type': 'Tipo',
                'start_date_local': 'Fecha',
                'distance_km': 'Distancia (km)',
                'moving_time_hours': 'Tiempo (h)',
                'total_elevation_gain': 'Desnivel (m)',
                'kudos_count': 'Kudos',
                'speed_kmh': 'Velocidad (km/h)',
                'pace_min_km': 'Ritmo (min/km)'
            }

            display_df = display_df.rename(columns=column_names)

            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )

            # Botón de descarga
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="⬇️ Descargar datos como CSV",
                data=csv,
                file_name=f"strava_activities_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

    # Footer
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: #666;'>
            <p>Dashboard de Strava | Desarrollado con Streamlit y Plotly</p>
            <p>Datos sincronizados desde Strava API</p>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
