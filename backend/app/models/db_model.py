from pydantic import BaseModel, EmailStr, root_validator, Field, validator
from typing import Dict
import uuid
from ..calculate import calculate_xp, get_time_stamps


class DB_User_Schema(BaseModel):
    username: str = Field(...)
    password: str = Field(...)
    email: EmailStr = Field(...)
    role: int = 0


class DB_League_Info_Schema(BaseModel):
    league_uuid: str = uuid.uuid4().hex[:8]
    league_name: str = Field(...)
    season: int = Field(...)
    start_time: int = Field(...)
    duration: int = Field(...)
    reset: int = Field(...)


class DB_League_User_Schema(BaseModel):
    league_uuid: str = Field(...)
    username: str = Field(...)
    role: int = 0


class DB_League_Data_Schema(BaseModel):
    league_uuid: str = Field(...)
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

    @root_validator
    def compute_xp(cls, values) -> Dict:
        values["xp_league"] = calculate_xp(reviews=values["reviews_league"],
                                           retention=values["retention_league"],
                                           minutes=values["minutes_league"],
                                           study_days=values["study_days"],
                                           day_over=values["day_over"])
        values["xp_today"] = calculate_xp(reviews=values["reviews_today"],
                                          retention=values["retention_today"],
                                          minutes=values["minutes_today"])
        return values


class DB_Achievement_Schema(BaseModel):
    username: str = Field(...)
    league_name: str = Field(...)
    gold: int = Field(...)
    silver: int = Field(...)
    bronze: int = Field(...)
