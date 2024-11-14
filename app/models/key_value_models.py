from pydantic import BaseModel, Field
from typing import Optional

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