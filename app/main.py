from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import users, key_values, prompt, message, strategy

app = FastAPI()

# 确保服务在应用启动时初始化
@app.on_event("startup")
async def startup_event():
    # 如果需要进行任何初始化检查，可以在这里添加
    pass

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router, tags=["users"])
app.include_router(key_values.router, tags=["key-values"])
app.include_router(prompt.router, tags=["prompt"])
app.include_router(message.router, tags=["messages"])
app.include_router(strategy.router, tags=["strategies"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Key-Value System"}