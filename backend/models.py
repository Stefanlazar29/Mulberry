from pydantic import BaseModel, Field, field_validator
from typing import Optional


class UserRegister(BaseModel):
    email: Optional[str] = Field(None, min_length=3)
    phone: Optional[str] = Field(None, min_length=7)
    password: str = Field(..., min_length=8)

    @field_validator("email", "phone")
    @classmethod
    def at_least_one_identifier(cls, v, info):
        data = info.data
        if not v:
            if not data.get("email") and not data.get("phone"):
                raise ValueError("Either email or phone must be provided")
        return v


class UserLogin(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    password: str = Field(..., min_length=8)

    @field_validator("email", "phone")
    @classmethod
    def at_least_one_identifier(cls, v, info):
        data = info.data
        if not v:
            if not data.get("email") and not data.get("phone"):
                raise ValueError("Either email or phone must be provided")
        return v


class TokenResponse(BaseModel):
    user_id: int
    email: Optional[str]
    phone: Optional[str]
    token: str
    expires_in: int = 86400


class HealthResponse(BaseModel):
    status: str = "ok"
