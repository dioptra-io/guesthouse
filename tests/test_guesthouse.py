from pych_client import AsyncClickHouseClient

CHPROXY_BASE_URL = "http://localhost:9090"


async def test_generate_credentials(client):
    credentials = client.post("/").json()
    async with AsyncClickHouseClient(
        base_url=CHPROXY_BASE_URL,
        username=credentials["username"],
        password=credentials["password"],
    ) as clickhouse:
        assert await clickhouse.json("SELECT 1") == [{"1": 1}]
