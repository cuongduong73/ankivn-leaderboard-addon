from pydantic import BaseModel, Field, EmailStr, validator
from ..validate import validate_username, validate_password
from .db_model import DB_User_Schema
from ..auth.security import get_password_hash

class UserSignUpSchema(BaseModel):
    email: EmailStr = Field(...)
    username: str = Field(...)
    password1: str = Field(...)
    password2: str = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "email": "chipheo@gmail.com",
                "username": "chipheo",
                "password1": "abc@123143",
                "password2": "abc@123143"
            }
        }
    def convert_to_db(self):
        return DB_User_Schema(username=self.username,
                              password=get_password_hash(self.password1),
                              email=self.email)

    @validator("username")
    def check_username(cls, v):
        if not validate_username(v):
            raise ValueError(
                "Username must be [6-20] characters and does not contain special characters")
        return v

    @validator("password1")
    def check_password(cls, v):
        if not validate_password(v):
            raise ValueError(
                "Password must be [8-20] characters, at least one letter and one number")
        return v

    @validator("password2")
    def check_password_match(cls, v, values, **kwargs):
        if 'password1' in values and v != values['password1']:
            raise ValueError('Passwords do not match')
        return v

class UserLoginSchema(BaseModel):
    username: str = Field(...)
    password: str = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "username": "chipheo",
                "password": "abc@123143"
            }
        }


class JWTPayloadSchema(BaseModel):
    username: str = Field(...)
    expired: float = Field(...)


### Testing ###
# try:
#     user = UserSignUpSchema(
#                 email = "chipheo@gmail.com",
#                 username = "chipheo_depzai",
#                 password1 = "abc@123143",
#                 password2 = "abc@123143"
#     )
#     print(user)
# except ValidationError as e:
#     print(e)

# try:
#     user = UserLeagueStatSchema(
#                 username = "test123",
#                 streak = "100",
#                 reviews_today = 100,
#                 retention_today = 98.0,
#                 minutes_today = 30.6,
#                 reviews_league = 9999,
#                 retention_league = 99.3,
#                 minutes_league = 2019.2,
#                 study_days = 20,
#                 day_over = 23
#     )
#     print(user)
# except ValidationError as e:
#     print(e)
