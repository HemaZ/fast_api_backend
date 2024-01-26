import pytest
from fastapi import HTTPException
from jose import jwt

from storeapi import security


def test_token():
    token = security.create_access_token("123")
    assert {"sub": "123"}.items() <= jwt.decode(
        token, key=security.SECRET_KEY, algorithms=[security.ALGORITHM]
    ).items()


@pytest.mark.anyio
async def test_get_user(registered_user: dict):
    user = await security.get_user(registered_user["email"])
    assert user.email == registered_user["email"]
    assert user.name == registered_user["name"]


@pytest.mark.anyio
async def test_auth_user(registered_user: dict):
    user = await security.auth_user(
        registered_user["email"], registered_user["password"]
    )
    assert user.email == registered_user["email"]
    assert user.name == registered_user["name"]


@pytest.mark.anyio
async def test_auth_user_not_found():
    with pytest.raises(security.HTTPException):
        _ = await security.auth_user("wrong@email.com", "dd")


@pytest.mark.anyio
async def test_auth_user_wrong_pass(registered_user: dict):
    with pytest.raises(security.HTTPException):
        _ = await security.auth_user(registered_user["email"], "wrong pass")


@pytest.mark.anyio
async def test_get_valid_token(registered_user: dict):
    token = security.create_access_token(registered_user["email"])
    user = await security.get_current_user(token)
    assert user.email == registered_user["email"]


@pytest.mark.anyio
async def test_get_invalid_token():
    with pytest.raises(HTTPException):
        _ = await security.get_current_user("token")
