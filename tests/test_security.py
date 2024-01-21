import pytest

from storeapi import security


@pytest.mark.anyio
async def test_get_user(registered_user: dict):
    user = await security.get_user(registered_user["email"])
    assert user.email == registered_user["email"]
    assert user.name == registered_user["name"]