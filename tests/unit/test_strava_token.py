from py_strava.strava.strava_token_1 import refreshToken, getTokenFromFile, openTokenFile
import unittest


class TestStravaToken(unittest.TestCase):
    def setUp(self):
        self.STRAVA_TOKEN_JSON = 'json/test/strava_tokens.json'
        self.access_token = "f4e2939500ffa174654f91a9177e05b87d217938"
        self.expires_at = 1613511684
        self.expires_in = 21600
        self.refresh_token = "e518c071c6bed349dbfb9b46e1e75efab02e4ff1"
        self.strava_tokens_json = {
                    "token_type": "Bearer", 
                    "access_token": "f4e2939500ffa174654f91a9177e05b87d217938", 
                    "expires_at": 1613511684, 
                    "expires_in": 21600, 
                    "refresh_token": "e518c071c6bed349dbfb9b46e1e75efab02e4ff1"
                    }

    def test_get_token_from_file(self):
        self.assertEqual(getTokenFromFile(self.STRAVA_TOKEN_JSON), self.strava_tokens_json)

    def test_no_refresh_token(self):
        strava_tokens = refreshToken(getTokenFromFile(self.STRAVA_TOKEN_JSON), self.STRAVA_TOKEN_JSON)
        self.assertEqual(strava_tokens['refresh_token'], self.refresh_token)

    def test_refresh_token(self):
        strava_tokens = refreshToken(getTokenFromFile(self.STRAVA_TOKEN_JSON), self.STRAVA_TOKEN_JSON)
        self.assertEqual(strava_tokens['access_token'], self.access_token)
