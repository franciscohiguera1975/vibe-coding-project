from typing import Any

from pydantic import BaseModel


class ConfigurationPublic(BaseModel):
    key: str
    value: dict[str, Any]
    description: str


class UpdateConfigurationRequest(BaseModel):
    value: dict[str, Any]
    description: str = ""
