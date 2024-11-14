from fastapi import APIRouter, Depends, HTTPException, status, Body, Query
from ..models.user_models import User, UserBase
from ..models.strategy_models import (
    Strategy,
    StrategyCreate,
    StrategyUpdate,
    StrategyDelete,
    StrategyList,
    StrategyListItem
)
from ..auth import get_current_user
from ..database import strategy_collection
from datetime import datetime

router = APIRouter()

@router.post("/strategies", response_model=Strategy, status_code=status.HTTP_201_CREATED)
async def create_strategy(strategy: StrategyCreate, current_user: UserBase = Depends(get_current_user)):
    existing_strategy = strategy_collection.find_one({"key": strategy.key})
    if existing_strategy:
        raise HTTPException(status_code=400, detail="Strategy key already exists")

    new_strategy = Strategy(
        **strategy.dict(),
        status="0",  # 初始状态为未开始
        user=current_user.username,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    result = strategy_collection.insert_one(new_strategy.dict())
    created_strategy = strategy_collection.find_one({"_id": result.inserted_id})
    return Strategy(**created_strategy)


@router.get("/strategies", response_model=Strategy)
async def read_strategy(key: str = Query(...), current_user: User = Depends(get_current_user)):
    strategy = strategy_collection.find_one({"key": key})
    if strategy is None:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return Strategy(**strategy)


@router.put("/strategies", response_model=Strategy)
async def update_strategy(strategy_update: StrategyUpdate, current_user: User = Depends(get_current_user)):
    update_data = {k: v for k, v in strategy_update.dict(exclude_unset=True).items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()

    updated_strategy = strategy_collection.find_one_and_update(
        {"key": strategy_update.key},
        {"$set": update_data},
        return_document=True
    )
    if updated_strategy is None:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return Strategy(**updated_strategy)


@router.delete("/strategies", status_code=status.HTTP_204_NO_CONTENT)
async def delete_strategy(strategy_delete: StrategyDelete, current_user: User = Depends(get_current_user)):
    result = strategy_collection.delete_one({"key": strategy_delete.key})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return {"detail": "Strategy deleted successfully"}


@router.post("/strategies/list", response_model=list[Strategy])
async def list_strategies(strategy_list: StrategyList = Body(...), current_user: User = Depends(get_current_user)):
    query = {}
    if strategy_list.prefix:
        query["key"] = {"$regex": f"^{strategy_list.prefix}"}
    if strategy_list.status:
        query["status"] = strategy_list.status
    if strategy_list.conversationId:
        query["conversationId"] = strategy_list.conversationId

    strategies = strategy_collection.find(query).skip(strategy_list.skip).limit(strategy_list.limit)
    return [Strategy(**strategy) for strategy in strategies]


@router.post("/strategies/keys", response_model=list[StrategyListItem])
async def list_strategy_keys(strategy_list: StrategyList = Body(...), current_user: User = Depends(get_current_user)):
    pipeline = [
        {"$project": {"_id": 0, "key": 1, "status": 1, "conversationId": 1}},
        {"$skip": strategy_list.skip},
        {"$limit": strategy_list.limit}
    ]

    match_stage = {}
    if strategy_list.prefix:
        match_stage["key"] = {"$regex": f"^{strategy_list.prefix}"}
    if strategy_list.status:
        match_stage["status"] = strategy_list.status
    if strategy_list.conversationId:
        match_stage["conversationId"] = strategy_list.conversationId

    if match_stage:
        pipeline.insert(0, {"$match": match_stage})

    keys = list(strategy_collection.aggregate(pipeline))
    return [StrategyListItem(**k) for k in keys]
