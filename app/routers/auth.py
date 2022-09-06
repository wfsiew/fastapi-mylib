from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from ..models import UserOut
from ..services.user import UserService
from ..constants import SECRET, ALGORITHM
from ..dependencies import get_user_service, get_current_user, Token
import logging

router = APIRouter(tags=['auth'])
logger = logging.getLogger(__name__)


async def authenticate_user(username: str, password: str, userService: UserService):
    user = await userService.find_by_username(username)
    if not user:
        return False
    if not userService.validate_credentials(user, password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=5)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET, algorithm=ALGORITHM)
    return encoded_jwt


@router.post('/o/token', response_model=Token, name='Login')
async def login_for_access_token(data: OAuth2PasswordRequestForm = Depends(), userService: UserService = Depends(get_user_service)):
    try:
        user = await authenticate_user(data.username, data.password, userService)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        token_expires = timedelta(days=5)
        token = create_access_token(
            data={'sub': user.username}, expires_delta=token_expires
        )
        return {'token': token, 'type': 'bearer'}
    
    except Exception as e:
        logger.error(e)
        raise

@router.get('/api/current-user', response_model=UserOut)
async def user_details(current_user: UserOut = Depends(get_current_user)):
    try:
        return current_user
    
    except Exception as e:
        logger.error(e)
        raise
