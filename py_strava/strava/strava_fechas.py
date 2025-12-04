import time
from datetime import datetime


def last_timestamp(activities_file):
    with open(activities_file) as f:
        lines = f.read().splitlines()
        first_line = lines[0].split(",")
        last_line = lines[-1].split(",")
        last_line_dict = dict(list(zip(first_line, last_line)))
        last_timestamp = last_line_dict["start_date_local"]
        f.close()
    return last_timestamp


def timestamp_to_unix(timestamp_string):
    timestamp_datatime = datetime.strptime(timestamp_string, "%Y-%m-%dT%H:%M:%SZ")
    datatime_tuple = timestamp_datatime.timetuple()
    unix_timestamp = int(time.mktime(datatime_tuple))
    return unix_timestamp
