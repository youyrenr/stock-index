from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class Message(BaseModel):
    messageId: str
    conversationId: str
    parentMessageId: Optional[str] = None
    sender: str
    text: str
    isCreatedByUser: bool
    isEdited: bool = False
    model: Optional[str] = None
    error: bool = False
    unfinished: bool = False
    tokenCount: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    user: Optional[str] = None

class MessageCreate(BaseModel):
    conversationId: Optional[str] = None
    parentMessageId: Optional[str] = None
    text: str
    sender: str
    isCreatedByUser: bool
    model: Optional[str] = None
    user: Optional[str] = None

class MessageUpdate(BaseModel):
    messageId: str
    text: str
    isEdited: bool = True
    user: Optional[str] = None

class MessageList(BaseModel):
    conversationId: str
    skip: int = 0
    limit: int = 50