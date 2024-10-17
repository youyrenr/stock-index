from fastapi import FastAPI
from .api import users, key_values

app = FastAPI()

app.include_router(users.router, tags=["users"])
app.include_router(key_values.router, tags=["key-values"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Key-Value System"}