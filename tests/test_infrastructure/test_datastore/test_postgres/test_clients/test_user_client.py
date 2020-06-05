import pytest
from aiokea.errors import DuplicateResourceError

from app.infrastructure.common.filters.filters import Filter
from app.infrastructure.common.filters.operators import EQ, NE
from app.usecases.resources.user import User
from tests import db_setup


async def test_get_where(db, user_pg_client):
    stub_count = len(db_setup.stub_users)
    # No filters
    results = await user_pg_client.get_where()
    assert len(results) == stub_count

    # Filters
    result_equal_to = await user_pg_client.get_where([Filter("username", EQ, "brian")])
    result_not_equal_to = await user_pg_client.get_where(
        [Filter("username", NE, "brian")]
    )
    assert len(result_equal_to) + len(result_not_equal_to) == stub_count


# async def test_get_where_paginated(db, user_pg_client):
#     db_count = len(await user_pg_client.get_where())
#     retrieved_records = 0
#     page = 0
#     page_size = 1
#     while retrieved_records < db_count:
#         results = await user_pg_client.get_where(page=page, page_size=page_size)
#         retrieved_records += len(results)
#         assert retrieved_records == (page * page_size) + len(results)
#         page += 1
#     assert retrieved_records == db_count


async def test_create(db, user_pg_client):
    old_user_count = len(await user_pg_client.get_where())

    new_user = User(username="test", email="test")
    createed_user = await user_pg_client.create(new_user)
    assert createed_user.id == new_user.id

    new_user_count = len(await user_pg_client.get_where())
    assert new_user_count == old_user_count + 1


async def test_create_duplicate_error(db, user_pg_client):
    old_user_count = len(await user_pg_client.get_where())

    new_user = User(username="test", email="test")
    await user_pg_client.create(new_user)
    with pytest.raises(DuplicateResourceError):
        await user_pg_client.create(new_user)

    new_user_count = len(await user_pg_client.get_where())
    assert new_user_count == old_user_count + 1


async def test_update(db, user_pg_client):
    # Get an existing user
    roman: User = await user_pg_client.get_first_where(
        [Filter("username", EQ, "roman")]
    )
    roman.username = "bigassforehead"
    # Update the user
    await user_pg_client.update(roman)

    # Check that the user has been updated
    updated_roman: User = await user_pg_client.get_first_where(
        [Filter("id", EQ, roman.id)]
    )
    assert updated_roman.username == "bigassforehead"


# async def test_update_where(db, user_pg_client):
#     # Get baseline
#     user_count = len(await user_pg_client.get_where())
#     old_disabled_user_count = len(
#         await user_pg_client.get_where([Filter("is_enabled", EQ, False)])
#     )
#     assert old_disabled_user_count != user_count
#
#     # Update users
#     await user_pg_client.update_where(
#         set_values={"is_enabled": False}, filters=[Filter("is_enabled", EQ, True)]
#     )
#
#     # Check all users are now disabled
#     new_disabled_user_count = len(
#         await user_pg_client.get_where([Filter("is_enabled", EQ, False)])
#     )
#     assert new_disabled_user_count == user_count