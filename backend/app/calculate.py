from datetime import datetime

def get_last_day(start_time: int, season_duration: int):
    today_from_begin = get_league_day(start_time)
    return min(today_from_begin, season_duration)

def get_league_day(start_time: int) -> int:
    delta = datetime.now() - datetime.fromtimestamp(start_time)
    return delta.days + 1 if delta.seconds > 0 else delta.days

def get_time_stamps() -> int:
    return int(datetime.timestamp(datetime.now()))

def calculate_xp(reviews: int, retention: float, minutes: float, study_days: int = 0, day_over: int = 0) -> float:
    xp = float(0)
    if day_over == 0 and study_days == 0:
        xp = reviews + retention + minutes
    else:
        # calculate xp for a league
        xp = reviews + retention + minutes + study_days + day_over

    return round(xp, 1)
