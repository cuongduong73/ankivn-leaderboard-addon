from .league import League


class LeagueManager:
    def __init__(self) -> None:
        self._leagues = []

    def add_league(self, league: League) -> None:
        lea, idx = self.get_league(league)
        if lea is None:
            self._leagues.append(league)
        else:
            self.update_league(league, idx)

    def update_league(self, league: League, idx: int) -> None:
        self._leagues[idx] = league

    def get_league(self, league: League) -> tuple[League, int]:
        for idx, lea in enumerate(self._leagues):
            if league.get_name() == lea.get_name():
                return lea, idx

        return None, -1
