import logging
import datetime
from passlib.context import CryptContext
from jose import jwt
from fastapi import HTTPException, status
from storeapi.database import database, user_table

logger = logging.getLogger(__name__)
SECRET_KEY = "9asfgfdhgjgfj2f5gj4fgj6fjg5fg88sdfsf555555dddddddddasas"
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"])

credintials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail="Couldn't validate user"
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
