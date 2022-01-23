import asyncio
from datetime import datetime, timezone

from pych_client import AsyncClickHouseClient

from guesthouse.chproxy import ChProxy
from guesthouse.clickhouse import delete_user, list_users
from guesthouse.username import parse_username


async def clean_loop(
    chproxy: ChProxy,
    clickhouse_base_url: str,
    clickhouse_username: str,
    clickhouse_password: str,
    user_prefix: str,
) -> None:
    while True:
        async with AsyncClickHouseClient(
            base_url=clickhouse_base_url,
            username=clickhouse_username,
            password=clickhouse_password,
        ) as client:
            await clean_users(client, chproxy, user_prefix)
        await asyncio.sleep(5)


async def clean_users(
    client: AsyncClickHouseClient,
    chproxy: ChProxy,
    user_prefix: str,
) -> None:
    users = await list_users(client, user_prefix)
    now = datetime.now(timezone.utc)
    for user in users:
        exp = parse_username(user["name"])
        if now > exp:
            await delete_user(client, user["name"])
            chproxy.remove_user(user["name"])
    chproxy.reload()
