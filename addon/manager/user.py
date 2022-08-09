class UserLeagueStudyData:
    def __init__(self) -> None:
        self.reviews = int(0)
        self.study_time = float(0)
        self.retention = float(0)
        self.days_learned = int(0)
        self.days_over = int(0)
        self.days_off = int(0)

    def to_json(self):
        return {
            "reviews": self.reviews,
            "study_time": self.study_time,
            "retention": self.retention,
            "days_learned": self.days_learned,
            "days_over": self.days_over,
            "days_off": self.days_off
        }


class UserDailyStudyData:
    def __init__(self) -> None:
        self.day = int(0)
        self.reviews = int(0)
        self.study_time = float(0)
        self.retention = float(0)

    def to_json(self):
        return {
            "day": self.day,
            "reviews": self.reviews,
            "study": self.study_time,
            "retention": self.retention,
        }


class UserLeagueInfo:
    def __init__(self) -> None:
        self.overall = UserLeagueStudyData()
        self.details = []

    def add_details(self, daily_study_data: UserDailyStudyData) -> None:
        check_exist = False
        for idx, detail in enumerate(self.details):
            # Update data if existed
            if detail.day == daily_study_data.day:
                self.details[idx].reviews = daily_study_data.reviews
                self.details[idx].study_time = daily_study_data.study_time
                self.details[idx].retention = daily_study_data.retention
                check_exist = True
                break

        if not check_exist:
            self.details.append(daily_study_data)


class User(object):
    def __init__(self) -> None:
        self._username = ""
        self._achievements = []
        self._today_stats = UserDailyStudyData()
        self._curr_league_stats = UserLeagueInfo()

    def get_username(self) -> str:
        return self._username

    def get_achievements(self) -> list[int]:
        return self._achievements

    def get_today_stats(self) -> UserDailyStudyData:
        return self._today_stats

    def get_curr_league_stats(self) -> UserLeagueInfo:
        return self._curr_league_stats

    ##### Set functions #########
    def set_username(self, username: str) -> None:
        self.username = username

    def set_achievements(self, achievements: list[int]) -> None:
        self._achievements = achievements

    def set_today_stats(self, stats: UserDailyStudyData) -> None:
        self._today_stats = stats

    def set_curr_league_stats(self, league_stats: UserLeagueInfo) -> None:
        self._curr_league_stats = league_stats

    def add_curr_league_stats(self, stats: UserDailyStudyData) -> None:
        self._curr_league_stats.add_details(stats)

    def set_overall_curr_league_stats(self, overall: UserLeagueStudyData) -> None:
        self._curr_league_stats.overall = overall
