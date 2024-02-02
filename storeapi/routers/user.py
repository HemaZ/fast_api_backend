import logging

from fastapi import APIRouter, HTTPException, status, Request

from storeapi.database import database, user_table
from storeapi.models.user import UserIn
from storeapi.security import (
    get_user,
    get_password_hash,
    auth_user,
    create_access_token,
    create_confirmation_token,
    get_subject_for_token_type,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/register", status_code=201)
async def register(user: UserIn, req: Request):
    if await get_user(user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )
    hashed_pass = get_password_hash(user.password)
    query = user_table.insert().values(
        email=user.email, name=user.name, password=hashed_pass
    )
    logger.debug(query)
    await database.execute(query)
    return {
        "detail": "User created Please confirm",
        "confirmation_url": req.url_for(
            "confirm_user", token=create_confirmation_token(user.email)
        ),
    }


@router.post("/token")
async def login(user: UserIn):
    user = await auth_user(user.email, user.password)
    access_token = create_access_token(user.email)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/confirm/{token}")
async def confirm_user(token: str):
    email = get_subject_for_token_type(token, "confirmation")
    query = (
        user_table.update().where(user_table.c.email == email).values(confirmed=True)
    )
    logger.debug(query)
    await database.execute(query)
    return {"detail": "User confirmed"}
