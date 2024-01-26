import pytest
from httpx import AsyncClient


async def create_post(
    body: str, async_client: AsyncClient, logged_in_token: str
) -> dict:
    response = await async_client.post(
        "/post",
        json={"body": body},
        headers={"Authorization": f"Bearer {logged_in_token}"},
    )
    return response.json()


@pytest.fixture()
async def created_post(async_client: AsyncClient, logged_in_token: str):
    return await create_post("Test Post", async_client, logged_in_token)


@pytest.mark.anyio
async def test_create_new_post(async_client: AsyncClient, logged_in_token):
    body = "Test Post"
    response = await create_post(body, async_client, logged_in_token)
    assert {"id": 1, "body": body}.items() <= response.items()


@pytest.mark.anyio
async def test_create_new_post_missing_data(async_client: AsyncClient, logged_in_token):
    response = await async_client.post(
        "/post", json={}, headers={"Authorization": f"Bearer {logged_in_token}"}
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_getting_all_posts(async_client: AsyncClient, created_post: dict):
    response = await async_client.get("/post")
    assert response.status_code == 200
    assert created_post.items() <= response.json()[0].items()
