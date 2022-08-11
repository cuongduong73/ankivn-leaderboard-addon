from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from form import models, schemas
import oauth2
from utils import calculate_xp, calculate_timedelta,  get_timestamp
from routers.helper import check_permission, create_league_info_response, check_user_existed, create_league_data_response

router = APIRouter(
    prefix="/league",
    tags=["Leagues"]
)

@router.post("/create", response_model=schemas.CreateLeagueResponse)
def create(request: schemas.CreateLeagueRequest, db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_current_user)):
    check_permission(current_user, db)

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

@router.post("/add_user", status_code=status.HTTP_202_ACCEPTED)
def add_user(request: schemas.AddUserRequest, response: Response,db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_current_user)):
    check_permission(current_user, db)
    league_info = db.query(models.League).filter(
        request.league.name == models.League.name).filter(
        request.league.season == models.League.season).first()
    if not league_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"League {request.name} - ss{request.season} is not existed !")

    user_info = check_user_existed(request.username, db)
    league_user_info = db.query(models.LeagueUser).filter(models.LeagueUser.user_id == user_info.id)
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

@router.post("/join", status_code=status.HTTP_202_ACCEPTED)
def submit_join(request: schemas.LeagueInfoRequest, db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_current_user)):
    
    league_info = db.query(models.League).filter(
        request.name == models.League.name).filter(
        request.season == models.League.season).first()
    if not league_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"League {request.name} - ss{request.season} is not existed !")
    
    user_info = check_user_existed(current_user, db)
    league_user_info = db.query(models.LeagueUser).filter(models.LeagueUser.league_id == league_info.id).filter(models.LeagueUser.user_id == user_info.id).first()
    if league_user_info:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                    detail=f"User {current_user} has submitted to join League {request.name} - ss{request.season} !")        
    info = models.LeagueUser(league_id=league_info.id,
                             user_id=user_info.id,
                             role=0)
    db.add(info)
    db.commit()
    db.refresh(info)
    return {"status": 1}

@router.post("/sync", status_code=status.HTTP_201_CREATED)
def sync(request: schemas.SyncRequest, response: Response, db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_current_user)):
    league_info = db.query(models.League).filter(models.League.id == request.league_id).first()
    if not league_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"League id {request.league_id} is not existed !")        
    timestamp = get_timestamp()
    today = calculate_timedelta(league_info.start_time, timestamp)
    if today > league_info.duration:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail=f"League {league_info.name} - ss{league_info.season} has finished !")
    if today < 0:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail=f"League {league_info.name} - ss{league_info.season} has not started !")
    user_info = db.query(models.User).filter(models.User.username == current_user).first()
    _joined = False
    for i in user_info.leagues:
        if i.league_id == request.league_id and i.role >=1:
            _joined = True
            break
    if not _joined:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail=f"User {current_user} has not joined {league_info.name} - ss{league_info.season} yet !")
    xp_league = calculate_xp(reviews=request.reviews_league, 
                             retention=request.retention_league, 
                             minutes=request.minutes_league, 
                             day=today, 
                             study_days=request.study_days)
    xp_day = calculate_xp(reviews=request.reviews_today, 
                          retention=request.retention_today, 
                          minutes=request.minutes_today)

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
    check_permission(current_user, db)
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

        


    


