from typing import List, Optional
from pydantic import BaseModel, EmailStr, validator
from utils import validate_password, validate_username


class CreateUserRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

    class Config():
        schema_extra = {
            "example": {
                "email": "chipheo@vudai.com",
                "username": "chipheo",
                "password": "thino1234"
            }
        }

    @validator("username")
    def check_username(cls, v):
        if not validate_username(v):
            raise ValueError(
                "Username must be [5-20] characters and does not contain special characters")
        return v

    @validator("password")
    def check_password(cls, v):
        if not validate_password(v):
            raise ValueError(
                "Password must be [8-20] characters, at least one letter and one number")
        return v


class CreateUserResponse(BaseModel):
    username: str
    email: EmailStr

    class Config():
        orm_mode = True

class SetUserRoleRequest(BaseModel):
    username: str
    role: int
    class Config():
        schema_extra = {
            "example": {
                "username": "admin",
                "role": 5,
            }
        }



class LeagueInfoRequest(BaseModel):
    name: str
    season: int

    class Config():
        schema_extra = {
            "example": {
                "name": "ankivn",
                "season": 1,
            }
        }


class Achievements(BaseModel):
    gold: int = 0
    silver: int = 0
    bronze: int = 0


class GetUserResponse(CreateUserResponse):
    leagues: List[LeagueInfoRequest] = []
    achievements: Achievements


class CreateLeagueRequest(LeagueInfoRequest):
    start_time: int
    duration: int
    reset: int

    class Config():
        schema_extra = {
            "example": {
                "name": "ankivn",
                "season": 1,
                "start_time": 1659286800,
                "duration": 100,
                "reset": 4
            }
        }


class CreateLeagueResponse(LeagueInfoRequest):
    id: int

    class Config():
        orm_mode = True


class LeagueUser(BaseModel):
    username: str
    role: int
    gold: int
    silver: int
    bronze: int

class LeagueInfoResponse(CreateLeagueRequest):
    id: int
    users: List[LeagueUser] = []

    class Config():
        orm_mode = True


class AddUserRequest(BaseModel):
    username: str
    league: LeagueInfoRequest

    class Config():
        schema_extra = {
            "example": {
                "username": "chipheo",
                "league": {
                    "name": "ankivn",
                    "season": 1,
                }
            }
        }


class TokenData(BaseModel):
    username: str

class SyncRequest(BaseModel):
    league_id: int
    streak: int
    study_days: int
    reviews_today: int
    retention_today: float
    minutes_today: int
    reviews_league: int
    retention_league: float
    minutes_league: int
    xp_today: Optional[float] = 0.0
    xp_league: Optional[float] = 0.0
    timestamp: Optional[int] = 0

    class Config():
        schema_extra = {
            "example": {
                "league_id": 1,
                "streak": 3,
                "study_days": 2,
                "reviews_today": 1000,
                "retention_today": 98.7,
                "minutes_today": 192,
                "reviews_league": 3069,
                "retention_league": 92.7,
                "minutes_league": 602
            }
        }


class SyncResponse(BaseModel):
    username: str
    streak: int
    study_days: int
    day_over: int
    xp: float
    timestamp: int
    reviews: int
    retention: float
    minutes: int
    gold: int
    silver: int
    bronze: int

class LeagueData(BaseModel):
    user_id: int
    league_id: int
    day: int 
    streak: int
    study_days: int
    reviews_today: int
    retention_today: float
    minutes_today: int
    reviews_league: int
    retention_league: float
    minutes_league: int
    xp_today: float
    xp_league: float
    timestamp: int

class LeagueDataResponse(BaseModel):
    league_id: int
    name: str
    season: int
    users: List[SyncResponse]
    class Config():
        orm_mode = True


class LeagueDataRequest(BaseModel):
    name: str
    season: int
    class Config():
        schema_extra = {
            "example": {
                "name": "ankivn",
                "season": 1
            }
        }

class SetUserAchievementRequest(BaseModel):
    username: str
    achievements: Achievements
    class Config():
        schema_extra = {
            "example": {
                "username": "chipheo",
                "achievements": {
                    "gold": 1,
                    "silver": 0,
                    "bronze": 0
                }
            }
        }
class SetUserAchievementResponse(BaseModel):
    username: str
    gold: int
    silver: int
    bronze: int
    class Config():
        orm_mode = True
