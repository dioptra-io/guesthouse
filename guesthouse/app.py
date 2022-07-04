import asyncio
import logging
import secrets

from fastapi import Body, FastAPI
from pych_client import AsyncClickHouseClient

from guesthouse.chproxy import ChProxy
from guesthouse.clickhouse import create_user, grant_select
from guesthouse.gc import clean_loop
from guesthouse.models import CredentialsRequest, CredentialsResponse
from guesthouse.settings import Settings
from guesthouse.username import generate_username

app = FastAPI()
settings = Settings()
chproxy = ChProxy(settings.chproxy_path, settings.template_path, settings.user_prefix)
background_tasks = {}


@app.on_event("startup")
async def configure_logging() -> None:
    logging.basicConfig(level=logging.INFO)


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
        for table in body.tables:
            await grant_select(client, username, table)
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
