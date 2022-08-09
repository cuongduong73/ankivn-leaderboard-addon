from .user import *
from .stats import Stats


class LeagueSeason():
    def __init__(self, season: int) -> None:
        self._season = season
        self._stats = Stats()
        self._user = User()
        self._competitors = []

    def get_season(self) -> int:
        return self._season

    def get_user(self) -> User:
        return self._user

    def get_competitors(self) -> list:
        return self._competitors

    def set_competitors(self, competitors: list[User]):
        self._competitors = competitors

    def set_stats_season_time(self, season_start, season_end) -> None:
        return self._stats.set_season_time(season_start, season_end)

    def set_stats_constraint(self, constraint: int) -> None:
        return self._stats.set_constraint(constraint)

    def set_stats_new_day(self, new_day: int) -> None:
        return self._stats.set_new_day(new_day)

    def get_user_today_stats(self) -> UserDailyStudyData:
        reviews, retention = self._stats.get_reviews_and_retention_today()
        _, days_over = self._stats.get_days_learned_season()
        user_today_study_data = UserDailyStudyData()
        user_today_study_data.day = days_over
        user_today_study_data.reviews = reviews
        user_today_study_data.study_time = self._stats.get_time_spend_today()
        user_today_study_data.retention = retention

        return user_today_study_data

    def get_user_season_stats(self) -> UserLeagueStudyData:
        reviews, retention = self._stats.get_reviews_and_retention_season()
        days_learned, days_over = self._stats.get_days_learned_season()
        user_league_study_data = UserLeagueStudyData()
        user_league_study_data.reviews = reviews
        user_league_study_data.retention = retention
        user_league_study_data.study_time = self._stats.get_time_spend_season()
        user_league_study_data.days_learned = days_learned
        user_league_study_data.days_over = days_over
        user_league_study_data.days_off = days_over - days_learned

        return user_league_study_data

    def update_user_stats(self) -> User:
        user_today_study_data = self.get_user_today_stats()
        user_league_study_data = self.get_user_season_stats()
        self.get_user().set_today_stats(user_today_study_data)
        self.get_user().add_curr_league_stats(user_today_study_data)
        self.get_user().set_overall_curr_league_stats(user_league_study_data)

        return self.get_user()

    def calc_xp_competitors(self) -> None:
        pass

    def sort_competitors(self) -> None:
        pass
