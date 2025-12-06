# Dashboard Web Interactivo de Strava

Guía completa para usar el dashboard web de visualización de actividades.

## Descripción

El dashboard de Strava es una aplicación web interactiva construida con Streamlit y Plotly que te permite:

- 📊 Visualizar estadísticas resumidas de tus actividades
- 📈 Analizar tendencias temporales y patrones
- 🏆 Descubrir tus mejores actividades
- 👍 Explorar quiénes te dan más kudos
- 📋 Filtrar y exportar datos

## Instalación

### Requisitos

El dashboard requiere las siguientes dependencias:

```bash
pip install streamlit plotly
```

O instala todas las dependencias del proyecto:

```bash
pip install -r requirements.txt
```

## Iniciar el Dashboard

### Opción 1: Comando directo

```bash
streamlit run dashboard_app.py
```

### Opción 2: Scripts de inicio rápido

**Windows**:
```cmd
run_dashboard.bat
```

**Linux/Mac**:
```bash
./run_dashboard.sh
```

El dashboard se abrirá automáticamente en tu navegador predeterminado en `http://localhost:8501`

## Funcionalidades

### 1. Resumen General

**Métricas principales** mostradas en tarjetas:
- Total de actividades
- Distancia acumulada (km)
- Tiempo total en movimiento
- Desnivel total acumulado (m)
- Total de kudos recibidos

### 2. Panel de Filtros (Sidebar)

Controla qué datos ver:

- **Tipo de Actividad**: Filtra por Run, Ride, Walk, etc.
- **Rango de Fechas**: Selecciona período temporal específico
- **Información de BD**: Muestra ubicación y última actualización

### 3. Tab: Análisis

**Gráficos incluidos**:

#### Distribución por Tipo
- Gráfico de pastel mostrando proporción de cada tipo de actividad
- Gráfico de barras con distancia total por tipo

#### Evolución Temporal
- Gráfico de líneas mostrando tendencias mensuales
- Selector de métrica: número de actividades, distancia o tiempo
- Identifica patrones y progresión

#### Actividades por Día de Semana
- Gráfico de barras mostrando distribución semanal
- Descubre tus días más activos

#### Tabla de Estadísticas
- Resumen numérico por tipo de actividad
- Incluye: actividades, distancia, tiempo, desnivel, kudos

### 4. Tab: Top Actividades

**Ranking de mejores actividades**:

- Criterios de ordenación:
  - Distancia (km)
  - Kudos recibidos
  - Desnivel acumulado (m)

- Número configurable de resultados (5-50)
- Tabla detallada con:
  - Nombre de la actividad
  - Tipo
  - Fecha y hora
  - Métricas principales

- Gráfico de barras del top seleccionado

### 5. Tab: Kudos

**Análisis de kudos**:

- Total de kudos recibidos
- Número de personas únicas
- Leaderboard de top seguidores (más kudos dados)
- Distribución de kudos por tipo de actividad
- Gráficos:
  - Ranking horizontal de top seguidores
  - Pastel de kudos por tipo de actividad

### 6. Tab: Datos

**Exploración de datos crudos**:

- Selector de columnas personalizables
- Tabla interactiva con todos los datos filtrados
- Formato legible de fechas y tiempos
- Botón de descarga CSV
  - Exporta datos filtrados actuales
  - Nombre de archivo con timestamp

## Uso Recomendado

### Flujo de Trabajo Típico

1. **Sincroniza datos**:
   ```bash
   strava sync
   ```

2. **Abre el dashboard**:
   ```bash
   streamlit run dashboard_app.py
   ```

3. **Explora tus datos**:
   - Revisa el resumen general
   - Aplica filtros según tu interés
   - Navega entre las pestañas
   - Exporta datos si necesitas análisis adicional

### Casos de Uso

#### Análisis de Progresión
1. Ve a la pestaña "Análisis"
2. Selecciona métrica "Distancia (km)"
3. Observa la evolución temporal
4. Identifica tendencias y picos

#### Descubrir Récords Personales
1. Ve a "Top Actividades"
2. Ordena por "Distancia"
3. Revisa tu actividad más larga
4. Cambia a "Desnivel" para ver tu mayor reto vertical

#### Analizar Comunidad
1. Ve a la pestaña "Kudos"
2. Revisa el leaderboard
3. Identifica tus seguidores más activos
4. Ve qué tipos de actividades reciben más kudos

#### Exportar Datos Personalizados
1. Ve a la pestaña "Datos"
2. Aplica filtros deseados (tipo, fechas)
3. Selecciona columnas específicas
4. Descarga CSV para análisis externo (Excel, Python, R, etc.)

## Personalización

### Configuración de Streamlit

El archivo `.streamlit/config.toml` controla:

- **Tema**: Colores de Strava (naranja #FC4C02)
- **Puerto**: 8501 por defecto
- **Comportamiento**: Sin recolección de estadísticas

### Modificar el Dashboard

Para personalizar el dashboard, edita `dashboard_app.py`:

- Agregar nuevos gráficos
- Modificar métricas calculadas
- Cambiar estilos CSS
- Añadir nuevas pestañas

### Cache de Datos

El dashboard usa `@st.cache_data` con TTL de 5 minutos:
- Los datos se recargan automáticamente cada 5 minutos
- Para forzar recarga: presiona `R` en el navegador
- O usa el botón "Rerun" en la esquina superior derecha

## Solución de Problemas

### Error: "No se encontró la base de datos"

**Causa**: La base de datos SQLite no existe o está vacía.

**Solución**:
```bash
# Inicializar BD
strava init-db

# Sincronizar actividades
strava sync
```

### Error: "ModuleNotFoundError: No module named 'streamlit'"

**Causa**: Streamlit no está instalado.

**Solución**:
```bash
pip install streamlit plotly
```

### El dashboard no se abre en el navegador

**Solución manual**:
1. Abre tu navegador
2. Navega a: `http://localhost:8501`

### Puerto 8501 en uso

**Solución**: Especifica otro puerto:
```bash
streamlit run dashboard_app.py --server.port 8502
```

### Datos no actualizados

**Solución**:
1. Sincroniza primero: `strava sync`
2. Recarga el dashboard (presiona `R`)
3. O reinicia el servidor

## Rendimiento

### Optimización

El dashboard está optimizado para:
- Miles de actividades
- Carga rápida con caché
- Gráficos interactivos sin lag

### Recomendaciones

- **Muchas actividades** (>5000): Usa filtros de fecha
- **Análisis específico**: Filtra por tipo de actividad
- **Exportaciones grandes**: Usa el comando `strava report` para CSV completo

## Tecnologías Utilizadas

- **Streamlit**: Framework de aplicaciones web para Python
- **Plotly**: Biblioteca de gráficos interactivos
- **Pandas**: Procesamiento de datos
- **SQLite**: Base de datos

## Próximas Funcionalidades

Funcionalidades planeadas:

- [ ] Mapas interactivos de rutas con Folium
- [ ] Análisis de ritmo por segmentos
- [ ] Comparativas entre períodos
- [ ] Predicciones de rendimiento
- [ ] Exportación de gráficos como imágenes
- [ ] Modo oscuro
- [ ] Autenticación multi-usuario

## Feedback y Contribuciones

¿Tienes ideas para mejorar el dashboard?

1. Abre un issue en el repositorio
2. Describe la funcionalidad deseada
3. Contribuye con un Pull Request

## Recursos Adicionales

- [Documentación de Streamlit](https://docs.streamlit.io)
- [Galería de Plotly](https://plotly.com/python/)
- [README principal](../../README.md)
- [Guía de inicio rápido](INICIO_RAPIDO.md)

---

**Última actualización**: 6 de diciembre de 2025
