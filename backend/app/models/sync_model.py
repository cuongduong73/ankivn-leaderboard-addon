from pydantic import BaseModel, Field, root_validator
from ..calculate import calculate_xp, get_time_stamps
from typing import Dict
from .db_model import DB_League_Info_Schema

class LeagueInfoDataRequest(BaseModel):
    league_uuid: str = ""
    league_name: str = Field(...)
    season: int = Field(...)
    start_time: int = 0
    duration: int = 0
    reset: int = 0

    def convert_to_db(self) -> DB_League_Info_Schema:
        return DB_League_Info_Schema(league_name=self.league_name,
                                     season=self.season,
                                     start_time=self.start_time,
                                     duration=self.duration,
                                     reset=self.reset)
class LeagueUserStats(BaseModel):
    username: str = Field(...)
    day_over: int = Field(...)
    streak: int = Field(...)
    reviews_today: int = Field(...)
    retention_today: float = Field(...)
    minutes_today: int = Field(...)
    xp_today: float = 0.0
    reviews_league: int = Field(...)
    retention_league: float = Field(...)
    minutes_league: int = Field(...)
    xp_league: float = 0.0
    study_days: int = Field(...)
    timestamps: int = get_time_stamps()

class UserSyncUpRequest(BaseModel):
    league_data: LeagueUserStats = Field(...)
    league_info: LeagueInfoDataRequest = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "league_info": {
                    "league_name": "ankivn",
                    "season": 1
                },
                "league_data": {
                    "username": "chipheo",
                    "day_over": 10,
                    "streak": 9,
                    "reviews_today": 100,
                    "retention_today": 92.2,
                    "minutes_today": 100,
                    "reviews_league": 1023,
                    "retention_league": 95.3,
                    "minutes_league": 10000,
                    "study_days": 9,
                }
            }
        }

class LeagueStatsResponse(BaseModel):
    league_info: LeagueInfoDataRequest = Field(...)
    league_users_data: list[LeagueUserStats] = Field(...)

class LeagueStatsRequest(BaseModel):
    league_info: LeagueInfoDataRequest = Field(...)
    class Config:
        schema_extra = {
            "example": {
                "league_info": {
                    "league_name": "ankivn",
                    "season": 1
                }
            }
        }

# create a new league request
class LeagueCreateRequest(BaseModel):
    league_info: LeagueInfoDataRequest = Field(...)
    class Config:
        schema_extra = {
            "example": {
                "league_info": {
                    "league_name": "ankivn",
                    "season": 1,
                    "start_time": 1660035905,
                    "duration": 100,
                    "time": 4
                }
            }
        }

# user request to join a league
class LeagueUserApplyRequest(BaseModel):
    username: str = Field(...)
    league_info: LeagueInfoDataRequest = Field(...)
    class Config:
        schema_extra = {
            "example": {
                "username": "chipheo",
                "league_info": {
                    "league_name": "ankivn",
                    "season": 1
                }
            }
        }

# approve a user to join a league
class LeagueUserApproveRequest(BaseModel):
    username: str = Field(...)
    league_info: LeagueInfoDataRequest = Field(...)
    role: int = Field(...)
    class Config:
        schema_extra = {
            "example": {
                "username": "chipheo",
                "role": 1,
                "league_info": {
                    "league_name": "ankivn",
                    "season": 1
                }
            }
        }

# get all users in a league
class LeagueGetUsersRequest(BaseModel):
    league_info: LeagueInfoDataRequest = Field(...)
    class Config:
        schema_extra = {
            "example": {
                "league_info": {
                    "league_name": "ankivn",
                    "season": 1
                }
            }
        }

class LeagueUserInfo(BaseModel):
    username: str = Field(...)
    role: int = Field(...)

class LeagueGetUsersResponse(BaseModel):
    league_info: LeagueInfoDataRequest = Field(...)
    users: list[LeagueUserInfo] = Field(...)

class LeaguesInfo(BaseModel):
    leagues: list[DB_League_Info_Schema] = Field(...)


