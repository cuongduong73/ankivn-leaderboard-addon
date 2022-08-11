import re
from datetime import datetime


def validate_username(username: str) -> bool:
    # username is 6-20 characters long
    # no _ or . at the beginning
    # no __ or _. or ._ or .. inside
    # allowed characters a-z, A-Z, 0-9, _
    # no _ or . at the end
    pattern = re.compile("^(?=[a-zA-Z0-9_]{5,20}$)(?!.*[_.]{2})[^_.].*[^_.]$")
    return False if pattern.match(username) is None else True


def validate_password(password: str) -> bool:
    # [8-20] characters, at least one letter and one number
    pattern = re.compile("^(?=.*[A-Za-z])(?=.*\d)[\w~@#$%^&*+=`|{}:;!.?\"()\[\]-]{8,20}$")
    return False if pattern.match(password) is None else True

def calculate_xp(reviews: int, retention: float, minutes: int, day: int = 0, study_days: int = 0) -> float:
    xp = 3*minutes + reviews*retention/100
    if day != 0 and study_days != 0:
        xp = xp * (study_days/day)
    return round(xp, 1)

seconds_per_day = 60 * 60 * 24

def calculate_timedelta(start_time: int, endtime: int) -> int:
    delta_in_seconds = endtime - start_time
    return int((delta_in_seconds + seconds_per_day - 1 ) // seconds_per_day)

def get_timestamp():
    return datetime.utcnow().timestamp()

