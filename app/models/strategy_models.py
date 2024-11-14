from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class Strategy(BaseModel):
    key: str
    value: str
    status: str  # 0 未开始 1 已开始 2 已完成 3 已报错
    user: Optional[str] = None  # 创建者
    conversationId: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class StrategyCreate(BaseModel):
    key: str
    value: str

class StrategyUpdate(BaseModel):
    key: str
    value: Optional[str] = None
    status: Optional[str] = None
    conversationId: Optional[str] = None

class StrategyDelete(BaseModel):
    key: str

class StrategyList(BaseModel):
    skip: int = 0
    limit: int = 10
    prefix: str | None = None
    status: str | None = None
    conversationId: str | None = None

class StrategyListItem(BaseModel):
    key: str
    status: str
    conversationId: str