from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import users, key_values

app = FastAPI()

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许的源
    allow_credentials=True,
    allow_methods=["*"],  # 允许的 HTTP 方法
    allow_headers=["*"],  # 允许的 HTTP 头
)

app.include_router(users.router, tags=["users"])
app.include_router(key_values.router, tags=["key-values"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Key-Value System"}