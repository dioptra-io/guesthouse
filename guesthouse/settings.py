from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    chproxy_path: Path = Path("/usr/bin/chproxy")
    """Path to the chproxy binary."""
    chproxy_base_url: str = "http://localhost:9090"
    """URL of the chproxy instance that will be returned to the user."""
    clickhouse_base_url: str = "http://localhost:8123"
    """URL of the HTTP interface of the ClickHouse instance on which the users will be created."""
    clickhouse_username: str = "default"
    """Username of the ClickHouse user used to delete temporary users (needs DROP USER permission)."""
    clickhouse_password: str = ""
    """Password of the ClickHouse user used to delete temporary users (needs DROP USER permission)."""
    template_path: Path = Path("configuration/chproxy/template.yml")
    """Path to the base chproxy configuration."""
    user_prefix: str = "guesthouse"
    """Prefix assigned to every temporary user."""
