from pych_client import AsyncClickHouseClient


async def test_generate_credentials(client):
    credentials = client.post("/").json()
    async with AsyncClickHouseClient(
        base_url=credentials["base_url"],
        username=credentials["username"],
        password=credentials["password"],
    ) as clickhouse:
        assert await clickhouse.json("SELECT 1") == [{"1": 1}]
