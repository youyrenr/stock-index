from pydantic import BaseModel

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    type: str

class User(UserBase):
    hashed_password: str

class UserLogin(UserBase):
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class KeyValue(BaseModel):
    key: str
    value: str

class KeyValueUpdate(KeyValue):
    pass

class KeyValueDelete(BaseModel):
    key: str