import sqlite3
from .env import DB_FILE
from .models.db_model import *
from .models.sync_model import LeagueUserStats
from .calculate import get_last_day
import inspect

USER_TBL = "users"
LEAGUES_INFO_TBL = "leagues_info"
LEAGUES_USER_TBL = "leagues_users"
LEAGUES_DATA_TBL = "leagues_data"
ACHIEVEMENT_TBL = "achievements"


class Database:
    def __init__(self) -> None:
        pass

    def connect_database(self):
        self.con = sqlite3.connect(DB_FILE)
        self.cur = self.con.cursor()
        self._create_tables()

    def release_database(self):
        self.con.close()

    def execute_fetchone(self, query: str):
        try:
            self.cur.execute(query)
            value = self.cur.fetchone()
            self.con.commit()
            return value
        except Exception as e:
            # print caller function name
            print(f"QUERY {inspect.stack()[1][3]} failed!")
            print(e)

    def execute_fetchall(self, query: str):
        try:
            self.cur.execute(query)
            values = self.cur.fetchall()
            self.con.commit()
            return values
        except Exception as e:
            # print caller function name
            print(f"QUERY {inspect.stack()[1][3]} failed!")
            print(e)


    def execute_one(self, query: str):
        try:
            self.cur.execute(query)
            self.con.commit()
        except Exception as e:
            # print caller function name
            print(f"QUERY {inspect.stack()[1][3]} failed!")
            print(e)

            

    @staticmethod
    def return_db_user_schema(value) -> DB_User_Schema:
        if value:
            return DB_User_Schema(username=value[0],
                                  password=value[1],
                                  email=value[2],
                                  role=value[3])
        return None

    @staticmethod
    def return_db_league_info_schema(value) -> DB_League_Info_Schema:
        if value:
            return DB_League_Info_Schema(league_uuid=value[0],
                                         league_name=value[1],
                                         season=value[2],
                                         start_time=value[3],
                                         duration=value[4],
                                         reset=value[5])
        return None

    @staticmethod
    def return_db_league_data_schema(value) -> DB_League_Data_Schema:
        if value:
            return DB_League_Data_Schema(league_uuid=value[0],
                                         username=value[1],
                                         day_over=value[2],
                                         streak=value[3],
                                         reviews_today=value[4],
                                         retention_today=value[5],
                                         minutes_today=value[6],
                                         xp_today=value[7],
                                         reviews_league=value[8],
                                         retention_league=value[9],
                                         minutes_league=value[10],
                                         xp_league=value[11],
                                         study_days=value[12],
                                         timestamps=value[13])
        return None

    @staticmethod
    def return_db_league_user_schema(value) -> DB_League_User_Schema:
        if value:
            return DB_League_User_Schema(league_uuid=value[0],
                                         username=value[1],
                                         role=value[2])
        return None

    @staticmethod
    def return_db_league_achievement_schema(value) -> DB_Achievement_Schema:
        if value:
            return DB_Achievement_Schema(username=value[0],
                                         league_name=value[1],
                                         gold=value[2],
                                         silver=value[3],
                                         bronze=value[4])
        return None

    @staticmethod
    def return_db_all_league_info_schema(values) -> list[DB_League_Info_Schema]:
        leagues = []
        if values:
            for value in values:
                leagues.append(Database.return_db_league_info_schema(value))
        return leagues

    @staticmethod
    def return_db_users_league_data_schema(values) -> list[DB_League_Data_Schema]:
        users = []
        if values:
            for value in values:
                users.append(Database.return_db_league_data_schema(value))
        return users

    @staticmethod
    def return_league_user_stats(values) -> list[LeagueUserStats]:
        users = []
        if values:
            for value in values:
                users.append(Database.return_db_league_data_schema(
                    value).league_stats)

        return users

    def get_user_info_by_name(self, username: str) -> DB_User_Schema:
        query = f"SELECT * FROM users WHERE username = '{username}';"
        result = self.execute_fetchone(query)
        return Database.return_db_user_schema(result)

    def get_user_info_by_email(self, email: str) -> DB_User_Schema:
        query = f"SELECT * FROM users WHERE email = '{email}';"
        result = self.execute_fetchone(query)
        return Database.return_db_user_schema(result)

    def insert_user_info(self, user: DB_User_Schema):
        query = f"""INSERT INTO {USER_TBL} VALUES ('{user.username}','{user.password}','{user.email}',{user.role});"""
        self.execute_one(query)

    def get_all_leagues_info(self) -> list[DB_League_Info_Schema]:
        query = f"SELECT * FROM {LEAGUES_INFO_TBL}"
        results = self.execute_fetchall(query)
        return Database.return_db_all_league_info_schema(results)

    # Return leagues_info of ALL season of league_name
    def get_leagues_info_by_name(self, league_name: str) -> list[DB_League_Info_Schema]:
        query = f"SELECT * FROM {LEAGUES_INFO_TBL} WHERE name = '{league_name}';"
        results = self.execute_fetchall(query)
        return Database.return_db_all_league_info_schema(results)

    # Return league_info only ONE season of league_name
    def get_league_info_by_name_and_season(self, league_name: str, league_season: int) -> DB_League_Info_Schema:
        query = f"SELECT * FROM {LEAGUES_INFO_TBL} WHERE name = '{league_name}' AND season = {league_season};"
        result = self.execute_fetchone(query)
        return Database.return_db_league_info_schema(result)

    def get_league_info_by_id(self, id: str) -> DB_League_Info_Schema:
        query = f"SELECT * FROM {LEAGUES_INFO_TBL} WHERE id = '{id}';"
        result = self.execute_fetchone(query)
        return Database.return_db_league_info_schema(result)

    def insert_league_info(self, league_info: DB_League_Info_Schema):
        query = f"""INSERT INTO {LEAGUES_INFO_TBL} VALUES ('{league_info.league_uuid}',
                                                           '{league_info.league_name}',
                                                            {league_info.season},
                                                            {league_info.start_time},
                                                            {league_info.duration},
                                                            {league_info.reset});"""

        self.execute_one(query)

    def insert_user_to_league(self, user: DB_League_User_Schema):
        query = f"""INSERT INTO {LEAGUES_USER_TBL} VALUES ('{user.league_uuid}',
                                                           '{user.username}',
                                                           '{user.role}');"""
        self.execute_one(query)

    def get_user_info_in_league(self, user: DB_League_User_Schema) -> DB_League_User_Schema:
        query = f"""SELECT * FROM {LEAGUES_USER_TBL} WHERE league_id = '{user.league_uuid}' 
                                                     AND username = '{user.username}';"""
        result = self.execute_fetchone(query)
        return Database.return_db_league_user_schema(result)

    def update_user_role_of_league(self, user: DB_League_User_Schema):
        query = f"""UPDATE {LEAGUES_USER_TBL}
                    SET league_role = {user.role} 
                    WHERE league_id = '{user.league_uuid}' AND username = '{user.username}';"""
        self.execute_one(query)

    def delete_user_in_league(self, user: DB_League_User_Schema):
        query = f"""DELETE FROM {LEAGUES_USER_TBL} 
                    WHERE league_id = '{user.league_uuid}' 
                    AND username = '{user.username}';"""

        self.execute_one(query)
        query = f"""DELETE FROM {LEAGUES_DATA_TBL} 
                    WHERE league_id = '{user.league_uuid}' 
                    AND username = '{user.username}';"""
        self.execute_one(query)

    def insert_league_data(self, data: DB_League_Data_Schema):
        query = f"""INSERT INTO {LEAGUES_DATA_TBL} VALUES ('{data.league_uuid}',
                                                           '{data.username}',
                                                           '{data.day_over}',
                                                           '{data.streak}',
                                                           '{data.reviews_today}',
                                                           '{data.retention_today}',
                                                           '{data.minutes_today}',
                                                           '{data.xp_today}',
                                                           '{data.reviews_league}',
                                                           '{data.retention_league}',
                                                           '{data.minutes_league}',
                                                           '{data.xp_league}',
                                                           '{data.study_days}',
                                                           '{data.timestamps}');"""
        self.execute_one(query)

    def update_league_data(self, data: DB_League_Data_Schema):
        query = f"""UPDATE {LEAGUES_DATA_TBL}
                    SET streak = '{data.streak}',
                        reviews_today = {data.reviews_league},
                        retention_today = {data.retention_today},
                        minutes_today = {data.minutes_today},
                        xp_today = {data.xp_today},
                        reviews_league = {data.reviews_league},
                        retention_league = {data.retention_league},
                        minutes_league = {data.minutes_league},
                        xp_league = {data.xp_league},
                        study_days = {data.study_days},
                        timestamps = {data.timestamps}
                    WHERE league_id = '{data.league_uuid}' AND
                          username = '{data.username}' AND
                          day = {data.day_over};"""
        self.execute_one(query)

    # get all user data by a league id
    def get_league_data_by_day(self, league_info: DB_League_Info_Schema, day: int = 0) -> list[LeagueUserStats]:
        if day == 0:
            day = get_last_day(league_info.start_time, league_info.duration)
        query = f"""SELECT * FROM {LEAGUES_DATA_TBL} WHERE league_id = '{league_info.league_uuid}' AND day = '{day}';"""
        results = self.execute_fetchall(query)
        return Database.return_league_user_stats(results)

    def get_league_user_data_by_day(self, league_uuid: str, username: str, day: int) -> DB_League_Data_Schema:
        query = f"""SELECT * FROM {LEAGUES_DATA_TBL} WHERE league_id = '{league_uuid}' AND day = {day} AND username = '{username}';"""
        result = self.execute_fetchone(query)
        return Database.return_db_league_data_schema(result)

    def sync_league_data(self, data: DB_League_Data_Schema):
        user_league_data = self.get_league_user_data_by_day(
            data.league_uuid, data.username, data.day_over)
        if user_league_data:
            self.update_league_data(data)
        else:
            self.insert_league_data(data)

    def _create_tables(self):
        try:
            self._create_users_auth_table()
            self._create_leagues_info_table()
            self._create_leagues_users_table()
            self._create_leagues_data_table()
            self._create_user_achievement_table()
        except:
            print("Create table error !")

    def _create_users_auth_table(self):
        query = f"""CREATE TABLE IF NOT EXISTS {USER_TBL} (
            username TEXT PRIMARY KEY,
            password TEXT,
            email TEXT,
            role INTEGER
        )"""
        self.cur.execute(query)
        self.con.commit()

    def _create_leagues_info_table(self):
        query = f"""CREATE TABLE IF NOT EXISTS {LEAGUES_INFO_TBL} (
            id TEXT PRIMARY KEY,
            name TEXT,
            season INTEGER,
            start_time INTEGER,
            duration INTEGER,
            reset INTEGER
        )"""
        self.cur.execute(query)
        self.con.commit()

    def _create_leagues_users_table(self):
        query = f"""CREATE TABLE IF NOT EXISTS {LEAGUES_USER_TBL} (
            league_id TEXT,
            username TEXT,
            league_role INTEGER,
            FOREIGN KEY(league_id) REFERENCES leagues_info(id),
            FOREIGN KEY(username) REFERENCES users(username)
        )"""
        self.cur.execute(query)
        self.con.commit()

    def _create_leagues_data_table(self):
        query = f"""CREATE TABLE IF NOT EXISTS {LEAGUES_DATA_TBL} (
            league_id TEXT,
            username TEXT,
            day INTEGER,
            streak INTEGER,
            reviews_today INTEGER,
            retention_today REAL,
            minutes_today INTEGER,
            xp_today REAL,
            reviews_league INTEGER,
            retention_league REAL,
            minutes_league INTEGER,
            xp_league REAL,
            study_days INTEGER,
            timestamps INTEGER,
            FOREIGN KEY(league_id) REFERENCES leagues_info(id),
            FOREIGN KEY(username) REFERENCES users(username)
        )"""
        self.cur.execute(query)
        self.con.commit()

    def _create_user_achievement_table(self):
        query = f"""CREATE TABLE IF NOT EXISTS {ACHIEVEMENT_TBL} ( 
            username TEXT,
            league_name TEXT,
            gold INTEGER,
            silver INTEGER,
            bronze INTEGER,
            FOREIGN KEY(league_name) REFERENCES leagues_info(name),
            FOREIGN KEY(username) REFERENCES users(username)
        )"""
        self.cur.execute(query)
        self.con.commit()
