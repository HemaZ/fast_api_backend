import datetime
import logging
from typing import Annotated, Literal

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


def create_credintials_exception(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def access_token_expire_minutes() -> int:
    return 30


def confirm_token_expire_minutes() -> int:
    return 1440


def create_access_token(email: str):
    logger.debug("Creating access token for the email %s", email)
    expire = datetime.datetime.now() + datetime.timedelta(
        minutes=access_token_expire_minutes()
    )
    jwt_data = {"sub": email, "exp": expire, "type": "access"}
    encoded_jwt = jwt.encode(jwt_data, key=SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_confirmation_token(email: str):
    logger.debug("Creating confirmation token for the email %s", email)
    expire = datetime.datetime.now() + datetime.timedelta(
        minutes=confirm_token_expire_minutes()
    )
    jwt_data = {
        "sub": email,
        "exp": expire,
        "type": "confirmation",
    }
    encoded_jwt = jwt.encode(jwt_data, key=SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_subject_for_token_type(
    token: str, type: Literal["access", "confirmation"]
) -> str:
    try:
        payload = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
    except ExpiredSignatureError as error:
        raise create_credintials_exception("Token has expired") from error
    except JWTError as error:
        raise create_credintials_exception("Invalid token") from error
    email = payload.get("sub")
    if email is None:
        raise create_credintials_exception("Token is missing sub field")
    token_type = payload.get("type")
    if token_type is None or token_type != type:
        raise create_credintials_exception("Token has invalid type")
    return email


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
        raise create_credintials_exception("Invalid Email")
    if not verify_password(password, user.password):
        raise create_credintials_exception("Invalid password")
    if not user.confirmed:
        raise create_credintials_exception("User email is not confirmed")
    return user


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    email = get_subject_for_token_type(token, "access")
    user = await get_user(email)
    if user is None:
        raise create_credintials_exception("Invalid email")
    return user
