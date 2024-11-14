from pydantic import BaseModel, Field
from datetime import datetime

class Prompt(BaseModel):
    key: str
    value: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class PromptCreate(BaseModel):
    key: str
    value: str

class PromptUpdate(BaseModel):
    key: str
    value: str

class PromptDelete(BaseModel):
    key: str

class PromptList(BaseModel):
    skip: int = 0
    limit: int = 10
    prefix: str | None = None

class PromptListItem(BaseModel):
    key: str