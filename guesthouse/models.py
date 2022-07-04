from datetime import datetime

from pydantic import BaseModel, Field


class CredentialsRequest(BaseModel):
    username: str = Field("default", title="Username of the admin user")
    password: str = Field("", title="Password of the admin user")
    cluster: str = Field(
        "default",
        title="Name of the cluster (as-specified in the chproxy configuration) on which to map the user",
    )
    lifetime: int = Field(
        3600,
        title="Lifetime of the user in seconds",
    )
    tables: list[str] = Field(
        default_factory=list,
        title="Tables on which the user is allowed to run SELECT queries, for the specified database",
    )


class CredentialsResponse(BaseModel):
    base_url: str = Field(..., title="ClickHouse URL")
    username: str = Field(..., title="ClickHouse user")
    password: str = Field(..., title="ClickHouse password")
    expiration_time: datetime = Field(..., title="User's expiration time")
