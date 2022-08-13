from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from routers.helper import check_user_existed_by_name
from security.hashing import Hash

from database import get_db
from form import models 
from security import jwt_token 

router = APIRouter(tags=["Authentication"])

@router.post("/login")
def login(request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user_info = check_user_existed_by_name(request.username, db).first()
    if not Hash.verify(user_info.password, request.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"Incorrected password")

    access_token = jwt_token.create_access_token(data={"sub": user_info.username})
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
    
    



