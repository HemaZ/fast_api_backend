import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_register_new_user(async_client: AsyncClient):
    user_details = {
        "name": "Ibrahim",
        "email": "ibrahim@hema.com",
        "password": "hemahema",
    }
    response = await async_client.post("/register", json=user_details)
    assert response.status_code == 201


@pytest.mark.anyio
async def test_register_existing_user(async_client: AsyncClient, registered_user: dict):
    response = await async_client.post("/register", json=registered_user)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


@pytest.mark.anyio
async def test_token_existing_user(async_client: AsyncClient, registered_user: dict):
    response = await async_client.post("/token", json=registered_user)
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.anyio
async def test_token_non_existing_user(async_client: AsyncClient):
    user_details = {
        "name": "test",
        "email": "test@hema.com",
        "password": "hemahema",
    }
    response = await async_client.post("/token", json=user_details)
    assert response.status_code == 401
    assert "Couldn't validate user" in response.json()["detail"]
