from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class SdkContractModel(BaseModel):
    """Shared strict Pydantic base for public Skills SDK contract models."""

    model_config = ConfigDict(extra="forbid", strict=True)
