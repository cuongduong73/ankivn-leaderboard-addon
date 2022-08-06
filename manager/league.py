from .season import LeagueSeason


class League:
    def __init__(self) -> None:
        self._name = ""
        self._seasons = []
        self._curr_season_idx = 1

    def set_name(self, name: str) -> None:
        self._name = name

    def get_name(self, name: str) -> str:
        return self._name

    def get_curr_season_idx(self) -> int:
        return self._curr_season_idx

    def set_curr_season_idx(self, idx: int):
        self._curr_season_idx = idx

    def add_season(self, season_data: LeagueSeason) -> None:
        idx, s = self.get_season(season_data)
        if s is None:
            self._seasons.append(season_data)
        else:
            self.update_season(season_data, idx)

    def update_season(self, season_data: LeagueSeason, idx: int) -> None:
        self._seasons[idx] = season_data

    def get_season(self, season_idx: int) -> tuple[LeagueSeason, int]:
        for i, s in enumerate(self._seasons):
            if s.season == season_idx:
                return s, i

        return None, -1

    def get_curr_season(self) -> LeagueSeason:
        season, _ = self.get_season(self.get_curr_season_idx)
        return season

    def update_curr_season(self, season_data: LeagueSeason) -> None:
        self._seasons[self.get_curr_season_idx] = season_data
