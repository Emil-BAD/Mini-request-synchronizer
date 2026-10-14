from pydantic import BaseModel, ConfigDict, Field


class ClientResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = ""
    phone: str
    email: str = ""
    amount: int | float


class StatsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    received: int = Field(default=0, ge=0)
    unique: int = Field(default=0, ge=0)
    duplicates_merged: int = Field(default=0, ge=0)
    invalid_dropped: int = Field(default=0, ge=0)


class SyncResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    clients: list[ClientResponse] = Field(default_factory=list)
    stats: StatsResponse
