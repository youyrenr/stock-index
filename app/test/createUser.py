from app.database import users_collection
from app.auth import get_password_hash

users_collection.insert_one({
    "username": "admin",
    "hashed_password": get_password_hash("admin123")
})