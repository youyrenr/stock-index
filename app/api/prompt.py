from fastapi import APIRouter, Depends, HTTPException, status, Body, Query
from ..models.user_models import User
from ..models.prompt_models import Prompt, PromptCreate, PromptUpdate, PromptDelete, PromptList, PromptListItem
from ..auth import get_current_user
from ..database import prompt_collection
from datetime import datetime

router = APIRouter()


@router.post("/prompts", response_model=Prompt, status_code=status.HTTP_201_CREATED)
async def create_prompt(prompt: PromptCreate, current_user: User = Depends(get_current_user)):
    existing_prompt = prompt_collection.find_one({"key": prompt.key})
    if existing_prompt:
        raise HTTPException(status_code=400, detail="Prompt key already exists")
    new_prompt = Prompt(**prompt.dict(), created_at=datetime.utcnow(), updated_at=datetime.utcnow())
    result = prompt_collection.insert_one(new_prompt.dict())
    created_prompt = prompt_collection.find_one({"_id": result.inserted_id})
    return Prompt(**created_prompt)


@router.get("/prompts", response_model=Prompt)
async def read_prompt(key: str = Query(...), current_user: User = Depends(get_current_user)):
    prompt = prompt_collection.find_one({"key": key})
    if prompt is None:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return Prompt(**prompt)


@router.put("/prompts", response_model=Prompt)
async def update_prompt(prompt_update: PromptUpdate, current_user: User = Depends(get_current_user)):
    update_data = prompt_update.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()
    updated_prompt = prompt_collection.find_one_and_update(
        {"key": prompt_update.key},
        {"$set": update_data},
        return_document=True
    )
    if updated_prompt is None:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return Prompt(**updated_prompt)


@router.delete("/prompts", status_code=status.HTTP_204_NO_CONTENT)
async def delete_prompt(prompt_delete: PromptDelete, current_user: User = Depends(get_current_user)):
    result = prompt_collection.delete_one({"key": prompt_delete.key})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return {"detail": "Prompt deleted successfully"}


@router.post("/prompts/list", response_model=list[Prompt])
async def list_prompts(prompt_list: PromptList = Body(...), current_user: User = Depends(get_current_user)):
    query = {}
    if prompt_list.prefix:
        query["key"] = {"$regex": f"^{prompt_list.prefix}"}

    prompts = prompt_collection.find(query).skip(prompt_list.skip).limit(prompt_list.limit)
    return [Prompt(**prompt) for prompt in prompts]


@router.post("/prompts/keys", response_model=list[PromptListItem])
async def list_prompt_keys(prompt_list: PromptList = Body(...), current_user: User = Depends(get_current_user)):
    pipeline = [
        {"$project": {"_id": 0, "key": 1}},
        {"$skip": prompt_list.skip},
        {"$limit": prompt_list.limit}
    ]

    match_stage = {}
    if prompt_list.prefix:
        match_stage["key"] = {"$regex": f"^{prompt_list.prefix}"}

    if match_stage:
        pipeline.insert(0, {"$match": match_stage})

    keys = list(prompt_collection.aggregate(pipeline))
    return [PromptListItem(**k) for k in keys]