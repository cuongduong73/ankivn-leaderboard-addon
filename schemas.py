from pydantic import BaseModel
from typing import List

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(LoginRequest):
    email: str

class StudyInfo(BaseModel):
    streak: int
    study_days: int
    reviews_today: int
    retention_today: float
    minutes_today: int
    reviews_league: int
    retention_league: float
    minutes_league: int

class SyncRequest(StudyInfo):
    league_id: int

class LeagueBase(BaseModel):
    name: str
    season: int

class LeagueInfo(LeagueBase):
    start_time: int
    duration: int
    reset: int

class LeagueUserInfo(BaseModel):
    username: int
    role: int = 0
    gold: int = 0
    silver: int = 0
    bronze: int = 0

class LeagueInfoResponse(LeagueInfo):
    id: int
    users: List[LeagueUserInfo]

class AddUserRequest(BaseModel):
    username: str
    league: LeagueBase

class SetUserRoleRequest(BaseModel):
    username: str
    role: int



    