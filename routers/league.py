from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from env import MIN_ADDON_VERSION
from form import models, schemas
import oauth2
from utils import calculate_xp, get_timestamp, calc_day_from
from routers.helper import ROLE_MOD, create_league_info_response, check_user_existed_by_name, create_league_data_response
from packaging import version

router = APIRouter(
    prefix="/league",
    tags=["Leagues"]
)

@router.post("/create", response_model=schemas.CreateLeagueResponse, status_code=status.HTTP_201_CREATED)
def create(request: schemas.CreateLeagueRequest, db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_current_user)):
    current_user_info = check_user_existed_by_name(current_user, db).first()
    if current_user_info.role < ROLE_MOD:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                    detail=f"User {current_user} doesn't have this permission !")            

    league_info = db.query(models.League).filter(request.name == models.League.name).filter(request.season == models.League.season).first()
    if league_info: 
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"League {request.name} - ss{request.season} has already existed !")       
    new_league = models.League(**request.dict())
    db.add(new_league)
    db.commit()
    db.refresh(new_league)
    return new_league

@router.get("/", status_code=status.HTTP_200_OK, response_model=List[schemas.LeagueInfoResponse])
def show(db: Session = Depends(get_db)):
    # Return all leagues information
    infos = db.query(models.League).all()
    responses: List[schemas.LeagueInfoResponse]= []
    for info in infos:
        responses.append(create_league_info_response(info, db))
    return responses


@router.get('/{id}', status_code=status.HTTP_200_OK, response_model=schemas.LeagueInfoResponse)
def show_by_id(id: int, db: Session = Depends(get_db)):
    # Return league information (name, season, start_time, duration, reset)
    info = db.query(models.League).filter(models.League.id == id).first()
    if not info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"League {id} is not existed !")
    return create_league_info_response(info, db)


@router.post("/info", status_code=status.HTTP_200_OK, response_model=schemas.LeagueInfoResponse)
def show_by_name(request: schemas.LeagueInfoRequest, db: Session = Depends(get_db)):
    info = db.query(models.League).filter(models.League.name == request.name).filter(
        models.League.season == request.season).first()
    if not info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"League {request.name} - ss{request.season} is not existed !")

    return create_league_info_response(info, db)

@router.post("/add_user/name", status_code=status.HTTP_202_ACCEPTED)
def add_user_by_name(request: schemas.AddUserByNameRequest, response: Response,db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_current_user)):
    current_user_info = check_user_existed_by_name(current_user, db).first()
    if current_user_info.role < ROLE_MOD:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                    detail=f"User {current_user} doesn't have this permission !")        
    league_info = db.query(models.League).filter(
        request.league.name == models.League.name).filter(
        request.league.season == models.League.season).first()
    if not league_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"League {request.name} - ss{request.season} is not existed !")

    user_info = check_user_existed_by_name(request.username, db).first()
    league_user_info = db.query(models.LeagueUser).filter(models.LeagueUser.user_id == user_info.id).filter(models.LeagueUser.league_id == league_info.id)
    info = models.LeagueUser(league_id=league_info.id,
                        user_id=user_info.id,
                        role=1)
    if league_user_info.first():
        response.status_code = status.HTTP_202_ACCEPTED
        league_user_info.update({"role": 1})
        db.commit()
    else:
        response.status_code = status.HTTP_201_CREATED        
        db.add(info)
        db.commit()
        db.refresh(info)
    return {"status": 1}

@router.post("/add_user/id", status_code=status.HTTP_202_ACCEPTED)
def add_user_by_id(request: schemas.AddUserByIDRequest, response: Response,db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_current_user)):
    current_user_info = check_user_existed_by_name(current_user, db).first()
    if current_user_info.role < ROLE_MOD:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                    detail=f"User {current_user} doesn't have this permission !")        
    league_info = db.query(models.League).filter(request.id == models.League.id).first()
    if not league_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"League id {request.id} is not existed !")

    user_info = check_user_existed_by_name(request.username, db).first()
    league_user_info = db.query(models.LeagueUser).filter(models.LeagueUser.user_id == user_info.id).filter(models.LeagueUser.league_id == request.id)
    info = models.LeagueUser(league_id=league_info.id,
                        user_id=user_info.id,
                        role=1)
    if league_user_info.first():
        response.status_code = status.HTTP_202_ACCEPTED
        league_user_info.update({"role": 1})
        db.commit()
    else:
        response.status_code = status.HTTP_201_CREATED        
        db.add(info)
        db.commit()
        db.refresh(info)
    return {"status": 1}

@router.post("/remove_user/id", status_code=status.HTTP_202_ACCEPTED)
def remove_user_by_id(request: schemas.AddUserByIDRequest, response: Response, db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_current_user)):
    current_user_info = check_user_existed_by_name(current_user, db).first()
    if current_user_info.role < ROLE_MOD:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                    detail=f"User {current_user} doesn't have this permission !")        
    league_info = db.query(models.League).filter(request.id == models.League.id).first()
    if not league_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"League id {request.id} is not existed !")
    user_info = check_user_existed_by_name(request.username, db).first()
    league_user_info = db.query(models.LeagueUser).filter(models.LeagueUser.user_id == user_info.id).filter(models.LeagueUser.league_id == request.id)
    if not league_user_info.first():
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail=f"User {user_info.username} has not joined {league_info.name} - ss{league_info.season} yet !")
    league_user_info.update({"role": 0})
    db.commit()
    league_user_data = db.query(models.LeagueData).filter(models.LeagueData.league_id == league_info.id).filter(models.LeagueData.user_id == user_info.id)
    if league_user_data:
        league_user_data.delete(synchronize_session=False)
    return {"status": 1}      

@router.post("/join", status_code=status.HTTP_202_ACCEPTED)
def submit_join_by_name(request: schemas.LeagueInfoRequest, db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_current_user)):
    league_info = db.query(models.League).filter(
        request.name == models.League.name).filter(
        request.season == models.League.season).first()
    if not league_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"League {request.name} - ss{request.season} is not existed !")
    
    user_info = check_user_existed_by_name(current_user, db).first()
    league_user_info = db.query(models.LeagueUser).filter(models.LeagueUser.league_id == league_info.id).filter(models.LeagueUser.user_id == user_info.id).first()
    if league_user_info:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                    detail=f"User {current_user} has submitted to join {request.name} - ss{request.season} !")        
    info = models.LeagueUser(league_id=league_info.id,
                             user_id=user_info.id,
                             role=0)
    db.add(info)
    db.commit()
    db.refresh(info)
    return {"status": 1}

@router.get("/join/{id}", status_code=status.HTTP_202_ACCEPTED)
def submit_join_by_id(id: int, db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_current_user)):
    league_info = db.query(models.League).filter(id == models.League.id).first()
    if not league_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"League ID {id} is not existed !")
    
    user_info = check_user_existed_by_name(current_user, db).first()
    league_user_info = db.query(models.LeagueUser).filter(models.LeagueUser.league_id == league_info.id).filter(models.LeagueUser.user_id == user_info.id).first()
    if league_user_info:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                    detail=f"User {current_user} has submitted to join this challenge!")        
    info = models.LeagueUser(league_id=league_info.id,
                             user_id=user_info.id,
                             role=0)
    db.add(info)
    db.commit()
    db.refresh(info)
    return {"status": 1}

@router.post("/sync", status_code=status.HTTP_201_CREATED)
def sync(request: schemas.SyncRequest, response: Response, db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_current_user)):
    if version.parse(MIN_ADDON_VERSION) > version.parse(request.version):
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                    detail="Your addon version is out of date, update addon and try again !")  
    league_info = db.query(models.League).filter(models.League.id == request.league_id).first()
    if not league_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"League id {request.league_id} is not existed !")        
    timestamp = get_timestamp()
    start_timestamp = league_info.start_time
    end_timestamp = league_info.start_time + league_info.duration * 60 * 60 * 24
    if timestamp > end_timestamp:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail=f"League {league_info.name} - ss{league_info.season} has finished !")
    if timestamp < start_timestamp:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail=f"League {league_info.name} - ss{league_info.season} has not started !")
    user_info = db.query(models.User).filter(models.User.username == current_user).first()
    league_user_info = db.query(models.LeagueUser).filter(models.LeagueUser.user_id == user_info.id).filter(models.LeagueUser.league_id == request.league_id)
    if not league_user_info.first() or league_user_info.first().role < 1:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail=f"User {user_info.username} has not joined {league_info.name} - ss{league_info.season} yet !")
    # _joined = False
    # for i in user_info.leagues:
    #     if i.league_id == request.league_id and i.role >=1:
    #         _joined = True
    #         break
    # if not _joined:
    #     raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
    #                         detail=f"User {current_user} has not joined {league_info.name} - ss{league_info.season} yet !")
    today = calc_day_from(start_timestamp, timestamp)
    xp_league = calculate_xp(reviews=request.reviews_league, 
                             retention=request.retention_league, 
                             minutes=request.minutes_league, 
                             day=today, 
                             study_days=request.study_days)
    xp_day = calculate_xp(reviews=request.reviews_today, 
                          retention=request.retention_today, 
                          minutes=request.minutes_today)
    if request.minutes_today >= league_info.constraint:
        league_data = db.query(models.LeagueData).filter(
    #                               models.LeagueData.day == today).filter(                    # Add data for days
                                        models.LeagueData.user_id == user_info.id).filter(
                                            models.LeagueData.league_id == request.league_id)
        new_league_data = models.LeagueData(user_id=user_info.id,
                                            league_id=request.league_id,
                                            day=today,
                                            streak=request.streak,
                                            study_days=request.study_days,
                                            reviews_today=request.reviews_today,
                                            retention_today=request.retention_today,
                                            minutes_today=request.minutes_today,
                                            reviews_league=request.reviews_league,
                                            retention_league=request.retention_league,
                                            minutes_league=request.minutes_league,
                                            xp_today=xp_day,
                                            xp_league=xp_league,
                                            timestamp=timestamp)
        if not league_data.first():
            db.add(new_league_data) 
            db.commit()
            db.refresh(new_league_data) 
            response.status_code = status.HTTP_201_CREATED  
        else:
            new_update_data = schemas.LeagueData(**new_league_data.__dict__)
            league_data.update(new_update_data.dict())
            db.commit()
            response.status_code = status.HTTP_202_ACCEPTED
    else:
        # Not study enough time T.B.D
        pass

    return {"status": 1}

@router.get("/data/{id}", status_code=status.HTTP_200_OK, response_model=schemas.LeagueDataResponse)
def get(id: int, db: Session = Depends(get_db)):
    league_info = db.query(models.League).filter(models.League.id == id).first()
    if not league_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"League id {id} is not existed !")     

    return create_league_data_response(league_info, db)

@router.post("/data", status_code=status.HTTP_200_OK, response_model=schemas.LeagueDataResponse)
def get(request: schemas.LeagueDataRequest, db: Session = Depends(get_db)):
    league_info = db.query(models.League).filter(models.League.name == request.name).filter(models.League.season == request.season).first()
    if not league_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"League {request.name} - ss{request.season} is not existed !")     

    return create_league_data_response(league_info, db)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(id: int, db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_current_user)):
    current_user_info = check_user_existed_by_name(current_user, db).first()
    if current_user_info.role < ROLE_MOD:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                    detail=f"User {current_user} doesn't have this permission !")        
    league = db.query(models.League).filter(id == models.League.id)
    if not league.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"League {id} is not existed !")  
    league_user = db.query(models.LeagueUser).filter(id == models.LeagueUser.league_id)
    if league_user.first():
        league_user.delete(synchronize_session=False)
        db.commit()
    
    league_data = db.query(models.LeagueData).filter(id == models.LeagueData.league_id)
    if league_data.first():
        league_data.delete(synchronize_session=False)
        db.commit()
          
    league.delete(synchronize_session=False)
    db.commit()
    return {"status": 1}

        


    


