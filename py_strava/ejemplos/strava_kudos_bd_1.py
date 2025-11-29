import pandas as pd
import requests
import json
import time
import sqlite3
import strava_token_1 as stravaToken


#print("refresh token")
strava_tokens = stravaToken.refreshToken(stravaToken.getTokenFromFile())

#Loop through all activities
page = 1
access_token = strava_tokens['access_token']
print("Access Token = {}\n".format(access_token))

conn = sqlite3.connect('bd/strava.sqlite')
cur = conn.cursor()

cur.execute('SELECT id, kudos, procesado FROM Activities')

for row in cur:
    #print(row[0],row[1], row[2])
    linea = row[0]
    kudos = row[1]
    procesado = row[2]
    if kudos > 70 and procesado == 0:
        kudos_url = "https://www.strava.com/api/v3/activities/" + str(linea) + "/kudos"
        print(kudos_url)
        # print("--------------")

        #while True:
    
            # Loop through all activities
            #header = {'Authorization': 'Bearer ' + access_token}
            #param = {'per_page': 30, 'page': page }
            #r = requests.get(kudos_url, headers=header, params=param).json()
        
            #if (not r):
            #    break
            #print(r) 
            # otherwise add new data to dataframe
            #for x in range(len(r)):
            #    print(x)
            # increment page
            #page += 1

conn.close()