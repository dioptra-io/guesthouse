import secrets
from datetime import datetime, timedelta, timezone


def generate_username(prefix: str, lifetime: int) -> tuple[str, datetime]:
    exp = datetime.now(timezone.utc) + timedelta(seconds=lifetime)
    time_ns = int(exp.timestamp() * 1e6)
    return f"{prefix}_{time_ns}_{secrets.token_hex(2)}", exp


def parse_username(username: str) -> datetime:
    prefix, time_ns, token = username.split("_")
    time_s = int(time_ns) / 1e6
    return datetime.fromtimestamp(time_s, timezone.utc)
