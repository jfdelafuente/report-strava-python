import requests
import urllib3
import json
from pandas.io.json import json_normalize
import csv
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

auth_url = "https://www.strava.com/oauth/token"
activites_url = "https://www.strava.com/api/v3/athlete/activities"

# Get the tokens from file to connect to Strava
with open('json/strava_tokens.json') as json_file:
    strava_tokens = json.load(json_file)

payload = {
    'client_id': 56852,
    'client_secret': '6b229c286a12180a2acad07d23a6f43ae999d046',
    'refresh_token': strava_tokens['refresh_token'],
    'grant_type': "refresh_token",
    'f': 'json'
}

print("Requesting Token...\n")
res = requests.post(auth_url, data=payload, verify=False)
access_token = res.json()['access_token']
print("Access Token = {}\n".format(access_token))
print(res.json())

header = {'Authorization': 'Bearer ' + access_token}
param = {'per_page': 200, 'page': 1}
print("Requesting Activites ...\n")
my_dataset = requests.get(activites_url, headers=header, params=param).json()
#print(my_dataset)

df = json_normalize(my_dataset)
df.to_csv('data/strava_activities_all_fields.csv')