import datetime
import logging
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext

from storeapi.database import database, user_table

logger = logging.getLogger(__name__)
SECRET_KEY = "9asfgfdhgjgfj2f5gj4fgj6fjg5fg88sdfsf555555dddddddddasas"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"])

credintials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Couldn't validate user",
    headers={"WWW-Authenticate": "Bearer"},
)


def create_access_token(email: str):
    logger.debug("Creating access token for the email %s", email)
    expire = datetime.datetime.now() + datetime.timedelta(minutes=30)
    jwt_data = {"sub": email, "exp": expire}
    encoded_jwt = jwt.encode(jwt_data, key=SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_pass: str, pass_hash: str) -> bool:
    return pwd_context.verify(plain_pass, pass_hash)


async def get_user(email: str):
    logger.debug("Getting the user with email %s", email)
    query = user_table.select().where(user_table.c.email == email)
    user = await database.fetch_one(query)
    if user:
        return user
    return None


async def auth_user(email: str, password: str):
    logger.debug("Auth user with email: %s", email)
    user = await get_user(email)
    if not user:
        raise credintials_exception
    if not verify_password(password, user.password):
        raise credintials_exception
    return user


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise credintials_exception
    except ExpiredSignatureError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        ) from error
    except JWTError as error:
        raise credintials_exception from error
    user = await get_user(email)
    if user is None:
        raise credintials_exception
    return user
