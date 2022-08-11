from operator import mod
from fastapi import HTTPException, status, Depends, APIRouter, Response
from sqlalchemy.orm import Session
from form import schemas, models
from database import get_db
import oauth2
from routers.helper import check_permission


router = APIRouter(
    prefix="/achievement",
    tags=["Achievement"]
)

@router.put("/", status_code=status.HTTP_202_ACCEPTED, response_model=schemas.SetUserAchievementResponse)
def update(request: schemas.SetUserAchievementRequest, db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_current_user)):
    check_permission(current_user, db)

    user_info = db.query(models.User).filter(models.User.username == request.username)
    if not user_info.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User {request.username} is not existed !")
    achievements = schemas.Achievements(gold=request.achievements.gold + user_info.first().gold,
                                        silver=request.achievements.silver + user_info.first().silver,
                                        bronze=request.achievements.bronze + user_info.first().bronze)

    user_info.update(achievements.dict())
    db.commit()

    return user_info.first()

