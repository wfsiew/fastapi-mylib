from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from app.models import UserOut
from app.services.user import UserService
from app.constants import SECRET, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES
from app.dependencies import get_user_service, get_current_user, Token
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

def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {'exp': expires_delta, 'sub': subject}
    encoded_jwt = jwt.encode(to_encode, SECRET, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(subject: str, expires_delta: timedelta | None = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode = {'exp': expires_delta, 'sub': subject}
    encoded_jwt = jwt.encode(to_encode, SECRET, algorithm=ALGORITHM)
    return encoded_jwt


@router.post('/o/token', response_model=Token, name='Login')
async def login_for_access_token(data: OAuth2PasswordRequestForm = Depends(), userService: UserService = Depends(get_user_service)):
    try:
        user = await authenticate_user(data.username, data.password, userService)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Incorrect username or password',
                headers={'WWW-Authenticate': 'Bearer'},
            )
        access_token = create_access_token(user.username, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        refresh_token = create_refresh_token(user.username, timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES))
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'type': 'bearer'
        }
    
    except Exception as e:
        logger.error(e)
        raise

@router.get('/api/current-user', response_model=UserOut)
async def user_details(current_user: UserOut = Depends(get_current_user)):
    try:
        return current_user
    
    except HTTPException:
        pass
    
    except Exception as e:
        logger.error(e)
        raise
