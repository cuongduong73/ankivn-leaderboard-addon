# Check whether the request is authorized or not [verification of the protected route]

from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from datetime import datetime

from fastapi import Request, HTTPException
from pydantic import ValidationError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer

from .jwt_handler import decodeJWT
from jose.exceptions import JWTError

credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


reuseable_oauth = OAuth2PasswordBearer(
    tokenUrl="/user/login",
    scheme_name="JWT"
) 

async def get_current_user(token: str = Depends(reuseable_oauth)) -> str:
    try:
        payload = decodeJWT(token)
        if datetime.fromtimestamp(payload.expired) < datetime.now():
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload.username
    except(JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    
    
    


# class JWTBearer(HTTPBearer):
#     def __init__(self, auto_error: bool = True):
#         super(JWTBearer, self).__init__(auto_error=auto_error)

#     async def __call__(self, request: Request):
#         credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
#         if credentials:
#             if not credentials.scheme == "Bearer":
#                 raise credentials_exception
#             if not self.verify_jwt(credentials.credentials):
#                 raise credentials_exception
#             return credentials.credentials
#         else:
#             raise credentials_exception

#     def verify_jwt(self, jwtoken: str) -> bool:
#         isTokenValid: bool = False

#         try:
#             payload = decodeJWT(jwtoken)
#         except:
#             payload = None
#         if payload:
#             isTokenValid = True
#         return isTokenValid