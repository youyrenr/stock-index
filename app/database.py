from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
# client = MongoClient("mongodb://chat-mongodb:27017")
db = client.key_value_system

users_collection = db.users
key_values_collection = db.key_values
prompt_collection = db.prompt
message_collection = db.message
strategy_collection = db.strategy

message_collection.create_index("messageId", unique=True)
message_collection.create_index("conversationId")
message_collection.create_index([("user", 1), ("created_at", -1)])
