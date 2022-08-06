from .Stats import Stats


class Manager():
    def __init__(self) -> None:
        self.stats = Stats()

    def set_stats_season_time(self, season_start, season_end) -> None:
        return self.stats.set_season_time(season_start, season_end)

    def set_stats_constraint(self, constraint: int) -> None:
        return self.stats.set_constraint(constraint)

    def set_stats_new_day(self, new_day: int) -> None:
        return self.stats.set_new_day(new_day)

    def get_daily_stats(self) -> dict:
        reviews, retention = self.stats.get_reviews_and_retention_today()
        daily_stats = {
            "reviews": reviews,
            "retention": retention,
            "study_time": self.stats.get_time_spend_today()
        }
        return daily_stats

    def get_season_stats(self) -> dict:
        reviews, retention = self.stats.get_reviews_and_retention_season()
        days_learned, days_over = self.stats.get_days_learned_season()
        season_stats = {
            "reviews": reviews,
            "retention": retention,
            "study_time": self.stats.get_time_spend_season(),
            "days_learned": days_learned,
            "days_over": days_over
        }
        return season_stats
