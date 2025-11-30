import strava_token as stravaToken
import strava_db_sqlite as stravaBBDD
import strava_activities as stravaActivities

# Creamos la conexión a la BD
STRAVA_BD = 'bd/strava.sqlite'
STRAVA_ACTIVITIES_LOG = 'data/strava_activities.log'
STRAVA_ACTIVITIES_CSV = 'data/strava_activities.csv'
STRAVA_TOKEN_JSON = 'json/strava_tokens.json'

create_table_activities = """
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

# Creamos las bbdd donde almacenar las Actividades y los Kudos
conn = stravaBBDD.sql_connection(STRAVA_BD)
#stravaBBDD.commit(conn,'DROP TABLE IF EXISTS Activities')
stravaBBDD.commit(conn, create_table_activities)

#print("refresh token")
strava_tokens = stravaToken.refreshToken(stravaToken.getTokenFromFile(STRAVA_TOKEN_JSON), STRAVA_TOKEN_JSON)
access_token = strava_tokens['access_token']
print("Access Token = {}\n".format(access_token))

# obtener las actividades
activities = stravaActivities.request_activities(access_token)

# guardar todas las actividades a un fichero csv
activities.to_csv(STRAVA_ACTIVITIES_CSV)

# Recuperamos las Actividades y las cargamos en la bbdd
for k in range(len(activities)):
    record_a = dict()
    record_a['id_activity'] = activities.loc[k,'id']
    record_a['name'] = activities.loc[k,'name']
    record_a['start_date_local'] = activities.loc[k,'start_date_local']
    record_a['type'] = activities.loc[k,'type']
    record_a['distance'] = activities.loc[k,'distance']
    record_a['moving_time'] = activities.loc[k,'moving_time']
    record_a['elapsed_time'] = activities.loc[k,'elapsed_time']
    record_a['total_elevation_gain'] = activities.loc[k,'total_elevation_gain']
    record_a['end_latlng'] = str(activities.loc[k,'end_latlng'])
    record_a['kudos_count'] = activities.loc[k,'kudos_count']
    record_a['external_id'] = activities.loc[k,'external_id']
    stravaBBDD.commit(conn, stravaBBDD.insert_statement("Activities", record_a))
