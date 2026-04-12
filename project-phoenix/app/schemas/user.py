import uuid

from fastapi_users import schemas
from pydantic import BaseModel


class UserRead(schemas.BaseUser[uuid.UUID]):
    full_name: str | None = None
    phone: str | None = None
    role: str = "customer"
    language_pref: str = "id"
    avatar_url: str | None = None


class UserCreate(schemas.BaseUserCreate):
    full_name: str | None = None
    phone: str | None = None


class UserUpdate(schemas.BaseUserUpdate):
    full_name: str | None = None
    phone: str | None = None
    language_pref: str | None = None
    avatar_url: str | None = None


class AddressCreate(BaseModel):
    label: str = "Home"
    full_name: str
    phone: str
    street: str
    city: str
    province: str
    postal_code: str
    is_default: bool = False


class AddressRead(BaseModel):
    id: int
    label: str
    full_name: str
    phone: str
    street: str
    city: str
    province: str
    postal_code: str
    is_default: bool

    model_config = {"from_attributes": True}


class AddressUpdate(BaseModel):
    label: str | None = None
    full_name: str | None = None
    phone: str | None = None
    street: str | None = None
    city: str | None = None
    province: str | None = None
    postal_code: str | None = None
    is_default: bool | None = None
