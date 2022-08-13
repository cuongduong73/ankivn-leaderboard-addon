from sqlalchemy.orm import Session
from form import models, schemas
from fastapi import status, HTTPException
from utils import get_timestamp, calculate_timedelta

ROLE_USER = 0
ROLE_MOD = 1
ROLE_DEPUTY_AD = 2
ROLE_ADMIN = 5

def create_league_info_response(info, db) -> schemas.LeagueInfoResponse:
    users = []
    for i in info.users:
        user = db.query(models.User).filter(i.user_id == models.User.id).first()
        league_user = db.query(models.LeagueUser).filter(i.user_id == models.LeagueUser.user_id).first()
        # users.append(schemas.LeagueUser(**user.__dict__))
        users.append(schemas.LeagueUser(username=user.username, 
                                        gold=user.gold, 
                                        silver=user.silver, 
                                        bronze=user.bronze,
                                        role=league_user.role))
    response = schemas.LeagueInfoResponse(name=info.name,
                                          season=info.season,
                                          start_time=info.start_time,
                                          duration=info.duration,
                                          reset=info.reset,
                                          id=info.id,
                                          users=users)
    return response

def create_league_data_response(league_info, db) -> schemas.LeagueDataResponse:
    timestamp = get_timestamp()
    today = calculate_timedelta(league_info.start_time, timestamp) 
    if today < 0:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail=f"League {league_info.name} - ss{league_info.season} has not started !")
    day = min(today, league_info.duration)       

    league_data = db.query(models.LeagueData).filter(
                                # models.LeagueData.day == day).filter(
                                    models.LeagueData.league_id == league_info.id).order_by(models.LeagueData.xp_league.desc())
    if not league_data.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"League {league_info.name} - ss{league_info.season} - day {day} data is empty !")

    users_data = []
    for data in league_data:
        user = db.query(models.User).filter(models.User.id == data.user_id).first()
        info = schemas.SyncResponse(username=user.username,
                                    gold=user.gold,
                                    silver=user.silver,
                                    bronze=user.bronze,
                                    streak=data.streak,
                                    study_days=data.study_days,
                                    day_over=day, 
                                    xp=data.xp_league, 
                                    timestamp=data.timestamp,
                                    reviews=data.reviews_league,
                                    retention=data.retention_league,
                                    minutes=data.minutes_league)
        users_data.append(info)

    response = schemas.LeagueDataResponse(league_id=league_info.id,
                                          name=league_info.name,
                                          season=league_info.season,
                                          users=users_data)
    return response


# def check_permission(username: str, db: Session):
#     current_user_info = db.query(models.User).filter(username == models.User.username).first()
#     if not current_user_info: 
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                     detail=f"User {username} is not existed !")
#     if current_user_info.role <= 1:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
#                     detail=f"User {username} doesn't have this permission !")
#     return current_user_info

def check_user_existed_by_name(username: str, db: Session):
    user_info = db.query(models.User).filter(username == models.User.username)
    if not user_info.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User {username} is not existed !")
    return user_info

def check_user_existed_by_id(id: int, db: Session):
    user_info = db.query(models.User).filter(id == models.User.id)
    if not user_info.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User id {id} is not existed !")
    return user_info

def create_user_info_response(user: models.User, db: Session) -> schemas.GetUserResponse:
    leagues = []
    for i in user.leagues:
        if i.role >= 1:
            league_info = db.query(models.League).filter(i.league_id == models.League.id).first()
            leagues.append(schemas.LeagueInfoRequest(name=league_info.name, season=league_info.season))
    


    achievements = schemas.Achievements(gold=user.gold, silver=user.silver, bronze=user.bronze)
    response = schemas.GetUserResponse(username=user.username,
                                        email=user.email,
                                        role=user.role,
                                        id=user.id,
                                        achievements=achievements,
                                        leagues=leagues)
    return response

