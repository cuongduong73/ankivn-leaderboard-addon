from operator import mod
from fastapi import HTTPException, status, Depends, APIRouter, Response
from sqlalchemy.orm import Session
from form import schemas, models
from database import get_db
import oauth2
from routers.helper import ROLE_DEPUTY_AD, check_user_existed_by_name


router = APIRouter(
    prefix="/achievement",
    tags=["Achievement"]
)

@router.put("/", status_code=status.HTTP_202_ACCEPTED, response_model=schemas.SetUserAchievementResponse)
def update(request: schemas.SetUserAchievementRequest, db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_current_user)):
    current_user_info = check_user_existed_by_name(current_user, db).first()
    if current_user_info.role < ROLE_DEPUTY_AD:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"User {current_user} doesn't have this permission !") 

    user_info = check_user_existed_by_name(request.username, db)
    achievements = schemas.Achievements(gold=request.achievements.gold + user_info.first().gold,
                                        silver=request.achievements.silver + user_info.first().silver,
                                        bronze=request.achievements.bronze + user_info.first().bronze)

    user_info.update(achievements.dict())
    db.commit()

    return user_info.first()

