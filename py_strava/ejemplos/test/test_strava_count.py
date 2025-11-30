import strava_db_sqlite as stravaBBDD
import csv

# Creamos la conexión a la BD
STRAVA_BD = 'bd/strava.sqlite'
STRAVA_KUDOS_COUNT = 'data/count2.csv'
select_table_kudos = """SELECT * FROM KUDOS"""

# Creamos las bbdd donde almacenar las Actividades y los Kudos
conn = stravaBBDD.sql_connection(STRAVA_BD)
count = dict()
record = stravaBBDD.fetch(conn,select_table_kudos)

'''

for elemento in record:
    atleta = elemento[1] + " " + elemento[2]
    if atleta not in count:
        count[atleta] = 1
    else:
        count[atleta] += 1
    
with open(STRAVA_KUDOS_COUNT, 'w', newline = '\n') as a:
    csv_write = csv.writer(a)
    csv_write.writerow(["nombre", "kudos"])
    for c in count:
        csv_write.writerow([c, count[c]])
a.close()
'''
with open(STRAVA_KUDOS_COUNT, 'w', newline = '\n') as a:
    for elemento in record:
        csv_write = csv.writer(a)
        csv_write.writerow(elemento)
a.close()

    