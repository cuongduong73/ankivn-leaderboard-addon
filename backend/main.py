from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.calculate import get_last_day
from app.models.auth_model import *
from app.models.db_model import *
from app.models.sync_model import *
from app.database import Database
from app.auth.jwt_handler import encodeJWT
from app.auth.jwt_bearer import get_current_user
from app.auth.security import verify_password

app = FastAPI()
db = Database()


@app.on_event("startup")
async def database_connect():
    db.connect_database()


@app.on_event("shutdown")
async def database_disconnect():
    db.release_database()


@app.get("/", tags=["test"])
async def get_root():
    return {"msg": "hello world"}

# User signup [ create a new user ]


@app.post("/user/signup", tags=["user"])
async def user_signup(user_info: UserSignUpSchema):
    user_by_name = db.get_user_info_by_name(user_info.username)
    if user_by_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="User {} is already existed".format(user_info.username))
    user_by_mail = db.get_user_info_by_email(user_info.email)
    if user_by_mail:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Email {} is already existed".format(user_info.email))
    db_data = user_info.convert_to_db()
    db.insert_user_info(db_data)
    return {"status": True}


# User login [ return access_token if username/password is correct ]
@app.post("/user/login", tags=["user"])
async def user_login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = db.get_user_info_by_name(form_data.username)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User {} not existed".format(form_data.username))

    result = verify_password(form_data.password, user.password)
    if not result:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Password is not correct")
    response = encodeJWT(form_data.username)
    return response

# TODO: Add JWTBearer depend


@app.post("/leagues/create_league", tags=["leagues"])
async def create_league(req: LeagueCreateRequest):
    league_info = req.league_info
    league = db.get_league_info_by_name_and_season(
        league_info.league_name, league_info.season)
    if league:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f'League: {league_info.league_name}, ss: {league_info.season} is already existed!')
    db.insert_league_info(league_info.convert_to_db())
    return {"status": True}

# TODO: Add JWTBearer depend


@app.post("/leagues/join_league", tags=["leagues"])
async def join_league(req: LeagueUserApplyRequest):
    league_info = req.league_info
    league = db.get_league_info_by_name_and_season(
        league_info.league_name, league_info.season)
    if not league:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'League: {league_info.league_name}, ss: {league_info.season} not found!')
    user_league_info = DB_League_User_Schema(league_uuid=league.league_uuid,
                                             username=req.username)
    user = db.get_user_info_in_league(user_league_info)
    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f'User: {user.username} has already joined in {league_info.league_name} - ss{league_info.season}')
    db.insert_user_to_league(user_league_info)

    return {"status": True}

# TODO: Add JWTBearer depend


@app.post("/leagues/set_role", tags=["leagues"])
async def set_role_league(req: LeagueUserApproveRequest):
    league_info = req.league_info
    league = db.get_league_info_by_name_and_season(
        league_info.league_name, league_info.season)
    if not league:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'League: {league_info.league_name}, ss: {league_info.season} not found!')
    db.update_user_role_of_league(DB_League_User_Schema(league_uuid=league.league_uuid,
                                                        username=req.username,
                                                        role=req.role))
    return {"status": True}


@app.get("/leagues/id", tags=["leagues"])
async def get_league_info_by_id(league_id: str):
    league_info = db.get_league_info_by_id(league_id)
    if league_info:
        users_data = db.get_league_data_by_day(league_info)
        if not users_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f'Resource not found!')

    return LeagueStatsResponse(league_info=LeagueInfoDataRequest(league_uuid=league_info.league_uuid,
                                                                 league_name=league_info.league_name,
                                                                 season=league_info.season,
                                                                 start_time=league_info.start_time,
                                                                 duration=league_info.duration,
                                                                 reset=league_info.reset,
                               league_users_data=users_data).dict())


@app.get("/leagues", tags=["leagues"])
async def get_leagues():
    leagues = db.get_all_leagues_info()
    return LeaguesInfo(leagues=leagues).dict()


@app.post("/sync", tags=["sync"])
async def sync_study_data(data: UserSyncUpRequest, user_verify: str = Depends(get_current_user)):
    if user_verify != data.league_data.username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"This user {user_verify} can't access resource!")
    league = db.get_league_info_by_name_and_season(
        data.league_info.league_name, data.league_info.season)
    user_league_info = DB_League_User_Schema(
        league_uuid=league.league_uuid, username=data.league_data.username)
    user = db.get_user_info_in_league(user_league_info)
    if not user or user.role < 1:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"User {data.league_data.username} have not joined {data.league_info.league_name} - ss{data.league_info.season}")
    day = get_last_day(league.start_time, league.duration)
    if day != data.league_data.day_over:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Overdue data !!!")

    db.sync_league_data(DB_League_Data_Schema(league_uuid=league.league_uuid,
                                                    username=data.league_data.username,
                                                    day_over=data.league_data.day_over,
                                                    streak=data.league_data.streak,
                                                    reviews_today=data.league_data.reviews_today,
                                                    retention_today=data.league_data.retention_today,
                                                    minutes_today=data.league_data.minutes_today, 
                                                    reviews_league=data.league_data.reviews_league,
                                                    retention_league=data.league_data.retention_league,
                                                    minutes_league=data.league_data.minutes_league,
                                                    study_days=data.league_data.study_days))
    
    return {"status": True}
