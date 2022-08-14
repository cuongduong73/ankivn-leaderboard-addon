from aqt import mw
from datetime import datetime, time, date, timedelta
UTC_7_TIMESTAMP_OFFSET = 60*60*7
SECONDS_IN_A_DAY = 60*60*24

def get_time_utc7(timestamp: int):
    utc7_time = timestamp + UTC_7_TIMESTAMP_OFFSET
    return datetime.fromtimestamp(utc7_time)

def get_datetime_now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_time_stamp():
    return int(datetime.now().timestamp())

def get_time_now():
    return datetime.now().time()

def get_reviews_and_retention_today(reset_point: int):
    new_day_time = time(reset_point, 0, 0)
    time_now = get_time_now()

    if time_now < new_day_time:
        start_day = datetime.combine(
            date.today() - timedelta(days=1), new_day_time)
    else:
        start_day = datetime.combine(date.today(), new_day_time)
    return get_reviews_and_retention(start_day, start_day + timedelta(days=1))

def get_time_spend_today(reset_point):
    new_day_time = time(reset_point, 0, 0)
    time_now = get_time_now()

    if time_now < new_day_time:
        start_day = datetime.combine(
            date.today() - timedelta(days=1), new_day_time)
    else:
        start_day = datetime.combine(date.today(), new_day_time)
    return get_time_spend(start_day, start_day + timedelta(days=1))    

def get_time_spend(start_date: datetime, end_date: datetime):
    return get_time_spend_from_timestamp(start_date.timestamp(), end_date.timestamp())

def get_time_spend_from_timestamp(start_timestamp: int, end_timestamp: int):
    start = int(start_timestamp * 1000)
    end = int(end_timestamp * 1000)

    time_study = mw.col.db.scalar(
        "SELECT SUM(time) FROM revlog WHERE id >= ? AND id < ?", start, end)
    if not time_study or time_study <= 0:
        return 0
    return int(round(time_study / 60000, 1))    

def get_reviews_and_retention(start_date: datetime, end_date: datetime):
    return get_reviews_and_retention_from_timestamp(start_date.timestamp(), end_date.timestamp())

def get_reviews_and_retention_from_timestamp(start_timestamp: int, end_timestamp: int):
    # get review and retention from timestamp
    start = int(start_timestamp * 1000)
    end = int(end_timestamp * 1000)
    reviews = mw.col.db.scalar(
        "SELECT COUNT(*) FROM revlog WHERE id >= ? AND id < ? AND ease > 0", start, end)
    flunked_total = mw.col.db.scalar(
        "SELECT COUNT(*) FROM revlog WHERE ease == 1 AND id >= ? AND id < ? AND ease > 0", start, end)

    if reviews == 0:
        return 0, 0

    retention = round((100 / reviews) * (reviews - flunked_total), 1)
    return reviews, retention

def get_streak(reset_point: int):
    reset_point_time = time(reset_point, 0, 0)
    time_now = get_time_now()
    new_day_shift_in_ms = reset_point * 60 * 60 * 1000

    date_list = []
    Streak = 0

    date_list = mw.col.db.list(
        "SELECT DISTINCT strftime('%Y-%m-%d', datetime((id - ?) / 1000, 'unixepoch', 'localtime')) FROM revlog WHERE ease > 0 ORDER BY id DESC;", new_day_shift_in_ms)

    reviews_today, _ = get_reviews_and_retention_today(reset_point)
    if time_now < reset_point_time or reviews_today == 0:
        start_date = date.today() - timedelta(days=1)
    else:
        start_date = date.today()

    end_date = date(2006, 10, 15)
    delta = timedelta(days=1)
    while start_date >= end_date:
        if not start_date.strftime("%Y-%m-%d") in date_list:
            break
        Streak = Streak + 1
        start_date -= delta
    return Streak

# def get_start_end_date(start_timestamp, duration):
#     season_start = datetime.fromtimestamp(start_timestamp)
#     season_end = datetime.fromtimestamp(start_timestamp + duration * SECONDS_IN_A_DAY)
#     return season_start, season_end

def get_end_timestamp(start_timestamp, duration):
    return start_timestamp + duration * SECONDS_IN_A_DAY

def get_reviews_and_retention_season(start_timestamp: int, duration: int):
    end_timestamp = get_end_timestamp(start_timestamp, duration)
    reviews, retention = get_reviews_and_retention_from_timestamp(start_timestamp, end_timestamp)

    # season_start, season_end = get_start_end_date(start_timestamp, duration)
    # reviews, retention = get_reviews_and_retention(
    #     season_start, season_end)
    return reviews, retention

def get_time_spend_season(start_timestamp, duration):
    end_timestamp = get_end_timestamp(start_timestamp, duration)
    return get_time_spend_from_timestamp(start_timestamp, end_timestamp)

def get_days_learned_season(start_timestamp: int, duration: int, reset_point: int, constraint: int):
    reset_point_time = time(reset_point, 0, 0)
    season_start = datetime.fromtimestamp(start_timestamp)
    season_end = datetime.fromtimestamp(get_end_timestamp(start_timestamp, duration))

    time_now = get_time_now()

    date_list = [datetime.combine(season_start, reset_point_time) + timedelta(
        days=x) for x in range((season_end - season_start).days + 1)]
    days_learned = 0
    days_over = 0
    for i in date_list:
        time_spend = get_time_spend(i, i + timedelta(days=1))
        if time_spend >= constraint:
            days_learned += 1
        if i.date() == date.today() and time_now < reset_point_time:
            continue
        if i.date() <= date.today():
            days_over += 1

    return days_learned, days_over