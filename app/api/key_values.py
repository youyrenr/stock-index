from fastapi import APIRouter, Depends, HTTPException, status, Body
from ..models import KeyValue, User, KeyValueUpdate, KeyValueDelete, KeyListItem, KeyList
from ..auth import get_current_user
from ..database import key_values_collection

router = APIRouter()

@router.post("/key-values", response_model=KeyValue, status_code=status.HTTP_201_CREATED)
async def create_key_value(key_value: KeyValue, current_user: User = Depends(get_current_user)):
    existing_key_value = key_values_collection.find_one({"key": key_value.key})
    if existing_key_value:
        raise HTTPException(status_code=400, detail="Key already exists")
    result = key_values_collection.insert_one(key_value.dict())
    created_key_value = key_values_collection.find_one({"_id": result.inserted_id})
    return KeyValue(**created_key_value)

@router.get("/key-values", response_model=KeyValue)
async def read_key_value(key: str = Body(..., embed=True), current_user: User = Depends(get_current_user)):
    key_value = key_values_collection.find_one({"key": key})
    if key_value is None:
        raise HTTPException(status_code=404, detail="Key not found")
    return KeyValue(**key_value)

@router.put("/key-values", response_model=KeyValue)
async def update_key_value(key_value: KeyValueUpdate, current_user: User = Depends(get_current_user)):
    updated_key_value = key_values_collection.find_one_and_update(
        {"key": key_value.key},
        {"$set": {"value": key_value.value}},
        return_document=True
    )
    if updated_key_value is None:
        raise HTTPException(status_code=404, detail="Key not found")
    return KeyValue(**updated_key_value)

@router.delete("/key-values", status_code=status.HTTP_204_NO_CONTENT)
async def delete_key_value(key_delete: KeyValueDelete, current_user: User = Depends(get_current_user)):
    result = key_values_collection.delete_one({"key": key_delete.key})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Key not found")
    return {"detail": "Key-value pair deleted successfully"}

@router.post("/key-values/list", response_model=list[KeyValue])
async def list_key_values(skip: int = Body(0), limit: int = Body(10), current_user: User = Depends(get_current_user)):
    key_values = key_values_collection.find().skip(skip).limit(limit)
    return [KeyValue(**kv) for kv in key_values]

@router.post("/key-values/keys", response_model=list[KeyListItem])
async def list_keys(key_list: KeyList = Body(...), current_user: User = Depends(get_current_user)):
    # 使用聚合管道来只获取 key 字段
    pipeline = [
        {"$project": {"_id": 0, "key": 1}},  # 只选择 key 字段
        {"$skip": key_list.skip},
        {"$limit": key_list.limit}
    ]

    # 如果提供了 prefix，添加一个匹配阶段
    if key_list.prefix:
        pipeline.insert(0, {
            "$match": {
                "key": {"$regex": f"^{key_list.prefix}"}
            }
        })

    keys = list(key_values_collection.aggregate(pipeline))
    return [KeyListItem(**k) for k in keys]