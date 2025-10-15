import asyncio
import logging
import os
import secrets

from fastapi import Body, FastAPI
from pych_client import AsyncClickHouseClient

from guesthouse.chproxy import ChProxy
from guesthouse.clickhouse import (
    create_user,
    grant_create_temporary_table,
    grant_select,
)
from guesthouse.gc import clean_loop
from guesthouse.models import CredentialsRequest, CredentialsResponse
from guesthouse.settings import Settings
from guesthouse.username import generate_username
from guesthouse.utilities import gather_with_concurrency

app = FastAPI()
settings = Settings()
chproxy = ChProxy(settings.chproxy_path, settings.template_path, settings.user_prefix)
background_tasks = {}


@app.on_event("startup")
async def configure_logging() -> None:
    level = os.getenv("LOG_LEVEL", "WARNING").upper()
    logging.basicConfig(level=getattr(logging, level, logging.WARNING))


@app.on_event("startup")
async def start_chproxy() -> None:
    chproxy.start()


@app.on_event("shutdown")
async def stop_chproxy() -> None:
    chproxy.stop()


@app.on_event("startup")
async def start_gc() -> None:
    background_tasks["gc"] = asyncio.create_task(
        clean_loop(
            chproxy=chproxy,
            clickhouse_base_url=settings.clickhouse_base_url,
            clickhouse_username=settings.clickhouse_username,
            clickhouse_password=settings.clickhouse_password,
            user_prefix=settings.user_prefix,
        )
    )


@app.on_event("shutdown")
async def stop_gc() -> None:
    background_tasks["gc"].cancel()


@app.post("/")
async def generate_credentials(
    body: CredentialsRequest = Body(CredentialsRequest()),
) -> CredentialsResponse:
    username, expiration_time = generate_username(settings.user_prefix, body.lifetime)
    password = secrets.token_hex(16)
    async with AsyncClickHouseClient(
        base_url=settings.clickhouse_base_url,
        username=body.username,
        password=body.password,
    ) as client:
        await create_user(client, username, password)
        await grant_create_temporary_table(client, username)
        await gather_with_concurrency(
            16, *[grant_select(client, username, table) for table in body.tables]
        )
    chproxy.users[username] = {
        "username": username,
        "password": password,
        "cluster": body.cluster,
    }
    chproxy.reload()
    return CredentialsResponse(
        base_url=settings.chproxy_base_url,
        username=username,
        password=password,
        expiration_time=expiration_time,
    )
