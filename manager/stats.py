from aqt import mw
from datetime import date, timedelta, datetime, time


class Stats:
    def __init__(self) -> None:
        # Default value
        self.season_start = datetime(2020, 1, 1, 0, 0, 0)
        self.season_end = datetime(2020, 1, 1, 0, 0, 0)
        self.constraint = 20
        self.new_day = 4
        self.new_day_time = time(int(self.new_day), 0, 0)
        self.update_time_now()

    def update_time_now(self) -> time:
        self.time_now = datetime.now().time()
        return self.time_now

    def set_season_time(self, season_start: datetime, season_end: datetime) -> None:
        self.season_start = season_start
        self.season_end = season_end

    def set_constraint(self, constraint: int) -> None:
        self.constraint = constraint

    def set_new_day(self, new_day: int) -> None:
        self.new_day = new_day
        self.new_day_time = time(int(self.new_day), 0, 0)

    def get_streak(self) -> int:
        new_day = self.new_day
        new_day_time = self.new_day_time
        time_now = self.update_time_now()

        new_day_shift_in_ms = int(new_day) * 60 * 60 * 1000
        new_day_time = time(int(new_day), 0, 0)

        date_list = []
        Streak = 0

        date_list = mw.col.db.list(
            "SELECT DISTINCT strftime('%Y-%m-%d', datetime((id - ?) / 1000, 'unixepoch', 'localtime')) FROM revlog WHERE ease > 0 ORDER BY id DESC;", new_day_shift_in_ms)

        reviews_today, _ = self.get_reviews_and_retention_today()

        if time_now < new_day_time or reviews_today == 0:
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

    ### daily study ###
    def get_reviews_and_retention_today(self) -> tuple[int, float]:
        new_day_time = self.new_day_time
        time_now = self.update_time_now()

        if time_now < new_day_time:
            start_day = datetime.combine(
                date.today() - timedelta(days=1), new_day_time)
        else:
            start_day = datetime.combine(date.today(), new_day_time)
        return Stats.get_reviews_and_retention(start_day, start_day + timedelta(days=1))

    def get_time_spend_today(self) -> float:
        new_day_time = self.new_day_time
        time_now = self.update_time_now()

        if time_now < new_day_time:
            start_day = datetime.combine(
                date.today() - timedelta(days=1), new_day_time)
        else:
            start_day = datetime.combine(date.today(), new_day_time)
        return Stats.get_time_spend(start_day, start_day + timedelta(days=1))

    ### season study ###
    def get_reviews_and_retention_season(self) -> tuple[int, float]:
        season_start = self.season_start
        season_end = self.season_end

        reviews, retention = Stats.get_reviews_and_retention(
            season_start, season_end)
        return reviews, retention

    def get_time_spend_season(self) -> float:
        season_start = self.season_start
        season_end = self.season_end
        return Stats.get_time_spend(season_start, season_end)

    def get_days_learned_season(self) -> tuple[int, int]:
        season_start = self.season_start
        season_end = self.season_end
        new_day_time = self.new_day_time
        time_now = self.update_time_now()
        constraint = self.constraint

        date_list = [datetime.combine(season_start, new_day_time) + timedelta(
            days=x) for x in range((season_end - season_start).days + 1)]
        days_learned = 0
        days_over = 0
        for i in date_list:
            time = Stats.get_time_spend(i, i + timedelta(days=1))
            if time >= constraint:
                days_learned += 1
            if i.date() == date.today() and time_now < new_day_time:
                continue
            if i.date() <= date.today():
                days_over += 1

        return days_learned, days_over

    @staticmethod
    def get_reviews_and_retention(start_date: datetime, end_date: datetime) -> tuple[int, float]:
        start = int(start_date.timestamp() * 1000)
        end = int(end_date.timestamp() * 1000)
        reviews = mw.col.db.scalar(
            "SELECT COUNT(*) FROM revlog WHERE id >= ? AND id < ? AND ease > 0", start, end)
        flunked_total = mw.col.db.scalar(
            "SELECT COUNT(*) FROM revlog WHERE ease == 1 AND id >= ? AND id < ? AND ease > 0", start, end)

        if reviews == 0:
            return 0, 0

        retention = round((100 / reviews) * (reviews - flunked_total), 1)
        return reviews, retention

    @staticmethod
    def get_time_spend(start_date: datetime, end_date: datetime) -> float:
        start = int(start_date.timestamp() * 1000)
        end = int(end_date.timestamp() * 1000)

        time = mw.col.db.scalar(
            "SELECT SUM(time) FROM revlog WHERE id >= ? AND id < ?", start, end)
        if not time or time <= 0:
            return 0
        return round(time / 60000, 1)
