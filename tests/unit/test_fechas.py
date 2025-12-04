import unittest

from py_strava.strava.strava_fechas import last_timestamp, timestamp_to_unix


class TestFechas(unittest.TestCase):
    def setUp(self):
        self.file = "data/test/strava_activities_all_fields.csv"

    def test_last_timestamp(self):
        self.assertEqual(last_timestamp(self.file), "2020-03-31T17:58:15Z")

    def test_timestamp_to_unix(self):
        self.assertEqual(timestamp_to_unix(last_timestamp(self.file)), 1585670295)

    def test_timestamp_to_unix_today(self):
        self.assertEqual(timestamp_to_unix("2021-02-16T19:00:00Z"), 1613498400)
