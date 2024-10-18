from pydantic import BaseModel, Field
from typing import Optional


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class UserOut(UserBase):
    type: str


class User(UserBase):
    hashed_password: str
    type: str


class UserLogin(UserBase):
    password: str


class UserList(BaseModel):
    skip: int = 0
    limit: int = 10


class Token(BaseModel):
    access_token: str
    token_type: str
    user_type: str


class TokenData(BaseModel):
    username: str | None = None


class KeyValue(BaseModel):
    key: str
    value: str
    parentKey: Optional[str] = Field(default=None)


class KeyValueCreate(KeyValue):
    pass


class KeyValueUpdate(KeyValue):
    pass


class KeyValueDelete(BaseModel):
    key: str


class KeyList(BaseModel):
    skip: int = 0
    limit: int = 10
    prefix: Optional[str] = None
    parentKey: Optional[str] = None


class KeyListItem(BaseModel):
    key: str
