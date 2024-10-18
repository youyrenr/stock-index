from fastapi import APIRouter, Depends, HTTPException, status, Body, Query
from ..models import KeyValue, KeyValueCreate, User, KeyValueUpdate, KeyValueDelete, KeyListItem, KeyList
from ..auth import get_current_user
from ..database import key_values_collection

router = APIRouter()


@router.post("/key-values", response_model=KeyValue, status_code=status.HTTP_201_CREATED)
async def create_key_value(key_value: KeyValueCreate, current_user: User = Depends(get_current_user)):
    existing_key_value = key_values_collection.find_one({"key": key_value.key})
    if existing_key_value:
        raise HTTPException(status_code=400, detail="Key already exists")
    result = key_values_collection.insert_one(key_value.dict(exclude_unset=True))
    created_key_value = key_values_collection.find_one({"_id": result.inserted_id})
    return KeyValue(**created_key_value)


@router.get("/key-values", response_model=KeyValue)
async def read_key_value(key: str = Query(...), current_user: User = Depends(get_current_user)):
    key_value = key_values_collection.find_one({"key": key})
    if key_value is None:
        raise HTTPException(status_code=404, detail="Key not found")
    return KeyValue(**key_value)


@router.put("/key-values", response_model=KeyValue)
async def update_key_value(key_value: KeyValueUpdate, current_user: User = Depends(get_current_user)):
    update_data = key_value.dict(exclude_unset=True)
    updated_key_value = key_values_collection.find_one_and_update(
        {"key": key_value.key},
        {"$set": update_data},
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
async def list_key_values(key_list: KeyList = Body(...), current_user: User = Depends(get_current_user)):
    query = {}
    if key_list.prefix:
        query["key"] = {"$regex": f"^{key_list.prefix}"}
    if key_list.parentKey == "":
        query["$or"] = [{"parentKey": None}, {"parentKey": {"$exists": False}}]
    elif key_list.parentKey is not None:
        query["parentKey"] = key_list.parentKey

    key_values = key_values_collection.find(query).skip(key_list.skip).limit(key_list.limit)
    return [KeyValue(**kv) for kv in key_values]

@router.post("/key-values/keys", response_model=list[KeyListItem])
async def list_keys(key_list: KeyList = Body(...), current_user: User = Depends(get_current_user)):
    pipeline = [
        {"$project": {"_id": 0, "key": 1}},
        {"$skip": key_list.skip},
        {"$limit": key_list.limit}
    ]

    match_stage = {}
    if key_list.prefix:
        match_stage["key"] = {"$regex": f"^{key_list.prefix}"}
    if key_list.parentKey == "":
        match_stage["$or"] = [{"parentKey": None}, {"parentKey": {"$exists": False}}]
    elif key_list.parentKey is not None:
        match_stage["parentKey"] = key_list.parentKey

    if match_stage:
        pipeline.insert(0, {"$match": match_stage})

    keys = list(key_values_collection.aggregate(pipeline))
    return [KeyListItem(**k) for k in keys]