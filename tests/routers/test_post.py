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


async def like_post(
    post_id: int, async_client: AsyncClient, logged_in_token: str
) -> dict:
    response = await async_client.post(
        "/like",
        json={"post_id": post_id},
        headers={"Authorization": f"Bearer {logged_in_token}"},
    )
    return response


@pytest.fixture()
async def created_post(async_client: AsyncClient, logged_in_token: str):
    return await create_post("Test Post", async_client, logged_in_token)


@pytest.mark.anyio
async def test_create_new_post(async_client: AsyncClient, logged_in_token):
    body = "Test Post"
    response = await create_post(body, async_client, logged_in_token)
    assert {"id": 1, "body": body}.items() <= response.items()


@pytest.mark.anyio
async def test_like_post(
    async_client: AsyncClient, logged_in_token, created_post: dict
):
    response = await like_post(created_post["id"], async_client, logged_in_token)
    assert response.status_code == 201
    assert {"id": 1, "post_id": created_post["id"]}.items() <= response.json().items()


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


@pytest.mark.parametrize("sorting,expected_out", [("new", [2, 1]), ("old", [1, 2])])
@pytest.mark.anyio
async def test_get_all_posts_sorting(
    async_client: AsyncClient, logged_in_token, sorting, expected_out
):
    await create_post("Test Post 1", async_client, logged_in_token)
    await create_post("Test Post 2", async_client, logged_in_token)
    response = await async_client.get("/post", params={"sorting": sorting})
    assert response.status_code == 200
    out = [post["id"] for post in response.json()]
    assert out == expected_out
