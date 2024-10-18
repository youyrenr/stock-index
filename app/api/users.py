from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordBearer
from datetime import timedelta
from ..auth import authenticate_user, create_access_token, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES, get_password_hash
from ..models import Token, User, UserCreate, UserOut, UserLogin, UserList
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
    return {"access_token": access_token, "token_type": "bearer", "user_type": user.type}

@router.post("/users", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(new_user: UserCreate, current_user: User = Depends(get_current_user)):
    # 检查当前用户是否有权限创建新用户
    if current_user.type != "1":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to create new users"
        )

    # 检查用户名是否已存在
    existing_user = users_collection.find_one({"username": new_user.username})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # 创建新用户
    hashed_password = get_password_hash(new_user.password)
    new_user_data = {
        "username": new_user.username,
        "hashed_password": hashed_password,
        "type": "0"  # 新创建的用户默认 type 为 "0"
    }

    result = users_collection.insert_one(new_user_data)
    created_user = users_collection.find_one({"_id": result.inserted_id})

    return UserOut(**created_user)

@router.get("/users/me", response_model=UserOut)
async def read_users_me(current_user: User = Depends(get_current_user)):
    user_data = users_collection.find_one({"username": current_user.username})
    return UserOut(**user_data)

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

@router.post("/users/list", response_model=list[UserOut])
async def list_users(user_list: UserList, current_user: User = Depends(get_current_user)):
    # 检查当前用户是否有权限查看用户列表
    if current_user.type != "1":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view the user list"
        )

    # 查询用户列表，使用分页参数
    users = users_collection.find().skip(user_list.skip).limit(user_list.limit)

    # 转换查询结果为UserOut模型列表
    user_list = [UserOut(**user) for user in users]

    return user_list