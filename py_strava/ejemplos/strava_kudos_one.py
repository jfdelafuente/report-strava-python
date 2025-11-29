import pandas as pd
import requests
import json
import time
import sqlite3
import strava_token_1 as stravaToken
import strava_bd_1 as stravaBBDD


#print("refresh token")
strava_tokens = stravaToken.refreshToken(stravaToken.getTokenFromFile())
access_token = strava_tokens['access_token']
print("Access Token = {}\n".format(access_token))


file = open('data/kudos.txt',"w")
log = open('data/strava.log',"w")

STRAVA_BD = 'bd/strava.sqlite'
conn = stravaBBDD.sql_connection(STRAVA_BD)
record = stravaBBDD.fetch(conn,'SELECT id, kudos, procesado FROM Activities')

actividad = []
count = dict()
seguir = 0
for row in record:
    linea = row[0]
    kudos = row[1]
    procesado = row[2]
    if kudos > 60 and procesado == 0 and seguir == 0:
        kudos_url = "https://www.strava.com/api/v3/activities/" + str(linea) + "/kudos"
        logger = kudos_url+ " "+ str(kudos)
        print(kudos_url, str(kudos))
        log.write(logger)
        log.write("\n")
        actividad.append(linea)

        page = 1
        while True:
            # Loop through all activities
            header = {'Authorization': 'Bearer ' + access_token}
            param = {'per_page': 30, 'page': page }
            r = requests.get(kudos_url, headers=header, params=param).json()
            #print(json.dumps(r, indent=2))
            #log.write("\n")

            if (not r or 'message' in r):
                seguir = 1
                print(json.dumps(r, indent=2))
                break

            for elemento in r:
                atleta = elemento['firstname'] + " " + elemento['lastname']
                log.write(elemento['firstname'] + " " + elemento['lastname'])
                # log.write("\n")
                if atleta not in count:
                    count[atleta] = 1
                else:
                    count[atleta] += 1

                # increment page
            page += 1

if seguir == 0:
    lst = list(count.keys())
    lst.sort()
    contador = 0
    for clave in lst:
        contador += count[clave]
        file.write(clave)
        file.write(":")
        file.write(str(count[clave]))
        file.write("\n")
        stravaBBDD.commit(conn,stravaBBDD.insert_statement("kuders", lst))
        #cur.execute('INSERT INTO kuders (nombre, kudos) VALUES (?,?)', (clave, count[clave]))
        #conn.commit()

    print("Hay Kudos en total : ", contador)

    for x in actividad:
        print("Actualizando ...", x)
        cur.execute('UPDATE Activities SET procesado = 1 where id = ?', (x,))

    conn.commit()
    conn.close()
    
file.close()
log.close()
