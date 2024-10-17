from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordBearer
from datetime import timedelta
from ..auth import authenticate_user, create_access_token, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES, get_password_hash
from ..models import Token, User, UserCreate, UserOut, UserLogin
from ..database import users_collection

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

@router.post("/auth/token", response_model=Token)
async def login_for_access_token(user_login: UserLogin):
    user = authenticate_user(user_login.username, user_login.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/users", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    existing_user = users_collection.find_one({"username": user.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(user.password)
    new_user = UserCreate(username=user.username, hashed_password=hashed_password)
    result = users_collection.insert_one(new_user.dict())
    created_user = users_collection.find_one({"_id": result.inserted_id})
    return UserOut(**created_user)

@router.get("/users/me", response_model=UserOut)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return UserOut(**current_user.dict())

@router.put("/users/me", response_model=UserOut)
async def update_user(user_update: UserCreate, current_user: User = Depends(get_current_user)):
    hashed_password = get_password_hash(user_update.password)
    users_collection.update_one(
        {"username": current_user.username},
        {"$set": {"hashed_password": hashed_password}}
    )
    updated_user = users_collection.find_one({"username": current_user.username})
    return UserOut(**updated_user)

@router.delete("/users/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(current_user: User = Depends(get_current_user)):
    users_collection.delete_one({"username": current_user.username})
    return {"detail": "User deleted successfully"}