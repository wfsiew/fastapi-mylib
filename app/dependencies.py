from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel

from .models import UserOut
from .services.user import UserService
from .services.book import BookService
from .constants import SECRET, ALGORITHM


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='o/token')

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

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
        username: str = payload.get('sub')
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = await userService.find_by_username(token_data.username)
    userx = UserOut(id=user.id, username=user.username, roles=user.roles)
    if user is None:
        raise credentials_exception
    return userx