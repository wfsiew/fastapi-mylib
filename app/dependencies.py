from datetime import datetime
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel, ValidationError

from .models import UserOut
from .services.user import UserService
from .services.book import BookService
from .constants import SECRET, ALGORITHM


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='o/token', scheme_name='JWT')

class Token(BaseModel):
    token: str
    refresh_token: str
    type: str

class TokenData(BaseModel):
    sub: str | None = None
    exp: str | None = None

async def get_user_service(request: Request) -> UserService:
    return UserService(request.app.state.pool)

async def get_book_service(request: Request) -> BookService:
    return BookService(request.app.state.pool)

async def get_current_user(token: str = Depends(oauth2_scheme), userService: UserService = Depends(get_user_service)) -> UserOut:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        token_data = TokenData(**payload)
        if token_data.sub is None:
            raise credentials_exception
        
        if datetime.fromtimestamp(token_data.exp) < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Token expired',
                headers={'WWW-Authenticate': 'Bearer'},
            )
    except (JWTError, ValidationError):
        raise credentials_exception
    user = await userService.find_by_username(token_data.sub)
    if user is None:
        raise credentials_exception
    userx = UserOut(id=user.id, username=user.username, roles=user.roles)
    return userx