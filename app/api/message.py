from fastapi import APIRouter, Depends, HTTPException, status, Body
from ..models.user_models import User, UserBase
from ..models.message_models import Message, MessageCreate, MessageUpdate, MessageList
from ..models.gpt_message_models import ChatMessage, ChatRequest
from ..auth import get_current_user
from ..database import message_collection
from ..services.chatgpt_service import ChatGPTService
from datetime import datetime
import uuid
from typing import List, Dict, Any

router = APIRouter()
chatgpt_service = ChatGPTService()


@router.post("/messages", response_model=Message)
async def create_message(message: MessageCreate, current_user: UserBase = Depends(get_current_user)):
    message_data = message.dict()

    # 生成新的messageId
    message_data["messageId"] = str(uuid.uuid4())

    # 如果conversationId为空，创建新的对话
    if not message_data.get("conversationId"):
        message_data["conversationId"] = str(uuid.uuid4())

    # parentMessageId为空时不设置该字段
    if not message_data.get("parentMessageId"):
        message_data.pop("parentMessageId", None)

    message_data["user"] = str(current_user.username)
    message_data["created_at"] = datetime.utcnow()
    message_data["updated_at"] = datetime.utcnow()

    new_message = Message(**message_data)
    result = message_collection.insert_one(new_message.dict())
    created_message = message_collection.find_one({"_id": result.inserted_id})
    return Message(**created_message)


@router.get("/messages/{conversation_id}", response_model=List[Message])
async def get_conversation_messages(
        conversation_id: str,
        current_user: UserBase = Depends(get_current_user)
):
    messages = message_collection.find({
        "conversationId": conversation_id,
        "user": str(current_user.username)
    }).sort("created_at", 1)
    return [Message(**msg) for msg in messages]


@router.put("/messages", response_model=Message)
async def update_message(message_update: MessageUpdate, current_user: UserBase = Depends(get_current_user)):
    update_data = message_update.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()

    updated_message = message_collection.find_one_and_update(
        {"messageId": message_update.messageId, "user": str(current_user.username)},
        {"$set": update_data},
        return_document=True
    )
    if not updated_message:
        raise HTTPException(status_code=404, detail="Message not found")
    return Message(**updated_message)


@router.post("/messages/chat", response_model=Message)
async def create_chat_message(
        request: MessageCreate,
        current_user: UserBase = Depends(get_current_user)
):
    # 创建用户消息
    user_message = await create_message(request, current_user)

    # 准备AI回复的消息历史
    messages = []

    if user_message.conversationId:
        conversation_messages = message_collection.find({
            "conversationId": user_message.conversationId
        }).sort("created_at", 1)
    else:
        conversation_messages = [user_message.dict()]

    for msg in conversation_messages:
        role = "user" if msg["sender"] == "User" else "assistant"
        messages.append(ChatMessage(role=role, content=msg["text"]))

    try:
        # 调用ChatGPT服务，使用request中的model
        chat_request = ChatRequest(messages=messages)
        response = await chatgpt_service.create_completion(
            [msg.dict() for msg in chat_request.messages],
            model=request.sender  # 使用用户传入的sender作为模型参数
        )

        # 创建AI回复消息，保存用户选择的模型
        ai_message = MessageCreate(
            conversationId=user_message.conversationId,
            parentMessageId=user_message.messageId,
            text=response["choices"][0]["message"]["content"],
            sender=request.sender,  # 使用用户传入的sender
            isCreatedByUser=False,
            model=request.sender  # 保存用户选择的模型
        )
        ai_response = await create_message(ai_message, current_user)
        return ai_response

    except Exception as e:
        # 错误处理保持不变
        error_message = MessageCreate(
            conversationId=user_message.conversationId,
            parentMessageId=user_message.messageId,
            text=str(e),
            sender="System",
            isCreatedByUser=False,
            error=True
        )
        await create_message(error_message, current_user)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/messages/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_message(message_id: str, current_user: UserBase = Depends(get_current_user)):
    result = message_collection.delete_one({
        "messageId": message_id,
        "user": str(current_user.username)
    })
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Message not found")
    return {"detail": "Message deleted successfully"}


@router.get("/conversations", response_model=List[Dict[str, Any]])
async def get_user_conversations(
        skip: int = 0,
        limit: int = 20,
        current_user: User = Depends(get_current_user)
):
    # 获取用户所有对话ID
    pipeline = [
        {"$match": {"user": str(current_user.id)}},
        {"$sort": {"created_at": -1}},
        {"$group": {
            "_id": "$conversationId",
            "lastMessage": {"$first": "$$ROOT"},
            "messageCount": {"$sum": 1}
        }},
        {"$skip": skip},
        {"$limit": limit}
    ]

    conversations = list(message_collection.aggregate(pipeline))
    return conversations


@router.post("/messages/regenerate", response_model=Message)
async def regenerate_ai_message(
        data: dict = Body(..., example={"conversation_id": "some-uuid"}),
        current_user: UserBase = Depends(get_current_user)
):
    conversation_id = data.get("conversation_id")
    model = data.get("sender", "gpt-4o-mini")  # 获取model参数，默认为gpt-4o-mini
    if not conversation_id:
        raise HTTPException(
            status_code=400,
            detail="conversation_id is required"
        )
    conversation_messages = message_collection.find({
        "conversationId": conversation_id,
        "user": str(current_user.username)
    }).sort("created_at", 1)

    messages = []
    last_user_message = None

    for msg in conversation_messages:
        if msg["sender"] == "User":
            messages.append(ChatMessage(role="user", content=msg["text"]))
            last_user_message = msg
        else:
            messages.append(ChatMessage(role="assistant", content=msg["text"]))

    if not messages:
        raise HTTPException(
            status_code=400,
            detail="No conversation history found"
        )

    try:
        chat_request = ChatRequest(messages=messages)
        response = await chatgpt_service.create_completion(
            [msg.dict() for msg in chat_request.messages],
            model=model  # 使用指定的模型
        )

        new_ai_message = MessageCreate(
            conversationId=conversation_id,
            parentMessageId=last_user_message["messageId"] if last_user_message else None,
            text=response["choices"][0]["message"]["content"],
            sender=model,  # 使用指定的模型作为sender
            isCreatedByUser=False,
            model=model,  # 保存模型信息
        )

        return await create_message(new_ai_message, current_user)

    except Exception as e:
        # 5. 发生错误时创建错误消息
        error_message = MessageCreate(
            conversationId=conversation_id,
            parentMessageId=last_user_message["messageId"] if last_user_message else None,
            text=f"Regeneration failed: {str(e)}",
            sender="System",
            isCreatedByUser=False,
            error=True
        )
        await create_message(error_message, current_user)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )