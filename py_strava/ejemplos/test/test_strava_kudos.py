import strava_token_1 as stravaToken
import strava_bd_1 as stravaBBDD
import strava_activities as stravaActivities
import json

# Creamos la conexión a la BD
STRAVA_BD = 'bd/strava.sqlite'
STRAVA_ACTIVITIES_LOG = 'data/strava_activities.log'
STRAVA_TOKEN_JSON = 'json/strava_tokens.json'

'''

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

'''

create_table_kudos = """
    CREATE TABLE IF NOT EXISTS Kudos (
    id_kudos INTEGER PRIMARY KEY AUTOINCREMENT,
    firstname TEXT,
    lastname TEXT,
    id_activity INTEGER,
    FOREIGN KEY (id_activity) REFERENCES Activities(id_activity)
    )
"""


# Creamos las bbdd donde almacenar las Actividades y los Kudos
conn = stravaBBDD.sql_connection(STRAVA_BD)
#stravaBBDD.commit(conn,'DROP TABLE IF EXISTS Activities')
#stravaBBDD.commit(conn,'DROP TABLE IF EXISTS Kudos')
#stravaBBDD.commit(conn, create_table_activities)
stravaBBDD.commit(conn, create_table_kudos)


#print("refresh token")
strava_tokens = stravaToken.refreshToken(stravaToken.getTokenFromFile(STRAVA_TOKEN_JSON), STRAVA_TOKEN_JSON)
access_token = strava_tokens['access_token']
print("Access Token = {}\n".format(access_token))

#record = stravaBBDD.fetch(conn,'SELECT id_activity FROM Activities WHERE kudos_count > 0')
record = stravaBBDD.fetch(conn,'SELECT id_activity FROM Activities WHERE kudos_count > 0 and id_activity not in (SELECT DISTINCT(Kudos.id_activity) from Kudos)')

for activity in record:
    # Obtener los kudos dados a una actividad
    try:
        kudos = ()
        print("Buscando ", activity[0])
        kudos = stravaActivities.request_kudos(access_token, activity[0])
        for k in range(len(kudos)):
            record = dict()
            record['id_activity'] = activity[0]
            record['firstname'] = kudos.loc[k,'firstname']
            record['lastname'] = kudos.loc[k,'lastname']
            stravaBBDD.commit(conn, stravaBBDD.insert_statement("Kudos", record))
    except Exception as ex:
        print(ex)
        exit(0)