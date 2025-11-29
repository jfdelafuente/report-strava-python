import requests
from pandas.io.json import json_normalize
import json

# Get the tokens from file to connect to Strava
with open('json/strava_tokens.json') as json_file:
    strava_tokens = json.load(json_file)

# Loop through all activities
url = "https://www.strava.com/api/v3/athlete"
access_token = strava_tokens['access_token']
print("Access Token = {}\n".format(access_token))


# Get first page of activities from Strava with all fields
r = requests.get(url + '?access_token=' + access_token)
r = r.json()
print(r)
    
df = json_normalize(r)
df.to_csv('data/strava_athlete_all_fields.csv')