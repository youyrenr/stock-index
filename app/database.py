from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client.key_value_system

users_collection = db.users
key_values_collection = db.key_values
