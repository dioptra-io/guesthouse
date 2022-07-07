from pych_client import AsyncClickHouseClient

from guesthouse.logger import logger


async def create_user(
    client: AsyncClickHouseClient, username: str, password: str
) -> None:
    logger.info("Creating user %s...", username)
    # Parameter interpolation is not supported for CREATE USER queries as of v22.6.
    query = f"CREATE USER {username} IDENTIFIED WITH sha256_password BY '{password}'"
    await client.execute(query)


async def delete_user(client: AsyncClickHouseClient, username: str) -> None:
    logger.info("Deleting user %s...", username)
    # Parameter interpolation is not supported for DROP USER queries as of v22.6.
    query = f"DROP USER {username}"
    await client.execute(query)


async def list_users(client: AsyncClickHouseClient, prefix: str) -> list[dict]:
    logger.info("Listing users with prefix %s...", prefix)
    query = "SELECT name FROM system.users WHERE startsWith(name, {prefix:String})"
    return await client.json(query, {"prefix": prefix})  # type: ignore


async def grant_select(
    client: AsyncClickHouseClient, username: str, table: str
) -> None:
    logger.info("Granting select on %s to %s", table, username)
    # Parameter interpolation is not supported for GRANT queries as of v22.6.
    query = f"GRANT SELECT ON {table} TO {username}"
    await client.execute(query)


async def grant_create_temporary_table(
    client: AsyncClickHouseClient, username: str
) -> None:
    logger.info("Granting create temporary table to %s", username)
    # Parameter interpolation is not supported for GRANT queries as of v22.6.
    query = f"GRANT CREATE TEMPORARY TABLE ON *.* TO {username}"
    await client.execute(query)
