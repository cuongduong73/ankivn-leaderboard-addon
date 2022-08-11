from operator import mod
from tabnanny import check
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from security.hashing import Hash
from typing import List
import oauth2

from form import schemas, models
from database import get_db
from routers.helper import check_permission, create_user_info_response

ADMIN_USERS = ["admin"]

router = APIRouter(
    prefix="/user",
    tags=["Users"]
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.CreateUserResponse)
def create(request: schemas.CreateUserRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == request.username).first()
    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"User {request.username} has already existed !")
    user = db.query(models.User).filter(models.User.email == request.email).first()
    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"Email {request.email} has already existed !")

    new_user = models.User(username=request.username,
                           password=Hash.bcrypt(request.password),
                           email=request.email,
                           role=0,gold=0,silver=0,bronze=0)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.put("/", status_code=status.HTTP_202_ACCEPTED)
def set_role(request: schemas.SetUserRoleRequest, db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_current_user)):
    if current_user not in ADMIN_USERS:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"User {current_user} doesn't have this permission !")   
    # check_permission(current_user, db)     
    user = db.query(models.User).filter(models.User.username == request.username)
    if not user.first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"User {request.username} isn't existed !")

    user.update({"role": request.role})
    db.commit()
    return {"status": 1}


@router.get("/{id}", status_code=status.HTTP_200_OK, response_model=schemas.GetUserResponse)
def get(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User {id} is not existed !")
    return create_user_info_response(user, db)

@router.get("/", status_code=status.HTTP_200_OK, response_model=List[schemas.GetUserResponse])
def get_all(db: Session = Depends(get_db)):
    users = db.query(models.User).all()

    responses: List[schemas.GetUserResponse] = []
    for user in users:
        responses.append(create_user_info_response(user, db))
    return responses

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(id: int, db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_current_user)):
    check_permission(current_user, db)
    user = db.query(models.User).filter(id == models.User.id)
    if not user.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User {id} is not existed !")  
    league_user = db.query(models.LeagueUser).filter(id == models.LeagueUser.user_id)
    if league_user.first():
        league_user.delete(synchronize_session=False)
        db.commit()
    
    league_data = db.query(models.LeagueData).filter(id == models.LeagueData.user_id)
    if league_data.first():
        league_data.delete(synchronize_session=False)
        db.commit()
          
    user.delete(synchronize_session=False)
    db.commit()
    return {"status": 1}
