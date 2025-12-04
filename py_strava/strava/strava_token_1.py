import json
import time

import requests


# Make Strava auth API call with your
# client_code, client_secret and code
def makeStravaAuth():
    response = requests.post(
        url="https://www.strava.com/oauth/token",
        data={
            "client_id": 56852,
            "client_secret": "6b229c286a12180a2acad07d23a6f43ae999d046",
            "code": "896509433675a143c7a61b819dd8f5294888a4d9",
            "grant_type": "authorization_code",
        },
    )
    # Save json response as a variable
    strava_tokens = response.json()
    return strava_tokens


# Save tokens to file
def saveTokenFile(strava_tokens, file):
    with open(file, "w") as outfile:
        json.dump(strava_tokens, outfile)


# Open JSON file and print the file contents
# to check it's worked properly
def openTokenFile(file):
    with open(file) as check:
        data = json.load(check)
    print(data)


# Get the tokens from file to connect to Strava
def getTokenFromFile(token_file):
    with open(token_file) as json_file:
        strava_tokens = json.load(json_file)
    return strava_tokens


# If access_token has expired then
# use the refresh_token to get the new access_token
def refreshToken(strava_tokens, file):
    if strava_tokens["expires_at"] < time.time():
        print("Actualizamos el refresh token")
        # Make Strava auth API call with current refresh token
        response = requests.post(
            url="https://www.strava.com/oauth/token",
            data={
                "client_id": 56852,
                "client_secret": "6b229c286a12180a2acad07d23a6f43ae999d046",
                "grant_type": "refresh_token",
                "refresh_token": strava_tokens["refresh_token"],
            },
        )
        # Save response as json in new variable
        new_strava_tokens = response.json()
        # Save new tokens to file
        saveTokenFile(new_strava_tokens, file)
    else:
        print("Refresh Token no ha expirado aun.")
        new_strava_tokens = strava_tokens

    return new_strava_tokens
