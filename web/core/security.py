from ..db.models import User, UserInDB, Token, TokenData
from ..core.error_handler import RedirectException
from ..db.db import users_collection, blocklist_collection
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer, HTTPBearer,  HTTPAuthorizationCredentials
from fastapi.encoders import jsonable_encoder
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from typing import List, Union
from typing import Optional, Annotated
from fastapi import FastAPI, HTTPException, Request, Depends, status, responses
import jwt
import uuid
import logging
from jwt.exceptions import InvalidTokenError
from fastapi.security.utils import get_authorization_scheme_param
from starlette.authentication import (
    AuthCredentials, AuthenticationBackend, AuthenticationError, SimpleUser
)


SECRET_KEY = "c7d2b1f170dcc6dfaf0fd9981100426c111926578f79d71cc9e3009326666f39"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 2

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[HTTPAuthorizationCredentials]:
        authorization: str = request.cookies.get("access_token")
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise RedirectException(status_code=401, 
                                    detail="INF_Please log in or create an account",
                                    loc = "/register")
            else:
                return None
        # payload = jwt.decode(param, SECRET_KEY, algorithms=ALGORITHM)
        payload = decode_token(param)
        if await token_in_blocklist(payload.get('jti')):
            raise RedirectException(status_code=401, 
                                detail="INF_You are logged out. Please log in.",
                                loc = "/login")
        return param


acccess_token_bearer = TokenBearer()


class BearerTokenAuthBackend(AuthenticationBackend):
    """
    This is a custom auth backend class for a middleware
    """
    async def authenticate(self, request):
        authorization: str = request.cookies.get("access_token")
        scheme, param = get_authorization_scheme_param(authorization)
        # if not authorization or scheme.lower() != "bearer":
        #         return None
        try:
            payload = jwt.decode(
            jwt=param,
            key=SECRET_KEY,
            algorithms=[ALGORITHM]
            )
        except:
             return None
        if await token_in_blocklist(payload.get('jti')):
             return None
        return param, SimpleUser(payload['sub'])



def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def get_user(email: str):
    user = await users_collection.find_one({"email": email})
    if not user:
        return None
    return UserInDB(
            email=user["email"],
            hashed_password=user["password"],
        )


async def authenticate_user(username: str, password: str):
    user = await get_user(email=username)
    user = jsonable_encoder(user)
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    return user


def create_access_token(data: str, expires_delta: Union[timedelta, None] = None):
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    payload = {
        "sub": data,
        "exp": expire,
        "jti": str(uuid.uuid4())
    }
    encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         # payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         payload = decode_token(token)
#         email: str = payload.get("sub")
#         if email is None:
#             raise credentials_exception
#         token_data = TokenData(email=email)
#     except InvalidTokenError:
#         raise credentials_exception
#     user = await get_user(email=token_data.email)
#     if user is None:
#         raise credentials_exception
#     return user


def decode_token(token: str) -> dict:
    try:
        token_data = jwt.decode(
            jwt=token,
            key=SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        return token_data
    except jwt.ExpiredSignatureError:
        # raise HTTPException(status_code=302, 
        #                     detail="ERR_Your session expired, please log in.",
        #                     headers = {"Location": "/login"})
        raise RedirectException(status_code=401, 
                                    detail="ERR_Your session expired, please log in.",
                                    loc = "/login")
    except Exception as e:
        logging.exception(e)
        return None


async def register_user(user_data: dict):
    # user_data = jsonable_encoder(user_data)
    user_data["password"] = get_password_hash(user_data["password"])
    user = await users_collection.insert_one(user_data)
    new_user = await users_collection.find_one({"_id": user.inserted_id})
    return new_user


async def add_jti_to_blocklist(jti: str) -> None:
    await blocklist_collection.insert_one({"jti": jti, 'createdon': datetime.now()})


async def token_in_blocklist(jti:str) -> bool:
   jti =  await blocklist_collection.find_one({"jti": jti})
   return jti is not None
